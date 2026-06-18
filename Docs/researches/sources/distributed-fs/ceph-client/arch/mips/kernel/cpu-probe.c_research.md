<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-probe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-probe.c

### Purpose
`cpu-probe.c` identifies MIPS CPU implementations and capabilities, programs CP0 feature controls, populates `cpuinfo_mips`, and exports hardware capability data to userspace.

### Important APIs, Types, And Functions
Key globals are `elf_hwcap`, `__cpu_name`, `__elf_platform`, `__elf_base_platform`, `__ua_limit`, and `mmid_disabled_quirk`. Important functions include boot-parameter handlers for `nodsp`, `nohtw`, and `noftlb`; config decoders `decode_config0` through `decode_config5`; guest/VZ decoders; vendor probes for legacy, MIPS, Alchemy, SiByte, Broadcom, Cavium, Loongson, and Ingenic; `cpu_probe()`, `cpu_report()`, `cpu_set_cluster()`, `cpu_set_core()`, `cpu_set_vpe_id()`, and `cpu_disable_mmid()`.

### Control Flow
`cpu_probe()` initializes defaults, reads PRID, dispatches by company ID, decodes CP0 Config registers, applies vendor quirks, validates CPU type, enables RIXI exceptions when available, honors disable boot options, configures FPU/no-FPU state, sets SR sets and ELF HWCAP bits, probes MSA/VZ/vmbits, synthesizes Loongson CPUCFG, updates 64-bit user-address limits, and reserves exception space.

### State, Persistence, And Dependencies
State persists in per-CPU `cpu_data`, global ELF platform strings, HWCAP bits, CP0 Config/PageGrain/PWCtl/GuestCtl/GTOOffset/MemoryMapID registers, TLB sizing, ASID/MMID masks, write-combine modes, and exception reservation state.

### Integration Points
Almost every MIPS subsystem consumes this data: cache/TLB management, FPU/MSA, VZ/KVM, ELF auxv, signal ABI, page tables, perf, SMP topology, timers, and CPU errata handling.

### Risks
CPU probing mutates hardware registers while discovering features; mistakes can disable TLBs, MMID, FTLB, or hardware page walking incorrectly. Vendor PRID tables are broad and hardware-specific. Boot options must remain coherent with decoded feature flags.

### Test Signals
Boot matrix across supported CPU families, HWCAP/auxv validation, FPU/MSA/DSP availability, VZ guest feature probing, TLB/MMID/ASID behavior, `noftlb/nohtw/nodsp` boot options, and CPU hotplug consistency are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-probe.c -->
