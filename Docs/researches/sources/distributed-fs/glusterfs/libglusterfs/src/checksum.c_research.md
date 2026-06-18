# sources/distributed-fs/glusterfs/libglusterfs/src/checksum.c

## Purpose
`checksum.c` supplies the checksum primitives used by GlusterFS rsync-style workflows and checksum FOPs. It provides a weak rolling-style checksum and strong cryptographic digests over caller-provided memory buffers.

## Important APIs, Types, And Functions
`gf_rsync_weak_checksum(unsigned char *buf, size_t len)` returns a `uint32_t` Adler-32 value from zlib. `gf_rsync_strong_checksum(unsigned char *data, size_t len, unsigned char *sha256_md)` writes a SHA-256 digest using OpenSSL `SHA256`. `gf_rsync_md5_checksum(unsigned char *data, size_t len, unsigned char *md5)` writes an MD5 digest using OpenSSL `MD5`.

## Control Flow
Each function is a direct wrapper. The weak checksum calls `adler32(0, buf, len)`. The strong checksum calls OpenSSL SHA-256 over the full buffer. The MD5 helper calls OpenSSL MD5 over the full buffer. There is no allocation, no locking, and no retry logic.

## State And Persistence Behavior
The file has no persistent state. All outputs are written into caller-owned buffers. The caller must provide digest buffers of the correct OpenSSL sizes.

## Dependencies And Integration Points
It depends on `<zlib.h>`, `<openssl/sha.h>`, `<openssl/md5.h>`, and basic C headers. It integrates with rsync checksum logic and with FOPs such as rchecksum that need weak and strong checksum pairs for data comparison or synchronization.

## Risks And Edge Cases
There is no NULL-pointer validation or output-size validation. The comment says these functions are only called for pathnames and therefore do not need arbitrary long data handling, but the signatures accept any `size_t`; callers must enforce intended use. MD5 is cryptographically weak and should be treated only as a compatibility checksum. OpenSSL 3 builds may warn about low-level MD5 APIs.

## Test Signals
Tests should compare known Adler-32, SHA-256, and MD5 vectors, verify zero-length buffers, exercise non-ASCII byte input, and run with sanitizer coverage for NULL or undersized output buffer misuse at callers.
