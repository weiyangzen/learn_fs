# subset-b-006081 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crct10dif-vpmsum_asm.S -->
# sources/distributed-fs/ceph-client/lib/crc/powerpc/crct10dif-vpmsum_asm.S

## Purpose
This PowerPC assembly file provides the vector polynomial multiply-sum accelerated CRC-T10DIF implementation used by the CRC library on capable PPC systems. It is almost entirely constant material plus an inclusion of `crc-vpmsum-template.S`, specializing that shared template as `__crct10dif_vpmsum` for the T10DIF 16-bit polynomial `0x8bb7`.

## Important APIs, Types, and Functions
The exported code entry is generated through `#define CRC_FUNCTION_NAME __crct10dif_vpmsum` followed by `#include "crc-vpmsum-template.S"`. Local data includes `.byteswap_constant`, the long `.constants` ladder for reducing large bit ranges, `.short_constants` for final 1024-to-64-bit folding, and `.barrett_constants` for the final modular reduction.

## Control Flow
There is no hand-written function body here. The included template consumes the aligned constant tables, performs byte swapping as needed, folds large input blocks with VPMSUM, folds the residual polynomial through shorter constants, then uses Barrett reduction to produce the 16-bit T10DIF result.

## State and Persistence
All state is CPU register/vector-register state during a checksum call. The file contributes immutable `.rodata` constants only; no persistent or global mutable state is introduced.

## Dependencies and Integration Points
It depends on PowerPC vector/crypto assembly support and the generic PowerPC CRC VPMSUM template. It integrates with the PPC CRC-T10DIF arch selector elsewhere in the CRC library, which chooses this implementation only when the needed CPU facility is available.

## Risks and Test Signals
Risks concentrate in constant correctness, byte-order handling, alignment assumptions from the shared template, and template ABI drift. Strong test signals are CRC-T10DIF vectors over short, unaligned, and large buffers, cross-checks against `crc_t10dif_generic()`, and KUnit/random CRC coverage on PPC builds with VPMSUM enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/powerpc/crct10dif-vpmsum_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-consts.h -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-consts.h

## Purpose
This generated header supplies RISC-V scalar carryless-multiply constants for CRC-16/T10DIF, CRC-32 IEEE, CRC-32C, CRC-64 ECMA, and CRC-64 NVMe. It is data-only support for the Zbc-based template in `crc-clmul-template.h`.

## Important APIs, Types, and Functions
The central type is `struct crc_clmul_consts` with two fold-across-two-longs constants and two Barrett reduction constants. It defines `crc16_msb_0x8bb7_consts`, `crc32_msb_0x04c11db7_consts`, `crc32_lsb_0xedb88320_consts`, `crc32_lsb_0x82f63b78_consts`, and, under `CONFIG_64BIT`, `crc64_msb_0x42f0e1eba9ea3693_consts` and `crc64_lsb_0x9a6c9329ac4bc9b5_consts`.

## Control Flow
There is no executable flow. Including CRC headers pass the relevant constant object into `crc*_clmul()` functions. The values differ for 32-bit and 64-bit RISC-V where the long-width fold distances and Barrett constants differ.

## State and Persistence
The constants are static immutable data marked `__maybe_unused` so the compiler can discard variants unused by a given translation unit. No runtime state exists.

## Dependencies and Integration Points
It depends on Linux types/macros and on the generator script contract documented in the header comment. It is included by `crc-clmul.h` and indirectly by RISC-V CRC arch headers.

## Risks and Test Signals
Manual edits would be risky because the constants encode polynomial arithmetic. Test signals include generator reproducibility, 32-bit versus 64-bit build coverage, and randomized CRC KUnit comparisons for all CRC variants that reference the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-consts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-template.h -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-template.h

## Purpose
This header is a C template that generates RISC-V Zbc scalar carryless-multiply CRC implementations for a caller-selected CRC width and bit order. Including files define `crc_t` and `LSB_CRC`, then get inline helpers plus the `crc_clmul()` engine.

## Important APIs, Types, and Functions
Key helpers are inline wrappers around `clmul`, `clmulh`, and `clmulr`, `crc_load_long()`, `crc_clmul_prep()`, `crc_clmul_long()`, `crc_clmul_update_long()`, `crc_clmul_update_partial()`, and `crc_clmul()`. It consumes `struct crc_clmul_consts` from `crc-clmul-consts.h`.

## Control Flow
`crc_clmul()` first aligns the buffer to `sizeof(unsigned long)` using partial-byte updates. Large buffers use a two-long folding loop that carries two polynomial accumulators, folds with precomputed constants, and consumes two longs per iteration. Remaining full longs are reduced one at a time, and any tail bytes are handled by `crc_clmul_update_partial()`. Final reductions use Barrett arithmetic specialized for reflected and non-reflected CRCs.

## State and Persistence
All state is local to the checksum call: the input pointer, length, current CRC value, temporary message polynomial, and fold accumulators. There is no global state, locking, or persistence.

## Dependencies and Integration Points
It depends on RISC-V inline assembly with `.option arch,+zbc`, Linux byte-order helpers, `BITS_PER_LONG`, and `BUILD_BUG_ON`. It is instantiated by the RISC-V CRC wrapper C files for 16-, 32-, and 64-bit CRCs.

## Risks and Test Signals
Risks include subtle polynomial bit-order mistakes, wrong tail handling when `len < sizeof(crc_t)`, alignment pointer arithmetic on `const void *`, and compiler/assembler support for Zbc inline asm. Test signals are random alignment and length vectors, zero-length calls, 32-bit RISC-V builds, 64-bit CRC builds, interrupt-context KUnit coverage, and comparison to generic table/bit implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul.h -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul.h

## Purpose
This header declares the RISC-V Zbc carryless-multiply CRC entry points and exposes the generated constant objects to arch selectors.

## Important APIs, Types, and Functions
It declares `crc16_msb_clmul()`, `crc32_msb_clmul()`, `crc32_lsb_clmul()`, and, under `CONFIG_64BIT`, `crc64_msb_clmul()` and `crc64_lsb_clmul()`. Each accepts an initial CRC, buffer pointer, length, and `struct crc_clmul_consts *`.

## Control Flow
There is no control flow beyond include guards. Callers choose which function and constant set to use based on CRC variant and CPU feature detection.

## State and Persistence
The header defines no state. It links translation units together through declarations.

## Dependencies and Integration Points
It depends on `linux/types.h` and `crc-clmul-consts.h`. It is the shared interface between RISC-V arch selector headers and the C files that instantiate `crc-clmul-template.h`.

## Risks and Test Signals
Risks are ABI/signature mismatches between declarations and generated functions, and accidentally exposing 64-bit CRC functions on 32-bit builds. Test signals include allmodconfig-style compile coverage and link checks for CRC32/T10DIF/CRC64 modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-t10dif.h

## Purpose
This arch header wires the generic CRC-T10DIF library to the RISC-V Zbc implementation when the CPU likely supports scalar carryless multiplication.

## Important APIs, Types, and Functions
The single public hook is `static inline u16 crc_t10dif_arch(u16 crc, const u8 *p, size_t len)`. It calls `crc16_msb_clmul()` with `crc16_msb_0x8bb7_consts` or falls back to `crc_t10dif_generic()`.

