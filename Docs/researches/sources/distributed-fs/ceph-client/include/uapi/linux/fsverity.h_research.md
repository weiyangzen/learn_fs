# sources/distributed-fs/ceph-client/include/uapi/linux/fsverity.h

This UAPI header defines the fs-verity userspace ABI for enabling transparent file authenticity verification, measuring file digests, and reading verity metadata. It is used by filesystems that support Merkle-tree-backed read-only verification.

Important exports include hash algorithm IDs `FS_VERITY_HASH_ALG_SHA256` and `SHA512`, `struct fsverity_enable_arg`, `struct fsverity_digest`, `struct fsverity_descriptor`, `struct fsverity_formatted_digest`, metadata type constants for Merkle tree, descriptor, and signature, `struct fsverity_read_metadata_arg`, and ioctls `FS_IOC_ENABLE_VERITY`, `FS_IOC_MEASURE_VERITY`, and `FS_IOC_READ_VERITY_METADATA`.

Control flow is ioctl based: userspace writes file contents, optionally supplies a salt and signature, calls enable verity, then the filesystem builds/stores metadata and marks the file verity-protected; later reads verify blocks against the Merkle tree, and userspace can measure digest or read metadata. State includes per-inode verity flag, descriptor, Merkle tree pages, optional signature, and page-cache verification state. Persistence is file metadata and Merkle tree storage.

Dependencies include `linux/ioctl.h`, `linux/types.h`, kernel crypto, filesystem fsverity hooks, key/signature verification if enabled, and generic `FS_XFLAG_VERITY`/`FS_VERITY_FL` flags. Integration points include Android verified files, package managers, immutable asset stores, ext4/F2FS, and userspace signing tools.

Risks include enabling verity on mutable or incomplete files, digest format/endian mistakes, signature context confusion, unsupported hash algorithms/block sizes, metadata disclosure, and incompatibility with encryption/compression features. Test signals include fsverity selftests, digest reproducibility tests, signature verification tests, corrupted block detection, metadata read tests, and filesystem-specific enable/read-only behavior.
