# sources/distributed-fs/ceph-client/arch/microblaze/lib/memmove.c

Purpose: C optimized overlap-safe `memmove` implementation for MicroBlaze.

Important APIs and state: exported `memmove(void *dst, const void *src, __kernel_size_t c)` under `CONFIG_OPT_LIB_FUNCTION`.

Control flow: zero length returns immediately. If destination is below source, it delegates to `memcpy`; otherwise it copies descending from the end, aligns destination, then performs direct or endian-specific unaligned word assembly before copying remaining bytes backward.

State and persistence: mutates destination memory.

Dependencies and integration: selected by lib Makefile when assembly fastcopy is off.

Risks and test signals: descending unaligned cases are explicitly marked as needing more testing. Test overlapping ranges where dst starts inside src, all alignments, counts near word boundaries, and both endian configurations.
