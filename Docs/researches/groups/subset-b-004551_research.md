# Research: subset-b-004551

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_matcher.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_matcher.c

## Purpose
`dr_matcher.c` turns a user-visible matcher mask into one or more ordered STE builder chains and connects those matcher chains into the RX, TX, or FDB table priority lists. It is the policy layer between match criteria (`outer`, `inner`, `misc*`) and the lower-level STE encoders in `dr_ste.c` / version-specific `dr_ste_v*.c`. It also owns matcher object lifetime, debug-list membership, and the hardware link updates that place or remove matchers from a table.

## Important APIs, Types, And Functions
The public entry points are `mlx5dr_matcher_create()`, `mlx5dr_matcher_destroy()`, `mlx5dr_matcher_add_to_tbl_nic()`, `mlx5dr_matcher_remove_from_tbl_nic()`, and `mlx5dr_matcher_select_builders()`. The main internal decision point is `dr_matcher_set_ste_builders()`, which copies the matcher mask into a temporary `struct mlx5dr_match_param`, selects builder callbacks based on nonzero mask fields, and verifies that all mask bytes were consumed. Helper predicates such as `dr_mask_is_tnl_geneve()`, `dr_mask_is_tnl_gtpu_any()`, `dr_mask_is_icmp()`, `dr_mask_is_reg_c_0_3_set()`, and `dr_mask_is_flex_parser_4_7_set()` encode capability-aware feature selection.

## Control Flow
Creation increments the parent table refcount, allocates and initializes `struct mlx5dr_matcher`, locks the domain, copies and validates the mask, initializes NIC-side matcher objects according to domain type, links the matcher into the debug list, then unlocks. For each NIC side, `dr_matcher_init_nic()` builds all IPv4/IPv6 outer/inner combinations, allocates an end anchor and start hash table, and keeps extra references so empty matchers remain present. FDB creates both RX and TX instances.

Builder selection is ordered. Outer criteria may add metadata/register builders, source GVMI/QPN, L2 source/destination, IPv4 or IPv6 L3/L4, tunnel parsers, MPLS, ICMP, GRE, and flexible parser builders. Inner criteria add tunneled L2/L3/L4/MPLS builders. Empty criteria produce an always-hit builder. Unsupported residual mask bytes cause `-EOPNOTSUPP`, which is an important guard against silently ignoring match fields.

## State And Persistence
Persistent state is in memory and hardware ICM tables: `matcher->mask`, per-IP-version `ste_builder_arr`, selected `ste_builder`, `num_of_builders_arr`, `s_htbl`, `e_anchor`, table list nodes, refcounts, and debug rule lists. `dr_nic_matcher_connect()` writes hardware links from previous anchor to current start table, current start to end anchor, and end anchor to the next matcher or table default ICM address. Removal reconnects the previous anchor directly to the next matcher or default destination.

## Dependencies And Integration Points
This file depends on `dr_types.h`, `mlx5dr_ste_build_*()` wrappers, STE hash table allocation and posting (`mlx5dr_ste_htbl_alloc()`, `mlx5dr_ste_htbl_init_and_postsend()`), domain/table locks, ICM pool address helpers, and device capabilities in `dmn->info.caps`. It integrates with `dr_rule.c`, which selects a precomputed builder chain for the concrete rule IP version and increments `nic_matcher->rules`, and with debug dumping via `matcher_list` and `dbg_rule_list`.

## Risks
The main correctness risk is capability-gated parser selection: Geneve, VXLAN-GPE, GTPU, MPLS-over-GRE/UDP, and ICMP rely on capability bits and flex parser IDs matching what the STE version supports. Residual-mask checking is strict, so new match fields must be consumed by a builder or matcher creation fails. Link insertion/removal updates both hardware and in-memory `pointing_ste` / `next_htbl`; partial failures could leave chains inconsistent if not handled by callers. Destroy refuses busy matchers via refcount, so leaked rules block matcher teardown.

## Test Signals
Useful tests include creating matchers for empty masks, unsupported partial masks, IPv4/IPv6 combinations, FDB source-port optimized RX paths, and capability-gated tunnel fields. Integration signals are successful rule insertion/removal through priority-ordered matcher lists, no residual mask bytes after builder selection, and hardware-table posts returning success during connect/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_matcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ptrn.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ptrn.c

