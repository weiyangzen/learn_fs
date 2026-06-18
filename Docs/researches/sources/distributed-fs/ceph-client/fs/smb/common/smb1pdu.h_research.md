# sources/distributed-fs/ceph-client/fs/smb/common/smb1pdu.h

Read coverage: full file.

## Purpose
`smb1pdu.h` defines minimal SMB1 protocol data units shared by common code, primarily the SMB1 header and negotiate request layout.

## Important APIs, types, and functions
`SMB1_PROTO_NUMBER` is the little-endian protocol marker for `0xff 'S' 'M' 'B'`. `struct smb_hdr` models the SMB1 header, including command, DOS/CIFS status union, flags, pid/tid/uid/mid fields, signature/sequence union, and word count. `SMB_NEGOTIATE_REQ` is a packed negotiate request with `struct smb_hdr`, `ByteCount`, and flexible `DialectsArray`.

## Control flow
There is no executable logic. These packed definitions are consumed by SMB1 negotiate and parsing code.

## State and persistence behavior
No state is stored in the header. The definitions encode wire-visible persistent protocol shape and field sizes.

## Dependencies and integration points
The file expects kernel endian conversion helpers to be available to users of `SMB1_PROTO_NUMBER`. It integrates with SMB1 negotiation and legacy CIFS header parsing paths.

## Risks and test signals
SMB1 is legacy and security-sensitive. Risks are wrong packing, endian misuse on `Tid` and `Uid` fields that are declared as `__u16`, and accidental changes to header size. Test signals include compile-time size checks, SMB1 negotiate packet construction tests, and parsing captures from known SMB1 servers when SMB1 support is enabled.
