# sources/distributed-fs/ceph-client/drivers/s390/net/Makefile

## Purpose
This Makefile maps s390 network Kconfig symbols to composite objects and modules.

## Important APIs, Types, And Functions
Composite objects include `ctcm-y`, `qeth-y`, `qeth_l2-y`, `qeth_l3-y`, and `ism-y`. Conditional object entries use `obj-$(CONFIG_CTCM)`, `obj-$(CONFIG_SMSGIUCV)`, `obj-$(CONFIG_SMSGIUCV_EVENT)`, `obj-$(CONFIG_QETH)`, `obj-$(CONFIG_QETH_L2)`, `obj-$(CONFIG_QETH_L3)`, and `obj-$(CONFIG_ISM)`.

## Control Flow
During the kernel build, enabled config symbols determine which module or built-in objects are included. `ctcm.o` is built from main, FSM, MPC, sysfs, and debug components plus `fsm.o`; qeth core and layer modules are split into core, L2, and L3 composites; ISM builds from `ism_drv.o`.

## State And Persistence
The file has no runtime state. It affects build artifacts.

## Dependencies And Integration Points
It consumes symbols defined in the same folder's Kconfig and references source/object names under `drivers/s390/net`. `ctcm_dbug.o` is included in `ctcm-y`, linking the debug facility helpers from this subset into the CTCM driver.

## Risks And Test Signals
Risks include object list drift when sources are renamed, missing dependencies when symbols change, and stale composite membership. Test signals are s390 builds across built-in and module configurations and link checks for CTCM/qeth/ISM modules.