## Purpose
`dr_ptrn.c` manages the modify-header pattern cache used on devices that support the pattern/argument modify-header model. Instead of posting a full modify-header action blob for every rule, it stores reusable pattern objects in dedicated ICM memory and lets per-rule arguments supply the variable inline data.

## Important APIs, Types, And Functions
The file defines `struct mlx5dr_ptrn_mgr`, which owns a domain pointer, a `DR_ICM_TYPE_MODIFY_HDR_PTRN` ICM pool, a cached pattern list, and `modify_hdr_mutex`. Public APIs are `mlx5dr_ptrn_mgr_create()`, `mlx5dr_ptrn_mgr_destroy()`, `mlx5dr_ptrn_cache_get_pattern()`, and `mlx5dr_ptrn_cache_put_pattern()`. Internal helpers compare patterns (`dr_ptrn_compare_modify_hdr()`), find an existing list entry (`dr_ptrn_find_cached_pattern()`), allocate a new pattern (`dr_ptrn_alloc_pattern()`), and free one (`dr_ptrn_free_pattern()`).

## Control Flow
`mlx5dr_ptrn_cache_get_pattern()` locks the cache, searches for an equivalent pattern, and either increments the cached object refcount or allocates a new ICM chunk and object. New patterns are masked before posting: for SET, ADD, and INSERT_INLINE actions, inline data is cleared because hardware later ORs pattern and argument data. The pattern is then posted with `mlx5dr_send_postsend_pattern()`. If posting fails, the refcount is dropped and the pattern is freed. Cache hits are moved to the list head to bias lookup toward recently used patterns.

## State And Persistence
Patterns persist as long as their `refcount` remains nonzero. Each `struct mlx5dr_ptrn_obj` stores a copy of hardware action data, the ICM chunk, action count, hardware pattern index, list node, and refcount. The index is computed from the chunk ICM address relative to `hdr_modify_pattern_icm_addr` in action-cache-line units. The cache list is in-memory; the pattern bytes are persisted to device ICM through the send path.

## Dependencies And Integration Points
This code depends on STE v1 action layouts (`mlx5_ifc_dr_ste_v1.h`) to read `action_id`, the domain capability helper `mlx5dr_domain_is_support_ptrn_arg()`, ICM chunk allocation, and the send-ring pattern post API. It is used by the modify-header action path through the STE context when the domain supports pattern arguments. The manager is created and destroyed with the domain.

## Risks
Comparison deliberately treats COPY actions as full 64-bit values but compares only the low 32 bits for other action IDs. That matches the pattern/argument model but is subtle and can incorrectly deduplicate if a new action type carries meaningful high bits. The destroy path warns if the list is non-empty but still frees listed objects without freeing their chunks through `dr_ptrn_free_pattern()`; this assumes normal users returned all refs before manager destruction. Mutex coverage is essential because pattern refcounts and list order are shared domain state.

## Test Signals
Exercise duplicate patterns with different inline data, COPY actions that differ in high bits, get/put refcount lifetimes, allocation failure, postsend failure cleanup, and manager destruction after all patterns are released. Hardware-level signals are correct pattern index calculation and successful modify-header rules using shared pattern plus per-rule arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ptrn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_rule.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_rule.c

## Purpose
`dr_rule.c` creates and destroys software steering rules under a matcher. It validates concrete match values against the matcher mask, builds STE byte arrays, inserts those STEs into hash tables, handles collisions and hash-table growth, attaches action STEs, posts hardware updates, and unwinds resources on failure or deletion.

## Important APIs, Types, And Functions
The public APIs are `mlx5dr_rule_create()`, `mlx5dr_rule_destroy()`, `mlx5dr_rule_set_last_member()`, and `mlx5dr_rule_get_reverse_rule_members()`. Important internals include `dr_rule_verify()`, `dr_rule_create_rule_nic()`, `dr_rule_handle_ste_branch()`, `dr_rule_handle_empty_entry()`, `dr_rule_handle_collision()`, `dr_rule_rehash_htbl()`, `dr_rule_handle_action_stes()`, and `dr_rule_clean_rule_members()`.

