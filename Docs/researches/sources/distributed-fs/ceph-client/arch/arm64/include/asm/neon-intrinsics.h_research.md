# sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h

### Purpose
`neon-intrinsics.h` prepares compiler type definitions and includes `<arm_neon.h>` for kernel code that uses ARM64 NEON intrinsics.

### Important APIs, Types, And Functions
It adjusts `__INT64_TYPE__` and `__UINT64_TYPE__` around the compiler intrinsic header so kernel integer type expectations remain compatible.

### Control Flow
There is no runtime flow. It is include-time compatibility glue for C code compiled with NEON enabled.

### State, Persistence, And Dependencies
No state. It depends on compiler-provided `arm_neon.h` and kernel integer type definitions.

### Integration Points
Used by optimized crypto/checksum/SIMD routines that may serve networking and storage paths.

### Risks
Compiler intrinsic ABI drift can break builds. Kernel code must still bracket NEON use with proper FPSIMD ownership helpers.

### Test Signals
Build SIMD-using objects with GCC/Clang; run crypto/checksum tests; ensure no NEON use without `kernel_neon_begin/end`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/neon-intrinsics.h -->
