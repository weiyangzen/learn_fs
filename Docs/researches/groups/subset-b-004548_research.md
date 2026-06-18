# Research: subset-b-004548

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.h

## Purpose
`action.h` is the internal Hardware Steering action contract for mlx5 HWS. It defines how higher-level rule actions are represented as steering table context (STC) slots, WQE data words, action templates, and concrete action objects. It is consumed by rule insertion, BWC compatibility code, action STE pools, command wrappers, debug dumping, and matcher setup.

## Important APIs, Types, And Functions
Key constants describe the action STE budget (`MLX5HWS_ACTION_MAX_STE`), STC indexes, action data offsets, and header/reformat sizes. `struct mlx5hws_action_default_stc` and `struct mlx5hws_action_shared_stc` are context-owned reusable STC resources with refcounts protected by `ctx->ctrl_lock`. `struct mlx5hws_actions_apply_data` is the transient rule-WQE population state, and `struct mlx5hws_actions_wqe_setter` stores per-stage callbacks plus slot indexes. `struct mlx5hws_action_template` is the processed sequence used by matchers, while `struct mlx5hws_action` stores action-specific backing objects such as STCs, modify-header pattern/argument IDs, packet reformat IDs, destination arrays, ASO objects, range tables, and table jumps.

The exported helpers include action type formatting, default STC get/put, decap L3 data preparation, action-template processing, combination validation, and single STC allocation/free. The inline setters fill missing action slots with default NOP STCs and `mlx5hws_action_apply_setter()` writes the control, action, and hit STC indexes into the WQE.

## Control Flow And State
Action template processing precomputes setter callbacks and flags; rule creation later iterates setters and calls `mlx5hws_action_apply_setter()`. The inline path always emits a control STC, handles either normal single/double/triple action layouts or jumbo STE layout, then emits the hit action and encodes the number of STC actions in the control STC index word.

## Dependencies And Integration Points
This header depends on HWS context, pools, command STC attributes, send queues, rule actions, and mlx5 PRM action types supplied through `internal.h`. BWC uses action templates for compatibility matchers, action STE pool code allocates jump-to-STE-table STCs with these offsets, and debug code prints action-template contents through `mlx5hws_action_type_to_str()`.

## Risks And Test Signals
The main risks are STC index/offset mismatches, incorrect action-combination classification, refcount imbalance for shared/default STCs, and endian mistakes while writing WQE data. Useful test signals are rule insertion with no-op/default slots, combinations of single/double/triple actions, jumbo STE rules, decap/reformat actions, and teardown paths that verify shared STC reference counts return to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.c

## Purpose
`action_ste_pool.c` implements per-queue repositories of action STE tables used when actions need their own STE ranges, such as jump-to-STE-table flows. It grows tables on demand, separates RX-only, TX-only, and RX/TX allocations to avoid wasting mirrored entries, and periodically garbage-collects stale full tables.

## Important APIs, Types, And Functions
The public entry points are `mlx5hws_action_ste_pool_init()`, `mlx5hws_action_ste_pool_uninit()`, `mlx5hws_action_ste_chunk_alloc()`, and `mlx5hws_action_ste_chunk_free()`. Creation helpers allocate an STE pool (`hws_action_ste_table_create_pool()`), create RX/TX RTCs (`hws_action_ste_table_create_rtcs()`), and allocate a jump-to-STE-table STC (`hws_action_ste_table_create_stc()`). `hws_action_ste_choose_elem()` maps `skip_rx`/`skip_tx` to the correct pool optimize element. Cleanup is driven by `hws_action_ste_pool_cleanup()` delayed work.

## Control Flow And State
Initialization allocates one `struct mlx5hws_action_ste_pool` per HWS queue and initializes three elements for `MLX5HWS_POOL_OPTIMIZE_NONE`, `ORIG`, and `MIRROR`. Allocation locks the selected pool, tries every available table, creates a larger table if needed, stores the owning table in `chunk->action_tbl`, and moves a table to the `full` list when the backing pool is empty. Freeing returns the chunk to its buddy pool, updates `last_used`, and moves the table back to `available`.

