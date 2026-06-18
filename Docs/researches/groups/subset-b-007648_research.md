# subset-b-007648 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/config.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/config.c

## Purpose

`config.c` is the kernel-side LNet configuration parser and local network object constructor. It turns legacy module strings such as `networks`, `routes`, and `ip2nets` into `struct lnet_net`, `struct lnet_ni`, route, and interface-selection state, and it exposes helpers that LNDs and dynamic configuration paths use to allocate/free NIs, bind interfaces, check link status, and select an enumerated inet interface for a configured NID.

The file is mostly initialization/configuration code rather than packet fast path. Its persistent state is in the live `the_lnet` topology: net lists, NI lists, CPT restrictions, route table entries, per-NI net namespace references, health/fatal-link flags, and route/NI allocation side effects.

## Important APIs, Types, and Functions

- `struct lnet_text_buf` is a temporary parser allocation used for route and `ip2nets` token expansion. Global `lnet_tbnob` bounds cumulative scratch allocation to `LNET_MAX_TEXTBUF_NOB`, and `LNET_SINGLE_TEXTBUF_NOB` bounds each token.
- `lnet_net_unique()` and `lnet_ni_unique_net()` enforce duplicate-network and duplicate-interface checks within supplied lists.
- `lnet_net_append_cpts()` and `lnet_net_remove_cpts()` maintain `net->net_cpts`, `net->net_ncpts`, and `the_lnet.ln_cpt_restricted_count` as NIs with restricted CPT arrays are added and removed.
- `lnet_net_alloc()`, `lnet_net_free()`, `lnet_ni_alloc()`, `lnet_ni_alloc_w_cpt_array()`, `lnet_ni_free()`, and `lnet_ni_add_interface()` create and destroy `lnet_net`/`lnet_ni` objects, allocate per-CPT NI refs and TX queues, capture the current net namespace, and attach new NIs to `net_ni_added`.
- `lnet_parse_networks()` parses the legacy `networks` string grammar: network name, optional interface list in parentheses, optional CPT expression in brackets on either the net or individual interface.
- `lnet_parse_routes()` parses legacy route strings into calls to `lnet_add_route()`. It supports comments/separators, bracket expansion, optional hop count, and per-gateway selection priority after `:`.
- `lnet_parse_ip2nets()` enumerates local inet devices, matches address expressions from `ip2nets`, then returns a synthesized networks string through `lnet_match_networks()`.
- `lnet_set_link_fatal_state()`, `lnet_get_link_status_locked()`, `lnet_get_link_status()`, and `lnet_inet_select()` expose link/inet helpers to LNDs.

## Control Flow

Network allocation starts with `lnet_net_alloc()`, which either returns an existing matching net or initializes a new net object with NI lists, route preference list, tunables set to undefined, `net_last_alive`, and max selection priority. NI allocation flows through `lnet_ni_alloc_common()`: it checks interface uniqueness on the pending list, allocates the NI, initializes locks/lists/handles, allocates per-CPT refs and TX queues, sets the NID or leaves the LND to fill in the address portion, takes a reference to the current or init net namespace, and appends to `net_ni_added`. The public allocation variants then interpret CPT restrictions either from a `cfs_expr_list` or a caller-provided array and append that CPT coverage to the parent net.

`lnet_parse_networks()` is a destructive parser over a private copy of the string. For each network token it parses name, optional interface list, and optional net-level CPT expression, rejects bad delimiters, converts the name with `libcfs_str2net()`, ignores explicit loopback, allocates/gets the net, and either creates a default NI or walks the interface list and optional interface-level CPT expressions. On syntax or allocation failure it emits `lnet_syntax()` diagnostics, frees any partially built nets/NIs, frees expression lists, and returns `-EINVAL`.

Route parsing first splits the input with `lnet_str2tbs_sep()` by newline, carriage return, or semicolon while honoring comments. Each route command is tokenized by `lnet_parse_route()`: first token is one or more destination nets with bracket expansion, optional second token can be hops, remaining tokens are gateway NIDs with optional `:priority`. Local gateways set `*im_a_router`; remote gateways call `lnet_add_route()` and tolerate existing/unreachable routes. All text buffers must drain back to `lnet_tbnob == 0`.

