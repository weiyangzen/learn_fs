# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/Makefile

## Purpose
Builds the Broadcom NetXtreme-C/E Ethernet driver object for the Linux kernel tree. The file maps Kconfig selections to the composite `bnxt_en.o` module/built-in object and lists which implementation objects are always linked versus conditionally linked for TC flower offload, debugfs, and hardware-monitoring support.

The Makefile is small, but it defines the feature composition of the entire `drivers/net/ethernet/broadcom/bnxt/` driver. The parent Broadcom Makefile enters this directory via `obj-$(CONFIG_BNXT) += bnxt/`, and this directory Makefile emits `bnxt_en.o` when `CONFIG_BNXT` is enabled.

## Important APIs, Types, and Functions
The primary kbuild API is `obj-$(CONFIG_BNXT) += bnxt_en.o`. When `CONFIG_BNXT=y`, `bnxt_en.o` is linked into the kernel; when `CONFIG_BNXT=m`, it becomes the `bnxt_en` module; when unset, none of the listed objects are built through this directory.

`bnxt_en-y` names the unconditional object list: `bnxt.o`, `bnxt_hwrm.o`, `bnxt_sriov.o`, `bnxt_ethtool.o`, `bnxt_dcb.o`, `bnxt_ulp.o`, `bnxt_xdp.o`, `bnxt_ptp.o`, `bnxt_vfr.o`, `bnxt_devlink.o`, `bnxt_dim.o`, `bnxt_coredump.o`, and `bnxt_gso.o`. These files form the baseline driver even though individual code regions inside them may still use C preprocessor guards such as `CONFIG_BNXT_SRIOV`.

Conditional fragments add `bnxt_tc.o` for `CONFIG_BNXT_FLOWER_OFFLOAD`, `bnxt_debugfs.o` for `CONFIG_DEBUG_FS`, and `bnxt_hwmon.o` for `CONFIG_BNXT_HWMON`. The parent Kconfig defines `BNXT` as a PCI NetXtreme-C/E driver that selects firmware loading, CRC32, devlink, page pool, DIM, and auxiliary bus support; it defines `BNXT_FLOWER_OFFLOAD` as TC flower/eswitch offload; and it defines `BNXT_HWMON` as thermal sensor exposure through hwmon sysfs.

## Control Flow and State
There is no runtime control flow in the Makefile. Its control flow is kbuild variable expansion. Kbuild first decides whether `bnxt_en.o` exists from `CONFIG_BNXT`, then folds every object in `bnxt_en-y` and every enabled `bnxt_en-$(CONFIG_...)` fragment into that single final object. Link order follows the object list, which matters for built-in initialization tables, symbol resolution diagnostics, and predictable module contents.

The persistent state influenced by this file is build output: whether the kernel or module contains the core PCI/netdevice implementation, HWRM firmware command layer, SR-IOV support file, ethtool operations, DCB hooks, upper-layer protocol hooks, XDP support, PTP support, VF representor support, devlink integration, DIM logic, coredump support, GSO helpers, optional TC flower offload, optional debugfs entries, and optional hwmon sysfs support.

## Dependencies and Integration Points
The Makefile depends on the Linux kbuild composite-object conventions and on Kconfig symbols from `drivers/net/ethernet/broadcom/Kconfig` plus global `CONFIG_DEBUG_FS`. It integrates with the parent Broadcom Makefile, which descends into `bnxt/` only under `CONFIG_BNXT`.

The unconditional object list mirrors include relationships seen in `bnxt.c`, which includes headers such as `bnxt_hwrm.h`, `bnxt_sriov.h`, `bnxt_ethtool.h`, `bnxt_dcb.h`, `bnxt_xdp.h`, `bnxt_ptp.h`, `bnxt_vfr.h`, `bnxt_tc.h`, `bnxt_devlink.h`, `bnxt_debugfs.h`, `bnxt_coredump.h`, `bnxt_hwmon.h`, and `bnxt_gso.h`. `bnxt_hwrm.o` provides the HWRM request/response command machinery. `bnxt_sriov.o` is always compiled into the composite object, while its SR-IOV behavior is mostly guarded in C by `CONFIG_BNXT_SRIOV`. The optional objects provide symbols only when their matching feature code is compiled and referenced.

Externally, the final `bnxt_en` object integrates with PCI probing, netdevice registration, ethtool, devlink, XDP/BPF, PTP clock support, DCB, SR-IOV/switchdev, debugfs, hwmon, firmware request infrastructure, and the kernel networking stack.

## Risks
The main risk is build-graph skew: adding a new source file or feature callsite without updating this Makefile can leave symbols undefined or feature code absent from `bnxt_en`. Conversely, linking an optional object unconditionally can create unwanted dependencies on subsystems that are disabled or modular in incompatible ways.

Configuration mismatch is another risk. `bnxt_sriov.o`, `bnxt_dcb.o`, `bnxt_ptp.o`, and similar baseline files must compile cleanly across all legal Kconfig combinations even when their functional subsystem support is disabled. Optional `bnxt_debugfs.o` and `bnxt_hwmon.o` must remain aligned with headers and stubs used by unconditional code. `CONFIG_BNXT_HWMON` has a Kconfig dependency preventing built-in BNXT from depending on modular HWMON; changing the Makefile without preserving that policy can introduce link failures.

Because this file controls a production NIC driver, missing objects are not always caught by a single default build. A feature may compile only in allmodconfig, only with `CONFIG_DEBUG_FS`, only with hwmon enabled, or only when flower offload is selected.

## Test Signals
Build tests should cover `CONFIG_BNXT=y`, `CONFIG_BNXT=m`, and `CONFIG_BNXT=n`, plus combinations of `CONFIG_BNXT_FLOWER_OFFLOAD`, `CONFIG_DEBUG_FS`, `CONFIG_BNXT_HWMON`, `CONFIG_BNXT_SRIOV`, `CONFIG_BNXT_DCB`, and PTP/HWMON dependency permutations allowed by Kconfig. Useful automated targets include `make drivers/net/ethernet/broadcom/bnxt/`, allmodconfig, allyesconfig where legal, and minimal PCI/net configs.

Runtime smoke signals for the resulting object include successful `bnxt_en` module load/unload, PCI probe/remove, firmware HWRM command initialization, netdevice up/down, ethtool query paths, devlink registration, XDP attach/detach, PTP registration when supported, SR-IOV enable/disable paths, optional TC flower offload setup when compiled, debugfs file creation when `CONFIG_DEBUG_FS` is enabled, and hwmon sysfs exposure when `CONFIG_BNXT_HWMON` is enabled.
