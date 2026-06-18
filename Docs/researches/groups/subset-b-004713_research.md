# subset-b-004713 Research

Grouped source research for Linux HDLC/WAN and WireGuard files under `sources/distributed-fs/ceph-client/drivers/net`. Each section preserves the original source path and is delimited for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc.c

## Purpose
`hdlc.c` is the generic HDLC core used by WAN hardware drivers and protocol modules. It owns the common `alloc_hdlcdev()`/`register_hdlc_device()` lifecycle, dispatches `ETH_P_HDLC` receive traffic to the currently attached protocol, forwards outbound packets through either protocol-specific `xmit` or the hardware driver, and coordinates carrier-change start/stop callbacks.

## Important APIs, Types, And Functions
The exported API is the file's main contract: `hdlc_start_xmit()`, `hdlc_open()`, `hdlc_close()`, `hdlc_ioctl()`, `alloc_hdlcdev()`, `unregister_hdlc_device()`, `attach_hdlc_protocol()`, `detach_hdlc_protocol()`, `register_hdlc_protocol()`, and `unregister_hdlc_protocol()`. It depends on the public `struct hdlc_device` and `struct hdlc_proto` definitions from `<linux/hdlc.h>`. `hdlc_packet_type` registers the receive hook for `ETH_P_HDLC`, and `hdlc_notifier` observes `NETDEV_CHANGE` events for carrier transitions.

## Control Flow
Module init registers the netdevice notifier and packet handler. Hardware drivers allocate an HDLC netdevice with `alloc_hdlcdev()`, then fill `hdlc->attach` and `hdlc->xmit` before `register_hdlc_device()`. User-space protocol selection is routed through `hdlc_ioctl()`: the currently attached protocol gets first chance, then all registered protocol modules are scanned. On open, the core calls `proto->open()`, records the open state under `state_lock`, and calls `proto->start()` immediately if carrier is already present. Carrier changes also call `proto->start()` or `proto->stop()` while holding the same lock. On close, open state is cleared, an active protocol is stopped, and `proto->close()` is invoked outside the spinlock.

## State And Persistence
State is in memory only: global `first_proto`, per-device `hdlc->proto`, optional `hdlc->state`, carrier/open flags, and a per-device spinlock. No durable persistence exists. `attach_hdlc_protocol()` allocates protocol state and module-pins the protocol owner; `detach_hdlc_protocol()` invokes optional protocol cleanup, drops the module reference, frees state, and resets netdevice properties to raw HDLC defaults.

## Dependencies And Integration Points
The file integrates with rtnetlink, netdevice notifiers, packet taps, `init_net`, protocol modules such as raw/Cisco/FR/PPP/X.25, and hardware drivers such as SCA, wanXL, and IXP4xx HSS. It assumes protocol changes occur with the device administratively down and uses `NETDEV_PRE_TYPE_CHANGE`/`NETDEV_POST_TYPE_CHANGE` around type transitions in protocol modules.

## Risks
`hdlc_rcv()` calls `BUG_ON(!hdlc->proto->netif_rx)`, so a malformed protocol attachment can panic the kernel. Receive handling is restricted to `init_net`; packets on HDLC devices outside the initial namespace are dropped. `detach_hdlc_protocol()` relies on callers respecting device-down constraints; detaching while callbacks are active would be unsafe. `first_proto` is protected by RTNL registration paths, so protocol ioctl scanning must remain under the expected netdevice serialization.

## Test Signals
Useful signals are protocol attach/detach via `sethdlc`, `IF_GET_PROTO` responses, `NETDEV_POST_TYPE_CHANGE` notifications from protocol modules, carrier up/down messages, packet delivery through `hdlc_type_trans()`, and module unload/reload with multiple registered protocol modules. Regression tests should exercise attach failure cleanup, carrier transitions while open and closed, and unregistering a device with an attached protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_cisco.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_cisco.c

## Purpose
`hdlc_cisco.c` implements Cisco HDLC protocol support for the generic HDLC core. It adds Cisco HDLC framing, keepalive negotiation, link dormancy management, and ioctl-based protocol selection using `IF_PROTO_CISCO`.

## Important APIs, Types, And Functions
The key wire structures are `struct hdlc_header` and `struct cisco_packet`. `struct cisco_state` holds user settings, a timer, peer sequence tracking, link-up state, and a spinlock. The protocol callbacks are `cisco_start()`, `cisco_stop()`, `cisco_type_trans()`, `cisco_rx()`, and `cisco_ioctl()` in a `struct hdlc_proto`. `cisco_hard_header()` is exposed through `cisco_header_ops`, and `cisco_keepalive_send()` creates control packets for address replies and keepalive requests.

## Control Flow
When user space selects Cisco HDLC, `cisco_ioctl()` validates privileges, device-down state, interval and timeout, asks the hardware driver to attach NRZ/CRC16, allocates `struct cisco_state`, stores settings, installs header ops, changes `dev->type` to `ARPHRD_CISCO`, and marks the interface dormant. On carrier start, `cisco_start()` initializes sequence state and starts a one-second timer. The timer checks timeout, marks the link dormant if keepalives age out, sends a `CISCO_KEEPALIVE_REQ`, and re-arms itself using the configured interval. Receive dispatch validates the Cisco header, drops system-info packets, replies to address requests with the configured IPv4 address if present, and uses keepalive ACKs to mark the link up.

## State And Persistence
All state is volatile per HDLC device. `txseq`, `rxseq`, `last_poll`, and `up` are guarded by `cisco_state.lock`. The timer is deleted synchronously on stop. The module registers and unregisters only the protocol callback object.

## Dependencies And Integration Points
This module depends on the generic HDLC protocol registry, netdevice header ops, `dev_queue_xmit()`, IPv4 address access via `__in_dev_get_rcu()`, traffic-control priority for control packets, and `netif_dormant_on/off()` to expose protocol-level link health separately from physical carrier.

## Risks
Timer send runs while `st->lock` is held and calls into transmit queueing, so changes around locking or allocator context need care. Keepalive packet validation allows only two exact Cisco control lengths; unexpected peer variants are treated as errors. The address-request path assumes `init_net` behavior inherited from the HDLC core. User-provided keepalive intervals are minimally bounded, so very low values could create excessive control traffic.

## Test Signals
Test by attaching Cisco HDLC with invalid and valid settings, confirming netdevice type and dormant state, observing periodic keepalive frames, simulating keepalive ACKs to transition dormant off, checking timeout transition back to dormant, and confirming unsupported protocols are dropped without corrupting stats except intended error counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_cisco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_fr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_fr.c

## Purpose
`hdlc_fr.c` implements Frame Relay support for generic HDLC. It configures FRAD devices, manages DLCI/PVC child netdevices, supports ANSI, CCITT, Cisco, and no-LMI modes, parses and emits LMI status traffic, and maps received Frame Relay payloads to IP, IPv6, SNAP, or Ethernet-bridged PVC devices.

## Important APIs, Types, And Functions
`struct fr_hdr` describes the Q.922 two-byte Frame Relay header. `struct pvc_device` tracks each DLCI and its optional point-to-point and Ethernet child devices. `struct frad_state` stores `fr_proto` settings, sorted PVC list, LMI timer state, DCE/DTE counters, reliability, sequence numbers, and recent error history. Core functions include `q922_to_dlci()`, `dlci_to_q922()`, `add_pvc()`, `delete_unused_pvcs()`, `fr_hard_header()`, `pvc_xmit()`, `fr_lmi_send()`, `fr_lmi_recv()`, `fr_rx()`, `fr_start()`, `fr_stop()`, `fr_add_pvc()`, `fr_del_pvc()`, and `fr_ioctl()`.

