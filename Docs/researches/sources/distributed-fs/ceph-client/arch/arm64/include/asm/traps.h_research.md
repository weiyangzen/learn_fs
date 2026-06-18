# sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/traps.h` Declares arm64 trap, breakpoint, signal-injection, RAS SError severity, and MOPS register-repair helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
try_emulate_armv8_deprecated(), force_signal_inject(), arm64_notify_segfault(), arm64_force_sig_fault*(), arm64_force_sig_mceerr(), arm64_force_sig_ptrace_errno_trap(), bug/cfi/reserved/kasan/ubsan brk handlers, early_brk64(), dump_kernel_instr(), arm64_skip_faulting_instruction(), __in_irqentry_text(), in_entry_text(), arm64_is_ras_serror(), arm64_ras_serror_get_severity(), arm64_is_fatal_ras_serror(), arm64_serror_panic(), arm64_mops_reset_regs(). The file is 162 lines / 4850 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Trap handlers inspect ESR/pt_regs, may emulate deprecated instructions, deliver signals, skip faulting instructions, or panic on fatal RAS errors. MOPS reset decodes ESR option bits and rewinds PC/registers to a canonical prologue state after a fault in memory copy/set instructions.

### State, Persistence, And Dependencies
State is pt_regs/user_pt_regs mutated during exception handling and section-boundary symbols used for entry text checks. No independent persistent storage. Depends on list, esr, ptrace, sections, CPU RAS capabilities; integrates exception entry, signal delivery, BUG/CFI/KASAN/UBSAN breakpoints, MTE/MOPS, RAS, and oops handling.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
ESR decoding is security and reliability critical; wrong MOPS repair can resume with corrupted registers; preemptible RAS checks are forbidden because CPU capability is per-CPU.

### Test Signals
Run trap/signal selftests, deprecated instruction emulation, BUG/KASAN/UBSAN/LKDTM breakpoints, RAS SError injection, MOPS fault tests, and entry-text classification checks.
