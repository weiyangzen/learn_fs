# sources/distributed-fs/ceph-client/arch/microblaze/lib/fastcopy.S

Purpose: optimized assembly implementation of `memcpy` and `memmove` for MicroBlaze when `CONFIG_OPT_LIB_ASM` is enabled.

Important APIs and state: exports `memcpy` and `memmove`. Arguments use r5 destination, r6 source, r7 byte count; r3 returns original destination.

Control flow: ascending copy handles small byte tail, aligns destination, copies 32-byte blocks, handles aligned and 1/2/3-byte unaligned source cases with shifts, copies word remainder, then byte tail. `memmove` chooses ascending path when destination is below source; otherwise it performs a mirrored descending copy to preserve overlapping regions.

State and persistence: mutates destination memory only. No exception table protection, so it is for trusted kernel memory copies.

Dependencies and integration: selected instead of C string routines by Makefile and exported for modules under optimized assembly config.

Risks and test signals: endian and unaligned-source shift paths are complex; comments contain some stale typo offsets but code drives behavior. Test overlapping and non-overlapping copies, all source/dest alignments, small sizes 0-64, large blocks, and both endian builds.
