# subset-b-004549 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.h

## Purpose
`definer.h` describes the Hardware Steering match-definer vocabulary for mlx5. It maps Linux flow-match fields into HWS definer field names, selector limits, high-level packet header layouts, match tag storage, and definer-cache objects. The implementation that fills and allocates definers lives in the HWS definer code, while this header is the central contract consumed by match templates, matchers, and rule insertion.

## Important APIs, types, and functions
The largest API surface is `enum mlx5hws_definer_fname`, which enumerates matchable fields across outer and inner Ethernet/IP/L4 headers, tunnel protocols, GTP/GRE/Geneve/VXLAN, flex parsers, metadata registers, MPLS, ICMP, IPsec, packet type, tunnel header dwords, and integrity bits. `enum mlx5hws_definer_match_criteria`, `enum mlx5hws_definer_type`, and `enum mlx5hws_definer_match_flag` describe match namespaces, ordinary versus jumbo definers, and protocol-specific layout flags.

`struct mlx5hws_definer_fc` is the field-copy descriptor used when creating tags: it carries source offsets and masks in PRM match parameters, destination byte/bit positions in the HWS tag, the logical field name, and callbacks for setting value and mask bits. `struct mlx5hws_definer` stores the final hardware object identity, definer type, DW and byte selectors, and the generated match mask. Cache types `mlx5hws_definer_cache` and `mlx5hws_definer_cache_item` let contexts reuse equivalent definer objects under the context control lock.

Exported helpers include `mlx5hws_definer_create_tag()`, `mlx5hws_definer_mt_init()`, `mlx5hws_definer_mt_uninit()`, `mlx5hws_definer_get_obj()`, `mlx5hws_definer_free()`, `mlx5hws_definer_calc_layout()`, `mlx5hws_definer_compare()`, `mlx5hws_definer_get_id()`, and `mlx5hws_definer_fname_to_str()`.

## Control flow
This header has no runtime body, but it defines the data path used by matcher and rule code. A match template carries a PRM mask; definer initialization converts that mask into field-copy descriptors and a compact hardware definer. Rule insertion later calls `mlx5hws_definer_create_tag()` with match values and the template's `fc` array to produce the STE tag written into hardware. Matcher resize validation compares definer layouts through `mlx5hws_definer_compare()` so rules can be moved only between equivalent matchers.

## State and persistence behavior
Runtime state is represented by cached definer objects and their firmware object IDs. A definer's hardware object persists until the context frees the cache entry or uninitializes the match template. The header also defines in-memory layouts for high-level parsed headers, but those are interpretation structures for PRM-format buffers rather than standalone persistent state.

## Dependencies and integration points
`definer.h` depends on rule tag storage from `rule.h`, command/object allocation paths, PRM match parameter layout, and HWS context locking. It is included through `internal.h` by matcher, rule, action, debug, and BWC code. Its field names are tightly coupled to firmware PRM selectors and Linux flow-match structures, so changes require cross-checking `mlx5_ifc_*` bit layouts and match criteria enable handling.

## Risks and edge cases
Selector limits are strict: ordinary match definers have limited DW/byte selectors and jumbo definers use larger tags. A wrong field offset, mask, selector, or bit order can silently steer traffic incorrectly. Protocol aliases such as Ethernet type versus IP version are later checked by `rule.c`, but this header is where those fields are named. Cache refcounts must remain aligned with firmware object lifetime, and adding new fields requires verifying hardware support, PRM layout, string conversion, and tag creation callbacks.

## Test signals
Useful signals are kernel build coverage, creating matchers for each criteria block, rules matching outer/inner IPv4 and IPv6, tunnel matches for VXLAN/Geneve/GRE/GTPU, jumbo match templates, flex parser fields, register matches, matcher resize between equivalent and non-equivalent definers, and negative tests for unsupported or too-large layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.c

## Purpose
`fs_hws.c` adapts the mlx5 flow-steering command interface to the HWS backend. It creates and destroys HWS namespaces, flow tables, groups, FTEs, packet reformat objects, modify-header objects, cached destination actions, counters, ASO meter actions, sampler actions, and default miss wiring. It is the compatibility layer that lets existing flow-steering users drive hardware steering for FDB tables while delegating unsupported firmware-termination tables back to the firmware command backend.

## Important APIs, types, and functions
The file exports `mlx5_fs_cmd_get_hws_cmds()`, `mlx5_fs_hws_is_supported()`, `mlx5_fs_hws_action_get_pkt_reformat_id()`, `mlx5_fs_get_hws_action()`, and `mlx5_fs_put_hws_action()`. The static command table `mlx5_flow_cmds_hws` binds flow-steering operations such as `create_flow_table`, `create_flow_group`, `create_fte`, `update_fte`, `packet_reformat_alloc`, and `modify_header_alloc`.

Important internal flows include `mlx5_cmd_hws_create_ns()` and `mlx5_cmd_hws_destroy_ns()` for context lifetime, `mlx5_fs_init_hws_actions_pool()` and `mlx5_fs_cleanup_hws_actions_pool()` for shared action pools, `mlx5_cmd_hws_create_flow_table()` and `mlx5_cmd_hws_destroy_flow_table()` for table lifecycle, `mlx5_cmd_hws_create_flow_group()` for BWC matcher creation, and `mlx5_fs_fte_get_hws_actions()` for translating a legacy `fs_fte` action bitmap into ordered `mlx5hws_rule_action` entries.

## Control flow
Namespace creation opens an HWS context with up to 16 queues and queue size 256, then creates shared tag, VLAN, drop, decap, remove-header, insert-header, and decap-L3 pools plus xarray caches for dynamic destinations and actions. Flow-table creation rejects non-FDB HWS tables, creates an HWS table, sets default miss when requested, records the HWS table ID as the flow-table ID, and creates a destination-table action cached by table ID. Firmware termination tables are created by the firmware command set but still get an HWS destination action.

Flow groups become BWC matchers using the group's PRM mask and priority. FTE creation first calls `mlx5_fs_fte_get_hws_actions()`, which enforces the HWS action order: decap, remove header, VLAN pops, modify header, VLAN pushes, insert/encap reformat, counters, tag, ASO meter, drop and forwarding destinations, destination array, and final `LAST`. It tracks actions that need later release in `fte->fs_hws_rule.hws_fs_actions`. The rule is then inserted through `mlx5hws_bwc_rule_create()`. Update rebuilds the action array, calls `mlx5hws_bwc_rule_action_update()`, and either destroys old actions or restores them on failure. Delete destroys the BWC rule and releases stored actions.

