# sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/signal.h` Adds arm64 signal-address tag stripping rules before exposing si_addr to userspace. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
arch_untagged_si_addr(). The file is 25 lines / 650 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
For SIGTRAP/TRAP_BRKPT watchpoint-like cases it preserves all address bits for historical ABI; otherwise it returns untagged_addr(addr).

### State, Persistence, And Dependencies
No state; transforms signal metadata during delivery. Depends on memory.h and uapi signal/siginfo; integrates with MTE/tagged-address ABI, signal delivery, ptrace/debug exceptions.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong tag stripping changes userspace ABI or leaks tag bits inconsistently; watchpoint exception compatibility is special-case sensitive.

### Test Signals
Run signal/MTE/tagged-address selftests, watchpoint SIGTRAP tests, and compat signal delivery checks.
