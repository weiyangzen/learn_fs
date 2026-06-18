# sources/distributed-fs/ceph-client/net/core/xdp.c

## Purpose

`xdp.c` implements core XDP runtime support shared by network drivers, AF_XDP, page-pool backed receive queues, skb conversion, metadata kfunc registration, and netdev XDP feature notifications. It is not a packet program runner; it manages the memory and object plumbing that lets drivers safely hand buffers to XDP and later recycle or convert them.

## Important APIs, Types, and Functions

The receive-queue registration API is `__xdp_rxq_info_reg()`, `xdp_rxq_info_unreg()`, `xdp_rxq_info_reg_mem_model()`, `xdp_rxq_info_unreg_mem_model()`, `xdp_rxq_info_unused()`, and `xdp_rxq_info_is_reg()`. Memory-provider registration is handled through `xdp_reg_mem_model()`, `xdp_reg_page_pool()`, `xdp_unreg_page_pool()`, and `xdp_rxq_info_attach_page_pool()`, with provider IDs tracked by `struct xdp_mem_allocator`, `mem_id_pool`, and `mem_id_ht`. Buffer return paths include `__xdp_return()`, `xdp_return_frame()`, `xdp_return_frame_rx_napi()`, `xdp_return_frame_bulk()`, `xdp_return_frag()`, and `xdp_return_buff()`. Conversion helpers include `xdp_convert_zc_to_xdp_frame()`, `xdp_build_skb_from_buff()`, `xdp_build_skb_from_zc()`, `__xdp_build_skb_from_frame()`, `xdp_build_skb_from_frame()`, and `xdpf_clone()`. The BPF metadata kfunc stubs are `bpf_xdp_metadata_rx_timestamp()`, `bpf_xdp_metadata_rx_hash()`, and `bpf_xdp_metadata_rx_vlan_tag()`.

## Control Flow

Drivers register `struct xdp_rxq_info` before exposing queues to XDP, optionally bind an XDP memory model, and unregister during teardown. Page-pool backed memory gets a cyclic ID, an rhashtable entry, and a page-pool disconnect callback. When a page pool disconnects, `mem_allocator_disconnect()` walks the ID table under `mem_id_lock` and removes matching allocators; removal frees IDs after an RCU grace period. XDP frame return dispatches by `enum xdp_mem_type`, with page-pool paths optionally using NAPI direct recycling and bulk queues. skb conversion either wraps existing XDP frame memory or allocates/copies from zero-copy XSK buffers when ownership cannot be transferred directly. Metadata kfuncs default to `-EOPNOTSUPP`; drivers can provide device-bound implementations through BTF kfunc dispatch. Feature setters update `dev->xdp_features` under netdev locking and notify listeners when registered devices change capabilities.

## State and Persistence Behavior

Persistent global state is the lazily allocated memory-ID rhashtable, IDA allocator, cyclic `mem_id_next`, and metadata BTF kfunc registration. Per-queue state lives in `struct xdp_rxq_info`: registration state, device pointer, queue index, fragment size, and memory info. Page pools retain `xdp_mem_id` ownership until unregistered or disconnected. Feature bits persist in `net_device::xdp_features`. RCU protects allocator lookup/free, while `mem_id_lock` serializes registration, cyclic ID allocation, and disconnect walks.

## Dependencies and Integration Points

The file integrates with page_pool, AF_XDP buffer pools, BPF/BTF kfunc infrastructure, netdevice locking/notifiers, skb allocation/build helpers, tracepoints, and NAPI recycling. Drivers call the exported GPL symbols to register queues and memory models. The skb conversion helpers are used when XDP actions pass packets into the normal networking stack.

## Risks

The high-risk area is lifetime management across page-pool disconnect, rhashtable lookup, RCU free, and ID reuse. `xdp_unreg_mem_model()` assumes the ID lookup succeeds for page pools before `page_pool_destroy()`. Incorrect `mem_type` propagation can free memory through the wrong allocator. skb conversion must preserve metadata, frags, truesize, pfmemalloc flags, and recycle eligibility. Feature updates must hold the expected netdev lock or notify listeners from inconsistent state. XSK zero-copy conversion is copy-heavy and must leave ownership unchanged on allocation failure.

## Test Signals

Useful coverage includes driver queue register/unregister misuse warnings, page-pool register/unregister and disconnect callbacks, cyclic ID wrap, XDP frame returns for page-pool, order-0, shared page, and XSK memory, fragmented XDP frames, skb conversion with metadata and frags, BPF metadata kfunc fallback behavior, and XDP feature-change notifier delivery. KASAN/KCSAN/lockdep runs are valuable for allocator lifetime and lock-order issues.
