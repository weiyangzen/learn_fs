# sources/distributed-fs/ceph-client/drivers/s390/net/Kconfig

## Purpose
This Kconfig file defines the s390 network-device driver menu and configuration symbols for CTCM, VM special-message IUCV support, qeth Ethernet/HiperSockets support, CCWGROUP aggregation, and ISM vPCI adapter support.

## Important APIs, Types, And Functions
Important symbols are `CTCM`, `SMSGIUCV`, `SMSGIUCV_EVENT`, `QETH`, `QETH_L2`, `QETH_L3`, `QETH_OSX`, `CCWGROUP`, and `ISM`. The menu depends on `NETDEVICES && S390`; individual options add dependencies such as `CCW`, `IUCV`, `IP_MULTICAST`, `QDIO`, `ETHERNET`, `BRIDGE`, `PCI`, and `DIBS`.

## Control Flow
Kconfig evaluation controls which drivers are built in, built as modules, or omitted. `CTCM`, `SMSGIUCV`, `QETH`, `QETH_L2`, and `QETH_L3` default to module or built-in values as specified. `QETH_OSX` defaults based on `!HAVE_MARCH_Z15_FEATURES`. `CCWGROUP` is selected by default when CTCM, QETH, or SMC are enabled.

## State And Persistence
The file contributes kernel build configuration state, persisted in `.config`, but has no runtime state itself.

## Dependencies And Integration Points
The companion Makefile consumes these symbols via `obj-$(CONFIG_*)`. Driver help text maps symbols to module names such as `ctcm`, `smsgiucv_app`, `qeth`, `qeth_l2`, `qeth_l3`, and `ism`.

## Risks And Test Signals
Risks include dependency mistakes that expose drivers without required bus/protocol support, default changes that alter s390 kernel footprint, and `CCWGROUP` not matching dependent drivers. Test signals include Kconfig dependency resolution, allyesconfig/allmodconfig builds for s390, and module presence matching selected symbols.
