# sources/distributed-fs/ceph-client/fs/smb/common/smb2pdu.h

Read coverage: full file.

## Purpose
`smb2pdu.h` is the common SMB2/SMB3 wire protocol definition header. It provides command codes, header layouts, negotiate/session/tree/create/read/write/lock/ioctl/query/set/notify/oplock/lease structures, dialect capabilities, crypto/compression constants, access masks, create options, security info bits, and POSIX extension layouts.

## Important APIs, types, and functions
Major constants include SMB2 command IDs in host and little-endian forms, cryptographic key/signature sizes, RFC header protocol numbers, SMB2 flags, dialect IDs, negotiate contexts, encryption/signing/compression algorithms, share flags/capabilities, file access/share/create options, create context names, lease/oplock constants, ioctl/copychunk structures, network interface response structures, query info classes, and security info masks.

Important structures include `smb2_hdr`, `smb3_hdr_req`, `smb2_pdu`, `smb2_err_rsp`, transform and compression headers, tree connect contexts and remoted identity data, negotiate request/response and negotiate context records, session setup/logoff/tree connect/close/read/write/flush/lock/echo/query directory/set info/change notify/create/ioctl/query info/oplock and lease break/ack PDUs. The header uses flexible arrays for variable payloads and static assertions for packed create-context offsets.

## Control flow
There is no runtime control flow. Client and server code use these packed structs to lay out outgoing requests and interpret incoming responses. The constants guide branch decisions in implementation files, such as negotiating dialects, computing signing/encryption transforms, validating read/write response sizes, building create contexts, and selecting query info classes.

## State and persistence behavior
The file has no local mutable state. It defines network-persistent state formats: session ids, tree ids, message ids, file ids, credit requests, lease keys, durable handle ids, negotiate capabilities, and security descriptors as represented on the wire. Any field layout or endian change is externally visible to SMB peers.

## Dependencies and integration points
The header depends on kernel type and build bug helpers. It is foundational for SMB client transport, session setup, tree connect, file create/open, I/O, locking, copy offload, compression/encryption, multichannel, RDMA, query/set info, notify, oplock/lease handling, and POSIX extensions. `transport.c` consumes read response sizing and command constants through dialect `server->vals` and ops; `xattr.c` uses security info flags defined here or adjacent common headers.

## Risks and test signals
Risks are dominated by wire compatibility: packing mistakes, wrong endian annotations, flexible-array length bugs, stale dialect capability constants, and unsafe assumptions about variable context padding. Security-sensitive areas include transform headers, signing/encryption algorithm negotiation, remoted identity contexts, security info masks, durable handle reconnects, and lease breaks. Test signals include build-time offset assertions, packet capture comparison against MS-SMB2 layouts, negotiate/session setup tests across SMB2.0 through SMB3.1.1, encrypted/compressed read/write, durable handles, leases/oplocks, copychunk/ioctl, query directory variants, POSIX create/query contexts, and malformed response fuzzing.