`ip2nets` parsing enumerates local IPv4 addresses via `lnet_inet_enumerate()`, converts to host-order addresses, filters each text entry by address expressions, splits matched network specs while preserving interface groups in parentheses, rejects duplicate networks, and returns the comma-joined matched networks. Empty match is `-ENOENT`.

## State and Persistence Behavior

This file persists configuration into in-memory LNet objects only. `struct lnet_net` owns live NI lists (`net_ni_list`, `net_ni_added`, `net_ni_zombie`), CPT restrictions, tunables, health-derived timestamps, and route preference data. `struct lnet_ni` owns per-CPT refs/queues, interface string, current net namespace reference, CPT restrictions, state, selection priority, health/fatal flags, and recovery-related handles initialized elsewhere.

CPT restriction accounting is subtle: `NULL net_cpts` with `net_ncpts == LNET_CPT_NUMBER` means unrestricted. Transitions between restricted and unrestricted update `ln_cpt_restricted_count`. OOM during CPT rebuild intentionally degrades to unrestricted behavior to preserve function at lower NUMA efficiency.

Text parser allocations are intentionally temporary and globally counted. `lnet_parse_routes()` and `lnet_match_networks()` assert the counter returns to zero, making leaks visible in debug builds.

## Dependencies and Integration Points

The file depends on kernel networking (`struct net_device`, rtnl locking, ethtool `get_link`, net namespaces), Lustre/LNet core types from `lib-lnet.h`, libcfs expression/range parsers, NID/net conversion helpers, route-table APIs such as `lnet_add_route()`, interface enumeration through `lnet_inet_enumerate()`, NI status propagation via `lnet_push_update_to_peers()`, and per-CPT allocation through `cfs_percpt_alloc()`.

It integrates with LND startup: LNDs consume allocated NIs, may fill unspecified NID address bits, call `lnet_inet_select()` against enumerated devices, and use link-status helpers. It also integrates with dynamic configuration because `lnet_net_alloc()` can be called against arbitrary net lists and because CPT accounting affects global scheduling/NUMA behavior.

## Risks and Edge Cases

- Legacy string parsing is destructive and delimiter-sensitive; malformed parentheses/brackets, empty interface names, duplicated nets in `ip2nets`, or unexpected delimiters all collapse to `-EINVAL`.
- `lnet_parse_networks()` returns `-EINVAL` for all failures after cleanup, including some allocation failures, so callers may lose exact `-ENOMEM` detail.
- `lnet_tbnob` is a static global parser counter and the route parser comments assume single-threaded use. Concurrent parser use would make the allocation limit/accounting unsafe.
- Interface uniqueness is checked only against `net_ni_added` during common allocation; comments say LNDs own broader interface conflict checks.
- `lnet_get_link_status_locked()` dereferences `dev->ethtool_ops->get_link` without first checking `dev->ethtool_ops`, so callers must pass devices with operations initialized or this path can fault.
- CPT counter transitions are easy to imbalance if future callers manipulate `net_cpts` outside the helpers.
- `ip2nets` currently records only `li_ipaddr` into `ipaddrs`, so IPv6 matching depends on lower helper behavior and the local representation available to this older code path.

## Test Signals

Useful tests should cover successful and failing `networks` strings, including net-level CPTs, interface-level CPTs, duplicate interface names, loopback suppression, malformed delimiters, and full cleanup of partially allocated nets. Route tests should exercise separators, comments, bracket expansion, optional hops, gateway priorities, local gateway router detection, duplicate route tolerance, and `lnet_tbnob` returning to zero. `ip2nets` tests should cover match/no-match, duplicate networks, interface groups in parentheses, malformed address tokens, and long strings. Allocation tests should validate restricted/unrestricted CPT transitions and `ln_cpt_restricted_count`. Link helper tests should cover no device, down device, missing `get_link`, and `lnet_inet_select()` matching by interface name, IPv4/IPv6 address, and default first interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-cpt.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/lib-cpt.c

## Purpose

