# sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal32.h` Defines AArch32 compat signal frame layouts and setup entry points for arm64 compat tasks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct compat_sigcontext, compat_ucontext, compat_sigframe, compat_rt_sigframe, compat_setup_frame(), compat_setup_rt_frame(), compat_setup_restart_syscall(). The file is 81 lines / 1980 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
CONFIG_COMPAT builds populate legacy sigcontext/ucontext and retcode fields for 32-bit signal delivery. Non-compat builds return -ENOSYS stubs.

### State, Persistence, And Dependencies
Signal frame state persists on the user stack and forms a userspace ABI. Header owns no kernel storage. Depends on linux/compat; integrates with signal delivery, rt_sigreturn, ptrace, restart_syscall, and compat syscall ABI.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Struct layout, padding, alignment, and register order are ABI fixed; mistakes break 32-bit signal handlers or restarts.

### Test Signals
Run compat signal, rt_sigreturn, SA_RESTART, ptrace signal injection, and layout compile assertions where available.
