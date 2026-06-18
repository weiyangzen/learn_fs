# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/chtls.h

## Purpose

`chtls.h` is the central private header for the Chelsio inline TLS TOE driver. It defines TLS key-context bitfields, device/socket state objects, SKB control-block layouts, helper macros, and cross-file function prototypes used by `chtls_main.c`, `chtls_cm.c`, `chtls_io.c`, and `chtls_hw.c`.

## Important APIs, Types, and Functions

- `struct chtls_dev` represents one Chelsio TLS TOE device and stores `tls_toe_device`, LLDI, ports, TID tables, response SKB cache, deferred queue, key map, listen hash, and sizing limits.
- `struct chtls_sock` is per-offloaded socket state: socket pointer, device, L2T/egress device, TX queues, WR credit accounting, TID, qid/channel/port metadata, flags, windows, and embedded `struct chtls_hws`.
- `struct chtls_hws` stores TLS hardware state: receive TLS queue, TX/RX key IDs, record parameters, key length, maximum fragment size, sequence number, and copied TLS crypto info.
- `struct key_map` tracks hardware TLS key-context slots with a bitmap and lock.
- `struct listen_info`, `struct listen_ctx`, and `struct chtls_listen` support passive-open registration.
- SKB control blocks: `wr_skb_cb`, `blog_skb_cb`, and `ulp_skb_cb` attach WR chaining, backlog callbacks, sequence flags, and TLS metadata to `skb->cb`.
- Inline helpers include `to_chtls_dev()`, `csk_set_flag()`, `csk_reset_flag()`, `csk_flag()`, `process_cpl_msg()`, refcount helpers, and `send_or_defer()`.
- Prototypes expose listener, socket, send/receive, TCB, key, and WR functions across implementation files.

## Control Flow

The header establishes shared conventions for CPL processing. `process_cpl_msg()` resets SKB headers, locks the socket with bottom halves, and either invokes a handler immediately or queues the SKB to the socket backlog when user context owns the socket. TX-side files use `ULP_SKB_CB()` and `WR_SKB_CB()` to track queued WRs and application data. Connection-manager files use `BLOG_SKB_CB()` to reroute deferred processing through a listener or child socket backlog.

## State and Persistence Behavior

All state is in-memory and socket/device scoped. `chtls_sock` lifetime is tied to socket user-data and a `kref`; `chtls_dev` lifetime is tied to `tls_toe_device.kref`. WR credits, TID IDs, TLS key IDs, receive queues, and listen hashes are maintained in these structures and are reset on close/detach.

## Dependencies and Integration Points

The header depends on Linux crypto, TLS, TCP, `tls_toe`, Chelsio CPL/FW APIs, L2T, ULD, and Chelsio crypto core headers. It integrates with Linux socket protocol replacement, TLS setsockopt/getsockopt, and `cxgb4` offload send helpers.

## Risks and Edge Cases

- `skb->cb` is shared storage; every path must agree on which control block layout is active.
- `csk_flag()` checks `CSK_CONN_INLINE` before reading flags; callers that already know inline state use `csk_flag_nochk()`.
- The header contains bitfield macros for hardware layouts; incorrect shifts/masks would be hard to detect without hardware tests.
- Device/socket object lifetimes depend on RCU socket user-data and refcount discipline across multiple files.

## Test Signals

Build tests should cover IPv4-only and IPv6-enabled configurations. Runtime signals include clean protocol replacement/restoration, correct socket backlog handling under owned sockets, WR credit accounting consistency, and TLS key allocation/free balance.