Table size grows from log size 10 by one until log size 20. The delayed cleanup scans all queues and optimization elements, collects available tables that are still full and older than 300 seconds, drops the pool lock, then destroys their STC, RTCs, and STE pool.

## Dependencies And Integration Points
This file integrates with `mlx5hws_pool_create()`, pool chunk alloc/free, RTC and STC command wrappers, `mlx5hws_action_alloc_single_stc()`, context reparse-mode selection, and context lifetime in `context.c`. It is also dumped by `debug.c`.

## Risks And Test Signals
Risks include allocation/free ordering around firmware resources, stale cleanup racing with allocation, choosing the wrong RX/TX optimized pool, and leaked delayed work on context close. Test signals include repeated chunk allocation/free, RX-only and TX-only rules, allocation growth across several log sizes, cleanup after expiration, and failure injection at pool/RTC/STC creation stages to verify unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.h

## Purpose
`action_ste_pool.h` declares the in-memory model and API for action STE pooling. It is the boundary between action/rule code that needs STE chunks and the implementation that owns backing STE pools, RTCs, and jump STCs.

## Important APIs, Types, And Functions
The header defines initial, step, and maximum table log sizes, plus cleanup and expiration periods. `struct mlx5hws_action_ste_table` wraps one STE pool, its jump STC, RX/TX RTC IDs, list membership, parent pool element, and `last_used` timestamp. `struct mlx5hws_action_ste_pool_element` groups available/full tables for one optimization mode and remembers the largest size allocated so far. `struct mlx5hws_action_ste_pool` contains a mutex and one element for each `mlx5hws_pool_optimize` mode. `struct mlx5hws_action_ste_chunk` is the caller-facing allocation result containing the table pointer and pool chunk.

The API exposes context-wide init/uninit and chunk alloc/free. Callers must set `chunk->ste.order` before allocation; allocation fills the table pointer and offset.

## Control Flow And State
The state is volatile kernel memory tied to an HWS context. Tables persist until explicit uninit or delayed cleanup removes stale full tables. List placement tracks whether a table can be searched for new chunks (`available`) or is exhausted (`full`). The per-pool mutex serializes allocation, free, and garbage-collection list movement.

## Dependencies And Integration Points
Definitions depend on HWS context, pool chunks, `list_head`, mutexes, delayed cleanup in `context.c`, action STC helpers, and command-level RTC creation. BWC complex/simple rule insertion can allocate action STEs through rule/action paths that depend on this contract.

## Risks And Test Signals
The header’s correctness depends on callers honoring `chunk->ste.order` and not freeing chunks after context teardown. Useful tests allocate each optimization mode (`skip_rx`, `skip_tx`, neither), exercise full/available transitions, and verify that debug dumps can safely walk table lists under the pool lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action_ste_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.c

## Purpose
`buddy.c` implements a compact buddy allocator used by HWS pools to allocate power-of-two chunks from firmware object ranges. It tracks free segments by order using Linux bitmaps.

## Important APIs, Types, And Functions
`mlx5hws_buddy_create()` allocates the object and initializes per-order bitmaps and free counters through `hws_buddy_init()`. `mlx5hws_buddy_alloc_mem()` finds the smallest available segment at or above the requested order, splits larger segments down to the requested order, and returns the segment offset. `mlx5hws_buddy_free_mem()` coalesces with free buddies while possible, then marks the final segment free. `mlx5hws_buddy_cleanup()` frees the bitmap arrays.

## Control Flow And State
Initialization creates `max_order + 1` bitmaps. Order `max_order` starts with a single free segment. Allocation scans upward from the requested order, clears the selected bit, decrements its free count, then repeatedly splits by shifting the segment and setting the sibling bit at lower orders. Freeing shifts the segment by order, repeatedly merges while the sibling bit is set, and sets the merged segment in the final order.

The allocator has no internal locking; callers must serialize access. It stores only in-memory bitmap state and does not persist across pool destruction.

