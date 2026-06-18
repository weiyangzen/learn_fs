<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/md5.c -->
# sources/distributed-fs/orangefs/src/common/misc/md5.c

Purpose: standalone MD5 implementation derived from L. Peter Deutsch's public-domain-style code and RFC 1321. OrangeFS uses it locally, notably for distributed-directory name hashing.

Important functions: private `md5_process()` transforms one 64-byte block using the four MD5 rounds and architecture-aware byte ordering. `md5_init()` initializes bit count and digest state. `md5_append()` updates bit count, handles partial block buffering, processes full blocks, and stores trailing bytes. `md5_finish()` pads to 56 bytes modulo 64, appends the original bit length, and writes the 16-byte digest.

Control flow is the standard streaming hash flow: initialize, append zero or more chunks, finish. Byte order is selected by `ARCH_IS_BIG_ENDIAN` if defined or detected dynamically. Aligned little-endian input may be processed without copying; unaligned or big-endian input is normalized through a local buffer.

State is caller-owned `md5_state_t`; there is no global mutable state and no persistence. Dependencies are `md5.h`, `string.h`, and OrangeFS internal endian configuration.

Risks: MD5 is cryptographically broken and should only be used for non-security distribution/checksum purposes. `md5_append()` takes `int nbytes`, limiting single-call size and making negative values a no-op. Alignment checks use pointer arithmetic against null, a common but technically questionable idiom. Tests should include RFC MD5 vectors, chunked versus one-shot equivalence, empty input, large streaming input crossing 32-bit bit-count boundaries, and big-endian/unaligned builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/md5.c -->
