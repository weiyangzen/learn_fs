# subset-b-004709 Research

Grouped research for the listed Linux network driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/virtio_net.c -->
# sources/distributed-fs/ceph-client/drivers/net/virtio_net.c

## Purpose
Implements the Linux virtio network device driver. It binds `VIRTIO_ID_NET` devices to a `net_device`, negotiates virtio-net features, creates RX/TX/control virtqueues, moves packets between virtqueues and the Linux networking stack, and exposes configuration through netdev, ethtool, XDP, AF_XDP, CPU hotplug, power-management, failover, and virtio config callbacks.

The driver supports legacy and modern virtio headers, checksum and segmentation offloads, mergeable and big receive buffers, multiqueue/RSS/hash reporting, device-provided queue statistics, notification coalescing and dynamic interrupt moderation, page-pool receive allocation, XDP including multi-buffer paths, and AF_XDP zero-copy queue binding.

## Important APIs, Types, And Functions
Key state lives in `struct virtnet_info`, which owns the `virtio_device`, `net_device`, queue arrays, current/max queue-pair counts, feature booleans, control virtqueue lock/buffer, RSS configuration, coalescing defaults, guest offload masks, failover object, and delayed work items. `struct send_queue` wraps a TX virtqueue, scatterlist, NAPI context, stats, coalescing settings, reset flag, and AF_XDP pool/header DMA state. `struct receive_queue` wraps an RX virtqueue, NAPI context, RCU-protected XDP program, page pool, mergeable-buffer sizing EWMA, free page list, XDP/AF_XDP rxq metadata, stats, coalescing state, and AF_XDP buffer batch.

`virtnet_probe()` is the main constructor: it derives queue capacity from config, allocates `alloc_etherdev_mq()`, sets netdev features and callbacks, reads MAC/MTU/RSS/offload capabilities, decides header size and receive mode, allocates virtqueues via `init_vqs()`, creates page pools, initializes failover/RSS/offload state, registers the netdev, marks the virtio device ready, sends initial RSS/MQ/MAC/stats commands, and establishes link state. `virtnet_remove()`, `virtnet_freeze()`, and `virtnet_restore()` tear down or rebuild the same resources.

The packet datapath is split across `start_xmit()`, `xmit_skb()`, `virtnet_poll_tx()`, `virtnet_receive()`, `virtnet_poll()`, and the receive-mode helpers `receive_small()`, `receive_big()`, and `receive_mergeable()`. `virtnet_send_command_reply()` and `virtnet_send_command()` serialize control-virtqueue commands for MAC tables, VLAN filters, queue pairs, RSS/hash config, guest offloads, coalescing, and device statistics. `virtnet_netdev`, `virtnet_ethtool_ops`, and `virtnet_stat_ops` are the public kernel integration surfaces.

XDP and AF_XDP support centers on `virtnet_xdp_set()`, `virtnet_xdp_handler()`, `virtnet_xdp_xmit()`, `receive_small_xdp()`, `receive_mergeable_xdp()`, `virtnet_xsk_pool_enable()`, `virtnet_xsk_pool_disable()`, `virtnet_add_recvbuf_xsk()`, and `virtnet_xsk_xmit()`. RSS and hash reporting are handled by `virtnet_init_default_rss()`, `virtnet_commit_rss_command()`, `virtnet_get_rxfh()`, `virtnet_set_rxfh()`, `virtnet_get_hashflow()`, `virtnet_set_hashflow()`, `virtio_skb_set_hash()`, and the XDP metadata callback `virtnet_xdp_rx_hash()`.

## Control Flow
Module initialization installs two CPU hotplug multi-states and registers `virtio_net_driver`. Virtio core calls `virtnet_validate()` to reject impossible feature combinations, then `virtnet_probe()`. Probe sets `curr_queue_pairs` from CPU count and device maximum, allocates per-queue NAPI/stat objects, calls `virtio_find_vqs()` with alternating RX/TX queues and optional control vq, sets affinity hints, configures RX page pools, registers the netdev under RTNL, disables config callbacks until open, then issues feature-dependent control commands.

