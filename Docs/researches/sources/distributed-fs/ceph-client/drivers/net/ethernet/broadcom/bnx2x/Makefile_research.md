# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/Makefile

## Purpose
This Kbuild makefile declares the Broadcom/QLogic `bnx2x` 10-Gigabit Ethernet driver object composition. It controls which compilation units are linked into `bnx2x.o` for the kernel configuration and adds SR-IOV support objects only when `CONFIG_BNX2X_SRIOV` is enabled.

## Important APIs, Types, and Build Targets
- `obj-$(CONFIG_BNX2X) += bnx2x.o` builds the driver as built-in or module according to the kernel config symbol.
- `bnx2x-y` lists the always-included objects: main probe/control, link management, common fast/load logic, ethtool, stats, DCB, slowpath, and self-test support.
- `bnx2x-$(CONFIG_BNX2X_SRIOV)` conditionally adds `bnx2x_vfpf.o` and `bnx2x_sriov.o` for virtual function and PF/VF mailbox support.

## Control Flow
There is no runtime flow in this file. At build time, Kbuild expands the config-controlled variables and links the selected object files into the final driver object.

## State and Persistence Behavior
The file only affects build artifacts. It does not define runtime state, persistence, or module parameters directly. Its choices determine which code paths exist in the resulting kernel/module.

## Dependencies and Integration Points
- Depends on the kernel Kbuild object aggregation model.
- `bnx2x_cmn.o` supplies common load/unload, queue, RX/TX, NAPI, interrupt, feature, and PM helpers declared by `bnx2x_cmn.h`.
- `bnx2x_main.o` typically owns probe/remove/netdev registration and calls into the common code.
- Conditional SR-IOV objects must stay in sync with `#ifdef CONFIG_BNX2X_SRIOV` declarations in headers such as `bnx2x.h`, `bnx2x_cmn.h`, and `bnx2x_sriov.h`.

## Risks
- Omitting a required object causes unresolved symbols at link time or disabled runtime features.
- Adding an object unconditionally when it depends on config-gated headers can break builds for non-SR-IOV configurations.
- Moving common functionality between files requires updating this makefile and all declarations together.

## Test Signals
- `CONFIG_BNX2X=m` and `CONFIG_BNX2X=y` builds link successfully.
- Builds with `CONFIG_BNX2X_SRIOV=y` include PF/VF mailbox symbols; builds without it do not require SR-IOV objects.
- Module load smoke tests confirm all always-linked subsystems initialize through the expected object set.
