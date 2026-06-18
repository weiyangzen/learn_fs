# Group Research: group_1382_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_dns64_synth_c_so_f32190b0c850

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.c

OpenBSD `unwind` DNS64 synthesis helper adapted from Unbound’s DNS64 module. It exports `dns64_synth_aaaa_data()` for frontend-side DNS64 response rewriting.

Key behavior:
- Uses global `dns64_prefixes` and `dns64_prefix_count` from `frontend.c`.
- Synthesizes one AAAA record per configured DNS64 prefix for each source A record.
- Preserves TTL, trust, and security metadata from the source A rrset.
- Constructs a replacement `ub_packed_rrset_key` with type `AAAA` and recomputed hash.
- Validates source A rdata shape as 2-byte rdatalen plus 4-byte IPv4 address.
- Uses Unbound regional allocation, so synthesized data lifetime is tied to the query region.

Important implementation detail:
- `synthesize_aaaa()` copies the IPv6 prefix, inserts the IPv4 address at `prefixlen / 8`, and skips byte position 8 per DNS64 address format handling.

Role in group:
- This is the OpenBSD-specific multi-prefix variant used by `frontend.c` when `unwind` receives an empty AAAA result and retries the same name as A.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.h

Header for the OpenBSD frontend DNS64 synthesis helper.

Exports:
- `dns64_synth_aaaa_data(const struct ub_packed_rrset_key *, const struct packed_rrset_data *, struct ub_packed_rrset_key *, struct packed_rrset_data **, struct regional *)`

Dependencies:
- The declaration relies on Unbound rrset and regional allocator types being visible from including translation units.

Role in group:
- Provides the local synthesis API used by `frontend.c` without exposing the helper internals.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/dns64_synth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/frontend.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/frontend.c

Main frontend process for OpenBSD `unwind`. It owns client-facing UDP/TCP DNS sockets, validates and logs queries, relays query requests to the resolver process over imsg, receives streamed answers, rewrites or synthesizes replies, tracks network changes, handles trust anchors, and enforces a domain blocklist.

Major responsibilities:
- Starts chrooted under `UNWIND_USER`, drops privileges, and pledges `stdio dns unix recvfd`.
- Receives socket file descriptors and configuration over imsg from the main process.
- Maintains UDP and TCP pending query state in `struct pending_query`.
- Parses DNS queries with Unbound/sldns helpers, validates header semantics, EDNS, qname, qtype, and qclass.
- Rejects AXFR/IXFR and malformed meta/obsolete types.
- Answers CHAOS `version.server.` and `version.bind.` locally with `unwind`.
- Relays accepted queries to resolver via `IMSG_QUERY`.
- Receives resolver answers in chunks using `answer_header->answer_len` and assembles them into `pq->abuf`.
- Re-encodes successful replies through Unbound `reply_info_parse()` / `reply_info_encode()` to preserve frontend policy and answer minimization.
- Performs DNS64 retry/synthesis for AAAA queries when no AAAA answer is present and DNS64 prefixes are configured.
- Handles route socket messages to notify resolver about network/DNS changes.
- Tracks available IPv4/IPv6 address families using `getifaddrs()` and sends `IMSG_CHANGE_AFS`.
- Parses, sorts, merges, sends, and writes trust anchors.
- Parses blocklist files into a reversed-domain RB tree supporting exact and wildcard-ish suffix comparison.
- Implements TCP accept backoff on descriptor exhaustion and per-query TCP timeout.

DNS64 flow:
- `noerror_answer()` parses a normal resolver answer. If it is an IN AAAA query, no answer rrset is present, and `dns64_prefix_count > 0`, it sets `pq->dns64_synthesize`.
- Resolver dispatch then calls `resend_dns64_query()`, which clones query state, changes the resolver query type to A, and marks the new pending query for synthesis.
- On the A answer, `synthesize_dns64_answer()` creates a new `reply_info`, converts answer-section A rrsets to AAAA via `dns64_synth_aaaa_data()`, copies other rrsets, and re-encodes the original AAAA response.

Networking:
- UDP uses `recvmsg()` into static `udp_ev` buffers and `sendto()` for replies.
- TCP accepts nonblocking sockets with `accept4()`, reads a two-byte DNS length prefix, then writes a length-prefixed response.
- `accept_reserve()` keeps `FD_RESERVE` descriptors free.

