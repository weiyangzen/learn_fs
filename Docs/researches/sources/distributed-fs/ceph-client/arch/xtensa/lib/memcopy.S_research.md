# sources/distributed-fs/ceph-client/arch/xtensa/lib/memcopy.S

Purpose: Provides optimized `memcpy`/`memmove` implementations for Xtensa and exports both internal and standard symbols.

Important APIs, types, and functions: `__memcpy`, weak `memcpy`, `__memmove`, weak `memmove`, byte-copy paths, aligned word-copy paths, unaligned-source `SRC` paths, backward-copy paths, and exported symbols.

Control flow: `memcpy` aligns destination with byte/halfword copies, then chooses word-aligned fast loops or unaligned-source merge loops, finishing with 8/4/2/1 byte tails. `memmove` detects overlap; non-overlap falls into memcpy logic, while overlap copies backward with analogous aligned and unaligned paths.

State and persistence: Writes destination memory and returns original destination. No exception fixup is used for normal kernel memory copies.

Dependencies and integration: Used broadly by the kernel and modules; depends on Xtensa load/store alignment behavior, optional loop instructions, `__src_b` endian-aware merge macro, and ABI macros.

Risks: Comments note IRAM/IROM special handling is not implemented; overlap detection must be exact; simulator alignment checks force conservative unaligned handling; copying faulting addresses is not protected here.

Test signals: libc-style memcpy/memmove tests across alignments, lengths, overlap directions, zero length, simulator alignment modes, and memory regions with device-like restrictions if relevant.
