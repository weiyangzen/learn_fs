# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/memcg_protection.m

## Purpose

`memcg_protection.m` is an Octave model for memory cgroup reclaim protection distribution. It simulates a one-level hierarchy used to justify expected `memory.low`/`memory.min` values in `test_memcontrol.c`. The complete 89-line script was read.

## Important APIs, Types, and Functions

The script defines inputs `E`, `n`, and `c` for parent effective protection, sibling nominal protection, and current consumption. It models reclaim with `cluster`, `alpha`, `epsilon`, and `timeout`, and records histories in `ch`, `eh`, and `rh`.

## Control Flow

For each iteration, it computes low usage, sibling protected share, effective protection normalized for overcommit, recursive unclaimed protection for overuse, reclaim pressure, protection-adjusted scan rate, cluster rounding, and updated consumption. It exits when reclaim drops below `epsilon` or when `timeout` is reached.

## State and Persistence Behavior

All state is in-memory Octave vectors. It prints final `t`, `c`, and `e` values but does not write files.

## Dependencies and Integration Points

It depends on `octave-cli` and the memory protection algorithm mirrored by Linux memory cgroup reclaim. Its expected output informs the comments and tolerance checks in `test_memcg_protection()`.

## Risks and Edge Cases

The model intentionally simplifies reclaim: all memory is reclaimable, only non-low reclaim is simulated, `memory.min` is zero, and sibling reclaim is parallel even though kernel reclaim is serialized. It is explanatory rather than a direct oracle for all kernels.

## Test Signals

Running `octave-cli memcg_protection.m` should converge near the usage values asserted by `test_memcontrol.c`, especially the 29M/21M/0M protected sibling behavior.
