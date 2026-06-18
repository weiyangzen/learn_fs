## sources/distributed-fs/ceph-client/arch/mips/kernel/syscall.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/syscall.c` implements MIPS-specific syscall wrappers and legacy `sysmips` operations. It handles unusual MIPS pipe return conventions, mmap offset validation, TLS setup, an atomic user memory operation, alignment-fixup flags, and cache flush requests.

### Important APIs, Types, And Functions
Entry points include `sysm_pipe()`, `SYSCALL_DEFINE6(mips_mmap)`, `SYSCALL_DEFINE6(mips_mmap2)`, `SYSCALL_DEFINE1(set_thread_area)`, `SYSCALL_DEFINE3(sysmips)`, and `SYSCALL_DEFINE3(cachectl)`. The internal helper `mips_atomic_set()` implements `MIPS_ATOMIC_SET`, with LL/SC assembly variants and a software fallback using `ll_bit` and `ll_task`.

### Control Flow
`sysm_pipe()` calls `do_pipe_flags()` and returns fd0 in `$v0` with fd1 in register `$v1`. mmap wrappers validate page offset alignment and call `ksys_mmap_pgoff()`. `set_thread_area()` stores TLS in `thread_info.tp_value` and writes CP0 UserLocal when available. `sysmips()` dispatches `MIPS_ATOMIC_SET`, `MIPS_FIXADE`, and `FLUSH_CACHE`; the atomic set writes the old value into `$v0`, clears error in `$a3`, and jumps to `syscall_exit`.

### State, Persistence, And Dependencies
State includes current pt_regs return registers, current thread TLS value, CP0 UserLocal, per-thread `TIF_FIXADE` and `TIF_LOGADE`, global cache state after flush, and user memory modified by `MIPS_ATOMIC_SET`. Dependencies include syscall core, user access helpers, MIPS LL/SC and EVA assembly helpers, `asm/sysmips.h`, `asm/cachectl.h`, and `ll_bit` state from trap LL/SC emulation.

### Integration Points
This file feeds MIPS syscall tables, interacts with `unaligned.c` through `TIF_FIXADE`, with `traps.c` through LL/SC emulation globals, with signal restart through saved static syscall functions, and with TLS/RDHWR support through `configure_hwrena()`.

### Risks
Inline assembly exception table entries must be correct or user faults can escape. `mips_atomic_set()` has nonstandard return control flow and must preserve static registers. Offset checks for mmap/mmap2 are ABI visible. The software atomic fallback is only a compatibility mechanism and depends on preemption and `ll_bit` semantics.

### Test Signals
Test `pipe()` return registers, `mmap` and `mmap2` invalid offsets, `set_thread_area` plus RDHWR UserLocal reads, `sysmips(MIPS_FIXADE)` behavior with unaligned accesses, `MIPS_ATOMIC_SET` success/fault/alignment cases, and cache flush dispatch.
