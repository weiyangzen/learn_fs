# Research: subset-b-004708

Grouped research for:
- sources/distributed-fs/ceph-client/drivers/net/usb/usbnet.c
- sources/distributed-fs/ceph-client/drivers/net/usb/zaurus.c
- sources/distributed-fs/ceph-client/drivers/net/veth.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/usbnet.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/usbnet.c

## Purpose

`usbnet.c` is the shared Linux USB networking framework used by many USB Ethernet-like minidrivers. It centralizes interface probing, endpoint discovery, RX/TX URB queueing, NAPI-like bottom-half cleanup through workqueues, runtime power management, ethtool plumbing, link/event handling, and generic USB control-message helpers. Device-specific drivers provide a `struct driver_info` through USB IDs; this core supplies the common `net_device_ops` and lifecycle behavior.

The framework supports simple bulk Ethernet adapters, host-to-host cables, CDC-like devices, wireless/WWAN USB net devices, and devices with custom packet framing through minidriver hooks such as `bind`, `rx_fixup`, `tx_fixup`, `status`, `link_reset`, `manage_power`, and `recover`.

## Important APIs, Types, and Functions

- `usbnet_get_endpoints()` scans USB interface alternate settings for bulk IN, bulk OUT, and optional interrupt status endpoints, sets the selected alternate interface, and records `dev->in`, `dev->out`, and `dev->status`.
- `usbnet_get_ethernet_addr()` reads a USB string descriptor containing 12 hex digits and installs it as the netdev MAC address.
- `usbnet_status_start()`, `usbnet_status_stop()`, `__usbnet_status_start_force()`, and `__usbnet_status_stop_force()` manage the optional interrupt URB reference count and suspend/resume behavior.
- `usbnet_skb_return()` finishes RX accounting, protocol assignment, timestamp deferral, and `netif_rx()` submission.
- `usbnet_change_mtu()`, `usbnet_update_max_qlen()`, `usbnet_pause_rx()`, `usbnet_resume_rx()`, and `usbnet_unlink_rx_urbs()` expose queue sizing and RX control utilities to minidrivers.
- `rx_submit()`, `rx_complete()`, `rx_process()`, `rx_alloc_submit()`, `usbnet_bh()`, and `usbnet_bh_work()` implement the receive path.
- `usbnet_start_xmit()`, `tx_complete()`, `usbnet_tx_timeout()`, and `build_dma_sg()` implement the transmit path.
- `usbnet_open()` and `usbnet_stop()` are the netdev open/close operations.
- `usbnet_probe()` and `usbnet_disconnect()` allocate, bind, register, unregister, and free the USB-backed `net_device`.
- `usbnet_suspend()`, `usbnet_resume()`, `usbnet_device_suggests_idle()`, `usbnet_manage_power()`, and `usbnet_link_change()` integrate runtime/system PM and link state.
- `usbnet_read_cmd()`, `usbnet_write_cmd()`, `_nopm` variants, and `usbnet_write_cmd_async()` provide synchronous and asynchronous USB control-transfer helpers.
- Exported ethtool helpers include MII/internal link settings, link query, nway reset, MII ioctl, driver info, and message-level controls.

Key state is held in `struct usbnet` from `<linux/usb/usbnet.h>`, including `struct net_device *net`, USB device/interface pointers, endpoint pipes, `struct driver_info *driver_info`, RX/TX/done/pause skb queues, work items, a throttle timer, MII data, interrupt URB fields, PM counters, and event flags. SKB private control data is stored in `struct skb_data` inside `skb->cb`; `usbnet_init()` has a `BUILD_BUG_ON()` to ensure the control buffer is large enough.

## Control Flow

