<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/signal.c

### Purpose
`signal.c` implements PA-RISC signal delivery, realtime signal frames, `rt_sigreturn`, syscall restart handling, and user-mode resume work.

### Important APIs, Types, And Functions
Core functions are `sys_rt_sigreturn()`, `get_sigframe()`, `setup_sigcontext()`, `setup_rt_frame()`, `handle_signal()`, `check_syscallno_in_delay_branch()`, `syscall_restart()`, `insert_restart_trampoline()`, `do_signal()`, and `do_notify_resume()`.

### Control Flow
Signal return locates the upward-growing signal frame below the current stack pointer, restores signal mask, register context, and altstack, then fixes `gr31` for syscall-return paths. Delivery builds a native or compat rt frame, saves siginfo/ucontext/mask, resolves PA-RISC function descriptors for handlers, installs VDSO sigtramp/restart return pointers, sets handler arguments, and advances the upward-growing user stack. Syscall restart either converts restart errors to `-EINTR`, rewinds the gateway branch sequence, or plants a VDSO restart trampoline.

### State, Persistence, And Dependencies
State persists in user signal frames, saved masks, `restart_block`, `orig_r28`, and user-visible registers. Dependencies include compat signal helpers, VDSO offsets, PA-RISC function descriptors, delayed-branch syscall ABI, and generic signal core.

### Integration Points
Called from syscall/interrupt return paths and uses VDSO trampolines built under `vdso32` and `vdso64`.

### Risks
PA-RISC stacks grow upward, making frame bounds and altstack logic unusual. Restart logic decodes user instructions in syscall delay slots. Incorrect in-syscall handling can restore the wrong IAOQ or return pointer.

### Test Signals
Test native and compat signal delivery, altstack, handler descriptors, `rt_sigreturn`, interrupted syscalls with all restart classes, ptrace single-step into handlers, and VDSO trampoline unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal.c -->
