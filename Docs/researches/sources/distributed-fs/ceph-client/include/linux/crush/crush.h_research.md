<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/crush.h -->
# sources/distributed-fs/ceph-client/include/linux/crush/crush.h

## Purpose

`crush.h` defines Ceph's CRUSH map data structures, rule language, bucket algorithms, replacement choose-argument structures, map-level tunables, destroy helpers, and mapper workspace layout. The source was read as a complete 360-line file.

## Important APIs, Types, and Functions

Constants include `CRUSH_MAGIC`, maximum depth/rule/device weights, `CRUSH_ITEM_UNDEF`, and `CRUSH_ITEM_NONE`. Rule structures include `crush_rule_step`, `crush_rule_mask`, and `crush_rule`, with opcodes such as `TAKE`, `CHOOSE_FIRSTN`, `CHOOSE_INDEP`, `CHOOSELEAF_*`, `EMIT`, and tunable override steps. Bucket types include uniform, list, tree, straw, and straw2 through `struct crush_bucket` and specialized bucket structs. Replacement data uses `crush_weight_set`, `crush_choose_arg`, and `crush_choose_arg_map`. `struct crush_map` stores bucket/rule arrays, limits, choose tunables, working size, and kernel rbtrees for names/types/choose args. APIs include `crush_bucket_alg_name()`, bucket/rule/map destroy helpers, `crush_get_bucket_item_weight()`, `crush_calc_tree_node()`, `clear_crush_names()`, and `clear_choose_args()`.

## Control Flow

The mapper interprets rules over the immutable map, taking a starting bucket/device, choosing items according to bucket algorithms and weights, descending leaves when requested, and emitting results. Workspace structures store temporary bucket permutations outside the immutable map.

## State and Persistence Behavior

`struct crush_map` is durable in memory as part of Ceph OSD maps and should be treated as immutable by mapping operations. Kernel rbtrees store decoded names and choose args. Workspace is separate per mapping call or reusable per caller and avoids mutating the map.

## Dependencies and Integration Points

In-kernel builds depend on rbtree and Linux types; userspace builds use `crush_compat.h`. It integrates with Ceph OSD map decoding, placement decisions, replicated/erasure-coded object mapping, and CRUSH choose-argument overrides.

## Risks and Edge Cases

Bucket algorithms differ in stability and cost. Tree buckets are legacy and excluded from default allowed legacy algorithms. Fixed-point weights must stay within defined limits. Choose-argument arrays must match bucket counts and straw2 item order. Rule masks and sizes must select the intended rule or placement can change cluster-wide.

## Test Signals

Signals include deterministic CRUSH mapping vectors, map encode/decode round trips, bucket destroy/leak tests, straw2 choose-arg override tests, rule selection tests, failure/out-weight behavior, and comparison with userspace Ceph CRUSH results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/crush.h -->