`lib-cpt.c` implements libcfs CPU partition tables for Lustre/LNet. A CPT is a software partition of CPUs and NUMA nodes used for lock sharding, per-partition allocation, NI affinity, message counters, and locality-aware network selection. The file builds the global `cfs_cpt_tab`, exposes query and mutation helpers, parses module parameters, supports per-CPT variable allocation, and registers CPU hotplug warnings.

## Important APIs, Types, and Functions

- `struct cfs_cpu_partition` stores a partition cpumask, nodemask, inter-CPT NUMA distances, spread rotor, and fallback node.
- `struct cfs_cpt_table` stores all partitions, CPU-to-CPT and node-to-CPT maps, global masks, partition count, global distance, and spread rotor.
- Module parameters `cpu_npartitions` and `cpu_pattern` control automatic or user-defined partitioning.
- Exported table lifecycle: `cfs_cpt_table_alloc()`, `cfs_cpt_table_free()`, `cfs_cpu_init()`, `cfs_cpu_fini()`.
- Exported queries: `cfs_cpt_table_print()`, `cfs_cpt_distance_print()`, `cfs_cpt_number()`, `cfs_cpt_weight()`, `cfs_cpt_online()`, `cfs_cpt_cpumask()`, `cfs_cpt_nodemask()`, `cfs_cpt_distance()`, `cfs_cpt_current()`, `cfs_cpt_of_cpu()`, `cfs_cpt_of_node()`, `cfs_cpt_spread_node()`.
- Exported mutation/helpers: `cfs_cpt_set_cpu()`, `cfs_cpt_unset_cpu()`, `cfs_cpt_set_cpumask()`, `cfs_cpt_unset_cpumask()`, `cfs_cpt_set_node()`, `cfs_cpt_unset_node()`, nodemask variants, and core include/exclude helpers.
- `cfs_cpt_bind()` changes current task CPU/memory affinity to a partition.
- `cfs_percpt_alloc()`, `cfs_percpt_free()`, and `cfs_percpt_number()` implement cacheline-aligned arrays indexed by CPT.

## Control Flow

`cfs_cpu_init()` registers CPU hotplug callbacks when enabled, takes `cpus_read_lock()`, then creates `cfs_cpt_tab` either from `cpu_pattern` or automatic partitioning. It logs the resulting NUMA node, CPU core, and partition counts. On failure it unwinds hotplug state and frees any partial table.

Automatic partitioning uses `cfs_cpt_num_estimate()` to choose a default based on online CPUs and hyperthread sibling width, capped more conservatively on 32-bit builds. `cfs_cpt_table_create()` validates requested partitions, allocates the table, then walks online NUMA nodes and calls `cfs_cpt_choose_ncpus()` to distribute CPUs across partitions. `cfs_cpt_choose_ncpus()` prefers CPUs in the same socket/core grouping and updates maps through `cfs_cpt_set_cpu()`.

Pattern creation in `cfs_cpt_table_create_pattern()` supports explicit partition ranges (`0[0-3]`), NUMA ranges (`N 0[0]`), default NUMA layout (`N`), CPU/NUMA relative core exclusion (`C[...]`, `N C[...]`), and processor exclusion (`X[...]`, `N X[...]`). It builds a default layout for exclusion modes, parses bracket ranges with `cfs_expr_list_parse()`, applies set/unset functions, and validates that every partition remains online.

Whenever CPUs or nodes are added/removed, `cfs_cpt_add_node()` and `cfs_cpt_del_node()` maintain node masks, `ctb_node2cpt`, per-partition distance arrays, and the global maximum distance using kernel `node_distance()`.

## State and Persistence Behavior

The global `cfs_cpt_tab` is exported and read-mostly after initialization. It is in-memory kernel state, not persisted externally. Each table owns dynamically allocated cpumasks, nodemasks, per-partition distance arrays, mapping arrays sized by `nr_cpu_ids` and `nr_node_ids`, and partition descriptors.

The per-CPT allocation API hides a `struct cfs_var_array` header immediately before the returned pointer array. Callers receive `void *` pointing at `va_ptrs[0]`; freeing relies on `container_of()`. Each partition buffer is `L1_CACHE_ALIGN(size)` and allocated with CPT-local allocation macros.

