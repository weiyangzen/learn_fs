# subset-b-004702 grouped research

Work item: `subset-b-004702`

This grouped report covers USB network drivers under `sources/distributed-fs/ceph-client/drivers/net/usb/`. Each section is bounded for reconciliation into the mapped per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/ax88179_178a.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/ax88179_178a.c

## Purpose

`ax88179_178a.c` is the ASIX AX88179/AX88178A USB 3.0/2.0 gigabit Ethernet driver. It plugs into the kernel `usbnet` framework but owns the vendor register protocol, PHY/MDIO access, EEPROM/eFuse/LED setup, wake-on-LAN, checksum/TSO feature programming, link reset, and the ASIX-specific RX/TX framing format. The USB ID table maps the same implementation to ASIX, Cypress, D-Link, Samsung, Lenovo, Belkin, Toshiba, MCT, and Allied Telesis adapters.

## Important APIs, types, and functions

The main private state is `struct ax88179_data`, carrying EEE state, cached RX control bits, PM-mode command selection, WoL capabilities/options, and disconnect suppression state. `struct ax88179_int_data` models the interrupt status payload. Register access flows through `ax88179_read_cmd()` and `ax88179_write_cmd()`, which wrap `usbnet_read_cmd*()` and `usbnet_write_cmd*()` with endian conversion and PM-aware variants.

Key hooks are collected in many `struct driver_info` instances, all pointing at the same core callbacks: `ax88179_bind()`, `ax88179_unbind()`, `ax88179_status()`, `ax88179_link_reset()`, `ax88179_net_reset()`, `ax88179_stop()`, `ax88179_rx_fixup()`, and `ax88179_tx_fixup()`. Netdev hooks in `ax88179_netdev_ops` implement MTU changes, MAC address changes, MII ioctls, multicast filtering, and feature toggles. `ax88179_ethtool_ops` exposes EEPROM access, WoL, EEE, message level, link settings, and timestamp metadata.

## Control flow

Probe is delegated to `usbnet_probe()`, which calls `ax88179_bind()`. Bind discovers endpoints, allocates `struct ax88179_data`, installs netdev and ethtool ops, configures MII support, enables SG/checksum/TSO features, sets headroom and max MTU, then calls `ax88179_reset()`. Reset powers and clocks the PHY, optionally enables auto-detach from EEPROM settings, reads or assigns the MAC address, programs RX bulk queue parameters, flow-control watermarks, checksum offload registers, RX control, PME monitor bits, default medium mode, WoL support, LED behavior, EEE defaults, and restarts autonegotiation.

Runtime link events arrive through the interrupt endpoint into `ax88179_status()`, which compares the device link bit with carrier state and schedules `usbnet` link handling. `ax88179_link_reset()` reprograms RX control, polls a TX FIFO control register, reads USB speed and PHY status, chooses bulk-in queue settings from `AX88179_BULKIN_SIZE`, sets `rx_urb_size`, writes medium mode bits for speed/duplex/flow-control/jumbo, updates EEE active state, and marks carrier on. TX prep writes two little-endian ASIX headers before each SKB, including TSO MSS and padding flags. RX parsing reads a trailer header containing packet count and metadata offset, validates the metadata array bounds, skips dummy entries, strips the two-byte IP alignment pseudo-header, handles errors, and returns either the final packet in-place or cloned packets through `usbnet_skb_return()`.

## State and persistence

Persistent device data is accessed through EEPROM and eFuse helpers. `ax88179_get_eeprom()` and `ax88179_set_eeprom()` expose word-aligned EEPROM access to ethtool, including magic validation and reload after writes. LED programming is derived from EEPROM, eFuse, or legacy conversion fallback. Runtime state lives in `dev->driver_priv`, `dev->mii`, `dev->net->features`, `dev->rx_urb_size`, cached `rxctl`, WoL options, and EEE flags. No filesystem persistence is used.

## Dependencies and integration points

The driver depends on `usbnet`, `mii`, `mdio`, ethtool, netdev feature flags, CRC helpers, USB autosuspend, and Ethernet address helpers. It integrates with `usbnet` for URB lifecycle, NAPI-like packet return, carrier changes, suspend/resume, and disconnect. It uses MDIO MMD indirect accesses for EEE and MII callbacks for link settings.

## Risks

The largest risks are malformed RX trailer metadata causing incorrect bounds or packet slicing, hardware register writes during suspend/disconnect, EEPROM writes with partial-word alignment, and link-reset sequencing that depends on undocumented vendor registers. The code has explicit bounds checks for metadata offset/count and suppresses noisy `-ENODEV` warnings while disconnecting, but the heavy use of vendor constants makes hardware regressions likely if setup order changes. Feature toggles XOR checksum bits, so netdev feature state must remain synchronized with hardware state.

## Test signals

Useful tests include module probe/remove with each USB ID class, suspend/resume and WoL wake with magic/link wake, ethtool EEPROM read/write failure cases, EEE get/set with link renegotiation, jumbo MTU transitions around 1500 bytes, multicast/promiscuous mode changes, checksum/TSO traffic, RX aggregation with dummy metadata entries, and USB2/USB3 link-speed changes that alter RX bulk queue sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/ax88179_178a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/catc.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/catc.c

