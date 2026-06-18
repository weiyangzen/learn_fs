# sources/distributed-fs/ceph-client/fs/smb/server/ndr.c

## Purpose
Implements a small Network Data Representation encoder/decoder for ksmbd extended attributes, especially DOS attributes, POSIX ACL snapshots, and v4 NT ACL blobs stored in xattrs. It serializes primitive little-endian values and byte/string fields into dynamically grown `struct ndr` buffers and parses those buffers back with bounds checks.

## Important APIs, Types, and Functions
- Internal helpers `ndr_get_field()`, `try_to_realloc_ndr_blob()`, `ndr_write_int16/32/64()`, `ndr_write_bytes()`, `ndr_write_string()`, `ndr_read_string()`, `ndr_read_bytes()`, and `ndr_read_int16/32/64()` maintain `n->offset`, `n->length`, and `n->data`.
- `ndr_encode_dos_attr()` encodes `struct xattr_dos_attrib` version 3 or 4 fields, including hex attr string, duplicated version, flags, attrs, optional EA/size/allocation/change-time fields, and timestamps.
- `ndr_decode_dos_attr()` validates version 3 or 4, validates duplicate version, skips unsupported/unused fields, and extracts attributes plus creation/itime fields.
- `ndr_encode_posix_acl()` serializes optional access/default SMB ACL references, inode owner/group/mode translated through `mnt_idmap`, and ACL entries via `ndr_encode_posix_acl_entry()`.
- `ndr_encode_v4_ntacl()` serializes version, level/ref id, hash metadata, descriptor string, current time, POSIX ACL hash, and security descriptor bytes from `struct xattr_ntacl`.
- `ndr_decode_v4_ntacl()` validates version 4 and duplicate version, reads hash metadata, requires descriptor text beginning with `posix_acl`, allocates `acl->sd_buf`, and copies the remaining security descriptor bytes.

## Control Flow
Each public encoder initializes the supplied `struct ndr` to offset zero, allocates an initial zeroed buffer, then emits fields in the Samba-compatible xattr order. Primitive write helpers grow the blob by 1024 bytes when the next field would exceed the current allocation. Decoders reset offset to zero and advance sequentially, returning `-EINVAL` on truncation or malformed version data and `-ENOMEM` on allocation failure. POSIX ACL encoding writes reference ids for present ACLs, then owner/group/mode, then one or two ACL entry arrays.

## State and Persistence
The only mutable state is the caller-provided `struct ndr` buffer. Encoded blobs are intended for xattr persistence by VFS/xattr code outside this file. Decoding `v4_ntacl` allocates `acl->sd_buf`; callers must free it. On encode failure after allocation, this file does not free `n->data`; ownership remains with caller/error path.

## Dependencies and Integration Points
This file depends on ksmbd xattr structures from `glob.h`, Linux inode/idmap helpers, endianness helpers, and memory allocation. It integrates with VFS xattr get/set code for DOS attributes and ACL/security descriptors, and with SMB ACL conversion code that prepares `xattr_smb_acl` and `xattr_ntacl` structures.

## Risks and Edge Cases
- `try_to_realloc_ndr_blob()` always adds 1024 to `n->length` rather than setting it to the true allocation size `offset + sz + 1024`; when `sz` is much larger than 1024, subsequent bounds accounting can understate allocated space and force repeated reallocations or confuse callers.
- Encoders leak the already allocated `n->data` unless caller cleanup handles every error return.
- Several casts write directly to potentially unaligned `char *` offsets; architectures requiring aligned access rely on compiler/architecture tolerance or need unaligned helpers.
- `ndr_read_string()` copies `len` bytes without appending a NUL to `value`; local fixed buffers are safe only if initialized or if the consumed string already fits with terminator semantics.
- `ndr_decode_v4_ntacl()` ignores the return value from reading the 10-byte descriptor before `strncmp()`, so a truncated blob could leave stale descriptor contents unless the caller zeroed the structure.
- `ndr.h` declares `ndr_encode_v3_ntacl()` but this file does not define it, so another object or dead declaration must satisfy builds.

## Test Signals
Test round trips for DOS attr versions 3 and 4, malformed versions, duplicate-version mismatch, and truncated blobs at every field boundary. Exercise POSIX ACL encoding with no ACLs, access only, access plus default, user/group entries, high uid/gid idmapped values, and large ACL counts that trigger realloc. Validate v4 NTACL encode/decode with expected `posix_acl` descriptor, bad descriptor, truncated hash/descriptor/security descriptor, and caller cleanup under fault-injected `kzalloc`/`krealloc`.