Probe begins in `usbnet_probe()`. It enables autosuspend support if the concrete USB driver did not advertise it, allocates an Ethernet netdev with `struct usbnet` private data, initializes queues, work items, timers, locks, MII/interrupt state, default MTU and ops, then invokes the minidriver `bind()` if supplied. If no bind hook is present, it either discovers endpoints generically or uses endpoint addresses from `driver_info`. It initializes the optional status interrupt URB, calculates `rx_urb_size`, `hard_mtu`, `maxpacket`, RX/TX queue lengths, assigns a random MAC if needed, sets WLAN/WWAN device type flags, optionally allocates a one-byte padding packet for SG/ZLP avoidance, registers the netdev, stores interface data, and attaches the device.

Open uses `usb_autopm_get_interface()`, calls minidriver `reset()` and `check_connect()` hooks, starts the status interrupt URB, sets `EVENT_DEV_OPEN`, starts the netdev queue, resets RX error counters, schedules bottom-half work to fill RX URBs, and either lets `manage_power()` hold/release runtime PM or keeps `EVENT_NO_RUNTIME_PM` for devices that cannot cooperate.

RX allocation is demand-driven. `usbnet_bh()` refills up to `RX_QLEN(dev)` unless the device is stopped, suspended, carrier-off, halted, paused, throttled, or going away. `rx_submit()` allocates an aligned skb, fills a bulk URB, verifies the interface is runnable, submits it under `rxq.lock`, and queues the skb in `rxq` as `rx_start`. `rx_complete()` updates skb length, maps URB errors into cleanup, throttle, halt, or disconnect behavior, tracks a short error-rate window with `pkt_cnt`/`pkt_err`, defers completion to the `done` queue, and resubmits the URB when appropriate. `usbnet_bh()` later processes `rx_done` through `rx_process()`, which calls minidriver `rx_fixup()` before delivering valid Ethernet frames via `usbnet_skb_return()`.

TX begins in `usbnet_start_xmit()`. It timestamps the skb, lets minidrivers apply `tx_fixup()`, allocates/fills a bulk URB, optionally builds scatter-gather DMA descriptors, handles maxpacket-aligned transfers by adding a byte or setting `URB_ZERO_PACKET`, records byte/packet stats, acquires async runtime PM, submits the URB, queues the skb in `txq`, updates BQL, and stops the queue when `TX_QLEN()` is reached. If the device is asleep under PM, the URB is anchored on `dev->deferred` for resume. `tx_complete()` updates per-CPU tx stats or error counters, handles TX halt/throttle cases, releases async PM, and defers skb/URB freeing to the bottom-half path.

Deferred event work in `usbnet_deferred_kevent()` handles bits in `dev->flags`: it clears stalled pipes with `usb_clear_halt()`, retries RX memory shortages, runs minidriver `link_reset()`, applies carrier changes through `__handle_link_change()`, and invokes minidriver multicast/filter programming via `set_rx_mode()`. `usbnet_defer_kevent()` is the common scheduler for this worker.

Stop clears `EVENT_DEV_OPEN`, stops the netdev queue, gets a PM reference to avoid resume races, calls minidriver `stop()`, optionally unlinks all TX/RX URBs through `usbnet_terminate_urbs()`, stops status interrupts, purges paused RX skbs, clears flags, deletes timers, cancels work, resets BQL, and balances PM/`manage_power()` references. Disconnect marks the device going away, unregisters the netdev, cancels work, frees deferred URBs, invokes `unbind()`, kills/frees the interrupt URB, frees padding storage, and frees the netdev.

Suspend increments `suspend_count`, rejects autosuspend while TX URBs are outstanding, sets `EVENT_DEV_ASLEEP`, detaches the device, drains URBs, kills the status interrupt URB, and reattaches for runtime wake use. Resume restarts status interrupts, submits anchored deferred TX URBs, clears `EVENT_DEV_ASLEEP`, refills RX, wakes TX queues, and handles a pending `EVENT_DEVICE_REPORT_IDLE` PM reference.

## State and Persistence Behavior