CPU hotplug support is intentionally limited. The callbacks do not rebalance the partition table; offline events only warn that performance/stability may be impacted, especially if all siblings in a core go offline.

## Dependencies and Integration Points

This file depends on Linux CPU, cpumask, nodemask, NUMA topology, hotplug, scheduler affinity, and memory policy APIs. It also depends on libcfs allocation wrappers, expression-list parsing, `LASSERT`, and exported symbols consumed by LNet and broader Lustre code.

Integration is broad: `lnet_cpt_table()` users map messages, MD pages, NIDs, counters, resource containers, NI TX queues, monitor queues, and allocations to CPTs. `config.c` uses `cfs_percpt_alloc()` for NI refs/TX queues. `lib-md.c` maps the first MD page to a CPT through `cfs_cpt_of_node()`. `lib-move.c` uses CPT distance to prefer local NIs and per-CPT locks/queues for message processing.

## Risks and Edge Cases

- Several setters, especially `cfs_cpt_set_cpumask()` and node helpers, call low-level add functions directly and can overwrite CPU-to-CPT mappings if given overlapping masks. Pattern validation avoids some cases but generic callers need discipline.
- `cfs_cpt_of_node()` checks `node > nr_node_ids` instead of `node >= nr_node_ids`, so `node == nr_node_ids` indexes past the allocated map.
- `cfs_cpt_bind()` returns after the first online CPU iteration, even if the current affinity is already compatible; this behavior should be tested against expected scheduler semantics.
- Pattern parsing is complex and mixes `node`, `exclude`, and `relative` modes. Invalid partition counts, empty partitions after exclusion, missing brackets, and offline CPUs all need coverage.
- CPU hotplug does not rebuild mappings. After CPU removal, `cfs_cpt_online()` and affinity binding may behave differently than initial partition design.
- `cfs_percpt_free()` assumes the pointer came from `cfs_percpt_alloc()` and cannot validate corrupted or offset pointers.

## Test Signals

Tests should validate table allocation/free under injected allocation failures; automatic partition counts for different CPU/HT topologies; pattern parsing for explicit, NUMA, include, exclude, relative-core, and malformed patterns; CPU/node add/remove distance recalculation; per-CPT allocation alignment/count/free behavior; `cfs_cpt_current()` remapping of unknown CPUs; `cfs_cpt_bind()` success and `-ENODEV`; print helpers returning `-E2BIG`; and hotplug callbacks preserving module stability while warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-cpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-md.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/lib-md.c

## Purpose

`lib-md.c` manages LNet memory descriptors. An MD describes user/kernel memory used for PUT, GET, REPLY, ACK, and portal receive operations. This file builds internal `struct lnet_libmd` objects from user-facing `struct lnet_md`, attaches MDs to match entries or binds free-floating RDMA MDs, maps buffers to `bio_vec` fragments, links MDs into per-CPT resource containers, detaches response trackers, and unlinks/free MDs safely when operations complete.

## Important APIs, Types, and Functions

- `lnet_md_build()` validates and converts `struct lnet_md` into `struct lnet_libmd`, including contiguous-buffer splitting into page fragments, KIOV copy/validation, GPU flag propagation, threshold/options/user pointer/handler setup, and optional small-MD slab allocation.
- `lnet_md_unlink()` marks an MD zombie, detaches it from its ME/portal, invalidates its handle, and frees it immediately only when `md_refcount == 0`.
- `lnet_get_first_page()` and `lnet_cpt_of_md()` resolve the first backing page and CPT for locality decisions. Bulk-handle MDs redirect to the bulk MD.
- `lnet_md_link()` initializes a resource handle and inserts the MD into `the_lnet.ln_md_containers[cpt]->rec_active`.
- `lnet_assert_handler_unused()` verifies no active MD still uses a handler.
- `lnet_md_deconstruct()` copies event-visible MD fields into `struct lnet_event`.
- Exported public API: `LNetMDAttach()`, `LNetMDBind()`, and `LNetMDUnlink()`.

## Control Flow