## Control Flow
At each call, `riscv_has_extension_likely(RISCV_ISA_EXT_ZBC)` gates the accelerated path. If false, execution immediately delegates to the generic CRC-T10DIF code.

## State and Persistence
No per-call state persists. CPU feature state is maintained by the RISC-V hwcap/alternative framework outside this header.

## Dependencies and Integration Points
It includes `asm/hwcap.h`, `asm/alternative-macros.h`, and `crc-clmul.h`. It is pulled into the generic CRC-T10DIF library as its RISC-V arch override.

## Risks and Test Signals
Risks are feature-detection false positives, missing Zbc assembler support, and divergence from generic T10DIF on unaligned buffers. Test signals include booting on RISC-V with and without Zbc and KUnit CRC-T10DIF comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc16_msb.c -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc16_msb.c

## Purpose
This file instantiates the RISC-V carryless-multiply template for a most-significant-bit-first 16-bit CRC, used by CRC-T10DIF.

## Important APIs, Types, and Functions
It sets `typedef u16 crc_t` and `#define LSB_CRC 0`, includes `crc-clmul-template.h`, and defines `u16 crc16_msb_clmul(...)`.

## Control Flow
The wrapper simply returns `crc_clmul(crc, p, len, consts)`. The template handles alignment, full-long folding, partial tails, and reduction.

## State and Persistence
No state persists beyond stack/register temporaries in the checksum call.

## Dependencies and Integration Points
It depends on `crc-clmul.h` and the template. `crc-t10dif.h` calls this function when Zbc is present.

## Risks and Test Signals
Risks are template parameter drift and incorrect polynomial constants supplied by callers. CRC-T10DIF KUnit, known-vector tests, and builds with `CONFIG_CRC_T10DIF` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc16_msb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc32.h

## Purpose
This arch header connects the generic CRC32 library to RISC-V Zbc implementations for CRC32 little-endian, CRC32 big-endian, and CRC32C.

## Important APIs, Types, and Functions
It defines `crc32_le_arch()`, `crc32_be_arch()`, `crc32c_arch()`, and `crc32_optimizations_arch()`. Accelerated calls use `crc32_lsb_clmul()` for IEEE reflected and Castagnoli reflected CRCs and `crc32_msb_clmul()` for big-endian CRC32.

## Control Flow
Each checksum hook gates on `riscv_has_extension_likely(RISCV_ISA_EXT_ZBC)`. Positive checks use the matching CLMUL function and constants; otherwise the hook calls the base/generic CRC implementation. `crc32_optimizations_arch()` returns the bitmask of all three optimizations when Zbc is available.

## State and Persistence
No local persistent state exists. CPU feature state is external.

## Dependencies and Integration Points
It depends on RISC-V hwcap helpers and the shared `crc-clmul.h` interface. It is included by the generic CRC32 implementation to override weak/base hooks.

## Risks and Test Signals
Risks include wrong reflected/non-reflected constant selection, incorrect optimization reporting, and runtime feature gating mismatches on alternatives. Test signals include KUnit CRC32/CRC32C tests, `/proc/crypto` or module optimization reporting if exposed, and cross-checks on Zbc and non-Zbc systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_lsb.c -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_lsb.c

## Purpose
This file instantiates the RISC-V CLMUL template for reflected/least-significant-bit-first 32-bit CRCs, covering CRC32 LE and CRC32C through different constants.

## Important APIs, Types, and Functions
It defines `crc_t` as `u32`, sets `LSB_CRC` to `1`, includes the template, and exports the callable function `crc32_lsb_clmul()`.

## Control Flow
`crc32_lsb_clmul()` delegates all logic to `crc_clmul()`. The caller determines whether the IEEE or Castagnoli constant set is passed.

## State and Persistence
All state is local to the checksum computation.

## Dependencies and Integration Points
It is linked into RISC-V CRC32 support and used by `crc32_le_arch()` and `crc32c_arch()`.

## Risks and Test Signals
Risks are reflected-tail math regressions in the shared template and incorrect constant selection by callers. KUnit CRC32 LE and CRC32C vectors with varied alignment are the key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_lsb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_msb.c -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_msb.c

## Purpose
This file instantiates the RISC-V CLMUL template for non-reflected/most-significant-bit-first 32-bit CRC32.

## Important APIs, Types, and Functions
It sets `crc_t` to `u32`, `LSB_CRC` to `0`, includes `crc-clmul-template.h`, and defines `crc32_msb_clmul()`.

## Control Flow
The wrapper calls `crc_clmul()` with the supplied constants. The shared template manages byte-order loads with big-endian interpretation for MSB-first CRCs.

## State and Persistence
No persistent state is present.

## Dependencies and Integration Points
It backs `crc32_be_arch()` in the RISC-V CRC32 header.

## Risks and Test Signals
Risks include byte-order mistakes and MSB-first partial-byte update errors. Test signals include CRC32 BE KUnit cases and comparison against `crc32_be_base()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_msb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc64.h -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc64.h

## Purpose
This arch header provides RISC-V Zbc acceleration hooks for CRC64 BE and CRC64 NVMe.

## Important APIs, Types, and Functions
It defines `crc64_be_arch()` and `crc64_nvme_arch()`. They call `crc64_msb_clmul()` with the ECMA polynomial constants or `crc64_lsb_clmul()` with the NVMe reflected constants when Zbc is likely present.

## Control Flow
Each hook performs a runtime Zbc feature check and either dispatches to the CLMUL function or falls back to `crc64_be_generic()`/`crc64_nvme_generic()`.

## State and Persistence
No mutable state is introduced. Feature state is handled by RISC-V CPU capability code.

## Dependencies and Integration Points
It depends on 64-bit RISC-V declarations from `crc-clmul.h`; the corresponding constant objects are only defined under `CONFIG_64BIT`.

## Risks and Test Signals
Risks include accidental use in 32-bit builds, reflected NVMe inversion convention mismatches, and runtime feature misdetection. CRC64 KUnit random tests, especially CRC64 NVMe wrapper tests, are the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_lsb.c -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_lsb.c

## Purpose
This file instantiates the RISC-V CLMUL template for reflected 64-bit CRCs, specifically the CRC64 NVMe path.

## Important APIs, Types, and Functions
It uses `typedef u64 crc_t`, `#define LSB_CRC 1`, includes the template, and defines `crc64_lsb_clmul()`.

## Control Flow
The wrapper returns `crc_clmul(crc, p, len, consts)`, with all actual folding and reduction in the template.

## State and Persistence
No persistent state exists.

## Dependencies and Integration Points
It is compiled only where 64-bit RISC-V CRC64 support is available and is called by `crc64_nvme_arch()`.

## Risks and Test Signals
Risks are reflected 64-bit polynomial reductions and ABI availability under `CONFIG_64BIT`. CRC64 NVMe KUnit coverage and large-buffer tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_lsb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_msb.c -->
# sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_msb.c

## Purpose
This file instantiates the RISC-V CLMUL template for non-reflected 64-bit CRC64 BE.

## Important APIs, Types, and Functions
It defines `crc_t` as `u64`, sets `LSB_CRC` to `0`, includes the template, and exposes `crc64_msb_clmul()`.

## Control Flow
`crc64_msb_clmul()` is a thin wrapper over `crc_clmul()`.

