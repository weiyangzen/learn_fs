# sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc.c

### Purpose
`netvsc.c` is the core VMBus/NVSP datapath for the Hyper-V synthetic network driver. It negotiates protocol version with the host, allocates and shares receive/send buffers through GPADLs, opens channels, sends and receives RNDIS packets over VMBus, handles TX completions and RX completions, supports subchannels and VF datapath switching, and performs teardown.

### Important APIs, Types, And Functions
External entry points include `netvsc_device_add()`, `netvsc_device_remove()`, `netvsc_send()`, `netvsc_poll()`, `netvsc_channel_cb()`, `netvsc_alloc_recv_comp_ring()`, `netvsc_dma_unmap()`, and `netvsc_switch_datapath()`. Internal setup and teardown helpers are `alloc_net_device()`, `netvsc_connect_vsp()`, `negotiate_nvsp_ver()`, `netvsc_init_buf()`, revoke/teardown helpers for send and receive GPADLs, and `free_netvsc_device_rcu()`.

TX helpers include `netvsc_get_next_send_section()`, `netvsc_copy_to_send_buf()`, `netvsc_dma_map()`, `netvsc_build_mpb_array()`, `netvsc_send_pkt()`, and multi-send batching in `netvsc_send()`. RX helpers include `netvsc_receive()`, `rndis_filter_receive()` integration, receive-completion ring management, `netvsc_receive_inband()`, `netvsc_send_table()`, `netvsc_send_vf()`, and `netvsc_process_raw_pkt()`.

### Control Flow
Device add allocates `netvsc_device`, initializes all channel slots and XDP RX queues, adds and enables primary-channel NAPI, opens the VMBus channel, negotiates the newest supported NVSP version, sends NDIS version/config, initializes shared receive and send buffers, and publishes `nvdev` with RCU. Buffer initialization allocates guest memory, establishes GPADLs, sends NVSP buffer messages, waits for host completions, validates host-provided section sizes/counts, and initializes send-section and receive-completion rings.

TX through `netvsc_send()` first rejects destroyed devices, chooses direct send for control/XDP traffic, otherwise attempts to batch small packets into a pre-shared send buffer. It may copy all data, copy only the RNDIS header, or send page buffers directly. `netvsc_send_pkt()` builds an NVSP RNDIS packet message, maps page buffers through DMA bounce buffers in isolation VMs, sends either MPB descriptors or in-band packets, tracks outstanding queue sends, and stops/wakes TX queues based on VMBus ring availability. TX completion releases send-buffer slots, updates stats, unmaps DMA, consumes SKBs, and wakes queues or drain waiters.

RX uses `netvsc_channel_cb()` to defer host-ring processing to NAPI. `netvsc_poll()` iterates VMBus descriptors until budget, processes completions, transfer-page RX packets, and in-band messages, flushes XDP redirects, sends queued RX completions to the host, and re-enables host interrupts when appropriate. `netvsc_receive()` validates NVSP and transfer-page metadata, checks receive-buffer bounds, forwards each RNDIS packet to `rndis_filter_receive()`, and enqueues one completion for the transfer page descriptor.

Teardown revokes host-visible buffers, nulls the RCU `nvdev`, disables and deletes NAPI for all channels, closes VMBus, tears down GPADLs in the host-version-specific order, and frees memory after an RCU grace period.

### State And Persistence Behavior
All state is per VMBus device and in memory. Shared send/receive buffers persist until revoke/GPADL teardown. `send_section_map` is a bitmap allocator for host-visible send sections. Each channel holds outstanding send count, pending multi-send batch state, receive-completion ring indices, RSC/XDP state, and stats. `destroy` and `tx_disable` gate queue wakeup and drain behavior. There is no disk persistence.

### Dependencies And Integration Points
The file integrates with Hyper-V VMBus packet APIs, GPADL memory sharing, RNDIS filter code, netdevice NAPI and queue APIs, XDP RX queue registration, DMA mapping for isolation VMs, tracepoints, VF association messages, and NVSP protocol structures from `hyperv_net.h`.

### Risks
Risk areas include host message length validation, GPADL revoke/teardown ordering across host versions, send-buffer bitmap concurrency, multi-send batching ownership of SKBs and send sections, DMA cleanup on all send failure paths, NAPI disable/delete ordering, transfer-page range bounds, receive-completion ring overflow, RCU publication of `nvdev`, and datapath switching while a VF is appearing or disappearing.

### Test Signals
Important tests include driver load/unload on multiple Hyper-V host versions, NVSP version fallback, isolation VM DMA path, send-buffer batching and direct page-buffer TX, TX ring low/high water queue stop/wake, RX transfer-page bounds rejection, receive completion backpressure, RNDIS packet processing, XDP redirect flushing, subchannel setup fallback, VF association and datapath switching, and teardown under traffic.
