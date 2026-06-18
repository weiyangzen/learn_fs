# sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/resctrl.h` Connects arm64 resource-control plumbing to MPAM support. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
Includes linux/arm_mpam.h as the architecture resctrl surface. The file is 2 lines / 67 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No local control flow; all behavior is delegated to MPAM headers and implementation files.

### State, Persistence, And Dependencies
No local state; MPAM/resctrl state lives in subsystem structures and hardware registers. Integrates scheduler/resctrl policies with Arm Memory Partitioning and Monitoring when enabled.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Risk is mostly include-contract drift: if MPAM header shape changes, resctrl consumers may fail or miscompile.

### Test Signals
Build CONFIG_ARM64_MPAM/resctrl combinations and run resctrl/MPAM allocation tests where hardware or emulation exists.