`LNetMDAttach()` requires an empty ME and at least one GET or PUT operation flag. It builds the MD, locks the ME CPT resource container, unlinks the ME on build error, links the MD, attaches it to the portal through `lnet_ptl_attach_md()`, creates the handle, unlocks, then drops bad delayed messages and resumes matching delayed PUTs. The ME is either linked to the MD or freed on failure.

`LNetMDBind()` creates a free-floating MD for active operations. It rejects MDs that have GET/PUT operation flags, builds the MD, rejects buffers larger than `LNET_MTU`, locks the current resource CPT, links the MD, and returns a handle. These MDs are later used by `LNetPut()` and `LNetGet()`.

`LNetMDUnlink()` maps the handle cookie to a CPT, locks resources, retries if a zero-refcount MD is concurrently in handler execution, marks the MD aborted, builds a standalone unlink event if a handler exists and no operations are active, detaches any response tracker, calls `lnet_md_unlink()`, unlocks, and invokes the handler outside the resource lock.

## State and Persistence Behavior

MDs persist in per-CPT active resource containers until explicitly unlinked, automatically unlinked, or freed after the last active operation. A handle lookup remains valid only until `lnet_res_lh_invalidate()` in `lnet_md_unlink()`. `md_refcount`, `LNET_MD_FLAG_ZOMBIE`, `LNET_MD_FLAG_ABORTED`, `LNET_MD_FLAG_HANDLING`, `LNET_MD_FLAG_AUTO_UNLINK`, and optional `md_rspt_ptr` govern lifetime.

Memory backing is not owned by LNet. The MD stores page vectors pointing to caller memory. For contiguous input, the file computes page fragments from `virt_to_page()` or `vmalloc_to_page()`. For `LNET_MD_KIOV`, it trusts caller page pointers but validates fragment offsets/lengths. Event persistence is through callbacks/queues using data copied by `lnet_md_deconstruct()` and events built by the message path.

## Dependencies and Integration Points

The MD layer integrates with ME/portal logic (`lnet_ptl_attach_md()`, `lnet_ptl_detach_md()`, delayed message lists), resource-handle containers, message attach/finalize code, response tracking in `lib-move.c`, small-MD slab caches, and public LNet APIs consumed by upper protocols. CPT selection integrates with `lib-cpt.c` through `lnet_cpt_of_md()` and later message pathway selection.

## Risks and Edge Cases

- `lnet_get_first_page()` follows bulk handles without taking an explicit visible lock in this function; callers need to ensure handle lifetime/locking is appropriate.
- Contiguous MD building uses kernel virtual address translation and assumes caller memory remains pinned/valid for the operation lifetime.
- KIOV page pointers are explicitly taken on trust. Invalid pages cannot be detected here.
- `LNetMDBind()` rejects lengths over `LNET_MTU`, while attached MDs can represent larger portal buffers. Callers must choose the correct API.
- Unlink races with handler execution require `lnet_md_wait_handling()`. Missing this pattern in future code could lead to use-after-free or duplicate events.
- Response tracker cleanup crosses MD/resource and monitor-thread state; detach ordering is important to avoid stale tracker pointers.

## Test Signals

