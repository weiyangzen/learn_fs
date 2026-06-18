# sources/distributed-fs/ceph-client/include/uapi/linux/types.h

Purpose: Provides common Linux UAPI scalar, endian-tagged, aligned, and bitwise types for userspace headers.

Important APIs/types/functions: Includes architecture scalar types from `asm/types.h` and POSIX-like kernel types from `linux/posix_types.h`. Defines optional 128-bit signed/unsigned types for non-32-bit userspace. Sparse-aware `__bitwise` tagging annotates endian and checksum types: `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`, `__sum16`, `__wsum`, and `__poll_t`. Alignment macros `__aligned_u64`, `__aligned_s64`, `__aligned_be64`, and `__aligned_le64` force 8-byte alignment in UAPI structs.

Control flow: No executable flow; this is a foundational type header.

State and persistence behavior: No state. Its ABI impact is structural layout and compile-time type checking.

Dependencies and integration points: Used by almost every Linux UAPI header, including this work item. Integrates with sparse (`__CHECKER__`) and architecture-specific type definitions.

Risks: Any change affects broad UAPI layout. 64-bit alignment macros are critical for compat ioctls. Endian tags are compile-time only unless checked by sparse.

Test signals: Build UAPI headers standalone for multiple architectures, verify struct layout involving `__aligned_u64`, run sparse checks for endian misuse, and validate 32-bit compat ioctl layouts.