## Control Flow
Rule creation increments the matcher refcount, verifies `value->match_sz`, copies match parameters, and checks every value byte is covered by the matcher mask. Domain type selects RX, TX, or both sides for FDB. FDB copies the match parameter because builder/tag functions consume fields as they encode them.

For each NIC side, `dr_rule_create_rule_nic()` skips impossible FDB directions based on source port and flow source, locks the NIC domain, selects the builder chain by outer/inner IP version, adds the matcher to the table if needed, builds STE tags, builds action STE data, then walks the STE array. Each STE is placed by CRC hash into the current hash table. Empty slots become new branches; matching non-last STEs are reused; occupied slots either trigger rehash or allocate a collision table linked through the miss list. Action STEs are appended when actions require more STEs than match builders. The queued STE updates are posted in reverse order so downstream STEs exist before upstream hit pointers expose them.

## State And Persistence
State spans `struct mlx5dr_rule`, `rule_actions_list`, RX/TX `last_rule_ste`, action refcounts, STE refcounts, miss lists, hash table collision counters, and matcher rule counters. Hardware persistence is through posted STE writes and hash table rewrites. Rehash allocates a larger table, copies entries and miss lists, posts the new table, updates the previous pointer, then releases the old table reference after the connect update is queued.

Destroy walks from the rule's last STE back to the first through `pointing_ste` and miss lists, calls `mlx5dr_ste_put()` for each, decrements matcher rule counters, and removes the matcher from the NIC table when the last rule is gone.

## Dependencies And Integration Points
This file is the central integration point for matchers, STE encoding, action encoding, ICM allocation, send-ring posting, and debug rule tracking. It calls `mlx5dr_matcher_select_builders()`, `mlx5dr_ste_build_ste_arr()`, `mlx5dr_actions_build_ste_arr()`, `mlx5dr_send_fill_and_append_ste_send_info()`, `mlx5dr_send_postsend_ste()`, `mlx5dr_send_postsend_htbl()`, and matcher table add/remove routines. It relies on domain NIC locks for per-side table mutation.

## Risks
Collision and rehash logic is complex: miss-list head replacement, `pointing_ste`, `next_htbl`, and rule last-member pointers must remain synchronized. Duplicate last-STE insertion is logged but still proceeds into collision handling, so callers should not depend on duplicate rejection. Failure unwinds must free pending send-info objects and remove table links only when no rules exist. Optimized stack STE arrays are disabled for small `CONFIG_FRAME_WARN`; changes to builder counts or action STE limits need stack-size review.

## Test Signals
Key tests include value-not-covered-by-mask rejection, RX/TX/FDB insertion and skip behavior, duplicate rules, high-collision insertion that triggers rehash, action chains that add STEs, failure injection for send-info allocation and postsend, and destruction of head, middle, and only STEs in miss lists. Runtime signals are no leaked matcher refs, correct rule counters, stable hardware after rehash, and successful reverse-order post updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_rule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_send.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_send.c

## Purpose
`dr_send.c` is the low-level transport for writing STEs, hash tables, modify-header actions, patterns, and arguments into hardware memory. It creates a loopback RC QP/CQ pair, stages data through DMA buffers when needed, posts RDMA write/read or flow-table-access WQEs, and drains completions to keep the send queue bounded.

## Important APIs, Types, And Functions
Public APIs include `mlx5dr_send_info_pool_create()`, `mlx5dr_send_info_pool_destroy()`, `mlx5dr_send_info_alloc()`, `mlx5dr_send_info_free()`, `mlx5dr_send_fill_and_append_ste_send_info()`, `mlx5dr_send_postsend_ste()`, `mlx5dr_send_postsend_htbl()`, `mlx5dr_send_postsend_formatted_htbl()`, `mlx5dr_send_postsend_action()`, `mlx5dr_send_postsend_pattern()`, `mlx5dr_send_postsend_args()`, `mlx5dr_send_ring_alloc()`, and `mlx5dr_send_ring_free()`. Important state types are `struct mlx5dr_send_ring`, `struct mlx5dr_qp`, `struct mlx5dr_cq`, `struct mlx5dr_mr`, `struct postsend_info`, and pooled `struct mlx5dr_ste_send_info`.

