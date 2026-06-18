# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/Makefile

## Purpose
Defines the kernel build composition for the Intel i40e driver module. It selects include paths, builds `i40e.o` when `CONFIG_I40E` is enabled, and lists the object files linked into the module, with DCB support added conditionally.

## Important APIs, Types, and Functions
The key build variables are `ccflags-y`, `subdir-ccflags-y`, `obj-$(CONFIG_I40E)`, `i40e-y`, and `i40e-$(CONFIG_I40E_DCB)`. Core objects include main, ethtool, admin queue, common, HMC, LAN HMC, NVM, debugfs, diagnostics, TX/RX, PTP, DDP, client, virtchnl PF, AF_XDP, and devlink support. Conditional DCB objects are `i40e_dcb.o` and `i40e_dcb_nl.o`.

## Control Flow
There is no runtime control flow. Kernel Kbuild uses these assignments to decide which source files are compiled and linked into `i40e.ko`.

## State and Persistence Behavior
The file defines build-time module composition only. It does not define runtime or persistent device state.

## Dependencies and Integration Points
Integrates with Linux Kbuild and `CONFIG_I40E`/`CONFIG_I40E_DCB`. The include path flags allow local driver headers to be found by objects in this directory and subdirectories.

## Risks
Removing or misordering objects can produce unresolved symbols or omit feature initialization at link time. Conditional DCB object selection must stay consistent with preprocessor guards in `i40e.h` and other source files. Adding a new source file without listing it here means it will not be part of the module.

## Test Signals
Build with `CONFIG_I40E=m`, `CONFIG_I40E=y`, and disabled; build with `CONFIG_I40E_DCB` on and off; run modpost for unresolved symbols; and verify the resulting module contains adminq, netdev, virtchnl, devlink, PTP, AF_XDP, and optional DCB entry points.