Packet reformat allocation validates supported types, chooses or creates a packet-reformat pool by action type and header size, acquires an offset, stores duplicated header data and header index, and marks ownership as HWS. Modify-header allocation groups identical action patterns into pools and acquires per-rule argument offsets. Deallocation frees duplicated data and releases pool indexes. `mlx5_fs_hws_action_get_pkt_reformat_id()` lazily creates a firmware reformat object for an HWS reformat when a firmware ID is required, guarding the cached ID with a mutex.

## State and persistence behavior
State is held under `ns->fs_hws_context`: the HWS context pointer and `mlx5_fs_hws_actions_pool`. Shared actions persist for namespace lifetime. Table destination actions are xarray entries keyed by flow-table ID. Vport destination actions are cached by vport or VHCA/vport tuple. ASO meter and sampler actions use `mlx5_fs_hws_data` objects with mutex-protected lazy creation and refcounts. Per-FTE actions own references to counters, ASO/sampler actions, destination arrays, range actions, and `LAST` actions until rule deletion or successful update replacement.

## Dependencies and integration points
This file integrates `fs_core` and `fs_cmd` with `mlx5hws.h`, `fs_hws_pools.h`, Linux xarrays, mlx5 counter bulks, execute-ASO meters, packet reformat resources, modify-header resources, firmware flow commands, BWC matchers/rules, and root namespace peer setup. HWS support is gated by device capabilities exposed through `mlx5hws_is_supported()`.

## Risks and edge cases
Action ordering is hardware-sensitive; reordering can break steering. Cleanup paths are mixed: some actions are shared, some cached with refcounts, some rule-owned, and some owned by generic flow-steering objects. Missing a release leaks firmware objects or pool indexes. Dynamic xarray insertion handles `-EBUSY` for vport actions but not all cache paths have identical race behavior. `packet_reformat_dealloc()` appears to use the L2-to-L2 pool path for L2-to-L3 tunnel release, which is a high-value review point. The remove-header allocation logs unsupported VLAN parameters but does not immediately return a distinct error after `hws_action` remains NULL, so callers depend on later failure behavior. Only FDB HWS tables are supported; non-FDB callers must get `-EOPNOTSUPP`.

## Test signals
Test namespace open/close, FDB table create/destroy/modify/default miss, firmware termination table fallback, group create/destroy, FTE create/update/delete for each action combination, multi-destination arrays, counters, ASO meters, samplers, range destinations, vport/VHCA/uplink destinations, packet reformat allocate/free for all supported types, modify-header pattern reuse, concurrent vport/ASO/sampler action creation, and failure injection through allocation, xarray insert, HWS action creation, and BWC rule update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.h

## Purpose
`fs_hws.h` declares the flow-steering-to-HWS adapter structures embedded in generic mlx5 flow-steering objects. It is the local contract between `fs_hws.c`, pool helpers, counter bulks, packet reformat resources, modify-header resources, matchers, and FTE rule state.

## Important APIs, types, and functions
`struct mlx5_fs_hws_actions_pool` stores namespace-wide shared actions and xarray caches for packet reformat pools, modify-header pools, table destinations, vport destinations, ASO meters, and sampler destinations. `struct mlx5_fs_hws_context` wraps the HWS context and this pool. Table, matcher, and rule adapter structs hold HWS table, BWC matcher, BWC rule, and per-rule action references.

`struct mlx5_fs_hws_action` is embedded in packet reformat and modify-header resources and stores the HWS action, associated fs pool, acquired packet-reformat or modify-header data, lazy firmware reformat ID, and a mutex protecting that ID. `struct mlx5_fs_hws_data` implements lazy shared action creation with a mutex and refcount. `struct mlx5_fs_hws_create_action_ctx` carries the action type, context, object ID, and optional return register for the generic action factory.

Exported functions are `mlx5_fs_get_hws_action()`, `mlx5_fs_put_hws_action()`, and, when HWS is configured, `mlx5_fs_hws_action_get_pkt_reformat_id()`, `mlx5_fs_hws_is_supported()`, and `mlx5_fs_cmd_get_hws_cmds()`.

## Control flow
The header has no executable flow. Generic flow-steering code uses these embedded structs after selecting HWS command operations. `fs_hws.c` initializes namespace-level pools, fills table/matcher/rule fields during create operations, and unwinds them on destroy/update. Conditional stubs return unsupported behavior when `CONFIG_MLX5_HW_STEERING` is disabled.

## State and persistence behavior
The declared state persists at the same lifetime as the flow-steering objects embedding it: root namespace, flow table, group, FTE, packet reformat, modify header, and counter bulk. `fw_reformat_id` can be initialized lazily and later freed through firmware commands. Refcounted `mlx5_fs_hws_data` objects persist in xarrays until namespace cleanup, while the underlying HWS action exists only while the refcount is nonzero.

## Dependencies and integration points
This header depends on `mlx5hws.h`, `fs_hws_pools.h`, Linux xarrays, mutexes, refcounts, counters, execute-ASO objects, and generic flow-steering types. It is included by flow-steering core headers so generic objects can carry HWS-private state without exposing implementation details.

## Risks and edge cases
Struct fields encode ownership contracts that are not obvious from types alone: `hws_action` can be shared, cached, or rule-owned depending on action kind; `fs_pool` must match the allocated `pr_data` or `mh_data`; and `fw_reformat_id` must be protected by the lock. Conditional compilation stubs must stay consistent with real signatures, or non-HWS builds break.

## Test signals
Build both with and without `CONFIG_MLX5_HW_STEERING`. Runtime validation comes from HWS namespace/table/rule lifecycle, packet reformat firmware-ID lookup, lazy shared action refcounting, and cleanup after failed FTE action construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.c

## Purpose
`fs_hws_pools.c` implements flow-steering HWS pools for packet reformat and modify-header action arguments. It wraps the generic `mlx5_fs_pool` bulk allocator so many FTEs can share one HWS action object while each rule gets a unique offset and per-rule data payload.

