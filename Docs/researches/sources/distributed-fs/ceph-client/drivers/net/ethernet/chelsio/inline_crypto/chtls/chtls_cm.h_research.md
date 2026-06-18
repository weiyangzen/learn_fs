# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls_cm.h

## Purpose

`chtls_cm.h` defines connection-manager constants, TCB bitfield helpers, TX header sizing, TLS content type values, deferred SKB metadata, request-socket helpers, accept queue macros, and WR queue primitives used by the Chelsio inline TLS connection manager and I/O code.

## Important APIs, Types, and Functions

- TCB/TLS field macros include `TCB_ULP_TYPE_*`, `TCB_ULP_RAW_*`, `TF_TLS_*`, and `TF_RX_QUIESCE_*`.
- Window and payload constants include `MAX_RCV_WND`, `MIN_RCV_WND`, `MAX_MSS`, `TX_HEADER_LEN`, `TX_TLSHDR_LEN`, and `TXDATA_SKB_LEN`.
- TLS record content enums map TLS header types to Chelsio SFO types.
- `struct deferred_skb_cb` and `DEFERRED_SKB_CB()` carry deferred handler state in `skb->cb`.
- `chtls_defer_reply()` is declared for deferred processing.
- `chtls_init_rsk_ops()` initializes request-socket ops for IPv4/IPv6 protocol replacements.
- Queue helpers include `chtls_free_skb()`, `chtls_kfree_skb()`, `chtls_reset_wr_list()`, `enqueue_wr()`, and `dequeue_wr()`.

## Control Flow

The header provides small inline pieces used in larger flows. `chtls_init_rsk_ops()` wires new protocol structures to existing TCP request socket slabs. `enqueue_wr()` and `dequeue_wr()` maintain the linked list of outstanding work requests, taking an SKB reference when enqueued and clearing `next_wr` on dequeue. Wakeup and request-address helpers are used during passive accept and receive processing.

## State and Persistence Behavior

No persistent state is stored here. The macros operate on socket queues, SKB control blocks, request sockets, and `chtls_sock` WR list pointers. State is in memory and tied to sockets/SKBs.

## Dependencies and Integration Points

This header depends on `chtls.h` structures and Linux TCP request-socket internals. It provides glue between Chelsio CPL/TLS hardware fields and the TCP socket/request APIs used by `chtls_cm.c`, `chtls_io.c`, and `chtls_hw.c`.

## Risks and Edge Cases

- The TLS error macros contain typo-prone shift references; hardware error reporting should be tested carefully.
- `enqueue_wr()` increments SKB references, so every successful dequeue path must free or put exactly once.
- `ACCEPT_QUEUE(sk)` reaches into request queue internals; kernel API changes can break assumptions.
- Inline free helpers steal dst refs before unlinking; callers must pass SKBs that really are on the expected queue.

## Test Signals

Tests should cover WR list enqueue/dequeue under credit ACKs, request-socket allocation/destruction, accept queue unlinking, RX queue free paths, and TCB quiesce/key field programming.