## Purpose

`catc.c` is a standalone USB Ethernet driver for CATC EL1210A NetMate, NetMate II, Belkin F5U011/F5U111 variants, and smartBridges smartNIC devices. Unlike most neighboring files, it does not use `usbnet`; it manually manages netdev registration, bulk/interrupt/control URBs, transmit buffering, receive parsing, multicast filter programming, and periodic hardware statistics.

## Important APIs, types, and functions

`struct catc` is the central state object. It stores the `net_device`, `usb_device`, running bits, TX and control ring indices, spinlocks, fixed TX/RX/control buffers, four URBs, a timer, stats snapshots, multicast hash table, F5U011 mode flags, and a receive backlog counter. Endpoint and request enums define the vendor protocol. Synchronous control helpers include `catc_ctrl_msg()` and macros such as `catc_get_mac()`, `catc_set_reg()`, and `catc_write_mem()`. Async control flow uses `catc_ctrl_async()`, `catc_ctrl_run()`, and `catc_ctrl_done()` with a 16-entry ring.

Netdev hooks are `catc_open()`, `catc_stop()`, `catc_start_xmit()`, `catc_tx_timeout()`, `catc_set_multicast_list()`, `eth_mac_addr`, and address validation. URB completions are `catc_rx_done()`, `catc_irq_done()`, `catc_tx_done()`, and `catc_ctrl_done()`. `catc_probe()` performs all device initialization and `catc_disconnect()` releases resources.

## Control flow

Probe sets altsetting 1, validates bulk and interrupt endpoints, allocates `alloc_etherdev()`, initializes locks/timer/URBs, detects the F5U011 by `bcdDevice`, and fills URBs for control, TX, RX, and interrupt traffic. Non-F5 devices run memory-size detection by writing and reading internal memory, configure TX/RX buffer counts, read MAC from SEEROM, copy MAC to station registers, initialize multicast SRAM, clear stats, and enable RX/TX merge modes. F5U011 devices reset, read MAC, and program a two-byte RX mode.

Opening submits the interrupt URB and starts the net queue; non-F5 devices also start the stats timer. Interrupt completions report link state and data availability. If data is available, the driver submits the RX URB unless one is already running; F5U011 increments `recq_sz` for extra packets. RX completion parses one or more length-prefixed frames on CATC hardware, or one full packet on F5U011, pushes SKBs to `netif_rx()`, updates stats, and resubmits if the F5 backlog says more packets are waiting. TX coalesces length-prefixed packets into alternating fixed buffers and submits a bulk URB, stopping the queue when the current burst is full or F5 has pending data.

## State and persistence

Runtime state is entirely in `struct catc`, including buffer rings, flags, timer state, queued control operations, stats baselines, and multicast hashes. Device nonvolatile state is only read through MAC/ROM paths; this driver does not persist configuration to disk. Non-F5 hardware stats are periodically read through async register operations and accumulated as deltas into `netdev->stats`.

## Dependencies and integration points

The driver integrates directly with USB core APIs (`usb_alloc_urb`, `usb_submit_urb`, `usb_control_msg`, endpoint checks), the netdev core, ethtool driver info/link reporting, CRC multicast hashing, timers, atomics, and spinlocks. Its link and packet flow bypass `usbnet`, so it must maintain queue stop/wake, carrier, URB cancellation, and stats itself.

## Risks

Key risks are fixed-size static buffers, asynchronous control queue overwrite when full, URB completion races during disconnect/stop, hardware-specific differences between CATC and F5U011 framing, and RX length trust. The code checks for oversized CATC packet lengths relative to URB length, but malformed multi-packet buffers can still produce packet loss. The control queue drops the oldest request on full queue, which can skip multicast/stat programming under heavy asynchronous updates.

## Test signals

Useful validation includes probe/remove for both CATC and F5U011 variants, altsetting failure handling, RX multi-frame bursts, F5 queued receive handling, TX timeout unlink recovery, multicast/promiscuous/allmulti programming, periodic stat accumulation, interrupt link up/down transitions, and teardown while RX/TX/control URBs are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/catc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc-phonet.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cdc-phonet.c

## Purpose

`cdc-phonet.c` implements a USB CDC Phonet host network interface for Nokia-style Phonet links. It creates an `ARPHRD_PHONET` point-to-point netdev rather than an Ethernet netdev, claims a paired CDC data interface, toggles data altsettings on open/close, and transfers Phonet packets over bulk endpoints.

## Important APIs, types, and functions

`struct usbpn_dev` stores the netdev, control and data interfaces, USB device, TX/RX pipes, active altsetting, disconnect flag, TX queue count, locks, an in-progress fragmented RX SKB, and a flexible array of RX URBs. `usbpn_setup()` configures the netdev type, header ops, MTU bounds, one-byte media address, queue length, and free-on-unregister behavior. Netdev ops are `usbpn_open()`, `usbpn_close()`, `usbpn_xmit()`, and `usbpn_siocdevprivate()`.

USB lifecycle is handled by `usbpn_probe()` and `usbpn_disconnect()`. RX/TX URB completions are `rx_complete()` and `tx_complete()`, with `rx_submit()` allocating page-backed receive buffers.

## Control flow

