# sources/distributed-fs/ceph-client/drivers/net/hyperv/hyperv_net.h

### Purpose
`hyperv_net.h` is the shared internal ABI and state header for the Hyper-V NetVSC driver. It defines NDIS/RNDIS structures, NVSP protocol messages, buffer sizing constants, per-device and per-channel state, stats structures, XDP hooks, and function prototypes shared by `netvsc.c`, `netvsc_drv.c`, `rndis_filter.c`, and `netvsc_bpf.c`.

### Important APIs, Types, And Functions
The most important runtime structures are `struct hv_netvsc_packet`, `struct netvsc_device_info`, `struct rndis_device`, `struct net_device_context`, `struct netvsc_channel`, and `struct netvsc_device`. `hv_netvsc_packet` is compact enough for `skb->cb` and carries send-buffer, DMA, queue, and packet accounting metadata. `netvsc_device` stores negotiated NVSP version, VMBus shared receive/send buffers and GPADLs, channel table, RNDIS extension, queue counts, and teardown flags. `netvsc_channel` stores per-channel NAPI, receive copy buffer, multi-send and receive-completion rings, RSC aggregation state, XDP program, XDP RX queue, and per-channel stats.

The header also defines NVSP versions and message structs from init through v6 packet-direct messages, RNDIS request/response packet formats, NDIS RSS and offload definitions, receive-side coalescing state, and helpers such as `netvsc_rqstor_size()` and `netvsc_get_hash()`.

### Control Flow
The header itself has no executable control flow beyond inline helpers. Its definitions describe the driver flow: VMBus/NVSP negotiation creates a `netvsc_device`, RNDIS initializes the virtual NIC, channels use NAPI for host ring processing, RNDIS packets move over NVSP messages, and XDP hooks can process receive data or transmit frames. The inline `netvsc_get_hash()` chooses full L4 hashing or address-only hashing based on configured hash policy and packet protocol, setting a software hash when needed.

### State And Persistence Behavior
State declared here is runtime-only and owned by the driver. Persistent host/guest protocol state exists only for the lifetime of the VMBus device. Notable synchronization primitives include RCU pointers for `nvdev`, VF netdev, and XDP programs; completions for channel init and VF association; wait queues for drain/subchannel open; atomics for queue sends/open channels; and per-CPU/stat sync structures.

### Dependencies And Integration Points
The header depends on Linux Hyper-V VMBus APIs, RNDIS definitions, netdevice, XDP, jhash, VLAN/checksum/offload UAPI, and NDIS/NVSP protocol constants. It is the integration contract between core VMBus transport (`netvsc.c`), RNDIS control (`rndis_filter.c`), user-facing netdev logic (`netvsc_drv.c`), and XDP support (`netvsc_bpf.c`).

### Risks
Risk concentrates in packed protocol layouts and size/offset constants. Any ABI drift can break host communication. Buffer-size constants must match host expectations, especially receive/send sections and maximum transfer page ranges. RCU-managed pointers and BPF program references require careful ownership. `netvsc_get_hash()` must preserve Azure host hashing limitations for fragmented UDP traffic.

### Test Signals
Compile-time layout coverage, sparse/packed-structure warnings, and cross-file build tests are critical. Runtime signals include successful NVSP negotiation, RNDIS initialization, multi-channel RSS setup, checksum/LSO/RSC offload negotiation, VF association, XDP attach/detach, and channel teardown without leaks.
