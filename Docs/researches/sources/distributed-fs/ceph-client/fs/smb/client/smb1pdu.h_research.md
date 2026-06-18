# sources/distributed-fs/ceph-client/fs/smb/client/smb1pdu.h

## Purpose
`smb1pdu.h` is the SMB1/CIFS protocol data-unit definition header. It centralizes command codes, flags, capabilities, info levels, packed request/response structures, Unix extension records, DFS referral records, ACL/xattr formats, and helper constants used by SMB1 command construction and parsing.

## Important APIs, types, and functions
The file defines protocol selectors, SMB command codes, Trans2/NT Transact subcommands, header sizing constants, crypto/session sizes, SMB flags/flags2, create/open/share options, capability bits, search flags, file information levels, Unix extension capability masks, and many packed structures. Key structures include `SMB_NEGOTIATE_RSP`, `SESSION_SETUP_ANDX`, `TCONX_REQ/RSP`, `OPEN_REQ/RSP`, legacy `OPENX_REQ/RSP`, `READ_REQ/RSP`, `WRITE_REQ/RSP`, `LOCK_REQ`, transaction/NT transaction wrappers, query/set path/file info requests, find-first/find-next records, DFS referral records, `FILE_ALL_INFO`, `FILE_UNIX_BASIC_INFO`, POSIX ACL records, EA records, and `xsymlink`.

## Control flow
There is no executable control flow. The header defines the exact wire layouts consumed by SMB1 command helpers, transport validation, session setup, open/read/write, metadata query/set, directory enumeration, DFS referral parsing, ACL/xattr code, and Unix extension paths.

## State and persistence
The structures describe transient SMB requests/responses and durable server metadata such as file attributes, timestamps, allocation size, Unix mode/uid/gid/device fields, POSIX ACL entries, EAs, and symlink payload formats. Endianness annotations and `__packed` layout are critical persistence/interop contracts.

## Dependencies and integration points
It includes the common SMB1 header and is used by `smb1proto.h`, SMB1 command implementation files, session setup, transport, signing, debug, metadata, DFS, ACL, xattr, and reparse paths. Many common CIFS abstractions convert these SMB1 layouts into SMB2-like internal structures such as `smb2_file_all_info` for shared upper-layer code.

## Risks and test signals
Risks include structure packing drift, duplicate capability macro definitions, endian misuse, flexible-array bounds errors, byte-count/offset mismatches, old-server layout quirks, and info-level constants diverging from command implementations. Test signals include compile-time structure layout assumptions, malformed PDU validation, negotiate/session/tcon interop with old and NT-capable servers, large read/write limits, directory enumeration at multiple info levels, Unix extension metadata round trips, DFS referrals, ACL/xattr requests, and reparse tag attribute parsing.