The file does not persist data to disk. Runtime state is in kernel objects owned by the USB interface and netdev: skb queues (`rxq`, `txq`, `done`, `rxq_pause`), URBs, timers, work items, per-CPU net stats, MII settings, interrupt URB refcount, runtime PM references, link speed fields, queue length fields, and bit flags. Device-specific identity and policy are stable only as long as the USB binding remains active through `driver_info`. The netdev MAC can be read from hardware descriptors, provided by a minidriver, or randomized at probe.

State transitions rely on locks and memory ownership conventions: queue locks protect skb queue mutation; `interrupt_mutex` protects the status URB count; the bottom-half queue serializes skb freeing and RX delivery outside URB completion context; wait queues coordinate stop/drain; runtime PM get/put calls bracket control and data transfers.

## Dependencies and Integration Points

This code depends on the Linux USB core (`struct usb_driver`, URBs, pipes, interface alternate settings, autosuspend), networking core (`net_device`, `net_device_ops`, BQL, ethtool, MII helpers, carrier/queue APIs, per-CPU stats), workqueue/timer infrastructure, SKB allocation and timestamping, and minidriver contracts from `<linux/usb/usbnet.h>`.

It exports many symbols with `EXPORT_SYMBOL_GPL()` for USB network minidrivers such as CDC Ethernet variants, RNDIS, ASIX, Zaurus, and related devices. Integration is table-driven: USB drivers set `.probe = usbnet_probe`, `.disconnect = usbnet_disconnect`, PM callbacks to `usbnet_suspend()`/`usbnet_resume()`, and point `usb_device_id.driver_info` at a `struct driver_info`.

## Risks and Edge Cases

- URB lifetime is subtle. `unlink_urbs()` takes an extra URB reference around `usb_unlink_urb()` to avoid races with completion and deferred cleanup.
- RX/TX error storms can flood logs or CPU, so both paths throttle via `dev->delay`; high RX packet error ratios temporarily set `EVENT_RX_KILL`.
- Runtime PM reference balancing is complex across open, stop, TX submit/complete, deferred TX during suspend, status URBs, and `manage_power()` hooks. Incorrect minidriver behavior can leak PM references or suspend active devices.
- MTU changes that make the link-layer MTU a multiple of `maxpacket` are rejected to avoid unwanted zero-length packet reads.
- Minidriver `rx_fixup()` and `tx_fixup()` can reshape packet ownership, lengths, stats, and multi-packet behavior; bugs in those hooks affect generic queue accounting.
- Link-change handling intentionally kills RX URBs when carrier drops to save bus bandwidth; minidrivers must call `usbnet_link_change()` correctly.
- `__usbnet_write_cmd()` warns and returns `-EINVAL` if a nonzero size is requested with no data pointer; callers must choose the correct helper for control messages.
- The interrupt status endpoint is optional but `init_status()` assumes a status endpoint exists when `driver_info->status` is set.

## Test Signals

Useful signals include USB bind/unbind logs, `ethtool -S` and message-level changes, netdev RX/TX counters, BQL behavior, carrier transitions, successful PM autosuspend/resume, absence of leaked URBs on disconnect, and pipe-halt recovery after injected `-EPIPE` errors. Regression testing should cover open/close cycles, unplug during traffic, TX timeout recovery, MTU changes, minidriver RX/TX fixups, interrupt status resubmission, runtime suspend while idle, refusal to autosuspend with queued TX, and control-message helper behavior under PM and no-PM contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/usbnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/zaurus.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/zaurus.c

## Purpose

`zaurus.c` is a USB network minidriver for Sharp Zaurus PDAs and devices using compatible Lineo/Belcarra-style protocols. These devices often claim CDC Ethernet or CDC MDLM conformance but violate important details, so the driver binds them to `usbnet` with custom framing and descriptor validation instead of relying on the generic CDC Ethernet driver.

The main device behavior is point-to-point USB Ethernet with Zaurus framing: transmitted frames get a little-endian Ethernet FCS appended, and receive buffers reserve extra header space for CRC/padding quirks. The file also handles pseudo-MDLM BLAN/SAFE descriptor matching for compatible phones and accessories.

