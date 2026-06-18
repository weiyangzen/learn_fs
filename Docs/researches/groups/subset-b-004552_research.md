# Research: subset-b-004552

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.c

## Purpose
This file implements the software-steering STE context for steering format v1. It converts high-level direct-rule match/action objects into 64-byte hardware STE records, action words, lookup type identifiers, byte masks, and modify-header pattern/argument objects. The file ends by publishing `ste_ctx_v1`, a `struct mlx5dr_ste_ctx` function table consumed by the generic STE/rule/action code.

## Important APIs, Types, And Functions
The exported entry point is `mlx5dr_ste_get_ctx_v1()`, which returns `ste_ctx_v1`. That context wires v1 implementations into generic operations for STE initialization, miss/hit address programming, byte-mask handling, RX/TX action assembly, action encoding, modify-header chunk allocation, and pre-send formatting.

Core STE field helpers include `dr_ste_v1_init()`, `dr_ste_v1_set_miss_addr()`, `dr_ste_v1_get_miss_addr()`, `dr_ste_v1_set_hit_addr()`, `dr_ste_v1_set_next_lu_type()`, `dr_ste_v1_get_next_lu_type()`, `dr_ste_v1_set_byte_mask()`, and `dr_ste_v1_prepare_for_postsend()`. Address helpers encode ICM addresses as shifted indices; hit addresses use `icm_addr >> 5` plus hash table size, while miss addresses use `miss_addr >> 6`.

Action encoders include VLAN push/pop, encapsulation, L3 encapsulation, RX decapsulation, insert/remove header, flow tag, counter, ASO flow meter, modify-list, accelerated modify-list, set/add/copy modify actions, and special L3 decap action-list construction. `dr_ste_v1_set_actions_tx()` and `dr_ste_v1_set_actions_rx()` are the control points that lay out action words across one or more STEs.

Match builders are numerous and follow the same pattern: build a bit mask from a mask `mlx5dr_match_param`, select the v1 lookup type, compute the byte mask with `mlx5dr_ste_conv_bit_to_byte_mask()`, and install a tag-building callback. Builders cover L2 source/destination, IPv4/IPv6 5-tuple pieces, tunnel L2, GRE, MPLS, MPLS-over-UDP/GRE flex parsers, ICMP, metadata registers, source GVMI/QPN, Geneve, VXLAN-GPE, GTP-U, programmable flex parsers, and tunnel header words.

## Control Flow
For normal rule construction, generic code selects builder functions through `ste_ctx_v1`, calls each builder init with a mask, and later calls the stored `ste_build_tag_func()` with a rule value. Many tag builders intentionally zero fields they consume from the input `mlx5dr_match_param`; this is a consumed-field accounting convention used elsewhere to detect unsupported or unconsumed match bits.

TX action assembly starts with a double-action capacity in the original STE. It may append additional MATCH STEs with `dr_ste_v1_arr_init_next_match()` when a requested action does not fit or when capability/order rules require separation. TX ordering is pop VLAN, modify header, push VLAN, encap/insert/remove, ASO flow meter, range, counter. RX ordering handles decap first, then tag, pop VLAN, modify header, push VLAN, counter, encap/insert/remove, ASO, and range. The final STE gets the hit GVMI and final hit ICM address.

Range matching is special: `DR_ACTION_TYP_RANGE` always appends a `DR_STE_V1_TYPE_MATCH_RANGES` STE, programs the range miss address, and encodes packet length min/max using the range definer. Range STEs do not carry normal actions.

## State And Persistence
The file does not persist Linux state directly; it mutates caller-owned byte buffers that are later posted to ICM hardware memory. It also allocates and releases modify-header pattern and argument objects through domain managers in `dr_ste_v1_alloc_modify_hdr_ptrn_arg()` and `dr_ste_v1_free_modify_hdr_ptrn_arg()`. Runtime persistence is therefore in device ICM, modify action objects, cached pattern objects, and argument objects referenced by `struct mlx5dr_action_rewrite`.

## Dependencies And Integration Points
The code depends on `mlx5_ifc_dr_ste_v1.h` hardware layout definitions, `dr_ste_v1.h` constants, generic `dr_types.h` structures, `MLX5_SET`/`MLX5_GET` accessors, `mlx5dr_ste_conv_bit_to_byte_mask()`, `mlx5dr_domain_get_vport_cap()`, flex-parser capability fields, and pattern/argument managers. It integrates with `dr_ste.c` through the `mlx5dr_ste_ctx` dispatch table and with action creation through modify-field conversion arrays.

