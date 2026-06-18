<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec.S

### Purpose
`cps-vec.S` implements low-level MIPS Coherent Processing System core boot, cache/coherence bring-up, VPE/VP startup, BEV exception stubs, and CPS power-management save/restore assembly.

### Important APIs, Types, And Functions
Important symbols/macros include `mips_cps_core_boot`, BEV stubs `excep_tlbfill`, `excep_xtlbfill`, `excep_cache`, `excep_genex`, `excep_intex`, `excep_ejtag`, `mips_cps_core_init`, `mips_cps_get_bootcfg`, `mips_cps_boot_vpes`, `mips_cps_cache_init`, `mips_cps_pm_save`, and `mips_cps_pm_restore`.

### Control Flow
Core boot saves CCA/GCR base, initializes caches if not already coherent, enters coherence, sets Kseg0 CCA, runs EVA init, retrieves boot config, performs MT core init, boots requested VPEs/VPs, loads target PC/GP/SP, and jumps to C code. VPE boot differs for MIPS R6 VP control via CPC run/stop registers versus classic MIPS MT TC/VPE configuration.

### State, Persistence, And Dependencies
State includes CP0 Config/EBase/MT registers, GCR/CPC registers, cache tags, coherence registers, boot config structures, and per-CPU suspend state. Dependencies include generated asm offsets, CPS SMP structures, EVA and PM macros, and optional NS16550 dumping.

### Integration Points
MIPS CPS SMP startup, CPU hotplug, early exception debugging, coherent domain entry, and CPU PM rely on this file.

### Risks
This executes before normal kernel services with fragile cache/coherence assumptions. Boot config offsets must match `asm-offsets.c`. MT and R6 VP paths have different register semantics, so config mismatches can strand VPEs.

### Test Signals
CPS SMP boot, multi-cluster/core/VPE startup, CPU hotplug, early BEV dump, cache initialization, coherent domain entry, and suspend/resume with CPS PM are key test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cps-vec.S -->
