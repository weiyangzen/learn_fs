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
