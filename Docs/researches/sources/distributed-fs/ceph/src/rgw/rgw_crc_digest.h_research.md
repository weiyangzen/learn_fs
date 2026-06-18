# sources/distributed-fs/ceph/src/rgw/rgw_crc_digest.h

## Purpose
Provides small digest wrappers for RGW checksum calculation: CRC32, CRC32C, and NVMe CRC64.

## Important APIs, types, and functions
`rgw::digest::byteswap()` is a constexpr C++23-style byte swap. `Crc32` uses `boost::crc_optimal` for IEEE CRC32 and reports a 4-byte digest. `Crc32c` uses Ceph's hardware-specialized `ceph_crc32c()` with standard initial/final xor. `Crc64Nvme` uses SPDK `spdk_crc64_nvme()` and reports an 8-byte digest. Each type exposes `Restart()`, `Update()`, `Final()`, and `digest_size`.

## Control flow
Callers instantiate a digest, feed chunks with `Update()`, and copy the final big-endian byte representation into the output buffer via `Final()`.

## State and persistence
State is only the current CRC accumulator. No persistence occurs, but output byte ordering affects persisted/user-visible checksum metadata.

## Dependencies and integration points
Depends on Boost CRC, Ceph CRC32C, SPDK CRC64, C++20 endian/bit utilities, and standard `memcpy`.

## Risks and test signals
Endian handling is explicitly called out by comments, especially for CRC64/NVMe and ARM/big-endian platforms. Tests should compare against AWS/S3 checksum vectors, incremental update equivalence, restart behavior, zero-length input, and big-endian builds or emulation.