## State and Persistence
All computation state is local.

## Dependencies and Integration Points
It integrates with `crc64_be_arch()` and the ECMA polynomial constants from `crc-clmul-consts.h`.

## Risks and Test Signals
Risks include MSB-first endianness, long-width assumptions, and CRC64 constant mismatch. CRC64 BE KUnit and generic cross-checks validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_msb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32-vx.h -->
# sources/distributed-fs/ceph-client/lib/crc/s390/crc32-vx.h

## Purpose
This small header declares the s390 z/Architecture Vector Extension Facility CRC32 assembly/C entry points.

## Important APIs, Types, and Functions
It declares `crc32_be_vgfm_16()`, `crc32_le_vgfm_16()`, and `crc32c_le_vgfm_16()`, all accepting an initial CRC, byte buffer, and size.

## Control Flow
No executable flow exists. The arch selector in `crc32.h` calls these functions after alignment and vector-state setup.

## State and Persistence
The header carries no state.

## Dependencies and Integration Points
It depends on `linux/types.h` and is shared by s390 CRC32 selector and vector implementation files.

## Risks and Test Signals
Risks are declaration/definition mismatches and wrong variant wiring. Compile/link tests plus CRC32 KUnit on s390 VX systems are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32-vx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32be-vx.c -->
# sources/distributed-fs/ceph-client/lib/crc/s390/crc32be-vx.c

## Purpose
This file implements the big-endian/non-reflected CRC32 vector algorithm for s390 using vector Galois-field multiply instructions.

## Important APIs, Types, and Functions
It defines a static `constants_CRC_32_BE` table and the callable function `u32 crc32_be_vgfm_16(u32 crc, unsigned char const *buf, size_t size)`.

## Control Flow
The function loads constants into vector registers, seeds V0 with the initial CRC in the leftmost word, loads the first 64-byte chunk, then repeatedly folds 64-byte blocks using `fpu_vgfmag()`. It folds V1-V4 into one 128-bit value, consumes remaining 16-byte chunks, reduces 128 bits to 96 then 64 bits, and applies Barrett reduction to return a 32-bit CRC.

## State and Persistence
All state is in vector registers during a caller-managed FPU section. The constant table is immutable static data.

## Dependencies and Integration Points
It depends on `asm/fpu.h` vector helper intrinsics and is called by the wrapper generated in s390 `crc32.h`.

## Risks and Test Signals
Risks include vector register convention mistakes, constants loaded in the wrong order, missing caller alignment/size assumptions, and final-word extraction errors. CRC32 BE KUnit vectors, large-buffer folding tests, and s390 VX build coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32be-vx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32le-vx.c -->
# sources/distributed-fs/ceph-client/lib/crc/s390/crc32le-vx.c

## Purpose
This file implements reflected/little-endian CRC32 and CRC32C vector algorithms for s390 VX.

## Important APIs, Types, and Functions
It defines `constants_CRC_32_LE`, `constants_CRC_32C_LE`, a shared `crc32_le_vgfm_generic()`, and wrappers `crc32_le_vgfm_16()` and `crc32c_le_vgfm_16()`.

## Control Flow
The generic function loads the selected constants, byte-permutes input vectors to the expected order, seeds the rightmost word with the CRC, folds 64-byte chunks into four accumulators, reduces to 128 then 64 bits, applies final 32-bit folding with R5, and performs Barrett reduction. Wrappers pass the IEEE or Castagnoli constant table.

## State and Persistence
Mutable state is entirely vector-register local. The two constant tables are immutable.

## Dependencies and Integration Points
It depends on the s390 FPU/vector helper layer. It is invoked from the s390 arch CRC32 wrapper after vector-state entry.

## Risks and Test Signals
Risks include byte-permutation errors for reflected CRCs, using the wrong constant table, and size assumptions inherited from the caller. CRC32 LE, CRC32C, alignment, and large-buffer KUnit tests on s390 VX are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/s390/crc32le-vx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/sparc/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/sparc/crc32.h

## Purpose
This SPARC arch header enables CRC32C acceleration on sparc64 CPUs that advertise the crypto facility and CRC32C opcode.

## Important APIs, Types, and Functions
It declares static key `have_crc32c_opcode`, maps CRC32 LE/BE to base implementations, declares `crc32c_sparc64()`, defines `crc32c_arch()`, `crc32_mod_init_arch()`, and `crc32_optimizations_arch()`.

## Control Flow
`crc32c_arch()` checks the static key, aligns the buffer to 8 bytes with the base implementation, calls `crc32c_sparc64()` on the aligned 8-byte body, then processes any tail in software. Module init checks `HWCAP_SPARC_CRYPTO` and ASR26 `CFR_CRC32C` before enabling the static key.

## State and Persistence
Persistent runtime state is a read-mostly static key indicating opcode availability. Per-call CRC state remains local.

## Dependencies and Integration Points
It depends on SPARC pstate/ELF hwcap definitions and the assembly routine in `crc32c_asm.S`. It plugs into generic CRC32 hooks only for CRC32C.

## Risks and Test Signals
Risks include ASR feature probing failures, static-key state before init, alignment arithmetic, and only accelerating CRC32C while CRC32 LE/BE remain base. Test signals include boot logs, KUnit CRC32C tests on sparc64 crypto-capable CPUs, and fallback coverage on older CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/sparc/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/sparc/crc32c_asm.S -->
# sources/distributed-fs/ceph-client/lib/crc/sparc/crc32c_asm.S

## Purpose
This assembly file implements the SPARC64 CRC32C opcode loop used by `crc32c_arch()`.

## Important APIs, Types, and Functions
It defines `ENTRY(crc32c_sparc64)`, with arguments `%o0=crc32p`, `%o1=data_ptr`, and `%o2=len`. It uses `VISEntryHalf`/`VISExitHalf` and the `CRC32C` opcode macro.

## Control Flow
The function loads the current CRC into a floating/vector register, loops over 8-byte chunks with `ldd`, applies the CRC32C opcode, decrements length by 8, advances the pointer, stores the final CRC back, and returns.

## State and Persistence
The only state is the inout CRC word pointed to by `%o0` and transient VIS/FPU state managed by entry/exit macros.

## Dependencies and Integration Points
It depends on SPARC opcode, VIS, ASI, and linkage headers. The C header ensures it is called only on aligned 8-byte bodies after feature detection.

## Risks and Test Signals
Risks include VIS state handling, length not being a multiple of 8 if the caller changes, and endian/ASI load-store semantics. CRC32C KUnit and stress tests in interrupt/task contexts are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/sparc/crc32c_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/tests/Makefile -->
# sources/distributed-fs/ceph-client/lib/crc/tests/Makefile

## Purpose
This Makefile builds the CRC KUnit test module/object when `CONFIG_CRC_KUNIT_TEST` is enabled.

## Important APIs, Types, and Functions
It contains one build rule: `obj-$(CONFIG_CRC_KUNIT_TEST) += crc_kunit.o`.

## Control Flow
Kbuild includes `crc_kunit.o` conditionally based on the Kconfig symbol.

## State and Persistence
No state exists.

## Dependencies and Integration Points
It integrates the CRC test suite under the kernel KUnit build system and depends on the surrounding lib/crc test Kconfig.

