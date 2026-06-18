# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/Makefile

## Purpose
Defines the kbuild object composition for the Intel ICE E800 series Ethernet driver. It selects the core `ice.o` module and conditionally adds source objects based on kernel configuration options.

## Important APIs, Types, and Functions
The important kbuild variables are `subdir-ccflags-y`, `obj-$(CONFIG_ICE)`, `ice-y`, and conditional `ice-$(CONFIG_...)` additions. The core object list includes main PCI/device control, control queue, common/NVM/switch/scheduler/base/lib code, Tx/Rx, filters, IRQ, VLAN mode and ops, Flow Director, parser, IDC, devlink, subfunction support, firmware update, LAG, ethtool, representors, TC, debugfs, and adapter code. Conditional blocks add SR-IOV/virtchnl support, PTP/DPLL/TSPLL support, DCB, accelerated RFS, AF_XDP, switchdev, GNSS, and HWMON.

## Control Flow
There is no runtime control flow. Kbuild evaluates config symbols and constructs the set of objects linked into `ice.o`. `subdir-ccflags-y += -I$(src)` ensures local headers are discoverable for files in subdirectories such as `devlink/` and `virt/`.

## State and Persistence
The Makefile persists build-time module composition. Runtime driver state is in the compiled sources it selects. Configuration-dependent object inclusion controls which features exist in the resulting module.

## Dependencies and Integration Points
Integrates with the Linux kernel kbuild system and the ICE source tree. Feature dependencies come from Kconfig symbols including `CONFIG_ICE`, `CONFIG_PCI_IOV`, `CONFIG_PTP_1588_CLOCK`, `CONFIG_DCB`, `CONFIG_RFS_ACCEL`, `CONFIG_XDP_SOCKETS`, `CONFIG_ICE_SWITCHDEV`, `CONFIG_GNSS`, and `CONFIG_ICE_HWMON`.

## Risks
Missing an object causes link failures or silently removes feature hooks if declarations are also conditional. Adding a feature object under the wrong config can create unresolved symbols or compile code without its subsystem dependencies. Subdirectory object paths must remain aligned with source layout.

## Test Signals
Build `CONFIG_ICE=m/y` with major feature combinations: base only, SR-IOV, PTP, DCB, RFS, AF_XDP, switchdev, GNSS, and HWMON. Watch for unresolved symbols, missing module sections, and feature-specific probe or ethtool/devlink behavior in the resulting ICE driver.
