# sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/por.h` Provides tiny Permission Overlay Register helpers used by pkey/PTE access checks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
POR_EL0_INIT, por_elx_allows_read(), por_elx_allows_write(), por_elx_allows_exec(). The file is 34 lines / 612 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Each helper extracts a 4-bit permission field for a pkey with POR_ELx_PERM_GET and tests the relevant R/W/X bit.

### State, Persistence, And Dependencies
No owned state; callers pass a POR register value read from hardware or initialized for a thread. Depends on sysreg POE encodings; integrated by pgtable.h access checks and pkey initialization paths.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect bit extraction or init permissions could silently allow or deny user memory access.

### Test Signals
Unit-style compile tests for all pkeys, POE selftests for read/write/exec faults, and regression checks around POR_EL0_INIT.