`ndo_open` calls `virtnet_open()`, pre-fills active RX queues, registers XDP rxq memory models, enables RX and TX NAPI, and enables config interrupts or assumes link up if no status feature exists. RX callbacks (`skb_recv_done`) schedule RX NAPI. `virtnet_poll()` first cleans the matching TX queue when TX NAPI is enabled, drains RX buffers with `virtnet_receive()`, refills the ring if it is more than half empty, flushes XDP redirects, completes NAPI using virtqueue callback re-enable/poll race checks, runs DIM sampling, and kicks XDP_TX completions when needed.

Receive dispatch begins in `receive_buf()`, which validates virtio header plus Ethernet minimum size, syncs page-pool DMA if needed, saves virtio flags before XDP can mutate data, and routes to small, big, or mergeable handlers. Small mode uses a single page-pool buffer with encoded context for actual allocation size and XDP headroom. Big mode chains pages through `page->private` and builds an skb with `page_to_skb()`. Mergeable mode reads the device `num_buffers`, validates each buffer length against encoded truesize/headroom, can build multi-frag XDP buffs, and appends extra receive buffers to an skb/frag_list when passing to the stack.

TX starts in `start_xmit()`: it frees completed descriptors or disables callbacks for TX NAPI, timestamps the skb, builds a virtio header through `virtio_net_hdr_tnl_from_skb()`, maps header and skb fragments into the queue scatterlist, stops the queue when descriptors are low, and kicks unless batching allows deferral. Completion frees skbs, XDP frames, or AF_XDP descriptors according to pointer-tagged `enum virtnet_xmit_type`. Queue resize and AF_XDP binding reset virtqueues with cleanup callbacks, pause NAPI/queues, then resume and refill.

Config changes are deferred to `virtnet_config_changed_work()`, which reads link status, acknowledges link-announcement events, updates speed/duplex, and toggles carrier/TX queues. CPU hotplug callbacks recalculate virtqueue affinity and XPS masks. PM freeze disables work and netdev activity, resets/free queues and buffers, while restore recreates virtqueues/page pools, marks the device ready, reopens if needed, and restores queue-pair count.

## State And Persistence Behavior
Runtime state is in kernel memory only. Per-queue software stats use `u64_stats_sync` and are accumulated into netdev stats, ethtool stats, and qstats. Device stats are queried on demand via `VIRTIO_NET_CTRL_STATS` and merged into the same output buffers. RSS key, indirection table, saved hash types, queue-pair count, interrupt coalescing settings, guest offload mask, XDP program references, page-pool state, AF_XDP pool bindings, and carrier/speed/duplex are held in `virtnet_info` and/or per-queue structures until device removal, reset, or PM freeze.

The driver persists configuration to the device only through virtio config space and control virtqueue commands. Examples include MAC changes, VLAN filter add/delete, multicast/unicast filter tables, RSS/hash configuration, queue-pair count, guest offload enablement, notification coalescing, and stats capability queries. There is no filesystem persistence. On restore or queue reset, the code must recreate virtqueues, page pools, coalescing values, RSS/queue settings, and guest offloads from in-memory saved state.

Memory ownership is a major part of state management. Page-pool buffers are recycled with `page_pool_put_page()` and may be DMA pre-mapped. Big-packet mode uses a private page chain and deliberately does not use page pools. TX descriptors store pointer-tagged ownership records so completion and reset can return skbs, XDP frames, or AF_XDP completions to the correct subsystem.

## Dependencies And Integration Points
The file depends on Linux networking core (`net_device`, NAPI, ethtool, netdev queue stats, GRO, VLAN, failover), virtio core (`virtqueue_*`, feature negotiation, config access, PM hooks), virtio-net header helpers, BPF/XDP and AF_XDP APIs, page_pool allocation/DMA helpers, dynamic interrupt moderation (`net_dim`), CPU hotplug state, scatterlist mapping, and optional sysfs RX queue attributes.

