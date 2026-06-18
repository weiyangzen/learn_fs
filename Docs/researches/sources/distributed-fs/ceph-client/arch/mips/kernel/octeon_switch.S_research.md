<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/octeon_switch.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/octeon_switch.S

### Purpose
`octeon_switch.S` implements Cavium Octeon-specific context switching and coprocessor state save/restore. It saves normal thread state, optional CVMSEG state, COP2 crypto/CRC/LLM state, and Octeon multiplier state variants.

### Important APIs, Types, And Functions
Exported assembly functions include `resume`, `octeon_cop2_save`, `octeon_cop2_restore`, `octeon_mult_save`, `octeon_mult_save2`, `octeon_mult_save3`, `octeon_mult_restore`, `octeon_mult_restore2`, and `octeon_mult_restore3`, plus end labels used for patching/copying. It uses structure offsets such as `THREAD_STATUS`, `THREAD_CVMSEG`, `OCTEON_CP2_*`, `PT_MTP`, and `PT_MPL`.

### Control Flow
`resume(prev, next, next_ti)` saves CP0 status and nonscratch registers to the previous task, optionally copies user-enabled CVMSEG memory into thread storage and disables access, updates the stack canary on UP stack-protector builds, switches `$28` to the next thread info, restores nonscratch registers, updates saved SP, merges selected status bits, and returns the previous task. COP2 save/restore reads `CvmCtl` feature-disable bits, saves/restores CRC state, optional DFA/LLM state, optional crypto state, and selects pass1, later Octeon, or Octeon III register maps by processor ID. Multiplier save/restore has stub space and Octeon II/III variants.

### State, Persistence, And Dependencies
State is stored in task thread structs, pt_regs, CP0 status/CvmCtl/CvmMemCtl, CVMSEG memory, COP2 registers, and multiplier pseudo-registers. Dependencies include Octeon ISA, assembler offsets, stackframe macros, and CPU revision IDs.

### Integration Points
This file plugs into the MIPS scheduler switch path, Octeon COP2 lazy/context management, exception save/restore macros, and runtime patching of multiplier helpers.

### Risks
Register ordering and delay slots are critical. Missing a COP2 register corrupts crypto/hash state across context switches. CVMSEG copying depends on configured size and user-enable bit. Processor-ID conditionals must match Octeon pass-specific register layouts.

### Test Signals
Run context-switch stress on Octeon I/II/III, user CVMSEG tests, COP2 crypto/hash workloads across preemption, multiplier state tests, stack-protector canary checks on UP, and scheduler switch tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/octeon_switch.S -->