## Important APIs, Types, and Functions

- `zaurus_tx_fixup()` is the main TX framing hook. It ensures sufficient tailroom, appends a CRC32/FCS to the skb, and returns the possibly copied skb for usbnet transmission.
- `zaurus_bind()` adjusts `hard_header_len` by six bytes, sets `rx_urb_size`, and delegates CDC endpoint/interface binding to `usbnet_generic_cdc_bind()`.
- `always_connected()` is the `check_connect` hook; PDA-style devices are treated as connected whenever present.
- `zaurus_sl5x00_info`, `zaurus_pxa_info`, and `olympus_mxl_info` are `struct driver_info` instances for CDC-Ethernet-claiming devices.
- `safe_guid` and `blan_guid` are CDC MDLM GUIDs used to identify pseudo-MDLM SAFE/BLAN devices.
- `blan_mdlm_bind()` parses class-specific MDLM and MDLM detail descriptors, validates BLAN/SAFE details, applies the same framing size adjustment, and calls `usbnet_get_endpoints()`.
- `bogus_mdlm_info` is the `driver_info` for pseudo-MDLM devices.
- `products[]` is the USB ID table mapping Sharp, Motorola, Olympus, and Logitech devices/interfaces to the appropriate `driver_info`.
- `zaurus_driver` is a `struct usb_driver` using `usbnet_probe`, `usbnet_disconnect`, `usbnet_suspend`, and `usbnet_resume`.

## Control Flow

USB matching selects an entry in `products[]`, and the selected `driver_info` pointer is passed to `usbnet_probe()` through `driver_info`. For CDC-Ethernet-like Zaurus devices, `usbnet_probe()` calls `zaurus_bind()`, which expands the netdev hard header length by six bytes, sizes RX URBs to the adjusted header plus MTU, and then relies on `usbnet_generic_cdc_bind()` to perform CDC-style binding and unbinding through `usbnet_cdc_unbind()`.

For pseudo-MDLM devices, `usbnet_probe()` calls `blan_mdlm_bind()`. That function walks the current altsetting's extra descriptors, only considers class-specific interface descriptors, requires exactly one MDLM descriptor with the BLAN or SAFE GUID, requires exactly one compatible MDLM detail descriptor, validates detail length and `bmDataCapabilities`, and rejects unsupported descriptor combinations with `-ENODEV`. On success it applies the same six-byte header/RX sizing adjustment and performs generic endpoint discovery with `usbnet_get_endpoints()`.

During TX, usbnet calls `zaurus_tx_fixup()`. The hook reserves two pad bytes conceptually and four bytes for the FCS. If the skb is cloned or lacks tailroom, it copies/expands the skb and frees the old one. It calculates `crc32_le(~0, skb->data, skb->len)`, complements the result, and appends the four FCS bytes. The hook does not append the two pad bytes despite reserving for them; this matches the Belcarra/Zaurus framing notes in the comments.

Runtime open, close, RX/TX URB queueing, PM, disconnect, stats, and generic netdev operations are inherited from `usbnet.c`. The Zaurus driver disables hub-initiated LPM through `.disable_hub_initiated_lpm = 1`.

## State and Persistence Behavior

The driver has no persistent storage. Static state consists of USB ID tables, `driver_info` descriptors, and MDLM GUID constants. Per-device runtime state is held by `usbnet` and by netdev fields adjusted at bind time: `hard_header_len`, `rx_urb_size`, point-to-point/framing flags, and endpoint selections. TX fixup mutates or replaces individual SKBs before URB submission.

## Dependencies and Integration Points

`zaurus.c` depends on the `usbnet` framework, CDC descriptor definitions, CRC32 helpers, USB core matching, and netdevice/ethtool infrastructure inherited through usbnet. It integrates with generic CDC helpers through `usbnet_generic_cdc_bind()` and `usbnet_cdc_unbind()` for conventional Zaurus entries, while pseudo-MDLM devices use direct endpoint discovery.

