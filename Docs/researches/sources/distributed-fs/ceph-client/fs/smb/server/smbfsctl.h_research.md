## sources/distributed-fs/ceph-client/fs/smb/server/smbfsctl.h

Purpose: centralizes SMB/CIFS/SMB2 FSCTL and reparse-tag numeric constants used by server IOCTL handling.

Important APIs and types: defines FSCTL codes for DFS referrals, oplock requests, compression/encryption/sparse/zero-data operations, allocated-range queries, duplicate extents, named-pipe operations, negotiate validation, network interface information, and server-side copychunk. It also defines classic and WSL/Linux reparse tags such as `IO_REPARSE_TAG_LX_SYMLINK_LE`, FIFO, character device, block device, and AF_UNIX.

Control flow: the header has no control flow; IOCTL handlers switch on these constants and encode/decode operation-specific payloads elsewhere.

State and persistence behavior: no runtime or persistent state is owned here. The reparse constants may influence persisted xattr or response data in other modules.

Dependencies and integration points: consumed by SMB2 IOCTL/FSCTL processing, copychunk handling, network-interface reporting, sparse/zero range VFS calls, and reparse-point support. It depends on endian conversion macros for little-endian WSL tags.

Risks: wrong numeric constants create wire-incompatible behavior that clients surface as unsupported or malformed FSCTL responses. Several entries are placeholders marked as future work, so handlers must reject unsupported codes cleanly instead of assuming struct definitions exist.

Test signals: FSCTL dispatch for validate-negotiate-info, query-network-interface-info, copychunk/copychunk-write, query-allocated-ranges, set-zero-data, pipe transceive, unsupported code status mapping, and WSL reparse tag endian output.