## Important APIs, types, and functions
Packet reformat pool functions are `mlx5_fs_hws_pr_pool_init()`, `mlx5_fs_hws_pr_pool_cleanup()`, `mlx5_fs_hws_pr_pool_acquire_pr()`, `mlx5_fs_hws_pr_pool_release_pr()`, and `mlx5_fs_hws_pr_get_action()`. Modify-header pool functions are `mlx5_fs_hws_mh_pool_init()`, `mlx5_fs_hws_mh_pool_cleanup()`, `mlx5_fs_hws_mh_pool_acquire_mh()`, `mlx5_fs_hws_mh_pool_release_mh()`, and `mlx5_fs_hws_mh_pool_match()`. Counter integration is provided by `mlx5_fc_get_hws_action()` and `mlx5_fc_put_hws_action()`.

Internal helpers create bulk HWS actions for decap-L3-to-L2, encap-L2-to-L3, encap-L2-to-L2, insert-header VLAN, and modify-header patterns. The default bulk length is 65,536 entries, with thresholds updated as roughly one tenth of used units capped at `BIT(18)`.

## Control flow
Pool initialization validates action type, stores a small pool context, and initializes `mlx5_fs_pool` with bulk create/destroy callbacks. When the generic pool needs capacity, the PR bulk creator allocates a flexible bulk structure, initializes a bitmap, fills per-entry backpointers and offsets, and creates one HWS reformat or insert-header action with `log_bulk_size`. The MH bulk creator performs the same shape for modify-header actions after checking the FDB root namespace is in HMFS mode.

Acquire calls obtain an index from `mlx5_fs_pool` and return the corresponding `prs_data` or `mhs_data` entry. Release reconstructs the pool index from the entry's bulk and offset and warns if the index was not acquired. Bulk destroy refuses to free if not all offsets are returned, then destroys the associated HWS action, cleans the bitmap, and frees memory. Modify-header pool matching compares stored pattern size and action words to reuse an existing pool for identical patterns.

Counter HWS actions are created lazily per counter bulk. `mlx5_fc_get_hws_action()` takes the local counter reference, calls the generic HWS action refcount helper on `fc_bulk->hws_data`, and drops the local reference if action creation fails. The put path releases the HWS action refcount and local counter reference.

## State and persistence behavior
Each pool owns a pool context and one or more bulks. A bulk owns an HWS action object and per-offset metadata. Per-rule data buffers are not stored by this file; callers in `fs_hws.c` duplicate and free them in the acquired entries. Modify-header pools persist a copied action pattern in `pool_ctx` so future allocations can detect reuse. Counter action lifetime is tied to counter bulk HWS data refcounts.

## Dependencies and integration points
This file depends on `fs_pool`, root namespace lookup, HMFS mode, HWS action creation APIs, packet reformat and modify-header PRM data, flow counters, and `mlx5_fs_get_hws_action()`. It is consumed by `fs_hws.c` when allocating packet reformat, modify-header, and counter actions for FTE rules.

## Risks and edge cases
Destroying a bulk with active offsets returns `-EBUSY`, so caller cleanup must release all PR/MH entries first. Pool matching for modify headers compares action words in a compact way; endian or action-size mistakes can accidentally merge incompatible patterns. Bulk action creation depends on FDB root namespace HWS mode, so early or wrong-namespace use returns NULL. Pool contexts must be freed after `mlx5_fs_pool_cleanup()` to avoid dangling callbacks. Very large bulk length implies allocation and bitmap pressure under many distinct patterns or reformat sizes.

## Test signals
Test packet reformat allocation/release for insert VLAN, L2-to-L2 tunnel, L2-to-L3 tunnel, and L3 tunnel decap; modify-header allocation with repeated and distinct patterns; pool cleanup with all entries released; cleanup with active entries; counter action get/put refcounting; HMFS disabled fallback; allocation failure paths; and high-churn pool threshold behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.h

## Purpose
`fs_hws_pools.h` declares the flow-steering HWS packet-reformat and modify-header pool types used by `fs_hws.c` and implemented in `fs_hws_pools.c`. It also defines the VLAN insert-header shape currently accepted by the HWS flow-steering adapter.

## Important APIs, types, and functions
Constants `MLX5_FS_INSERT_HDR_VLAN_ANCHOR`, `MLX5_FS_INSERT_HDR_VLAN_OFFSET`, and `MLX5_FS_INSERT_HDR_VLAN_SIZE` encode supported VLAN header insertion. The L3-tunnel decap header indexes distinguish MAC-only and MAC+VLAN headers.

`struct mlx5_fs_hws_pr`, `mlx5_fs_hws_pr_bulk`, and `mlx5_fs_hws_pr_pool_ctx` describe packet-reformat offsets, associated HWS action bulk, header index, copied data pointer, and reformat type/size. `struct mlx5_fs_hws_mh` and `mlx5_fs_hws_mh_bulk` describe modify-header offsets, copied data, pool pointer, and HWS action. The declared functions initialize, clean up, acquire, release, match, and retrieve actions for these pools, plus get/put HWS counter actions.

## Control flow
This header has no runtime control flow. Callers initialize a pool for a specific reformat type or modify-header pattern, acquire entries while building FTE actions, use the returned offset/data/action in `mlx5hws_rule_action`, and release entries during resource deallocation or rule cleanup.

## State and persistence behavior
The structs carry per-offset metadata owned by pool bulks. `data` points to per-resource copied header or modify-action data and is freed by the caller that allocated the resource. Bulk actions persist for the lifetime of the backing pool and are shared by all offsets in that bulk.

## Dependencies and integration points
The header depends on Linux VLAN definitions, `fs_pool`, `fs_core`, and HWS action types. It integrates directly with packet reformat objects, modify-header objects, flow counters, and FTE action translation in `fs_hws.c`.

## Risks and edge cases
The fixed VLAN insert-header constants mean broader insert-header use is intentionally unsupported by this adapter. Callers must pair each acquire with the matching pool release; the type system does not prevent releasing a PR/MH entry to the wrong pool. The `data` pointer ownership is external, so missing cleanup leaks per-rule buffers.

## Test signals
Build coverage plus runtime packet reformat and modify-header allocation/free tests are the direct signals. Negative tests should cover unsupported insert-header anchors, wrong sizes, release of unacquired entries, and modify-header pattern matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/fs_hws_pools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/internal.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/internal.h

## Purpose
`internal.h` is the umbrella private header for the mlx5 HWS implementation. It gathers kernel/mlx5 dependencies, HWS submodule headers, shared constants, logging wrappers, and small utility helpers used across context, table, send, action, matcher, rule, command, definer, BWC, and pattern/argument code.