## Dependencies And Integration Points
It relies on kernel bitmap allocation, `find_first_bit()`, `test_bit()`, and HWS pool code that translates pool chunks into firmware object offsets. `buddy.h` exposes the state shape and API.

## Risks And Test Signals
Risks are invalid order/segment inputs, lack of locking in direct callers, integer shifts at large `max_order`, and double-free corruption because `free_mem()` does not validate that the target segment is currently allocated. Test signals include exhaustive allocate/free cycles, fragmentation/coalescing patterns, invalid allocation exhaustion returning `-ENOMEM`, and running under lockdep/KASAN with pool users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.h

## Purpose
`buddy.h` declares the HWS buddy allocator used by pool implementations that need variable-sized allocations from a fixed object range.

## Important APIs, Types, And Functions
`struct mlx5hws_buddy_mem` contains an array of per-order bitmaps, per-order free counts, and the maximum order. The exported functions are `mlx5hws_buddy_create()`, `mlx5hws_buddy_cleanup()`, `mlx5hws_buddy_alloc_mem()`, and `mlx5hws_buddy_free_mem()`.

## Control Flow And State
The state model is intentionally minimal. The allocator starts with one free block at `max_order`; allocations split larger blocks and frees coalesce with buddy blocks. The header does not declare any lock, so ownership and serialization are delegated to pool-level callers.

## Dependencies And Integration Points
This header is included by `buddy.c` and by HWS pool code that needs low-level chunk management. The returned segment offsets feed into `struct mlx5hws_pool_chunk` offsets used by action STCs, match STEs, and action STE chunks.

## Risks And Test Signals
The contract assumes valid power-of-two order semantics and serialized callers. Tests should check allocation exhaustion, reuse after free, coalescing to the top order, and caller behavior when `mlx5hws_buddy_create()` returns NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/buddy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.c

## Purpose
`bwc.c` implements the backward-compatible HWS API layer for matcher and rule creation. It creates resizable HWS matchers behind a compatibility interface, manages action-template attachment, chooses BWC queues, synchronously polls rule operations, and grows or shrinks matchers by rehashing rules.

## Important APIs, Types, And Functions
Public entry points include `mlx5hws_bwc_matcher_create()`, `mlx5hws_bwc_matcher_destroy()`, `mlx5hws_bwc_rule_create()`, `mlx5hws_bwc_rule_destroy()`, `mlx5hws_bwc_rule_action_update()`, `mlx5hws_bwc_queue_poll()`, and the simple matcher/rule helpers also used by `bwc_complex.c`. Internal helpers initialize matcher attributes, lock BWC queues, create and destroy simple matchers, extend action-template arrays, determine rehash thresholds, move rules during resize, and maintain per-RX/TX rule counters.

## Control Flow And State
Matcher creation verifies BWC support, initializes RX/TX size logs and atomics, then chooses simple or complex creation based on whether the match mask fits a single definer. Simple matchers allocate per-BWC-queue rule lists, create a dummy action template, build one match template, and create a resizable HWS matcher.

Rule creation allocates an HWS rule wrapper, derives skip-RX/TX from flow source, chooses a random BWC queue index, locks that queue, finds or attaches an action template matching the requested action types, increments counters, possibly rehashes, creates the HWS rule, polls completion synchronously, and links the rule into the queue list. Non-busy insertion failures trigger one forced rehash retry. Destruction synchronously deletes the HWS rule, removes it from the list, decrements counters, and if the matcher becomes empty, locks all BWC queues and shrinks back to the initial size.

## Dependencies And Integration Points
The file depends on context BWC queue partitioning, HWS matcher/rule APIs, action and match template APIs, complex matcher helpers, send queue polling/flushing, and firmware capability limits. Complex matchers reuse the simple rule/matcher machinery for each submatcher.

## Risks And Test Signals
Risks include deadlocks during queue-lock release/reacquire around all-queue rehash, partial rehash failure because old matcher rollback is not possible, action-template leaks after attach failure, queue polling timeouts, and counter/list inconsistency on create/destroy failures. Test signals include high collision insertion, rehash growth and shrink, concurrent create/destroy on different BWC queues, action update with new action templates, queue full/timeout injection, and complex/simple selection coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.h

