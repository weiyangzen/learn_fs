# sources/distributed-fs/ceph-client/include/net/xdp_sock.h

## Purpose

`xdp_sock.h` defines AF_XDP socket and UMEM internal state, XSK map layout, socket lifecycle states, generic receive/redirect entry points, and TX metadata callbacks used by drivers and AF_XDP core.

## Important APIs, types, and functions

Key types are `struct xdp_umem`, `struct xsk_map`, `struct xdp_sock`, and `struct xsk_tx_metadata_ops`. AF_XDP functions under `CONFIG_XDP_SOCKETS` include `xsk_generic_rcv()`, `__xsk_map_redirect()`, `__xsk_map_flush()`, and `xsk_destruct_skb()`. Metadata helpers are `xsk_tx_metadata_to_compl()`, `xsk_tx_metadata_request()`, and `xsk_tx_metadata_complete()`.

## Control flow

AF_XDP setup creates UMEM, binds an `xdp_sock` to a netdevice queue, and optionally uses an XSK map for BPF redirect. Receive paths either enqueue XDP buffers to the socket or redirect through the map and later flush pending sockets. Generic TX builds SKBs from TX descriptors and can resume partially built packets through `xs->skb`. Driver TX paths inspect metadata at submission, request timestamp/checksum/launch-time offloads, save completion pointers, and fill completion timestamps when hardware completes.

## State and persistence behavior

`struct xdp_umem` persists pinned user memory, page array, chunk geometry, flags, users refcount, DMA list, and work item. `struct xdp_sock` embeds `struct sock`, RX/TX queues, UMEM/pool pointers, bound device/queue, zero-copy and scatter-gather flags, state enum, TX budget, drop stats, partial SKB, map membership, and control mutex. XSK maps store RCU socket pointers and atomic count.

## Dependencies and integration points

It depends on BPF maps, workqueues, AF_XDP UAPI, socket core, locks, MM, and optional `CONFIG_XDP_SOCKETS`. It integrates with BPF redirect maps, AF_XDP bind/send/recv, NIC zero-copy drivers, generic SKB fallback, and TX metadata UAPI.

## Risks and test signals

Risks include UMEM lifetime/refcount bugs, map updates racing with redirect, starvation if TX budget accounting fails, stale completion metadata pointers into user UMEM, unsupported metadata silently ignored, and disabled-config stubs returning different errors. Tests should cover bind/unbind, shared and non-shared UMEM, XSK map redirect/flush, generic receive/TX, partial multi-buffer TX resume, metadata timestamp/checksum/launch-time, and `CONFIG_XDP_SOCKETS` disabled builds.
