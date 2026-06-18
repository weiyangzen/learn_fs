# sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.h

## Purpose
`smb2pdu.h` defines SMB2/SMB3 wire-format constants and packed structures used by the client PDU implementation. It covers transform headers, create contexts, IOCTL payloads, query information payloads, POSIX extension records, and WSL-style extended attribute metadata.

## Important APIs, Types, And Functions
The header exports constants such as `SMB2_TRANSFORM_HEADER_SIZE`, `MAX_SMB2_HDR_SIZE`, `SMB2_READWRITE_PDU_HEADER_SIZE`, `COMPOUND_FID`, `SMB2_CREATE_IOV_SIZE`, `MAX_SMB2_CREATE_RESPONSE_SIZE`, `SMB2_IOCTL_IOV_SIZE`, and WSL xattr names/sizes. It declares `extern char smb2_padding[7]`.

Important structs include `smb2_rdma_transform`, `smb2_rdma_crypto_transform`, symlink and error-context response structs, share redirect error context structures, create contexts for timewarp/query-id/security descriptor/EA, FSCTL retrieval pointer structures, DFS referral request, network resiliency request, compression ioctl payload, EA/reparse/file-id query structures, `create_posix_rsp`, `smb2_posix_info`, `smb2_posix_info_parsed`, and `smb2_create_ea_ctx`.

## Control Flow
The header has no executable control flow. Its fields are consumed by `smb2pdu.c` when building create contexts and parsing returned file/directory metadata, and by RDMA/encryption paths when describing transform metadata.

## State And Persistence Behavior
All types are packed wire views or parsed helpers. They do not own lifetime or persistence. State becomes persistent only when callers copy decoded fields into `TCP_Server_Info`, `cifs_tcon`, inode/open metadata, or search buffers.

## Dependencies And Integration Points
The header depends on socket types and CIFS ACL/SID definitions. It ties protocol layout to ACL helpers, POSIX extension parsing, DFS, FSCTL, SMBDirect transform handling, and WSL xattr compatibility code.

## Risks
Because these structs model wire layout, alignment, endianness, packing, and flexible-array lengths are critical. Changing field order or sizes can silently break interoperability. Variable-length POSIX SID/name fields and WSL EA size macros require careful bounds checks in consumers. IOV and max-size constants must remain synchronized with contexts appended by `SMB2_open_init`.

## Test Signals
Compile-time layout checks, sparse/endian warnings, POSIX directory parsing, create-context interop, symlink/error-context parsing, WSL xattr query tests, and SMBDirect transform negotiation are the most relevant signals.