## Risks and Test Signals
The main risk is the test not being built due to a symbol mismatch. Test signal is that enabling `CONFIG_CRC_KUNIT_TEST` produces and runs the `crc` KUnit suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/tests/crc_kunit.c -->
# sources/distributed-fs/ceph-client/lib/crc/tests/crc_kunit.c

## Purpose
This file provides generic KUnit tests and optional benchmarks for CRC library functions, including CRC7, CRC16, T10DIF, CRC32, CRC32C, CRC64 BE, and CRC64 NVMe.

## Important APIs, Types, and Functions
Important state and types include `struct crc_variant`, global PRNG state `rng`, `test_buffer`, and `test_buflen`. Key helpers are `crc_ref()`, `crc_suite_init()`, `crc_suite_exit()`, `generate_random_initial_crc()`, `generate_random_length()`, `crc_interrupt_context_test()`, `crc_test()`, and `crc_benchmark()`. Wrapper functions adapt public CRC APIs to the uniform `u64 (*)(u64,const u8*,size_t)` signature.

## Control Flow
Suite init allocates a page-rounded vmalloc buffer so overreads hit a guard page, seeds deterministic random data, and each enabled CRC variant runs 1000 randomized tests. Each test picks an initial CRC, random length, and random offset, sometimes placing the input adjacent to the guard page, then compares the implementation to a bit-at-a-time reference. It also runs concurrent task/softirq/hardirq context checks. Benchmarks run only under `CONFIG_CRC_BENCHMARK`.

## State and Persistence
The buffer and PRNG state live for the suite lifetime and are released in suite exit. No persistent data is written.

## Dependencies and Integration Points
It depends on KUnit, `kunit_run_irq_test()`, Linux CRC headers, PRNG, vmalloc, and optional CRC Kconfig symbols. It is the main cross-arch signal for the accelerated implementations in this subset.

## Risks and Test Signals
Risks include the reference implementation itself being wrong for a variant convention, deterministic random coverage missing specific thresholds, and benchmark code perturbing timing. Its strongest signals are guard-page tail tests, random alignment/length coverage, and interrupt-context validation for SIMD/FPU-safe accelerated code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/tests/crc_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-consts.h -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-consts.h

## Purpose
This generated header defines the x86 [V]PCLMULQDQ constant tables used to fold and reduce CRC16/T10DIF, CRC32, CRC32C, CRC64 BE, and CRC64 NVMe.

## Important APIs, Types, and Functions
It defines static cacheline-aligned constant structs for `crc16_msb_0x8bb7_consts`, `crc32_lsb_0xedb88320_consts`, `crc32_lsb_0x82f63b78_consts`, `crc64_msb_0x42f0e1eba9ea3693_consts`, and `crc64_lsb_0x9a6c9329ac4bc9b5_consts`. Fields include optional `bswap_mask`, fold constants for 2048/1024/512/256/128-bit distances, a shuffle table for short tails, and Barrett reduction constants.

## Control Flow
There is no code flow. Runtime x86 CRC hooks pass pointers to the `fold_across_128_bits_consts` field; the assembly template relies on fixed negative and positive offsets from that field to access neighboring constants.

## State and Persistence
The constants are immutable static data. No mutable state exists.

## Dependencies and Integration Points
It depends on the exact layout expected by `crc-pclmul-template.S` and on generated polynomial constants from `scripts/gen-crc-consts.py`. It is included by `crc-pclmul-template.h`.

## Risks and Test Signals
Risks include struct layout drift, generator mistakes, and mismatch between constant order and assembly offset assumptions. Test signals are x86 CRC KUnit across SSE, AVX2, and AVX512 dispatch paths plus build tests with all accelerated CRC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-consts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.S -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.S

## Purpose
This assembly template generates x86 PCLMULQDQ/VPCLMULQDQ CRC functions for different CRC widths, bit orders, and vector widths. It emits SSE, AVX2, and AVX512 implementations from one macro body.

## Important APIs, Types, and Functions
Major macros include `_cond_vex`, `_vbroadcast`, `_load_data`, `_prepare_v0`, `_pclmulqdq`, `_fold_vec`, `_fold_vec_mem`, `_load_vec_folding_consts`, `_fold_vec_final`, `_crc_pclmul`, and `DEFINE_CRC_PCLMUL_FUNCS`. Generated functions are named `<prefix>_pclmul_sse`, `<prefix>_vpclmul_avx2`, and `<prefix>_vpclmul_avx512`.

## Control Flow
Generated functions require at least 16 bytes of input. They seed a vector with the initial CRC, optionally byte-swap lanes for MSB-first CRCs, process data in vector-sized chunks, use folding constants to reduce across 128/256/512/1024/2048-bit distances, fold final vector lanes down to 128 bits, handle short residual bytes through shuffle masks, and run Barrett reduction to return the CRC width requested by the instantiator.

## State and Persistence
Only vector registers, general registers, and stack/register save state are used during the call. There is no global mutable state in this file.

## Dependencies and Integration Points
It depends on x86 assembler support for SSE/PCLMUL, AVX2/VPCLMUL, and AVX512 variants, Linux linkage annotations, objtool annotations, and the constant layout from `crc-pclmul-consts.h`. The C template header dispatches to the generated functions through static calls inside `kernel_fpu_begin()` sections.

## Risks and Test Signals
Risks include vector-state ABI misuse, incorrect non-VEX emulation, short-tail shuffle bugs, i386 register convention mistakes, and AVX512 dispatch on CPUs that prefer YMM. CRC KUnit with forced CPU feature variants, objtool validation, and interrupt-context tests are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.h -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.h

## Purpose
This C header declares and dispatches x86 [V]PCLMUL CRC functions generated by the assembly template.

## Important APIs, Types, and Functions
It defines `DECLARE_CRC_PCLMUL_FUNCS(prefix, crc_t)`, `have_vpclmul()`, `have_avx512()`, and the `CRC_PCLMUL()` macro. It includes CPU feature, FPU, static-call, and constant definitions.

## Control Flow
`CRC_PCLMUL()` checks length >= 16, a static key for PCLMUL availability, and `irq_fpu_usable()`. If all pass, it enters a kernel FPU section, calls the selected static-call target with the constant pointer, exits FPU state, and returns the updated CRC. Init hooks in CRC-specific headers update the static call to AVX2 or AVX512 variants when supported.

## State and Persistence
Persistent state is held in caller-defined static keys and static-call targets. This header itself defines only inline feature predicates and macros.

## Dependencies and Integration Points
It depends on `crc-pclmul-consts.h`, x86 CPU feature APIs, FPU availability checks, and Linux static calls. It is included by x86 CRC16/T10DIF, CRC32, and CRC64 arch headers.

## Risks and Test Signals
Risks include entering FPU state in unusable contexts, stale static-call target selection, and AVX feature checks not matching actual XSAVE state. KUnit interrupt-context tests and x86 feature-matrix boot tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-t10dif.h -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc-t10dif.h

## Purpose
This x86 arch header accelerates CRC-T10DIF with PCLMULQDQ or VPCLMULQDQ when available.

## Important APIs, Types, and Functions
It defines static key `have_pclmulqdq`, declares generated `crc16_msb` functions via `DECLARE_CRC_PCLMUL_FUNCS`, defines `crc_t10dif_arch()`, and provides `crc_t10dif_mod_init_arch()`.

