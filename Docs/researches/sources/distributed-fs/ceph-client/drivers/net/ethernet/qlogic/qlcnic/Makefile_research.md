# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/Makefile

## Purpose

This Makefile declares how the Linux kernel Kbuild system composes the `qlcnic` QLogic 1G/10G CNA Ethernet driver. It maps `CONFIG_QLCNIC` to the `qlcnic.o` module/built-in object and lists the source objects that form the driver, with optional SR-IOV PF and DCB objects controlled by separate Kconfig options.

## Important Build Rules

- `obj-$(CONFIG_QLCNIC) := qlcnic.o` builds the driver when `CONFIG_QLCNIC` is enabled.
- `qlcnic-y := ...` links the common driver body from hardware, main netdev, initialization, ethtool, context, I/O, sysfs, minidump, 83xx hardware/init/vNIC, and SR-IOV common objects.
- `qlcnic-$(CONFIG_QLCNIC_SRIOV) += qlcnic_sriov_pf.o` conditionally adds physical-function SR-IOV support.
- `qlcnic-$(CONFIG_QLCNIC_DCB) += qlcnic_dcb.o` conditionally adds Data Center Bridging support.

The always-built list includes:

- `qlcnic_hw.o`, `qlcnic_main.o`, `qlcnic_init.o`
- `qlcnic_ethtool.o`, `qlcnic_ctx.o`, `qlcnic_io.o`
- `qlcnic_sysfs.o`, `qlcnic_minidump.o`
- `qlcnic_83xx_hw.o`, `qlcnic_83xx_init.o`, `qlcnic_83xx_vnic.o`
- `qlcnic_sriov_common.o`

## Control Flow And Integration Behavior

Build-time control flow is Kbuild driven:

1. If `CONFIG_QLCNIC` is disabled, none of these objects are linked as the `qlcnic` driver.
2. If enabled, all `qlcnic-y` objects are linked into one composite `qlcnic.o`.
3. If `CONFIG_QLCNIC_SRIOV` is enabled, PF-specific SR-IOV code is linked in addition to common SR-IOV code.
4. If `CONFIG_QLCNIC_DCB` is enabled, DCB implementation code is linked; otherwise call sites must be guarded or provided by stubs/conditionals in headers.

## Dependencies And Integration Points

This file integrates with the kernel top-level driver build and Kconfig system. It assumes corresponding `.c` files exist in the same directory and that shared headers expose valid stubs or conditional declarations for optional features.

The Makefile makes `qlcnic_83xx_hw.c` part of the normal driver, so the 83xx operation tables and mailbox/flash/link support are compiled whenever the driver is enabled, not only for a separate 83xx config.

## Risks And Edge Cases

- Optional feature mismatches can produce unresolved symbols if common code calls PF SR-IOV or DCB functions without matching `#ifdef` protection or static stubs.
- Moving an object out of `qlcnic-y` can silently remove registration paths or operation tables needed for supported hardware.
- Adding new source files without updating this Makefile leaves code unbuilt in kernel builds.
- `qlcnic_sriov_common.o` is always linked; it must remain valid even when PF SR-IOV is disabled.

## Test Signals

- Kernel build with `CONFIG_QLCNIC=m` and `=y`.
- Build matrix with `CONFIG_QLCNIC_SRIOV` and `CONFIG_QLCNIC_DCB` both enabled and disabled.
- `modinfo qlcnic` and module load smoke tests on systems without optional hardware.
- Link-time checks for unresolved symbols after changing object membership.
