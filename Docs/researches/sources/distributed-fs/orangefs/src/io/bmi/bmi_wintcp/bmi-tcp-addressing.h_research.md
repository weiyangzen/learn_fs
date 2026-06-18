# sources/distributed-fs/orangefs/src/io/bmi/bmi_wintcp/bmi-tcp-addressing.h

## Purpose

This header defines the TCP-specific address metadata for the `bmi_wintcp` transport. It mirrors the Unix TCP address shape closely enough for shared-style transport logic, but it is located under the Windows TCP method tree.

## Important APIs, Types, And Macros

- `BMI_TCP_ZERO_READ_LIMIT` caps sequential zero-read observations before the transport treats a connection as dead.
- `BMI_TCP_HEADER_WAIT_SECONDS` caps how long a partial BMI TCP header may remain incomplete after detection.
- `BMI_TCP_PEER_IP` and `BMI_TCP_PEER_HOSTNAME` classify the cached peer string.
- Under `USE_TRUSTED`, `struct tcp_allowed_connection_s` stores trusted port and network enforcement state, allowed port range, network count, and network/netmask arrays.
- `struct tcp_addr` stores the backpointer to the generic BMI method address, BMI address handle, address error, hostname, port, socket fd, server-port flag, write reference count, connection state, socket-collection link/index, zero-read and short-header counters, reconnect policy, and cached peer string/type.
- `bmi_tcp_errno_to_pvfs` aliases `bmi_errno_to_pvfs`.
- Prototypes expose `tcp_forget_addr` and `alloc_tcp_method_addr`.

## Control Flow

The header has no executable control flow. It defines the state consumed by the WinTCP implementation and socket collection code. Address instances are expected to be allocated by `alloc_tcp_method_addr`, filled during lookup/connect/accept, updated by socket collection macros, and cleaned by `tcp_forget_addr`.

## State And Persistence Behavior

`struct tcp_addr` is the per-address in-memory persistence object for the transport. It records whether the socket is connected, whether reconnect is allowed, the last address-level error, current socket-collection index, pending write-interest count, zero-read counter, partial-header timer, and peer identity cache. No durable persistence is involved.

## Dependencies And Integration Points

The header depends on `bmi-types.h`, and under trusted builds it expects `struct in_addr` to be visible from the including context. It also uses `bmi_method_addr_p` and `struct qlist_head` without including their defining headers directly, so it relies on include order in the WinTCP source tree. It integrates with WinTCP's socket collection and BMI method implementation through the same field names used by the Unix TCP code.

## Risks And Edge Cases

- The file comments out `<netinet/in.h>` but trusted mode uses `struct in_addr`; Windows or compatibility headers must provide it before this header is parsed.
- It does not include the quicklist header even though `struct tcp_addr` embeds `struct qlist_head sc_link`.
- The Unix `bmi_tcp` version includes a `zone` field under `BMI_TCP_ZONE`; this WinTCP header does not. Shared code assumptions about `tcp_addr->zone` would not compile here.
- Socket descriptors are stored as `int`, which may be problematic if mapped directly to native Windows `SOCKET` handles without an abstraction layer.

## Test Signals

Build tests should compile the WinTCP transport with and without `USE_TRUSTED`, with strict include-order checks. Runtime-oriented tests should validate address allocation defaults, socket collection add/remove index updates, reconnect/error state transitions, peer string caching, zero-read limit handling, and partial-header timeout behavior in the WinTCP implementation.