The comments note a cross-driver dependency: PXA devices claiming CDC Ethernet must also be blacklisted in `cdc_ether`, otherwise the wrong driver may bind before `zaurus`.

## Risks and Edge Cases

- Descriptor parsing in `blan_mdlm_bind()` trusts descriptor `bLength` to advance through `extra`; malformed zero-length descriptors would be dangerous in general descriptor parsers, although USB core usually sanitizes descriptor blobs.
- All supported devices are treated as always connected; there is no physical link verification.
- Many devices report non-unique or unreliable Ethernet descriptors, so the driver intentionally avoids relying on MDLM/CDC Ethernet address information in pseudo-MDLM mode.
- TX framing uses skb copy/expand when tailroom is insufficient; allocation failure drops the packet through the usbnet TX path.
- Device matching must remain coordinated with generic CDC drivers to prevent incorrect binding.
- The six-byte hard-header adjustment affects MTU/RX sizing and must stay aligned with usbnet framing assumptions.

## Test Signals

Useful validation includes USB ID binding for every table entry, rejection of unsupported MDLM GUID/detail combinations, successful endpoint discovery in both CDC and pseudo-MDLM modes, TX packets carrying the expected appended FCS, no skb tail overwrite when tailroom is insufficient, correct point-to-point `usb%d` naming from usbnet flags, suspend/resume through usbnet PM callbacks, and coexistence tests with `cdc_ether` blacklist behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/zaurus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/veth.c -->
# sources/distributed-fs/ceph-client/drivers/net/veth.c

## Purpose

`veth.c` implements the Linux virtual Ethernet pair driver. A veth link creates two peer `net_device` instances; packets transmitted on one endpoint are delivered as received packets on the other endpoint, often across network namespaces. The driver is central to containers, namespaces, bridges, routing tests, XDP redirect targets, and virtual datapaths.

The implementation supports ordinary skb forwarding, software stats, ethtool queue/stat reporting, GRO-over-NAPI mode, XDP program execution, XDP_TX and XDP_REDIRECT, ndo_xdp_xmit frame injection, XDP metadata accessors, configurable channel counts, peer link creation/deletion through rtnetlink, and feature negotiation against peer state.

## Important APIs, Types, and Functions

- `struct veth_priv` stores the RCU-protected peer pointer, drop counter, attached XDP program pointer, receive queue array, and requested headroom.
- `struct veth_rq` represents one receive queue with NAPI state, optional XDP program, XDP memory info, stats, notification mask, ptr_ring, xdp_rxq info, and page pool.
- `struct veth_stats` and `struct veth_rq_stats` hold per-queue XDP/drop counters protected by `u64_stats_sync`.
- Ettool support is implemented by `veth_get_drvinfo()`, `veth_get_strings()`, `veth_get_sset_count()`, `veth_get_ethtool_stats()`, `veth_get_channels()`, `veth_set_channels()`, and `veth_get_link_ksettings()`.
- The normal skb transmit path is `veth_xmit()`, with forwarding through `veth_forward_skb()`.
- XDP and NAPI paths include `veth_xdp_xmit()`, `veth_ndo_xdp_xmit()`, `veth_xdp_rcv_one()`, `veth_xdp_rcv_skb()`, `veth_xdp_rcv()`, `veth_poll()`, `veth_xdp_tx()`, and flush helpers.
- NAPI/XDP resource management is handled by `veth_enable_xdp_range()`, `veth_disable_xdp_range()`, `__veth_napi_enable_range()`, `veth_napi_del_range()`, `veth_enable_xdp()`, `veth_disable_xdp()`, `veth_napi_enable()`, and range-safe variants for channel changes.
- Device lifecycle uses `veth_open()`, `veth_close()`, `veth_dev_init()`, `veth_dev_free()`, `veth_setup()`, and `veth_free_queues()`.
- Netdevice ops include `ndo_start_xmit`, stats, multicast no-op, MAC address change, iflink lookup, feature fix/set, RX headroom, BPF/XDP setup, XDP xmit, and peer lookup.
- Rtnetlink integration is provided by `veth_validate()`, `veth_newlink()`, `veth_dellink()`, `veth_get_link_net()`, and `veth_link_ops`.
- XDP metadata ops expose timestamp, RSS hash, and VLAN tag through `veth_xdp_rx_timestamp()`, `veth_xdp_rx_hash()`, and `veth_xdp_rx_vlan_tag()`.

