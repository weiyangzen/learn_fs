# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.h

## Purpose

This header exposes the AF_XDP test library API and inline ring helpers used by selftests. It mirrors the libbpf xsk API shape closely enough for tests to create UMEMs, sockets, manipulate producer/consumer rings, and access UMEM data.

## Important APIs, Types, and Functions

`DEFINE_XSK_RING` defines `struct xsk_ring_prod` and `struct xsk_ring_cons`. Inline helpers include `xsk_ring_prod__fill_addr`, `xsk_ring_cons__comp_addr`, `xsk_ring_prod__tx_desc`, `xsk_ring_cons__rx_desc`, `xsk_ring_prod__needs_wakeup`, `xsk_ring_prod__reserve`, `xsk_ring_prod__submit`, `xsk_ring_prod__cancel`, `xsk_ring_cons__peek`, `xsk_ring_cons__cancel`, `xsk_ring_cons__release`, and UMEM address helpers. Public structs are `xsk_umem_config` and `xsk_socket_config`; public prototypes cover UMEM/socket creation, deletion, fd access, XDP attach/map operations, mode query, and MTU setting.

## Control Flow

The inline ring flow caches producer/consumer indices, uses acquire loads when refreshing peer pointers, advances cached indices on reserve/peek, and uses release stores when submitting or releasing entries. Higher-level creation/deletion flow is implemented in `xsk.c`.

## State and Persistence Behavior

Ring structs store mmapped kernel/user shared pointer locations, masks, sizes, flags, and cached indices. UMEM and socket objects are opaque and owned by `xsk.c`.

## Dependencies and Integration Points

It depends on `<linux/if_xdp.h>`, libbpf BPF program/map types, atomic builtins, and exact AF_XDP ring semantics. It is included by AF_XDP tests and `xdp_hw_metadata.c`.

## Risks and Test Signals

Risks include memory-barrier regressions, cached index underflow/overflow, non-power-of-two ring sizes, and UMEM unaligned-address interpretation mistakes. Signals are correct packet ordering, no descriptor reuse before release, need-wakeup behavior, and stable multi-buffer/unaligned tests.