Probe parses CDC descriptors from the control interface with `cdc_parse_cdc_header()`, requiring both a union descriptor and Phonet magic. It finds the data interface from the union slave interface, verifies exactly two altsettings with one inactive and one active endpoint pair, allocates a netdev sized for `rxq_size` URB pointers, chooses RX/TX bulk pipes by endpoint direction, claims the data interface, forces inactive mode, and registers the netdev.

Opening switches the data interface to the active altsetting, allocates and submits 17 RX URBs using full pages, and wakes the TX queue. TX allocates one URB per SKB, rejects non-Phonet protocols, submits bulk output with `URB_ZERO_PACKET`, increments an internal queue count, and stops the queue at `tx_queue_len`. TX completion updates packet/error counters, decrements the queue count, wakes the queue, frees the SKB, and frees the URB. RX completion chains full-page fragments into `pnd->rx_skb` until a short transfer marks the last fragment, then strips the one-byte media header, sets Phonet protocol, updates stats, and delivers via `netif_rx()`.

## State and persistence

The only persistent runtime state is in `struct usbpn_dev`, including claimed interfaces, active altsetting, active URBs, TX queue depth, and a partially assembled RX SKB. There is no hardware nonvolatile programming or filesystem persistence.

## Dependencies and integration points

The driver depends on USB CDC descriptor parsing, Phonet header operations, Phonet ioctl constants, netdev registration, page-backed SKB fragments, spinlocks, and USB interface claiming/releasing. It shares the USB driver across both the control and claimed data interfaces.

## Risks

Risk centers on fragmented RX assembly and disconnect ordering. A stream of full-page URBs can accumulate fragments until `MAX_SKB_FRAGS`; overflow drops the assembled SKB and increments length errors. `usbpn_disconnect()` assumes `usb_get_intfdata()` is valid and uses a `disconnected` flag to handle double callbacks from the two claimed interfaces. TX queues can stall if URB completion is lost, but normal completion always wakes the queue.

## Test signals

Important tests include CDC descriptor rejection paths, alternate data-interface layouts, open/close altsetting toggles, fragmented RX across multiple pages, short-packet finalization, non-Phonet TX drop behavior, queue stop/wake under multiple TX URBs, private Phonet autoconf ioctl, and disconnect through either control or data interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc-phonet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_eem.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_eem.c

## Purpose

`cdc_eem.c` implements the USB CDC Ethernet Emulation Model. It is a `usbnet` minidriver that discovers endpoints, wraps outgoing Ethernet frames in EEM headers plus Ethernet FCS, parses bundled EEM data and command packets on receive, and responds to mandatory EEM echo commands.

## Important APIs, types, and functions

`eem_bind()` calls `usbnet_get_endpoints()` and adjusts `hard_header_len` and `hard_mtu` for EEM header, FCS, and VLAN header allowance. `eem_tx_fixup()` adds the EEM data header, computes CRC32, appends FCS, and adds an optional zero-length EEM packet to avoid ambiguous full-size USB transfers. `eem_rx_fixup()` loops through all EEM packets in an URB, handling command and data packet types. `eem_linkcmd()` submits asynchronous command responses, with completion handled by `eem_linkcmd_complete()`.

The `eem_info` `driver_info` advertises `FLAG_ETHER | FLAG_POINTTOPOINT` and supplies bind/RX/TX fixups. USB matching is the CDC EEM interface class/subclass/protocol tuple.

## Control flow

Probe, disconnect, suspend, and resume are delegated to `usbnet`. During TX, the driver ensures enough headroom and tailroom, copies if needed, appends calculated Ethernet CRC, prepends a two-byte data header with the CRC-present bit, and optionally appends a zero-length EEM packet when the transfer would otherwise end exactly on a USB maxpacket boundary.

RX processes the input SKB as a bundle. It reads each two-byte EEM header, branches on command versus data, validates lengths, and either consumes command payloads or extracts Ethernet frames. Echo commands are cloned, converted to echo responses, and submitted on the bulk OUT pipe. Suspend/response hints are ignored or passed to `usbnet_device_suggests_idle()`. Data payloads are CRC-validated against either calculated CRC or the EEM no-CRC sentinel `0xdeadbeef`; non-final frames are cloned and returned with `usbnet_skb_return()`, while the final frame is left in the original SKB for `usbnet`.

## State and persistence

The driver keeps no private per-device state beyond `usbnet` fields. Its only transient state is per-SKB framing and short-lived URBs used for EEM link-command replies. There is no persistent hardware or filesystem state.

## Dependencies and integration points

It depends on `usbnet`, USB CDC constants, Ethernet/VLAN sizes, CRC32 helpers, SKB head/tail manipulation, unaligned endian accessors, and runtime PM hinting through `usbnet_device_suggests_idle()`.

## Risks

Main risks are malformed bundled frames, CRC handling, and command echo response allocation from atomic context. The parser returns failure on incomplete headers or bogus lengths, which may be counted as RX errors by `usbnet` even when the final item was a command or zero-length packet. TX deliberately avoids bundling, so performance is simpler but may be lower than devices that benefit from large bundles.

## Test signals