## Purpose
`bwc.h` declares the compatibility matcher/rule data structures and APIs for HWS BWC mode. It defines how BWC queues, resizable matcher sizes, action-template arrays, and rule lists are represented across simple and complex matchers.

## Important APIs, Types, And Functions
Constants define the initial matcher size, resize step, 70 percent rehash threshold, burst polling threshold, maximum attached action templates, maximum actions, and polling timeout. `enum mlx5hws_bwc_matcher_type` distinguishes standalone simple matchers, first complex matchers, and complex submatchers. `struct mlx5hws_bwc_matcher_size` stores size log and atomic counters. `struct mlx5hws_bwc_matcher` owns the underlying matcher, match template, action-template array, optional complex data, RX/TX sizes, and per-queue rule lists. `struct mlx5hws_bwc_rule` wraps a rule, links subrules, stores flow source and queue assignment, and tracks RX/TX skipping.

The header exports simple matcher/rule operations, generic BWC create/destroy/update functions, rule-attribute filling, queue polling, and inline queue-count/queue-ID mapping.

## Control Flow And State
The queue mapping reserves the first send queue as control and splits the remaining queues into regular HWS queues and BWC queues; BWC queue IDs are offset by the number of BWC queues. Matcher state is mutable because action templates and size logs grow dynamically and shrink when rule counts return to zero.

## Dependencies And Integration Points
It depends on `context.h` for capability checks and queue count, HWS table/matcher/rule/action types, and `bwc_complex.h` for complex matcher extension. The structures are inspected by debug dumping and operated on by `bwc.c` and `bwc_complex.c`.

## Risks And Test Signals
Risks are incorrect queue math when `ctx->queues` is small or BWC support is absent, atomic size counters diverging from rule lists, and callers using simple helpers on complex-first matchers incorrectly. Tests should validate queue count mapping, matcher type dispatch, rule list ownership, and teardown with nonzero counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc_complex.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc_complex.c

## Purpose
`bwc_complex.c` implements BWC matchers whose masks are too large for one hardware definer. It splits a wide match into up to four simple submatchers, chains them with metadata register C6, deduplicates identical subrules, and moves complex subrules during resize.

## Important APIs, Types, And Functions
`mlx5hws_bwc_match_params_is_complex()` checks whether a mask exceeds a definer. `mlx5hws_bwc_matcher_create_complex()` splits the mask and initializes submatchers; `mlx5hws_bwc_matcher_destroy_complex()` tears them down. `mlx5hws_bwc_rule_create_complex()` and `mlx5hws_bwc_rule_destroy_complex()` create/destroy chained subrules. `mlx5hws_bwc_matcher_complex_move()` and `mlx5hws_bwc_matcher_complex_move_first()` support resize. Internal helpers split masks (`hws_bwc_matcher_split_mask()`), avoid IPv6 address ambiguity, create isolated tables, initialize hash tables and ID allocators, create metadata/last actions, and manage subrule refcount data.

## Control Flow And State
Creation copies and consumes the original mask into submasks. All submatchers after the first also match on register C6. The first submatcher lives in the original table; later submatchers live in isolated tables whose miss path points to the original matcher end anchor. Non-last submatchers use chain actions: set C6, jump to the next table, and last action. The final submatcher uses the caller’s actions.

Rule creation duplicates match parameters, creates the first subrule, then for each later subrule writes the previous chain ID into C6 and either chains onward or applies user actions. Each submatcher hashes `mlx5hws_rule_match_tag` to a `mlx5hws_bwc_complex_subrule_data` record with refcount, chain ID, RTCs, and move state. Duplicate subrules share the physical rule and set `skip_delete` on non-last deletion.

## Dependencies And Integration Points
This file depends on definer layout calculation, match template creation, BWC simple matcher/rule APIs, action creation for modify-header/table/last actions, table creation and miss modification, rhashtable, IDA, and queue polling. It relies on `bwc.c` to perform per-submatcher rehash and synchronous rule operations.

