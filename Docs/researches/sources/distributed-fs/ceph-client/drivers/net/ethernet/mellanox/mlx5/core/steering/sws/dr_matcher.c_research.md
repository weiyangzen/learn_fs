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