External integration is broad: virtio devices call the driver through the `virtio_driver` table; network stack calls `net_device_ops`; userspace controls behavior through ethtool, ip link feature toggles, XDP setup, AF_XDP sockets, VLAN/filter changes, and link settings; virtio backends consume the virtqueue descriptors and control commands. Feature bits are central contracts, especially `VIRTIO_NET_F_CTRL_VQ`, `VIRTIO_NET_F_MRG_RXBUF`, `VIRTIO_NET_F_MQ`, `VIRTIO_NET_F_RSS`, `VIRTIO_NET_F_HASH_REPORT`, coalescing features, guest/host offload bits, tunnel GSO bits, and device stats.

## Risks
Feature dependency mistakes can expose invalid device behavior, so `virtnet_validate_features()` rejects many control-dependent features without `CTRL_VQ`; new features must extend that gate. RX buffer sizing is sensitive: mergeable-buffer context packs headroom and truesize into pointer-sized values, XDP assumes reserved head/tail room and page-sized frag semantics, and malformed devices can report lengths or `num_buffers` that must be contained. DMA synchronization depends on whether page-pool DMA mapping is active and whether virtio core already synced memory.

Concurrency risks include NAPI callback re-enable races, TX queue stop/wake ordering, queue reset while RX poll may clean TX, RCU-protected XDP program replacement, RTNL/control-vq locking, DIM work cancellation, and CPU hotplug affinity updates. XDP enablement disables guest offloads and may add raw XDP TX queues; failures during that transition must restore offloads, queue counts, NAPI, and program references without leaks. AF_XDP requires matching RX/TX DMA devices and correct header DMA mapping; partial enable/disable failures can otherwise leak pool mappings or leave queues reset with stale pool pointers.

Control virtqueue commands spin until completion or broken queue, so backend bugs can cause latency or failed configuration. Queue resize resets descriptors and then reapplies coalescing; unsupported coalescing is tolerated, but real command failures abort. Device stats parsing trusts reply sizes enough to walk the reply buffer, so spec compliance matters. Several paths warn but keep probing when optional features fail, which can downgrade RXHASH/RSS or MAC programming silently from userspace's perspective.

## Test Signals
Useful signals include successful module load/probe/remove with virtio-net devices across legacy and modern feature sets, `ip link set up/down`, carrier changes, suspend/resume, CPU hotplug, multiqueue changes via `ethtool -L`, ring resize via `ethtool -G`, coalescing via `ethtool -C` including per-queue and adaptive RX, RSS key/table/hash-field changes via `ethtool -X/-x/-N`, and stats consistency via `ethtool -S` plus netdev qstats.

Datapath tests should cover checksum/GSO/GRO offloads, tunnel GSO, VLAN filtering, multicast/promisc changes, link announce ack, large MTU, mergeable buffers, big-packet mode, non-coherent DMA/page-pool paths, queue full/stop/wake behavior, TX timeout accounting, virtqueue resize while traffic runs, and backend error injection for short packets, overlong mergeable buffers, missing buffers, and bad csum/GSO headers. XDP signals include PASS/DROP/TX/REDIRECT, multi-buffer XDP on mergeable RX, XDP metadata hash extraction, enabling/disabling XDP with guest offloads, and AF_XDP zero-copy RX/TX with need-wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/virtio_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vmxnet3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/Makefile

## Purpose
Builds the VMware vmxnet3 Ethernet NIC driver as a kernel object when `CONFIG_VMXNET3` is enabled. It identifies the driver object and the compilation units that make up the module.

## Important APIs, Types, And Functions
The file uses standard Kbuild variables. `obj-$(CONFIG_VMXNET3) += vmxnet3.o` makes the object conditional on the kernel config option. `vmxnet3-objs := vmxnet3_drv.o vmxnet3_ethtool.o vmxnet3_xdp.o` declares the composite object members: the main driver, ethtool support, and XDP support.

## Control Flow
There is no runtime control flow. During kernel build, Kbuild evaluates `CONFIG_VMXNET3`; if built-in or module-enabled, it compiles the listed object files and links them into `vmxnet3.o` according to normal kernel build rules.

## State And Persistence Behavior
The file contains no runtime state and persists no data. Its only persistent effect is build-system metadata: changing the object list changes what source files are included in the built driver.