## Risks
Risks are mostly hardware ABI risks: a wrong field code, shift, lookup type, or byte mask can silently steer traffic incorrectly. RX/TX action ordering is fragile because some actions must be split across STEs. `prepare_for_postsend()` swaps tag and mask for full STEs; the range STE workaround deliberately writes min/max in locations that survive that generic swapping path. Builders mutate match parameters, so callers must pass scratch copies, not shared immutable masks. Source GVMI/QPN matching depends on peer-domain xarray state and vport capability lookup, returning `-EINVAL` when unavailable.

## Test Signals
Useful tests include compile coverage for all `MLX5_SET` fields, rule creation with combinations of VLAN pop/push, modify header, decap/encap, counters, ASO meters, and range matching, plus traffic tests for inner/outer IPv4/IPv6, tunnel protocols, metadata registers, and peer vport source matching. Negative tests should verify invalid IP version, invalid peer GVMI, unavailable vport caps, undersized L3 decap action buffers, and missing pattern/argument managers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.h

## Purpose
This header defines the public v1 STE constants and function prototypes used by v1, v2, and v3 STE contexts. It names v1 entry formats, lookup types, header anchors, action sizes, action IDs, modify-header hardware field codes, and ASO context types.

## Important APIs, Types, And Functions
Important constants include `DR_STE_DECAP_L3_ACTION_NUM`, `DR_STE_L2_HDR_MAX_SZ`, `DR_STE_CALC_DFNR_TYPE()`, `DR_STE_V1_TYPE_*`, `DR_STE_V1_LU_TYPE_*`, `DR_STE_HEADER_ANCHOR_*`, `DR_STE_ACTION_*_SZ`, `DR_STE_V1_ACTION_ID_*`, and v1 modify field offsets. Function prototypes expose all v1 STE utilities, action encoders, match-builder init routines, and modify-header pattern/argument allocation helpers.

## Control Flow
The header itself has no runtime flow, but it defines the dispatch surface for `ste_ctx_v1` and reused v1 behavior in v2/v3. The lookup type constants are combined by `DR_STE_CALC_DFNR_TYPE()` to choose inner or outer definer types during builder initialization.

## State And Persistence
No state is stored here. The values are part of the driver/hardware ABI and must remain synchronized with the STE layout headers and firmware-supported steering format.

## Dependencies And Integration Points
It includes `dr_types.h` and `dr_ste.h`, so all prototypes are expressed in generic direct-rule types such as `mlx5dr_ste_ctx`, `mlx5dr_domain`, `mlx5dr_ste_build`, `mlx5dr_match_param`, and `mlx5dr_action`. It is included by `dr_ste_v1.c`, `dr_ste_v2.c`, and `dr_ste_v3.c`.

## Risks
Changing numeric constants breaks hardware encoding. The header is reused by newer contexts, so v1-looking constants such as action IDs and anchors are not v1-only in practice. Prototype changes can cascade through v2/v3 because they intentionally call v1 implementations.

## Test Signals
Build tests should compile all STE versions. Runtime tests should cover every action ID and lookup type that has a public builder or encoder, especially fields reused by v2/v3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.c

## Purpose
This file defines the steering format v2 context by reusing almost all v1 builders, setters, and action assembly while substituting the v2 modify-header field mapping and a slightly different action capability mask.

## Important APIs, Types, And Functions
The only exported function is `mlx5dr_ste_get_ctx_v2()`. It returns a static `mlx5dr_ste_ctx` whose builder and getter/setter pointers mostly target `dr_ste_v1_*` functions. The context uses `dr_ste_v2_action_modify_field_arr` from `dr_ste_v2.h`.

## Control Flow
Generic STE code selects this context when the domain reports steering format v2. From that point, rule building, tag building, miss/hit address programming, action packing, and pre-send preparation run through the inherited v1 implementations. Modify-header software fields are translated through the v2 field array.

## State And Persistence
The file owns only the static function table. Persistent state is in the domain, STE buffers, ICM chunks, and modify-header objects allocated by the inherited helpers.

## Dependencies And Integration Points
It includes `dr_ste_v1.h` for all shared behavior and `dr_ste_v2.h` for v2 hardware field-code definitions. It is selected indirectly by `mlx5dr_ste_get_ctx()` in the generic STE layer.

