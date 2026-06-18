# sources/distributed-fs/ceph-client/arch/parisc/lib/memset.c

Purpose: supplies PA-RISC `memset()` using word-sized stores after aligning the destination. The implementation is derived from classic libc-style logic and is independent of user access handling.

Important APIs/types/functions: `memset(void *dstpp, int sc, size_t len)` is the only function. `op_t` is `unsigned long`; `OPSIZ` follows `BITS_PER_LONG / 8`, so the bulk store width changes between 32-bit and 64-bit kernels.

Control flow: for lengths at least 8 bytes, it builds a repeated-byte word `cccc`, byte-fills until destination alignment matches `OPSIZ`, stores eight `op_t` words per loop, then one `op_t` per loop for the remaining word count. A final byte loop writes trailing bytes. It returns the original destination pointer.

State and dependencies: no persistent state. Depends on `<linux/types.h>`, `<asm/string.h>`, and `BITS_PER_LONG`. It writes only the caller-specified memory range.

Risks: assumes normal kernel memory, so it is not suitable for user-space faulting access or MMIO ordering. Pointer arithmetic is performed through `long int dstp`; this matches PA-RISC kernel assumptions but would be questionable as generic portable C. Store alignment and `op_t` aliasing are intentionally low-level.

Test signals: generic kernel string/memory selftests, boot-time memory initialization checks, byte-pattern tests at all alignments and lengths around `OPSIZ * 8`, and 32-bit/64-bit PA-RISC builds.
