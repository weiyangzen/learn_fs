# sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/proc-fns.h` Declares low-level CPU idle, suspend, and resume assembly entry points. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct cpu_suspend_ctx forward declaration, cpu_do_idle(), cpu_do_suspend(), cpu_do_resume(). The file is 25 lines / 564 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Callers enter assembly routines to idle the CPU or save/restore CPU context around suspend/resume; this header only declares the ABI.

### State, Persistence, And Dependencies
State is CPU register/context memory passed by pointer and idmap TTBR values. The header itself owns no storage. Depends on asm/page.h and memory.h; used by cpuidle, PSCI/suspend, hibernation, and early MMU/idmap code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Prototype mismatch with proc.S corrupts saved state or resume address; incorrect idmap TTBR use can fail resume before normal mappings exist.

### Test Signals
Suspend/resume, CPU hotplug, hibernation, and cross-build checks against assembly symbol prototypes.
