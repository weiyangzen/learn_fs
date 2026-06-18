# sources/distributed-fs/ceph-client/fs/smb/server/ndr.h

## Purpose
Defines the minimal NDR buffer abstraction and declares the xattr encode/decode functions used by ksmbd ACL and DOS attribute persistence.

## Important APIs, Types, and Functions
- `struct ndr` contains `char *data`, current `offset`, and current `length`.
- `NDR_NTSD_OFFSETOF` defines an offset constant for NT security descriptor-related encoding.
- Declared public functions: `ndr_encode_dos_attr()`, `ndr_decode_dos_attr()`, `ndr_encode_posix_acl()`, `ndr_encode_v4_ntacl()`, `ndr_encode_v3_ntacl()`, and `ndr_decode_v4_ntacl()`.

## Control Flow
Callers allocate a `struct ndr` on the stack or in another object, pass it to an encoder or decoder with domain-specific xattr structures, then consume or free `n->data` according to the operation. Encoders initialize and allocate the backing buffer; decoders expect `data` and `length` to describe an existing blob.

## State and Persistence
The header carries no global state. It defines the in-memory buffer that becomes the serialized xattr payload. Ownership and freeing of `data` are external to the header.

## Dependencies and Integration Points
The prototypes reference `struct xattr_dos_attrib`, `struct xattr_smb_acl`, `struct xattr_ntacl`, `struct mnt_idmap`, and `struct inode`, supplied by ksmbd and Linux VFS headers included by translation units. It is consumed by xattr/ACL VFS code.

## Risks and Edge Cases
- There is no include guard in the visible header, so multiple inclusion relies on source discipline or surrounding includes.
- `offset` and `length` are `int`, while buffer sizes are often `size_t`; very large blobs risk signed overflow if ever permitted upstream.
- `ndr_encode_v3_ntacl()` is declared but not implemented in the adjacent `ndr.c`; link coverage should verify whether another file provides it or the declaration is stale.
- Callers must know whether a function allocates `data` or expects it to be pre-populated.

## Test Signals
Compile all consumers with warnings enabled to catch missing declarations and duplicate inclusion problems. Link tests should verify every declared symbol is provided. Runtime tests should confirm encoder allocation ownership and decoder behavior on caller-provided buffers.
