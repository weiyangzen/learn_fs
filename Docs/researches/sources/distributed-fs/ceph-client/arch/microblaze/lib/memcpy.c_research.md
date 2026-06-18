# sources/distributed-fs/ceph-client/arch/microblaze/lib/memcpy.c

Purpose: C optimized `memcpy` implementation used when `CONFIG_OPT_LIB_FUNCTION` is enabled and assembly fastcopy is not selected.

Important APIs and state: exported `memcpy(void *dst, const void *src, __kernel_size_t c)`.

Control flow: aligns destination byte by byte, then chooses a word-copy path based on source alignment. Aligned sources copy words directly; unaligned sources assemble each word from adjacent aligned loads with endian-specific shifts. Remaining 1-3 bytes are copied individually.

State and persistence: mutates destination memory only.

Dependencies and integration: selected by lib Makefile when not using assembly fastcopy; module export is conditional through ksyms.

Risks and test signals: it is not overlap-safe; callers needing overlap must use memmove. Unaligned paths may be slow without barrel shifter. Test all alignments, endian builds, small counts, and non-overlap assumptions.
