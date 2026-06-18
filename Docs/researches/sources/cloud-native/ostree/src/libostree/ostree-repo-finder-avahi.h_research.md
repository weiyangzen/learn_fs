# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi.h

Purpose: declares the public final `OstreeRepoFinderAvahi` type and its lifecycle API for LAN repository discovery using Avahi.

Important APIs/types/functions: `OSTREE_TYPE_REPO_FINDER_AVAHI`, `G_DECLARE_FINAL_TYPE`, `ostree_repo_finder_avahi_new(GMainContext *context)`, `ostree_repo_finder_avahi_start`, and `ostree_repo_finder_avahi_stop`. The type is also an `OstreeRepoFinder` implementation through the `.c` interface registration.

Control flow: callers create an instance with an optional main context, start network monitoring, use the generic `ostree_repo_finder_resolve_async()` API inherited from the finder interface, then stop monitoring. The header intentionally exposes lifecycle only, not the internal cache or TXT record details.

State and persistence: no state is declared in the header; object internals are private to the `.c` file. Runtime state is transient and tied to the main context and Avahi connection.

Dependencies/integration: includes GLib/GIO/GObject, `ostree-repo-finder.h`, and `ostree-types.h`. It is exported as unstable public API and appears in the released symbol list. Pull code uses it as the default `lan` finder when configured.

Risks: users must understand the main-context requirement documented in the implementation; the header itself cannot enforce that `start` is called before resolving. Builds without Avahi still expose the type but runtime methods return not-supported errors.

Test signals: construction is directly covered by `tests/test-repo-finder-avahi.c`; lifecycle behavior with a real Avahi daemon is environment-dependent.
