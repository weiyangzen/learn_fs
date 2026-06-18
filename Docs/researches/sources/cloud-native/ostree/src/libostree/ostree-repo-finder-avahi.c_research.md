# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.c

Purpose: implements the Avahi/DNS-SD `OstreeRepoFinder` backend, discovering OSTree repositories advertised on the local network and resolving requested `OstreeCollectionRef` values to dynamic HTTP remotes.

Important APIs/types/functions: exports `ostree_repo_finder_avahi_new`, `ostree_repo_finder_avahi_start`, and `ostree_repo_finder_avahi_stop`; implements the finder interface through `ostree_repo_finder_avahi_resolve_async/finish`. Internal types include `OstreeAvahiService`, `UriAndKeyring`, and `ResolveData`. Key helpers parse Avahi TXT records, evaluate Bloom filters, fetch and validate remote summaries, map refs to checksums, and build `OstreeRepoFinderResult` instances.

Control flow: construction stores a `GMainContext` and, when compiled with Avahi, initializes the Avahi GLib poll object and caches. `start` creates an Avahi client and service browser for `_ostree_repo._tcp`. Browser callbacks create resolvers; resolver callbacks cache successful services. Resolve requests are marshalled into the Avahi context, queued in `resolve_tasks`, and completed only once the browser is quiescent and all resolvers have finished. For each cached service, TXT attributes `v`, `rb`, `st`, and `ri` are validated; possible refs from the Bloom filter are grouped by URI/keyring; summaries are fetched to replace Bloom hits with actual checksums before returning results.

State and persistence: state is in memory only: pending tasks, Avahi handles, resolver map, found service cache, cancellable, and client/browser flags. It temporarily registers dynamic remotes in the parent repo while fetching summaries, then removes them if they were not already configured.

Dependencies/integration: depends on optional Avahi, `ostree-bloom-private`, TXT record parsing in `ostree-repo-finder-avahi-private.h`, remote/keyring resolution, summary parsing constants, and the shared `OstreeRepoFinder` interface. `ostree-repo-pull.c` creates it for the configured `lan` repo finder and starts it before `ostree_repo_finder_resolve_all_async`.

Risks: behavior is compile-time optional; without Avahi, resolve and start return not-supported errors. Network discovery is asynchronous and requires the supplied main context to be iterated. Bloom filters can produce false positives, so summary download and validation are required. Dynamic remote names are derived from escaped URI/keyring strings with an acknowledged weak `_` separator. TXT parsing rejects malformed or non-normal `GVariant` values, but bad peers can still cause repeated summary fetch failures. `stop` cancels all pending resolves and clears Avahi handles from the Avahi context.

Test signals: `tests/test-repo-finder-avahi.c` covers construction and TXT record parsing edge cases. Full live Avahi discovery is not exercised there; integration is indirectly covered by pull/find-remotes paths when the `lan` finder is enabled.