## Dependencies And Integration Points
Depends on the kernel Kbuild system and the `CONFIG_VMXNET3` Kconfig symbol defined elsewhere. It integrates with the vmxnet3 source directory by naming `vmxnet3_drv.o`, `vmxnet3_ethtool.o`, and `vmxnet3_xdp.o`; any source split or new feature file must be reflected here to be linked.

## Risks
The main risk is object-list drift. Adding code in a new `.c` file without updating `vmxnet3-objs` produces unresolved symbols or missing functionality; removing or renaming a source file without updating the list breaks the build. Incorrectly changing `obj-$(CONFIG_VMXNET3)` can alter built-in/module behavior for the driver.

## Test Signals
Build signals are sufficient: `make M=drivers/net/vmxnet3` or a full kernel build with `CONFIG_VMXNET3=m/y` should compile and link `vmxnet3.o`. Runtime smoke testing requires the linked module to expose the expected vmxnet3 driver functionality, including ethtool and XDP paths that come from the separate object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vmxnet3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vmxnet3/upt1_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/upt1_defs.h

## Purpose
Defines common UPT v1 structures and constants consumed by the vmxnet3 driver/device ABI. It describes per-queue TX/RX hardware statistics, interrupt moderation levels, RSS configuration format, and feature flags shared with the vmxnet3 descriptor/shared-memory definitions.

## Important APIs, Types, And Functions
`struct UPT1_TxStats` contains 64-bit counters for post-segmentation TSO packets/bytes, unicast/multicast/broadcast packets and bytes, TX errors, and TX discards. `struct UPT1_RxStats` mirrors RX-side counters with LRO packets/bytes, pre-LRO unicast/multicast/broadcast packets and bytes, out-of-buffer events, and RX errors.

Interrupt moderation constants define `UPT1_IML_NONE`, `UPT1_IML_HIGHEST`, and `UPT1_IML_ADAPTIVE`. RSS constants define supported hash type bits for IPv4, TCP/IPv4, IPv6, and TCP/IPv6, and hash functions including Toeplitz. `struct UPT1_RSSConf` holds `hashType`, `hashFunc`, key/table sizes, a 40-byte hash key, and a 128-entry indirection table.

Feature flags are little-endian 64-bit values: RX checksum verification, RSS, VLAN tag stripping, LRO, and inner checksum offload for Geneve/VXLAN-like encapsulation. The use of `cpu_to_le64()` makes these constants suitable for device-shared little-endian feature fields rather than host-native bit arithmetic.

## Control Flow
There is no executable control flow. The vmxnet3 driver includes this header through `vmxnet3_defs.h`, embeds `UPT1_TxStats` and `UPT1_RxStats` in queue descriptors, and writes/reads RSS and feature fields as part of device configuration and stats retrieval.

## State And Persistence Behavior
The structures define shared-memory state exchanged between driver and device. Queue stats are populated by the device and read by the driver after stats/status commands. RSS configuration and feature bits are driver-provided configuration state. There is no standalone persistence; values survive only while the vmxnet3 device instance and shared memory allocations remain valid.

## Dependencies And Integration Points
Depends on kernel integer typedefs (`u8`, `u16`, `u64`) and endian helpers. It is included by `vmxnet3_defs.h`, where UPT stats become part of `Vmxnet3_TxQueueDesc` and `Vmxnet3_RxQueueDesc`, and UPT feature flags feed `Vmxnet3_MiscConf.uptFeatures`. It is an ABI boundary with VMware virtual hardware, so layout and sizes matter.

## Risks
Changing field order, field width, constants, or endian treatment can break driver/device compatibility. Stats counters are plain 64-bit shared fields, so readers must account for device update timing and endian/atomicity expectations in the consuming code. The RSS table and key size limits are fixed; callers must not overrun the arrays or advertise unsupported sizes.

## Test Signals
Build testing should catch missing typedef/endian dependencies. Runtime signals include correct ethtool statistics for vmxnet3 queues, successful RSS configuration with expected hash distribution, interrupt moderation behavior matching selected levels, VLAN/RX checksum/LRO feature negotiation, and compatibility across vmxnet3 device revisions that consume the UPT v1 ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vmxnet3/upt1_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_defs.h

