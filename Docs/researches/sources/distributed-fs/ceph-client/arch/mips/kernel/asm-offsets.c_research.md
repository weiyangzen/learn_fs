<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/asm-offsets.c

### Purpose
`asm-offsets.c` generates assembly-visible constants for MIPS kernel structures, signal numbers, page-table geometry, KVM FPU state, power-management state, and CPS boot configuration.

### Important APIs, Types, And Functions
The file defines `output_ptreg_defines()`, `output_task_defines()`, `output_thread_info_defines()`, `output_thread_defines()`, `output_thread_fpu_defines()`, `output_mm_defines()`, ABI-specific `output_sc_defines()`, `output_signal_defined()`, `output_octeon_cop2_state_defines()`, `output_pbe_defines()`, `output_pm_defines()`, `output_kvm_defines()`, and `output_cps_defines()`.

### Control Flow
During the build, kbuild compiles this file with `COMPILE_OFFSETS`; `OFFSET()` and `DEFINE()` emit constants derived from C structure layout. Conditional compilation emits only constants relevant to the enabled architecture features.

### State, Persistence, And Dependencies
The generated `asm-offsets.h` is build-time persistent state consumed by assembly. Dependencies include scheduler, mm, ptrace, processor, PM, SMP-CPS, KVM, signal, and page-table headers.

### Integration Points
Exception entry/exit assembly, context switching, signal trampolines, KVM assembly, Octeon COP2 save/restore, hibernation, CPU PM, and CPS boot vectors depend on these offsets.

### Risks
Any C structure layout change that is not reflected through generated offsets can break assembly silently if hard-coded constants exist elsewhere. Conditional offsets must match assembly conditional paths.

### Test Signals
Full MIPS build coverage across configs is the primary test. Runtime signals include successful boot, syscall/interrupt return, signal delivery/return, KVM context operations, CPU suspend/resume, and CPS SMP startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/asm-offsets.c -->
