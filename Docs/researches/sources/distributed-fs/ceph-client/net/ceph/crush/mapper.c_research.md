# sources/distributed-fs/ceph-client/net/ceph/crush/mapper.c

## Purpose
Implements the core CRUSH placement rule interpreter and bucket-selection algorithms. Given a CRUSH map, rule, input hash value, device weights, and workspace, it deterministically maps objects to OSD/device ids while avoiding out devices and collisions.

## Important APIs, Types, and Functions
Public APIs are `crush_find_rule()`, `crush_init_workspace()`, and `crush_do_rule()`. Bucket algorithms include `bucket_perm_choose()`, `bucket_uniform_choose()`, `bucket_list_choose()`, `bucket_tree_choose()`, `bucket_straw_choose()`, and `bucket_straw2_choose()`. Placement helpers include `crush_bucket_choose()`, `is_out()`, `crush_choose_firstn()`, and `crush_choose_indep()`. Straw2 uses `crush_ln()` and lookup tables from `crush_ln_table.h`. It uses `struct crush_map`, `struct crush_rule`, `struct crush_bucket`, `struct crush_work`, `struct crush_work_bucket`, and optional `struct crush_choose_arg`.

## Control Flow
`crush_find_rule()` scans rules for a ruleset/type/size mask match. `crush_init_workspace()` lays out per-bucket work pointers and permutation arrays inside caller-provided memory; callers must rerun it when map layout changes. `crush_do_rule()` interprets rule steps: TAKE seeds the working set, SET_* steps adjust retry and chooseleaf behavior, CHOOSE/CHOOSELEAF FIRSTN or INDEP expands buckets using the selected algorithm, and EMIT copies working items into the result.

`crush_choose_firstn()` performs depth-first selection for replicas, retrying local bucket choices, fallback permutations, or full descents when items collide or are out. With chooseleaf, it recursively descends to leaves and writes final leaves through `out2`. `crush_choose_indep()` is the positionally stable breadth-first variant, filling undefined slots independently. Bucket selection dispatches by algorithm: uniform uses cached random permutation, list/tree use weight-proportional choices, straw uses straw lengths, and straw2 uses logarithmic draws divided by per-position weights with optional choose args.

## State and Persistence
The mapper is deterministic and owns no global mutable state. Temporary state is in caller-provided workspace and result arrays. `crush_work_bucket` caches permutations per bucket and input `x`. Device out-ness is supplied by the caller's weight vector, with weights below `0x10000` interpreted probabilistically.

## Dependencies and Integration Points
Depends on CRUSH map structures, CRUSH hash functions, fixed-point logarithm tables, and OSD map code that supplies weights, rules, and choose args. Kernel and userspace builds share the same algorithmic source style, so compatibility is critical.

## Risks
Any change affects data placement and can cause large remaps. Workspace sizing/layout must match `map->working_size`; `BUG_ON` catches mismatches. Invalid maps can produce bad bucket ids, empty buckets, unknown algorithms, or unknown hash types; this code often skips or returns fallback items rather than fully validating. Retry parameters strongly influence collision resolution and undersized results. Choose-arg indexing uses `-1 - bucket->id`, so bucket ids must be valid negative ids.

## Test Signals
Use known CRUSH map vectors from userspace Ceph, all bucket algorithms, firstn and indep rules, chooseleaf stable/vary-r modes, local and fallback retries, out-device probabilities, zero-weight devices, empty buckets, choose args with per-position weights and ids, workspace reinitialization after map changes, and result-size truncation.
