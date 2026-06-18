<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32c.c -->
# sources/distributed-fs/ceph-client/crypto/crc32c.c

## Purpose

`crc32c.c` registers a Crypto API shash wrapper for CRC-32C/Castagnoli using the kernel `crc32c()` helper. Unlike `crc32.c`, it initializes to `~0` and applies a final bitwise complement.

## Important APIs, Types, and Flow

`struct chksum_ctx` stores the transform seed; `struct chksum_desc_ctx` stores the streaming accumulator. `crc32c_cra_init()` initializes the seed to `~0`. `chksum_setkey()` accepts exactly four little-endian bytes to override the seed. `chksum_init()` copies seed into descriptor state, `chksum_update()` advances with `crc32c()`, and `chksum_final()` writes `~crc` little-endian. `finup()` and `digest()` share `__chksum_finup()`.

The registered algorithm name is `crc32c`, driver `crc32c-lib`, block size 1, digest size 4, optional key, and descriptor size `sizeof(struct chksum_desc_ctx)`.

## State, Dependencies, and Integration

State is transform seed plus per-request CRC accumulator. Dependencies are `linux/crc32.h`, shash internals, and unaligned helpers. It integrates with protocols and filesystems that select CRC32C through the Crypto API.

## Risks and Test Signals

Risks are variant confusion around initial and final complement, seed byte order, and hardware/software CRC32C equivalence. Tests should compare against known Castagnoli vectors, custom seed cases, split update equivalence, and invalid key length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32c.c -->