## Risks
The intentional inheritance means any behavioral change in v1 action ordering or builder mutation also affects v2. The context drops `DR_STE_CTX_ACTION_CAP_POP_MDFY` compared with v1, so tests must ensure pop-VLAN plus modify-header splitting remains correct on v2 devices. A stale v2 modify-field array would corrupt modify-header actions even if matching still works.

## Test Signals
Test modify-header actions touching metadata register C fields, because v2 changes those field codes. Also test mixed pop/modify actions to verify action-cap splitting and traffic tests for representative v1-inherited builders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.h

## Purpose
This header defines the v2 modify-header hardware field codes and the mapping from software `MLX5_ACTION_IN_FIELD_*` selectors to those codes, bit starts/ends, and L3/L4 type restrictions.

## Important APIs, Types, And Functions
The central artifact is `dr_ste_v2_action_modify_field_arr[]`, a `static const struct mlx5dr_ste_action_modify_field` indexed by `MLX5_ACTION_IN_FIELD_*`. It covers L2 source/destination MAC, ethertype, DSCP, TCP/UDP ports, TCP flags, TTL/hop limit, IPv4/IPv6 addresses, metadata registers A/B/C, TCP sequence/ack, first VLAN ID, and EMD fields.

## Control Flow
There is no executable control flow. `dr_ste_v2.c` installs this array into `ste_ctx_v2`, and generic modify-header conversion code indexes it when compiling user-requested set/add/copy operations.

## State And Persistence
No runtime state is stored. The array is read-only driver data that must match the v2 hardware steering format.

## Dependencies And Integration Points
The array type comes from `dr_types.h` through the include chain in users. It is consumed by `dr_ste_v2.c` and v3 also reuses this array for modify-header field conversion.

## Risks
The v2 register C field codes differ from v1; copy/paste mistakes here would specifically break metadata register modifications. Because this is a header with a `static const` array, every including C file gets its own internal copy, which is intentional but worth remembering for size and linkage.

## Test Signals
Tests should exercise all supported modify-header fields, especially metadata register C0-C5 and EMD fields. Compile tests should catch missing enum definitions from include-chain changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v3.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v3.c

## Purpose
This file defines the steering format v3 context. It reuses v1 builders and most generic action assembly, uses v2 modify-header field codes, and overrides packet-reformat/VLAN action encoders whose bit layouts changed in v3.

## Important APIs, Types, And Functions
The exported entry point is `mlx5dr_ste_get_ctx_v3()`. V3-specific setters include `dr_ste_v3_set_encap()`, `dr_ste_v3_set_push_vlan()`, `dr_ste_v3_set_pop_vlan()`, `dr_ste_v3_set_encap_l3()`, `dr_ste_v3_set_rx_decap()`, `dr_ste_v3_set_insert_hdr()`, `dr_ste_v3_set_remove_hdr()`, and `dr_ste_v3_set_action_decap_l3_list()`.

## Control Flow
Generic code selects `ste_ctx_v3` by steering format version. Match building still calls v1 builder functions. RX/TX action assembly still calls the v1 packers, but those packers dispatch through the context for encap, VLAN, decap, insert, and remove actions, so the v3 bitfield setters are used at the actual action-write points.

## State And Persistence
The file only owns a static function table and writes caller-provided action buffers. Persistent effects occur when the generic send path posts those buffers to hardware ICM/action memory.

## Dependencies And Integration Points
It includes `dr_ste_v1.h` for shared action IDs, anchors, sizes, builders, and v1 helpers, and `dr_ste_v2.h` for modify-field mappings. It depends on v3 layout structures defined in `mlx5_ifc_dr.h` for action bitfields.

## Risks
The v3 context is a hybrid: v1 matching plus v3 action layouts plus v2 modify fields. A reviewer must verify all three ABI families when changing it. The L3 decap inline-list algorithm mirrors v1 but uses v3 structures; any future change to padding or inline data width must update both. As with v2, `DR_STE_CTX_ACTION_CAP_POP_MDFY` is not advertised.

## Test Signals
Traffic tests should emphasize packet reformat operations on v3 hardware: L2-to-tunnel, L3 tunnel, insert/remove header, VLAN push/pop, and decap-L3 action-list creation. Modify-header tests should match v2 expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_table.c

## Purpose
This file implements direct-rule flow table lifecycle and miss-action wiring. It creates software-owned hardware flow tables rooted at STE hash-table anchors, initializes RX/TX/FDB table state, and exposes table IDs back to the flow steering layer.

