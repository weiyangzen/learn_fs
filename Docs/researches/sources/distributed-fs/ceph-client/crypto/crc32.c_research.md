<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32.c -->
# sources/distributed-fs/ceph-client/crypto/crc32.c

## Purpose

`crc32.c` registers a Crypto API shash wrapper around `crc32_le()`. It exposes `crc32` with optional seed keying and no final XOR, matching the behavior of the library helper.

## Important APIs, Types, and Flow

The transform context is a `u32` seed initialized to zero by `crc32_cra_init()`. `crc32_setkey()` accepts exactly four little-endian key bytes and stores the seed. `crc32_init()` copies the seed to descriptor state. `crc32_update()` advances descriptor CRC with `crc32_le()`. `crc32_final()` writes the current CRC little-endian. `crc32_finup()` and `crc32_digest()` perform update plus output in one step, with digest using the transform seed directly.

The registered `shash_alg` has block size 1, digest size 4, optional key flag, driver `crc32-lib`, and descriptor size `sizeof(u32)`.

## State, Dependencies, and Integration

State is the per-transform seed and per-request accumulator. Dependencies are `linux/crc32.h`, unaligned little-endian accessors, and shash registration. It integrates with kernel consumers that need CRC32 through the Crypto API rather than direct library calls.

## Risks and Test Signals

Risks include confusion with CRC variants that use initial/final XOR, seed endianness, and one-shot digest mutating expectations. Test signals are vectors matching `crc32_le()`, custom seed tests, update-versus-finup equivalence, and rejection of non-four-byte keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32.c -->