## Risks And Test Signals
Risks include mask splitting that changes IPv6 semantics, exceeding the four-submatcher limit, C6 chain ID leaks, hash/refcount mismatches, isolated table miss loops during first-submatcher resize, and partial create/destroy failures across a chain. Tests should cover large IPv6 masks, duplicate subrules, rehash of first and non-first submatchers, destruction after partial creation failure, and action updates that target the last subrule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc_complex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc_complex.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc_complex.h

## Purpose
`bwc_complex.h` declares the data structures and APIs used when BWC match parameters require multiple chained submatchers.

## Important APIs, Types, And Functions
The header caps complex matchers at `MLX5HWS_BWC_COMPLEX_MAX_SUBMATCHERS` of four. `struct mlx5hws_bwc_complex_subrule_data` stores a match tag, refcount, C6 chain ID, cached RTC IDs for duplicate-rule moves, a move marker, and a hash node. `struct mlx5hws_bwc_complex_submatcher` owns an optional isolated table, a destination-table action, the simple BWC matcher, a rules hash, an IDA for chain IDs, and a mutex. `struct mlx5hws_bwc_matcher_complex_data` groups submatchers and shared chain actions.

The public functions detect complex masks, create/destroy complex matchers, move first/non-first submatchers during resize, and create/destroy complex rules.

## Control Flow And State
Complex state is hierarchical: one outer `mlx5hws_bwc_matcher` points to `complex` data, which owns submatchers. First-submatcher storage is embedded in the outer matcher; later submatchers allocate their own simple matcher objects. Rule chains are represented by `next_subrule`, while shared physical subrules are represented by hash-table refcounts.

## Dependencies And Integration Points
The header depends on BWC base structures, HWS table/action/matcher/rule types, `rhashtable`, `ida`, mutexes, and definer match tags. `bwc.c` dispatches to these APIs when a match mask does not fit a single definer.

## Risks And Test Signals
Risks are lifetime ordering between isolated tables, table actions, and submatcher objects; missing hash-lock coverage; and users assuming one compatibility rule equals one hardware rule. Tests should create masks requiring two, three, and four submatchers, verify duplicate refcounts, and destroy matchers only after all subrules are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/bwc_complex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.c

## Purpose
`cmd.c` is the firmware command marshalling layer for HWS. It translates HWS-internal attributes into mlx5 command mailboxes for flow tables, flow groups, FTEs, RTCs, STCs, STEs, definers, packet reformat contexts, send queues, generated WQEs, capability queries, and GVMI lookup.

## Important APIs, Types, And Functions
The file exports create/modify/query/destroy wrappers for flow tables, RTCs, STCs, STE pools, definers, header modify arguments and patterns, packet reformat contexts, generated WQEs, forward tables, and FTEs. `hws_cmd_stc_modify_set_stc_param()` is the central STC action switch and covers counters, TIR/FT jumps, modify-header lists, header insert/remove, modify actions, vport/uplink jumps, ASO, jump-to-STE-table, remove words, IPsec crypto, and trailer actions. `mlx5hws_cmd_query_caps()` performs several capability queries and fills `struct mlx5hws_cmd_query_caps`.

## Control Flow And State
Most functions build zeroed command input buffers with `MLX5_SET`, execute `mlx5_cmd_exec*()`, copy IDs or queried fields from output buffers, and unwind allocated memory. `mlx5hws_cmd_forward_tbl_create()` composes multiple commands: create flow table, create flow group, set FTE, then stores IDs for later destruction in reverse order. `mlx5hws_cmd_set_fte()` dynamically sizes its command buffer based on destination format and emits optional packet reformat, crypto, and extended destination data.

Capability querying proceeds through general device caps, general device 2 caps, NIC flow table caps, WQE-based flow table caps when supported, and e-switch caps when the device is an e-switch manager. The resulting caps drive context support checks, definer selection, queue setup, and BWC behavior.

## Dependencies And Integration Points
This layer depends on mlx5 PRM field macros, core command execution, flow destination enums, vport GVMI helpers, and HWS headers that define command attribute structures. It is used by context initialization, table/matcher/action code, action STE pool creation, definer cache allocation, debug queries, and BWC isolated-table setup.