## Important APIs, Types, And Functions
Public functions are `mlx5dr_table_create()`, `mlx5dr_table_destroy()`, `mlx5dr_table_set_miss_action()`, `mlx5dr_table_get_id()`, and `mlx5dr_table_get_from_fs_ft()`. Internal helpers initialize/uninitialize NIC RX/TX anchors, FDB pairs, create/destroy the firmware flow table, and update miss paths.

## Control Flow
Table creation increments the domain refcount, allocates `struct mlx5dr_table`, initializes per-domain-type anchors under the domain lock, creates a firmware flow table with `sw_owner = true`, records debug state, and returns the table. RX/TX tables get one anchor; FDB tables get both RX and TX anchors. Creation passes the anchor ICM addresses to firmware as roots.

Miss-action setting validates that only destination-table actions are accepted, locks the domain, updates RX and/or TX miss chains depending on domain type, swaps the table's stored miss action, and adjusts action refcounts. The NIC miss update finds the last matcher anchor if matchers exist, otherwise the table start anchor, then posts a miss connection with `mlx5dr_ste_htbl_init_and_postsend()`.

Table destruction refuses to run with outstanding table references, removes debug state, destroys the firmware table, releases anchors, drops any miss action reference, decrements the domain refcount, and frees memory.

## State And Persistence
State is held in `struct mlx5dr_table`: level, flags, table type/id, RX/TX anchors, matcher lists, miss action, refcount, and debug node. Hardware-visible persistence is the firmware flow table and ICM-rooted STE anchors. Refcounts protect domain, table, hash-table, and action lifetimes.

## Dependencies And Integration Points
The file depends on `dr_types.h` for all structures and internal APIs. It calls ICM hash-table allocation/free, STE postsend initialization, firmware flow-table create/destroy commands, and debug table registration. `fs_dr.c` uses these APIs as the flow steering backend.

## Risks
Miss-action updates partially program RX then TX for FDB; a failure after one side may leave hardware state changed before returning an error. Refcount checks protect against destroying active tables but rely on all action/rule users to hold references correctly. Anchor initialization and firmware table creation must unwind in the right order to avoid leaked ICM chunks.

## Test Signals
Tests should create/destroy NIC RX, NIC TX, and FDB tables, set and clear miss actions, chain tables through miss actions, and verify refcount busy failures. Error-injection tests around anchor postsend and firmware create/destroy paths would exercise unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_types.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_types.h

## Purpose
This header is the central private contract for the mlx5 software-steering direct-rule subsystem. It defines core constants, match structures, domain/table/matcher/rule/action state, ICM chunk abstractions, send-ring support types, command wrappers, and internal helper prototypes.

## Important APIs, Types, And Functions
Key constants include STE sizes, action limits, ICM chunk sizes, ICM memory types, match criteria bits, action type enum values, action capability bits, and flex-parser bounds. Inline helpers cover flex parser family checks, hash-table refcounting, domain RX/TX locking, chunk size conversions, and table growth thresholds.

Important structures include `mlx5dr_ste`, `mlx5dr_ste_htbl`, `mlx5dr_ste_build`, `mlx5dr_ste_actions_attr`, `mlx5dr_match_param` and its `outer`, `inner`, `misc*` substructures, `mlx5dr_cmd_caps`, `mlx5dr_domain`, `mlx5dr_table`, `mlx5dr_matcher`, `mlx5dr_action`, `mlx5dr_rule`, `mlx5dr_icm_chunk`, send-ring QP/CQ/MR types, and firmware command information structures.

The file also declares most internal subsystem APIs: STE building, action compilation, rule helpers, ICM pool management, command wrappers, send-ring posting, flow-table helper creation, pattern/argument managers, and firmware checksum recalculation helpers.

## Control Flow
There is little executable code, but the type graph describes subsystem flow. Domains own capabilities, ICM pools, send rings, caches, and STE context. Tables own RX/TX anchors and matcher lists. Matchers own builder arrays derived from masks. Rules point to RX/TX last STEs and hold action memberships. Actions carry a discriminated union based on `enum mlx5dr_action_type`. ICM chunks bind software arrays, hardware STE byte arrays, and miss lists.

## State And Persistence
This header defines the persistent in-memory state for software steering. Long-lived objects are refcounted domains, tables, matchers, actions, STE hash tables, pattern objects, and rewrite argument objects. Hardware persistence is represented by ICM chunks, firmware flow table IDs, modify-header object IDs, reformat IDs, sampler IDs, and command-created resources. Locks are per RX/TX NIC domain, and `mlx5dr_domain_lock()` always locks RX then TX and unlocks in reverse.

