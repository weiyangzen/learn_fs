# sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.h

Purpose: Declares the RISC-V scalar and optional vector unaligned copy assembly entry points.

Important APIs/types/functions: Declares `__riscv_copy_words_unaligned`, `__riscv_copy_bytes_unaligned`, and, under vector support, `__riscv_copy_vec_words_unaligned` and `__riscv_copy_vec_bytes_unaligned`.

Control flow: This header has no runtime control flow. It supplies prototypes used by C code to select scalar or vector copy helpers.

State and persistence: No state is stored here.

Dependencies and integration points: Integrates `copy-unaligned.S`, vector copy assembly, and RISC-V unaligned access performance/handling code.

Risks and test signals: Prototype mismatches with assembly calling conventions can corrupt copies or registers. Test through the unaligned copy users with scalar-only and vector-enabled configs.
