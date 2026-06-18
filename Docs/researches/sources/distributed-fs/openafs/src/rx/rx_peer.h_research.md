# sources/distributed-fs/openafs/src/rx/rx_peer.h

## Purpose
Defines `struct rx_peer`, the RX representation of a remote process identified by `(host, port)`.

## Important APIs, Types, And Functions
Key fields are hash/free-list `next`, optional `peer_lock`, network-order `host` and `port`, interface and negotiated MTU fields (`ifMTU`, `natMTU`, `maxMTU`, `MTU`, `maxDgramPackets`, `ifDgramPackets`, `nDgramPackets`), lifetime fields (`idleWhen`, `refCount`), RTT/congestion counters (`rtt`, `rtt_dev`, `nSent`, `reSends`, `cwind`, `congestSeq`), byte counters, RPC stats queue, reachability time, max acknowledged packet size, and optional Linux error-queue state.

## Control Flow
The header has no executable flow. Peer objects are initialized by peer lookup code and `rxi_InitPeerParams`, then updated by transmit, receive, RTT, congestion, debug, and network-error paths.

## State And Persistence
Peer state persists in memory for as long as the peer remains referenced or cached. It records transport tuning and statistics across calls to the same remote `(host, port)`, but no state is persisted to disk.

## Dependencies And Integration Points
It depends on RX primitive types, optional lock types, atomics, and `opr_queue`. `rx_packet.c` reads peer MTU and updates `bytesSent`; `rx_user.c` initializes peer network parameters; debug packet handling exports much of the structure through `rx_debugPeer`.

## Risks And Test Signals
Risks include lock discipline around `peer_lock` versus `rx_peerHashTable_lock`, stale MTU/congestion values affecting new calls, and byte-order mistakes for `host` and `port`. Useful signals are peer debug output, RTT/congestion behavior under loss, path-MTU adaptation, and network error reporting tests.
