# sources/distributed-fs/ceph-client/fs/smb/client/rfc1002pdu.h

## Purpose
`rfc1002pdu.h` defines NetBIOS-over-TCP session service packet types and the packed RFC 1002 session packet layout used around SMB session transport framing.

## Important APIs, types, and functions
The main type is `struct rfc1002_session_packet`, whose header uses big-endian length fields and whose trailer union models session requests, retarget responses, negative responses, and SMB message payloads. Constants define session packet types, the length-extension flag, negative session response error codes, and `DEFAULT_CIFS_CALLED_NAME`.

## Control flow
The file contains no executable code. Transport code includes these definitions when building or interpreting RFC 1002 session requests/responses and message wrappers before the SMB header begins.

## State and persistence
No persistent state exists. The structure describes transient network packets. The important state invariant is that this framing is big-endian, unlike SMB/CIFS message bodies.

## Dependencies and integration points
It integrates with low-level CIFS transport/session setup code and NetBIOS name-based connection paths. It deliberately omits datagram service definitions because the client resolves server names via DNS, IP address, or hosts-style mechanisms.

## Risks and test signals
Risks include endian mistakes in length/retarget fields, mishandling length extension for larger payloads, and treating keepalives or positive responses as carrying SMB trailers. Test signals include RFC 1002 session request/positive/negative/retarget parsing, keepalive handling, and large SMB message length encoding.
