
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_acl_drops.sh`

## Purpose
Tests mlxsw devlink trap accounting for packets dropped by ingress and egress tc flower ACL actions.

## Important APIs, Types, And Functions
- Topology helpers create a bridge with two switch ports and clsact on both ports.
- `ingress_flow_action_drop_test()` installs ingress drop on `swp1` and egress pass counter on `swp2`.
- `egress_flow_action_drop_test()` installs egress drop and a separate egress pass counter on `swp2`.
- Both use `devlink_trap_drop_test()` and `devlink_trap_drop_cleanup()` from the devlink library.

## Control Flow
For each test, tc filters are installed, continuous mausezahn IP traffic is started from h1 to h2, devlink trap drop counters are validated against the pass counter, the specific drop filter is removed, and cleanup kills traffic and removes pass filter state.

## State And Persistence
Mutates bridge topology, clsact qdiscs, tc flower filters, and background traffic. Trap-level cleanup is delegated to the library helper.

## Dependencies And Integration Points
Depends on forwarding libs, `tc_common.sh`, `devlink_lib.sh`, mausezahn, tc flower offload/drop actions, and mlxsw devlink trap drop groups.

## Risks
Correctness depends on the pass filter counter being placed where it observes packets that would otherwise be dropped and on devlink trap accounting being synchronized enough for the helper.

## Test Signals
Pass requires `devlink_trap_drop_test` to observe the expected ingress or egress flow action drop trap while the corresponding tc counter confirms test traffic.