## Control Flow

Module initialization registers `veth_link_ops` as the `veth` rtnetlink link type. Creating a veth link enters `veth_newlink()`. It parses optional `VETH_INFO_PEER` attributes, creates and registers the peer first in the peer net namespace, assigns random MAC addresses when needed, disables GRO by default for established compatibility, registers the requested endpoint second, turns carrier off initially, connects both `veth_priv.peer` pointers with RCU assignment, initializes real RX/TX queue counts, and calculates XDP feature flags for both sides. Deletion through `veth_dellink()` clears peer pointers and queues both devices for unregister.

`veth_setup()` defines Ethernet defaults and veth-specific properties: no TX skb sharing, live address changes, no queue, phony headroom, disabled netpoll, lockless TX, feature flags, VLAN/MPLS/GSO capabilities, per-CPU tstats, destructor, ops tables, and `ETH_MAX_MTU`.

The ordinary TX path starts in `veth_xmit()`. Under RCU it resolves the peer, verifies the skb can expose an Ethernet header, selects the peer receive queue from the skb queue mapping, decides whether to use NAPI based on `rq->napi` and GRO eligibility, timestamps TX, and calls `veth_forward_skb()`. Without NAPI, the peer receives the skb through `__netif_rx()` and the transmitting device records software TX stats. With NAPI/GRO/XDP, the skb is put into the peer queue's `ptr_ring`; `__veth_xdp_flush()` schedules peer NAPI. If the ring is full and the TX queue can be stopped, the Ethernet header is restored and the queue is stopped until the peer NAPI poll releases backpressure. Drops increment `priv->dropped`.

NAPI polling in `veth_poll()` consumes queued skbs or XDP frames from `rq->xdp_ring` through `veth_xdp_rcv()`. SKBs are converted into XDP buffers when an XDP program is attached by `veth_xdp_rcv_skb()`, possibly copying/COWing data with the page pool to create sufficient headroom. XDP frames from ndo_xdp_xmit are processed by `veth_xdp_rcv_one()`. XDP actions are handled as follows: `XDP_PASS` rebuilds an skb or updates the original skb and sends it to GRO/receive; `XDP_TX` batches frames back toward the peer with `veth_xdp_tx()` and `veth_xdp_flush()`; `XDP_REDIRECT` calls `xdp_do_redirect()` and later `xdp_do_flush()`; `XDP_DROP` and `XDP_ABORTED` update drop/exception stats and free the frame/buffer. After poll completion, the code clears notification masking, reschedules if the ring refilled, and wakes a stopped peer TX queue.

`veth_xdp_xmit()` implements peer injection of XDP frames. It requires valid XDP flags, a live peer, and an initialized peer NAPI pointer, selects a receive queue, validates frame length against MTU/header/VLAN allowance, enqueues tagged XDP-frame pointers into the peer `ptr_ring`, optionally flushes, and updates peer transmit-queue XDP counters for ndo-originated calls. Pointer tagging uses `VETH_XDP_FLAG` to distinguish `struct xdp_frame *` from `struct sk_buff *` in the same ring.

