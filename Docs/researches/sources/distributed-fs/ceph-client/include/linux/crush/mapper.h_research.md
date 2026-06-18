<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/mapper.h -->
# sources/distributed-fs/ceph-client/include/linux/crush/mapper.h

## Purpose

`mapper.h` declares the CRUSH rule lookup and mapping API that maps an input value to output device IDs using a CRUSH map, weights, workspace, and optional choose arguments. The source was read as a complete 34-line file.

## Important APIs, Types, and Functions

APIs include `crush_find_rule()`, `crush_do_rule()`, `crush_work_size()`, and `crush_init_workspace()`. `crush_do_rule()` accepts a map, rule number, input `x`, result buffer and size, weight array and size, caller-provided workspace, and choose-arg overrides.

## Control Flow

Callers find a rule matching ruleset/type/size, allocate or reuse workspace sized by `crush_work_size()`, initialize it, and invoke `crush_do_rule()` to fill the result array. The rule interpreter uses the immutable map and mutable workspace while honoring per-device weights and optional replacement choose args.

## State and Persistence Behavior

The mapper should not mutate the `crush_map`. Workspace is caller-owned transient state and may be stack, heap, or long-lived per-thread storage if reinitialized appropriately.

## Dependencies and Integration Points

It includes `crush.h` and integrates with Ceph OSD map placement, object locator hashing, and CRUSH tunables.

## Risks and Edge Cases

`result_max` must match caller expectations and workspace sizing. Weight arrays must cover `weight_max` devices. Reusing workspace without initialization can leak previous permutations. Invalid rules or undersized result buffers can produce incomplete placement.

## Test Signals

Signals include deterministic placement vectors, workspace size/init tests, invalid rule lookup tests, underweight/out device mapping, choose-arg override tests, and kernel/userspace mapper parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/mapper.h -->