## Dependencies And Integration Points
It includes kernel mlx5/vport, refcount, flow steering core, work queue, mlx5 library, hardware IFC direct-rule layouts, public `mlx5dr.h`, and debug definitions. It is included widely by SW steering C files, making it the shared ABI between domain, table, matcher, rule, action, STE, command, ICM, and send modules.

## Risks
This file is high blast-radius. Structure layout changes affect many compilation units. Match parameter fields are consumed/mutated by builders, so semantic mistakes can appear as unsupported leftover fields or missed matches. Lock ordering is encoded in inline helpers and must remain consistent. Refcount fields are plain in several internal objects, so lifetime discipline depends on callers. Capability flags gate hardware features such as SW owner, flex parsers, ranges, and pattern arguments; stale capability interpretation can create invalid STEs.

## Test Signals
Broad build coverage is essential. Runtime signals include domain create/destroy, all table types, matcher builder selection for every match criteria bit, rule insertion/removal with all action types, hash-table growth/collision behavior, ICM allocation/free, send-ring posts, and capability-dependent paths such as match ranges, Geneve TLV, GTP-U flex parsers, and modify-header pattern arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.c

## Purpose
This file adapts the generic mlx5 flow steering command interface to the software-steering direct-rule backend. It implements a `struct mlx5_flow_cmds` table whose operations create DR domains, tables, matchers, rules, packet reformats, modify headers, and peer relationships while delegating firmware-terminal tables back to the firmware command backend.

## Important APIs, Types, And Functions
The exported functions are `mlx5_fs_cmd_get_dr_cmds()`, `mlx5_fs_dr_is_supported()`, and `mlx5_fs_dr_action_get_pkt_reformat_id()`. The static command methods implement namespace create/destroy, table create/destroy/modify, group create/destroy, FTE create/update/delete, packet reformat alloc/free, modify header alloc/free, peer setup, root FT update, and capability reporting.

`mlx5_cmd_dr_create_fte()` is the main translation function. It converts a flow steering `fs_fte` into ordered `mlx5dr_action` arrays, creates terminal destination actions, handles special multi-destination tables, creates counters/tags/ASO actions, and calls `mlx5dr_rule_create()`.

## Control Flow
Table/group creation maps flow tables to `mlx5dr_table_create()` and groups to `mlx5dr_matcher_create()`. Rule creation builds ordered actions because SW steering supports constrained action ordering: decap/pop/modify on RX and modify/push/encap on TX. Packet reformat can be delayed so encapsulation happens after VLAN push/modify ordering. Terminal destinations are accumulated separately, then appended directly when single or wrapped in a multi-destination table action when multiple.

Update FTE creates a replacement rule first, then deletes the old rule. Delete FTE destroys the DR rule and then frees fs_dr-owned actions in reverse order. Table miss-action changes create a destination-table action for the next table and install it through `mlx5dr_table_set_miss_action()`.

## State And Persistence
DR-owned pointers are stored inside existing FS objects: namespace `fs_dr_domain`, flow table `fs_dr_table`, group `fs_dr_matcher`, FTE `fs_dr_rule`, packet reformat `fs_dr_action`, and modify header `fs_dr_action`. The adapter tracks only actions it created itself in `mlx5_fs_dr_rule.dr_actions`, so externally allocated packet reformat and modify header actions remain owned by their resource objects.

## Dependencies And Integration Points
It depends on flow steering core types, firmware command backend helpers, `mlx5dr.h` public APIs, `fs_dr.h` wrapper structs, and private `dr_types.h` for error logging and action internals. It is selected by `fs_core.c` when DR support is available and falls back to firmware commands for terminal tables and unsupported operations.

## Risks
Ownership is subtle: some actions are per-rule temporary and must be destroyed on failure/delete, while packet reformat and modify-header actions are resource-owned and must not be destroyed by rule cleanup. The hard action limit is 34, sized for 32 destinations plus extras. The function mutates `fte->act_dests.action.action` to drop packet reformat when a vport destination embeds a reformat ID. Update creates new then deletes old, so duplicate-rule or resource pressure behavior matters.

## Test Signals
Tests should cover rule creation failures at each allocation point, mixed action ordering, single and multi-destination rules, FW-owned reformat rejection, vport reformat handling, counters, flow tags, ASO flow meter, range destination, table miss chaining, update rollback, delete cleanup, terminal-table fallback, and capability bits for VLAN push/pop and match ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.h