## Risks And Test Signals
Risks are wrong PRM field names or units, missing destroy on partial create, destination-format mismatches when extended destinations are enabled, capability fields queried under the wrong op_mod, and silent destroy failures because several destroy helpers ignore return values. Test signals include firmware command failure injection at every create step, capability matrices with and without WQE-based update/e-switch support, FTEs with vport/TIR/table/sampler destinations, STC modify coverage for each action type, and generated-WQE status error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.h

## Purpose
`cmd.h` defines the data-transfer structures and exported command-wrapper API used by HWS code to interact with mlx5 firmware. It keeps PRM command details out of higher-level context, table, action, matcher, and definer code.

## Important APIs, Types, And Functions
Important structs include FTE destination and attribute records, flow table create/modify/query attributes, flow group attributes, forward-table ownership records, RTC create attributes, alias object attributes, STC create/modify attributes, STE create attributes, definer create attributes, packet reformat create attributes, generated WQE attributes, and the large queried capability record. The STC modify union is the core action command schema and includes IDs, remove/insert header parameters, modify-header IDs, inline modify data, ASO fields, vport fields, STE-table jump fields, remove-words fields, trailer fields, and destination table/TIR IDs.

The API declares all create/modify/destroy/query helpers implemented in `cmd.c`, including `mlx5hws_cmd_query_caps()` and `mlx5hws_cmd_query_gvmi()`.

## Control Flow And State
The header itself stores no runtime state except through caller-owned structs. Many returned firmware IDs become persistent state in higher layers: flow table IDs in tables and forward islands, RTC IDs in matchers/action STE tables, STC/STE object bases in pools, definer IDs in the definer cache, and packet reformat IDs in actions.

## Dependencies And Integration Points
It depends on mlx5 core types, PRM enums, HWS pool chunks, and HWS context declarations. Context initialization consumes capability fields; table/action/definer code constructs these attributes and relies on `cmd.c` to emit firmware commands.

## Risks And Test Signals
Risks are stale or mismatched struct fields relative to firmware PRM definitions, unit confusion for sizes/log sizes/word counts, and missing initialization of boolean flags before command submission. Tests should validate every command attribute through successful create/destroy loops and negative firmware responses, with special attention to STC action unions and capability-dependent paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.c

## Purpose
`context.c` manages HWS context lifetime. It queries capabilities, decides whether HWS/BWC are supported, allocates protection domains and shared pools, opens send queues, starts action STE pools, registers debugfs dumping, initializes vport state, and tears everything down in reverse order.

## Important APIs, Types, And Functions
Public functions are `mlx5hws_context_open()`, `mlx5hws_context_close()`, `mlx5hws_context_set_peer()`, `mlx5hws_context_cap_dynamic_reparse()`, and `mlx5hws_context_get_reparse_mode()`. Internal helpers initialize/uninitialize pools, private PDs, and HWS resources. `hws_context_check_hws_supp()` validates required capabilities: WQE-based insertion, e-switch manager mode, reparse support, 8DW STE format, hash/offset RTC update modes, and select definer support.

## Control Flow And State
Open allocates and initializes the context, creates locks/xarrays, queries caps, initializes vports, initializes HWS if supported, and registers debugfs. HWS initialization allocates a private PD, pattern and definer caches, an FDB STC pool, sets BWC support, opens send queues, starts the per-queue action STE pool, and initializes the table list. If capability checks fail, the context can still be returned without HWS support rather than treating unsupported hardware as an allocation failure.

Close removes debugfs, uninitializes HWS resources only if HWS support was set, uninitializes vports, frees caps, destroys xarrays/locks, and frees the context. Peer contexts are stored by VHCA ID under `ctrl_lock`.

## Dependencies And Integration Points
This file integrates command capability queries, vport setup, core PD allocation, pattern and definer caches, STC and action STE pools, send queues, debugfs, and BWC support. All HWS table/matcher/action paths depend on `struct mlx5hws_context` state initialized here.

