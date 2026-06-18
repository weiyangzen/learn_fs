# sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/syscall_wrapper.h` Defines arm64 syscall definition wrappers that marshal pt_regs into typed syscall arguments and generate compat/native entry symbols. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
SC_ARM64_REGS_TO_ARGS, COMPAT_SYSCALL_DEFINEx/DEFINE0, COND_SYSCALL_COMPAT, __SYSCALL_DEFINEx, SYSCALL_DEFINE0, COND_SYSCALL, __arm64_sys_ni_syscall(). The file is 82 lines / 3163 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Wrapper macros create __arm64_sys* entry points taking pt_regs, call sign-extension/de-lousing shim functions, run argument tests/protection, then call __do_sys* typed implementations. Conditional syscalls weakly return sys_ni_syscall.

### State, Persistence, And Dependencies
No runtime state beyond generated functions and syscall table references. Depends on ptrace and generic syscall macro infrastructure; integrated by syscall implementation files and build-generated tables.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Macro argument order must match AAPCS syscall register convention; compat wrappers must de-louse 32-bit args; weak fallback symbols must match table names.

### Test Signals
Build syscall tables, run syscall ABI tests, compat syscalls, error injection metadata checks, and sparse/compile coverage for generated wrappers.