## Purpose
This header declares the flow-steering-to-direct-rule bridge state embedded in generic FS objects and exposes the DR command table accessor when software steering is enabled.

## Important APIs, Types, And Functions
Wrapper structures are `mlx5_fs_dr_action`, `mlx5_fs_dr_rule`, `mlx5_fs_dr_domain`, `mlx5_fs_dr_matcher`, and `mlx5_fs_dr_table`. Public declarations under `CONFIG_MLX5_SW_STEERING` are `mlx5_fs_dr_is_supported()`, `mlx5_fs_dr_action_get_pkt_reformat_id()`, and `mlx5_fs_cmd_get_dr_cmds()`. The disabled-config stubs return unsupported/null values.

## Control Flow
No runtime flow is implemented here. Compile-time flow depends on `CONFIG_MLX5_SW_STEERING`: enabled builds use `fs_dr.c`; disabled builds compile stub functions so generic flow steering can call the accessors safely.

## State And Persistence
The wrapper structs persist DR pointers inside generic FS resources. `mlx5_fs_dr_rule` also stores an array of fs_dr-created actions and a count for reverse-order cleanup on delete.

## Dependencies And Integration Points
It includes public `mlx5dr.h` and forward-declares flow root namespace and FTE types. It is included by the flow steering core and by `fs_dr.c`.

## Risks
Incorrect ownership assumptions around `mlx5_fs_dr_rule.dr_actions` can leak or double-free DR actions. The stubs must continue to match enabled prototypes or disabled builds fail.

## Test Signals
Build both enabled and disabled `CONFIG_MLX5_SW_STEERING` configurations. Runtime tests should verify packet reformat ID retrieval and rule action cleanup through the stored wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr.h

## Purpose
This header declares hardware interface bit layouts for direct-rule STE tags, legacy STE formats, modify-header actions, ASO flow-meter actions, and v3 packet-reformat action layouts. These structures are used by `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF` macros, not as normal C data structures.

## Important APIs, Types, And Functions
It defines `MLX5DR_STE_LU_TYPE_DONT_CARE` and many `mlx5_ifc_ste_*_bits` structures for general STE control, SX transmit, RX steering multicast, packet modify STEs, L2/L3/L4 tags, IPv6 addresses, tunnel tags, MPLS, metadata registers, GRE, flex parsers, tunnel headers, general purpose lookup, source GVMI/QP, L2 headers, set/copy modify actions, ASO flow meters, and v3 insert/remove action formats.

## Control Flow
There is no executable flow. The field names are referenced by STE builders and action setters. For example, v1 builders set tag fields such as `ste_eth_l2_tnl_v1`, while v3 action setters use `ste_double_action_insert_with_ptr_v3` and related structures from this header.

## State And Persistence
No runtime state is stored. The definitions describe byte/bit positions in hardware command or STE buffers that are later posted to device memory.

## Dependencies And Integration Points
This header is included through `dr_types.h` and directly/indirectly by STE code. It must stay synchronized with firmware PRM definitions and with the action/match builders in `dr_ste_v*.c`.

## Risks
Field names and widths are hardware ABI. A single width or ordering mistake changes how `MLX5_SET` packs bytes and can cause traffic missteering. Some structures are older direct-rule layouts while v1-specific layouts live in `mlx5_ifc_dr_ste_v1.h`, so callers must use the correct family.

## Test Signals
Compile tests catch missing field names; only hardware/traffic tests catch most semantic layout mistakes. Exercise L2/L3/L4, tunnel, flex parser, ASO, and v3 reformat actions on devices that support the corresponding steering formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr_ste_v1.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr_ste_v1.h

## Purpose
This header declares steering format v1 hardware bit layouts for single/double actions, v1 STE control formats, match range STEs, and v1 tag layouts. It is the direct layout companion for `dr_ste_v1.c`.

## Important APIs, Types, And Functions
Important definitions include `MLX5_MODIFY_HEADER_V1_QW_OFFSET`, v1 action layouts for flow tag, modify list, remove header, remove-by-size, copy, set, add, insert inline, insert pointer, accelerated modify action list, and v1 STE layouts `ste_match_bwc_v1`, `ste_mask_and_match_v1`, and `ste_match_ranges_v1`.

Tag layouts cover v1 L2 source/destination/source-destination, IPv4 5-tuple, L2 tunnel, IPv4 misc, L4, L4 misc, MPLS, GRE, source GVMI/QP, and ICMP fields.

