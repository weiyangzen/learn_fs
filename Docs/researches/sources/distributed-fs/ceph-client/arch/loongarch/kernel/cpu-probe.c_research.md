<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cpu-probe.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/cpu-probe.c

Purpose: probes LoongArch CPU capabilities, address sizes, TLB geometry, FPU masks, hardware watchpoint counts, and ELF hardware capabilities.
Important APIs and types: defines/export `elf_hwcap`, `vm_map_base`, `__ua_limit`, CPU name/family arrays, `cpu_probe`, `cpu_probe_common`, `cpu_probe_addrbits`, `cpu_probe_loongson`, SIMD boot parameter handling, and spectre mitigation reporting.
Control flow: boot/CPU bring-up reads CPUCFG and CSR registers, sets ISA/options/HWCAP bits, configures ASID masks, TLB sizes, timer bits, KSave masks, watchpoint availability, vendor/core names, address-space base, and user-access limit. An early `simd=` parameter can cap LSX/LASX exposure before final arch init.
State and persistence: populates `cpu_data`, `elf_hwcap`, CPU family/name strings, `vm_map_base`, `__elf_platform`, `__ua_limit`, and per-CPU feature masks.
Dependencies and integration: feeds ELF auxvec, `pgtable.h` layout, uaccess, TLB code, FPU/vector code, hardware breakpoints, Loongson IOCSR features, and sysfs vulnerability reporting.
Risks and test signals: over-advertised features cause illegal instructions; address-bit mistakes break kernel/user layout. Signals include boot logs, auxvec HWCAP checks, vector/FPU tests, TLB/page-table stress, and different CPUCFG configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/cpu-probe.c -->
