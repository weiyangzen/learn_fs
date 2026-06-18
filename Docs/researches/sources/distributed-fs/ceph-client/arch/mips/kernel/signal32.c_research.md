## sources/distributed-fs/ceph-client/arch/mips/kernel/signal32.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal32.c` implements small 32-bit compatibility wrappers for classic signal syscalls on a 64-bit MIPS kernel. It translates compat signal action structures and delegates mask suspension to the generic compat realtime implementation.

### Important APIs, Types, And Functions
The file defines the 32-bit handler typedefs `__sighandler32_t` and `vfptr_t`. Runtime entry points are `sys32_sigsuspend()` and `SYSCALL_DEFINE3(32_sigaction, ...)`. The sigaction path uses `struct compat_sigaction`, `struct k_sigaction`, `old_sigset_t`, `do_sigaction()`, and compat-safe handler pointer conversion.

### Control Flow
`sys32_sigsuspend()` directly calls `compat_sys_rt_sigsuspend()` with a compat signal set size. `32_sigaction` validates and copies a 32-bit user action, sign-extends the handler through `s32` to a kernel pointer, converts the one-word legacy mask with `siginitset()`, calls `do_sigaction()`, and if requested writes the old action back in compat layout while zeroing unused mask words.

### State, Persistence, And Dependencies
No durable state is stored in this file. It mutates the current task's signal disposition through the generic signal core. The stable interface is the legacy 32-bit `sigaction` ABI layout and handler pointer representation. Dependencies include `linux/compat.h`, `asm/compat-signal.h`, `asm/syscalls.h`, `linux/uaccess.h`, and `signal-common.h`.

### Integration Points
This file complements `signal_o32.c`, which builds o32 signal frames and implements sigreturn. It plugs compat syscalls into the MIPS syscall table and relies on generic signal action storage for cross-ABI behavior.

### Risks
Pointer sign extension and mask copying are the main compatibility risks. Failing to zero unused mask words can expose stale data or confuse old user programs. Incorrect `access_ok()` coverage would turn user faults into kernel faults.

### Test Signals
Exercise compat `sigaction` install/query, NULL `act` and `oact` combinations, bad user pointers, high-bit handler addresses, legacy one-word masks, and `sigsuspend` interruption on o32/n32 compat tasks.
