<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-r3k-probe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-r3k-probe.c

### Purpose
This file is the reduced CPU probe path for R3000/R2000-era MIPS systems selected by `CONFIG_CPU_R3K_TLB`.

### Important APIs, Types, And Functions
It exports `elf_hwcap`, defines `check_bugs32()`, `cpu_has_confreg()`, `set_elf_platform()`, `cpu_probe()`, and `cpu_report()`.

### Control Flow
`cpu_probe()` reads PRID, switches on legacy implementation IDs, distinguishes R3000A from R3081 by toggling the alternate cache bit and comparing cache size, sets CPU name/type/options/FPU flags/TLB size, and BUGs on unknown CPU. `cpu_report()` logs CPU and FPU revisions.

### State, Persistence, And Dependencies
State persists in `current_cpu_data`, `__cpu_name`, `__elf_platform`, and `elf_hwcap`. Dependencies include R3K cache probing, CP0 PRID/conf reads, FPU detection, and CPU feature definitions.

### Integration Points
The kernel Makefile selects this instead of generic `cpu-probe.o` for R3K TLB builds. Early boot, cache/TLB management, ELF platform exposure, and bug checking rely on it.

### Risks
This path supports old hardware with simple feature detection. Misidentifying R3081/R3000 affects cache and TLB assumptions. Unknown PRIDs trigger BUG rather than fallback.

### Test Signals
Build with `CONFIG_CPU_R3K_TLB`, boot R2000/R3000/R3000A/R3081 targets, validate cache-size probing, FPU detection, TLB size, and reported CPU name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cpu-r3k-probe.c -->
