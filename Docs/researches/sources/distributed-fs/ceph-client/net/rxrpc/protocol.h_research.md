<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/protocol.h -->
# sources/distributed-fs/ceph-client/net/rxrpc/protocol.h

## Purpose
`protocol.h` defines AF_RXRPC on-wire packet layout, fixed protocol constants, packet type/flag values, ACK payload/trailer structures, jumbo-packet sizing, and security challenge/response headers shared by TX, RX, and security modules.

## Important APIs, Types, And Functions
Important definitions include `rxrpc_seq_t`, `rxrpc_serial_t`, `struct rxrpc_wire_header`, connection/channel masks and shifts, packet type constants, packet flags, `struct rxrpc_jumbo_header`, `RXRPC_JUMBO_DATALEN`, `RXRPC_MAX_NR_JUMBO`, `RXRPC_JUMBO()`, `struct rxrpc_ackpacket`, ACK reason/type constants, `struct rxrpc_acktrailer`, `struct rxkad_challenge`, `struct rxkad_response`, `struct rxgk_header`, and `struct rxgk_response`.

## Control Flow
The header has no runtime control flow. It establishes the byte-exact network-order contract used by packet construction, parsing, verification, ACK/SACK generation, jumbo subpacket expansion, PMTU calculations, and security handshakes.

## State And Persistence
The structures describe transient wire state, not persistent in-memory ownership. Multi-byte fields are explicitly network byte order and packed. Constants such as `RXRPC_MAXCALLS` determine persistent connection channel array sizing elsewhere.

## Dependencies And Integration Points
`output.c`, `recvmsg.c`, input paths, RxKAD, RxGK, peer PMTU code, proc output, and tracepoints all depend on these definitions. User-status and security-index fields connect protocol framing with AuriStor service upgrade and security module dispatch.

## Risks And Edge Cases
Any layout or constant change is wire-protocol compatibility-sensitive. The flag bit `0x20` is overloaded as DATA jumbo and ACK slow-start support by packet type. Jumbo sizing assumes UDP/IP maximums and exact subpacket header accounting. The comment typo in RESPONSE does not affect ABI but signals this is legacy protocol surface.

## Test Signals
Build-time structure size/packing checks, interoperability with OpenAFS/YFS peers, jumbo boundary tests up to `RXRPC_MAX_NR_JUMBO`, ACK reason parsing, endian tests, and security challenge/response packet decode coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/protocol.h -->