## Control Flow
There is no executable flow. `dr_ste_v1.c` uses these names in `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF` calls to encode match tags, masks, actions, hit/miss addresses, range min/max values, and reparse/counter state.

## State And Persistence
No state is stored in the header. It defines the binary contract for the hardware buffers that become persistent in ICM when posted.

## Dependencies And Integration Points
It is included by `dr_ste_v1.c`. V2 reuses v1 functions for many operations, so these v1 layouts also indirectly affect v2 for the shared action/match parts that did not change.

## Risks
The v1 action layouts have small fields and non-byte-aligned anchors/offsets. Mistakes in reserved-field placement or field width break all generated hardware STEs. `MLX5_MODIFY_HEADER_V1_QW_OFFSET` is applied by modify-action setters; changing it would shift all modify-header fields.

## Test Signals
Run traffic tests for all v1 match builders and action encoders, plus modify-header set/add/copy and match-range packet length. Compile tests should include v1, v2, and v3 users because v2/v3 reuse v1 functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5_ifc_dr_ste_v1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5dr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5dr.h

## Purpose
This is the public software-steering direct-rule API header. It exposes opaque domain/table/matcher/rule/action types, lifecycle functions, action constructors, support checks, sync flags, reformat types, match parameter wrapper, destination wrapper, and buddy allocator APIs.

## Important APIs, Types, And Functions
Public domain and object APIs include `mlx5dr_domain_create/destroy/set_peer`, `mlx5dr_table_create/destroy/get_id/get_from_fs_ft/set_miss_action`, `mlx5dr_matcher_create/destroy`, `mlx5dr_rule_create/destroy`, and `mlx5dr_action_destroy`.

Action constructors cover destination table/table number/FW table/vport, multi-destination table, drop, tag, sampler, counter, packet reformat, modify header, pop/push VLAN, ASO, and match-range destination. `mlx5dr_action_get_pkt_reformat_id()` exposes reformat IDs. `mlx5dr_is_supported()` gates support on RoCE and SW-owner capabilities, with a steering-format limit for SW owner v2.

The buddy allocator API declares init/cleanup/alloc/free for ICM memory management.

## Control Flow
Consumers such as `fs_dr.c` create a domain, create tables and matchers, create actions, then create rules that bind values and actions. Destroy calls unwind in reverse. Support checking happens before selecting the DR command backend.

## State And Persistence
The header hides object internals behind forward declarations. Persistent state lives in the private `dr_types.h` structures and hardware resources allocated by the implementation. Match parameters are passed as device-spec buffers through `struct mlx5dr_match_parameters`.

## Dependencies And Integration Points
It is included by `fs_dr.h`, private DR modules, and generic flow steering code. It intentionally provides a smaller API than `dr_types.h`, keeping internals private except for the buddy allocator structure needed by ICM code.

## Risks
This is an API boundary: prototype or enum changes affect all callers. The inline `mlx5dr_is_supported()` depends on current device capability semantics; overly broad support would select SW steering on unsupported hardware, while overly narrow support would disable valid devices.

## Test Signals
Build tests for public callers, DR-enabled namespace creation through FS, support-check tests across capability combinations, and lifecycle tests for every public object/action constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5dr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/transobj.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/transobj.c

## Purpose
This file wraps mlx5 firmware commands for transport-domain and transport object lifecycle, and implements hairpin queue pairing between a function device and peer device. It is a general mlx5 core support file used by Ethernet/RDMA paths, not specific to SW steering.

## Important APIs, Types, And Functions
Exported transport command wrappers include allocation/deallocation of transport domains, create/modify/destroy/query RQ, create/modify/destroy/query SQ, query SQ state, create/modify/destroy TIR, create/modify/destroy TIS, create/modify/destroy RQT. Hairpin APIs are `mlx5_core_hairpin_create()`, `mlx5_core_hairpin_destroy()`, and `mlx5_core_hairpin_clear_dead_peer()`.

Internal hairpin helpers create RQs on the function device and SQs on the peer, transition SQs/RQs from reset to ready with peer VHCA and queue numbers, undo transitions on failures, and destroy queues.

## Control Flow
The simple wrappers set the opcode and object number fields, execute the corresponding command, and return object IDs from output buffers. `mlx5_core_query_sq_state()` allocates a query buffer, calls SQ query, reads the state from SQ context, and frees the buffer.

