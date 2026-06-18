
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/Kconfig

Purpose: groups Loongson DMA controller options and exposes three DMAEngine drivers for Loongson1 APB, Loongson2 APB, and Loongson2 chain multi-channel DMA hardware.

Important APIs and control flow: the menu is active under `MACH_LOONGSON32 || MACH_LOONGSON64 || COMPILE_TEST`. `LOONGSON1_APB_DMA` is tristate, depends on `MACH_LOONGSON32 || COMPILE_TEST`, and selects DMAEngine plus virt-dma. `LOONGSON2_APB_DMA` and `LOONGSON2_APB_CMC_DMA` are tristate, depend on `MACH_LOONGSON64 || COMPILE_TEST`, and select the same DMAEngine infrastructure.

State and persistence behavior: no runtime state exists; symbols control whether the matching platform drivers are compiled as built-ins or modules.

Dependencies and integration points: integrates with the local Makefile and architecture configuration. The help text describes Loongson1 NAND/audio, Loongson2 single-channel APB peripherals, and Loongson-2K0300/2K3000 multi-channel bidirectional controllers.

Risks and test signals: risks include architecture dependency drift, help text not matching actual compatible coverage, and missing compile-test dependencies if APIs evolve. Test signals include all three symbols building under native Loongson configs and `COMPILE_TEST`, and module aliases being generated from OF/ACPI tables in the C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Kconfig -->