## Control Flow
Send-ring allocation creates a CQ, RC QP, moves the QP through RST->INIT->RTR->RTS, allocates a staging buffer and sync buffer, and registers both as physical-address mkeys. Posts are serialized under `send_ring->lock`. Before posting, `dr_handle_pending_wc()` polls completions when the number of pending WQEs reaches the signal threshold or drains harder when the queue is near full.

ICM writes are posted as an RDMA write followed by an RDMA read into the sync buffer, giving ordering/synchronization. Modify-header arguments use `MLX5_OPCODE_FLOW_TBL_ACCESS` and are chunked by action cache line. Hash-table posts format either default STEs or existing reduced STEs plus masks, preparing each STE for the hardware format through the STE context before posting.

## State And Persistence
The file maintains RX/TX send-info pools, send queue producer/consumer accounting, CQ ownership state, `pending_wqe`, `tx_head`, `signal_th`, DMA-backed staging memory, an error-state bit, QP/CQ resources, and registered memory keys. Hardware persistence is the remote ICM or argument memory written by successful WQEs. If the device is in internal error or the ring is in error state, posts are skipped with success-like return to avoid making shutdown worse.

## Dependencies And Integration Points
It integrates with mlx5 core command APIs, work queue helpers, CQ helpers, DMA mapping, GID querying, ICM chunk address/rkey helpers, and STE preparation callbacks. `dr_rule.c`, `dr_ste.c`, `dr_ptrn.c`, and action code all rely on this file for posts. Capability fields control force-loopback QP setup, RoCE GID use, isolated VL/TC, inline size, and source UDP port.

## Risks
Queue accounting is subtle because ICM writes consume two WQEs while argument updates consume one. CQ errors set `err_state`; after that, callers may see posts skipped instead of failed. Large table writes are split by `max_post_send_size`; iteration math must match chunk sizes. Resource teardown assumes QP/CQ/MR creation reached the corresponding stage. DMA mapping and mkey creation failures need exact unwind order to avoid leaks.

## Test Signals
Useful tests include send-info pool refill/exhaustion, QP setup with and without force-loopback, CQ polling on success and error CQEs, posts with inline and staged data, table writes larger than one post, argument writes spanning multiple cache lines, and shutdown behavior during internal device error. Integration signals are successful rule/matcher hardware programming and no pending-WQE deadlock under high update rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.c

## Purpose
`dr_ste.c` provides format-independent STE and hash-table services: hash-index calculation, STE address helpers, miss-list deletion behavior, hash table allocation/free, action wrapper calls, match-parameter parsing, prechecks, generic STE-array construction, and dispatch to version-specific STE contexts.

## Important APIs, Types, And Functions
Important exported functions include `mlx5dr_ste_calc_hash_index()`, `mlx5dr_ste_conv_bit_to_byte_mask()`, `mlx5dr_ste_set_bit_mask()`, `mlx5dr_ste_get_icm_addr()`, `mlx5dr_ste_get_mr_addr()`, `mlx5dr_ste_get_hw_ste()`, `mlx5dr_ste_get_miss_list()`, `mlx5dr_ste_free()`, `mlx5dr_ste_htbl_alloc()`, `mlx5dr_ste_htbl_free()`, `mlx5dr_ste_create_next_htbl()`, `mlx5dr_ste_htbl_init_and_postsend()`, `mlx5dr_ste_copy_param()`, `mlx5dr_ste_build_ste_arr()`, and `mlx5dr_ste_get_ctx()`. It also exposes wrapper builders such as `mlx5dr_ste_build_eth_l2_src_dst()` and `mlx5dr_ste_build_tnl_gtpu_flex_parser_0()`.

## Control Flow
Matcher creation calls wrapper builders, which set `rx`, `inner`, capabilities/domain fields, then dispatch to `ste_ctx->build_*_init()`. Rule creation calls `mlx5dr_ste_build_ste_arr()`, which initializes each STE, copies the builder bit mask, invokes the builder tag function to encode concrete values, and connects each STE to the next lookup type and byte mask.

Table allocation obtains a `struct mlx5dr_ste_htbl` and ICM chunk, initializes every STE and miss-list head, and stores lookup metadata. `mlx5dr_ste_create_next_htbl()` allocates and posts a next table for non-last STEs, sets the hit address in the current hardware STE, and records `next_htbl` / `pointing_ste`.

