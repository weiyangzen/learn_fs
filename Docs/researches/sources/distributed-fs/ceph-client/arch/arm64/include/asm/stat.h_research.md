# sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stat.h` Defines arm64 compat stat64 layout while delegating native stat ABI to UAPI. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
uapi stat include, struct stat64 under CONFIG_COMPAT, STAT64_HAS_BROKEN_ST_INO. The file is 51 lines / 947 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow; compat syscall implementations copy to/from this fixed layout.

### State, Persistence, And Dependencies
State persists in userspace ABI buffers only. Depends on linux/time and asm/compat for compat types; integrates with stat/newfstatat compat syscalls and filesystem VFS copyout.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Layout and padding are ABI fixed; broken st_ino handling must match historical userspace expectations.

### Test Signals
Run compat stat syscall tests, structure-size checks, and filesystem metadata round trips.