Route handling:
- `RTM_PROPOSAL` with `RTA_DNS` sends `IMSG_REPLACE_DNS`.
- `RTM_IFINFO` sends `IMSG_NETWORK_CHANGED`.
- address/desync events trigger address-family availability checks.
- interface removal sends a replacement DNS proposal with empty `sockaddr_rtdns`.

Security posture:
- Strong OpenBSD privilege separation: chroot, uid/gid drop, pledge, fd passing.
- Query validation happens before resolver relay.
- Resolver answers that are bogus and not client-CD are converted to SERVFAIL.
- Blocklist returns REFUSED.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/frontend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/frontend.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/frontend.h

Public declarations and shared frontend data structures for `unwind`.

Definitions:
- `HAVE_IPV4`, `HAVE_IPV6` bit flags.
- `struct trust_anchor`: TAILQ node containing a DNSKEY trust anchor string.
- `struct imsg_rdns_proposal`: interface index, source, and routing DNS sockaddr for resolver updates.
- `struct dns64_prefix`: IPv6 prefix, prefix length, and flags.

Exports:
- frontend lifecycle and imsg dispatch/compose functions.
- `ip_port()` formatting helper.
- trust anchor helpers: `add_new_ta()`, `free_tas()`, `merge_tas()`.

Role in group:
- Shared contract between frontend implementation, resolver/main messaging, and DNS64 synthesis helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/frontend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/Makefile.inc

OpenBSD make include for building the vendored/embedded Unbound sources used by `unwind`.

Behavior:
- Adds warning-oriented CFLAGS and includes `${.CURDIR}`.
- Sets `.PATH` to `${.CURDIR}/libunbound`.
- Includes component make fragments for dns64, iterator, libunbound, respip, services, cache, sldns, util, storage, and validator.

Role in group:
- Top-level build wiring for the `libunbound` subtree consumed by `sbin/unwind`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/config.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/config.h

Generated Unbound `config.h` for the OpenBSD `unwind` embedded Unbound build. It captures platform capabilities, feature toggles, package metadata, compatibility shims, and default paths.

Key configuration:
- Package version: `unbound 1.25.1`.
- Configure line enables all symbols, OpenSSL/LibreSSL, libevent, expat; disables Python module, shared libraries, explicit port randomisation, and pthreads.
- Default paths point to `/var/unbound`.
- `HAVE_LIBRESSL`, `HAVE_SSL`, `USE_LIBEVENT`, `USE_ECDSA`, `USE_ED25519`, `USE_SHA1`, and `USE_SHA2` are enabled.
- `USE_DNSTAP`, `USE_DNSCRYPT`, `USE_CACHEDB`, `USE_DSA`, `USE_GOST`, `USE_IPSECMOD`, `USE_IPSET`, Python bindings, and Windows support are disabled.
- `DISABLE_EXPLICIT_PORT_RANDOMISATION` is enabled for kernel-based UDP source port randomization.

Compatibility layer:
- Provides replacement symbol mappings for absent functions such as `inet_pton`, `inet_ntop`, `strlcpy`, `strlcat`, `reallocarray`, `explicit_bzero`, and others when needed.
- Defines attribute macros like `ATTR_FORMAT`, `ATTR_UNUSED`, `ATTR_NONSTRING`, and fallthrough/noreturn helpers.
- Enables extension macros such as `_OPENBSD_SOURCE`, `_NETBSD_SOURCE`, `_GNU_SOURCE`, etc.
- Defines Unbound default ports for DNS, DoT, DoH, DoQ, and control.

Role in group:
- Central compile-time contract for all embedded Unbound files in this group.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/acl_list.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/acl_list.h

Unbound daemon header for client access control storage.

Core types:
- `enum acl_access`: deny/refuse variants, non-local restrictions, allow modes, set-RD allow, and cookie-gated allow.
- `struct acl_list`: regional allocator plus address tree.
- `struct acl_addr`: address tree node with ACL action, tag lists/actions/data, interface marker, and optional view pointer.

API:
- create/delete ACL list.
- insert listening interface ACL entries.
- apply normal and interface ACL config.
- lookup `acl_addr` by sockaddr and retrieve action.
- compute memory usage.
- convert ACL enum to string and log decisions.
- swap trees for reload-style replacement.

Role in group:
- Interface definition for Unbound’s downstream client policy engine, though `unwind` primarily uses its own frontend socket/process model.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/acl_list.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/remote.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/remote.h

Unbound daemon header for remote-control support and fast reload plumbing.