Test with single and multiple EEM frames per URB, command-only bundles, mandatory echo request/response, suspend hints, CRC-present and no-CRC data modes, full-maxpacket TX padding behavior, VLAN-sized frames, short/bogus headers, and suspend/resume through `usbnet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_eem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ether.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ether.c

## Purpose

`cdc_ether.c` is the generic USB CDC Ethernet/ECM binding driver and a shared helper provider for other USB networking drivers. It parses CDC descriptors, claims paired data interfaces, initializes endpoints and packet filters, handles CDC notifications, exposes common bind/unbind/status symbols, and carries a large device ID table with blacklist and WWAN/ZTE quirks.

## Important APIs, types, and functions

Exported helpers include `usbnet_cdc_update_filter()`, `usbnet_generic_cdc_bind()`, `usbnet_ether_cdc_bind()`, `usbnet_cdc_unbind()`, `usbnet_cdc_status()`, `usbnet_cdc_bind()`, and `usbnet_cdc_zte_rx_fixup()`. The functions use `struct cdc_state` stored in `dev->data` to track control/data interfaces and CDC descriptors. `cdc_ether_ethtool_ops` overrides internal link-ksettings behavior. `cdc_info`, `zte_cdc_info`, and `wwan_info` define generic ECM, ZTE workaround, and mobile broadband variants.

## Control flow

Generic bind starts from the probed control interface and looks for CDC descriptors in interface extra data, configuration extra data, or endpoint extra data to tolerate firmware layout bugs. It detects RNDIS-like interfaces when that support is enabled, parses descriptors, validates union/control/data relationships, accepts known RNDIS fallbacks, handles merged control/data interfaces, validates class codes, checks MBM GUID and MDLM detail lengths, claims the data interface, collects endpoints, validates optional notification endpoint, requires RNDIS status endpoint when applicable, and installs CDC ethtool ops.

`usbnet_ether_cdc_bind()` then initializes the device packet filter to directed plus broadcast, plus promiscuous/all-multicast when requested. `usbnet_cdc_bind()` additionally reads the Ethernet MAC string descriptor. Unbind releases the paired interface from either side. CDC notifications update carrier on `NETWORK_CONNECTION` and TX/RX speeds on `SPEED_CHANGE`, including split notification payload handling via `EVENT_STS_SPLIT`. ZTE variants randomize locally administered MACs, rewrite bogus destination MACs on RX, and force off/on carrier transitions for duplicate carrier-on notifications.

## State and persistence

State is kept in `dev->data` as `struct cdc_state`, in `dev->status`, in carrier/speed fields, and in netdev filter flags. There is no filesystem persistence. The driver can program the device packet filter through a class control request but does not store hardware configuration across binds.

## Dependencies and integration points

It depends on `usbnet`, USB CDC parsing helpers, USB interface claiming, netdev multicast flags, ethtool, optional RNDIS-host classification, and many other USB net drivers through exported symbols. Its ID table intentionally blacklists devices handled by `qmi_wwan`, Realtek, Aquantia, Zaurus-specific drivers, and other specialized drivers.

## Risks

Descriptor parsing has many compatibility branches; regressions can misbind devices or steal interfaces from more specific drivers. The product table order is critical because blacklist entries with `driver_info = 0` must precede generic whitelist matches. Packet filter programming ignores control errors, trading robustness for compatibility. ZTE MAC and carrier workarounds are device-specific and could be wrong for newly added IDs.

## Test signals

Test descriptor locations, union-less RNDIS fallback, merged control/data interfaces, paired-interface release from either disconnect path, CDC notification split handling, packet filter updates for promisc/allmulti, MAC descriptor failures, ZTE RX destination rewrite, product-table blacklists, and coexistence with `qmi_wwan`, `r8152`, `aqc111`, RNDIS, and MBIM/NCM drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ether.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_mbim.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_mbim.c

## Purpose

`cdc_mbim.c` implements CDC MBIM networking on top of CDC NCM framing. It binds MBIM or dual NCM/MBIM functions, registers a `cdc-wdm` MBIM control subdriver, maps VLAN IDs to MBIM IPS/DSS sessions, strips/adds synthetic Ethernet headers around raw IP/DSS datagrams, and coordinates power management between `usbnet` and the WDM control function.

## Important APIs, types, and functions

`struct cdc_mbim_state` overlays `dev->data` and must match `cdc_ncm` expectations: it begins with `struct cdc_ncm_ctx *ctx`, followed by PM counter, subdriver pointer, and flags. `FLAG_IPS0_VLAN` controls whether MBIM IP session 0 is untagged or mapped to VLAN 4094. Netdev ops add VLAN callbacks around the usual `usbnet` methods. Core functions are `cdc_mbim_bind()`, `cdc_mbim_unbind()`, `cdc_mbim_manage_power()`, `cdc_mbim_tx_fixup()`, `cdc_mbim_rx_fixup()`, `cdc_mbim_process_dgram()`, `cdc_mbim_suspend()`, and `cdc_mbim_resume()`.

## Control flow

Bind optionally switches the communication interface to MBIM altsetting, rejects non-MBIM current altsettings, calls `cdc_ncm_bind_common()` with MBIM data altsetting and quirk flags, registers a WDM subdriver on the control interface using the MBIM descriptor's max control message size, disables `usbnet` use of the interrupt endpoint, marks the netdev `IFF_NOARP`, enables VLAN TX/filter features, and installs MBIM netdev ops. Unbind disconnects the WDM subdriver first, then delegates cleanup to NCM.

TX validates packet type, extracts VLAN TCI from accelerated metadata or an inline VLAN header, strips Ethernet/VLAN headers, enforces IP versus DSS session rules, maps VLAN 0-255 to IPS signatures and 256-511 to DSS signatures, optionally maps VLAN 4094 to IPS0, and calls `cdc_ncm_fill_tx_frame()` under the NCM context lock. RX verifies NCM NTB/NDP16 structures, accepts MBIM IPS and DSS signatures, maps signature session byte to VLAN TCI, converts each datagram into a synthetic Ethernet SKB, tags VLAN where needed, and returns SKBs to `usbnet`. IPv6 neighbor solicitations may be answered manually because MBIM netdevs are `NOARP`.

## State and persistence

Persistent runtime state includes the NCM context, WDM subdriver pointer, atomic PM reference count, session-zero VLAN flag, VLAN registrations, and NCM stats. There is no disk persistence. MBIM session mapping is represented through VLAN devices and ephemeral SKB tags.

## Dependencies and integration points

This file depends directly on exported `cdc_ncm` helpers and structures, `cdc-wdm`, USB CDC MBIM descriptors, VLAN acceleration APIs, IPv4/IPv6 header parsing, IPv6 neighbor discovery, USB autosuspend, and `usbnet`. It is selected ahead of NCM for MBIM altsettings based on `cdc_ncm_select_altsetting()` and the `prefer_mbim` policy in `cdc_ncm`.

## Risks

Risks include the strict overlay layout between `cdc_mbim_state` and NCM state, VLAN/session mapping mistakes, unsupported VLAN ranges causing drops, PM reference imbalance between data and control interfaces, and malformed NTBs with bad NDP chains. The RX loop has a bounded NDP chain count to avoid infinite loops. Manual IPv6 neighbor advertisement is subtle because it must find the right VLAN device under RCU.

## Test signals

Test MBIM-preferred dual functions, WDM registration failure cleanup, suspend/resume ordering with active WDM users, VLAN add/remove for session 0 and sessions 1-511, unsupported VLAN drop logs, raw IPv4/IPv6 RX conversion, DSS session traffic, IPv6 neighbor solicitation response, Huawei NDP-to-end quirk, ZLP behavior, and Telit altsetting-toggle avoidance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_mbim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ncm.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ncm.c

## Purpose

`cdc_ncm.c` is the CDC Network Control Model host driver and the shared NCM framing engine used by MBIM. It negotiates NCM/MBIM descriptors, data altsettings, NTB parameters, 16-bit or 32-bit NTB formats, RX/TX maximums, datagram sizes, alignment rules, coalescing timers, sysfs tuning knobs, ethtool stats, notification handling, and multi-packet RX/TX framing.

## Important APIs, types, and functions

The main state is `struct cdc_ncm_ctx` from the CDC NCM header, stored in `dev->data[0]`. This file exports `cdc_ncm_change_mtu()`, `cdc_ncm_bind_common()`, `cdc_ncm_unbind()`, `cdc_ncm_select_altsetting()`, `cdc_ncm_fill_tx_frame()`, `cdc_ncm_tx_fixup()`, RX verifier helpers for NTH/NDP16/NTH/NDP32, and `cdc_ncm_rx_fixup()`. It defines sysfs attributes under `cdc_ncm`, ethtool stats for NTB reasons/overhead/counts, and `driver_info` variants for generic NCM, ZLP devices, Apple tethering/private modes, and WWAN/no-ARP devices.

## Control flow

Bind allocates the context, initializes the hrtimer/tasklet/lock, parses CDC descriptors, locates the data interface via union or IAD fallback, validates NCM/ECM or MBIM descriptors, claims the data interface, sets or avoids data altsetting toggles based on quirk flags, issues `GET_NTB_PARAMETERS`, optionally disables CRC mode, selects NTB16 or NTB32, initializes TX/RX limits and alignment values, waits briefly for firmware, activates the data altsetting, discovers endpoints on data/control interfaces, reads the MAC address when available, performs NCM setup, allocates delayed NDP storage for NDP-to-end devices, installs ethtool/sysfs/netdev ops, and sets max MTU.

TX uses `cdc_ncm_tx_fixup()` and `cdc_ncm_fill_tx_frame()` to coalesce Ethernet datagrams into an NTB until the NTB is full, the NDP is full, max datagrams are reached, a timer expires, or an explicit flush occurs. It builds NTH16/NTH32 headers, chains or delays NDPs, aligns payloads, handles low-memory fallback by shrinking NTB allocation, pads or forces short packets, updates private overhead counters, and adjusts usbnet TX stats to count payload bytes. A high-resolution timer schedules a tasklet that flushes pending frames through `usbnet_start_xmit(NULL, dev->net)`.

RX verifies the NTH signature, block length, and sequence number, verifies NDP size and bounds, checks NDP signatures, iterates datagram entries until the first null entry, validates offset/length against the SKB and `rx_max`, copies each Ethernet frame into a fresh SKB, and returns it. CDC notifications update carrier and speed, including split speed-change data. `cdc_ncm_update_filter()` delegates CDC packet filter programming only if the device advertises filtering support.

## State and persistence

Runtime state includes negotiated NCM parameters, RX/TX max sizes, max datagram size, NDP format, TX coalescing SKBs, delayed NDP buffers, timer state, stop flag, sequence counters, stats, quirk flags, and sysfs-configurable values. No disk persistence exists. Device state is programmed through CDC class requests for NTB input size, NTB format, CRC mode, and max datagram size.

## Dependencies and integration points

The driver depends on `usbnet`, USB CDC descriptors and class requests, hrtimers, tasklets, ethtool, sysfs groups, MII/link helpers, CRC/ethernet helpers, and exported `usbnet_cdc_update_filter()` from `cdc_ether.c`. `cdc_mbim.c` depends on its exported bind/framing/RX verification helpers.

## Risks

High-risk areas are descriptor compatibility, NTB bounds verification, NDP chaining, low-memory TX fallback, timer/tasklet flushing races, and sysfs changes while the netdev is running. The code uses locks around TX context mutation and cancels timer/tasklet on unbind. Product matching order matters because MBIM-compatible NCM functions may be rejected here so `cdc_mbim` can bind when preferred.

## Test signals

Test NTB16 and NTB32 devices, generic and ZLP variants, Apple interfaces, WWAN/no-ARP IDs, MBIM preference rejection, descriptor fallback through IAD, RX malformed NTH/NDP cases, multi-NDP chains, TX coalescing timeout/full/max-datagram reasons, sysfs changes to `rx_max`, `tx_max`, `tx_timer_usecs`, `ndp_to_end`, MTU changes, suspend/resume, and CDC notification speed/carrier handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ncm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_subset.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_subset.c

## Purpose

`cdc_subset.c` supports very simple USB networking links that use a minimal subset of CDC Ethernet behavior: bulk Ethernet frames with no class-specific runtime control, no extra framing, and generally point-to-point semantics. It exists for legacy host-to-host cables, embedded/PDA firmware, and bootloader/device modes selected by Kconfig options.

## Important APIs, types, and functions

Most logic is declarative `struct driver_info` and `usb_device_id` data behind `CONFIG_USB_*` feature blocks. Optional helpers include `always_connected()` for PDA-style devices and `m5632_recover()` for ALi M5632 reset recovery. Driver info variants describe ALi M5632, AnchorChips/Cypress AN2720, Belkin/eTEK, Epson, KC2190, Linux PDA/gadget, Yopy, and blob bootloader devices. The USB driver delegates probe/disconnect/suspend/resume to `usbnet`.

## Control flow

At module load, only device entries enabled by Kconfig are compiled into the `products` table. `usbnet_probe()` uses the matched `driver_info` to select endpoint numbers, flags, optional `check_connect`, and optional recovery behavior. Runtime packet flow is generic `usbnet` Ethernet transfer without RX/TX fixups. The dummy pre/post reset callbacks always return success and avoid special reset handling in this driver.

## State and persistence

The file has no private per-device state. Runtime state is held by `usbnet`; configuration is compile-time through Kconfig and the USB ID table. No hardware nonvolatile settings or filesystem state are written.

## Dependencies and integration points

It depends on `usbnet`, USB device matching, Kconfig-selected hardware support, netdev/ethernet helpers, and USB suspend/resume. It integrates with the older Linux USB gadget ecosystem and host-to-host cable devices by identifying vendor/product IDs and endpoint quirks.

## Risks

The main risks are accidental binding to devices that need richer protocol handling, endpoint assumptions for old hardware, and the lack of link/reset handshakes for unplug/replug scenarios. Product support is compile-time gated; a build with no hardware options emits a preprocessor warning. Some supported hardware explicitly does not interoperate with Windows framing or needs power-cycle recovery because vendor docs are unavailable.

## Test signals

Test each enabled Kconfig ID, endpoint override behavior, plain Ethernet frame TX/RX without fixups, suspend/resume, ALi recovery reset behavior, always-connected devices, reset callbacks, and coexistence with CDC Ethernet/RNDIS/gadget alternatives for devices exposing multiple configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cdc_subset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/ch9200.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/ch9200.c

## Purpose

`ch9200.c` is a `usbnet` minidriver for the QinHeng CH9200 USB Ethernet adapter. It implements vendor control register access, MII callbacks, link status handling, MAC initialization, RX/TX framing with a 64-byte transmit header and receive trailer metadata, and basic device setup.

## Important APIs, types, and functions

`control_read()` and `control_write()` wrap vendor USB control messages and handle buffer allocation. `ch9200_mdio_read()` and `ch9200_mdio_write()` map MII register accesses to 16-bit vendor register reads/writes. `ch9200_bind()` initializes endpoints, MII fields, FIFO/threshold/pause/flow-control registers, RX URB size, and MAC address. `ch9200_tx_fixup()` and `ch9200_rx_fixup()` implement device framing. `ch9200_status()` consumes interrupt status and `ch9200_link_reset()` refreshes MII media state.

## Control flow

Probe uses `usbnet_probe()` with the single `ch9200_info` entry for VID/PID `1a86:e092`. Bind discovers endpoints, sets MII masks and callbacks, initializes `hard_mtu` and a fixed receive URB size, restarts autonegotiation, writes a sequence of MAC registers including an undocumented register 254, reads the MAC station registers in reverse byte order, and installs it on the netdev.

TX ensures 64 bytes of headroom, prepends two repeated length/control blocks in the header, clears reserved bytes, and increments the reported length if the transfer would be a USB maxpacket multiple. RX requires at least 64 bytes of overhead, reads packet length from 16 bytes before the end of the SKB, trims to that length, and lets `usbnet` process the frame. Interrupt status uses bit 0 of the first byte as carrier and schedules link reset when link comes up.

## State and persistence

There is no private allocation beyond `usbnet`; state is in hardware registers, `dev->mii`, `dev->rx_urb_size`, and netdev carrier. MAC address is read from device registers and not persisted by the driver.

## Dependencies and integration points

The driver depends on `usbnet`, USB vendor control requests, MII helpers, ethtool command helpers through `mii`, and standard Ethernet/netdev facilities. It uses `FLAG_ETHER` and delegates generic open/stop/TX scheduling to `usbnet`.

## Risks

Risks include weak error propagation in `control_write()` because it returns 0 after `usb_control_msg()` unless buffer allocation failed, minimal RX trailer validation, fixed undocumented setup constants, and no custom multicast programming. The RX path trusts the trailer length after only a tiny-frame check, so malformed device data can produce trimmed garbage frames.

## Test signals

Test probe/setup register writes, MAC byte order, MII read/write through ethtool, link interrupt transitions, TX full-maxpacket padding, RX tiny-frame rejection and trailer length trimming, suspend/resume through generic `usbnet`, and behavior under vendor control transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/ch9200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cx82310_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/cx82310_eth.c

## Purpose

`cx82310_eth.c` supports the USB Ethernet port of Conexant CX82310-based ADSL routers. It uses `usbnet` for generic networking but implements the router command protocol, firmware-ready polling, Ethernet-mode enablement, MAC readout, unusual RX packet reassembly, and a simple two-byte TX length header.

## Important APIs, types, and functions

`enum cx82310_cmd` and `enum cx82310_status` define the command channel. `struct cx82310_priv` stores a re-enable work item and `usbnet` pointer. `cx82310_cmd()` sends fixed 64-byte command packets over endpoint 1 and optionally waits for validated replies. `cx82310_bind()` handles product filtering, endpoint discovery, firmware wait, Ethernet mode, MAC read, partial buffer allocation, and work initialization. `cx82310_rx_fixup()` and `cx82310_tx_fixup()` implement framing, and `cx82310_reenable_work()` re-enters Ethernet mode after router reboot notifications.

## Control flow

Bind first rejects likely ADSL modem functions by checking that the USB product string is exactly `USB NET CARD`. It gets endpoints, sets `hard_header_len` to zero because partial RX continuations may lack Ethernet headers, sizes `hard_mtu` for 1514 bytes plus a two-byte TX header, sets 4 KiB receive URBs, allocates `dev->partial_data`, allocates private work state, polls `CMD_GET_LINK_STATUS` for up to about 25 seconds until firmware is ready, enables Ethernet mode, reads the MAC, sends `CMD_START`, and returns to `usbnet`.

RX handles a stream where each packet normally starts with a little-endian length, odd lengths are padded, and the last packet can be split across URBs without a header. If `partial_rem` is set, the next SKB prefix completes the previous packet. The special length `0xffff` indicates router reboot and schedules re-enable work. Complete non-final packets are copied into new SKBs and returned, while the final packet is left for `usbnet`. TX prepends a two-byte little-endian payload length.

## State and persistence

Runtime state includes the allocated partial packet buffer in `dev->partial_data`, `dev->partial_len` and `dev->partial_rem` aliases in `usbnet` data storage, and private delayed work. No filesystem or nonvolatile device state is written.

## Dependencies and integration points

It depends on `usbnet`, USB bulk command transfers, workqueues, netdev/Ethernet helpers, and endpoint matching through a custom USB ID macro matching device class/subclass/protocol.

## Risks

The most important risk is RX reassembly across URBs: incorrect `partial_rem` handling can desynchronize the stream. Command communication uses endpoint 1 directly and retries only empty replies, so firmware timing affects probe. Product-string filtering may reject localized or variant devices. Router reboot handling is asynchronous and can race with disconnect unless work is cancelled, which unbind does.

## Test signals

Test firmware-ready timeout, product-string rejection, MAC command failure cleanup, split RX packet reassembly, odd-length padding, `0xffff` reboot notification and work cancellation on unbind, oversized RX length rejection, TX header generation, and disconnect during pending re-enable work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/cx82310_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/dm9601.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/dm9601.c

## Purpose

`dm9601.c` is a `usbnet` minidriver for Davicom DM9601/DM9620/DM9621-family USB 10/100 Ethernet devices and compatible low-cost adapters. It implements vendor register access, shared EEPROM/PHY word operations, MII/ethtool integration, multicast hash programming, MAC address programming, chip-mode setup, RX/TX framing, and interrupt link status.

## Important APIs, types, and functions

Low-level helpers are `dm_read()`, `dm_read_reg()`, `dm_write()`, `dm_write_reg()`, and async write variants. `dm_read_shared_word()` and `dm_write_shared_word()` serialize EEPROM/PHY operations through `dev->phy_mutex` and poll `DM_SHARED_CTRL`. Ettool support includes EEPROM readout and MII link settings. Netdev hooks in `dm9601_netdev_ops` override multicast and MAC address behavior. Core `usbnet` hooks are `dm9601_bind()`, `dm9601_rx_fixup()`, `dm9601_tx_fixup()`, `dm9601_status()`, and `dm9601_link_reset()`.

## Control flow

Bind discovers endpoints, installs ops, increases hard header length for the two-byte TX header, sets RX URB size for status/length/CRC overhead plus DM9620 padding, initializes MII callbacks, resets the chip, reads the MAC, writes a generated MAC back if EEPROM is invalid, reads chip ID, switches DM9620-like devices into DM9601 mode, powers up the PHY, initializes multicast reception, resets and advertises the PHY, and starts autonegotiation.

RX expects a three-byte prefix containing status and length including CRC, followed by Ethernet data and four CRC bytes. It rejects tiny frames, maps status bits to netdev RX error counters, strips the prefix, trims the CRC, and returns success. TX adds a two-byte little-endian payload length header and pads up to three bytes to avoid odd or maxpacket-aligned lengths that trigger DM962x FIFO errata. Interrupt status reads an eight-byte notification and toggles carrier based on bit `0x40`.

## State and persistence

Runtime state is mainly in hardware registers, MII state, netdev address/filter state, `dev->data` used as an eight-byte multicast filter scratch buffer, and link carrier. EEPROM contents are exposed read-only through ethtool; the driver writes MAC/filter/PHY registers but does not persist settings to disk.

## Dependencies and integration points

It depends on `usbnet`, MII helpers, ethtool EEPROM APIs, CRC multicast hashing, USB vendor requests, mutex-protected PHY access, and the generic `usbnet` open/stop/TX path. The product table covers many rebranded devices, including a ZyXEL DSL modem ID.

## Risks

Risks include shared PHY/EEPROM polling timeouts, invalid MAC fallback behavior, DM9620 mode quirks, TX padding required for FIFO errata, and RX length/status trust. Async multicast/MAC writes can fail silently. MII read errors return zero, which may hide hardware failures from callers.

## Test signals

Test DM9601 and DM9620 IDs, EEPROM read alignment, invalid EEPROM MAC fallback and writeback, multicast hash programming for promisc/allmulti/many multicast addresses, MDIO read/write timeouts, RX status error counters, TX odd/maxpacket padding, link interrupt transitions, and suspend/resume with link reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/dm9601.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/gl620a.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/gl620a.c

## Purpose

`gl620a.c` is a `usbnet` minidriver for GeneSys GL620USB-A host-to-host USB link cables. It supports the full-duplex GL620USB-A protocol, where one USB transfer can bundle multiple Ethernet packets with a simple little-endian packet-count and per-packet length framing.

## Important APIs, types, and functions

`struct gl_header` and `struct gl_packet` model the transfer framing. `genelink_bind()` sets the receive buffer size and adjusts hard-header length before calling `usbnet_get_endpoints()`. `genelink_rx_fixup()` unpacks bundled packets and returns individual SKBs. `genelink_tx_fixup()` wraps one outgoing Ethernet frame in the GeneLink count/length header and adds padding when needed. `genelink_info` sets `FLAG_POINTTOPOINT`, `FLAG_FRAMING_GL`, and `FLAG_NO_SETINT`, with fixed endpoint numbers `in = 1` and `out = 2`.

## Control flow

Probe is delegated to `usbnet_probe()` for VID/PID `05e3:0502`. Bind configures `hard_mtu` to `GL_RCV_BUF_SIZE`, allowing up to 32 maximum-length packets in one receive buffer, and accounts for the four-byte packet-count header. TX ensures eight bytes of headroom for count and single packet length, copies or repositions the SKB if needed, writes count `1` and original packet length in little-endian form, and appends one padding byte if the USB transfer would otherwise end on a maxpacket boundary. RX reads packet count, rejects counts above 32, iterates all but the last packet by allocating new SKBs and returning them, then leaves the final packet in the original SKB after pulling the length field.

## State and persistence

There is no private persistent state. All state is per-SKB framing and generic `usbnet` device state. The driver does not program nonvolatile hardware settings or write files.

## Dependencies and integration points

The driver depends on `usbnet`, Ethernet SKB allocation/copy helpers, endian conversion, and USB endpoint matching. It intentionally does not support the half-duplex GL620USB variant, whose direction handshake is only described in comments.

## Risks

The RX parser validates packet count and per-packet maximum size, but multi-packet pointer arithmetic is still sensitive to malformed length fields and truncated URBs. TX sends one frame per USB transfer despite the protocol supporting bundles, reducing complexity but limiting throughput. Half-duplex devices with similar IDs are excluded because the handshake is not implemented.

## Test signals

Test single and multi-packet receive buffers, invalid packet counts, oversized packet lengths, short/truncated GL headers, TX maxpacket padding, endpoint assumptions, suspend/resume through `usbnet`, and rejection/non-binding of unsupported half-duplex GL620USB devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/gl620a.c -->