## State And Persistence
STE state is split: reduced hardware STE bytes live in `chunk->hw_ste_arr`, software metadata lives in `chunk->ste_arr`, and collision chains live in per-index `miss_list`. `mlx5dr_ste_free()` updates hardware differently for three deletion cases: only head becomes always-miss, head with collisions is replaced by the next collision STE, and middle collision updates the previous miss address. Hash table refcounts gate `mlx5dr_ste_htbl_free()`.

## Dependencies And Integration Points
This file depends on Linux CRC32, mlx5 IFC field helpers, ICM pool helpers, send posting, rule last-member repair, and the version-specific STE contexts declared in `dr_ste.h`. It parses user match buffers in the hardware FTE layout into `struct mlx5dr_match_param` and optionally clears consumed source bytes to let matcher creation detect unsupported fields.

## Risks
The hash function masks tag bytes according to `byte_mask`; any builder mask bug changes collision behavior and lookup correctness. STE deletion mutates list topology and hardware in tandem, so errors can orphan collision entries or leave stale rule last STEs. `mlx5dr_ste_copy_param()` supports truncated match buffers by copying tails into a temporary buffer; boundary mistakes here can corrupt match interpretation. Prechecks only enforce a few partial-mask constraints, so unsupported semantics must be caught by residual-mask checks.

## Test Signals
Test signals include deterministic hash indexes for known tags/masks, correct byte-mask conversion, STE-array construction consuming all value fields, partial source-port/IP mask rejection, next-table allocation and posts, deletion of only/head/middle collision entries, and version selection for ConnectX-5/6DX/7/8. Runtime signals are clean hash-table refcounts and no stale `pointing_ste` after delete or rehash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.h

## Purpose
`dr_ste.h` defines shared constants, field-setting macros, action modify enums, and the `struct mlx5dr_ste_ctx` vtable used by the software steering code to isolate generic rule/matcher logic from STE hardware-format versions.

## Important APIs, Types, And Functions
The header exports constants for IP/L4/VLAN encodings and L2 header lengths, helper macros such as `DR_STE_SET_VAL`, `DR_STE_SET_TAG`, `DR_STE_SET_ONES`, `DR_STE_SET_TCP_FLAGS`, `DR_STE_SET_MPLS`, and `DR_STE_SET_FLEX_PARSER_FIELD`, and parser helpers like `dr_ste_calc_flex_parser_offset()`. It declares `mlx5dr_ste_conv_bit_to_byte_mask()` and version context getters `mlx5dr_ste_get_ctx_v0()` through `mlx5dr_ste_get_ctx_v3()`.

The central type is `struct mlx5dr_ste_ctx`, which contains builder initializers for L2/L3/L4/tunnel/register/flex-parser match types, core STE getters/setters, action encoding callbacks, modify-header field metadata, reformat action callbacks, and an optional postsend preparation hook.

## Control Flow
Generic code calls wrapper functions in `dr_ste.c`; those wrappers populate common fields in `struct mlx5dr_ste_build` and invoke the matching `mlx5dr_ste_ctx` function pointer. Version-specific files fill this vtable with callbacks that know their hardware layout. Macros both set hardware tag/mask fields and clear consumed software fields, which drives the residual-mask and residual-value validation model.

## State And Persistence
The header itself owns no runtime state, but its vtable controls all persistent hardware encoding state written into STE ICM memory. The field-clearing macros intentionally mutate temporary masks or values to mark fields consumed. `actions_caps`, `modify_field_arr`, and `modify_field_arr_sz` describe the action surface supported by the selected STE version.

## Dependencies And Integration Points
It includes `dr_types.h` and relies on mlx5 IFC structures through the `MLX5_SET` family used by implementation files. `dr_matcher.c` selects builders through this interface, `dr_rule.c` invokes generated builder chains, `dr_actions` code uses action callbacks and modify-field mappings, `dr_send.c` calls `prepare_for_postsend()`, and `dr_ste.c` dispatches version selection.

## Risks
Because macros clear source fields, callers must pass temporary copies when they need to reuse match parameters. Adding a builder callback to generic code requires adding it to this context and all supported version implementations or guarding for NULL. Flex parser offset calculation assumes groups of four parser IDs and tag layout compatibility. Incorrect length constants for L2 decap actions would reject valid reformat data or emit malformed modify actions.