Opening a device requires a peer. It enables full XDP resources if an XDP program is attached, or NAPI resources if GRO was requested; if the peer is up, it turns carrier on for both sides. Closing turns carrier off on both sides and removes XDP/NAPI resources as appropriate. Feature changes toggle NAPI for GRO when the device is up and no XDP program is attached. XDP program setup through `veth_xdp_set()` validates peer presence, peer MTU against XDP headroom and fragment support, RX/TX queue compatibility, enables resources when up, adjusts peer GSO and max MTU limits, manages BPF program references, and updates peer features.

Channel changes through `veth_set_channels()` validate nonzero queues and XDP constraints between local RX and peer TX counts. When running, it temporarily drops carrier, enables newly added RX queue resources before applying queue counts, reverts on errors where possible, disables removed queue resources, restores carrier, and refreshes XDP feature flags on both peers.

## State and Persistence Behavior

The driver has no disk persistence. State exists in paired netdevices, their private `veth_priv` structures, RCU peer pointers, per-queue rings/NAPI/page pools/XDP rxq info, BPF program references, feature bits, real queue counts, per-CPU tstats, per-queue u64 stats, atomic drop counters, carrier state, requested headroom, and MTU/max-MTU constraints. Peer relationships can cross network namespaces; `veth_get_link_net()` reports the peer namespace when available.

Resource lifetime is tied to netdev registration and open/XDP/GRO state. Queue arrays are allocated during `ndo_init` and freed by the private destructor. NAPI/page-pool/ptr-ring/XDP rxq resources are enabled only when needed and explicitly torn down on close, XDP removal, GRO disable, channel shrink, or unregister. RCU and `synchronize_net()` protect peer/ring/NAPI pointer changes from in-flight TX, poll, and stats readers.

## Dependencies and Integration Points

`veth.c` depends on the Linux networking core, rtnetlink link operations, network namespaces, SKB helpers, RCU, per-CPU software stats, ethtool, qdisc/queue APIs, XDP/BPF core, page-pool helpers, ptr_ring, GRO/NAPI, VLAN metadata, and optional page-pool stats. It registers as `MODULE_ALIAS_RTNL_LINK("veth")`, so userspace creates devices with netlink tools such as `ip link add type veth`.

The driver integrates heavily with peer feature negotiation. XDP attachment on one side constrains the peer's GSO and max MTU, sets redirect-target features, and requires local RX queue count to cover peer TX queues. GRO enables NAPI and redirect target behavior even without an XDP program.

## Risks and Edge Cases

- Peer pointer access is RCU-protected; missing RCU discipline would cause use-after-free during namespace teardown or peer deletion.
- The shared ptr_ring stores both skb and XDP frame pointers with low-bit tagging. This assumes pointer alignment keeps the tag bit free.
- Backpressure relies on stopping the correct peer TX queue and waking it from NAPI poll; queue mapping and real queue counts must stay consistent.
- XDP setup must reject incompatible MTU, queue, or detached-peer states; otherwise frames may exceed available headroom or arrive on queues without resources.
- Channel changes while running have partial rollback limits; the code warns if RX queue restoration fails after a TX queue update failure.
- SKB-to-XDP conversion can COW/copy through page_pool and may drop packets on memory pressure.
- Feature changes are asymmetric because local XDP affects peer GSO/max MTU and redirect capabilities.
- GRO is disabled by default for compatibility, so tests expecting GRO must explicitly enable it.
- XDP metadata helpers return `-ENODATA` when processing pure XDP frames without backing skbs.

## Test Signals

Useful tests include rtnetlink creation with and without explicit peer attributes, cross-namespace peer placement, deletion from either endpoint, carrier state when one or both peers are up, ordinary skb forwarding and stats, full rings causing TX queue backpressure and wakeup, GRO enable/disable while up, channel resize with and without attached XDP, XDP attach rejection for too-large peer MTU or insufficient RX queues, XDP_PASS/TX/REDIRECT/DROP behavior, ndo_xdp_xmit bulk injection, XDP metadata reads for skb-backed packets, peer ifindex ethtool stat reporting, page-pool stats when configured, and feature/MTU restoration after XDP program removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/veth.c -->
