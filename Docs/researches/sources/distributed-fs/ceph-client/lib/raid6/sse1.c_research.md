## sources/distributed-fs/ceph-client/lib/raid6/sse1.c

Purpose: implements legacy 32-bit x86 SSE1/MMXEXT RAID-6 syndrome generation. The implementation is actually MMX-based but uses SSE/MMXEXT features such as prefetch and non-temporal stores.

Important APIs/functions: `raid6_have_sse1_or_mmxext()` checks MMX plus XMM or MMXEXT. `raid6_sse11_gen_syndrome()` processes one 64-bit MMX lane per loop, while `raid6_sse12_gen_syndrome()` is unrolled by two. Public descriptors are `raid6_sse1x1` and `raid6_sse1x2`; neither provides `xor_syndrome`.

Control flow: each function identifies highest data disk `z0`, P at `z0+1`, Q at `z0+2`, enters FPU/MMX context, initializes the GF reduction constant `0x1d`, and walks each byte range across data disks. Q is multiplied by two in GF(2^8) using compare-mask, byte add, mask with `0x1d`, and XOR; P is a simple XOR accumulator. Results are written with `movntq` and finalized with `sfence`.

State and persistence: no persistent state. The routines mutate only parity buffers and use MMX registers under `kernel_fpu_begin/end()`.

Dependencies/integration: compiled only under `CONFIG_X86_32`; depends on `raid6_mmx_constants` from `mmx.c`, `x86.h`, and generic RAID-6 algorithm selection.

Risks/test signals: risks include MMX/FPU state handling, non-temporal store ordering, and maintaining support for old 32-bit feature combinations. Validation is available through `raid6/test`, which includes `sse1.o` for i386 builds and compares recovery across algorithms.