## Control Flow
`fr_ioctl()` handles protocol setup and PVC creation/deletion. Protocol setup validates LMI parameters and DCE mode, attaches NRZ/CRC16 to the hardware, allocates `frad_state` if needed, and sets `ARPHRD_FRAD`. PVC add creates either an `ARPHRD_DLCI` child named `pvc%d` or an Ethernet child named `pvceth%d`, stores it in the DLCI record, and increments DCE PVC count when a previously unused PVC becomes used. Child transmit calls `pvc_xmit()`, which verifies active state, pads Ethernet frames, ensures headroom, prepends FR encapsulation, and sends through the FRAD.

On receive, `fr_rx()` validates the Q.922 header and routes matching LMI DLCIs to `fr_lmi_recv()`. Non-LMI payloads are looked up by DLCI, FECN/BECN state is updated, and payload format is decoded: direct NLPID IP/IPv6 goes to the main PVC, SNAP OUI `00-00-00` maps to Ethertype on the main PVC, and SNAP OUI `00-80-C2` PID `00-07` maps to Ethernet frames on the Ethernet PVC. LMI timers differ by role: DTE sends status enquiries and grades reliability with N391/N392/N393, while DCE waits for requests and sends integrity or full reports.

## State And Persistence
PVCs and LMI state are in-memory only. PVC activity is a combination of administrative open count, LMI existence/new/active bits, and FRAD carrier reliability. `fr_destroy()` unregisters child devices and frees all PVC records during detach. Timers are created on protocol start and synchronously deleted on stop.

## Dependencies And Integration Points
The file integrates deeply with generic HDLC, rtnetlink netdevice registration, Ethernet setup for bridged PVCs, IPv4/IPv6/SNAP protocol demux, netdevice carrier/dormant APIs, traffic-control priority for LMI control frames, and user-space `sethdlc` ioctls. It uses child-device `ml_priv` to link back to PVC metadata.

## Risks
The PVC list is manually maintained and relies on RTNL/admin serialization. LMI parsing uses many direct byte offsets; malformed frames are checked, but any future format extension needs careful bounds auditing. `fr_lmi_send()` refuses full DCE reports that exceed `HDLC_MAX_MRU`, so very large PVC sets can fail status reporting. Active PVC state depends on timer behavior, carrier state, and DCE/DTE role, making state-machine regressions easy if changes are not tested with both roles.

## Test Signals
High-value tests attach all LMI modes, create/delete both DLCI and Ethernet PVC devices, validate netdevice type and headroom, inject malformed LMI frames, verify DTE reliability transitions after missed replies, verify DCE full-report/new-bit behavior, test IP/IPv6/SNAP receive demux, and ensure detach unregisters child devices without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_fr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_ppp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_ppp.c

## Purpose
`hdlc_ppp.c` implements PPP over generic HDLC, including HDLC-style PPP framing, LCP/IPCP/IPv6CP control protocol state machines, echo keepalives, and protocol demux for IP and IPv6 payloads.

## Important APIs, Types, And Functions
`struct hdlc_header` and `struct cp_header` describe PPP-over-HDLC and PPP control packets. `struct proto` stores one CP instance with timer, PID, state, last request ID, and retry counter. `struct ppp` stores the three CP instances, shared lock, last echo reply time, retry/timeout settings, and sequence numbers. `ppp_cp_event()` is the main state-machine executor using `cp_table`. Other important functions are `ppp_hard_header()`, `ppp_tx_cp()`, `ppp_cp_parse_cr()`, `ppp_rx()`, `ppp_timer()`, `ppp_start()`, `ppp_stop()`, and `ppp_ioctl()`.

## Control Flow
Attaching PPP through `ppp_ioctl()` requires CAP_NET_ADMIN, a down device, and successful hardware attach with NRZ/CRC16. The module allocates `struct ppp`, initializes defaults, installs PPP header ops, sets `ARPHRD_PPP`, and marks the device dormant. On start, all CP structs are initialized and LCP receives a START event. LCP opening clears dormancy, starts IPCP and IPv6CP, records `last_pong`, and schedules echo keepalives. Incoming control packets are parsed under `ppp->lock`; Configure-Request options are ACKed, NAKed, or rejected, ACK/NAK/Terminate/Code-Reject events drive `cp_table`, and unsupported protocols are rejected when LCP is open. Timers retransmit configure/terminate requests, restart after carrier loss, or send LCP echo requests.

## State And Persistence
State is per attached HDLC device plus one module-global `tx_queue`, used to defer `dev_queue_xmit()` until after releasing the PPP spinlock. There is no durable persistence. Timers are deleted when protocols reach CLOSED, and `ppp_close()` flushes pending control packets.

## Dependencies And Integration Points
The file integrates with generic HDLC attach/xmit, header ops, `netif_dormant_on/off()`, timer APIs, skb queues, and standard PPP protocol identifiers. IP and IPv6 payloads are exposed to the kernel stack through `ppp_type_trans()` after stripping the four-byte HDLC PPP header.

## Risks
The module-global `tx_queue` is shared by all PPP HDLC devices and relies on flushing discipline after lock release; concurrency assumptions should not be relaxed casually. Control parsing uses direct casts after length checks; option parsing must preserve the existing bounds checks. `ppp_tx_cp()` uses a static zero-initialized `magic` value for echo/control magic, so it is not a robust loop-detection mechanism. All configurable retry/keepalive values are hard-coded; behavior changes require protocol-level testing.

## Test Signals
Signals include successful PPP attach, LCP open/dormant-off, IPCP/IPv6CP start after LCP, handling of Configure-Ack/Nak/Rej, Echo-Reply updating `last_pong`, timeout-triggered LCP restart, IP/IPv6 payload demux, and module unload with timers inactive. Fuzzing CP frames should focus on short packets, malformed option lengths, and unknown protocol rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_ppp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw.c

## Purpose
`hdlc_raw.c` provides raw IP-over-HDLC support for the generic HDLC framework. It is the simplest protocol module: attach line encoding/parity, classify received frames as IPv4, and let the hardware driver transmit unmodified HDLC payloads.

## Important APIs, Types, And Functions
The module has one `struct hdlc_proto` with `.type_trans = raw_type_trans` and `.ioctl = raw_ioctl`. `raw_ioctl()` handles `IF_GET_PROTO` and `IF_PROTO_HDLC` using `raw_hdlc_proto`. `raw_type_trans()` always returns `ETH_P_IP`.

## Control Flow
When selected via ioctl, the function requires CAP_NET_ADMIN and a down device, copies `raw_hdlc_proto` from user space, normalizes default encoding to NRZ and default parity to CRC16 PR1 CCITT, asks the hardware driver to attach those settings, attaches this protocol with enough state to store the settings, changes `dev->type` to `ARPHRD_RAWHDLC`, notifies type change, and clears dormancy. Receive classification has no frame header parsing; generic HDLC will classify packets as IP.

## State And Persistence
Only the copied `raw_hdlc_proto` settings are persisted in the per-device HDLC state until detach. There are no timers, queues, child devices, or persistent external resources.

