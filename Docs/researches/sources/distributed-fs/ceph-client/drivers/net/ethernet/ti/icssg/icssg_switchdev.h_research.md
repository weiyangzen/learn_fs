<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.h

## Purpose

`icssg_switchdev.h` declares the private switchdev integration API for the ICSSG driver.

## Important APIs, Types, and Functions

It declares `prueth_switchdev_register_notifiers()`, `prueth_switchdev_unregister_notifiers()`, and `prueth_dev_check()`, and includes `icssg_prueth.h` for `struct prueth` and `struct net_device` visibility.

## Control Flow

There is no executable flow. The main driver calls the register/unregister helpers during probe/remove when switch mode is supported, while switchdev code calls `prueth_dev_check()` to filter events to running ICSSG switch-mode netdevs.

## State and Persistence Behavior

The header owns no state. Its declared functions manage notifier block state embedded in `struct prueth` and query netdev state in the main driver.

## Dependencies and Integration Points

It connects `icssg_prueth.c` and `icssg_switchdev.c` without exposing switchdev internals to other files.

## Risks and Edge Cases

Because `prueth_dev_check()` is declared here but implemented in the main driver, SR1 builds and non-switch configurations must continue to compile/link with the expected object set. Any signature change affects switchdev notifier registration and event filtering.

## Test Signals

Build the driver with switchdev support and validate probe/remove notifier registration. Runtime bridge enslave/leave tests confirm `prueth_dev_check()` admits only running ICSSG devices in switch mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.h -->
