# sources/distributed-fs/ceph-client/fs/smb/common/md4.h

Read coverage: full file.

## Purpose
`md4.h` declares the CIFS MD4 context and digest API used by the common SMB MD4 implementation.

## Important APIs, types, and functions
Constants are `MD4_DIGEST_SIZE`, `MD4_HMAC_BLOCK_SIZE`, `MD4_BLOCK_WORDS`, and `MD4_HASH_WORDS`. `struct md4_ctx` stores the four-word hash state, sixteen-word block buffer, and total byte count. Function prototypes are `cifs_md4_init`, `cifs_md4_update`, and `cifs_md4_final`.

## Control flow
The header has no runtime control flow. It supplies the compile-time contract consumed by `cifs_md4.c` and callers.

## State and persistence behavior
`struct md4_ctx` is caller-owned mutable state. The header fixes its shape, so all update/final calls must use the same context instance for a digest stream. No global persistence exists.

## Dependencies and integration points
The header depends on `linux/types.h` for `u32`, `u64`, and `u8`. It integrates with the SMB common Makefile and any authentication code needing the exported MD4 helpers.

## Risks and test signals
Changing constants or context layout would break the implementation and any stack/static allocations. Test signals are compile coverage for all users, sparse/type checks, and MD4 known-answer tests through the public three-call API.