## Dependencies And Integration Points
The module depends on generic HDLC attach/detach, hardware-driver `hdlc->attach()` support for the requested encoding/parity, netdevice type-change notifications, and user-space WAN ioctls.

## Risks
Because every received frame is treated as IPv4, non-IP frames are passed upward with an IP protocol tag. Correctness depends on administrators selecting this mode only for raw IP links. Encoding/parity validation is delegated to the hardware attach callback.

## Test Signals
Attach with default and explicit line settings, confirm state returned by `IF_GET_PROTO`, confirm type `ARPHRD_RAWHDLC`, verify dormant-off after attach, and exercise unsupported hardware parity/encoding errors through `hdlc->attach()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw_eth.c

## Purpose
`hdlc_raw_eth.c` presents an HDLC link as an Ethernet-like netdevice. It uses Ethernet header parsing for receive and pads short transmit frames before delegating to the hardware HDLC transmitter.

## Important APIs, Types, And Functions
The protocol callback object sets `.type_trans = eth_type_trans`, `.xmit = eth_tx`, and `.ioctl = raw_eth_ioctl`. `eth_tx()` pads frames shorter than `ETH_ZLEN`, growing tailroom if required, then calls `dev_to_hdlc(dev)->xmit()`. `raw_eth_ioctl()` mirrors raw HDLC setup but calls `ether_setup()` and assigns a random Ethernet address.

## Control Flow
`IF_PROTO_HDLC_ETH` requires admin privileges and a down device. Defaults are normalized to NRZ and CRC16 PR1 CCITT. After successful hardware attach and protocol attach, the module stores settings, preserves the old TX queue length across `ether_setup()`, disables TX skb sharing, randomizes MAC address, notifies the type change, and marks the device non-dormant. Outbound packets go through `hdlc_start_xmit()`, which calls this module's `eth_tx()`.

## State And Persistence
Per-device state stores only `raw_hdlc_proto` settings. MAC address is generated for the current netdevice instance and is not made durable by this file. No timers or child objects are used.

## Dependencies And Integration Points
This module integrates with generic HDLC, Ethernet netdevice setup, `eth_type_trans()`, skb head/tail management, netdevice stats, and WAN protocol ioctls.

## Risks
The module changes a WAN HDLC device into an Ethernet-shaped device; generic HDLC detach must reset all altered netdevice fields, which `hdlc_setup_dev()` explicitly handles. Padding failures update `tx_dropped` and consume the skb. Protocol correctness depends on both endpoints agreeing to Ethernet emulation over HDLC.

## Test Signals
Test attach/detach restores device shape, random MAC assignment, TX padding to `ETH_ZLEN`, behavior when `pskb_expand_head()` fails, receive classification via `eth_type_trans()`, and `IF_GET_PROTO` returning the stored line settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_x25.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_x25.c

## Purpose
`hdlc_x25.c` bridges generic HDLC devices to the kernel LAPB/X.25 stack. It accepts X.25 pseudo-header commands from upper layers, passes data through LAPB, and sends LAPB connect/disconnect/data indications back through the X.25 network stack.

## Important APIs, Types, And Functions
`struct x25_state` contains `x25_hdlc_proto` settings, an `up` flag with spinlock, a receive queue, and a tasklet. Important callbacks are `x25_open()`, `x25_close()`, `x25_rx()`, `x25_xmit()`, `x25_data_indication()`, `x25_data_transmit()`, and the connect/disconnect helpers. The protocol object supplies `.open`, `.close`, `.ioctl`, `.netif_rx`, and `.xmit`.

## Control Flow
Protocol selection validates optional X.25 settings or applies backward-compatible defaults, attaches hardware as NRZ/CRC16, allocates `x25_state`, initializes queues and tasklet, sets `ARPHRD_X25`, and adjusts headroom for the one-byte pseudo-header versus LAPB header insertion. Device open registers LAPB callbacks, applies DCE/modulo/window/timer parameters, and marks the state up. Upper-layer transmit first checks the one-byte pseudo-header: data is sent by `lapb_data_request()`, connect by `lapb_connect_request()`, and disconnect by `lapb_disconnect_request()`. Received HDLC frames are passed into `lapb_data_received()` while up. LAPB callbacks enqueue X.25 pseudo-header indications and schedule the tasklet to call `netif_receive_skb_core()`.

## State And Persistence
All state is per-device volatile memory. The `up` flag serializes data paths against close. `rx_queue` buffers indications until tasklet processing. `x25_close()` marks the link down, unregisters LAPB, and kills the tasklet.

## Dependencies And Integration Points
The module depends on generic HDLC, the kernel LAPB implementation, `<net/x25device.h>` helpers such as `x25_type_trans()`, tasklets, skb queues, and WAN ioctls.

## Risks
`x25_open()` returns errors after `lapb_register()` if `lapb_getparms()` or `lapb_setparms()` fails without explicitly unregistering LAPB in those intermediate paths. Data transmit ignores the hardware `xmit()` return value by design. Correct operation requires upper layers to provide the pseudo-header byte. Tasklet and up-lock sequencing are important for preventing delivery after close.

## Test Signals
Test invalid and default settings, LAPB registration failure paths, open/close with queued indications, connect/disconnect pseudo-header handling, data transfer through LAPB, malformed short transmit packets, carrier and dormant state, and tasklet cleanup on close/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_x25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/ixp4xx_hss.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/ixp4xx_hss.c

## Purpose
`ixp4xx_hss.c` is an Intel IXP4xx HSS synchronous serial/HDLC driver. It configures the platform NPE firmware, Queue Manager queues, GPIO modem-control lines, DMA descriptors, NAPI receive handling, and generic HDLC integration for IXP4xx HSS ports.

## Important APIs, Types, And Functions
`struct port` is the central device state: NPE handle, queue IDs, GPIOs, HDLC netdevice, NAPI object, DMA descriptor table, RX/TX buffer arrays, clock settings, carrier, and HDLC config flags. `struct msg` models NPE commands. `struct desc` models HDLC packet descriptors. Important functions include `hss_npe_send()`, `hss_config()`, `hss_load_firmware()`, `hss_hdlc_poll()`, `hss_hdlc_xmit()`, `request_hdlc_queues()`, `init_hdlc_queues()`, `hss_hdlc_open()`, `hss_hdlc_close()`, `hss_hdlc_attach()`, `find_best_clock()`, `hss_hdlc_ioctl()`, and `ixp4xx_hss_probe()`.

## Control Flow
Probe verifies SoC HDLC/HSS feature bits through syscon, requests an NPE engine from device tree, reads Queue Manager queue phandles, obtains CTS/RTS/DCD/DTR/internal-clock GPIOs, allocates an HDLC netdevice, sets hardware attach/xmit callbacks, adds NAPI, and registers the device. Open calls `hdlc_open()`, loads NPE firmware if needed, requests queues, allocates coherent descriptors and DMA RX buffers, samples DCD, requests a DCD IRQ, asserts DTR/RTS, populates TX-ready and RX-free queues, enables NAPI and queue IRQs, configures the NPE port, starts packet flow, and schedules receive polling. TX maps skb data, obtains a TX descriptor from the ready queue, submits it to the TX queue, and stops the netdev queue if descriptors run out. RX IRQ disables queue IRQ and schedules NAPI; polling drains descriptors, maps status to stats, copies/switches buffers depending on endian mode, calls `hdlc_type_trans()`, and returns descriptors to RX-free.

## State And Persistence
State is volatile and hardware-backed. `ports_open` and `dma_pool` are module-global. Per-port descriptor memory is coherent DMA. Queue contents live in IXP4xx Queue Manager hardware. Carrier is based on DCD unless loopback forces carrier. Close drains queues, disables IRQs, deasserts modem lines, frees DMA buffers/descriptors, releases queues, and calls `hdlc_close()`.

## Dependencies And Integration Points
The driver integrates with generic HDLC, IXP4xx NPE firmware loader, IXP4xx Queue Manager, syscon feature detection, device tree phandles, GPIO descriptors, DMA API, NAPI, and platform-driver probing.

## Risks
Probe contains a concrete lifecycle hazard: it assigns `ndev = alloc_hdlcdev(port)` and then separately assigns `port->netdev = alloc_hdlcdev(port)`, but initializes and registers `ndev` while runtime/remove paths use `port->netdev`. That can leak one netdevice and unregister/free the wrong one. Several NPE command failures call `BUG()`, turning firmware/queue faults into kernel panics. `hss_hdlc_ioctl()` calls `hss_hdlc_set_clock()` before fully validating `clock_type`, so an invalid value after GPIO side effects should be considered. Queue drain loops can log critical errors if NPE descriptors remain stuck.

## Test Signals
Tests need platform/device-tree coverage for all phandles, open/close queue allocation and cleanup, DCD IRQ carrier changes, internal/external clock ioctls, CRC16/CRC32 attach validation, TX descriptor exhaustion and wakeup, RX status-to-stats mapping, and remove after probe failure. Static analysis should flag the double-netdev allocation and mismatched `port->netdev` usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/ixp4xx_hss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/lapbether.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/lapbether.c

## Purpose
`lapbether.c` creates pseudo X.25/LAPB netdevices over Ethernet devices. It registers an `ETH_P_DEC` packet handler, creates `lapb%d` devices when Ethernet devices come up, and uses the kernel LAPB layer to encapsulate X.25-style pseudo-header traffic inside Ethernet frames with a two-byte length prefix.

## Important APIs, Types, And Functions
`struct lapbethdev` links an Ethernet device to its LAPB/X.25 netdevice and holds up-state, receive queue, and NAPI. Important functions are `lapbeth_rcv()`, `lapbeth_data_indication()`, `lapbeth_xmit()`, `lapbeth_data_transmit()`, `lapbeth_connected()`, `lapbeth_disconnected()`, `lapbeth_open()`, `lapbeth_close()`, `lapbeth_new_device()`, `lapbeth_free_device()`, and `lapbeth_device_event()`.

## Control Flow
Module init registers the DEC packet handler and a netdevice notifier. On `NETDEV_UP` for an Ethernet device, `lapbeth_new_device()` allocates a `lapb%d` netdevice, computes required headroom from the underlying Ethernet device, holds the Ethernet device, initializes NAPI and queues, registers the netdevice, and adds it to the RCU list. Incoming DEC frames are cloned if needed, length-checked for the two-byte prefix, mapped to the matching `lapbethdev`, and passed to `lapb_data_received()` while up. Upper transmit expects a one-byte X.25 pseudo-header; data calls `lapb_data_request()`, connect/disconnect call LAPB control APIs. LAPB's data-transmit callback prepends a two-byte length and Ethernet header and queues the frame to the underlying Ethernet device.

## State And Persistence
State is volatile. The global RCU list tracks active mappings. `up` is protected by `up_lock`, RX indications are queued to NAPI, and the Ethernet device reference is held until unregister. Cleanup unregisters notifiers/packet handler and removes all remaining pseudo devices under RTNL.

## Dependencies And Integration Points
The file depends on Ethernet netdevices in `init_net`, packet type hooks, netdevice notifiers, the LAPB module, X.25 type translation, NAPI, RCU list traversal, and `netdev_lock` semantics via `dev_is_ethdev()`.

## Risks
The DEC packet handler accepts broadcast-style encapsulated traffic on any managed Ethernet device in `init_net`, so deployment must account for link-layer exposure. `lapbeth_rcv()` increments underlying Ethernet stats based on the embedded length before trimming. Removal uses RCU list deletion plus netdevice unregister; ordering must preserve the held Ethernet reference. A malformed length can trim beyond pulled data only as allowed by skb helpers; pskb and trim behavior should be regression-tested.

## Test Signals
Test automatic pseudo-device creation/removal on Ethernet up/unregister, prevention of underlying type changes, open/close LAPB registration, connect/disconnect pseudo-header delivery, DEC frame receive with valid/short lengths, NAPI draining, and cleanup with multiple devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/lapbether.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/n2.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/n2.c

## Purpose
`n2.c` is the ISA-style SDL RISCom/N2 synchronous serial card driver. It exposes up to two generic HDLC netdevices backed by a Hitachi HD64570 SCA controller, memory-windowed RAM, I/O ports, and module-parameter hardware configuration.

## Important APIs, Types, And Functions
`port_t` stores per-port HDLC device, SCA settings, ring indices, clock registers, and physical/logical node identity. `card_t` stores mapped RAM window, I/O port, IRQ, RAM/ring sizing, and two ports. The driver includes shared `hd64570.c`, which supplies SCA helpers such as `sca_init()`, `sca_open()`, `sca_close()`, `sca_attach()`, and `sca_xmit()`. Local functions include `n2_set_iface()`, `n2_open()`, `n2_close()`, `n2_ioctl()`, `n2_destroy_card()`, `n2_run()`, and `n2_init()`.

## Control Flow
The `hw` module parameter is parsed as `io,irq,ram,ports[:...]`. `n2_run()` validates I/O, IRQ, and memory-window values, allocates a card and two HDLC netdevices, requests I/O and IRQ, maps the RAM window, resets/configures the board, detects RAM, sizes SCA TX/RX rings, starts the SCA, initializes enabled ports, and registers their HDLC devices. Open calls `hdlc_open()`, asserts DTR, opens the memory/DMA window, starts SCA, and applies clock/interface settings. Close stops SCA, deasserts DTR, and calls `hdlc_close()`. Ioctls handle sync-serial settings locally and delegate unknown WAN requests to `hdlc_ioctl()`.

## State And Persistence
All hardware state is runtime-only. Cards are held in a global linked list for module cleanup. Port settings are in memory and not persisted across unload. Resource cleanup releases IRQ, I/O ports, memory region, ioremap, HDLC devices, and netdev allocations.

## Dependencies And Integration Points
The driver depends on ISA I/O accessors, memory-mapped board RAM, `hd64570.c`, generic HDLC, WAN sync-serial ioctls, and module parameter parsing.

## Risks
The module cannot auto-detect hardware; incorrect `hw` parameters can cause failed probes or unsafe legacy I/O assumptions. Cleanup paths call `unregister_hdlc_device()` then later `free_netdev()`, so port ownership must remain consistent. Ring sizing depends on detected RAM and enabled-port count; low RAM aborts after resource allocation and must fully unwind.

## Test Signals
Test invalid parameter parsing, single-port and dual-port enablement, RAM detection failure, open/close DTR and DMA-window behavior, clock type validation, SCA ring debug ioctl, and cleanup after partial initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/n2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/pc300too.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/pc300too.c

## Purpose
`pc300too.c` is a PCI driver for Cyclades PC300 synchronous serial cards using HD64572 SCA-II. It registers one or two generic HDLC ports, configures PLX PCI9050 bridge registers, maps SCA and buffer RAM, supports X.21/V.35/V.24 interface selection depending on card type, and delegates packet movement to shared `hd64572.c`.

## Important APIs, Types, And Functions
`plx9050` models bridge registers. `port_t` stores NAPI, netdev, SCA ring indices, sync settings, interface type, and channel number. `card_t` stores mapped RAM/SCA/PLX bases, saved init control, ring sizing, card type, port count, and IRQ. Core functions include `pc300_set_iface()`, `pc300_open()`, `pc300_close()`, `pc300_ioctl()`, `pc300_pci_init_one()`, and `pc300_pci_remove_one()`.

## Control Flow
Probe enables the PCI device, requests regions, allocates card state, validates BAR sizes, maps PLX/SCA/RAM regions, works around a PLX read bug by temporarily switching BAR0, derives card type and port count, allocates HDLC netdevices, resets/reloads the bridge, detects RAM, chooses clock source, sizes rings, enables bridge interrupts, requests IRQ, initializes SCA and ports, and registers HDLC devices. Open calls `hdlc_open()`, starts SCA, and applies interface settings. Ioctl exposes `IF_GET_IFACE` and accepts only interface modes compatible with the detected card type before delegating other requests to generic HDLC.

## State And Persistence
State is volatile in `card_t` and `port_t`. Module parameters `pci_clock_freq` and `use_crystal_clock` influence `CLOCK_BASE` at module init. Cleanup unregisters HDLC devices, frees IRQ, unmaps BARs, releases PCI regions, disables the device, frees netdevices, and frees card memory.

## Dependencies And Integration Points
The driver depends on PCI IDs for Cyclades PC300 variants, PLX bridge register behavior, `hd64572.c` SCA helpers, generic HDLC, NAPI fields shared with SCA code, sync-serial ioctls, and module parameters.

## Risks
PC300 TE cards are detected but noted as not fully supported; users may see registered behavior for hardware with incomplete semantics. The PLX BAR workaround is hardware-specific and sensitive to ordering. `CLOCK_BASE` is global, so multiple cards with different clock expectations are not represented. Error unwind must handle partially allocated netdevices and mapped resources.

## Test Signals
Test PCI probe on 1-port and 2-port IDs, invalid BAR-size rejection, RAM-detection failure, IRQ request failure unwind, card type to allowed interface mapping, `use_crystal_clock` behavior, open/close SCA start/stop, and generic protocol attach through `hdlc_ioctl()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/pc300too.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/pci200syn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/pci200syn.c

