# sources/distributed-fs/ceph-client/drivers/tty/hvc/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/hvc/Makefile` maps HVC Kconfig symbols to the common hypervisor virtual console core and backend object files. The source was read as a complete 13-line file for this report.

## Important APIs, Types, and Functions

This is kbuild data. Important mappings are `CONFIG_HVC_DRIVER` to `hvc_console.o`, `CONFIG_HVC_IRQ` to `hvc_irq.o`, `CONFIG_HVC_CONSOLE` to `hvc_vio.o hvsi_lib.o`, `CONFIG_HVC_OPAL` to `hvc_opal.o hvsi_lib.o`, `CONFIG_HVC_OLD_HVSI` to `hvsi.o`, `CONFIG_HVC_RTAS` to `hvc_rtas.o`, `CONFIG_HVC_DCC` to `hvc_dcc.o`, `CONFIG_HVC_XEN` to `hvc_xen.o`, `CONFIG_HVC_IUCV` to `hvc_iucv.o`, `CONFIG_HVC_UDBG` to `hvc_udbg.o`, `CONFIG_HVC_RISCV_SBI` to `hvc_riscv_sbi.o`, and `CONFIG_HVCS` to `hvcs.o`.

## Control Flow

kbuild evaluates the `obj-$(CONFIG_*)` lines after the parent TTY Makefile descends into `drivers/tty/hvc/`. Built-in and module linkage follows the selected symbol values. Shared `hvsi_lib.o` is included by both pSeries HVC and OPAL configurations when selected.

## State and Persistence Behavior

No runtime state is owned here. The file persists build decisions as object inclusion in the kernel image or modules.

## Dependencies and Integration Points

It is paired with `drivers/tty/hvc/Kconfig` and depends on the parent `drivers/tty/Makefile` only entering the directory when `CONFIG_HVC_DRIVER` is enabled. It integrates HVC backend source files with the common console layer.

## Risks and Edge Cases

Shared library object inclusion must remain aligned with backend users; omitting `hvsi_lib.o` for a backend that references it would fail link. If Kconfig selects a backend without `HVC_DRIVER`, the parent directory might not be entered, so the Kconfig select relationships are part of the build contract.

## Test Signals

Useful signals include build-only checks for each HVC backend symbol, link checks for shared `hvsi_lib.o`, module/built-in combinations for `HVCS`, and config tests verifying the directory is skipped when no HVC backend selects `HVC_DRIVER`.