Hairpin creation allocates one object containing arrays of RQNs and SQNs, creates all function RQs, creates all peer SQs, pairs peer SQs first, then function RQs. On failures it rolls back modified queues and destroys created queues. Destroy unpairs, destroys queues, and frees memory. Dead-peer cleanup unpairs/destroys peer SQs and marks `peer_gone` so later destroy skips peer SQ destruction.

## State And Persistence
Firmware object IDs persist in device hardware until destroyed: transport domain numbers, RQNs, SQNs, TIRNs, TISNs, and RQTNs. Hairpin state persists in `struct mlx5_hairpin`, which stores devices, channel count, dynamic RQN/SQN arrays, and `peer_gone`.

## Dependencies And Integration Points
The file depends on `linux/mlx5/driver.h`, `linux/mlx5/transobj.h`, command layout macros, and `mlx5_cmd_exec*` helpers. Ethernet TC hairpin code calls `mlx5_core_hairpin_create()`, and other core/driver paths call the exported transport object wrappers.

## Risks
Most destroy functions ignore firmware command errors, which is common for cleanup but can hide leaks. Hairpin rollback must exactly mirror the create/pair order; a missed reset can leave queues ready against stale peers. Dead-peer handling must avoid sending destroy commands to a gone peer while still cleaning function-side resources later.

## Test Signals
Tests should cover command wrapper success/failure, SQ state query allocation failure, hairpin create failure during RQ creation, SQ creation, SQ pairing, and RQ pairing, plus dead-peer cleanup followed by normal destroy. Device integration tests should verify traffic through hairpin queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/transobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/uar.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/uar.c

## Purpose
This file manages mlx5 user access region pages and BlueFlame register allocation. It allocates UARs from firmware, maps them with regular or write-combining IO mappings, partitions each UAR page into regular and fast-path BFREG slots, and refcounts pages until all users release them.

## Important APIs, Types, And Functions
Core internal helpers are `mlx5_cmd_alloc_uar()`, `mlx5_cmd_free_uar()`, `uars_per_sys_page()`, `uar2pfn()`, `alloc_uars_page()`, `map_offset()`, `alloc_bfreg()`, and `addr_to_dbi_in_syspage()`. Exported APIs are `mlx5_get_uars_page()`, `mlx5_put_uars_page()`, `mlx5_alloc_bfreg()`, and `mlx5_free_bfreg()`.

## Control Flow
`alloc_uars_page()` allocates page metadata and bitmaps, initializes regular and fast-path slot availability, allocates a UAR index through firmware, maps the BAR page either write-combining or normal, initializes the kref, and returns the page. `mlx5_get_uars_page()` reuses or creates a regular mapped UAR page under the regular-list lock.

`alloc_bfreg()` selects the WC or regular list, creates a UAR page if needed, grabs a page reference, selects either the fast-path or regular bitmap, clears the first available bit, updates availability, removes the page from the free list when that slot class is exhausted, and returns the mapped BFREG pointer and index. `mlx5_alloc_bfreg()` falls back from WC to non-WC mapping on `-EAGAIN`. Freeing computes the slot index from the mapped address, restores the bit, re-adds the page when availability transitions from zero to one, and drops the kref.

## State And Persistence
Persistent driver state is in `mdev->priv.bfregs` lists and locks, `struct mlx5_uars_page` objects, bitmaps, availability counters, krefs, firmware UAR indexes, and IO mappings. The release callback removes the page from its list, unmaps IO memory, deallocates the firmware UAR, frees bitmaps, and frees metadata.

## Dependencies And Integration Points
The file depends on mlx5 core command macros, BAR address state, device capabilities `uar_4k`, `num_of_uars_per_page`, and `log_bf_reg_size`, kernel bitmap/list/kref/mutex APIs, and IO mapping helpers. Core device initialization and send-queue paths allocate BFREGs through these APIs.

## Risks
The allocator assumes an available bit exists in a listed page; bitmap/list accounting bugs can produce out-of-range slots. Pointer arithmetic in `addr_to_dbi_in_syspage()` depends on map addresses being within the UAR page and on BFREG size capability. WC mapping fallback changes performance characteristics. The release callback runs under list locks and calls firmware deallocation, so lock ordering must remain stable.

## Test Signals
Tests should allocate/free regular and fast-path BFREGs, exercise WC mapping failure fallback, exhaust a page to force list removal, free a slot to force list re-addition, and run repeated get/put UAR page refcount cycles. Device tests should verify doorbell writes through returned BFREG mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/uar.c -->