## Purpose
`pci200syn.c` is the Goramo PCI200SYN synchronous serial card driver. It exposes two V.35 generic HDLC ports over a PLX PCI bridge and HD64572 SCA-II controller, using shared `hd64572.c` logic for rings, interrupts, attach, and xmit.

## Important APIs, Types, And Functions
`plx9052` models the bridge registers. `port_t` stores netdev, card pointer, spinlock, sync settings, SCA channel/ring state, encoding, parity, and NAPI. `card_t` stores mapped RAM/SCA/PLX bases, ring sizing, IRQ, and two ports. Local functions include `new_memcpy_toio()` for chunked writes with posted-write flushing, `pci200_set_iface()`, `pci200_open()`, `pci200_close()`, `pci200_ioctl()`, `pci200_pci_init_one()`, and `pci200_pci_remove_one()`.

## Control Flow
Module init validates `pci_clock_freq` and registers the PCI driver. Probe enables PCI, requests regions, allocates card and two HDLC netdevices, validates BAR sizes, maps PLX/SCA/RAM, resets the PLX bridge, detects RAM, sizes TX/RX rings for two ports, enables bridge interrupts, requests shared IRQ, initializes SCA, initializes each port, and registers HDLC devices. Open/close wrap `hdlc_open()`/`hdlc_close()` with SCA start/stop and bridge flushing. Ioctl exposes V.35 sync serial settings and delegates other WAN commands to `hdlc_ioctl()`.