## Control Flow
`crc_t10dif_arch()` uses `CRC_PCLMUL()` with `crc16_msb_0x8bb7_consts`; fallback is `crc_t10dif_generic()`. Init enables the PCLMUL static key when the CPU has `X86_FEATURE_PCLMULQDQ`, then updates the static call to AVX512 or AVX2 VPCLMUL when available.

## State and Persistence
Runtime state is the static key and static-call target chosen at module init. Per-call state is local.

## Dependencies and Integration Points
It depends on x86 CPU feature detection, the PCLMUL template header, and generic CRC-T10DIF hooks.

## Risks and Test Signals
Risks include CPU feature selection bugs and CRC16 constant layout assumptions. KUnit T10DIF tests and feature-specific x86 boot coverage validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc16-msb-pclmul.S -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc16-msb-pclmul.S

## Purpose
This assembly stub instantiates the x86 PCLMUL template for MSB-first 16-bit CRCs.

## Important APIs, Types, and Functions
It includes `crc-pclmul-template.S` and invokes `DEFINE_CRC_PCLMUL_FUNCS(crc16_msb, 16, 0)`.

## Control Flow
Generated SSE, AVX2, and AVX512 functions are produced by the template; this file contributes no separate logic.

## State and Persistence
No persistent state exists.

## Dependencies and Integration Points
It provides the generated functions declared by `crc-t10dif.h`.

## Risks and Test Signals
Risks are limited to instantiation arguments and template compatibility. CRC-T10DIF KUnit and link tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc16-msb-pclmul.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc32-pclmul.S -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc32-pclmul.S

## Purpose
This assembly stub instantiates the x86 PCLMUL template for reflected 32-bit CRCs.

## Important APIs, Types, and Functions
It invokes `DEFINE_CRC_PCLMUL_FUNCS(crc32_lsb, 32, 1)`, generating SSE, AVX2, and AVX512 functions.

## Control Flow
All processing flow is inherited from `crc-pclmul-template.S`.

## State and Persistence
No persistent state exists.

## Dependencies and Integration Points
Generated functions are used for CRC32 LE and, on some CPUs, CRC32C through x86 `crc32.h`.

## Risks and Test Signals
Risks are wrong bit-order instantiation and template ABI mismatch. CRC32 LE/CRC32C KUnit with PCLMUL dispatch is the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc32-pclmul.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc32.h -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc32.h

## Purpose
This x86 arch header selects optimized CRC32 LE and CRC32C implementations using PCLMULQDQ, VPCLMULQDQ, SSE4.2 CRC32 instructions, and a long-buffer three-way CRC32C combiner.

## Important APIs, Types, and Functions
It defines static keys `have_crc32`, `have_pclmulqdq`, and `have_vpclmul_avx512`, declares `crc32_lsb` PCLMUL functions, defines `crc32_le_arch()`, `crc32c_arch()`, `crc32_mod_init_arch()`, and `crc32_optimizations_arch()`, and declares `crc32c_x86_3way()`.

## Control Flow
CRC32 LE first tries `CRC_PCLMUL()` and otherwise falls back to `crc32_le_base()`. CRC32C requires SSE4.2 CRC32 support; for long x86_64 buffers with usable FPU and PCLMUL, it uses either AVX512 VPCLMUL or `crc32c_x86_3way()`. Otherwise it emits scalar `crc32{q,l,w,b}` instructions over full words and tail bytes. Init enables static keys and updates the CRC32 LSB static call to AVX512 or AVX2 when supported.

## State and Persistence
Runtime feature state is persisted in static keys and a static-call target. Per-call state is local CRC, pointer, length, and loop counters.

## Dependencies and Integration Points
It depends on x86 CPU features, kernel FPU APIs, the PCLMUL template, and the scalar CRC32 instruction. It integrates with generic CRC32 hooks; CRC32 BE remains the base implementation on x86.

## Risks and Test Signals
Risks include FPU use in disallowed contexts, threshold regressions, unaligned word casts, static-branch feature mismatches, and differences between CRC32C scalar and PCLMUL-combined paths. KUnit CRC32/CRC32C, irq-context tests, and CPU feature matrix testing are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc32c-3way.S -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc32c-3way.S

## Purpose
This x86_64 assembly file computes CRC32C for long buffers by running three parallel scalar CRC32 streams and combining them with PCLMULQDQ.

## Important APIs, Types, and Functions
It defines `SYM_FUNC_START(crc32c_x86_3way)`, constants such as `SMALL_SIZE`, and the `K_table` of PCLMUL combination constants.

## Control Flow
The function routes buffers below `SMALL_SIZE` to a simple scalar CRC32 path. Larger buffers are aligned to 8 bytes, split into three equal lanes of qwords, processed with unrolled `crc32q` streams, then combined using two PCLMUL multiplications and an XOR with the third lane. It repeats for full and partial blocks, then finishes remaining qword/dword/word/byte tails with scalar CRC32 instructions.

## State and Persistence
All mutable state is in registers. `K_table` is immutable read-only data.

## Dependencies and Integration Points
It depends on x86_64, SSE/PCLMUL availability, and is called by `crc32c_arch()` only inside a kernel FPU section when long-buffer conditions are met.

## Risks and Test Signals
Risks include lane-length arithmetic, table indexing by chunk size, alignment prologue bugs, and PCLMUL state assumptions. Long-buffer CRC32C KUnit tests and comparisons across the scalar/PCLMUL threshold validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc32c-3way.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc64-pclmul.S -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc64-pclmul.S

## Purpose
This assembly stub instantiates x86 PCLMUL CRC functions for both MSB-first and LSB-first 64-bit CRCs.

## Important APIs, Types, and Functions
It invokes `DEFINE_CRC_PCLMUL_FUNCS(crc64_msb, 64, 0)` and `DEFINE_CRC_PCLMUL_FUNCS(crc64_lsb, 64, 1)`.

## Control Flow
The shared template emits the SSE, AVX2, and AVX512 bodies for each prefix.

## State and Persistence
No state is introduced.

## Dependencies and Integration Points
Generated functions are declared and dispatched by x86 `crc64.h`.

## Risks and Test Signals
Risks are instantiation correctness and x86_64 ABI handling for 64-bit CRC return values. CRC64 BE and NVMe KUnit tests under PCLMUL dispatch validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc64-pclmul.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc64.h -->
# sources/distributed-fs/ceph-client/lib/crc/x86/crc64.h

## Purpose
This x86 arch header accelerates CRC64 BE and CRC64 NVMe with PCLMULQDQ/VPCLMULQDQ.

## Important APIs, Types, and Functions
It defines static key `have_pclmulqdq`, declares `crc64_msb` and `crc64_lsb` generated functions, provides `crc64_be_arch()`, `crc64_nvme_arch()`, and `crc64_mod_init_arch()`.

## Control Flow
Each arch hook invokes `CRC_PCLMUL()` with the corresponding 64-bit constants and falls back to generic CRC64. Init enables the PCLMUL static key and updates both static-call targets to AVX512 or AVX2 variants when VPCLMUL is supported.

## State and Persistence
Runtime dispatch persists in static key/static-call state. Per-call checksum state is local.

## Dependencies and Integration Points
It depends on the x86 PCLMUL template and generic CRC64 library. It integrates both reflected and non-reflected CRC64 variants.