Core structures:
- `struct rc_state`: active remote-control connection state, commpoint, handshake state, optional SSL handle, fd, and owning remote controller.
- `struct daemon_remote`: remote-control listener state, worker, accept list, certificate mode, active/max-active counters, busy list, and optional SSL context.
- `struct remote_stream`: SSL-or-plain output stream.
- `enum fast_reload_notification`: protocol between fast reload thread and server thread.
- `struct fast_reload_printq`: queued output for a remote-control client during fast reload.
- `struct fast_reload_auth_change`: tracks auth-zone add/delete/change during reload.
- `struct fast_reload_thread`: thread, socketpairs, output queue, locks, auth-zone change state, and reload coordination flags.

API:
- create/delete/clear remote control state.
- open/listen/stop/start remote-control ports.
- execute remote commands.
- SSL printing/line-reading helpers when SSL is available.
- start/stop fast reload thread.
- fast reload callbacks and worker pickup.

Role in group:
- Declares Unbound remote-control machinery. In this OpenBSD build, SSL support is compiled in, but `unwind` does not expose the full upstream daemon control surface in the frontend file read here.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/remote.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/stats.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/stats.h

Unbound daemon statistics interface.

API:
- Initialize `ub_server_stats` from config.
- Record cache misses and prefetches.
- Log stats per worker/thread.
- Obtain stats from another worker through command pipe.
- Compile/reset stats for a worker.
- Reply with stats over worker communication.
- Add stats blocks together.
- Insert query metadata, rcode, and downstream DNS Cookie stats.

Role in group:
- Stats contract used by Unbound workers and remote-control/reporting paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/worker.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/worker.h

Unbound worker structure and lifecycle interface.

Core types:
- `enum worker_commands`: quit, stats, stats-noreset, remote command, and fast-reload stop/start/poll.
- `struct worker`: thread identity, daemon pointer, command tube, event base, front/back network interfaces, port list, signal handler, command commpoint, stats timer, error rate limiting, random state, allocation cache, per-thread stats, scratch regional, module environment, optional dnstap env, and cache reuse flag.

API:
- create/init/run/delete worker.
- send worker command.
- clear/init worker stats.

Role in group:
- Describes Unbound’s worker execution context used by resolver-side components.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/worker.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/Makefile.inc

Build fragment for Unbound DNS64 module.

Behavior:
- Adds `.PATH` for `libunbound/dns64`.
- Adds `dns64.c` to `SRCS`.

Role in group:
- Enables DNS64 module compilation in the embedded Unbound source build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.c

Unbound DNS64 module implementation. It plugs into Unbound’s module chain and synthesizes AAAA answers from A answers when appropriate.

Configuration:
- Default DNS64 prefix is `64:ff9b::/96`.
- Accepts DNS64 prefix lengths 32, 40, 48, 56, 64, or 96.
- Supports `dns64_ignore_aaaa` tree for names whose real AAAA answers should be ignored and synthesized anyway.
- Supports `dns64_synthall`.

Core state:
- `enum dns64_state`: internal query, new external query, subquery finished.
- `struct dns64_qstate`: per-query state plus original `no_cache_store`.
- `struct dns64_env`: prefix address/net length and ignore-AAAA name tree.

Major functions:
- `dns64_init()` allocates module env and applies config.
- `dns64_deinit()` frees ignore-AAAA tree.
- `dns64_operate()` handles module events and controls query state.
- `handle_event_pass()` handles new queries, PTR rewrite cases, and forced synthesis cases.
- `handle_event_moddone()` decides whether a completed AAAA query needs an A subquery.
- `generate_type_A_query()` attaches an A subquery for an AAAA query.
- `handle_ipv6_ptr()` rewrites reverse IPv6 PTR queries under the DNS64 prefix into IPv4 PTR subqueries.
- `dns64_inform_super()` receives subquery completion and adjusts the parent query.
- `dns64_adjust_a()` converts A answer rrsets to AAAA rrsets and updates parent response.
- `dns64_adjust_ptr()` copies IPv4 PTR response and rewrites answer owner name to original IPv6 PTR qname.
- `dns64_synth_aaaa_data()` synthesizes one AAAA rrset from one A rrset for the configured prefix.

Cache behavior:
- New external queries force `qstate->no_cache_store = 1` while DNS64 determines whether to modify results.
- Synthesized responses may be stored if the query did not start as no-cache.
- Negative AAAA entries may be removed from rrset/msg cache when synthesized data replaces them.

Address synthesis:
- `synthesize_aaaa()` embeds IPv4 bytes at the configured prefix offset and skips byte 8.
- `extract_ipv4()` reverses that process for PTR handling.
- `ipv4_to_ptr()` builds wire-format `in-addr.arpa` names.

