# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/Makefile

## Purpose
Defines the object composition of the Intel IOSM WWAN driver module.

## Important APIs, Types, And Functions
`iosm-y` includes task queue, IMEM, MMIO, port, WWAN, uevent, PM, PCIe, IRQ, channel config, protocol, mux, devlink, flash, and coredump objects. `iosm-$(CONFIG_WWAN_DEBUGFS)` adds `iosm_ipc_debugfs.o` and `iosm_ipc_trace.o`. `obj-$(CONFIG_IOSM) := iosm.o` builds the aggregate module/object.

## Control Flow
Kbuild links the listed objects into `iosm.o` when `CONFIG_IOSM` is enabled. Debugfs-specific objects are included only when `CONFIG_WWAN_DEBUGFS` is set.

## State And Persistence
No runtime state. It determines which IOSM features are compiled into the module.

## Dependencies And Integration Points
Integrates with IOSM C files and WWAN debugfs Kconfig. The files in this work item are part of the listed core and debugfs object sets.

## Risks
Ordering is not usually semantic for linking, but missing objects break symbols such as devlink, flash, coredump, or trace hooks. Debugfs stub headers must match Makefile conditional inclusion.

## Test Signals
Build IOSM with `CONFIG_IOSM=y/m` and `CONFIG_WWAN_DEBUGFS=y/n`. Check that devlink flash/coredump symbols resolve and trace/debugfs objects are included only in debugfs builds.
