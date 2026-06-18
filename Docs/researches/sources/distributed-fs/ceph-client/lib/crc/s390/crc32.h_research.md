# sources/distributed-fs/ceph-client/lib/crc/s390/crc32.h

## Purpose
This s390 arch header selects vector-accelerated CRC32 implementations when the Vector Extension Facility is present and the buffer is large enough.

## Important APIs, Types, and Functions
The main macro is `DEFINE_CRC32_VX()`, which generates `crc32_le_arch()`, `crc32_be_arch()`, and `crc32c_arch()`. It also defines constants `VX_MIN_LEN`, `VX_ALIGNMENT`, `VX_ALIGN_MASK`, and `crc32_optimizations_arch()`.

## Control Flow
Generated hooks fall back to software when the buffer is shorter than the vector threshold or `cpu_has_vx()` is false. Otherwise they process a prealignment fragment in software, enter a kernel FPU/vector section with `kernel_fpu_begin()`, call the relevant `*_vgfm_16()` routine on the aligned body, exit vector state, and process residual bytes in software.

## State and Persistence
State is local plus temporary vector/FPU save state declared on the stack. No persistent state is created.

## Dependencies and Integration Points
It depends on `linux/cpufeature.h`, `asm/fpu.h`, and declarations from `crc32-vx.h`. It plugs into the generic CRC32 library as s390 arch hooks.

## Risks and Test Signals
Risks include vector-state use in contexts where FPU is unavailable, alignment length arithmetic, and stale optimization bit reporting. Test signals are short/large/unaligned CRC32 and CRC32C KUnit cases on s390 with and without VX.
