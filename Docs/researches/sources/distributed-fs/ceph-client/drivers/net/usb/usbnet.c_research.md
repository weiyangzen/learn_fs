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

Probe begins in `usbnet_probe()`. It enables autosuspend support if the concrete USB driver did not advertise it, allocates an Ethernet netdev with `struct usbnet` private data, initializes queues, work items, timers, locks, default MTU and ops, then invokes the minidriver `bind()` if supplied. If no bind hook is present, it either discovers endpoints generically or uses endpoint addresses from `driver_info`. It initializes the optional status interrupt URB, calculates `rx_urb_size`, `hard_mtu`, `maxpacket`, RX/TX queue lengths, assigns a random MAC if needed, sets WLAN/WWAN device type flags, optionally allocates a one-byte padding packet for SG/ZLP avoidance, registers the netdev, stores interface data, and attaches the device.

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