## State And Persistence
All state is runtime memory and hardware registers. The only module-level setting is `pci_clock_freq`, used as `CLOCK_BASE`. Cleanup releases IRQ, unmaps resources, releases PCI regions, disables the device, frees netdevices, and frees `card_t`.

## Dependencies And Integration Points
The file integrates with PCI matching on PLX subsystem IDs, generic HDLC, shared `hd64572.c`, SCA interrupt handling, PLX register access, DMA-capable memory-mapped RAM, and sync-serial ioctls.

## Risks
The driver assumes exactly two ports and V.35 semantics. `new_memcpy_toio()` overrides `memcpy_toio` for included SCA code and relies on readback from `dest` after advancing, which is a subtle hardware flush pattern. PCI error unwind must cope with both netdevices allocated before BAR validation. As with similar SCA drivers, changing shared `hd64572.c` contracts can affect this driver indirectly.

## Test Signals
Test PCI matching, invalid clock parameter rejection, invalid BAR sizes, RAM/ring sizing, IRQ request failure, open/close flush behavior, V.35 ioctl validation, protocol attach via generic HDLC, and SIOCDEVPRIVATE ring dumps when debug is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/pci200syn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.c

## Purpose
`slic_ds26522.c` is a SPI driver for configuring a Maxim DS26522 line interface/framer device, specifically programming it for E1 operation. It performs product-code detection, reset, register clearing, clock setup, E1 framer/LIU configuration, and SPI driver binding.

## Important APIs, Types, And Functions
Important helpers are `slic_write()`, `slic_read()`, `get_slic_product_code()`, `ds26522_e1_spec_config()`, `slic_ds26522_init_configure()`, `slic_ds26522_probe()`, and `slic_ds26522_remove()`. The driver uses register and bit constants from `slic_ds26522.h`. `g_spi` is assigned in probe but not otherwise used by this file.

## Control Flow
Probe stores the SPI device globally, sets `bits_per_word` to 8, reads the product ID register through the DS26522 bit-reversed SPI address format, and returns success without configuration if the product code does not match. If detection passes, `slic_ds26522_init_configure()` programs global clock registers, asserts global LIU/framer resets, clears receiver/transmitter/framer/LIU/BERT register ranges, calls `ds26522_e1_spec_config()` to set E1 receive/transmit mode, clocks, framing, impedance, and transmitter enable, then clears GTCR1.

## State And Persistence
State is primarily in hardware registers. The only software state is the global `g_spi`, which is not consumed elsewhere in this source. No runtime control interface or persistent configuration store exists. Remove only logs module removal.

## Dependencies And Integration Points
The driver integrates with the SPI core, OF matching on `maxim,ds26522`, module SPI registration, Linux bit-reversal helpers, and the local DS26522 register header.

## Risks
SPI transfer return values are ignored in `slic_write()` and `slic_read()`, so failed bus operations may silently produce misconfiguration. Probe returns success if product detection fails, which can bind without configuring unsupported or unreachable hardware. The configuration is hard-coded for E1 and 75-ohm assumptions; T1 or alternate impedance/rate constants in the header are unused. `g_spi` is global and would not represent multiple devices correctly.

