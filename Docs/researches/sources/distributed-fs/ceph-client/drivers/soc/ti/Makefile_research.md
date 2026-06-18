# sources/distributed-fs/ceph-client/drivers/soc/ti/Makefile

## Purpose

`drivers/soc/ti/Makefile` maps TI SoC Kconfig symbols to built objects. It is the build glue for Keystone Navigator, AMx3 PM, Wakeup M3 IPC, K3 RingACC, K3 SoC info, PRUSS, TI SCI INTA MSI, and OMAP SmartReflex.

## Important APIs, Types, and Functions

This file has no executable APIs. Object mappings include `knav_qmss.o` from `knav_qmss_queue.o` and `knav_qmss_acc.o`, `knav_dma.o`, `pm33xx.o`, `wkup_m3_ipc.o`, `ti_sci_inta_msi.o`, `k3-ringacc.o`, `k3-socinfo.o`, `pruss.o`, and `smartreflex.o`.

## Control Flow

Kbuild evaluates each `obj-$(CONFIG_...)` line after Kconfig. Tristate symbols produce built-in or module objects, while bool symbols produce built-in objects when enabled. `knav_qmss-y` composes the QMSS object from queue and accumulator implementation files.

## State and Persistence Behavior

The Makefile only affects build outputs. It does not define runtime state or persistence. The resulting object/module inclusion is determined by the persistent kernel `.config`.

## Dependencies and Integration Points

It integrates directly with `drivers/soc/ti/Kconfig` symbols and Kbuild. `CONFIG_POWER_AVS_OMAP` links `smartreflex.o` even though that symbol is owned outside this TI SoC Kconfig snippet.

## Risks and Edge Cases

Symbol/object drift between Kconfig and Makefile will cause enabled drivers not to build or stale objects to be referenced. Composite object naming for `knav_qmss-y` requires the final `knav_qmss.o` line to stay aligned. Module naming changes can affect autoload and packaging.

## Test Signals

Build all TI SoC symbol combinations as built-in and module where allowed. Confirm `knav_qmss.o` contains both queue and accumulator objects, and that each enabled Kconfig symbol contributes exactly the expected object.
