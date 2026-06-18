## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.c

Purpose: implements the shared Ethernet-over-USB link layer for gadget functions such as ECM, EEM, CDC subset, NCM, and RNDIS. It owns the Linux `net_device`, USB request pools, RX/TX queueing, MAC address helpers, suspend/resume behavior, and connect/disconnect handoff between protocol-specific function drivers and the network stack.

Important APIs, types, and functions:
- `struct eth_dev` is the private netdev state. It contains the active `struct gether *port_usb`, netdev/gadget pointers, request freelists, RX frame queue, queue multiplier, protocol wrap/unwrap hooks, work item for RX memory recovery, ZLP/no-reserve flags, interface-name flag, and MAC addresses.
- `qlen()` scales endpoint request queue depth for high/super speed using `qmult`.
- `rx_submit()`, `rx_complete()`, `rx_fill()`, and `eth_work()` manage OUT endpoint receive buffers, unwrap protocol frames, feed SKBs into `netif_rx()`, and retry after allocation pressure.
- `eth_start_xmit()` applies CDC filters, invokes protocol `wrap()` for outgoing frames, queues IN endpoint requests, handles fixed-size NCM transfers and ZLP policy, and maintains netdev stats.
- `tx_complete()` recycles TX requests and wakes the netdev queue.
- Netdev methods are `eth_open()`, `eth_stop()`, and `eth_start_xmit()` in `eth_netdev_ops`; ethtool reports gadget driver information through `eth_get_drvinfo()`.
- Setup and config helpers include `gether_setup_name()`, `gether_setup_name_default()`, `gether_register_netdev()`, `gether_set/attach/detach_gadget()`, MAC getters/setters, `gether_set/get_qmult()`, and `gether_set/get_ifname()`.
- Link lifecycle exports are `gether_connect()`, `gether_disconnect()`, `gether_suspend()`, `gether_resume()`, and `gether_cleanup()`.

Control flow:
- Setup allocates an Ethernet netdev, initializes locks/lists/work, chooses configured or random device/host MACs, installs netdev and ethtool ops, sets MTU bounds, and registers the netdev or returns an unregistered default netdev for later configfs setup.
- A protocol function fills `struct gether` endpoints, filter/framing fields, and callbacks, then calls `gether_connect()` when USB data endpoints are enabled for the selected configuration. Connect enables endpoints, preallocates RX/TX requests, copies wrap/unwrap/header settings into `eth_dev`, sets `port_usb`, turns carrier on, and starts queues if the netdev is open.
- RX requests allocate SKBs sized from Ethernet header + MTU + protocol header + hardware alignment/fixed-size requirements, queue them on the OUT endpoint, and on completion unwrap to one or more SKBs before handing each to the network stack.
- TX begins from the network stack. It checks carrier/endpoint availability, honors suspend wakeup and CDC packet filters, obtains a TX request, optionally protocol-wraps the SKB, queues it on the IN endpoint, and recycles on completion.
- Disconnect clears `port_usb`, stops carrier/queue, disables endpoints, frees idle request objects, clears endpoint descriptors, and resets wrap/unwrap state.

State and persistence:
- MAC addresses, qmult, ifname override, request queues, and carrier state are held in `eth_dev` while the netdev exists.
- `port_usb` is the current active USB configuration link and is guarded by `dev->lock`.
- Request freelists are guarded by `req_lock`; RX memory retry state is a bit in `todo`.
- Network statistics accumulate in `net_device->stats` until netdev unregister.

Dependencies and integration points:
- Integrates Linux networking (`alloc_etherdev`, SKB APIs, `netif_*`, ethtool, MAC validation), USB composite endpoint APIs, and protocol function drivers through `struct gether`.
- Protocol-specific functions supply CDC filters and optional `wrap()`/`unwrap()` callbacks for RNDIS/EEM/NCM framing.
- Configfs macros in `u_ether_configfs.h` call MAC/qmult/ifname helpers.
- Suspend/resume uses `usb_func_wakeup()` or `usb_gadget_wakeup()` depending on function suspend state.

Risks:
- `get_ether_addr()` assumes parseable pairs and does not explicitly reject `hex_to_bin()` failures before composing bytes; invalid strings generally fall through to random address only after `is_valid_ether_addr()` fails.
- `eth_start_xmit()` reads `dev->port_usb` outside the lock after the initial snapshot in some wrap/fixed-size checks; disconnect races are mostly tolerated but deserve stress testing.
- `eth_stop()` disables and re-enables endpoints to flush pending I/O while preserving descriptors, which is hardware-sensitive.
- `rx_submit()` computes buffer sizes from MTU, header, alignment quirks, and fixed lengths; mistakes can cause truncation or excess memory allocation.
- Multi-frame wrappers can retain SKBs and return NULL; `supports_multi_frame` must be set consistently to avoid false drops.
- Queue-depth tuning via `qmult` can create memory pressure at high/super speed.

Test signals:
- Bring up ECM/EEM/NCM/RNDIS/subset gadgets, check netdev registration, carrier transitions, MAC attributes, MTU limits, and ethtool information.
- Run sustained bidirectional traffic at full/high/super speed with disconnect/reconnect cycles and inspect tx/rx error counters.
- Exercise CDC packet filters for broadcast, multicast, directed, and promiscuous traffic.
- Test suspend/resume while TX requests are in flight and verify wakeup behavior.
- Run with low-memory fault injection around SKB/request allocation and ensure RX retry work recovers.
