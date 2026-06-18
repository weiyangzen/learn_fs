# Group Research: group_1387_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_servi_972514a363e9

Scope: `Docs/research_subset_a.md`, OpenBSD source tree subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.h

## Role

Declares the service-facing listener API for Unbound/unwind DNS client ingress. It covers shared listening sockets, per-worker comm points, UDP/TCP/TLS/HTTP/2/DoQ listeners, TCP pipelining reply bookkeeping, socket creation helpers, DSCP setup, and conditional DNS-over-QUIC state structures.

## Main Types

- `struct listen_dnsport`: per-thread listener container with event base, shared UDP buffer, optional DNSCrypt UDP buffer, and linked comm point list.
- `struct listen_list`: singly linked list of `comm_point` listener events.
- `enum listen_type`: listener transport discriminator for UDP, TCP, ancillary UDP, TLS, DNSCrypt variants, HTTP over TLS, and DoQ.
- `struct unbound_socket`: startup socket metadata: address, descriptor, family, and ACL.
- `struct listen_port`: shared opened listener port list, including fd, transport type, PROXYv2 flag, and `unbound_socket`.
- `struct tcp_req_info`: tracks outstanding and completed DNS requests over one TCP/TLS channel, including open mesh states and queued response buffers.
- `struct tcp_req_open_item` / `struct tcp_req_done_item`: linked-list entries for outstanding mesh references and completed wire responses.
- Conditional `struct doq_table`, `doq_timer`, `doq_conn_key`, `doq_conn`, `doq_conid`, and `doq_stream`: QUIC/DoQ shared connection table, timers, connection IDs, connection state, and per-stream input/output buffers.

## Public API Surface

- Listener lifecycle: `listening_ports_open`, `listening_ports_free`, `listen_create`, `listen_delete`, `listen_setup_locks`, `listen_desetup_locks`, `listen_list_delete`, `listen_get_mem`.
- Listener flow control: `listen_stop_accept`, `listen_start_accept`.
- Socket helpers: `create_udp_sock`, `create_tcp_accept_sock`, `create_local_accept_sock`, `resolve_interface_names`, `set_ip_dscp`, `verbose_print_unbound_socket`.
- TCP multiplexing helpers: `tcp_req_info_create`, `tcp_req_info_delete`, `tcp_req_info_clear`, `tcp_req_info_remove_mesh_state`, `tcp_req_info_handle_writedone`, `tcp_req_info_handle_readdone`, `tcp_req_info_add_meshstate`, `tcp_req_info_send_reply`, `tcp_req_info_handle_read_close`, stream buffer accounting helpers.
- HTTP/2 helpers under `HAVE_NGHTTP2`: callback creation, stream cleanup, and DNS response submission.
- DoQ helpers under `HAVE_NGTCP2`: SSL context/table lifecycle, connection/stream create-delete, rb-tree comparators, connection ID association, packet receive/write/close, timer tree/list manipulation, write-interest lists, QUIC buffer accounting, and test client callbacks.

## Important Behavior and Dependencies

- The header is transport glue between network event code (`util/netevent.h`), ACLs, worker callbacks, mesh state replies, TCP connection limit lists, dnstap, TLS contexts, HTTP/2, and QUIC/ngtcp2.
- UDP uses a shared packet buffer because a datagram is processed one at a time per listener context.
- TCP/TLS request state is explicit because multiple outstanding DNS queries may exist on a single channel and replies may complete out of order.
- DoQ support is guarded by compile-time feature macros and uses rbtrees plus locks for connection lookup by endpoint/DCID and by connection ID.

## Research Notes

- This file is declaration-only; implementation details live in corresponding listener/network service C files.
- The DoQ declarations are substantial and include concurrency-sensitive shared table state, buffer accounting, timer multiplexing, and write-interest lists.
- Socket creation helpers expose platform-sensitive options such as `SO_REUSEPORT`, transparent bind, freebind, systemd socket activation, MSS, TCP_NODELAY/QUICKACK, and DSCP.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.c

## Role

Implements Unbound's local authoritative zone service. It parses and stores configured `local-zone` and `local-data` entries, adds default special/reverse/AS112 zones, supports tags and per-netblock overrides, answers matching queries locally, and supports dynamic add/delete of zones and records.

