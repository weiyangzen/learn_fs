# sources/distributed-fs/ceph-client/fs/ubifs/Kconfig

## Purpose
This Kconfig file defines UBIFS build options, compression support, atime policy, xattrs/security labels, and authentication.

## Important APIs, Types, and Functions
The main option is `UBIFS_FS`, a tristate filesystem depending on `MTD_UBI`. It selects CRC and crypto helpers as needed. Suboptions include `UBIFS_FS_ADVANCED_COMPR`, `UBIFS_FS_LZO`, `UBIFS_FS_ZLIB`, `UBIFS_FS_ZSTD`, `UBIFS_ATIME_SUPPORT`, `UBIFS_FS_XATTR`, `UBIFS_FS_SECURITY`, and `UBIFS_FS_AUTHENTICATION`.

## Control Flow and State
This is build-time configuration. Compressor selections affect which compression algorithms are compiled and therefore which existing UBIFS images can be read. Authentication selects keys, HMAC, and system data verification support but intentionally does not auto-select a hash algorithm.

## Persistence, Dependencies, and Integration
UBIFS integrates with UBI/MTD, crypto compression, fs encryption, xattrs, LSM security labels, keyrings, and data verification. Options affect on-media compatibility, especially compressors and authentication.

## Risks and Test Signals
Risks include building without a compressor required by deployed volumes, enabling atime and increasing flash wear, enabling security labels without xattrs, and authentication misconfiguration without a hash algorithm/key. Build matrix tests and mount tests against images using each compressor/authentication mode are important.
