# sources/distributed-fs/ceph-client/arch/microblaze/lib/memset.c

Purpose: C optimized `memset` implementation for MicroBlaze.

Important APIs and state: exported `memset(void *v_src, int c, __kernel_size_t n)` under `CONFIG_OPT_LIB_FUNCTION`.

Control flow: truncates fill byte, expands it to a 32-bit repeated word, aligns destination to a word boundary, writes full words, then writes remaining 1-3 bytes.

State and persistence: mutates the target memory region only.

Dependencies and integration: always selected by lib Makefile; export depends on function config.

Risks and test signals: alignment switch intentionally falls through. Test zero and nonzero fills, all destination alignments, small sizes, and large word fills.
