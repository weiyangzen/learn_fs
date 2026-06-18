# sources/distributed-fs/ceph-client/arch/riscv/kernel/copy-unaligned.S

Purpose: Implements scalar RISC-V helpers for unaligned copy operations used by misaligned access handling and copy benchmarks.

Important APIs/types/functions: Defines `__riscv_copy_words_unaligned` and `__riscv_copy_bytes_unaligned`.

Control flow: The word helper copies full machine words in a loop using unaligned load/store sequences, then falls through to byte copying for the tail. The byte helper copies remaining bytes one at a time until the requested count is consumed.

State and persistence: No persistent state. It mutates only caller-provided source/destination memory and clobbers scratch registers per the assembly ABI.

Dependencies and integration points: Depends on RISC-V assembler macros and is declared by `copy-unaligned.h`; it may be selected against vector copy alternatives by unaligned access code.

Risks and test signals: Overlap semantics, count handling, and tail copying must match callers. Test with randomized unaligned source/destination offsets, small sizes, word-boundary tails, KASAN/KMSAN, and platforms with strict misaligned access traps.