## Storage Model

- `local_zones_create` initializes a locked rbtree of `local_zone` objects.
- Each `local_zone` owns a regional allocator for all local data, an rbtree of `local_data` names, linked `local_rrset` entries per name, optional tag bitmap, optional address override tree, and cached SOA pointers for negative answers.
- `local_zone_cmp` sorts zones by DNS class and hierarchical dname order; `local_data_cmp` sorts data names canonically.
- Parent pointers are maintained by `lz_init_parents`, `find_closest_parent`, and dynamic update helpers so lookup can climb from closest less/equal rbtree entries to covering zones.

## Configuration Loading

- `lz_enter_zone` parses textual zone name/type and inserts a zone, returning it write-locked.
- `lz_enter_rr_str` parses RR strings, finds a covering zone, and inserts data.
- `local_zone_enter_defaults` adds built-in localhost, reverse localhost, RFC special-use, and AS112 empty zones unless disabled or excluded by `nodefault`.
- `lz_setup_implicit` creates transparent zones for `local-data` entries without explicit covering `local-zone` statements, including handling non-IN classes by repeating setup.
- `lz_enter_zone_tags` and `lz_enter_overrides` apply tag bitmaps and netblock-specific local-zone type overrides.
- `local_zones_apply_cfg` orchestrates explicit zones, defaults, overrides, implicit zones, parent setup, tags, data insertion, and cleanup of consumed config lists.

## Record Handling

- `rrstr_get_rr_content` and `get_rr_nameclass` parse text RRs into wire format and expose owner/type/class/TTL/RDATA.
- `new_local_rrset`, `rrset_insert_rr`, and `local_zone_enter_rr` build packed rrset structures in the zone region.
- Duplicate RRs are ignored by content comparison.
- Redirect zones reject incompatible CNAME coexistence and require data at the zone apex.
- SOA records at the zone apex are tracked in `z->soa`, and `lz_mark_soa_for_zone` builds an artificial `soa_negative` RRset with TTL clamped to SOA.MINIMUM for negative responses.
- Empty nonterminals are created recursively by `lz_find_create_node`.

## Query Answering

- `local_zones_answer` first checks view-local zones, honors `noview`, then falls back to global tagged lookup.
- `lz_type` applies per-client netblock overrides before tag-action overrides.
- `local_data_answer` returns exact local data, redirect apex data rewritten to the query name, tag-specific redirect data, or deferred local CNAME alias state.
- Wildcard CNAME targets are synthesized into per-query local aliases and checked for maximum DNS name length.
- `local_zones_zone_answer` handles zone-type fallback behavior:
  - `deny`/`always_deny`/`inform_deny`: drop by clearing the output buffer.
  - `refuse`/`always_refuse`: authoritative REFUSED.
  - `static`, `redirect`, `inform_redirect`, `always_nxdomain`, `always_nodata`, UDP `truncate`: authoritative NXDOMAIN/NODATA/truncated responses, using negative SOA when available.
  - `transparent`, `typetransparent`, `inform`, `always_transparent`, `block_a`: pass through as appropriate.
  - `always_null`: synthetic `0.0.0.0`, `::0`, or NODATA.
- Local replies run inplace reply callbacks and may attach EDE options when configured.

## Dynamic Updates and Maintenance

- `local_zones_add_zone` and `local_zones_del_zone` update the zone tree and repair child parent pointers.
- `local_zones_add_RR` creates a transparent zone if no covering zone exists, then inserts the RR.
- `local_zones_del_data` removes DS separately with DS lookup semantics, clears other rrsets, resets zone SOA pointers when needed, and prunes terminal empty-nonterminal nodes.
- `local_zones_get_mem` accounts zone structure, names, taglist, and regional allocations.
- `local_zones_swap_tree` swaps rbtrees for prebuilt data replacement.

## Research Notes

- Locking is layered: the global zone tree lock protects tree membership and structural zone fields; each zone lock protects per-zone data and runtime metadata.
- Regional allocation simplifies lifetime but means dynamic deletions do not reclaim per-record memory until the entire zone is replaced or deleted.
- DS lookups intentionally move to a parent zone for normal add/remove semantics, with a special answering exception for `always_refuse` at a zone cut.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.h