## Important APIs, types, and functions
It includes `prm.h`, `mlx5hws.h`, `pool.h`, `vport.h`, `context.h`, `table.h`, `send.h`, `action_ste_pool.h`, `rule.h`, `cmd.h`, `action.h`, `definer.h`, `matcher.h`, `debug.h`, `pat_arg.h`, `bwc.h`, and `bwc_complex.h`. Shared constants include `W_SIZE`, `DW_SIZE`, `BITS_IN_BYTE`, `BITS_IN_DW`, and `MLX5HWS_TABLE_TYPE_BASE`. Macros wrap logging as `mlx5hws_err()`, `mlx5hws_info()`, and `mlx5hws_dbg()`. Utilities are `IS_BIT_SET()`, `is_mem_zero()`, and a local `align()` helper.

## Control flow
The header has no larger runtime flow. It influences nearly every HWS C file by controlling include order and providing common inline helpers. `is_mem_zero()` checks for zero-size buffers and then uses a first-byte plus `memcmp()` pattern to detect all-zero memory. `align()` rounds an integer up to the next alignment boundary.

## State and persistence behavior
No persistent state is owned here. It exposes shared compile-time constants and inline behavior used by modules that own firmware objects, send queues, matchers, actions, and rules.

## Dependencies and integration points
The header depends on mlx5 transport/vport/fs core headers, workqueue support, and all private HWS module headers. Any cyclic include or prototype mismatch in the HWS subsystem tends to surface through this file.

## Risks and edge cases
Because this is an umbrella header, adding includes can increase coupling and hide missing direct dependencies. The local `align()` name may be confused with kernel alignment helpers, and it assumes power-of-two alignment semantics. `is_mem_zero()` warns on size zero and returns true, so callers must not use true as proof that a zero-length input was valid.

## Test signals
The main direct signal is full HWS build coverage. Indirect signals are successful compile and runtime coverage of all HWS modules that include this header, especially with warnings enabled and with changes to utility helpers or include ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.c

## Purpose
`matcher.c` implements HWS matcher and match-template lifecycle. A matcher owns match definers, action template processing, STE ranges, RTC objects, end flow-table anchors, collision matchers, priority-chain wiring, isolated matcher wiring, dynamic action-template attachment, and resize target setup. It is the table-level orchestration layer between PRM match/action templates and rule insertion.

## Important APIs, types, and functions
Public functions are `mlx5hws_matcher_create()`, `mlx5hws_matcher_destroy()`, `mlx5hws_match_template_create()`, `mlx5hws_match_template_destroy()`, `mlx5hws_matcher_attach_at()`, `mlx5hws_matcher_resize_set_target()`, `mlx5hws_matcher_resize_rule_move()`, and `mlx5hws_matcher_update_end_ft_isolated()`.

Core internal groups include attribute processing (`hws_matcher_process_attr()`, `hws_matcher_validate_insert_mode()`, `hws_matcher_check_attr_sz()`), template binding (`hws_matcher_bind_mt()`, `hws_matcher_bind_at()`), object allocation (`hws_matcher_create_end_ft()`, `hws_matcher_create_rtc()`), chain manipulation (`hws_matcher_connect()`, `hws_matcher_disconnect()` and isolated variants), collision matcher handling, and resize validation.

## Control flow
Creation allocates a matcher, copies attributes, validates insert/distribute/resource modes against device caps, converts rule-count sizing into hash-table dimensions when needed, sets resizable/isolated flags, copies match and action templates, and enters `hws_matcher_init()` under the context control lock. Initialization binds match templates by creating definers and RX/TX STE ranges, processes action templates into setters and calculates the maximum number of action STEs, creates an end flow table, creates RX and TX RTCs, connects the matcher into the table's priority list, and optionally creates a collision matcher for large hash tables.

For non-isolated tables, connection inserts the matcher by priority, points the new matcher's end FT to the next matcher or default miss table, points the previous FT or table start FT to the new matcher's RTCs, resets default miss refcounts, and updates connected miss tables when the first matcher changes. Isolated tables use a special chain where matcher end FTs point back to the complex matcher's end FT and the start FT or previous isolated end FT points at the current match RTCs. Destruction reverses the process under the control lock: destroy collision matcher, disconnect from the chain, destroy RTCs, destroy end FT, unbind STE ranges and definers, free template arrays, and free the matcher.

RTC creation configures hash, hash-split, or linear lookup modes based on insert and distribute mode. It sets match definer IDs, access/update index mode, PD, STE base, STC base, table type, reparse mode, miss FT, and mirrored TX RTC for FDB tables. Optimization by flow source can allocate zero-sized RX or TX resources.

Resize setup validates source and destination table type, resizable flags, insert mode, no existing resize, equal number of match templates, sufficient action STE capacity, and equivalent definers. It then records `src_matcher->resize_dst`. Rule moves are delegated to `mlx5hws_rule_move_hws_add()`.

## State and persistence behavior
Matchers persist in `tbl->matchers_list` and own firmware resources: STE ranges, RTCs, end FTs, and definer references. Collision matchers share copied template arrays with the parent but own their own resources. Runtime matcher state includes IP-version match flags and learned IP version constraints, resize destination pointer, and maximum action STE count. Match templates own copied PRM masks until destroyed.

## Dependencies and integration points
`matcher.c` depends on command helpers for RTC/STE allocation, table FT wiring helpers, definer initialization/comparison, action template processing and validation, context capabilities, action STE sizing, rule move helpers, and Linux list/mutex primitives. It is called by the public HWS API and by BWC wrappers used from `fs_hws.c`.

## Risks and edge cases
Flow-table chain rewiring is high risk: a failed connect/disconnect can leave miss paths or priority ordering wrong. Isolated matcher logic has multiple first/last/collision/rehash cases. RTC sizing must honor caps and avoid invalid zero-sized resources except for explicit flow-source optimization. Collision matcher sizing uses a fixed assured ratio and depth; wrong thresholds affect insertion success. Dynamic AT attachment grows arrays and mirrors the count into collision matchers, so array capacity and processed setters must remain consistent. Resize requires equivalent definers; skipping checks could move rules into incompatible hardware layout.

