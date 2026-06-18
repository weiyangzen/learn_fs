## sources/distributed-fs/ceph-client/arch/mips/power/cpu.c

### Purpose
This file saves and restores MIPS processor state across hibernation and marks the nosave memory range.

### Important APIs, Types, And Functions
State includes `saved_status` and global `saved_regs`, which assembly uses for callee-saved registers. `save_processor_state()` saves CP0 status, current FPU state if owned, and DSP state. `restore_processor_state()` restores CP0 status, FPU if owned, and DSP. `pfn_is_nosave()` checks PFNs against `__nosave_begin`/`__nosave_end`.

### Control Flow
Generic hibernation calls save before snapshot and restore after resume. Low-level assembly saves GPRs separately in `saved_regs`. PFN filtering excludes the nosave section from the image.

### State, Persistence, And Dependencies
Persistent hibernation state is saved CP0 status, saved registers, FPU/DSP state, and the nosave section boundaries. Dependencies include MIPS FPU/DSP helpers and linker section symbols.

### Integration Points
Works with `hibernate_asm.S` and generic swsusp memory image code.

### Risks
FPU restore is conditional on current ownership; ownership transitions during hibernation must be correct. Missing CPU extension state beyond FPU/DSP would not be preserved.

### Test Signals
Hibernate/resume with FPU and DSP workloads, verify CP0 status restoration, and confirm nosave pages are excluded.