Tests should cover MD validation failures, contiguous and KIOV fragment construction, max-size constraints, GPU and bulk-handle flags, small versus large allocation paths, attach failure unlinking the ME, delayed PUT match/drop behavior after attach, free-floating bind constraints, unlink with and without active refs, handler callback delivery for immediate unlink, response tracker detachment, and race tests around `LNET_MD_FLAG_HANDLING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-md.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-me.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/lib-me.c

## Purpose

`lib-me.c` manages LNet match entries. An ME is a portal-table entry that defines which incoming PUT/GET traffic can attach to an MD by requester ID and match/ignore bits. This file creates MEs in the correct portal match table/hash bucket, orders them according to insertion policy, and unlinks/frees an ME together with any attached MD when required.

## Important APIs, Types, and Functions

- `LNetMEAttach()` is the exported constructor. It validates the portal, chooses the match table via `lnet_mt_of_attach()`, allocates from `lnet_mes_cachep`, initializes match criteria, stores unlink policy and CPT, chooses either the ignore hash bucket or the normal hash head from `lnet_mt_match_head()`, and inserts before/after.
- `lnet_me_unlink()` removes the ME from its list, detaches any attached MD from the portal, unlinks that MD, and frees the ME slab object. It must be called with the LNet resource lock held.
- The disabled `lib_me_dump()` is a debug helper showing the ME fields and list neighbors.

## Control Flow

ME creation requires `the_lnet.ln_refcount > 0`. `LNetMEAttach()` rejects portals beyond `ln_nportals`, asks portal code for the attach match table, and rejects incompatible portal types with `-EPERM`. After allocation, it locks `mtable->mt_cpt`, fills fields from caller parameters, selects a list head based on `ignore_bits` and match hash, records the bucket offset in `me_pos`, inserts at head or tail according to `LNET_INS_BEFORE`, `LNET_INS_AFTER`, or `LNET_INS_LOCAL`, then unlocks and returns the pointer.

Unlink is synchronous from the ME perspective. It removes the list node first, then if an MD is attached it calls `lnet_ptl_detach_md()` and `lnet_md_unlink()`. The MD might only become zombie if active operations hold references. Finally the ME slab object is freed.

## State and Persistence Behavior

MEs persist in portal match-table hash lists until unlinked directly or until an attached MD created with `LNET_UNLINK` causes `lnet_md_unlink()` to unlink the ME. The ME stores portal index, match ID, match bits, ignore mask, unlink policy, MD pointer, CPT, list position, and list linkage. There is no disk persistence.

## Dependencies and Integration Points

The file depends on portal match-table helpers (`lnet_mt_of_attach()`, `lnet_mt_match_head()`), resource locking, ME slab cache accounting, and MD/portal detach functions from `lib-md.c` and portal code. `LNetMDAttach()` in `lib-md.c` consumes an empty ME and either attaches an MD to it or unlinks it on MD build failure.

## Risks and Edge Cases

- The public API returns a raw `struct lnet_me *` rather than an opaque handle in this tree, so consumers must preserve locking/lifetime discipline.
- `lnet_me_unlink()` assumes the caller holds the resource lock and that the ME is linked; misuse can corrupt match lists.
- Portal compatibility is delegated to `lnet_mt_of_attach()`, making ME correctness dependent on portal table configuration.
- `ignore_bits != 0` forces use of the ignore bucket, which may have different performance and matching behavior than exact-hash buckets.
- The interaction between `me_unlink == LNET_UNLINK` and MD auto-unlink needs coverage because ME lifetime can be triggered by MD completion rather than explicit ME operations.

## Test Signals

Tests should validate invalid portals, incompatible portal types, allocation failure, insertion order for before/after/local modes, ignore-bucket versus hashed-bucket placement, ME/MD attach then unlink behavior, auto-unlink through MD unlink policy, and resource-lock assertions under debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-me.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-move.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/lib-move.c

## Purpose

`lib-move.c` is LNet's data movement core. It sends and receives LNet messages, chooses local and peer NIs, enforces NI/peer/router credits, parses incoming PUT/GET/REPLY/ACK traffic, handles routed forwarding, tracks response timeouts, drives resend and recovery queues, and exposes public `LNetPut()`, `LNetGet()`, `LNetDist()`, `lnet_parse()`, and related helpers.

The file is the integration point where MDs, MEs, portals, peers, routes, NIs, health, CPT locality, LND callbacks, test failure injection, and monitor-thread recovery converge.

## Important APIs, Types, and Functions

- `struct lnet_send_data` carries pathway-selection state: chosen local NI, destination/gateway peer NIs, final destination, peer objects, source/destination/router NIDs, CPTs, message, and send-case flags.
- Stats helpers `lnet_incr_stats()`, `lnet_sum_stats()`, and `lnet_usr_translate_stats()` maintain per-element send/receive/drop counters by message type.
- Failure injection uses `lnet_fail_nid()` and `fail_peer()` with `the_lnet.ln_test_peers`.
- Buffer helpers `lnet_iov_nob()`, `lnet_kiov_nob()`, `lnet_extract_kiov()`, and `lnet_copy_kiov2iter()` support vector length, subrange extraction, and page-vector copying into kernel iterators.
- LND boundary helpers `lnet_ni_recv()`, `lnet_prep_send()`, `lnet_ni_send()`, and `lnet_ni_eager_recv()` call `lnd_recv`, `lnd_send`, and `lnd_eager_recv`.
- Credit functions `lnet_post_send_locked()`, `lnet_return_tx_credits_locked()`, `lnet_post_routed_recv_locked()`, and `lnet_return_rx_credits_locked()` manage NI, peer, peer-router, and router-buffer credits and delayed queues.
- Path selection is centered on `lnet_select_pathway()`, `lnet_handle_send_case_locked()`, `lnet_get_best_ni()`, `lnet_select_peer_ni()`, `lnet_handle_find_routed_path()`, and the source/destination/MR/NMR case handlers.
- Monitor and recovery code includes `lnet_monitor_thread()`, `lnet_monitor_thr_start()`, `lnet_monitor_thr_stop()`, response tracker helpers, resend queues, local/peer NI recovery, and `lnet_mt_event_handler()`.
- Incoming parse path includes `lnet_parse()`, `lnet_parse_forward_locked()`, `lnet_parse_local()`, `lnet_parse_put()`, `lnet_parse_get()`, `lnet_parse_reply()`, and `lnet_parse_ack()`.
- Public operations are `LNetPut()`, `LNetGet()`, optimized GET reply helpers `lnet_create_reply_msg()` and `lnet_set_reply_msg_len()`, and distance API `LNetDist()`.

## Control Flow

The send flow starts with an upper layer preparing a message through `LNetPut()` or `LNetGet()`. Those functions allocate a message, validate and attach a free-floating MD, fill the wire header, build the local send event, optionally attach a response tracker, and call `lnet_send()`. `lnet_send()` marks the message sending, delegates to `lnet_select_pathway()`, and if credits are immediately available calls `lnet_ni_send()`.

`lnet_select_pathway()` locks a current CPT, derives an MD locality CPT from the first backing page, creates or finds the destination peer NI, optionally initiates peer discovery, classifies the send as source-specified or source-any, local or remote, MR or NMR, response or request, then dispatches to a case handler. Case handlers either use an explicit local NI, prefer a stable source NI for non-MR peers, search local peer nets before routes for MR peers, or find a route/gateway through `lnet_handle_find_routed_path()`. Final send setup in `lnet_handle_send()` updates round-robin sequence numbers, may switch CPT locks after computing the selected NI CPT, commits the message, sets source/destination wire NIDs, records response-tracker next hop, and posts send credits.

Transmit credit posting first checks deadline and peer aliveness for routed messages, aborts if the MD was unlinked, then consumes peer TX credits and NI TX credits. If either credit pool goes negative, the message is queued on the peer or NI delayed queue. Delay rules can also queue a message. Credit return wakes the next delayed message and carefully switches CPT locks if the queued message belongs to another CPT.

The receive flow enters `lnet_parse()` from an LND with a header, source NID, private LND state, and RDMA flag. It validates message type and payload size, updates router liveness for reserved GET pings, rejects bad destination/routing cases, applies failure/drop rules, allocates and initializes a message, finds the sender peer NI, marks sender status/aliveness, commits the receive message, and either forwards it through router-buffer credit posting or parses it locally. Local parsing matches PUT/GET traffic against portal MDs, attaches reply/ack MDs by wire handle, calls `lnet_ni_recv()` to pull payload, or sends a REPLY for GET.

The monitor thread waits for LNet start then loops once per second while running. It checks routers, resends queued messages, expires response trackers at half transaction-timeout cadence, pings local and peer NIs in recovery queues, emits rate-controlled health console updates, and queues ping-buffer updates. Stop transitions the monitor to stopping/shutdown, flushes ping-buffer work, wakes the thread, waits on a semaphore, then cleans response trackers, recovery queues, and resend queues.

## State and Persistence Behavior

All state is in-memory kernel state. Messages carry pointers to attached MDs, TX/RX NIs, peer NIs, router buffers, private LND state, response/recovery flags, deadlines, retry counts, original source/router NID parameters, and event fields. MD refcounts and NI/peer refcounts keep objects alive across unlock/send/receive/finalize boundaries.

Credit state is distributed across `struct lnet_tx_queue`, `struct lnet_peer_ni`, router buffer pools, and peer router queues. Negative credit counts represent blocked queues and are paired with non-empty delayed lists. Return paths restore credits and schedule queued work.

Response tracking attaches `struct lnet_rsp_tracker` to an MD and per-CPT monitor queue. Receipt invalidates the handle for later cleanup. Expiry unlinks the MD, increments timeout counters, and penalizes the next-hop peer health. If the monitor cannot look up an MD that still has a valid tracker, it moves the tracker to a zombie queue until final MD detach or shutdown cleanup.

Recovery queues hold local NIs and peer NIs with extra refs. Recovery sends reserved-portal GET pings using temporary MDs and event metadata. On send/reply/unlink events, the handler updates pending/failed flags and health.

## Dependencies and Integration Points

`lib-move.c` depends on almost every LNet subsystem: peer tables, route tables, router checker, portal matching, MD/ME resource handles, message allocation/finalization, NI health/status, ping buffers, discovery, dynamic configuration sequence checks, delay/drop rules, libcfs failpoints, and per-CPT locks/counters. It calls LND operations `lnd_send`, `lnd_recv`, `lnd_eager_recv`, and optional `lnd_get_dev_prio`.

It integrates upward with public LNet consumers through `LNetPut()`, `LNetGet()`, `LNetDist()`, event handlers, ACK/REPLY/PUT/GET semantics, and MD callbacks. It integrates downward with LNDs through header parse/receive/send callbacks and optimized RDMA GET reply helpers.

## Risks and Edge Cases

- Locking is complex: code moves among `lnet_net_lock(cpt)`, `lnet_res_lock(cpt)`, NI locks, peer locks, and spinlocks, sometimes dropping locks around LND callbacks and reacquiring possibly different CPT locks.
- Credit invariants rely on negative counts matching non-empty queues. Imbalance can stall sends/receives or overrun router buffers.
- Path selection combines health, selection priority, direct DMA device priority, NUMA distance, available credits, and round-robin sequence numbers. Small changes can alter routing fairness or locality.
- Peer discovery can replace peer ownership and queue the message for discovery, so callers must treat `LNET_DC_WAIT` as non-final and not touch freed message state.
- Response tracker lifetime crosses MD unlink, monitor expiry, and shutdown paths. Zombie tracker handling exists because MD lookup can fail while the tracker is still logically attached.
- `lnet_check_message_drop()` enforces deadlines only for non-routing originators; routers intentionally forward beyond upper-layer deadlines.
- Incoming `lnet_parse()` must always call back into `lnd_recv()` for accepted packets, even drops, so LND resources are released.
- Routed receive uses eager receive when available before credits exist; LNDs without eager receive mark ready-delay and queue.
- Recovery intentionally drops NI/peer refs before sending pings to avoid deadlocks with deletion, then looks objects up again; races with user deletion are expected.
- Public `LNetPut()` and `LNetGet()` return success once the operation is queued/sent; completion and many failures are asynchronous events.

## Test Signals

High-value tests include send-path selection for every source/local/remote/MR/NMR/response case; route comparison by UDSP preference, priority, hops, gateway health, queue length, credits, and sequence; NI selection by fatal flag, health, selection priority, GPU device priority, NUMA distance, credits, and round robin; credit exhaustion and wakeup for peer TX, NI TX, peer router, and router-buffer pools; MD unlink races canceling sends; deadline and peer-dead drops; peer discovery queuing; failure/drop/delay rule injection; incoming parse validation for bad payloads, bad destinations, disabled routing, asymmetrical routes, local PUT/GET/REPLY/ACK matching, truncation, ACK disable, and optimized RDMA GET; delayed PUT drop/resume; response tracker attach/update/expire/zombie cleanup; monitor start/stop cleanup; local and peer NI recovery state transitions; `LNetPut()`/`LNetGet()` invalid MD and allocation failures; and `LNetDist()` local, same-net, routed, namespace-priority, and unreachable cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/lib-move.c -->
