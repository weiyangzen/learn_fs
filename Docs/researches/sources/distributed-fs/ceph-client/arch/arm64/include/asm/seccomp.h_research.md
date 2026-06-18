# sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/seccomp.h` Defines arm64 seccomp audit architecture metadata and compat syscall numbers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__NR_seccomp_*_32 aliases, SECCOMP_ARCH_NATIVE*, SECCOMP_ARCH_COMPAT* constants, generic seccomp include. The file is 31 lines / 891 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow here; generic seccomp uses these constants to validate filter architecture and syscall numbers.

### State, Persistence, And Dependencies
No local state; filters persist in task seccomp state. Depends on unistd_compat_32, asm-generic/seccomp, audit arch constants; integrates with syscall entry, audit, ptrace, and compat tasks.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong audit arch or compat syscall constants could let filters match the wrong ABI or fail open/closed unexpectedly.

### Test Signals
Run seccomp selftests for native and compat tasks, audit arch checks, and CONFIG_COMPAT off builds.
