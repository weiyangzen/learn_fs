# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.h

## Purpose
Central private header for the socklnd implementation. It defines all in-memory driver objects, tunable pointers, scheduler state, connection and peer models, protocol operations, refcount helpers, constants, and cross-file function prototypes.

## Important APIs and types
`struct ksock_sched` owns per-CPT RX/TX work queues and scheduler thread accounting. `struct ksock_interface`, `struct ksock_net`, and `struct ksock_nal_data` model selected network interfaces, per-NI state, and global driver state. `struct ksock_tx` wraps an LNet message or NOOP, including header iov, page payloads, zero-copy cookies, deadlines, and health status. `struct ksock_conn` tracks one socket, callback replacements, refcounts, RX state machine, TX queue, deadlines, and scheduler assignment. `struct ksock_conn_cb` is the route/reconnect controller. `struct ksock_peer_ni` aggregates all connections and pending work for a peer. `struct ksock_proto` provides per-wire-version operations.

## Control flow and integration
The header binds together `socklnd.c` lifecycle, `socklnd_cb.c` data path, `socklnd_lib.c` socket primitives, `socklnd_proto.c` protocol variants, and `socklnd_modparams.c` tunables. Inline helpers manage reference transitions for conns, sockets, TXs, conn control blocks, and peers. The public LND callback prototypes are here so the module registration table can bind to them.

## State and persistence
All declared structures are runtime kernel memory with explicit list ownership and refcounting. RX state constants define the receive parser stages: socklnd header, LNet header, parse handoff, payload, and slop skipping. Timeout helpers read mutable module tunables or LNet defaults.

## Dependencies
Depends on Linux kernel networking, TCP, kthreads, crypto CRC32, libcfs, LNet internals, and the wire IDL header. `SOCKNAL_RISK_KMAP_DEADLOCK` changes behavior by build configuration.

## Risks and test signals
Layout and bitfield widths affect concurrency and connection-count correctness. Refcount helper misuse can leak sockets or free live peers. Test coverage should stress lifecycle transitions, callback replacement/reset, RX parser state changes, zero-copy completion, typed vs untyped connections, and conns-per-peer bounds.
