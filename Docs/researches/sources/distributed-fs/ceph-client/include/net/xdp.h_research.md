# sources/distributed-fs/ceph-client/include/net/xdp.h

## Purpose

`xdp.h` defines the kernel XDP buffer/frame API for drivers, BPF execution, memory model registration, fragment support, XDP-to-SKB conversion, metadata kfuncs, RSS hash type reporting, and netdevice XDP feature flags.

## Important APIs, types, and functions

Core types are `enum xdp_mem_type`, `struct xdp_mem_info`, `struct xdp_rxq_info`, `struct xdp_txq_info`, `struct xdp_buff`, `struct xdp_frame`, `struct xdp_frame_bulk`, `struct xdp_attachment_info`, `enum xdp_rx_metadata`, `enum xdp_rss_hash_type`, and `struct xdp_metadata_ops`. Important helpers include `xdp_init_buff()`, `xdp_prepare_buff()`, `xdp_data_hard_end()`, `xdp_get_shared_info_from_buff()`, `xdp_get_buff_len()`, `xdp_buff_add_frag()`, `xdp_scrub_frame()`, `xdp_update_skb_frags_info()`, `xdp_convert_frame_to_buff()`, `xdp_update_frame_from_buff()`, `xdp_convert_buff_to_frame()`, `xdp_return_frame*()`, `xdp_flush_frame_bulk()`, RXQ/memory registration helpers, metadata validation helpers, feature flag setters, and `bpf_prog_run_xdp()`.

## Control flow

Drivers register `xdp_rxq_info`, attach a memory model, prepare an `xdp_buff` for each RX packet, run BPF through `bpf_prog_run_xdp()`, and then act on XDP_PASS/TX/REDIRECT/DROP. XDP_PASS may build an SKB from the buffer or frame. Redirect/TX paths convert buffers to `xdp_frame` objects, preserve enough memory-model information for remote free, and return memory via bulk page-pool queues. Fragmented XDP buffers store `skb_shared_info` at reserved tailroom and update SKB fields when converted.

## State and persistence behavior

RX queue info persists for the lifetime of a driver RX ring and must not be modified during NAPI polling. Memory registrations persist by `xdp_mem_info` IDs. `xdp_buff` is per-packet and NAPI-local; `xdp_frame` may outlive NAPI and therefore stores only memory type, not raw RXQ pointer. Feature flags persist on netdevices. Fragment flags and metadata pointers live in packet-local structures.

## Dependencies and integration points

It depends on BPF, netdevice, SKB shared info, page-pool memory, netlink feature enums, and optional `CONFIG_NET`. It integrates with NIC drivers, BPF dispatcher, cpumap/devmap redirects, AF_XDP zero-copy, XDP metadata kfuncs, SKB construction, and netdevice feature advertisement.

## Risks and test signals

Risks include drivers failing to reserve tailroom for `skb_shared_info`, insufficient headroom for `xdp_frame`, using RXQ pointers after NAPI lifetime, fragment count overflow, unreadable/pfmemalloc flag loss, invalid metadata alignment/length, and missing RCU protection when running BPF. Tests should cover RXQ registration/unregistration, all memory models, XDP_PASS/TX/REDIRECT/DROP, fragmented buffers, frame conversion failure paths, page-pool bulk return, metadata kfunc exposure, bond master redirect, and disabled `CONFIG_NET` stubs.
