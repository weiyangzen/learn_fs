# sources/distributed-fs/ceph-client/arch/arm/lib/memset.S

Purpose: implements `__memset`, weak `memset`, `mmioset`, `__memset32`, and `__memset64`.

Control flow aligns the destination, expands an 8-bit value to words, stores 64-byte/32-byte/16-byte blocks with optional cacheline alignment strategy, then writes byte tails. `__memset32`/`__memset64` enter the shared word-fill path. State is the target memory only. Dependencies include assembler macros, unwind annotations, and optional CALGN configuration. Risks are alignment tail mistakes, MMIO ordering assumptions for `mmioset`, and preserving the destination return value. Test signals include memset tests for every length/alignment, 32/64-bit fill helpers, and boot memory initialization paths.
