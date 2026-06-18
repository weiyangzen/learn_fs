# sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h

### Purpose
`neon.h` declares the safe kernel NEON/FPSIMD entry and exit API.

### Important APIs, Types, And Functions
It defines `cpu_has_neon()` as `system_supports_fpsimd()` and declares `kernel_neon_begin()` and `kernel_neon_end()`.

### Control Flow
Kernel code calls `kernel_neon_begin()` before using NEON registers and `kernel_neon_end()` afterward, allowing the FPSIMD subsystem to save/restore task state and manage preemption constraints.

### State, Persistence, And Dependencies
State is FPSIMD/NEON register ownership and optional saved `user_fpsimd_state`. It depends on `asm/fpsimd.h` and CPU feature detection.

### Integration Points
Used by crypto, RAID/checksum, compression, and other optimized routines that can affect filesystem/network throughput.

### Risks
Using NEON without bracketing corrupts user or guest FP state. Calling in invalid contexts can violate preemption/interrupt assumptions.

### Test Signals
Run crypto SIMD tests, preemption stress with NEON users, and KVM/FPSIMD state-switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon.h -->
