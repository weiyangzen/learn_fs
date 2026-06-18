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