## Test Signals
Test SPI error injection, product ID mismatch behavior, expected register write sequence for E1 configuration, reset delay timing, OF/SPI ID matching, multiple-device probe behavior, and readback of key DS26522 mode registers after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.h

## Purpose
`slic_ds26522.h` defines DS26522 register addresses, reset values, clock/framer/LIU bit fields, and small enums used by the DS26522 SPI configuration driver. It is a hardware-description header rather than a logic implementation.

## Important APIs, Types, And Functions
There are no functions. Register ranges cover receive framer, global, transmit framer, LIU, test, and BERT address spaces. Individual address constants include mode, clock, reset, ID, E1 TAF/TNAF, receive/transmit control, and LIU impedance/control registers. Bit/value constants encode E1/T1 selection, framer enable, init done, HDB3/CCS, B8ZS, 1.544/2.048 MHz clocking, reset/normal states, and transmitter enable. Enums define `line_rate`, `tdm_trans_mode`, and `card_support_type`.

## Control Flow
Control flow is supplied by `slic_ds26522.c`; this header drives which addresses are cleared and which values are written during E1 setup. The range constants are used in loops that zero framer, LIU, and BERT registers.

## State And Persistence
The header has no runtime state. Its constants describe hardware state that persists in the DS26522 until reset or reprogramming.

## Dependencies And Integration Points
It is included by `slic_ds26522.c` and depends conceptually on the DS26522 data sheet. The enums suggest broader line-control integration, but in this source set only hard-coded E1 configuration is used.

## Risks
There is no include guard, so repeated inclusion would rely on build structure rather than protection. Several constants and enums are unused by the current C file, which can hide stale or unvalidated register definitions. Naming comments reference an older `drivers/tdm/line_ctrl` path, while the file now lives under `drivers/net/wan`.

## Test Signals
Compile coverage is the basic signal. Hardware tests should confirm constants against the DS26522 data sheet and verify that range endpoints do not accidentally cover reserved or test-only registers during zeroing loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.c

## Purpose
`wanxl.c` is the host-side PCI driver for SBE wanXL serial cards. It loads on-card firmware, establishes a shared host/card status area, handles PLX9060 doorbell interrupts, registers generic HDLC ports, and moves HDLC packets through shared descriptors and DMA mappings.

## Important APIs, Types, And Functions
`struct port` stores per-port HDLC netdevice, TX ring indexes, clock type, and skb ownership. `struct card_status` is the shared memory layout visible to firmware, containing RX descriptors and per-port status blocks. `struct card` stores mapped PLX registers, PCI device, RX ring, coherent status memory, and flexible port array. Key functions include `wanxl_cable_intr()`, `wanxl_tx_intr()`, `wanxl_rx_intr()`, `wanxl_intr()`, `wanxl_xmit()`, `wanxl_attach()`, `wanxl_ioctl()`, `wanxl_open()`, `wanxl_close()`, `wanxl_get_stats()`, `wanxl_puts_command()`, `wanxl_reset()`, and `wanxl_pci_init_one()`.

## Control Flow
Probe enables PCI, sets a temporary 28-bit DMA mask for coherent status memory due to card/QUICC limitations, requests regions, allocates the card and coherent `card_status`, restores 32-bit DMA for packet buffers, maps PLX registers, waits for PUTS self-test completion, reads reported RAM size, commands byte-swap mode, allocates RX skbs/descriptors, maps card RAM, writes included firmware and shared-memory pointers into card RAM, commands abort-and-jump, waits for firmware initialization, requests IRQ, allocates/registers HDLC ports, and reports cable state. TX maps skb data, fills a per-port TX descriptor, rings the card doorbell, advances the ring, and stops the queue if the next descriptor is busy. Doorbell interrupt dispatch handles TX completion, cable changes, and RX completions.

## State And Persistence
Firmware and card registers hold active hardware state; host state is volatile. The coherent `card_status` is the key shared contract with firmware. `wanxl_close()` asks firmware to close a port, waits for status, stops the queue, and unmaps/frees outstanding TX skbs. Remove unregisters ports, frees IRQ, resets the card, unmaps RX buffers, unmaps PLX, frees coherent status memory, releases PCI resources, and frees card memory.

## Dependencies And Integration Points
The driver integrates with generic HDLC, PCI IDs for wanXL100/200/400, DMA mapping APIs, PLX9060 registers, the generated `wanxlfw.inc` firmware blob, constants and shared layouts from `wanxl.h`, and firmware-side doorbell/status behavior from `wanxlfw.S`.

## Risks
The host/firmware ABI is tight: descriptor sizes, status offsets, doorbell bits, and endianness must match `wanxl.h` and `wanxlfw.S`. DMA mask switching is delicate and platform-sensitive. `wanxl_rx_intr()` allocates a replacement skb after consuming one; if allocation fails, the descriptor address becomes zero and later packets are dropped until a future successful replacement. Open/close wait loops use `time_after(timeout, jiffies)` style and should be checked carefully when modified. Firmware loading from an included blob complicates independent updates.

## Test Signals
Test probe through firmware initialization, PUTS timeout/failure paths, RAM-size sanity check, DMA mask failures, IRQ dispatch for RX/TX/cable bits, queue stop/wake under TX ring pressure, port open/close status handshakes, RX replacement allocation failure, and generic HDLC attach validation for all supported parity/encoding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.h

## Purpose
`wanxl.h` defines the shared host/firmware ABI for the wanXL driver. It contains board configuration flags, cable/personality status bits, buffer and descriptor constants, PLX register offsets, doorbell bit assignments, status-memory offsets, and C structures used by the host driver.

## Important APIs, Types, And Functions
There are no functions. Important constants include `TX_BUFFERS`, `RX_BUFFERS`, `RX_QUEUE_LENGTH`, `BUFFER_LENGTH`, `BUFFERS_ADDR`, packet states (`PACKET_EMPTY`, `PACKET_FULL`, `PACKET_SENT`, `PACKET_UNDERRUN`), doorbell bits from card and to card, PLX mailbox/doorbell/control offsets, DMA register offsets for assembler, and status offsets. `desc_t` is the shared packet descriptor with volatile status and length. `port_status_t` is the per-port shared status block containing open/cable/error fields, parity/encoding/clocking fields, and TX descriptors.

## Control Flow
The host driver uses these constants to populate shared memory, ring PLX doorbells, and interpret card interrupts. The firmware uses the same values to service open/close/TX commands, fill RX descriptors, and notify cable/TX/RX events.

## State And Persistence
The header declares the layout of volatile shared state; it does not own state itself. `volatile` fields in `desc_t` and `port_status_t` mark locations updated asynchronously by firmware or host.

## Dependencies And Integration Points
The file is included by both `wanxl.c` and `wanxlfw.S`. It includes `HDLC_MAX_MRU` indirectly in `BUFFER_LENGTH` and uses `__ASSEMBLER__` guards to expose different PLX offsets and DMA register definitions for firmware assembly versus host C.

## Risks
Any change to descriptor sizes, offsets, or doorbell bit numbers requires synchronized host and firmware rebuilds. Comments explicitly note that some flags require rebuilding firmware. The ABI uses raw offsets and packed assumptions rather than generated structure validation, so compile-time cross-checks would be valuable.

