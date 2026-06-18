# sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp_plat.h` Provides platform SMP helpers for MPIDR hashing and logical CPU lookup. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct mpidr_hash, extern mpidr_hash, mpidr_hash_size(), get_logical_index(). The file is 44 lines / 824 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
get_logical_index linearly scans possible CPUs and compares cpu_logical_map(cpu) to the requested MPIDR.

### State, Persistence, And Dependencies
Persistent state is global mpidr_hash and __cpu_logical_map from smp.h. Depends on cpumask, smp, types; used by CPU topology, boot CPU discovery, and platform CPU operations.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
MPIDR map collisions or stale logical maps break CPU bring-up and affinity reporting; linear lookup assumes nr_cpu_ids is initialized.

### Test Signals
Boot multi-cluster systems, validate logical map against firmware tables, CPU hotplug, and topology dumps.