## Role

Public interface and data model for the local authoritative zone service implemented in `localzone.c`.

## Main Types

- `enum localzone_type`: defines all local-zone behaviors: unset, deny, refuse, static, transparent, typetransparent, redirect, nodefault, inform variants, always-transparent/refuse/nxdomain/nodata/deny/null, noview, truncate, and invalid.
- `struct local_zones`: locked rbtree of local zones.
- `struct local_zone`: one authoritative local zone, including rbtree node, parent pointer, wire-format name, class, lock, behavior type, tag bitmap, optional address override tree, regional allocator, data tree, and SOA/negative-SOA cached rrsets.
- `struct local_data`: one domain name within a local zone, with exact wire name and linked rrsets; `rrsets == NULL` represents an empty nonterminal.
- `struct local_rrset`: linked wrapper around `ub_packed_rrset_key`.
- `struct local_zone_override`: address-tree node mapping client netblocks to override zone type.
- `enum respip_action`: shares values with local-zone types for response-IP/RPZ-style policy actions.

## API Categories

- Lifecycle/config: `local_zones_create`, `local_zones_delete`, `local_zones_apply_cfg`, `local_zone_enter_defaults`.
- Lookup/debug: `local_zones_tags_lookup`, `local_zones_lookup`, `local_zones_find`, `local_zones_find_le`, `local_zones_print`.
- Answering: `local_zones_answer`, `local_zones_zone_answer`, `local_data_answer`.
- Type conversion: `local_zone_str2type`, `local_zone_type2str`.
- Mutation: `local_zones_add_zone`, `local_zones_del_zone`, `local_zones_add_RR`, `local_zones_del_data`, `local_zone_enter_rr`, `local_rrset_remove_rr`.
- Parsing/building helpers: `parse_dname`, `rrstr_get_rr_content`, `rrset_insert_rr`.
- Tag policy: `local_data_find_tag_datas`, `local_data_find_tag_action`.
- Testing/internal exposure: `lz_enter_zone`, `lz_init_parents`.
- Memory/swap: `local_zones_get_mem`, `local_zones_swap_tree`.

## Contracts and Semantics

- Callers must respect locking notes: many lookup and mutation helpers require the zones tree or returned zone to be locked by the caller.
- `local_zones_answer` may return true without an encoded answer when `qinfo->local_alias` is set; the caller must complete and encode the alias chain.
- `local_zones_answer` can signal a deliberate drop by returning true with an empty buffer.
- `local_zone_nodefault` is a configuration-only value, not a serving behavior.

## Research Notes

- The header documents how local aliases are allocated and when callers need deep copies.
- `respip_action` intentionally aliases local-zone behavior values so access-control tag actions can be shared between local zones and response-IP logic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.c

## Role

Implements the per-worker resolver mesh: a graph of active DNS query states, shared client replies/callbacks, subquery dependencies, runnable states, module-stack execution, response delivery, stale-answer serving, RPZ/response-IP postprocessing, and mesh statistics.

## State Identity and Creation

- `mesh_state_compare` keys states by uniqueness pointer, priming flag, validation-recursion flag, RD/CD flags, query info, and response-IP client info.
- `client_info_compare` prevents unsafe state sharing when tag lists, tag actions, tag data pointers, or view names differ.
- `mesh_state_create` obtains a regional allocator, copies query name/client info into it, initializes module qstate fields, module ext states, EDNS option lists, and mesh rb-tree nodes.
- `mesh_state_make_unique` disables aggregation by making the state key include its own pointer.

## Mesh Lifecycle and Limits

- `mesh_create` initializes `run` and `all` rbtrees, histogram, query-buffer backup, reply-state limits, jostle timeout, and counters.
- `mesh_delete` and `mesh_delete_all` delete all active states, with `mesh_delete_all` accounting unsent replies as dropped.
- `mesh_make_new_space` enforces `num_queries_per_thread`; it may jostle the oldest eligible reply state, notify superstates with SERVFAIL, delete the state, and restore the incoming query buffer.
- `mesh_jostle_exceeded` checks all active query count against the reply-state limit.

## Client, Callback, and Prefetch Entry Points