## Purpose
Defines the vmxnet3 hardware/software ABI used by the VMware vmxnet3 Linux driver. It specifies register offsets, command IDs, descriptor layouts, ring sizing and alignment constraints, queue configuration descriptors, interrupt/filter/power/RSS/coalescing/memory-region structures, shared driver/device memory, event/capability bits, and helper macros for ring and VLAN table manipulation.

## Important APIs, Types, And Functions
Register constants cover BAR 1 device registers (`VMXNET3_REG_VRRS`, `UVRS`, driver shared address, command, MAC, interrupt/event cause, device capability, passthrough capability), BAR 0 queue producer registers, and large passthrough BAR offsets. Command IDs are split into set commands beginning at `0xCAFE0000` and get commands beginning at `0xF00D0000`, including activate/quiesce/reset, RX mode/MAC/VLAN/RSS/coalescing/feature/ring buffer updates, memory region registration, and stats/link/capability queries.

Descriptor structures are the packet ABI. `struct Vmxnet3_TxDesc` carries DMA address, length, generation bit, descriptor type, checksum/TSO fields, VLAN insertion, completion request, end-of-packet, and offload mode. `struct Vmxnet3_TxDataDesc` provides a 128-byte header-copy area. `struct Vmxnet3_TxCompDesc` reports completed TX descriptor index and generation. `struct Vmxnet3_RxDesc` supplies RX buffers with buffer type, length, descriptor type, and generation. `struct Vmxnet3_RxCompDesc` and `Vmxnet3_RxCompDescExt` report RX descriptor index, queue/ring ID, SOP/EOP, RSS type/hash, VLAN stripping, length, errors, checksum/IP/TCP/UDP flags, LRO metadata, completion type, and generation. Timestamp descriptors and `Vmxnet3TSInfo` carry TX/RX timestamp data.

`union Vmxnet3_GenericDesc` lets driver code view descriptors as qwords/dwords/words or typed TX/RX/comp descriptors. Ring constants define generation initialization, max buffer sizes, descriptor limits per packet, ring alignment, data/timestamp descriptor size ranges, and max ring sizes. Queue and device configuration types include `Vmxnet3_DriverInfo`, `Vmxnet3_MiscConf`, `Vmxnet3_TxQueueConf`, `Vmxnet3_RxQueueConf`, timestamp queue configs, queue status/control structs, RX filter configuration, power-management packet filters, variable-length config descriptors, coalescing schemes, memory region registration, RSS fields, ring buffer size config, `union Vmxnet3_CmdInfo`, `Vmxnet3_DSDevRead`, `Vmxnet3_DSDevReadExt`, and `Vmxnet3_DriverShared`.

Macros such as `VMXNET3_FLIP_RING_GEN()`, `VMXNET3_INC_RING_IDX_ONLY()`, `VMXNET3_SET_VFTABLE_ENTRY()`, `VMXNET3_CLEAR_VFTABLE_ENTRY()`, and `VMXNET3_VFTABLE_ENTRY_IS_SET()` encode common ring/VLAN table operations. Capability bits describe UDP/ESP RSS, Geneve/VXLAN checksum and TSO support, packet steering, inner RSS/ESP RSS, CRC32 hash, OAM filter, large BAR, out-of-order RX completion, and TSO/LRO offload disablement.

## Control Flow
There is no executable function flow in this header, but it encodes the control flow the driver follows. The driver allocates and fills `Vmxnet3_DriverShared`, writes its physical address to DSAL/DSAH, initializes queue descriptor tables from `Vmxnet3_TxQueueDesc` and `Vmxnet3_RxQueueDesc`, writes queue producer indices to BAR0/BAR large offsets as descriptors are posted, and writes command IDs to `VMXNET3_REG_CMD` to activate, quiesce, reset, update filters/RSS/features/coalescing, or query status.

