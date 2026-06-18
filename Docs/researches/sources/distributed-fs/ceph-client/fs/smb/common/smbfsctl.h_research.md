# sources/distributed-fs/ceph-client/fs/smb/common/smbfsctl.h

Purpose: centralizes SMB/CIFS/SMB2 FSCTL and IOCTL protocol constants shared by client and server code. These values identify remote filesystem-control operations, named-pipe controls, server-side copy/offload operations, reparse tags, and flags used in SMB2 IOCTL packets.

Important APIs/types/functions: the header defines bit-field masks for FSCTL device, access, function, and method components; many `FSCTL_*` codes including DFS referrals, oplock requests, reparse point management, sparse/zero data, snapshot enumeration, resume keys, `FSCTL_VALIDATE_NEGOTIATE_INFO`, copychunk, and network-interface query; reparse tags such as `IO_REPARSE_TAG_SYMLINK`, `IO_REPARSE_TAG_NFS`, and WSL tags; `IS_REPARSE_TAG_NAME_SURROGATE(tag)`; and `SMB2_0_IOCTL_IS_FSCTL`.

Control flow: there is no local execution. SMB2 IOCTL handlers dispatch on the `CtlCode` field using these constants. Reparse-aware paths use the tag definitions and name-surrogate macro to decide whether an object is a link-like namespace substitution or an application-specific reparse object.

State and persistence behavior: no mutable state is present. Reparse tag values may be persisted in filesystem xattrs or reparse buffers by consumers, so the numeric constants are a wire/storage ABI.

Dependencies and integration points: integrates with SMB2 IOCTL request handling, DFS support, named pipe forwarding, server-side copy, durable/resilient handle support, sparse file management, reparse point handling, and Windows compatibility logic. It intentionally includes codes for operations that may be unimplemented locally so switch statements can reject them with precise statuses.

Risks: incorrect FSCTL numbers or device/access/method bits break interoperability. Some constants are listed for future or partial support; implementing a dispatcher case without validating input/output buffer contracts can expose kernel memory or return malformed protocol data. Reparse tag handling is security-sensitive because name-surrogate tags affect path traversal semantics.

Test signals: cover IOCTL dispatch for supported FSCTLs, explicit `STATUS_NOT_SUPPORTED` or `STATUS_INVALID_DEVICE_REQUEST` for unsupported ones, DFS referral behavior, validate-negotiate integrity checks, sparse/zero range controls, reparse tag query/set/delete, named-pipe controls, and copychunk/resume-key behavior against Windows and Samba clients.