- `mesh_new_client` handles incoming client queries:
  - Applies infra wait limits.
  - Reuses an existing mesh state unless EDNS/options require uniqueness.
  - Enforces reply-address limits.
  - Adds `mesh_reply` state, TCP request linkage, HTTP/2 stream linkage, serve-expired timer, wait-limit accounting, and jostle/forever list placement.
  - Starts the run loop for newly created states.
- `mesh_new_callback` attaches callback consumers with similar state reuse/create logic and no reply-count hard limit.
- `mesh_new_prefetch` schedules detached recursive refreshes, forcing RD and optionally preserving ECS/subnet information when compiled with `CLIENT_SUBNET`.
- `mesh_report_reply` converts outbound network completion into module events and resumes the relevant mesh state.

## Dependency Graph

- `mesh_add_sub` finds or creates a subquery state, queues new states in `run`, and checks cycles when reusing an existing state.
- `mesh_attach_sub` attaches super/sub references and updates detached-state accounting.
- `mesh_state_attachment` inserts symmetric region-allocated refs into super `sub_set` and sub `super_set`.
- `mesh_detach_subs` removes all subquery relationships for a qstate and repairs detached counters.
- `mesh_detect_cycle` and helper recursion bound cycle detection by `MESH_MAX_SUBSUB`.
- `mesh_walk_supers` makes superstates runnable, calls module `inform_super`, and copies relevant state upward.

## Module Run Loop

- `mesh_run` repeatedly calls the current module's `operate`, clears transient reply/scratch state, reads module ext state, and delegates transition decisions to `mesh_continue`.
- `mesh_continue` handles:
  - Activation loop guard via `MESH_MAX_ACTIVATION`.
  - Passing to next modules for `module_wait_module` / `module_restart_next`.
  - Error conversion to SERVFAIL, query completion, super notification, and state deletion.
  - Finished-state backtracking to prior modules or final response handling at module 0.
  - Refetch scheduling after answer completion when `need_refetch` is set.

## Response Delivery

- `mesh_query_done` stops serve-expired timers, optionally tries stale cache on SERVFAIL, logs servfail details, generates DNS Error Reporting subqueries when configured, drops stale UDP replies past discard-timeout, logs response-IP/RPZ inform actions, sends replies, runs callbacks, and updates mesh accounting.
- `mesh_send_reply` handles per-client response encoding:
  - Applies RPZ TCP-only truncation for UDP.
  - Converts bogus/failed secure answers to SERVFAIL when validation is required.
  - Reuses a previously encoded response only when EDNS flags/options and alias state are safe to share.
  - Runs inplace callbacks, attaches EDE for validation failures, encodes DNS answers/errors, sends comm replies, updates infra wait-limit, timing histogram, extended stats, and optional reply logs.
- `mesh_do_callback` builds callback responses or callback SERVFAIL/error results and passes security status/reason/ratelimit information.
- `mesh_state_add_reply` deep-copies EDNS options, qname, HTTP/2 stream pointer, and local CNAME alias data into the mesh state region.
- `mesh_state_add_cb` stores callback metadata and EDNS option copies.
- `mesh_state_remove_reply` removes all replies for a comm point, with HTTP/2 stream cleanup and accounting fixes.
- `mesh_remove_callback` removes a matching callback consumer and updates reply/detached counters.

## Serve-Expired and DNS Error Reporting

- `mesh_serve_expired_init` creates per-state serve-expired data and timer.
- `mesh_serve_expired_lookup` performs cache lookup, detects expired TTL, reconstructs `dns_msg`, and rejects bogus/unchecked entries when validation is required.
- `mesh_serve_expired_callback` tries to answer from stale cache, applies response-IP/RPZ logic, follows one alias completion pass, attaches Stale Answer EDE when configured, sends replies/callbacks, and updates expired/RPZ stats.
- `mesh_respond_serve_expired` triggers the same callback path for immediate SERVFAIL fallback.
- `dns_error_reporting` implements RFC9567-style report-query synthesis when EDE and Report-Channel data are available, creating a TXT subquery under `_er...`.

## Cleanup and Stats

