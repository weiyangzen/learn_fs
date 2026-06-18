# sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall.h` Defines arm64 syscall table ABI and helpers for syscall tracing, argument access, rollback, return values, and audit architecture. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
syscall_fn_t, sys_call_table, compat_sys_call_table, syscall_get_nr(), syscall_rollback(), syscall_get_return_value(), syscall_get_error(), syscall_set_return_value(), syscall_set_nr(), syscall_get/set_arguments(), syscall_get_arch(), syscall_trace_enter/exit(). The file is 126 lines / 2967 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Helpers read syscallno, orig_x0, and regs[1..5]; rollback restores x0 from orig_x0; compat return values are sign-extended or truncated as required. Setting nr to -1 skips the syscall and returns -ENOSYS explicitly.

### State, Persistence, And Dependencies
State is pt_regs syscall fields and task thread compatibility flags. Tables are global const dispatch arrays. Depends on audit, compat, err; integrates syscall entry/exit, ptrace, seccomp, audit, tracing, and compat syscalls.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
orig_x0 handling affects restart/rollback and tracing; compat sign extension is ABI critical; wrong audit arch breaks seccomp/audit filters.

### Test Signals
Run syscall selftests, ptrace syscall emulation, seccomp/audit, compat syscall return tests, and tracepoint checks.
