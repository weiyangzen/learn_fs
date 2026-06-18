# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.h

## Purpose
`cpsw_switchdev.h` declares the CPSW switchdev integration API used by the switch-mode CPSW driver.

## Important APIs, Types, And Functions
It includes `<net/switchdev.h>` and declares `cpsw_port_dev_check()`, `cpsw_switchdev_register_notifiers()`, and `cpsw_switchdev_unregister_notifiers()`.

## Control Flow
There is no implementation in the header. `cpsw_new.c` calls register/unregister during probe/remove, and switchdev notifier helpers use `cpsw_port_dev_check()` as their filter predicate.

## State And Persistence
No state is stored in this header. The functions it declares operate on `struct cpsw_common` and `struct net_device` state owned by `cpsw_new.c` and `cpsw_priv.h`.

## Dependencies And Integration Points
The header is the narrow contract between the switchdev implementation file and the `cpsw-switch` front end. It depends on `struct cpsw_common` being visible to includers through `cpsw_priv.h`.

## Risks
The prototypes expose global notifier registration, so probe/remove ordering must avoid double registration or unregistering without prior registration. `cpsw_port_dev_check()` is security-sensitive in the sense that it gates which netdevs receive CPSW hardware offload operations.

## Test Signals
Compile with switchdev enabled, probe/remove `cpsw-switch`, confirm only CPSW switch-mode ports pass the device check, and verify bridge/switchdev operations do not affect legacy `cpsw` or unrelated netdevs.
