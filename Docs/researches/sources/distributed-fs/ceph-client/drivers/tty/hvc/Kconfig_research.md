# sources/distributed-fs/ceph-client/drivers/tty/hvc/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/hvc/Kconfig` defines configuration options for hypervisor virtual console infrastructure and backend drivers. It covers generic HVC support, IRQ support, PowerPC pSeries/PowerNV/RTAS/HVSI/HVCS backends, z/VM IUCV, Xen, PPC udbg, ARM DCC, RISC-V SBI, and related debug constraints. The source was read as a complete 136-line file for this report.

## Important APIs, Types, and Functions

This is Kconfig data. Important symbols include `HVC_DRIVER`, `HVC_IRQ`, `HVC_CONSOLE`, `HVC_OLD_HVSI`, `HVC_OPAL`, `HVC_RTAS`, `HVC_IUCV`, `HVC_XEN`, `HVC_XEN_FRONTEND`, `HVC_UDBG`, `HVC_DCC`, `HVC_DCC_SERIALIZE_SMP`, `HVC_RISCV_SBI`, and `HVCS`.

## Control Flow

Kconfig dependency evaluation makes `HVC_DRIVER` a hidden common infrastructure symbol selected by individual backends. `HVC_IRQ` is selected by interrupt-driven backends. Architecture and hypervisor symbols gate each backend: for example `PPC_PSERIES` gates pSeries HVC, `PPC_POWERNV` gates OPAL, `S390 && NET` gates IUCV, `XEN` gates Xen, `ARM || ARM64` gates DCC, and `RISCV_SBI && NONPORTABLE` gates RISC-V SBI. Defaults enable common console paths for several platform types.

## State and Persistence Behavior

The file persists build-time HVC choices in `.config`. Runtime state is owned by the corresponding HVC C drivers and the common `hvc_console` layer, not by this Kconfig file.

## Dependencies and Integration Points

It integrates with `drivers/tty/hvc/Makefile`, the TTY Makefile's `obj-$(CONFIG_HVC_DRIVER) += hvc/`, architecture platform symbols, Xen and S390 IUCV infrastructure, serial console support for DCC, and the common HVC core. The selected symbols determine which backend object files are built.

## Risks and Edge Cases

Several options are architecture-specific and should not be visible outside their platform dependencies. `HVC_UDBG` and `HVC_RISCV_SBI` are explicitly bring-up or nonportable paths and can conflict with production console expectations. `HVC_DCC_SERIALIZE_SMP` intentionally restricts DCC use to CPU0 and can affect CPU hotplug or SMP behavior.

## Test Signals

Useful signals include configuration tests for each architecture backend; build checks that selecting a backend also selects `HVC_DRIVER` and, where needed, `HVC_IRQ`; boot console tests on pSeries, PowerNV, Xen, S390 z/VM, ARM DCC, and RISC-V SBI setups; and negative config tests confirming unavailable backends stay hidden when architecture dependencies are false.
