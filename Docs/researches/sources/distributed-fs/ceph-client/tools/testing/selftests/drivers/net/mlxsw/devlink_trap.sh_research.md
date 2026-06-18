
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap.sh`

## Purpose
Tests generic mlxsw devlink trap behavior during device reload/delete while trapped packets are arriving.

## Important APIs, Types, And Functions
- Standard topology helpers create two simple host interfaces connected through a bridge on two switch ports.
- `dev_del_test()` sends continuous multicast-source packets that trigger `source_mac_is_multicast`, sets the trap action to `trap`, repeatedly reloads the devlink device, and rebuilds topology.

## Control Flow
Setup creates VRFs and bridge topology. `dev_del_test()` starts mausezahn in the background, loops five times setting trap action, sleeping, reloading the device, waiting for netdevices to be recreated, then calling cleanup/setup again. It logs one ksft test at the end and kills the traffic generator.

## State And Persistence
Mutates bridge topology, trap action, and triggers devlink reloads. Cleanup tears down bridge/VRF state; reload recreates netdevices and requires topology reconstruction.

## Dependencies And Integration Points
Depends on forwarding libraries, `devlink_lib.sh`, mausezahn, mlxsw devlink reload support, and `source_mac_is_multicast` trap support.

## Risks
The test is disruptive and timing-heavy, with a fixed 20 second wait after reload. It validates robustness primarily by absence of crash/failure during repeated reload under trapped traffic.

## Test Signals
Pass is successful completion of five reload iterations while traffic is trapped, with no command failures in setup/cleanup/reload.
