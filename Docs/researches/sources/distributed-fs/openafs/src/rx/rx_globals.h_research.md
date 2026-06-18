# Research: sources/distributed-fs/openafs/src/rx/rx_globals.h

## sources/distributed-fs/openafs/src/rx/rx_globals.h

### Purpose
`rx_globals.h` declares or defines RX's process/kernel global state and tuning variables depending on `GLOBALSINIT`. It is the central configuration and shared-state header for RX internals.

### Important State
- Sockets/services: `rx_socket`, `rx_services`, server pool locks, port and dead/idle timings.
- Packet pool and quota state: `rx_freePacketQueue`, `rx_mallocedPacketQueue`, `rx_nFreePackets`, `rx_packetQuota`, `rxi_dataQuota`, `rx_nPackets`, packet size and jumbo size limits.
- Thread-specific packet queue support for pthread builds: `rx_ts_info_key`, `rx_ts_info_t`, and `RX_TS_FPQ_*` macros.
- Connection/call state: free call queue, `rx_port`, select masks for LWP, `rx_nextCid`, `rx_epoch`, peer and connection hash tables, cleanup list, and locks.
- Tuning variables: window sizes, NACK threshold, datagram fragment counts, soft/hard ACK rates, send/receive frag counts, peer timeout minimums, and packet quota behavior.
- Debug/stat state: debug files, packet type strings, key-create destructors, abort throttling thresholds, stats flags, hot-thread flag, and IP/UDP size.

### Control Flow
Most content is declarations, definitions, or macros. Thread-specific free packet queue macros move packets between local and global queues, update counters, and recompute limits under packet locks. Allocation macros map typed RX objects onto `rxi_Alloc`/`rxi_Free`.

### Dependencies and Integration Points
Depends on `rx.h`, `rx_packet.h`, and platform locking/threading headers. It is consumed by packet allocation, call allocation, receive/transmit paths, service scheduling, debug and stats code, connection cache, LWP/pthread listeners, and kernel support.

### State and Persistence Behavior
All state is in-memory. Some values are exported over debug/stat protocols, but no durable persistence occurs.

### Risks and Edge Cases
- This file exposes many globals; ordering and lock discipline are critical and mostly enforced by convention.
- Thread-specific free packet queue macros assume locks are held as documented and can corrupt queues if misused.
- `FD_SETSIZE` manipulation must happen before system headers; include order matters.
- Packet size globals must never decrease in some cases while applications are running.
- A typo in comments names "Threshholds"; variable names preserve the historic spelling `Threshhold`.

### Test Signals
High-value tests include packet pool stress under pthread local queues, quota exhaustion/deadlock prevention tests, dynamic window tuning tests, hash table initialization/finalization tests, and debug/stat export validation.