## Risks and Test Signals
Risks include wrong reflected/non-reflected function pairing, FPU context issues, and AVX512 selection on CPUs with poor wide-vector behavior. CRC64 KUnit and feature-specific boot tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crc/x86/crc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/lib/crypto/Kconfig

## Purpose
This Kconfig file defines configuration symbols for the kernel crypto library modules and their architecture-specific acceleration toggles.

## Important APIs, Types, and Functions
Important symbols in this subset include `CRYPTO_LIB_AES`, `CRYPTO_LIB_AES_ARCH`, `CRYPTO_LIB_AESCFB`, `CRYPTO_LIB_AES_CBC_MACS`, `CRYPTO_LIB_AESGCM`, `CRYPTO_LIB_ARC4`, `CRYPTO_LIB_BLAKE2B`, `CRYPTO_LIB_BLAKE2B_ARCH`, `CRYPTO_LIB_BLAKE2S_ARCH`, `CRYPTO_LIB_CHACHA`, and `CRYPTO_LIB_CHACHA_ARCH`. It also defines related symbols for GF128, Curve25519, Poly1305, SHA, SM3, NH, and utility libraries.

## Control Flow
Kconfig selection is declarative. Library symbols select their required helper libraries, and arch-acceleration symbols default to `y` on architectures with supported code and constraints such as `!UML`, `!KMSAN`, vector crypto toolchain support, or efficient unaligned access.

## State and Persistence
Configuration choices persist in the kernel build configuration, not at runtime. They control which objects and arch headers are compiled.

## Dependencies and Integration Points
It integrates with `lib/crypto/Makefile`, generic crypto library headers, and architecture-specific acceleration files. Dependencies avoid unsupported environments such as UML/KMSAN for sensitive SIMD implementations.

## Risks and Test Signals
Risks include selecting arch code without toolchain/runtime support, missing generic fallbacks, and dependency loops. Test signals include allyesconfig/allmodconfig builds across architectures and crypto selftests under selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/Makefile -->
# sources/distributed-fs/ceph-client/lib/crypto/Makefile

## Purpose
This Makefile maps crypto library Kconfig symbols to objects, architecture-specific accelerators, generated perlasm sources, sanitizer exceptions, and clean targets.

## Important APIs, Types, and Functions
It defines build rules for `libaes.o`, `libaescfb.o`, `libaesgcm.o`, `libarc4.o`, `libblake2b.o`, always-built `blake2s.o` and `chacha-block-generic.o`, `libchacha.o`, and many other crypto libraries. It defines perlasm commands and arch object lists for ARM, ARM64, PPC, RISCV, S390, SPARC, X86, MIPS, and generated clean files.

## Control Flow
Kbuild conditionals append generic objects first, then add arch objects when the corresponding `CONFIG_CRYPTO_LIB_*_ARCH` symbol is enabled. Some objects include `CFLAGS_* += -I$(src)/$(SRCARCH)` so generic C files can include arch-local headers named like `aes.h` or `chacha.h`.

## State and Persistence
Build state is confined to generated object/source files and Kbuild variables. No runtime state exists.

## Dependencies and Integration Points
It is the central integration point between Kconfig and the source files in this subset. It also generates perlasm assembly for PPC, ARM/ARM64, MIPS, RISCV, and x86 crypto routines and marks some generated objects non-standard for objtool/build handling.

## Risks and Test Signals
Risks include wrong arch object inclusion, stale generated assembly flavor, missing clean-file entries, and include-path collisions. Test signals are cross-arch builds with arch acceleration toggled and crypto selftest modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/aes.c -->
# sources/distributed-fs/ceph-client/lib/crypto/aes.c

## Purpose
This file implements the generic AES block cipher library, exports S-box and T-table data, provides key preparation/encryption/decryption wrappers, and implements AES-CMAC, AES-XCBC-MAC, and AES-CBC-MAC helper APIs.

## Important APIs, Types, and Functions
Exported data includes `crypto_aes_sbox`, `crypto_aes_inv_sbox`, `aes_enc_tab`, and `aes_dec_tab`. Exported APIs include `aes_expandkey()`, `aes_preparekey()`, `aes_prepareenckey()`, `aes_encrypt()`, `aes_decrypt()`, `aes_cmac_preparekey()`, `aes_xcbcmac_preparekey()`, `aes_cmac_update()`, `aes_cmac_final()`, `aes_cbcmac_update()`, and `aes_cbcmac_final()`. Internal helpers include `aes_expandkey_generic()`, `aes_encrypt_generic()`, `aes_decrypt_generic()`, MixColumns helpers, and optional arch hooks from `aes.h`.

## Control Flow
Key preparation validates key length, computes round count, and either calls an arch `aes_preparekey_arch()` or the generic key expansion. Encryption/decryption wrappers call arch hooks that may be generic or accelerated. CMAC preparation derives subkeys by encrypting zero and multiplying in GF(2^128); update paths buffer partial blocks, run CBC-MAC blocks, and finalization applies the complete/incomplete final subkey before one last AES encryption. Module init runs architecture init and optional FIPS CMAC selftest.

## State and Persistence
Persistent state lives in caller-owned key/context structs: AES round keys, inverse keys, CMAC subkeys, CBC-MAC chaining value, partial block, and counters. File-scope static data is immutable. No on-disk persistence exists.

## Dependencies and Integration Points
It depends on `<crypto/aes.h>`, `<crypto/aes-cbc-macs.h>`, crypto utils, unaligned access helpers, module exports, and optional arch headers selected through `CONFIG_CRYPTO_LIB_AES_ARCH`. AES-GCM and AES-CFB in this subset build on these APIs.

## Risks and Test Signals
Risks include table-based AES cache timing leakage on CPUs without AES instructions, key-length validation mistakes, CMAC final-block edge cases, namespace export misuse, and arch/generic behavior divergence. Test signals include crypto selftests, FIPS CMAC test, AES known-answer vectors, in-place CMAC/CBC-MAC updates, and arch fallback comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/aescfb.c -->
# sources/distributed-fs/ceph-client/lib/crypto/aescfb.c

## Purpose
This file implements the generic AES-CFB library encryption/decryption helpers and optional selftests.

## Important APIs, Types, and Functions
It exports `aescfb_encrypt()` and `aescfb_decrypt()`. Selftest state is an `aescfb_tv[]` vector table and module init/exit functions under `CONFIG_CRYPTO_SELFTESTS`.

## Control Flow
Encryption copies the IV to a local chaining value, encrypts it to produce keystream blocks, XORs source to destination block-by-block, and shifts ciphertext into the chaining value. Decryption precomputes keystream from IV/source ciphertext and alternates two keystream buffers so in-place decryption is safe. Selftest prepares an encryption key, checks encrypt/decrypt and in-place encryption against vectors.

## State and Persistence
No state persists in the module. Callers provide an AES encryption key and IV; local chaining and keystream buffers are stack state.

## Dependencies and Integration Points
It depends on `crypto/aescfb.h`, AES library encryption-key preparation/encryption, XOR helpers, and module exports. It is built as `libaescfb.o` when `CRYPTO_LIB_AESCFB` is selected.