## Risks And Test Signals
Risks include partial-init unwind ordering, returning a context without HWS support to callers that assume BWC support, queue-count assumptions in BWC, peer xarray lifetime, and reparse-mode fallback behavior. Test signals include unsupported capability combinations, allocation failures at each init step, open/close stress, peer insertion errors, and verifying delayed action STE cleanup is canceled before pool memory is freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.h

## Purpose
`context.h` defines the central HWS context object and capability flags shared by the steering subsystem.

## Important APIs, Types, And Functions
`enum mlx5hws_context_flags` records HWS support, private PD ownership, BWC support, and native API support. `enum mlx5hws_context_shared_stc_type` indexes shared STC resources. `struct mlx5hws_context_common_res` stores default STCs, shared STCs, and default miss table. `struct mlx5hws_context_debug_info` stores debugfs dentries. `struct mlx5hws_context_vports` stores e-switch manager/uplink GVMI and vport xarray. `struct mlx5hws_context` ties together the mlx5 device, queried caps, PD number, STC pool, action STE pools, delayed cleanup work, caches, control lock, send queues, BWC queue locks, table list, debug data, peers, and vports.

Inline helpers test BWC and native support. Function declarations expose dynamic reparse capability and selected reparse mode.

## Control Flow And State
The context is process/kernel-lifetime state for HWS. Most fields are initialized in `context.c` and then referenced by table, matcher, action, BWC, definer, vport, send, and debug code. `ctrl_lock` is the broad control-plane serialization primitive for context-wide resources and some refcounts.

## Dependencies And Integration Points
The header is included throughout the HWS implementation. It integrates command caps, pools, delayed work, send engine state, debugfs, xarrays, and vport peer mapping.

## Risks And Test Signals
Risks are stale assumptions about which fields exist when `HWS_SUPPORT` is not set, insufficient locking around shared state, and teardown ordering for delayed work and debugfs readers. Tests should validate all public operations reject unsupported contexts and run under lockdep during open/close and debug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.c

## Purpose
`debug.c` exposes an HWS debugfs dump for FDB steering state. It emits CSV-like records describing the context, attributes, capabilities, send engines, STC resources, tables, matchers, templates, definers, and action STE tables.

## Important APIs, Types, And Functions
Public functions are `mlx5hws_debug_init_dump()` and `mlx5hws_debug_uninit_dump()`. `hws_dump_show()` calls `hws_debug_dump()`, which validates inputs and serializes the dump under `ctx->ctrl_lock`. Dump helpers format matcher definers, match templates, action templates, matcher attributes, matcher table/STE IDs, flow table ICM indexes, send queue state, capabilities, context attributes, STC pools, and action STE pools.

## Control Flow And State
Initialization creates `steering/fdb` under the mlx5 debugfs device root and a per-context file named from the context pointer. Reading the file locks the context and walks the current table list, matcher lists, STC pool resources, send queues, and action STE pool lists. It issues flow table query commands to obtain ICM addresses. Uninitialization removes the steering debugfs subtree recursively.

## Dependencies And Integration Points
The file depends on Linux debugfs and seq_file APIs, HWS context/table/matcher/action/definer structures, command flow table query, action type formatting, and pool base ID helpers. Its output format is versioned by `HWS_DEBUG_FORMAT_VERSION` in `debug.h`.

## Risks And Test Signals
Risks include sleeping firmware queries while holding `ctrl_lock`, debug readers racing teardown, only dumping available action STE tables but not full-list tables, pointer-derived IDs that are not stable across runs, and format drift with user-space parsers. Test signals include reading debugfs during active rule insertion/deletion, reading after unsupported-context open, faulting flow table query, and parser compatibility against all emitted resource type IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.h

## Purpose
`debug.h` defines the debug dump format version, stable resource type identifiers, pointer-to-ID helper, ICM-address conversion helper, and debugfs init/uninit declarations for HWS.

