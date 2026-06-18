# sources/distributed-fs/ceph-client/fs/smb/client/smb1proto.h

## Purpose
`smb1proto.h` declares the SMB1/CIFS implementation surface used by SMB1 ops, transport, session setup, metadata, ACL, xattr, and tests. It is gated by `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`, reflecting SMB1's legacy/insecure status.

## Important APIs, types, and functions
It defines `struct cifs_unix_set_info_args`, declares SMB1 command helpers such as negotiate, tree connect/disconnect, session logoff/setup, open/read/write/lock/close, query/set path and file info, find-first/next/close, DFS referral, Unix extension operations, reparse query/create, ACL/xattr helpers, signing/verification, map-error functions, misc helpers, and transport send/receive helpers. It also declares `smb1_operations`, `smb1_values`, `CIFS_SessSetup`, and test-only maperror exports. Inline helpers include `get_mid`, `compare_mid`, `BCC`, `pByteArea`, `get_bcc`, and `put_bcc`.

## Control flow
The header has no runtime flow beyond inline packet field access. Build-time gating removes the SMB1 declarations when insecure legacy SMB1 support is disabled. Callers assemble requests through declared command helpers and use inline helpers to locate the byte-count and byte area within variable-length SMB1 packets.

## State and persistence
No state is stored here. The declared APIs mutate server sessions, tree connections, open files, inodes, server-side metadata, locks, ACLs, EAs, reparse data, and transport request queues in their implementation files.

## Dependencies and integration points
The header integrates SMB1 PDU definitions, common SMB2 PDU definitions needed for shared structs, CIFS global structures, KUnit maperror tests, and the common dialect operation model. It is the main include boundary between SMB1 implementation units and common CIFS code.

## Risks and test signals
Risks include prototype drift from implementations, unsafe byte-area pointer arithmetic on malformed packets, unaligned field access, missing declarations under config combinations, and SMB1-only types leaking into common code. Test signals include all SMB1 config combinations, KUnit maperror exports, sparse/build warnings for prototypes, packet byte-count helper tests, and transport send/receive paths using multi-iov requests.