## Test Signals
Build both host and firmware include paths, verify `sizeof(desc_t)` matches `DESC_LENGTH`, validate status offsets against `port_status_t`, confirm doorbell bit compatibility with firmware event loops, and run hardware tests after any buffer-count or RAM-layout change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/wanxlfw.S -->
# sources/distributed-fs/ceph-client/drivers/net/wan/wanxlfw.S

## Purpose
`wanxlfw.S` is the firmware-side m68k/QUICC code for wanXL cards. It is loaded by `wanxl.c` into on-card RAM and handles SCC HDLC port setup, host/card descriptor movement, PLX DMA transfers, doorbell commands, cable/status monitoring, and interrupts.

## Important APIs, Types, And Functions
The firmware consumes shared constants from `wanxl.h`. Entry starts at `_start`, then `init`. Important routines are `open_port`, `close_port`, `tx`, `rx`, `tx_end`, `pci9060_interrupt`, `port_interrupt_1..4`, `check_csr`, `timer_interrupt`, and optional `ram_test`. Macros implement PCI/local copies either via PLX DMA (`memcpy_from_pci`, `memcpy_to_pci`) or direct windowed memcpy depending on `QUICC_MEMCPY_USES_PLX`.

## Control Flow
Initialization translates host-provided shared-memory PCI addresses into the firmware's window, installs interrupt vectors, configures CPM/PLX interrupts and DMA, optionally sizes/tests RAM, signals initialization through mailbox 5, configures port pins, and enters the main loop. The main loop waits for accumulated `channel_stats`, handles close before open for each port, processes open commands, queues host TX descriptors, services SCC tasks by completing TX and draining RX, builds a host doorbell mask, and writes `PLX_DOORBELL_FROM_CARD`.

`open_port` sets shared open status, initializes TX/RX BD rings in DPRAM, applies clocking from host status, asserts DTR, configures SCC parity/CRC/encoding, and enables SCC interrupts. `tx` copies host packet data into card buffers and marks transmit BDs ready. `rx` validates received BDs, removes parity bytes, copies packet data to host RX descriptors if available, updates error counters on overrun/bad frame, and frees BDs. `tx_end` converts SCC completion into `PACKET_SENT` or `PACKET_UNDERRUN`.

## State And Persistence
Firmware state lives in on-card RAM variables such as `channel_stats`, per-port TX/RX indices, `rx_out`, `tx_count`, `parity_bytes`, and CSR output shadows. Shared host-visible state is stored through `ch_status_addr` and `rx_descs_addr`. State lasts until card reset or firmware reload.

## Dependencies And Integration Points
The firmware depends on m68k/QUICC register layout, PLX9060 mailboxes/doorbells/DMA, SCC HDLC buffer descriptors, shared ABI definitions in `wanxl.h`, and host initialization in `wanxl.c` that writes firmware and shared-memory pointers.

## Risks
Host/firmware ABI drift is the primary risk. The firmware assumes descriptor status values, offsets, buffer counts, and shared memory addresses are valid. PLX DMA copy macros wait for interrupts and must run with expected interrupt masking. RX overrun handling drops frames when host RX descriptors are not empty. Cable status is polled by timer and signaled by doorbells, so status updates depend on firmware timer operation.

