## sources/distributed-fs/ceph-client/arch/loongarch/kernel/lbt.S

### Purpose
`lbt.S` provides low-level save, restore, initialization, and signal-context transfer helpers for the LoongArch Binary Translation extension state. It preserves scratch registers, x86 compatibility flags, and x87 top-of-stack metadata used by LBT-aware task switching, signal delivery, and ptrace-style context export.

### Important APIs, Types, And Functions
Exported symbols are `_save_lbt`, `_restore_lbt`, `_save_lbt_context`, `_restore_lbt_context`, `_save_ftop_context`, and `_restore_ftop_context`; `_init_lbt` is local architecture setup. The code uses `movscr2gr`, `movgr2scr`, `x86mfflag`, `x86mtflag`, `x86mftop`, and `x86mttop`, plus `THREAD_SCR*` and `THREAD_EFLAGS` offsets from `asm-offsets.h`. The `EX` macro wraps user-memory loads/stores with exception-table fixups that return `-EFAULT`.

### Control Flow
Thread save/restore paths copy `$scr0..$scr3` and flag state between hardware and `thread_struct`. User signal helpers copy the same state to user buffers with fault recovery. FTOP restore masks the requested value to three bits, jumps through an eight-entry inline table, executes the matching immediate `x86mttop`, then returns success. Any protected user access fault branches to `.L_lbt_fault` and returns `-EFAULT`.

### State, Persistence, And Dependencies
The persistent state is the per-task LBT snapshot in `thread_struct` and user signal-frame LBT context. Hardware state persists only while the task owns the LBT unit. The file depends on LoongArch LBT instructions, the exception table mechanism, thread offset definitions, and C wrappers in `signal.c` and `traps.c`.

### Integration Points
`process.c` duplicates and clears LBT state across fork/exec boundaries, `traps.c` lazily initializes/restores LBT on BTD exceptions, and `signal.c` uses the context helpers when building or restoring extended signal frames. The GPL exports are available to architecture code and modules that need LBT context management.

### Risks
The routines assume exact offsets and register widths; stale `asm-offsets.h` values would corrupt unrelated thread fields. FTOP restore is marked non-standard stack frame, so unwinder assumptions are limited. Signal-context helpers must fault safely on invalid user pointers, and any missing exception-table annotation would turn a recoverable bad frame into a kernel fault.

### Test Signals
Exercise LBT workloads across context switch, signal delivery, sigreturn, fork, and exec. Add invalid-user-frame sigreturn tests for `-EFAULT`, FTOP values 0-7 plus masked out-of-range values, and mixed FPU/LBT signal frames. Build tests should cover `CONFIG_CPU_HAS_LBT` and unwinder warnings.