## Risks and Test Signals
Risks include in-place decryption hazards, handling lengths not divisible by 16, IV mutation expectations, and AES key misuse. Selftests with varied key sizes and in-place operations are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/aescfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/aesgcm.c -->
# sources/distributed-fs/ceph-client/lib/crypto/aesgcm.c

## Purpose
This file implements a compact AES-GCM authenticated encryption library on top of AES-CTR and GF(2^128) GHASH.

## Important APIs, Types, and Functions
Exported APIs are `aesgcm_expandkey()`, `aesgcm_encrypt()`, and `aesgcm_decrypt()`. Internal helpers are `aesgcm_mac()` and `aesgcm_crypt()`. The context `struct aesgcm_ctx` stores an AES encryption key, GHASH key, and auth tag size.

## Control Flow
Key expansion validates auth tag size and prepares AES, then encrypts the zero block to derive the GHASH key. Encryption initializes the 96-bit IV counter, encrypts/decrypts data with AES-CTR starting at counter value 2, and authenticates ciphertext and associated data with GHASH plus encrypted counter block 1. Decryption authenticates the input ciphertext first with `crypto_memneq()`, clears the temporary tag on failure, and only then decrypts.

## State and Persistence
Caller-owned context persists AES/GHASH key material and tag size. Per-message state includes the big-endian counter block, GHASH accumulator, temporary AES block, and tag buffer. No storage persists outside memory.

## Dependencies and Integration Points
It depends on AES, GF128 hash, crypto utils, unaligned/big-endian helpers, and module exports. Optional selftests use NIST/McGrew-Viega-style vectors and exercise in-place encrypt/decrypt.

## Risks and Test Signals
Risks include counter overflow behavior, tag-size validation, GHASH length encoding, decrypt-before-auth mistakes, partial final block handling, and IV reuse by callers. Test signals include AES-GCM known-answer tests for 128/192/256-bit keys, AAD coverage, tag failure tests, and in-place operation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/aesgcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arc4.c -->
# sources/distributed-fs/ceph-client/lib/crypto/arc4.c

## Purpose
This file implements the ARC4 stream cipher key-scheduling algorithm and pseudorandom generation/XOR routine for legacy users.

## Important APIs, Types, and Functions
It exports `arc4_setkey()` and `arc4_crypt()`, operating on caller-provided `struct arc4_ctx` containing `S[256]`, `x`, and `y`.

## Control Flow
`arc4_setkey()` initializes the permutation to identity, then runs the standard 256-step key scheduling loop cycling over the provided key. `arc4_crypt()` loads `x` and `y`, repeatedly swaps permutation entries, derives a keystream byte from `S[(a+b)&0xff]`, XORs input to output, and stores the updated indices back to the context.

## State and Persistence
The ARC4 permutation and indices persist in `struct arc4_ctx` across calls, so encryption/decryption continues the stream. There is no module-global mutable state.

## Dependencies and Integration Points
It depends on `<crypto/arc4.h>` and kernel export/module APIs. It is selected by `CRYPTO_LIB_ARC4`.

## Risks and Test Signals
ARC4 is cryptographically weak and should be legacy-only. Implementation risks include zero-length key assumptions, context reuse mistakes, and in-place pointer overlap expectations. Test signals are known ARC4 vectors, stream continuation tests, zero-length data calls, and in-place encryption/decryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/aes-cipher-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/aes-cipher-core.S

## Purpose
This ARM assembly file implements scalar AES block encryption and decryption using T-tables, optimized for ARM and integrated as the ARM AES arch backend.

## Important APIs, Types, and Functions
It defines `ENTRY(__aes_arm_encrypt)` and `ENTRY(__aes_arm_decrypt)`. Macros include `__select`, `__load`, `__hround`, `fround`, `iround`, and `do_crypt`.

## Control Flow
`do_crypt` loads the round keys and input block, handles big-endian byte reversal, XORs the first round key, prefetches the selected T-table with interrupts disabled, executes paired round macros until the final round, prefetches inverse S-box data for decryption final round, restores interrupts after data-dependent lookups, and stores the result.

## State and Persistence
All state is register/stack-local during a single block operation. It reads global AES tables from `aes.c` and does not mutate persistent state.

## Dependencies and Integration Points
It depends on ARM assembler helpers, cacheline constants, AES tables, and the C wrapper in `arm/aes.h`. `Makefile` includes it in `libaes` for ARM when AES arch support is enabled.

## Risks and Test Signals
Risks include table-based cache timing leakage, interrupt disabling window length, alignment assumptions, big-endian handling, and register clobber ABI errors. Test signals include AES known-answer tests on ARM, unaligned buffer wrapper tests, and FIPS/crypto selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/aes-cipher-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/aes.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/aes.h

## Purpose
This ARM arch header binds the generic AES library to the ARM scalar assembly block functions and handles unaligned buffers on systems without efficient unaligned access.

## Important APIs, Types, and Functions
It declares `__aes_arm_encrypt()` and `__aes_arm_decrypt()`, and defines `aes_preparekey_arch()`, `aes_encrypt_arch()`, and `aes_decrypt_arch()`.

## Control Flow
Key preparation delegates to `aes_expandkey_generic()`. Encryption/decryption check whether input or output is 4-byte aligned when unaligned access is inefficient; if not, they copy through a 16-byte aligned bounce buffer, call the assembly routine in-place, then copy to the destination. Aligned paths call assembly directly.

## State and Persistence
Prepared keys persist in caller-owned AES key structs. Bounce buffers are stack-local.

## Dependencies and Integration Points
It is included by `aes.c` when ARM arch AES is selected via Makefile include paths. It depends on AES types/macros and efficient unaligned-access configuration.

## Risks and Test Signals
Risks include bounce-buffer copy mistakes, in-place aliasing, and key layout mismatch with assembly. Test signals are AES vectors over aligned and unaligned in/out buffers, encryption-only keys, and decryption keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b-neon-core.S

## Purpose
This ARM NEON assembly file implements the BLAKE2b compression function for ARM systems with NEON.

## Important APIs, Types, and Functions
It defines `ENTRY(blake2b_compress_neon)`. Important data includes rotation tables for 24- and 16-bit byte rotations and the BLAKE2b IV. The core macro is `_blake2b_round`.

## Control Flow
The function aligns a stack spill buffer, loads `h`, `t`, and `f` fields from `struct blake2b_ctx`, increments the counter by `inc` per block, loads the 128-byte message block into NEON registers, executes 12 BLAKE2b rounds with sigma message ordering, folds the final state into the chaining value, stores updated `h`, and loops over `nblocks`.

## State and Persistence
Persistent hash state is caller-owned in `struct blake2b_ctx`: chaining value, counter, and finalization flags. The assembly mutates those fields. Stack spill and NEON registers are transient.

## Dependencies and Integration Points
It depends on ARM NEON and Linux linkage. The wrapper in `arm/blake2b.h` calls it inside SIMD-safe sections when NEON is available.

## Risks and Test Signals
Risks include counter carry handling, stack alignment, NEON register clobbers, final flag handling, and message schedule errors. BLAKE2b known-answer tests and chunked update/final-block cases are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b.h

## Purpose
This ARM arch header selects the NEON BLAKE2b compression implementation when available and SIMD use is allowed.

