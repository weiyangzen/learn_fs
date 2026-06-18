# sources/distributed-fs/openafs/src/rx/rx_peer.c

## Purpose
Provides small accessor wrappers for `struct rx_peer` host and port fields.

## Important APIs, Types, And Functions
`rx_HostOf(struct rx_peer *peer)` returns `peer->host`; `rx_PortOf(struct rx_peer *peer)` returns `peer->port`. Both values are stored in network byte order.

## Control Flow
There is no branching or lifecycle logic. Callers pass an initialized peer pointer and receive the stored host or UDP port.

## State And Persistence
The file owns no state. It reads fields from peer objects owned by RX peer hash-table management elsewhere.

## Dependencies And Integration Points
It includes `rx.h`, `rx_atomic.h`, `rx_clock.h`, and `rx_peer.h`, giving external code stable functions instead of direct structure access. These functions integrate with consumers that need peer addressing without including private peer internals.

## Risks And Test Signals
The only meaningful risks are null pointers and byte-order misunderstandings by callers. Build/link coverage and debug output showing expected peer addresses are sufficient signals.
