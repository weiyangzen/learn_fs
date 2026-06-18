# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memcpy.S

Purpose: Niagara4 optimized memcpy engine and copy-user template.

Important APIs/functions: Emits `NG4memcpy` by default; macro hooks include `LOAD`, `STORE`, `STORE_INIT`, `EX_LD`, `EX_ST`, `EX_LD_FP`, `EX_ST_FP`, `FUNC_NAME`, and `PREAMBLE`.

Control flow: Checks length, handles tiny copies, aligns destination, prefetches source, uses VIS-assisted larger copy paths, and finishes with xword/byte tails. Wrapper files override memory access macros and exception target behavior.

State and persistence: Stateless data movement with temporary VIS/FPU and ASI state. Uses shared `Memcpy_utils.S` helpers for exceptional exits.

Dependencies/integration: Includes `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; patched by `NG4patch.S`.

Risks/test signals: Alignment-specific labels and prefetch/VIS interactions are high risk. Test all low-bit alignment combinations, exact threshold sizes, faulting user-copy variants, and throughput/correctness against generic routines.