## Test Signals
Test firmware load and mailbox initialization, port open/close shared status transitions, host TX descriptor to SCC BD movement, TX underrun reporting, RX good/bad/overrun paths, cable status changes, PLX DMA completion, and compatibility checks after changing `wanxl.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/wanxlfw.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/Makefile

## Purpose
This Kbuild Makefile defines how the in-kernel WireGuard module is built. It sets logging/debug compiler flags, lists all object files that compose `wireguard.o`, and connects the aggregate object to `CONFIG_WIREGUARD`.

## Important APIs, Types, And Functions
There are no C APIs. Build variables are the important interface: `ccflags-y` defines `pr_fmt`, `ccflags-$(CONFIG_WIREGUARD_DEBUG)` adds `-DDEBUG`, `wireguard-y` accumulates object files, and `obj-$(CONFIG_WIREGUARD)` selects the final module/object.

## Control Flow
When `CONFIG_WIREGUARD` is enabled, Kbuild links `wireguard.o` from the listed objects: core device, peer, noise, timers, queueing, send/receive, socket, peer lookup, allowed IPs, ratelimiter, cookie, and netlink/generated netlink sources. When debug config is enabled, files compile with `DEBUG`, enabling debug-only paths such as WireGuard selftests and extra checks.

## State And Persistence
No runtime state exists. The file controls compile-time composition only.

## Dependencies And Integration Points
It integrates with Linux Kbuild and depends on `generated/netlink.o` being generated by the surrounding kernel build. Object order is part of module link composition and should remain aligned with initialization dependencies in WireGuard sources.

## Risks
Removing an object can create link failures or silently drop subsystem behavior. Debug flag changes affect conditional code and selftest visibility. The `pr_fmt` definition is globally applied to this directory, so conflicting source-local definitions would need care.

## Test Signals
Build with `CONFIG_WIREGUARD=m/y`, build with `CONFIG_WIREGUARD_DEBUG=y`, verify `generated/netlink.o` is produced, and run module load/selftest coverage where debug paths are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.c

## Purpose
`allowedips.c` implements WireGuard's allowed-IPs routing table. It stores IPv4 and IPv6 CIDR prefixes in compressed binary tries, maps prefixes to peers, supports longest-prefix lookup for source/destination packet validation/routing, and maintains peer-owned lists for efficient removal.

## Important APIs, Types, And Functions
The public functions are `wg_allowedips_init()`, `wg_allowedips_free()`, `wg_allowedips_insert_v4()`, `wg_allowedips_insert_v6()`, `wg_allowedips_remove_v4()`, `wg_allowedips_remove_v6()`, `wg_allowedips_remove_by_peer()`, `wg_allowedips_read_node()`, `wg_allowedips_lookup_dst()`, `wg_allowedips_lookup_src()`, `wg_allowedips_slab_init()`, and `wg_allowedips_slab_uninit()`. Core internals include `swap_endian()`, `copy_and_assign_cidr()`, `choose()`, `common_bits()`, `prefix_matches()`, `find_node()`, `lookup()`, `node_placement()`, `add()`, `remove_node()`, and `remove()`.

## Control Flow
Insert operations increment the table sequence, convert network-order addresses into trie-order aligned keys, then call `add()` under the caller-provided mutex. `add()` handles empty trie creation, exact prefix replacement/list move, direct child insertion, or intermediate parent creation based on common prefix length. Lookup converts the packet address, enters RCU read-side critical section, finds the best matching node, and returns a strong peer reference with retry if the peer is being torn down. Removal finds the exact node for a peer, clears its peer pointer/list entry, collapses nodes with zero or one child where possible, and defers freeing via RCU. Full table free detaches roots, removes all peer-list entries, and schedules RCU traversal/free of the old roots.

## State And Persistence
The table contains two RCU roots (`root4`, `root6`) and a sequence counter. Each node stores peer pointer, two child pointers, prefix metadata, packed parent pointer/bit, and either peer-list membership or RCU head. Nodes come from a module slab cache. No durable persistence exists; WireGuard netlink configuration repopulates this state at runtime.

## Dependencies And Integration Points
This file integrates with `struct wg_peer` reference counting and `allowedips_list`, skb IP/IPv6 headers, RCU BH read-side locking, caller-held mutexes for mutation, kernel slab caches, and the optional included `selftest/allowedips.c` under debug.

## Risks
Pointer-bit packing depends on alignment; the header explicitly aligns `struct allowedips` for m68k. Mutations require the correct mutex; misuse can corrupt parent links or peer lists. Prefix comparison uses endian-swapped aligned buffers and casts to u32/u64, so alignment assumptions are important. `MAX_ALLOWEDIPS_DEPTH` bounds stack traversal; debug warns on overflow, but trie invariants should keep depth within IPv6 prefix length plus root.

## Test Signals
Use the built-in allowedips selftest under DEBUG, plus tests for overlapping prefixes, exact replacement, peer removal, IPv4/IPv6 longest-prefix lookup, source and destination lookup reference handling, RCU free after table reset, and sequence-number changes on every mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.h

## Purpose
`allowedips.h` declares WireGuard's allowed-IPs trie structures and public operations for initialization, mutation, lookup, readback, and slab-cache lifecycle.

## Important APIs, Types, And Functions
`struct allowedips_node` contains an RCU peer pointer, two RCU child pointers, prefix metadata (`cidr`, bit offsets, bit length, aligned bits buffer), a packed parent pointer/bit, and a union used as either peer-list entry or RCU callback. `struct allowedips` contains IPv4 and IPv6 roots plus a sequence counter and is explicitly aligned because low pointer bits are packed elsewhere. Function declarations cover insert/remove for v4/v6, remove by peer, node readback, destination/source lookup returning strong peer references, debug selftest, and slab init/uninit.

## Control Flow
The header does not implement control flow, but its API establishes the contract: callers initialize a table, mutate it under a mutex, use lookups in packet paths, and free the table while holding the same lock. Readback expects aligned IP output storage.

## State And Persistence
The declared structures are in-memory only. The sequence field lets callers detect route-table changes. Node lifetime is RCU-managed after removal.

## Dependencies And Integration Points
The header includes mutex, IPv4, and IPv6 kernel headers and forward-declares `struct wg_peer`. It is used by WireGuard peer, netlink, send, and receive paths to enforce allowed IP routing and anti-spoofing.

## Risks
The packed parent pointer design means structure alignment is not incidental; changes to `struct allowedips` or allocation alignment must preserve low-bit availability. The union of list and RCU head requires nodes not be on peer lists once scheduled for RCU free. API users must observe the documented strong-reference return from lookups and release peers accordingly.

## Test Signals
Compile with DEBUG to expose `wg_allowedips_selftest()`, verify structure alignment on supported architectures, run netlink add/remove peer allowed-IP tests, and use KASAN/KCSAN/RCU debugging around remove/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.c

## Purpose
`cookie.c` implements WireGuard's handshake MAC and cookie mechanism. It validates MAC1, optionally validates MAC2 cookies tied to source address/port, rate-limits unauthenticated handshake traffic, creates encrypted cookie replies, and consumes cookie replies on peers.

## Important APIs, Types, And Functions
Public functions are `wg_cookie_checker_init()`, `wg_cookie_checker_precompute_device_keys()`, `wg_cookie_checker_precompute_peer_keys()`, `wg_cookie_init()`, `wg_cookie_validate_packet()`, `wg_cookie_add_mac_to_packet()`, `wg_cookie_message_create()`, and `wg_cookie_message_consume()`. Internal helpers are `precompute_key()`, `compute_mac1()`, `compute_mac2()`, and `make_cookie()`. Cryptographic dependencies are BLAKE2s and XChaCha20-Poly1305.

## Control Flow
Initialization seeds the checker secret and lock, while key precomputation derives MAC/cookie keys from static public keys and fixed labels. Outbound handshake messages call `wg_cookie_add_mac_to_packet()`: MAC1 is computed and remembered, then MAC2 is filled only if a still-valid cookie is available. Incoming handshake validation recomputes MAC1 against the device key; if cookie checking is required, it derives a cookie from the rotating secret and packet source address/UDP source port, checks MAC2, and finally asks the ratelimiter before returning `VALID_MAC_WITH_COOKIE`. Cookie replies are created by deriving the same source cookie and encrypting it with the peer's MAC1 as associated data. Cookie replies are consumed by looking up the receiver index, verifying a MAC1 was sent, decrypting, and storing a fresh valid cookie in the peer.

## State And Persistence
`cookie_checker` holds a rotating random secret, birthdate, precomputed device keys, and device pointer. `cookie` holds per-peer decrypted cookie, birthdate, validity flag, last MAC1 sent, sent-MAC flag, precomputed peer keys, and rwsem. Secrets are in memory only and rotate based on `COOKIE_SECRET_MAX_AGE`.

## Dependencies And Integration Points
The module integrates with WireGuard device, peer, index hashtable, timers/birthdate helpers, ratelimiter, skb IP/IPv6/UDP headers, Noise constants, message layouts, BLAKE2s, XChaCha20-Poly1305, and crypto constant-time comparison.

## Risks
Correctness depends on message length including trailing `struct message_macs`; callers must pass complete handshake messages. `make_cookie()` assumes the skb has IP/IPv6 and UDP headers available. Lock ordering around peer cookie rwsem and index lookup must remain consistent with other WireGuard paths. Device key precompute requires the static identity lock as documented by the comment.

## Test Signals
Test MAC1 rejection, valid MAC without cookie, valid MAC2 with ratelimiter allow/deny, cookie secret rotation, encrypted cookie reply creation/consumption, stale cookie latency cutoff, invalid receiver index, consume without prior MAC1, IPv4 and IPv6 source-cookie derivation, and constant-time comparison paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.h

## Purpose
`cookie.h` declares WireGuard cookie/MAC state structures, validation result enum, and public cookie helper functions used by handshake send/receive paths.

## Important APIs, Types, And Functions
`struct cookie_checker` contains the device-wide rotating secret, precomputed cookie encryption key, precomputed MAC1 key, secret birthdate, rwsem, and device pointer. `struct cookie` contains per-peer cookie state, last MAC1 sent, precomputed decryption/MAC1 keys, validity flags, birthdate, and rwsem. `enum cookie_mac_state` distinguishes invalid MAC, valid MAC without cookie, valid cookie but ratelimited, and valid cookie. Function prototypes cover checker/peer initialization, key precompute, packet validation, MAC insertion, cookie message creation, and cookie message consumption.

## Control Flow
The header defines the call contract: devices initialize a checker, peers initialize a cookie and precompute peer keys, send paths add MACs, receive paths validate packets and optionally issue cookie messages, and peers consume encrypted cookie replies.

## State And Persistence
All declared state is volatile memory. The birthdate fields interact with timer helpers to expire cookies and secrets. Locks protect concurrent handshake send/receive access to cookie material.

## Dependencies And Integration Points
The header includes WireGuard message definitions and rwsem support, forward-declares peers, and is consumed by cookie, send, receive, peer, and device code. It depends on Noise and message constants provided by included headers.

## Risks
Callers must respect lock expectations from the implementation, especially static identity locking before device key precompute and peer cookie locking during concurrent send/consume operations. Enum handling must preserve the distinction between ratelimited and fully valid cookies because receive paths use it for response policy.

## Test Signals
Compile all WireGuard users, exercise concurrent send/receive cookie updates under lock debugging, verify enum handling in receive policy, and test secret/cookie expiration using timer helper boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.h -->