## Test Signals
Compile coverage across all STE format versions is important because the vtable is broad. Unit-like signals include macro consumption behavior, flex parser offset placement, TCP flag expansion, MPLS field packing, action modify field lookups, and NULL handling for optional callbacks. Integration tests should exercise the same match/action feature on each supported steering format version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v0.c

## Purpose
`dr_ste_v0.c` implements the ConnectX-5 (`MLX5_STEERING_FORMAT_CONNECTX_5`) STE format. It provides the v0 `mlx5dr_ste_ctx` callbacks for STE initialization, hit/miss address encoding, match builder initialization/tag encoding, RX/TX action encoding, modify-header action encoding, and decap-L3 action-list generation.

## Important APIs, Types, And Functions
The public output is `mlx5dr_ste_get_ctx_v0()`, returning `ste_ctx_v0`. The file defines v0 entry types, tunnel/action encodings, lookup-type constants, modify-header hardware field mappings, and many builder callbacks. Core setters include `dr_ste_v0_set_miss_addr()`, `dr_ste_v0_get_miss_addr()`, `dr_ste_v0_set_hit_addr()`, `dr_ste_v0_set_next_lu_type()`, `dr_ste_v0_set_byte_mask()`, and `dr_ste_v0_init()`. Action encoders include `dr_ste_v0_set_actions_tx()`, `dr_ste_v0_set_actions_rx()`, `dr_ste_v0_set_action_set()`, `dr_ste_v0_set_action_add()`, `dr_ste_v0_set_action_copy()`, and `dr_ste_v0_set_action_decap_l3_list()`.

## Control Flow
Each match builder has an init function that encodes the matcher mask into `sb->bit_mask`, computes `sb->byte_mask`, sets a v0 lookup type, and installs a tag-build function. At rule insertion, the tag-build function encodes concrete values and clears consumed fields. Builders cover L2 source/destination, tunnel L2, IPv4 5-tuple and misc, IPv6 L3/L4, MPLS, GRE, MPLS-over-GRE/UDP via flex parsers, ICMP via parser IDs, metadata/registers, source GVMI/QPN, programmable flex parsers, Geneve/VXLAN-GPE/GTPU tunnel headers, GTPU flex parser fields, and tunnel header words 0/1.

Action flow differs for TX and RX. TX orders modify-header before encapsulation, handles push VLANs, emits extra STEs when modify/push/encap cannot share one STE, sets counters, and finally points to the final ICM address. RX handles counters, L3/L2 decap, pop VLAN, modify header, and flow tags, adding extra STEs when entry-type conflicts require it.

## State And Persistence
The static `ste_ctx_v0` vtable is the long-lived state. Runtime state is encoded into hardware STE byte arrays: entry type, lookup type, next lookup type, byte mask, hit/miss addresses, GVMI, counters, flow tags, tunnel actions, rewrite action indexes, reformat IDs, and flex parser values. Modify-field metadata maps software action fields to v0 hardware modify fields with bit ranges and optional L3/L4 type constraints.

## Dependencies And Integration Points
The file depends on `dr_ste.h`, Linux types/CRC headers, mlx5 IFC layouts, domain capabilities for parser IDs and `prio_tag_required`, and generic action attributes built outside this file. It is selected by `mlx5dr_ste_get_ctx()` for ConnectX-5 and is called by matcher/rule/action code only through the context interface.

## Risks
This file is dense with hardware layout assumptions. Lookup-type selection must match RX/TX/inner direction; flex parser IDs must map to FLEX_PARSER_0 or FLEX_PARSER_1 correctly; source GVMI/QPN lookup depends on vport capabilities and peer domains; and action splitting must respect v0 entry-type limitations. Many builders consume fields by clearing them, so missing a clear yields false unsupported-field errors, while clearing too much hides invalid input.

## Test Signals
Test signals include v0 matcher creation for each builder family, concrete rule tags for IPv4/IPv6/L2/tunnel/register/flex-parser cases, source-port matching across local and peer domains, TX action combinations of modify/push/encap/counter, RX combinations of decap/pop/modify/tag/counter, decap-L3 with and without VLAN, and parser-ID boundary cases around `DR_STE_MAX_FLEX_0_ID`. Hardware integration should verify packets hit expected rules on ConnectX-5 format devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v0.c -->