## Important APIs, Types, And Functions
`HWS_DEBUG_FORMAT_VERSION` is currently `1.0`. `enum mlx5hws_debug_res_type` assigns numeric IDs for context, context attrs/caps/send engine/send ring/STC, table, matcher, matcher attrs/templates/definers, and action STE tables. `HWS_PTR_TO_ID()` truncates a pointer to a 32-bit-ish printable identifier. `mlx5hws_debug_icm_to_idx()` converts an ICM byte address to an index by shifting by six and masking. `mlx5hws_debug_init_dump()` and `mlx5hws_debug_uninit_dump()` are implemented in `debug.c`.

## Control Flow And State
The header contains no mutable state, but its constants are part of the externally consumed debugfs record schema. Resource type IDs govern how each emitted line is interpreted.

## Dependencies And Integration Points
It depends on HWS context declarations and is included by debug implementation and internal users that need debug identifiers. User-space diagnostics must stay aligned with the version and enum values.

## Risks And Test Signals
Risks include changing enum values without a format-version bump, pointer truncation collisions in large systems, and ICM index assumptions tied to STE granularity. Test signals are debug dump parser tests and comparisons of dumped ICM indexes against firmware query data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.c

## Purpose
`definer.c` converts mlx5 flow match masks into HWS match definer layouts and tag-generation field-copy programs. It understands outer/inner headers, misc parameter blocks, tunnels, flex parsers, registers, MPLS, GTP/Geneve/VXLAN/GRE, packet type fields, and source-port GVMI translation. It also caches firmware definer objects by selector/mask layout.

## Important APIs, Types, And Functions
Public APIs include `mlx5hws_definer_fname_to_str()`, `mlx5hws_definer_create_tag()`, `mlx5hws_definer_get_id()`, `mlx5hws_definer_compare()`, `mlx5hws_definer_calc_layout()`, cache init/uninit, `mlx5hws_definer_get_obj()`, `mlx5hws_definer_free()`, `mlx5hws_definer_mt_init()`, and `mlx5hws_definer_mt_uninit()`. Internal conversion helpers map each match criteria block into `struct mlx5hws_definer_fc` entries, assign tag setters, validate incompatible flags, build a header-layout bitmap, choose selectors recursively, bind field-copy offsets to tag offsets, create tag masks, and allocate/cache firmware definers.

## Control Flow And State
Match-template initialization allocates a full field-copy array, converts enabled criteria blocks into header-layout offsets, validates conflicts, compresses active field copies into `mt->fc`, and fills an `hl` mask. `hws_definer_find_best_match_fit()` first tries normal match selectors; if that fails and jumbo is allowed, it tries jumbo/full-limited selector layouts based on firmware caps. `hws_definer_fc_bind()` maps header-layout byte offsets into final tag offsets selected by the definer. A definer object is then looked up in `ctx->definer_cache`; matching selector and mask layouts are refcounted and moved to the front of the list, otherwise `mlx5hws_cmd_definer_create()` creates a new object.

Tag generation later iterates `mt->fc` and calls each field’s setter to copy or synthesize bits into the hardware tag. Some setters synthesize values, such as VLAN type, L3 type, ICMP words, parser OK bits, or GVMI from source port and peer context.

## Dependencies And Integration Points
This file depends heavily on mlx5 PRM field macros, firmware capabilities, vport GVMI lookup, peer context xarray, command definer create/destroy, match template lifetime, BWC complex detection, and debug dumping of selectors/masks. `bwc_complex.c` also calls `mlx5hws_definer_calc_layout()` with jumbo disabled to determine when masks must be split.

## Risks And Test Signals
Risks include incorrect bit/byte offsets, endian errors in tag setters, unsupported misc blocks returning the wrong error, selector search exponential behavior, conflicts among tunnel/protocol flags, stale definer-cache refcounts, source-port GVMI lookup under wrong peer context, and jumbo-vs-complex decisions that change rule semantics. Test signals include exact tag vectors for every field family, unsupported-field negative cases, jumbo and non-jumbo layout boundaries, complex-split `-E2BIG` behavior, cache reuse/free refcounts, tunnel parser capability matrices, IPv4/IPv6 and VLAN synthesis, and peer-vport source matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.c -->
