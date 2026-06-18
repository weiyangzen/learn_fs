# sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/shmparam.h` Defines shared-memory low-boundary alignment for arm64 and compat IPC. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
COMPAT_SHMLBA and asm-generic/shmparam include. The file is 17 lines / 425 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; generic IPC code uses constants during SHM attachment address selection.

### State, Persistence, And Dependencies
No local state; shared memory state is in IPC/mm subsystems. Integrates compat syscalls with generic shmparam behavior and page-size assumptions.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong compat alignment can break legacy 32-bit applications; page-size assumptions must match non-aliasing D-cache behavior.

### Test Signals
Run native and compat SYSV SHM attach tests on 4K/16K/64K configs.