## Test signals
Test matcher create/destroy across hash, insert-by-index hash-split, and linear lookup modes; invalid cap combinations; priority insertion before/middle/after; default miss updates; isolated matcher first/last/collision cases; large-rule collision matcher creation; dynamic action-template attachment; resizable matcher creation and target setup; resize rejection for incompatible templates; and failure injection at definer, STE, end FT, RTC, and connect stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.h

## Purpose
`matcher.h` declares the private matcher data model and constants for mlx5 HWS. It captures sizing heuristics, matcher flags, match template layout, match STE identifiers, IP-version tracking, and inline predicates used by matcher and rule code.

## Important APIs, types, and functions
Constants define assured collision table behavior, update multiplier, and maximum attachable action templates. `enum mlx5hws_matcher_flags` identifies collision, resizable, and isolated matchers. `struct mlx5hws_match_template` owns a definer, field-copy array, copied match parameters, criteria enable mask, and field-copy count. `struct mlx5hws_matcher_match_ste` stores RTC IDs and STE base IDs for RX and TX. `struct mlx5hws_matcher` combines table pointer, attributes, template arrays, action STE sizing, flags, IP-version match tracking, end FT ID, collision matcher, resize destination, match STE IDs, and table list node.

Inline helpers test jumbo match templates, resizable state, resize-in-progress state, isolated state, and insert-by-index mode. The header declares `mlx5hws_matcher_update_end_ft_isolated()`.

## Control flow
This header contains only inline predicates. Runtime flow is implemented in `matcher.c` and `rule.c`; they use these predicates to choose RTC creation, action STE allocation, delete-info storage, resize behavior, and isolated matcher chaining.

## State and persistence behavior
The structs declared here are the persistent in-memory state for match templates and matchers. Firmware object IDs in `match_ste` and `end_ft_id` remain valid until matcher destruction. The IP-version fields are mutable runtime constraints updated as rules are inserted.

## Dependencies and integration points
The header depends on definer types, table attributes from the public HWS API, Linux lists, and table/rule code. It is included by `internal.h`, so it is visible throughout HWS internals.

## Risks and edge cases
Small bitfields encode whether matchers have seen outer/inner ethertype or IP-version fields and what IP version is allowed. Incorrect initialization or mutation can reject valid rules or accept inconsistent rules. Collision matchers share templates with their parent, so ownership must be handled in implementation. Maximum attached action templates limits BWC or dynamic update behavior.

## Test signals
Build coverage plus matcher create/destroy, collision matcher creation, jumbo match templates, insert-by-index rules, isolated matchers, dynamic AT attach up to the maximum, and IP-version consistency checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/mlx5hws.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/mlx5hws.h

## Purpose
`mlx5hws.h` is the public in-kernel API for mlx5 Hardware Steering. It defines opaque context/table/matcher/rule handles, table and matcher attributes, action types and flags, rule attributes, per-action payload structures, queue operations, debug dumping, and BWC helper APIs used by the flow-steering adapter.

## Important APIs, types, and functions
The header defines table type `MLX5HWS_TABLE_TYPE_FDB`, matcher resource modes, action types for drop, miss, table, counter, tag, modify header, vport, VLAN, reformat, ASO meter, insert/remove header, range, sampler, destination arrays, and `LAST`. It also defines action flags, ASO meter colors, send queue drain flags, context/table/matcher/rule attributes, and `struct mlx5hws_rule_action` payloads for tag, counter, modify header, reformat, push VLAN, and ASO meter.

Public lifecycle APIs include `mlx5hws_context_open()`, `mlx5hws_context_close()`, `mlx5hws_context_set_peer()`, table create/destroy/get-id/default-miss functions, match/action template create/destroy functions, matcher create/destroy/attach/resize functions, rule create/destroy/update functions, action create/destroy/get-type/get-dev functions, send queue poll/action, and debug dump. The BWC section declares blocking matcher and rule helpers used by `fs_hws.c`.

## Control flow
This header has no executable flow except `mlx5hws_is_supported()`, which checks device capabilities for WQE-based flow-table updates and ignoring flow-level RTC validity. Normal callers open a context, create tables, create match and action templates, create matchers, create actions, enqueue rules on send queues, drain or poll completions, update/destroy rules, then destroy objects in reverse order. BWC callers use simplified blocking matcher/rule operations that internally create templates, attach action templates as needed, and poll to completion.

## State and persistence behavior
Opaque objects represent HWS firmware resources and driver state. Contexts own queues, protection domain data, caps, caches, and common resources. Tables own flow-table IDs and default miss state. Matchers own definers, RTCs, STE ranges, and action template state. Actions own STC/action resources and sometimes argument or pattern objects. Rule handles track hardware insertion state and are asynchronous unless BWC helpers are used.

## Dependencies and integration points
The API depends on mlx5 core devices, flow tables, rule attributes, PRM action data, send queues, and firmware object commands implemented in private HWS modules. Its main in-tree consumer in this subset is `fs_hws.c`, which maps generic flow steering to the BWC API and shared action constructors.

## Risks and edge cases
The API exposes both asynchronous rule operations and blocking BWC helpers; callers must honor queue IDs, user-data completion requirements, action ordering, and object lifetime. Action offsets point into shared argument resources and are not atomically reusable. Matcher insert/distribute modes are capability-dependent. FDB tables have mirrored RX/TX resources and flow-source optimization, so callers must set attributes consistently.

## Test signals
Build coverage of all declarations, HWS support gating on devices with and without required caps, context/table/matcher/action/rule lifecycle tests, queue drain and poll tests, BWC rule create/update/destroy, all action constructors used by flow steering, matcher resize and rule move, and debug dump coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/mlx5hws.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.c

## Purpose
`pat_arg.c` implements HWS modify-header pattern caching and modify-header argument allocation/writes. It converts modify-action sizes into firmware argument allocation orders, determines when actions require packet reparse, caches firmware header-modify pattern objects, writes argument data through HWS send queues, validates modify actions, and inserts NOP actions between dependent modifications.

## Important APIs, types, and functions
Size helpers are `mlx5hws_arg_data_size_to_arg_log_size()`, `mlx5hws_arg_data_size_to_arg_size()`, `mlx5hws_arg_get_arg_log_size()`, and `mlx5hws_arg_get_arg_size()`. Pattern cache APIs are `mlx5hws_pat_init_pattern_cache()`, `mlx5hws_pat_uninit_pattern_cache()`, `mlx5hws_pat_get_pattern()`, and `mlx5hws_pat_put_pattern()`. Argument APIs are `mlx5hws_arg_create()`, `mlx5hws_arg_destroy()`, `mlx5hws_arg_create_modify_header_arg()`, `mlx5hws_arg_write()`, `mlx5hws_arg_decapl3_write()`, and `mlx5hws_arg_write_inline_arg_data()`. Validation and normalization APIs are `mlx5hws_pat_verify_actions()`, `mlx5hws_pat_require_reparse()`, and `mlx5hws_pat_calc_nop()`.

