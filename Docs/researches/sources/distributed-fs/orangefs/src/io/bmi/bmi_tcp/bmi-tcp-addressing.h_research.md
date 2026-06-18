# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp-addressing.h

## Purpose
`bmi-tcp-addressing.h` defines TCP-specific address state for the OrangeFS BMI TCP method. It is a private method header that records how a BMI method address maps to a TCP socket, peer host/port metadata, socket-collection bookkeeping, reconnect policy, partial-read tracking, and optional trusted-connection rules.

## Important APIs, Types, and Definitions
`BMI_TCP_ZERO_READ_LIMIT` is the maximum number of sequential zero-byte reads tolerated before treating a TCP connection as dead. `BMI_TCP_HEADER_WAIT_SECONDS` caps how long the TCP method waits for the rest of a partial BMI header after detecting part of it.

`BMI_TCP_PEER_IP` and `BMI_TCP_PEER_HOSTNAME` identify the interpretation of the `peer` field in `struct tcp_addr`.

When `USE_TRUSTED` is enabled, `struct tcp_allowed_connection_s` describes policy for accepted peers. It can enforce a port range, enforce network membership, store a count of allowed networks, and hold arrays of network and netmask `struct in_addr` values.

`struct tcp_addr` is the main TCP per-address record. It stores the owning generic BMI method address (`map`), BMI address id, address-level error code, hostname and zone strings, port, socket fd, server-port marker, pending write reference count, not-connected flag, socket collection link/index, sequential zero-read count, partial-header timer, reconnect suppression flag, peer string, and peer type.

The header aliases `bmi_tcp_errno_to_pvfs` to the shared `bmi_errno_to_pvfs` mapper, and declares `tcp_forget_addr` and `alloc_tcp_method_addr`.

## Control Flow and Integration
This header contains declarations and state layout rather than executable code. The TCP BMI implementation fills `struct tcp_addr` as addresses are parsed, connections are accepted or initiated, sockets are added to socket collections, reads/writes are posted, failures occur, and reconnect decisions are made.

`tcp_forget_addr` is the cleanup/invalidation entry point: callers pass a generic method address, a deallocation flag, and an error code. Based on the fields here, that function is expected to close or detach sockets, update address error state, remove socket collection links, and optionally free address storage. `alloc_tcp_method_addr` creates a generic BMI method address with enough TCP-specific private data to hold `struct tcp_addr`.

The zero-read and short-header constants are consumed by receive-side logic. `zero_read_limit` tracks repeated EOF-like reads that may signal dead peers. `short_header_timer` supports bounded waits for a complete BMI protocol header after a partial header arrives.

## State and Persistence Behavior
All state is process-local and tied to live TCP method addresses. `struct tcp_addr` persists as long as the generic BMI method address remains live. It can outlive a specific socket across reconnect attempts unless `dont_reconnect` is set or cleanup deallocates it.

`write_ref_count` tracks pending sends to avoid freeing or reconnecting address state while writes are active. `not_connected`, `addr_error`, and `dont_reconnect` together describe connection health and future reconnect behavior. `sc_link` and `sc_index` persist the address's membership in a socket collection.

No fields are written to disk by this header; persistence here means lifetime within the OrangeFS process and BMI address registry.

## Dependencies and Integration Points
The header depends on BMI core types through `bmi-types.h`, IPv4 address structures from `<netinet/in.h>`, and quicklist linkage through the `struct qlist_head` member made available by included BMI/common headers in the TCP implementation build context.

It integrates with the BMI TCP method's socket collection, method-address allocation, address-forget cleanup, reconnect logic, trusted-connection filtering, and BMI error mapping. It is separate from the RDMA files in this work item but plays a similar role for TCP private method address state.

## Risks and Edge Cases
The header is IPv4-centric: trusted network policy uses `struct in_addr`, and `struct tcp_addr` stores host/port as strings plus integer port without visible IPv6-specific fields. IPv6 support, if present elsewhere, would require additional handling.

The ownership of string fields (`hostname`, `zone`, and `peer`) is not documented here. Cleanup correctness depends on `tcp_forget_addr` and allocation/parsing code following consistent ownership rules.

`write_ref_count`, reconnect flags, socket collection indices, and socket fd state can become inconsistent if error paths do not update them together. The header exposes mutable fields directly, so invariants are distributed across implementation files.

`zero_read_limit` and `short_header_timer` are per-address counters/timers; tests should ensure they are reset on successful reads/reconnects and not inherited incorrectly across new sockets.

`USE_TRUSTED` policy stores arrays by pointer without lengths beyond `network_count`, so allocation and cleanup must keep those arrays synchronized. Port policy uses a two-element `ports` array whose ordering and inclusivity are not documented in the header.

## Test Signals
TCP method tests should cover address allocation and cleanup, hostname/zone/peer ownership, active write references during cleanup, server-port addresses, reconnect and `dont_reconnect` behavior, repeated zero-byte reads crossing `BMI_TCP_ZERO_READ_LIMIT`, partial-header timeout handling, socket collection add/remove bookkeeping, and trusted network/port filtering when `USE_TRUSTED` is enabled.

Static checks should verify every `struct tcp_addr` field is initialized in `alloc_tcp_method_addr` or address parsing paths, and that `tcp_forget_addr` clears socket collection links and frees owned strings consistently.
