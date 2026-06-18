# sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.h

## Purpose

`tcp_vegas.h` is the shared private-state and callback interface for Vegas-style congestion-control modules. It defines the `struct vegas` layout used by `tcp_vegas.c` and embedded as the first field of `struct yeah` in `tcp_yeah.c`, then declares reusable Vegas functions.

## Important APIs, Types, and Functions

The central type is `struct vegas`, containing `beg_snd_nxt`, `beg_snd_una`, `beg_snd_cwnd`, `doing_vegas_now`, `cntRTT`, `minRTT`, and `baseRTT`. Declared functions are `tcp_vegas_init()`, `tcp_vegas_state()`, `tcp_vegas_pkts_acked()`, `tcp_vegas_cwnd_event()`, `tcp_vegas_cwnd_event_tx_start()`, and `tcp_vegas_get_info()`.

## Control Flow

The header has no executable control flow. It establishes the ABI between congestion modules and the Vegas implementation: modules install declared callbacks in `struct tcp_congestion_ops` or call them from their own wrappers.

## State and Persistence Behavior

The struct fields persist per socket inside congestion-control private storage. `beg_*` fields delimit an RTT-sized measurement window, `doing_vegas_now` controls active sampling, `cntRTT` and `minRTT` are reset each RTT, and `baseRTT` persists as the long-term propagation-delay estimate.

## Dependencies and Integration Points

It assumes inclusion in TCP congestion-control modules with access to `struct sock`, `struct ack_sample`, `enum tcp_ca_event`, and `union tcp_cc_info` definitions through surrounding TCP headers. The layout is important for YeAH because `struct yeah` embeds `struct vegas` first and reuses exported Vegas callbacks.

## Risks and Edge Cases

Changing `struct vegas` size or order can break modules that embed it or rely on `ICSK_CA_PRIV_SIZE` constraints. Declared functions are GPL-exported by `tcp_vegas.c`, so build configuration and module dependencies must ensure symbols are available.

## Test Signals

Build tests should cover Vegas and YeAH modules together, including `BUILD_BUG_ON(sizeof(... ) > ICSK_CA_PRIV_SIZE)` checks. Runtime tests should verify YeAH callbacks operate on the embedded Vegas prefix correctly and inet_diag reporting remains consistent.
