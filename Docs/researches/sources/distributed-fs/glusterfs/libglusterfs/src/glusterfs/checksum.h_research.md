# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/checksum.h

## Purpose
`checksum.h` declares rsync-style checksum helpers used by GlusterFS code that compares or synchronizes byte ranges.

## Important APIs, Types, and Functions
- `gf_rsync_weak_checksum(unsigned char *buf, size_t len)`: returns a 32-bit weak rolling checksum.
- `gf_rsync_strong_checksum(unsigned char *buf, size_t len, unsigned char *sum)`: writes a strong checksum.
- `gf_rsync_md5_checksum(unsigned char *data, size_t len, unsigned char *md5)`: writes an MD5 digest.

## Control Flow
This header only declares functions. Implementations in checksum source files compute weak and strong hashes over caller-provided buffers and write digest bytes to caller-provided output storage.

## State and Persistence
No state is declared. All state is local to the implementation and caller-provided buffers.

## Dependencies and Integration Points
Integrates with FOPs such as `rchecksum`, replication/heal checks, and any translator needing rsync-compatible block comparison.

## Risks and Edge Cases
- Callers must supply output buffers of the expected digest size.
- MD5 and rsync weak checksums are not security primitives; they are integrity/synchronization helpers.
- Header lacks explicit size constants for strong and MD5 outputs, so caller/implementation agreement matters.

## Test Signals
Compare weak, strong, and MD5 outputs against known vectors, including empty input, single byte, large buffers, and repeated patterns. Test callers for correct output buffer sizing.