## Control flow
Pattern lookup locks the context pattern cache, searches for an equivalent pattern, moves hits to the list head as a simple LRU behavior, increments refcount, and returns the cached firmware pattern ID. On miss it creates a firmware header-modify pattern object, duplicates the pattern into a new cache item, stores refcount one, and returns the new ID. Put finds by pattern ID, decrements refcount, and when it reaches zero removes the cache item and destroys the firmware object.

Argument creation maps data size to a single-argument log size, adds the bulk log size, verifies firmware caps, creates an argument object, optionally writes initial data through the control send queue, and returns the base ID. Inline writes lock `ctx->ctrl_lock`, use the last send queue as control queue, post one or more table-access WQEs of 64 bytes each, flush, and drain synchronously. Decap-L3 writes prepare special decap data before posting.

`mlx5hws_pat_require_reparse()` scans modify actions and returns true for insert/remove/unknown actions or modifications of ethertype/next-header fields. `mlx5hws_pat_calc_nop()` detects adjacent dependent actions where one reads or writes the other's source/destination or both write the same destination, inserts a NOP before the later action, records the location bitmap, and copies the resulting sequence.

## State and persistence behavior
Pattern cache state is a mutex-protected linked list of firmware pattern IDs, duplicated pattern data, action count, and refcount. Argument objects are firmware resources created under the context PD and destroyed by ID. Writes mutate hardware argument memory and can be asynchronous at the WQE level unless the inline helper drains synchronously.

## Dependencies and integration points
This file depends on PRM modify-action layouts, HWS command helpers for pattern and argument objects, HWS send engine posting, action helper `mlx5hws_action_prepare_decap_l3_data()`, context caps and control lock, and firmware PD number. It feeds action creation and rule application paths that need modify-header or reformat argument storage.

## Risks and edge cases
Pattern comparison intentionally ignores SET/ADD values and compares only control words, while COPY/ADD_FIELD compare full words. That is correct for separating pattern from argument data but risky if a future action encodes structural fields outside the compared portion. Cache uninit only frees the cache object; callers must have put all patterns first. Argument size must stay within firmware granularities. `mlx5hws_arg_write()` uses multiple WQEs for data larger than 64 bytes, so completion/user-data assumptions must match the caller. NOP insertion can fail if `max_actions` cannot accommodate dependencies.

## Test signals
Test pattern cache hit/miss/refcount/destroy, equivalent SET patterns with different values, COPY patterns with different fields, argument size boundary mapping, invalid firmware argument sizes, inline write drain failure, multi-WQE argument writes, decap-L3 argument formatting, reparse detection for ethertype/next-header/insert/remove actions, and NOP insertion for dependent modify sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.h

## Purpose
`pat_arg.h` declares the pattern-cache and argument-object API for HWS modify-header and related action data. It defines the supported argument chunk sizes and the in-memory cache structures used by `pat_arg.c`.

## Important APIs, types, and functions
`enum mlx5hws_arg_chunk_size` defines supported chunk orders from one to four 64-byte chunks, with `MLX5HWS_ARG_CHUNK_SIZE_MAX` as an invalid/out-of-range marker. Constants define 8-byte modify actions and 64-byte argument data chunks. `struct mlx5hws_pattern_cache` owns the mutex and list, while `struct mlx5hws_pattern_cache_item` stores firmware pattern ID, duplicated pattern bytes, action count, refcount, and list node.

Declared functions cover argument size conversion, pattern cache init/uninit/get/put, action verification, argument create/destroy, modify-header argument create, reparse detection, WQE-based argument writes, inline synchronous writes, decap-L3 writes, and NOP calculation.

## Control flow
The header has no runtime flow. Action creation code calls these helpers to allocate or reuse firmware pattern objects, allocate argument memory with optional data upload, and normalize modify action lists before action templates are processed.

## State and persistence behavior
The declared cache structures persist under the HWS context. Pattern items refcount firmware pattern objects. Argument IDs returned by create functions represent firmware resources that persist until explicitly destroyed. WQE write helpers mutate argument memory referenced by actions and rules.

## Dependencies and integration points
The API depends on HWS context and send engine types, PRM modify-action encoding, and action code that creates modify-header STCs. It is included through `internal.h` by action, context, and rule-related modules.

## Risks and edge cases
The four supported chunk sizes cap single argument data at 512 bytes. Callers must not confuse data byte size with log chunk size. Cache refcounts are protected by the cache lock; bypassing get/put can leak or prematurely destroy firmware pattern objects. NOP location output is a bitmap, so action counts must fit its width.

## Test signals
Build coverage plus modify-header action creation, cache reuse, invalid action sizes, max-size arguments, reparse detection, NOP insertion, and write completion behavior provide the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.c

## Purpose
`pool.c` implements the generic HWS resource pool for STE and STC firmware objects. It allocates backing firmware resource ranges, tracks free chunks through either a bitmap or buddy allocator, supports mirrored FDB resources, and exposes chunk allocate/free plus pool create/destroy helpers.

## Important APIs, types, and functions
Public APIs are `mlx5hws_pool_create()`, `mlx5hws_pool_destroy()`, `mlx5hws_pool_chunk_alloc()`, and `mlx5hws_pool_chunk_free()`. Internal resource helpers create and destroy one STE or STC object range through `mlx5hws_cmd_ste_create()`, `mlx5hws_cmd_ste_destroy()`, `mlx5hws_cmd_stc_create()`, and `mlx5hws_cmd_stc_destroy()`. Database backends are bitmap helpers for order-zero allocations and buddy helpers for variable-order allocations.

## Control flow
Pool creation allocates the pool, copies attributes, selects database type from `MLX5HWS_POOL_FLAG_BUDDY`, sets available element count, initializes the selected database, and initializes the mutex. Database initialization allocates the bitmap or buddy structure, then calls `hws_pool_resource_alloc()` to create firmware resources. FDB pools allocate original and mirror resources unless optimization requests one side to be size zero.

