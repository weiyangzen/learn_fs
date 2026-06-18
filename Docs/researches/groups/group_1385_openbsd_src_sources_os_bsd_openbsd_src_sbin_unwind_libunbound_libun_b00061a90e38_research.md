# Group Research: group_1385_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_libun_b00061a90e38

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/openbsd-src`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.c

Implements the libunbound worker used by the library API to execute DNS resolution and validation in foreground, background thread/process, or caller-supplied event-loop mode.

Major responsibilities:
- Builds a worker-local `module_env` from `ub_ctx`, including scratch region/buffer, random state, SSL context, comm base, outside network object, and mesh.
- Supports foreground blocking queries via `libworker_fg()`.
- Supports asynchronous background operation via `libworker_bg()`, using a thread when enabled or `fork()` where threading is unavailable/disabled.
- Supports event-loop integration through `libworker_create_event()` and `libworker_attach_mesh()`.
- Serializes/deserializes async commands and answers through context/tube helpers.

Query flow:
- `setup_qinfo_edns()` builds wire-format qname, EDNS DO settings, and advertised UDP size.
- Foreground/event/background paths first check local zones and authoritative downstream zones for immediate answers.
- Otherwise, queries are attached to the mesh with callbacks for completion.
- Completion callbacks fill `ub_result`, copy packet data as needed, mark DNSSEC status, record bogus reasons, and handle rate-limit indicators.

Result handling:
- `libworker_enter_result()` parses a DNS packet into query/reply structures, extracts answer RR data, canonical name, rcode, NXDOMAIN state, security state, bogus state, and TTL.
- `fill_res()` copies packed RRset RDATA into libunbound’s public result arrays and computes minimum TTL across answer CNAME/answer rrsets.
- Background answers are queued back to the application via the result pipe unless canceled or shutting down.

Network integration:
- `libworker_send_query()` allocates an outbound entry in the module query region and calls `outnet_serviced_query()`.
- `libworker_handle_service_reply()` validates basic DNS reply shape and reports success/timeout/error back to mesh.

Cleanup and compatibility:
- Worker deletion tears down mesh, scratch storage, random state, SSL context, outside network, and comm base.
- Allocation cleanup clears rrset and message cache slabhashes for allocator ID reuse.
- Provides assertion-only fake daemon-worker callbacks so function-pointer whitelist/linkage expectations are satisfied in libunbound builds.

Filesystem/storage relevance:
- No filesystem implementation. Relevant as resolver infrastructure using shared caches, slabhash-backed DNS data, event loops, threads/forked workers, and careful ownership across shared `ub_ctx` state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.h

Internal header for the libunbound library worker.

Defines:
- `struct libworker`: per-worker state with thread number, owning `ub_ctx`, background/thread flags, quit flag, worker-local `module_env`, comm base, outside-network backend, random state pointer, and SSL context pointer.

Declares:
- `libworker_bg()` for background worker creation.
- `libworker_fg()` for blocking foreground resolution.
- `libworker_create_event()` / `libworker_delete_event()` for external event-loop workers.
- `libworker_attach_mesh()` for event-driven async query attachment.
- `libworker_alloc_cleanup()` for cache cleanup on allocator reuse.
- `libworker_enter_result()` for converting parsed DNS packets into public `ub_result`.

Role:
- Captures the private boundary between libunbound context/query code, the resolver mesh, and the outside network backend.
- Distinguishes libunbound worker APIs from daemon worker APIs declared in `worker.h`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libworker.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound-event.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound-event.h

Public libunbound header for integrating resolution with caller-provided event systems.

Defines:
- Event bit constants: timeout, read, write, signal, persist.
- `UB_EVENT_MAGIC` version guard for pluggable event objects.
- `struct ub_event_base_vmt`: virtual methods for event-base free, dispatch, loopexit, event creation, signal creation, and Windows WSA event registration.
- `struct ub_event_base`: magic plus base vtable.
- `struct ub_event_vmt`: methods to add/delete bits, set fd, free, activate/deactivate, manage timers/signals, handle Windows WSA events, and signal TCP would-block state.
- `struct ub_event`: magic plus event vtable.
- `ub_event_callback_type`: callback receiving user data, rcode, packet pointer/length, DNSSEC status, bogus reason, and rate-limit status.

Public API:
- `ub_ctx_create_ub_event()` creates a libunbound context on a generic pluggable event base.
- `ub_ctx_create_event()` creates a context on libevent’s `event_base`.
- `ub_ctx_set_event()` swaps the libevent base and cancels outbound queries.
- `ub_resolve_event()` submits an asynchronous resolution using the configured event base.

Role:
- Lets applications run libunbound state machines inside their own event loop without a worker thread or forked process.
- Documents that event callbacks receive internal buffers that must not be freed or modified.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound-event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound.h

Main public libunbound API header.

Defines:
- Version macros filled by build configuration.
- Opaque `struct ub_ctx`.
- `struct ub_result`: public query result with original qname/type/class, RDATA array and lengths, canonical name, rcode, answer packet, havedata/NXDOMAIN/security/bogus flags, bogus reason, rate-limit flag, and TTL.
- `ub_callback_type` for asynchronous `ub_resolve_async()`.
- `enum ub_ctx_err`: public error codes such as no error, socket, nomem, syntax, servfail, fork failure, after-finalize config change, init failure, pipe error, readfile error, and unknown async id.

Context/configuration API:
- Create/delete contexts.
- Set/get unbound.conf-style options.
- Load config files, resolv.conf, and hosts files.
- Configure forwarding, DNS-over-TLS forwarding, stub zones, debug output/level, trust anchors, trust-anchor files, RFC5011 autotrust files, and BIND-style trusted-keys files.
- Enable asynchronous threaded/forked behavior with `ub_ctx_async()`.

Resolution API:
- `ub_resolve()` for blocking resolution.
- `ub_resolve_async()` for callback-based async resolution.
- `ub_poll()`, `ub_wait()`, `ub_fd()`, and `ub_process()` for non-threaded async result processing.
- `ub_cancel()` cancels in-flight async queries.
- `ub_resolve_free()` releases results.
- `ub_strerror()` and `ub_version()` provide diagnostics/versioning.

Local authority helpers:
- Print local zones.
- Add/remove local zones.
- Add/remove local data.

Statistics:
- `struct ub_shm_stat_info` exposes shared-memory global stats and memory buckets.
- `struct ub_server_stats` exposes per-worker query, cache, protocol, DNSSEC, DNSCrypt, auth-zone, subnet, cachedb, RPZ, QUIC, and timeout counters.
- `struct ub_stats_info` wraps server stats plus mesh counters and reply timing data.

Role:
- This is API contract documentation and declarations, not implementation.
- It describes libunbound’s supported usage modes: blocking, nonblocking fd polling, threaded async, forked async, and shared-context threaded blocking.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/worker.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/worker.h

Declares worker callback and network service interfaces shared by libunbound worker code and daemon worker code.

Main declarations:
- `libworker_send_query()` and `worker_send_query()` send module-serviced outbound queries to authoritative/upstream servers.
- `libworker_handle_service_reply()` and `worker_handle_service_reply()` process network replies.
- `libworker_handle_control_cmd()` and `worker_handle_control_cmd()` process tube control messages.
- Foreground, background, and event mesh completion callbacks for libworker.
- Daemon worker callbacks for signal handling, client request handling, allocation cleanup, statistics/probe timers, accept start/stop, and remote-control accept/data handling.
- `remote_get_opt_ssl()` prints option values over SSL remote-control paths.

Role:
- Provides a common function-pointer surface expected by module code and callback whitelists.
- In `libworker.c`, daemon-only symbols are implemented as assertion stubs because the library worker does not accept client-facing daemon traffic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/worker.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/Makefile.inc

OpenBSD make fragment for the libunbound response-IP module.

Contents:
- Adds `${.CURDIR}/libunbound/respip` to `.PATH`.
- Adds `respip.c` to `SRCS`.

Role:
- Pulls response-IP support into the unwind/libunbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.c

Implements Unbound’s response-IP module, which inspects A/AAAA answers and applies configured actions when returned addresses match configured netblocks or RPZ response-IP triggers.

Data structures:
- `struct respip_addr_info`: copied matched address/netblock data for inform logging.
- `enum respip_state`: module state for initial processing and CNAME-subquery completion.
- `struct respip_qstate`: per-query response-IP state.

Configuration and storage:
- `respip_set_create()` builds a regional allocator, address tree, and rw lock.
- `respip_sockaddr_find_or_create()` and `respip_find_or_create()` manage address-tree nodes.
- Config application handles response-address tags, response-IP actions, and response-IP redirect data.
- Supports global response-IP config and per-view response-IP config.
- `respip_enter_rr()` validates redirect RR type against address family, rejects incompatible CNAME coexistence, creates rrsets, and inserts RDATA.
- `respip_copy_rrset()` deep-copies rrsets into a region, excludes RRSIGs, and normalizes memory layout.

Reply matching and rewriting:
- `respip_addr_lookup()` scans answer-section A/AAAA rrsets, validates RDATA length, converts addresses to sockaddr, and finds matching netblocks.
- `respip_rewrite_reply()` selects applicable action from view-specific data, global tag/action data, or RPZ zones.
- Tag-based redirect data can override configured node data.
- Actions can redirect, inform, deny/drop, refuse, synthesize NXDOMAIN/NODATA, pass through, or apply RPZ override behavior.
- Deny variants can mark `qstate->is_drop` so no response is sent.
- Redirect-to-CNAME actions can generate subqueries to complete the CNAME chain.

RPZ integration:
- Iterates auth-zone RPZ linked list under locks.
- Applies RPZ action overrides, CNAME override data, logging settings, disabled/pass-through behavior, and per-RPZ tags.
- Tracks `rpz_passthru` to stop later RPZ processing.

Module lifecycle:
- `respip_get_funcblock()` returns the module function block.
- `respip_operate()` passes new queries to the next module, rewrites final replies on module completion, and waits for subqueries when redirect CNAME completion is needed.
- `respip_inform_super()` merges CNAME target replies back into the original rewritten response.
- `respip_clear()` drops per-query module state.

CNAME handling:
- `generate_cname_request()` attaches a subquery for the redirect CNAME target.
- `respip_merge_cname()` appends target answer rrsets to the base reply, excluding RRSIGs from copied target rrsets and rejecting target replies that would themselves trigger response-IP action.

Logging/memory:
- `respip_inform_print()` emits inform/RPZ log lines with source address, matched response-IP netblock, action, qname, type, and class.
- `respip_set_get_mem()` reports set memory under read lock.
- `respip_set_swap_tree()` swaps prebuilt tree/region/tag metadata for updates.

Filesystem/storage relevance:
- No filesystem logic. Relevant as DNS response policy/cache-adjacent code with regional allocation, rbtrees, rw locks, per-view policy, and RPZ/auth-zone integration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.h

Header for the response-IP module.

Defines:
- `struct respip_set`: regional allocator, address rbtree, rw lock, shallow tag-name metadata, and tag count.
- `struct resp_addr`: address-tree node with node lock, tag bitlist, action, and optional local-data rrset.
- `struct respip_client_info`: client tag/action/data attributes and view/view-name context.
- `struct respip_action_info`: selected action, RPZ flags, log name, CNAME override flag, and matched address info pointer.

Declares:
- Set creation/deletion and config application for global and view response-IP data.
- `respip_rewrite_reply()` for applying response-IP/RPZ actions to replies.
- `respip_merge_cname()` for completing redirect CNAME chains.
- Module function block and lifecycle functions.
- Test/introspection helpers for tree access, action lookup, rrset lookup, emptiness, and memory accounting.
- Inform logging helper.
- Address lookup/create/delete and RR insertion helpers.
- `respip_copy_rrset()` and `respip_set_swap_tree()`.

Role:
- Public internal contract between response-IP module, local-zone/tag code, view code, auth-zone/RPZ code, and tests.
- Documents ownership expectations for shallow-copied rrsets and region-allocated rewritten replies.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/respip/respip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/Makefile.inc

OpenBSD make fragment for libunbound service modules.

Contents:
- Adds `${.CURDIR}/libunbound/services` to `.PATH`.
- Adds service sources: `authzone.c`, `listen_dnsport.c`, `localzone.c`, `mesh.c`, `modstack.c`, `outbound_list.c`, `outside_network.c`, `rpz.c`, and `view.c`.

Role:
- Includes resolver service-layer implementation files in the unwind/libunbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.h

Header for locally hosted authoritative zones used by the iterator and downstream answer path.

Major structures:
- `struct auth_zones`: shared auth-zone container with zone tree, transfer tree, downstream flag, RPZ linked-list head, and RPZ lock.
- `struct auth_zone`: zone identity, lock, authoritative data tree, zonefile/fallback flags, slave/upstream/downstream flags, ZONEMD settings, RPZ pointer, online ZONEMD callback state, delete state, and RPZ list links.
- `struct auth_data`: one owner name and linked rrsets.
- `struct auth_rrset`: typed authoritative RRset data.
- `struct auth_xfer`: zone-transfer coordinator with next-probe, SOA probe, transfer tasks, NOTIFY state, allowed-notify list, current serial/timers, and lease/expiry state.
- `struct auth_nextprobe`, `auth_probe`, and `auth_transfer`: worker-owned event-loop tasks for scheduled refresh, SOA probes, and AXFR/IXFR/HTTP transfer.
- `struct auth_master`, `auth_addr`, and `auth_chunk`: upstream master config, resolved addresses, and transfer data chunks.

Zone management API:
- Create, configure, cleanup, delete, and memory-account auth zones.
- Apply config and read/write zonefiles.
- Find zones/transfer records by name/class.
- Create zones and transfer records under locks.
- Configure zonefile and fallback behavior.
- Determine whether fallback to normal recursion is allowed.

Answering/query integration:
- `auth_zones_lookup()` answers iterator-side queries from local authoritative data or signals fallback.
- `auth_zones_downstream_answer()` creates downstream authoritative answers for clients.
- `auth_zones_find_zone()` finds closest enclosing local auth zone.

Transfer/notify API:
- Processes NOTIFY messages, parses SOA serials, starts probe sequences, compares RFC1982 serials, sets masters, and exposes probe/transfer callbacks.
- Supports UDP SOA probe callbacks, TCP/HTTP transfer callbacks, timers, and mesh callbacks for resolving master hostnames.
- Provides pickup/disown/delete helpers so transfer tasks are attached to the correct worker event loop.

ZONEMD:
- Defines supported ZONEMD scheme and SHA-384/SHA-512 algorithm constants.
- Declares hash generation, digest checking, full verification, DNSKEY lookup callback, and worker pickup for online verification.

RPZ role:
- Auth zones can contain RPZ data and are linked under `auth_zones.rpz_first`.
- Response-IP processing uses this RPZ list to apply policy based on returned IPs.

Filesystem/storage relevance:
- Not filesystem code, but it manages persistent zonefile paths and locally stored authoritative DNS data with rbtrees, locks, event-loop transfer tasks, and optional write-back.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/Makefile.inc

OpenBSD make fragment for libunbound cache services.

Contents:
- Adds `${.CURDIR}/libunbound/services/cache` to `.PATH`.
- Adds `dns.c`, `infra.c`, and `rrset.c` to `SRCS`.

Role:
- Includes DNS message cache, infrastructure cache, and RRset cache implementations in the unwind/libunbound build.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.c

Implements DNS message-cache services on top of Unbound’s message cache and RRset cache.

Storage path:
- `dns_cache_store()` copies regional reply data into malloc/cache-owned storage, fixes reply flags for cache use, and stores either only referral rrsets or a full message plus rrsets.
- `dns_cache_store_msg()` converts relative TTLs to absolute TTLs, stores rrsets, handles TTL-zero messages, removes stale message-cache entries for TTL-zero answers, sorts rrset refs, and inserts message replies into the slabhash message cache.
- `store_rrsets()` updates/inserts rrsets into the RRset cache, prefers better cached rrsets when available, and adjusts message TTL/prefetch/serve-expired TTL to the minimum cached rrset TTL.

Lookup path:
- `msg_cache_lookup()` hashes query info plus flags, returns a locked message-cache entry if present and unexpired.
- `dns_cache_lookup()` first tries exact message-cache hits, then synthesizes answers from cached DNAME, CNAME, DS/DNSKEY rrsets, harden-below-NXDOMAIN data, or common RRsets for type ANY.
- `tomsg()` converts cached message entries back into region-allocated `dns_msg` replies with relative TTLs, checking rrset availability, CNAME-chain validity, and secure-message rrset security consistency.
- Supports serve-expired logic by allowing expired messages only when configured and permitted by reply metadata.

Delegation support:
- `dns_cache_find_delegation()` finds closest cached NS rrset, creates a delegation point, optionally synthesizes a referral message, adds DS/NSEC data, and fills A/AAAA glue from cache.
- `find_closest_of_type()` walks upward through qname labels looking for cached NS or DNAME rrsets, with optional checks that no expired rrsets exist above the found point.
- `cache_fill_missing()` fills missing nameserver A/AAAA addresses and negative address-cache entries into an existing delegation point.
- `find_add_addrs()` and `find_add_ds()` populate referral additional/authority sections from rrset/message caches.

Message synthesis:
- `dns_msg_create()` creates an unpacked region-allocated DNS message with a fixed rrset capacity.
- `dns_msg_authadd()` and `dns_msg_ansadd()` copy rrsets into authority/answer sections and update TTL.
- `rrset_msg()` builds a one-rrset answer from cached CNAME/DS/DNSKEY-like rrsets.
- `synth_dname_msg()` builds DNAME plus synthesized CNAME responses, handles TTL-zero upstream DNAME grace, YXDOMAIN on excessive synthesized name length, and carries DNAME security state to the caller.
- `fill_any()` returns either RFC8482-style NOTIMPL when `deny_any` is configured or a limited set of cached common RR types.

Serve-expired and prefetch:
- When serve-expired is enabled, `dns_cache_store()` avoids overwriting useful expired validated entries with unchecked validator-pending data, while updating no-recursion retry TTLs for error responses.
- `dns_cache_prefetch_adjust()` extends a cached message’s prefetch TTL under write lock.

Filesystem/storage relevance:
- No filesystem code. This is core cache infrastructure: slabhash message cache, RRset cache, TTL conversion, regional/malloc ownership transitions, lock ordering, and synthesis of resolver-visible DNS messages from cached records.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.h

Header for DNS cache services.

Defines:
- `DNSCACHE_STORE_EXPIRED_MSG_CACHEDB`: store-policy flag allowing zero-TTL messages for cachedb-style behavior.
- `struct dns_msg`: region-allocated query info plus reply info wrapper.

Declares:
- `dns_cache_store()` and `dns_cache_store_msg()` for storing messages/rrsets into shared caches.
- `dns_cache_find_delegation()` for reconstructing delegation points and optional referral messages from cache.
- `tomsg()` for converting cached message entries to region-allocated messages with relative TTLs.
- `dns_msg_deepcopy_region()` for deep-copying messages into a region.
- `dns_cache_lookup()` for full cache lookup and synthesis.
- `cache_fill_missing()` for filling nameserver address data into delegations.
- `dns_msg_create()`, `dns_msg_authadd()`, and `dns_msg_ansadd()` for building unpacked cache responses.
- `dns_cache_prefetch_adjust()` to adjust prefetch timing.
- `msg_cache_lookup()` and `msg_cache_remove()` for lower-level message-cache access.

Role:
- Defines the contract between iterator/validator/module code and the DNS cache implementation.
- Makes explicit that returned cache messages are region allocated and that `msg_cache_lookup()` returns locked entries requiring caller unlock.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.h -->