## Important APIs, Types, and Functions
It defines static key `have_neon`, declares `blake2b_compress_neon()`, overrides `blake2b_compress()`, and defines `blake2b_mod_init_arch()`.

## Control Flow
`blake2b_compress()` falls back to `blake2b_compress_generic()` if NEON is unavailable or SIMD cannot be used. Otherwise it processes input in chunks capped at `SZ_4K / BLAKE2B_BLOCK_SIZE` inside `scoped_ksimd()` sections, updating data pointer and block count. Init enables the static key when `elf_hwcap` has `HWCAP_NEON`.

## State and Persistence
Persistent state is the static key and caller-owned BLAKE2b context. No other state persists.

## Dependencies and Integration Points
It depends on ARM NEON/SIMD helpers and is included by generic `blake2b.c` via arch include path when selected.

## Risks and Test Signals
Risks include SIMD use in preempt/irq contexts, chunking mistakes, and static-key feature detection. Test signals are BLAKE2b vectors with NEON enabled/disabled and context-sensitive SIMD tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s-core.S

## Purpose
This ARM scalar assembly file implements BLAKE2s compression faster than the generic C path on ARM without relying on NEON.

## Important APIs, Types, and Functions
It defines `ENTRY(blake2s_compress)` and macros for loading/storing words, endian swaps, quarter rounds, rounds, and the permutation. It embeds the BLAKE2s IV.

## Control Flow
For each block, the function loads the hash state and message words, sets up the BLAKE2s state with counters and flags, runs the required rounds with message schedule permutations, folds the result into the chaining value, updates counters, advances input, and loops until `nblocks` is exhausted.

## State and Persistence
The caller-owned `struct blake2s_ctx` state is updated across blocks. Temporary message/state words live in ARM registers and stack spill slots.

## Dependencies and Integration Points
It depends on ARM assembler helpers and is built when `CRYPTO_LIB_BLAKE2S_ARCH` selects ARM. `arm/blake2s.h` declares the function for the generic BLAKE2s code.

## Risks and Test Signals
Risks include endian conversion on ARM big-endian, delayed rotation bookkeeping, stack spill correctness, and counter/final flag handling. Known-answer BLAKE2s tests and incremental update tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s.h

## Purpose
This minimal ARM header declares the architecture-provided BLAKE2s compression routine.

## Important APIs, Types, and Functions
It declares `void blake2s_compress(struct blake2s_ctx *ctx, const u8 *block, size_t nblocks, u32 inc);`.

## Control Flow
There is no code flow; the declaration causes generic BLAKE2s code to bind to the ARM assembly implementation when selected.

## State and Persistence
No state is defined here.

## Dependencies and Integration Points
It depends on the generic BLAKE2s context type being visible to the including translation unit and matches `arm/blake2s-core.S`.

## Risks and Test Signals
Risks are declaration/signature drift. Build/link tests and BLAKE2s known-answer tests are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-neon-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-neon-core.S

## Purpose
This ARM NEON assembly file implements ChaCha block XOR, four-block XOR, and HChaCha using vectorized NEON operations.

## Important APIs, Types, and Functions
It defines `ENTRY(chacha_block_xor_neon)`, `ENTRY(hchacha_block_neon)`, and `ENTRY(chacha_4block_xor_neon)`. It includes permutation/rotate constants and a `.Lpermute` table for partial-block stores.

## Control Flow
The one-block path loads the ChaCha state, runs 12 or 20 rounds, adds the original state, XORs one 64-byte block, and stores. HChaCha runs the permutation and stores words x0-x3 and x12-x15. The four-block path transposes four states across NEON registers, adds counters 0-3, runs double rounds, re-interleaves output keystream, XORs up to 256 bytes, and uses table-based partial handling for the final incomplete block.

## State and Persistence
All state is register and stack-local; the wrapper updates the caller-owned block counter after calls. No global mutable state is created.

## Dependencies and Integration Points
It depends on ARM NEON, Linux linkage, and is selected by `arm/chacha.h` when NEON is usable. It complements the scalar ARM ChaCha implementation.

## Risks and Test Signals
Risks include partial-block overlap stores, counter lane addition, 12- versus 20-round selection, state transposition bugs, and SIMD context misuse if called outside wrappers. ChaCha/XChaCha known-answer tests, partial lengths 1-255, and in-place XOR tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-neon-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-scalar-core.S -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-scalar-core.S

## Purpose
This ARM scalar assembly file implements ChaCha encryption/XOR and HChaCha without NEON, optimized around ARM register constraints.

## Important APIs, Types, and Functions
It defines `ENTRY(chacha_doarm)` and `ENTRY(hchacha_block_arm)`. Core macros include `_halfround`, `_doubleround`, `_chacha_permute`, and `_chacha`.

## Control Flow
`chacha_doarm()` loads the 16-word state and chooses 12 or 20 rounds. `_chacha` permutes the state, adds the original state, XORs a full aligned 64-byte block quickly when possible, otherwise generates a keystream block on the stack and XORs the required bytes. It increments the block counter and loops. `hchacha_block_arm()` runs the permutation and stores x0-x3 and x12-x15.

## State and Persistence
The function consumes caller-provided state and output/input pointers. It does not mutate the original state directly; the C wrapper updates `state->x[12]`. Temporary state is in registers and stack.

## Dependencies and Integration Points
It depends on ARM assembler helpers and is always part of ARM `libchacha` arch support. `arm/chacha.h` uses it as fallback and for small messages.

## Risks and Test Signals
Risks include stack layout complexity, alignment slow-path correctness, counter overflow conventions, 12-round selection, and big-endian byte swaps. ChaCha20, ChaCha12, HChaCha, XChaCha, partial-block, and unaligned-buffer tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-scalar-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/chacha.h -->
# sources/distributed-fs/ceph-client/lib/crypto/arm/chacha.h

## Purpose
This ARM arch header selects between scalar and NEON ChaCha/HChaCha implementations and updates the block counter for callers.

## Important APIs, Types, and Functions
It declares NEON and scalar assembly entry points, defines static key `use_neon`, helper `neon_usable()`, `chacha_doneon()`, `hchacha_block_arch()`, `chacha_crypt_arch()`, and `chacha_mod_init_arch()`.

## Control Flow
`hchacha_block_arch()` chooses scalar unless kernel-mode NEON is enabled and usable. `chacha_crypt_arch()` uses scalar for no NEON, unusable SIMD, or <=64-byte messages; otherwise it processes up to `SZ_4K` per SIMD section using `chacha_doneon()`. `chacha_doneon()` uses four-block NEON chunks and a one-block final path, including a bounce buffer for partial final blocks. Init enables NEON except on Cortex-A7/A5 where scalar is preferred.

## State and Persistence
Persistent state is the static key and caller-owned `struct chacha_state`, especially `x[12]` block counter, which the wrapper increments by blocks consumed.

## Dependencies and Integration Points
It depends on crypto SIMD helpers, ARM hwcap/cputype APIs, and the generic ChaCha library. The Makefile includes scalar and optional NEON objects for ARM.

## Risks and Test Signals
Risks include counter update mismatches between scalar and NEON paths, SIMD use in invalid contexts, CPU blacklist logic, and partial final-block copy handling. Test signals include ChaCha selftests over small/large lengths, Cortex feature-path coverage, and in-place encryption tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/arm/chacha.h -->