Packet flow is ring based. For TX, driver writes one or more `Vmxnet3_TxDesc` entries and optionally header-copy/timestamp descriptors, toggles generation as indices wrap, and consumes `Vmxnet3_TxCompDesc` completions. For RX, driver posts `Vmxnet3_RxDesc` buffers in ring 1/ring 2, consumes `Vmxnet3_RxCompDesc` or extended LRO completions, interprets checksum/RSS/VLAN/error bits, and advances producer indices. Event flow uses `VMXNET3_REG_ECR` bits for RX/TX queue errors, link change, device implementation change, and debug events.

## State And Persistence Behavior
All structures describe volatile driver/device shared state. The driver writes configuration into DMA-visible shared memory; the device reads `devRead` regions and writes queue status/statistics after get commands or through completion rings. `Vmxnet3_DriverShared` includes magic, size, driver-readable event cause, and a command-info union valid only while executing the relevant command. Queue descriptors hold persistent-for-device-lifetime ring base physical addresses, sizes, interrupt indexes, driver data areas, queue status, UPT stats, and timestamp config.

No filesystem state is involved. Persistence across reset or suspend must be recreated by the driver from its own runtime configuration. Endianness is explicit for shared scalar fields (`__le16`, `__le32`, `__le64`) and bitfield layout is guarded by `__BIG_ENDIAN_BITFIELD`; the comments note that converting descriptor dwords lets big-endian drivers interpret bitfields correctly.

## Dependencies And Integration Points
Includes `upt1_defs.h` for UPT stats, RSS config limits, and feature flags. Depends on kernel fixed-width/endian types and bitfield-endian macros. It integrates directly with vmxnet3 driver implementation files, ethtool/XDP support, PCI BAR mapping, DMA allocation, interrupt setup, netdev feature negotiation, RSS/coalescing configuration, VLAN filtering, power management, and VMware virtual hardware/firmware.

The ABI is revisioned through supported vmxnet3 revision and UPT version fields in `Vmxnet3_DriverInfo`, device capability registers, extended interrupt config for v6+, and capability max markers. Queue count constants differ for older and extended revisions (`VMXNET3_MAX_*` versus `VMXNET3_EXT_MAX_*`), so driver code must select limits based on negotiated revision/capabilities.

## Risks
This file is layout-critical. Any change to struct packing, field order, bit positions, endian annotations, alignment constants, or max sizes can break communication with the virtual NIC. C bitfields are especially risky across endian modes, so code that bypasses typed bitfields with `GenericDesc.dword/qword` must keep shift constants synchronized with the struct definitions.

Ring sizing and alignment constraints must be enforced before programming hardware; invalid ring base alignment, non-multiple ring sizes, too many descriptors per packet, or buffers larger than `VMXNET3_MAX_*_BUF_SIZE` can trigger device errors such as `VMXNET3_ERR_TXD_REUSE`, `VMXNET3_ERR_BIG_PKT`, `VMXNET3_ERR_SMALL_BUF`, or queue stopped status. Capability drift is another risk: adding a device capability requires updating `VMXNET3_CAP_MAX` and driver negotiation logic, while extended queue/interrupt limits must remain compatible with older revisions.

Shared-memory state is command-context sensitive. `Vmxnet3_DriverShared.cu.cmdInfo` is valid only for the command being executed, so concurrent command execution must be serialized in implementation code. VLAN filter table macros assume valid VLAN IDs below 4096. Power-management pattern sizes and memory region counts are fixed and must be bounds-checked by callers.

## Test Signals
Build-time signals include successful compilation on little- and big-endian configurations and static size/alignment checks in consuming code. Runtime signals include successful vmxnet3 probe, revision/UPT negotiation, device activation/reset/quiesce, TX/RX traffic with wraparound generation bits, checksum/TSO/LRO/RSS/VLAN offloads, interrupt moderation, coalescing modes, link event handling, queue error reporting, ring resize or buffer size commands, timestamp rings, memory region registration, and large BAR/extended queue capability paths.

Negative tests should exercise malformed descriptor limits, unsupported capability combinations, queue status error retrieval, VLAN table edge IDs, RSS field changes, coalescing boundary values, PM wake filters, and compatibility against multiple VMware virtual hardware revisions. ABI tests should verify descriptor field offsets and sizes against device documentation or known-good driver builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_defs.h -->
