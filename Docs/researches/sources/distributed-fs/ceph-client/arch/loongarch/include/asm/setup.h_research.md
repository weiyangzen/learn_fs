<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/setup.h

Purpose: declares LoongArch early boot parameters and setup-time globals.
Important APIs and types: exposes firmware argument variables, command-line pointers, CPU address-bit globals (`cpu_pabits`, `cpu_vabits`), memory limits, `early_memblock`, `loongarch_parse_*` setup helpers, and boot CPU configuration hooks.
Control flow: early assembly stores firmware arguments; setup code parses them and populates boot configuration before normal memory management and CPU probing.
State and persistence: globals persist early firmware-provided command line, memory layout, and CPU address-size decisions used later by MM and platform code.
Dependencies and integration: shared by `head.S`, environment parsing, CPU probe, memblock setup, EFI/FDT/ACPI paths, and `pgtable.h` layout.
Risks and test signals: wrong setup state breaks boot before diagnostics are rich. Signals include EFI and FDT boot, command-line parsing, memblock reservations, and multiple page-size/address-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/setup.h -->
