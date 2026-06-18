<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscall.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/syscall.S

### Purpose
`syscall.S` implements the PA-RISC Linux gateway page, regular syscall entry, ptrace-aware syscall dispatch, light-weight syscalls, syscall tables, and gateway-page lock table.

### Important APIs, Types, And Functions
Important labels include `linux_gateway_page`, `lws_entry`, `set_thread_pointer`, `linux_gateway_entry`, `syscall_nosys`, `tracesys`, `tracesys_exit`, `lws_start`, `lws_compare_and_swap32/64`, `lws_compare_and_swap_2`, `lws_atomic_xchg`, `lws_atomic_store`, `lws_table`, `sys_call_table`, `sys_call_table64`, and `lws_lock_start`.

### Control Flow
Userland enters the gateway page at fixed offsets. The syscall entry promotes privilege, switches space registers, handles 64-bit wide-mode/compat argument clipping, saves syscall state into `task->thread.regs`, saves FP/SAR state, chooses native or compat syscall tables, and branches to the syscall with a return pointer to `syscall_exit` or `syscall_exit_rfi`. The trace path saves a fuller register image, calls `do_syscall_trace_enter()`, dispatches or skips, then calls `do_syscall_trace_exit()`. LWS operations run on the gateway page without switching address spaces, validate arguments, hash the user address to an aligned lock, disable interrupts and page faults for critical sections, use exception table entries for user faults, and return errno/retry reason in PA-RISC ABI registers.

### State, Persistence, And Dependencies
Persistent state includes saved task registers, `cr27` thread pointer, generated syscall tables, and the 256-entry LWS lock table. Dependencies include `entry.S` return paths, ptrace/seccomp C helpers, generated syscall headers, exception table offsets relative to `linux_gateway_page`, and PA-RISC gateway privilege semantics.

### Integration Points
This is the central interface between userspace and the kernel, glibc fixed gateway offsets, VDSO trampolines, signal restart, ptrace, and atomic user helpers.

### Risks
Fixed offsets at `0xb0`, `0xe0`, and `0x100` are ABI. Register save/restore must match `pt_regs`, signal, ptrace, and syscall restart code. LWS critical sections must not sleep and must always release locks/pagefault disable state on every fault path.

### Test Signals
Run native and compat syscall suites, ptrace/seccomp/audit tracing, `rt_sigreturn` from syscall and interrupt contexts, glibc thread-pointer setup, LWS CAS/exchange/store success and EFAULT/EAGAIN paths, and syscall table generation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscall.S -->