Role in group:
- Upstream-style single-prefix DNS64 module, contrasted with OpenBSD `dns64_synth.c`, which provides frontend multi-prefix synthesis for `unwind`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.h

Header for the Unbound DNS64 module.

Exports:
- `dns64_get_funcblock()`
- `dns64_init()`
- `dns64_deinit()`
- `dns64_operate()`
- `dns64_inform_super()`
- `dns64_clear()`
- `dns64_get_mem()`

Role in group:
- Module API contract that lets Unbound’s module framework instantiate and drive DNS64 processing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt.h

Conditional DNSCrypt interface header for Unbound. Contents are compiled only when `USE_DNSCRYPT` is defined.

Important point for this build:
- `dnscrypt_config.h` leaves `USE_DNSCRYPT` disabled, so these declarations are inactive in the OpenBSD `unwind` build.

When enabled, defines:
- DNSCrypt magic/header sizes and padding defaults.
- `KeyPair`, `dnsccert`, `dnsc_env`, and `dnscrypt_query_header`.
- Environment state for certificates, keypairs, provider keys, shared-secret cache, nonce cache, replay counters, and locks.

API when enabled:
- create/apply/delete DNSCrypt environment.
- handle curved and uncurved DNSCrypt requests.
- cache size/compare/delete callbacks for shared secrets and nonce cache.

Role in group:
- Dormant optional interface retained from Unbound.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt_config.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt_config.h

Generated-style feature shim for DNSCrypt.

Behavior:
- Exists so code can check `USE_DNSCRYPT` without directly including full `config.h`.
- Contains `#if 0 /* ENABLE_DNSCRYPT */`, so it does not define `USE_DNSCRYPT`.

Role in group:
- Confirms DNSCrypt is disabled in this OpenBSD embedded Unbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnscrypt/dnscrypt_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap.h

Conditional dnstap interface header for Unbound. Contents are compiled only when `USE_DNSTAP` is defined.

Important point for this build:
- `dnstap_config.h` leaves `USE_DNSTAP` disabled, so these declarations are inactive in the OpenBSD `unwind` build.

When enabled, defines:
- `struct dt_env`: dnstap I/O thread, per-worker message queue, identity/version strings, enabled message-type flags, sample lock/rate/counter.

API when enabled:
- create/apply/init/deinit/delete dnstap environment.
- apply log configuration.
- emit client query/response messages.
- emit resolver/forwarder outside query/response messages.

Role in group:
- Dormant optional telemetry interface retained from Unbound.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap_config.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap_config.h

Generated-style feature shim for dnstap.

Behavior:
- Exists so code can check `USE_DNSTAP` without directly including full `config.h`.
- Contains `#if 0 /* ENABLE_DNSTAP */`, so it does not define `USE_DNSTAP`.

Role in group:
- Confirms dnstap is disabled in this OpenBSD embedded Unbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dnstap/dnstap_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/Makefile.inc

Build fragment for Unbound iterator module sources.

Behavior:
- Adds `.PATH` for `libunbound/iterator`.
- Adds iterator-related source files to `SRCS`, including delegation points, do-not-query, forward zones, hints, private address handling, response typing, scrub logic, utilities, and main iterator.

Role in group:
- Wires iterator support into the embedded Unbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.c

Implementation of Unbound delegation points: NS names, target addresses, and selection lists for iterative resolution.

Allocation modes:
- Regional allocation for per-query delegation points.
- Malloc-backed `_mlc` variants for persistent configuration objects such as forward zones.

Core behavior:
- Create/copy/set delegation point name.
- Add NS names, target addresses, A rrsets, AAAA rrsets, and generic NS/A/AAAA rrsets.
- Avoid duplicate NS names and duplicate target addresses.
- Track whether NS names have usable A/AAAA data.
- Track bogus and lame/parent-side information.
- Maintain `target_list`, `usable_list`, and `result_list`.
- Build delegation points from DNS messages by finding NS rrsets in authority or answer sections and collecting relevant glue from answer/additional sections.
- Mark negative A/AAAA lookups for nameservers.
- Mark nameservers resolved when IPv4 or IPv6 is unavailable.
- Log delegation point summary and details.
- Compute memory usage.