Chunk allocation locks the pool, calls the backend `p_get_chunk`, subtracts `1 << order` from `available_elems`, and unlocks. Free does the reverse with backend `p_put_chunk`. Bitmap pools reject nonzero-order allocations and use the first set bit as the free index. Buddy pools allocate and free variable-order chunks. Destroy checks that all elements are available, frees firmware resources, uninitializes the database, and frees the pool.

## State and persistence behavior
Pool state includes context, pool type, flags, allocation order, available element count, table type, optimization type, original and mirror firmware resource base IDs/ranges, backend storage, function pointers, and mutex. Firmware STE/STC object ranges persist until pool destruction. Chunk state persists only in the backend free structure and the caller-held `mlx5hws_pool_chunk`.

## Dependencies and integration points
This file depends on command helpers, table resource type mapping, context logging, Linux bitmaps and mutexes, and the HWS buddy allocator. It is used by context/action/matcher code for STE and STC resource management and by action STE pools for per-rule action STE memory.

## Risks and edge cases
Bitmap pools support only order-zero allocations; callers needing multi-STE chunks must request a buddy pool. Destroying a non-empty pool only logs an error before continuing, so callers must ensure all chunks are returned to avoid freeing resources still referenced by hardware or software. FDB mirror allocation doubles resource handling and must respect optimization side effects. `available_elems` accounting depends on valid chunk order and paired free calls.

## Test signals
Test STE and STC pool creation, bitmap order-zero allocation exhaustion/reuse, buddy variable-order allocation/free/coalescing, FDB mirror resources, optimization modes, allocation failure cleanup, non-empty destroy warnings, and concurrent allocation/free under the pool mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.h

## Purpose
`pool.h` declares the generic HWS STE/STC pool data model. It defines pool resource types, allocation chunks, pool attributes, database backends, function-pointer hooks, and inline helpers for base IDs and fullness checks.

## Important APIs, types, and functions
`enum mlx5hws_pool_type` distinguishes STE and STC pools. `struct mlx5hws_pool_chunk` carries offset and order. `struct mlx5hws_pool_resource` stores base object ID and range. `enum mlx5hws_pool_flags` enables buddy allocation. `enum mlx5hws_pool_optimize` controls original/mirror allocation optimization. `struct mlx5hws_pool_attr` configures pool type, table type, flags, optimization, and allocation size.

`struct mlx5hws_pool_db` stores bitmap or buddy backend state. `struct mlx5hws_pool` combines context, type, flags, mutex, size, available count, table type, resources, backend, and backend callbacks. Public functions create/destroy pools and allocate/free chunks. Inline helpers return base IDs and test empty/full state under the pool lock.

## Control flow
The header has no substantial runtime flow aside from inline getters and lock-protected `mlx5hws_pool_empty()` / `mlx5hws_pool_full()`. Implementation in `pool.c` fills callback pointers based on bitmap or buddy backend.

## State and persistence behavior
The pool struct is persistent runtime state for firmware STE/STC ranges. Resource base IDs remain valid until destroy. Backend state tracks free offsets. `available_elems` mirrors backend free space and is used by fullness helpers and destroy checks.

## Dependencies and integration points
The header depends on HWS context/table enums, Linux mutexes and bit operations, and the HWS buddy allocator type. It is consumed by context, matcher, action, and action STE pool code.

## Risks and edge cases
The backend function pointers must be initialized before allocation. The fullness helpers rely on `available_elems` being accurate. Optimization modes can create zero-sized original or mirror resources, so base-ID callers must use the right side for their table direction. Chunk order must match the backend capabilities.

## Test signals
Build coverage and generic pool runtime tests for bitmap and buddy modes, full/empty helpers, base ID access, and invalid allocation orders are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/prm.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/prm.h

## Purpose
`prm.h` defines HWS-specific mlx5 PRM constants, enums, and bit layouts for firmware objects and generated WQEs. It is the hardware contract layer for RTCs, STCs, STEs, definers, header-modify patterns, argument access, ASO modes, and flow-table modification fields.

## Important APIs, types, and functions
The header defines modify action type IDs, `enum mlx5_modification_field`, HCA capability opmods, RTC update/access/STE/reparse modes, STC action types, STC reparse modes, ASO object counts, header anchors, STC parameter layouts for table/TIR/counter/modify-header/ASO/remove/insert/vport/IPsec/trailer actions, RTC bits, STC bits, STE bits, definer bits, header modify pattern input bits, create object command input wrappers, generate-WQE input/output layouts, ASO opcode modifiers, and flow table miss/RTC modify field masks.

## Control flow
This header has no runtime control flow. Implementation files use these layouts with `MLX5_SET`, `MLX5_GET`, and command helpers to build firmware object create/modify/query inputs and WQE data. For example, matcher RTC creation fills `mlx5_ifc_rtc_bits`, action creation fills STC parameter unions, definer creation fills selector fields and masks, and pattern creation writes `mlx5_ifc_header_modify_pattern_in_bits`.

## State and persistence behavior
The structures represent serialized firmware command payloads and WQE payloads rather than owned software state. Values written using these layouts create or mutate persistent firmware objects such as RTCs, STCs, STE ranges, definers, patterns, and arguments.

## Dependencies and integration points
`prm.h` depends on common mlx5 IFC bitfield conventions and command infrastructure. It is included through `internal.h` by virtually all HWS modules, especially command, action, matcher, definer, send, and pattern/argument code.

## Risks and edge cases
Every field width and enum value is hardware ABI. Incorrect values can create invalid firmware objects or subtly wrong steering behavior. Several enum values alias protocol-specific fields, such as IPv4 protocol and IPv6 next-header modification. Insert/remove header layouts depend on anchors and size/offset constraints enforced elsewhere. Adding new actions requires updating action validation, STC generation, capability checks, and tests in addition to this header.

## Test signals
Build coverage catches syntax and type drift, but functional validation needs firmware object create/destroy tests for RTC/STC/STE/definer/pattern/argument flows, action tests for every STC type, insert/remove header validation, ASO modes, generated WQE tests, and negative tests for unsupported capability combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/prm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.c

## Purpose
`rule.c` implements low-level HWS rule create, destroy, action update, and resize-move operations. It builds STE WQEs from match templates and action templates, allocates action STE chunks when rules require multiple STEs, tracks rule status and delete/resize metadata, chooses RX/TX RTCs based on flow source, and validates IP-version consistency for matchers that match both ethertype and IP version.