- `mesh_state_cleanup` deletes serve-expired timers, drops unsent replies/callbacks with SERVFAIL, removes HTTP/2 backreferences, deinitializes module per-state data, and releases the regional allocator.
- `mesh_state_delete` detaches subqueries, removes list membership, fixes reply/detached counters, removes reverse super refs, deletes from run/all trees, and cleans up the state.
- `mesh_stats`, `mesh_stats_clear`, `mesh_log_list`, and `mesh_get_mem` provide operational accounting and diagnostics.

## Research Notes

- Mesh state is intentionally per-thread; no locks appear in this implementation path.
- Correct accounting is delicate: `num_reply_addrs`, `num_reply_states`, `num_detached_states`, forever/jostle lists, HTTP/2 stream pointers, TCP request info, and infra wait-limit counters are updated across several early-return and cleanup paths.
- Regional allocation means many per-state helper entries are not individually freed; deletion is by qstate region release.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.h

## Role

Defines the resolver mesh data structures and public functions used by workers and modules to create, share, run, attach, detach, answer, and delete active DNS query states.

## Main Types

- `struct mesh_area`: per-worker mesh root containing module stack copy, module environment, runnable/all query rbtrees, reply/detached counters, jostle/forever lists, stats, histogram, query-buffer backup, and response-IP/RPZ flags.
- `struct mesh_state`: one active query state, with rb-tree nodes, embedded `module_qstate`, reply/callback lists, first-reply time, super/sub rbtree sets, activation count, linked-list membership, uniqueness marker, and sent flag.
- `struct mesh_state_ref`: rbtree reference wrapper used for super/sub dependency sets.
- `struct mesh_reply`: per-client reply metadata: copied comm reply, EDNS, start time, original ID/flags/qname, local alias copy, and optional HTTP/2 stream.
- `mesh_cb_func_type` and `struct mesh_cb`: callback consumer interface and callback metadata.

## Constants

- `MESH_MAX_ACTIVATION`: max module activations before treating a state as looping.
- `MESH_MAX_SUBSUB`: max recursive dependency scan size for cycle detection.

## API Categories

- Worker-facing entry points: `mesh_create`, `mesh_delete`, `mesh_new_client`, `mesh_new_callback`, `mesh_new_prefetch`, `mesh_report_reply`.
- Module environment helpers: `mesh_detach_subs`, `mesh_attach_sub`, `mesh_add_sub`, `mesh_query_done`, `mesh_walk_supers`, `mesh_state_delete`.
- Mesh internals exposed for implementation/tests: `mesh_state_create`, `mesh_state_make_unique`, `mesh_state_cleanup`, `mesh_delete_all`, `mesh_area_find`, `mesh_state_attachment`, `mesh_state_add_reply`, `mesh_state_add_cb`, `mesh_run`.
- Diagnostics/accounting: `mesh_stats`, `mesh_stats_clear`, `mesh_log_list`, `mesh_get_mem`.
- Dependency/list/limit helpers: `mesh_detect_cycle`, `mesh_state_compare`, `mesh_state_ref_compare`, `mesh_make_new_space`, `mesh_list_insert`, `mesh_list_remove`, `mesh_state_remove_reply`, `mesh_jostle_exceeded`.
- Serve-expired helpers: `mesh_serve_expired_callback`, `mesh_serve_expired_lookup`, `mesh_respond_serve_expired`.
- Callback removal: `mesh_remove_callback`.

## Contracts and Semantics

- Mesh states aggregate equivalent queries unless EDNS or client policy requires uniqueness.
- Reply states are bounded and may be split into run-to-completion "forever" states and jostle-eligible states.
- Subquery edges must remain symmetric between a super state's `sub_set` and a sub state's `super_set`.
- Reply consumers and callback consumers both contribute to reply address accounting.

## Research Notes

- The header documents that each `mesh_state` is region-allocated using the qstate region; all dependent structures are expected to share that lifetime.
- The interface is central to module execution: modules attach subqueries, wait, finish, and are informed through this mesh rather than directly managing recursion scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.c

## Role

Implements configuration, factory lookup, startup/init/deinit, reload validation, and memory introspection for Unbound's ordered module stack.

## Main Behavior

