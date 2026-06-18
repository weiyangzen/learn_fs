# sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/simd.h` Controls safe use of kernel-mode SIMD/FPSIMD/NEON and provides scoped guard helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
may_use_simd(), DEFINE_LOCK_GUARD_1(ksimd), scoped_ksimd(). The file is 60 lines / 1484 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
may_use_simd checks finalized CPU capabilities, FPSIMD support, and excludes hardirq/NMI context. scoped_ksimd wraps kernel_neon_begin/end around a temporary user_fpsimd_state buffer.

### State, Persistence, And Dependencies
State affected is current task/kernel FPSIMD save area while inside guarded SIMD sections. Header owns no storage. Depends on cleanup, irqflags, percpu, preempt, neon; integrates crypto, RAID/checksum, compression, and other kernel NEON users.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Using SIMD in hardirq/NMI or before capability finalization can corrupt user FPSIMD state; callers must not assume may_use_simd remains true after preemption changes.

### Test Signals
Run kernel NEON users under preemption/softirq stress, crypto selftests, FPSIMD context-switch tests, and CONFIG_KERNEL_MODE_NEON off builds.