## Important APIs, types, and functions
Public APIs are `mlx5hws_rule_create()`, `mlx5hws_rule_destroy()`, `mlx5hws_rule_action_update()`, `mlx5hws_rule_skip()`, `mlx5hws_rule_free_action_ste()`, `mlx5hws_rule_move_hws_add()`, `mlx5hws_rule_move_hws_remove()`, `mlx5hws_rule_move_in_progress()`, and `mlx5hws_rule_clear_resize_info()`.

Key internal helpers initialize dependent WQEs, copy match tags for updates, save/delete/load delete information, save resize information, allocate action STE chunks, create/update HWS WQEs, handle failed destroys, generate completions, perform resize add/remove, precheck enqueue conditions, and check outer/inner IP version consistency.

## Control flow
Rule creation first checks IP-version consistency against matcher state, records the matcher in the rule handle, verifies that the matcher is not resizing and that the send queue has room, validates template indexes and match parameters, then calls `hws_rule_create_hws()`. That function initializes rule status and send attributes, allocates a dependent WQE, fills RTC IDs based on flow source and matcher/collision RTCs, allocates action STE chunks if the action template requires them, applies action setters from last STE to first, creates the match tag through the definer for new rules, sends action STEs and match STEs, saves delete info for later removal, saves resize info for resizable matchers, increments queue rule count, and flushes dependent WQEs unless burst mode defers notification.

Destroy validates user data and queue capacity, rejects rules still creating/updating, handles already failed rules by generating a delete completion and freeing action STEs, handles complex `skip_delete` rules by completing without hardware delete, otherwise sends a deactivate STE WQE using saved tag/delete information and clears delete info. Action update requires a resizable matcher, rule-index optimization, or insert-by-index mode and a created rule; it reuses `hws_rule_create_hws()` with `match_param == NULL`, saves old action STEs, copies the prior tag, and writes replacement action/match STEs.

Resize move is two-phase. `mlx5hws_rule_move_hws_add()` verifies the rule belongs to a matcher in resize, saves old RTC IDs and rule index in `resize_info`, resets active RTC IDs, writes the saved STE data into the destination matcher RTCs, and marks move state writing. `mlx5hws_rule_move_hws_remove()` later deactivates the old RTC IDs using saved delete info and marks state deleting.

## State and persistence behavior
Rule state includes matcher pointer, match tag or resize info, current and old action STE chunks, active RX/TX RTC IDs, status, pending WQE count, and `skip_delete`. Non-resizable rules store the match tag for deletion. Resizable rules store full WQE control/data segments and old RTC IDs so they can be moved and later removed. Hardware state persists in STE tables and action STE chunks until deactivation and completion.

## Dependencies and integration points
This file depends on matcher attributes and RTC IDs, definer tag creation, action template setters, action STE pool allocation, send engine WQE posting/dependency handling/completion generation, PRM WQE layouts, Ethernet/IP constants, and BWC/complex rule behavior through `skip_delete`. It is called by public HWS users and matcher resize logic.

## Risks and edge cases
Asynchronous status transitions are central: destroying a rule while creating/updating returns `-EBUSY`, and failed rules follow a synthetic cleanup path. Action update can leak or prematurely free old action STEs if completion ordering is wrong. Delete requires saved match tags or resize data; missing metadata prevents correct deactivation. Flow-source optimization skips RX or TX RTCs, so wrong skip logic can install rules in the wrong direction. IP-version state is mutable on the matcher; inconsistent insertion order or concurrent rule creation can reject later rules or leave a matcher constrained unexpectedly. Burst mode requires callers to drain queues.

## Test signals
Test create/destroy for single-STE and multi-STE action templates, jumbo match tags, RX-only/TX-only flow sources, collision matcher retry RTCs, insert-by-index rules, action updates with and without action STE replacement, destroy during create/update, failed queue state cleanup, burst and non-burst behavior, resize move add/remove, complex `skip_delete`, and IP-version mismatch cases for outer and inner headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.h

## Purpose
`rule.h` declares the private HWS rule state and low-level rule helper API. It defines STE/tag sizes, rule lifecycle statuses, resize move states, match-tag storage, resize metadata, and the fields a rule needs for creation, update, deletion, action STE cleanup, and matcher resize.

## Important APIs, types, and functions
Constants define STE control size, action segment size, normal and jumbo match tag sizes, and jumbo tag offset. `enum mlx5hws_rule_status` tracks unknown, creating, created, updating, updated, deleting, deleted, failing, and failed states. `enum mlx5hws_rule_move_state` tracks idle, writing, and deleting during matcher resize.

`struct mlx5hws_rule_match_tag` overlays a jumbo tag with an action-reserved prefix plus normal match tag. `struct mlx5hws_rule_resize_info` stores old RTCs, rule index, move state, and saved WQE control/data segments. `struct mlx5hws_rule` stores matcher pointer, tag or resize info, current and old action STE chunks, active RTC IDs, status, pending WQEs, and `skip_delete`.

Declared helpers cover flow-source skip decisions, action STE free, resize remove/add, move-in-progress tests, and resize-info cleanup.

## Control flow
The header has no executable flow beyond declarations. `rule.c` mutates the declared state during create/update/delete/move, while matcher resize code calls move helpers and other modules free action STE chunks after completions.

## State and persistence behavior
The rule struct is the persistent handle supplied by API callers. Its RTC IDs and action STE chunks describe hardware resources currently associated with the rule. During resize, the union switches from tag storage to `resize_info`, which owns copied WQE segments required to recreate and delete the rule across matchers.

## Dependencies and integration points
The header depends on matcher declarations, action STE chunk types, WQE size constants, and public rule attributes. It is included by `internal.h`, matcher code, send completion code, BWC code, and action STE cleanup paths.

## Risks and edge cases
The union between `tag` and `resize_info` means code must know whether a matcher is resizable before reading deletion metadata. Status values must align with send completion transitions. `old_action_ste` is valid during updates only and must be freed after it is no longer referenced by hardware. `skip_delete` is specialized for complex rules and can intentionally suppress hardware deletion.

## Test signals
Build coverage plus rule create/update/delete, completion status transitions, action STE cleanup after update and delete, resizable matcher moves, non-resizable delete-tag storage, jumbo tag handling, and complex-rule skip-delete paths validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.h -->