Important semantics:
- `delegpt_add_target()` only accepts target addresses whose owner name matches an existing NS in the delegation point.
- `delegpt_add_addr()` can add address-only targets, used by configured forwarders.
- `delegpt_from_message()` treats a message as useful if it can construct a delegation point; it does not fully validate referral semantics.
- Parent-side/lame addresses are dispreferred but kept for fallback.

Role in group:
- Foundational data model used by iterator and forward-zone code for upstream server selection.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.h

Header defining Unbound delegation point structures and APIs.

Core structures:
- `struct delegpt`: delegated domain name, NS list, target/usable/result address lists, bogus flag, parent-side/fallback flags, upstream TCP/TLS flags, auth-zone marker, no-cache marker, allocation-mode marker.
- `struct delegpt_ns`: nameserver wire name, lookup counters, resolved/got4/got6 state, lame/parent-side state, TLS auth name, port.
- `struct delegpt_addr`: sockaddr target, attempt/selection RTT counters, bogus/lame/dnsseclame flags, TLS auth name, and list links.

API:
- Regional create/copy/name/add functions.
- Add NS/A/AAAA rrsets and parsed target addresses.
- Find NS or address.
- Count/log names and addresses.
- Move usable targets to result list.
- Count missing/total targets.
- Build from DNS message.
- Mark negative address lookups and IPv4/IPv6 unavailability.
- Malloc-backed create/free/add variants.
- Memory accounting and result-list helpers.

Role in group:
- Public contract for delegation point manipulation across iterator, hints, stubs, and forwards.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_delegpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.c

Implementation of iterator do-not-query address filtering.

Core behavior:
- `donotq_create()` allocates structure and regional allocator.
- `donotq_apply_cfg()` clears old regional data, initializes address tree, reads configured `donotqueryaddrs`, optionally adds localhost ranges, and initializes parent pointers.
- `donotq_str_cfg()` parses netblock strings with `netblockstrtoaddr()`.
- `donotq_lookup()` checks if an address matches a blocked span.
- `donotq_get_mem()` reports structure plus regional memory.

Default policy:
- If `cfg->donotquery_localhost` is set, adds `127.0.0.0/8`.
- Adds `::1` as well when IPv6 is enabled.

Role in group:
- Prevents iterator server selection from querying prohibited addresses such as localhost.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.h

Header for iterator do-not-query address storage.

Core structure:
- `struct iter_donotq`: regional allocator plus address-span RB tree.

API:
- create/delete.
- apply config.
- lookup blocked address.
- memory accounting.

Role in group:
- Interface used by iterator code to quickly reject upstream target addresses that must not be queried.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.c

Implementation of Unbound forward-zone storage and lookup.

Data model:
- Forward zones are stored in an RB tree ordered by class and domain-name label ordering.
- Each `iter_forward_zone` may contain a malloc-backed `delegpt`.
- Entries with `dp == NULL` are “holes” for stub/auth zones that should override broader forward zones.
- Parent pointers are computed after tree changes to support closest ancestor lookup.

Core behavior:
- Create/delete `iter_forwards` with RW lock.
- Parse forward zone names, forward-host names, and forward-address entries from config.
- Configure delegation-point flags: `has_parent_side_NS`, `no_cache`, `ssl_upstream`, and `tcp_upstream`.
- Warn about forward-host circular dependency when host lies below forwarded zone.
- Add holes for configured stub zones and auth zones.
- Apply config by replacing the tree under write lock.
- Exact lookup via `forwards_find()`.
- Closest-encloser forwarding lookup via `forwards_lookup()`.
- Root forward lookup and iteration over root entries by class.
- Add/delete forward zones and stub holes dynamically.
- Swap internal trees for reload.

Important semantics:
- `forward-first` clears `has_parent_side_NS`, allowing fallback to internet nameservers after forwarder failure.
- Stub/auth holes deliberately stop a broader forward from catching names that should be handled by more specific configured zones.
- Locking can be skipped with `nolock` when caller already holds the appropriate lock.

Role in group:
- Resolver policy component that routes selected domains to configured upstream forwarders instead of normal iteration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.h

Header for iterator forward-zone storage.

Core structures:
- `struct iter_forwards`: RW lock and RB tree.
- `struct iter_forward_zone`: tree node, wire-format name, label count, optional forwarder delegation point, parent pointer, and class.

API:
- create/delete/apply config.
- exact and closest-encloser lookup.
- root lookup and root-class iteration.
- memory accounting.
- comparator.
- add/delete zones.
- add/delete stub holes.
- swap trees.

Role in group:
- Public contract for forward-zone policy used by the iterator and reload/config paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.h -->