- `count_modules` counts whitespace-separated module names in `module_conf`.
- `modstack_init` and `modstack_free` initialize/free the dynamic array of `module_func_block*`.
- `modstack_config` validates module count, allocates the function-block array, parses each configured module with `module_factory`, and reports unknown/uncompiled modules.
- `module_list_avail` returns the statically compiled module names in execution order availability: `dns64`, optional `python`, optional `dynlib`, optional `cachedb`, optional `ipsecmod`, optional `subnetcache`, optional `ipset`, then `respip`, `validator`, `iterator`.
- `module_funcs_avail` maps the names to each module's `*_get_funcblock` provider.
- `module_factory` skips leading whitespace, matches a configured token by prefix against available module names, advances the caller's string pointer, and returns the function block.

## Lifecycle

- `modstack_call_startup` requires an empty stack, configures it, then calls optional module `startup` hooks.
- `modstack_call_init` verifies reload ordering against `module_conf`, rejects reordered modules that have startup/destartup hooks, rebuilds the stack if only restartable modules changed, clears `env->need_to_validate`, and calls each module `init`.
- `modstack_call_deinit` calls every module `deinit`.
- `modstack_call_destartup` calls optional module `destartup`.

## Utility

- `modstack_find` returns a module index by exact name.
- `mod_get_mem` finds a module by name in the active mesh stack and calls its `get_mem` hook.

## Research Notes

- Function pointer calls are guarded through `fptr_wlist` checks before invocation.
- Module matching uses `strncmp` with module-name length after skipping whitespace; the surrounding parsing assumes whitespace-separated config tokens.
- Reload behavior explicitly distinguishes modules that require startup/destartup from modules that can be reconfigured by rebuilding the stack.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.h

## Role

Declares the module stack abstraction used by the mesh and daemon environment.

## Main Type

- `struct module_stack`: stores `num` modules and an array of borrowed `struct module_func_block*` pointers.

## Public API

- `modstack_init`: set an empty stack.
- `modstack_free`: free the module function-block pointer array and reset state.
- `modstack_call_startup`: configure an empty stack and run module startup hooks.
- `modstack_config`: parse `module_conf` into a module function-block array.
- `module_factory`: map one config token to a module function block and advance the parse pointer.
- `module_list_avail`: list compiled-in module names.
- `modstack_call_init`: initialize modules and validate reload ordering.
- `modstack_call_deinit`: deinitialize modules.
- `modstack_call_destartup`: run module shutdown hooks for modules with startup resources.
- `modstack_find`: locate a module index by name.
- `mod_get_mem`: query a named module's memory usage.

## Research Notes

- The header makes clear that the stack stores references to module function blocks, not owned module instances.
- `MAX_MODULE` and the `module_func_block` contract are supplied by the broader Unbound module framework.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.c

## Role

Implements a small doubly linked list used by modules to track outbound serviced queries currently outstanding to authoritative/upstream servers.

## Functions

- `outbound_list_init`: initializes an empty list by setting `first = NULL`.
- `outbound_list_clear`: walks all entries, stops each serviced query through `outnet_serviced_query_stop(p->qsent, p)`, then reinitializes the list.
- `outbound_list_insert`: inserts an entry at the head and fixes `prev` links.
- `outbound_list_remove`: stops the associated serviced query, unlinks the entry from the list, and leaves memory reclamation to the owning region/lifetime.

## Dependencies

- Includes `services/outside_network.h` for `outnet_serviced_query_stop`.
- The list entries connect outbound network service state back to the `module_qstate` that issued them.

## Research Notes

- The implementation comments say entries are region allocated, so removal does not free memory.
- `outbound_list_remove` tolerates `NULL` entries.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.h

## Role

Declares the outbound serviced-query tracking list used by module-specific query state.

## Main Types

- `struct outbound_list`: owner-side list head containing `first`.
- `struct outbound_entry`: doubly linked entry containing `next`, `prev`, the sent `serviced_query`, and the originating `module_qstate`.

## Public API

- `outbound_list_init`: initialize caller-owned list storage.
- `outbound_list_clear`: stop and remove all serviced queries in the list.
- `outbound_list_insert`: insert a caller-allocated entry.
- `outbound_list_remove`: stop and unlink one entry.

## Research Notes

- The header says callers allocate entries; the C implementation assumes they are usually tied to a broader region/lifetime and are not individually freed on removal.
- This list is part of per-module qstate bookkeeping, not a global outbound scheduler.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.h -->