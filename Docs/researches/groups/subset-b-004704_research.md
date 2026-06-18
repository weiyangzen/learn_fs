# Research: subset-b-004704

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.c

## Purpose
`lan78xx.c` is the full Linux USB network driver for Microchip LAN7800, LAN7850, LAN7801, and the AT29M2-AF USB gigabit Ethernet devices. Unlike many files in this directory, it is not a thin `usbnet` minidriver: it owns `net_device` allocation, URB pools, NAPI polling, phylink/MDIO integration, interrupt-domain mapping, register access, EEPROM/OTP access, VLAN and multicast filters, checksum/TSO offloads, statistics, Wake-on-LAN, autosuspend, and reset/resume behavior.

## Important APIs, Types, And Functions
Core state is split between `struct lan78xx_net`, which is the netdev-private runtime object, and `struct lan78xx_priv`, which holds receive-filter state, multicast/perfect filter tables, VLAN table, deferred work items, and the configured WoL bitmap. `struct skb_data` is overlaid on `skb->cb` for every driver-owned URB buffer and tracks the URB, device, buffer state, payload length, and packet count. `struct statstage` tracks hardware statistic snapshots and rollover accounting, while `struct irq_domain_data` exposes the device interrupt endpoint as a small Linux IRQ domain, primarily for PHY interrupts.

USB register access is centralized through `lan78xx_read_reg()`, `lan78xx_write_reg()`, and `lan78xx_update_reg()`, using vendor control requests defined in `lan78xx.h`. EEPROM/OTP support is implemented by `lan78xx_read_raw_eeprom()`, `lan78xx_write_raw_eeprom()`, `lan78xx_read_raw_otp()`, `lan78xx_write_raw_otp()`, and guarded wrappers that check Microchip magic indicators. `lan78xx_init_mac_address()` chooses a MAC address from current registers, Device Tree, EEPROM, OTP, or a random fallback and mirrors it into perfect filter slot 0.

The PHY side is handled through `lan78xx_mdio_init()`, `lan78xx_mdiobus_read()`, `lan78xx_mdiobus_write()`, `lan78xx_setup_irq_domain()`, and the phylink sequence `lan78xx_get_phy()`, `lan78xx_phylink_setup()`, `lan78xx_mac_prepare_for_phy()`, `lan78xx_phy_init()`, and `lan78xx_phy_uninit()`. LAN7800 and LAN7850 use an internal GMII PHY; LAN7801 uses RGMII and can fall back to a fixed 1 Gbps full-duplex link for switch-board designs without a visible PHY.

The data path is built around `lan78xx_start_xmit()`, `lan78xx_tx_bh()`, `lan78xx_tx_buf_fill()`, `tx_complete()`, `rx_submit()`, `rx_complete()`, `lan78xx_bh()`, and `lan78xx_poll()`. The driver preallocates pools of SKB-backed URBs by USB speed, batches outgoing packets into large bulk URBs with LAN78xx TX command words, and parses incoming URB buffers containing one or more RX command headers plus Ethernet frames. RX checksum and VLAN acceleration are handled by `lan78xx_rx_csum_offload()` and `lan78xx_rx_vlan_offload()`.

Public kernel integration points include `lan78xx_netdev_ops`, `lan78xx_ethtool_ops`, `lan78xx_phylink_mac_ops`, the `usb_driver` named `lan78xx`, `module_usb_driver()`, and the USB product table. Ettool exposes EEPROM access, register dumps, hardware stats, self-tests, WoL, EEE, pause parameters, link settings, and timestamp info.

## Control Flow
Probe starts in `lan78xx_probe()`: allocate an Ethernet netdev, initialize queues, locks, NAPI, delayed work, timer, URB pools, endpoint pipes, then call `lan78xx_bind()`. Binding allocates private state, initializes filters and VLAN table, advertises netdev offload features, creates the IRQ domain, performs `lan78xx_reset()`, registers the MDIO bus, and enables multicast support. Probe then allocates the interrupt URB, records packet size, enables remote wake, initializes phylink/PHY, registers the netdev, stores interface data, enables wakeup, and sets the autosuspend delay.

Open runs `lan78xx_open()`: it takes runtime PM, locks `dev_mutex`, initializes stats, enables NAPI, marks `EVENT_DEV_OPEN`, submits the interrupt URB, and starts phylink. Actual MAC TX/RX path enablement is driven by phylink `mac_link_up()`, which configures speed/duplex, flow control, USB U1/U2 settings, submits RX URBs, flushes FIFOs, starts TX/RX hardware paths, and starts the netdev queue. Link down stops the queue, disables TX/RX paths, and resets the MAC.

Transmit is two-stage. `ndo_start_xmit` timestamps and appends the stack SKB to `txq_pend`, then schedules NAPI. `lan78xx_tx_bh()` wakes or stops the stack queue based on pending bytes versus free URB space, fills free TX buffers from pending SKBs, applies checksum/TSO/VLAN command words, submits bulk URBs, or anchors them during suspend. Completion updates stats, releases runtime PM, returns the URB buffer to `txq_free`, and reschedules NAPI if pending data remains.

Receive starts by filling free RX URBs through `lan78xx_rx_urb_submit_all()`. `rx_complete()` records status, moves the URB buffer from `rxq` to `rxq_done`, and schedules NAPI. `lan78xx_bh()` drains overflow frames, snapshots completed RX buffers, parses each buffer via `lan78xx_rx()`, returns valid frames through GRO, resubmits RX URBs, and then services TX. Budget overflow is preserved in `rxq_overflow` so a partially processed URB does not drop frames merely because NAPI budget expired.

Deferred work in `lan78xx_delayedwork()` handles TX/RX halt recovery, PHY interrupt acknowledgment, and exponential-backoff statistics updates. The interrupt URB completion path calls `lan78xx_status()`, which only treats PHY interrupt bits as expected, acks them in work context, and forwards them into the IRQ domain for phylib.

## State And Persistence Behavior
Volatile state lives in URB queues, NAPI, `flags` event bits, delayed work, the stat timer, and runtime PM references. Persistent device configuration is read from hardware registers, EEPROM, OTP, Device Tree MAC properties, optional PHY LED properties, and ethtool-written EEPROM/OTP contents. The driver writes MAC address registers, perfect filter slot 0, multicast hash/perfect filters, VLAN filter RAM, flow-control thresholds, USB LPM/LTM registers, PHY reset state, wake-frame filters, and suspend wake registers. Hardware statistics are 20-bit or 32-bit counters; the driver maintains software rollover state to expose stable 64-bit ethtool counters.

## Dependencies And Integration Points
The file depends on USB core, netdev, NAPI/GRO, phylink, phylib, MDIO, OF MDIO, irqdomain/irqchip, runtime PM, ethtool, VLAN helpers, checksum helpers, VXLAN feature checks, and `lan78xx.h` register definitions. It integrates with Linux networking through netdev ops and ethtool ops, with PHY drivers through MDIO/phylink, with platform firmware through Device Tree MAC and PHY LED properties, and with power management through autosuspend, system suspend, remote wake, and reset-resume callbacks.

## Risks And Edge Cases
Register access can race disconnect, so helpers return `-ENODEV` once `EVENT_DEV_DISCONNECT` is set. MAC reset is serialized against MDIO because the file documents possible MAC-interface lockups if reset occurs while MDIO is busy. EEPROM access temporarily disables LED muxing on LAN7800 and must restore `HW_CFG` even after timeout. TX unlinking holds an extra URB reference to avoid use-after-free races with completion handlers. RX parsing copies frames out of URB buffers; malformed command lengths, too-short frames, or hardware error bits increment error counters and drop. VLAN checksum handling deliberately disables hardware checksum trust when VLAN stripping is not active. Suspend refuses autosuspend while TX is pending, anchors deferred TX URBs when asleep, and has separate behavior for open versus closed interfaces. LAN7801 fixed-link fallback is intentionally special-case and may hide board configuration mistakes.

## Test Signals
Useful signals include successful `register_netdev()`, link up/down via phylink, interrupt URB resubmission, ethtool register/stat/EEPROM reads, NAPI RX/TX progress, no growth in `rx_errors`, `tx_errors`, `rx_over_errors`, or halt events, successful runtime autosuspend/resume and reset-resume, and WoL wake from magic, PHY, broadcast, multicast, unicast, or ARP according to configured `wolopts`. Hardware validation should cover SuperSpeed, High-Speed, and Full-Speed URB sizing, jumbo MTU rejection when it would force a zero-length packet read, TSO size limits, VLAN filter add/remove, multicast hash/perfect-filter transitions, EEE enable/disable, and LAN7801 RGMII/fixed-link behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.h

## Purpose
`lan78xx.h` is the hardware contract for the LAN78xx driver. It defines USB vendor request IDs, interrupt endpoint bits, TX/RX descriptor command fields, system control/status registers, MAC/PHY datapath registers, wake and offload registers, OTP register addresses, and masks used by `lan78xx.c`.

## Important APIs, Types, And Constants
The header has no functions and no exported types; its API is the named register and bitfield namespace. The top-level USB commands are `USB_VENDOR_REQUEST_WRITE_REGISTER`, `USB_VENDOR_REQUEST_READ_REGISTER`, and `USB_VENDOR_REQUEST_GET_STATS`. TX/RX packet metadata uses `TX_CMD_A_*`, `TX_CMD_B_*`, `RX_CMD_A_*`, `RX_CMD_B_*`, and `RX_CMD_C_*`, including checksum, TSO, VLAN insertion/removal, length, error, and wake indication fields.

Register groups include identity and reset (`ID_REV`, `HW_CFG`, `PMT_CTL`), GPIO and wake (`GPIO_CFG0`, `GPIO_CFG1`, `GPIO_WAKE`), dataport RAM selectors (`DP_SEL`, `DP_CMD`, `DP_ADDR`, `DP_DATA`), EEPROM (`E2P_CMD`, `E2P_DATA`), USB descriptors and link power management (`USB_CFG0`, `USB_CFG1`, `USB_CFG2`, `USB_CFG3`, `USB_STATUS`, `U1_LATENCY`, `U2_LATENCY`), interrupt endpoint control (`INT_STS`, `INT_EP_CTL`), receive filter engine (`RFE_CTL`, `VLAN_TYPE`, MAF and VLAN/hash RAM constants), FIFO control (`FCT_RX_CTL`, `FCT_TX_CTL`, `FCT_FLOW`), MAC control (`MAC_CR`, `MAC_RX`, `MAC_TX`, `FLOW`, `ERR_STS`), MII access (`MII_ACC`, `MII_DATA`), EEE timing, wake filters (`WUCSR`, `WUCSR2`, `WK_SRC`, `WUF_CFG`, `WUF_MASK*`), network offload registers, RGMII DLL tuning, and OTP programming/readback registers.

## Control Flow And Usage
`lan78xx.c` reads and writes these constants through the control-message register helpers. The TX path writes `TX_CMD_A/B` into outgoing URB buffers; the RX path parses `RX_CMD_A/B/C` from incoming buffers. Reset and probe use `ID_REV`, `HW_CFG`, `USB_CFG*`, FIFO, flow-control, RFE, MAC, and PMT definitions. MDIO access is encoded with `MII_ACC_*`. EEPROM and OTP helpers drive `E2P_*` and `OTP_*` bits. Suspend/WoL code programs `WUCSR`, `WUCSR2`, `WK_SRC`, `WUF_CFG`, and `WUF_MASK` fields.

## State And Persistence Behavior
The header itself has no state. It defines the persistent and volatile hardware state that the C file manipulates: EEPROM bytes, OTP bytes, MAC address registers, filter RAM, VLAN/hash tables, wake filters, PHY/MAC control bits, USB LPM settings, and counters. Mask correctness is critical because most operations are read-modify-write sequences.

## Dependencies And Integration Points
It depends on Linux bit macros being available before inclusion and is coupled tightly to Microchip LAN7800/LAN7850/LAN7801 register documentation. The file is included only by the LAN78xx implementation in this subset.

## Risks And Test Signals
Duplicated macro definitions appear for `GPIO_CFG1_GPIOD6_` and `PHY_DEV_ID_REV_SHIFT_`, which is harmless for identical values but a maintenance smell. Any incorrect mask width or shift can silently corrupt hardware configuration, so tests should exercise register dump paths, EEPROM/OTP read/write paths, TX/RX checksum and VLAN offloads, WoL filter programming, LPM/LTM setup, MDIO access, and MAC/PHY mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/lan78xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/lg-vl600.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/lg-vl600.c

## Purpose
`lg-vl600.c` is a `usbnet` minidriver for the Ethernet data interface of the LG VL600 LTE modem. The hardware presents a CDC Ethernet-like interface but requires a proprietary frame and packet header format that replaces the normal Ethernet header on USB. The driver binds through CDC helpers and translates between Linux Ethernet SKBs and the modem-specific encapsulation.

## Important APIs, Types, And Functions
`struct vl600_frame_hdr` describes the outer batch header: total length, serial, packet count, flags/dummy fields, and a magic value. `struct vl600_pkt_hdr` is the per-packet header and is intentionally the same size as `struct ethhdr`, with `h_proto` in the same offset. `struct vl600_state` stores `current_rx_buf`, allowing a modem batch to be assembled across multiple USB frames.

`vl600_bind()` allocates private state, delegates interface parsing to `usbnet_cdc_bind()`, marks the netdev `IFF_NOARP`, and enables multicast for IPv6 NDP. `vl600_unbind()` frees any partial RX buffer and calls `usbnet_cdc_unbind()`. `vl600_rx_fixup()` validates magic, assembles fragments, splits batches into packets, reconstructs Ethernet source/destination fields, fixes bogus inbound IPv6 ethertype, and returns either a final SKB to usbnet or additional cloned SKBs via `usbnet_skb_return()`. `vl600_tx_fixup()` adds frame and packet headers, pads to a 4-byte boundary, forces the protocol field to IPv4 as expected by the modem, and preserves or reallocates SKB head/tailroom as needed.

## Control Flow
`usbnet_probe()` matches the single USB product/interface descriptor and uses `vl600_info`. RX data enters `vl600_rx_fixup()` before usbnet delivers it to the stack. If a batch is incomplete, the driver copies the incoming frame into `current_rx_buf` with enough tailroom for the declared length and returns 0. When complete, it pulls the outer header, iterates `pkt_cnt`, clones intermediate packets, trims the last packet, and either returns 1 for the original SKB or explicitly returns an assembled partial buffer. TX takes normal Ethernet frames from usbnet, prepends the VL600 frame header, rewrites the in-place packet header fields, pads, and returns the encapsulated SKB.

## State And Persistence Behavior
The only persistent runtime state is the partial RX SKB. A static TX serial counter increments per transmitted modem frame. No nonvolatile device state is read or written. Netdev flags persist for the lifetime of the bound interface.

## Dependencies And Integration Points
The file depends on `usbnet`, CDC Ethernet binding helpers, Ethernet helpers, and normal USB driver registration. It integrates with usbnet through `.bind`, `.unbind`, `.status = usbnet_cdc_status`, `.rx_fixup`, and `.tx_fixup`, and marks `FLAG_RX_ASSEMBLE | FLAG_WWAN`.

## Risks And Test Signals
Risk centers on malformed proprietary lengths: bad magic, oversized fragments, short headers, packet lengths beyond the buffer, and clone allocation failures. The code deliberately accepts odd-length correct frames due to observed device behavior. ARP handling copies MAC addresses from ARP payloads, while non-ARP traffic fabricates addresses; IPv6 detection peeks at the L3 version nibble. Tests should cover fragmented RX batches, multiple packets per batch, IPv6 ethertype repair, ARP address reconstruction, short/malformed frames, TX headroom/tailroom reuse, and disconnect cleanup of `current_rx_buf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/lg-vl600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/mcs7830.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/mcs7830.c

## Purpose
`mcs7830.c` is a `usbnet` minidriver for Moschip MCS7730, MCS7830, MCS7832, and a Sitecom LN-030 variant. It configures the adapter through vendor HIF registers, exposes MII link controls, handles multicast filtering, strips/validates the chip's RX status byte, and reports link changes from interrupt status packets.

## Important APIs, Types, And Functions
`struct mcs7830_data` is stored in usbnet's private data area and keeps the 8-byte multicast hash plus a cached config byte. Vendor register I/O is performed by `mcs7830_get_reg()`, `mcs7830_set_reg()`, and `mcs7830_set_reg_async()`. MAC address helpers read/write `HIF_REG_ETHERNET_ADDR`; PHY helpers `mcs7830_read_phy()` and `mcs7830_write_phy()` serialize access with `dev->phy_mutex`, issue command registers, poll the ready bit, and exchange little-endian `HIF_REG_PHY_DATA`.

`mcs7830_set_autoneg()` programs the advertised MII capabilities and restarts autonegotiation. `mcs7830_get_rev()` probes whether register 22 is readable to distinguish rev C or newer, and `mcs7830_rev_C_fixup()` writes the pause threshold for those devices. `mcs7830_data_set_multicast()` calculates the multicast hash with Ethernet CRC bits and updates config flags for promiscuous/all-multicast behavior. `mcs7830_apply_base_config()` restores MAC, autoneg, filter, config, and rev-C fixup after bind or reset-resume.

## Control Flow
Probe is delegated to usbnet using `moschip_info` or `sitecom_info`. `mcs7830_bind()` retries reading the EEPROM MAC, stores it in the netdev, initializes filter/config state, applies base configuration, installs ethtool and netdev ops, reserves one extra RX byte for status, initializes usbnet MII callbacks, derives the PHY ID from the second MAC byte, and gets endpoints. On reset-resume, `mcs7830_reset_resume()` reapplies base configuration before calling `usbnet_resume()`.

RX packets carry a trailing status byte. `mcs7830_rx_fixup()` first rejects unexpectedly tiny frames, trims the status byte, reads it from the old final byte position, updates error counters for length, alignment, or CRC errors, and returns whether any payload remains. Link interrupt packets are handled by `mcs7830_status()`, which treats `buf[1] == 0x20` as link-down and calls `usbnet_link_change()` when carrier state changes.

## State And Persistence Behavior
Runtime state is the cached multicast filter/config in `dev->data`, usbnet MII state, and netdev MAC address. Persistent hardware state includes the adapter MAC register, PHY advertisement/BMCR, multicast hash, HIF config, and rev-C pause threshold. MAC address changes are rejected while the interface is running to avoid active hardware reconfiguration.

## Dependencies And Integration Points
The file depends on usbnet, ethtool, MII helpers, CRC32/Ethernet helpers, and USB vendor control messages. It integrates through custom `net_device_ops`, `ethtool_ops`, `driver_info` callbacks, usbnet suspend/resume, and USB product IDs.

## Risks And Test Signals
The PHY command polling loop is short and returns `-EIO` on readiness timeout. The multicast path intentionally sets `ALLMULTICAST` even when not strictly required because the device reportedly does not work otherwise. `mcs7830_get_regs()` can expose odd data lengths, as noted in the file TODO. Test signals include successful MAC read after retries, autoneg restart, link interrupt carrier transitions, RX status-byte stripping, error counter increments for each status bit, multicast hash programming, MAC set rejection while running, and reset-resume preserving ethtool register output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/mcs7830.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/net1080.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/net1080.c

## Purpose
`net1080.c` is a `usbnet` minidriver for NetChip 1080 USB host-to-host cables, including some LapLink devices. These are point-to-point USB links that carry Ethernet frames using NetChip-specific framing with a header, optional padding byte, and trailer packet ID to detect dropped USB packets.

## Important APIs, Types, And Functions
`struct nc_header` contains header length, packet length, and packet ID; optional out-of-band fields may follow the minimum header. `struct nc_trailer` repeats the packet ID. Register helpers `nc_vendor_read()`, `nc_register_read()`, `nc_vendor_write()`, and `nc_register_write()` access vendor registers such as USB control, TTL, and status. Debug helpers decode USB control and status bits.

`net1080_reset()` reads status and USB control, flushes both sides, reads TTL, writes a read TTL of 255 ms for this side, and reports peer connection state. `net1080_check_connect()` returns `-ENOLINK` if the peer is not connected. `nc_ensure_sync()` counts framing errors in `dev->data[1]` and asynchronously flushes both sides after repeated errors. `net1080_rx_fixup()` validates odd USB frame length, header length, framed-size limit, pad byte, payload length, and matching header/trailer packet IDs before exposing the Ethernet frame. `net1080_tx_fixup()` prepends the header, adds an optional pad byte to force odd transfer length, appends the trailer, and increments `dev->xid` for packet IDs.

## Control Flow
USB matching delegates probe to `usbnet_probe()` with `net1080_info`. `net1080_bind()` increases the netdev hard header length by the NetChip framing overhead, sizes RX URBs to hard header plus MTU, sets `hard_mtu` to the framing maximum, and asks usbnet to discover endpoints. Reset and check-connect are usbnet driver-info callbacks. TX and RX fixups translate frame formats around usbnet's normal transmit and receive paths.

## State And Persistence Behavior
Runtime state includes usbnet `xid` for packet IDs and `data[1]` as `frame_errors`. Hardware state touched by reset includes USBCTL flush bits and the TTL register. No EEPROM or nonvolatile state is managed here.

## Dependencies And Integration Points
The file depends on usbnet, USB vendor control messages, unaligned helpers, Ethernet/netdevice APIs, and MII/ethtool headers through the usbnet environment. It declares `FLAG_POINTTOPOINT | FLAG_FRAMING_NC` and supplies `.bind`, `.reset`, `.check_connect`, `.rx_fixup`, and `.tx_fixup`.

## Risks And Test Signals
This protocol is sensitive to exact framing. Even-length USB transfers, bad pad bytes, oversized packet lengths, short headers, payload-length mismatches, and packet-ID mismatches are treated as framing or FIFO errors. Repeated framing errors trigger a flush to regain synchronization. Tests should cover odd-length enforcement, pad insertion/removal, trailer ID validation, peer-disconnect `-ENOLINK`, reset TTL programming, and recovery after several malformed frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/net1080.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.c

## Purpose
`pegasus.c` is a standalone USB Ethernet driver for ADMtek Pegasus and Pegasus II adapters rather than a usbnet minidriver. It owns netdev allocation, endpoint validation, URB allocation/submission, RX tasklet retry, interrupt handling, MII/EEPROM access, device-specific reset/configuration, carrier polling, ethtool operations, Wake-on-LAN, suspend/resume, and a module parameter for adding an extra USB ID.

## Important APIs, Types, And Functions
The main runtime type is `pegasus_t` from `pegasus.h`, stored as netdev private data. The generated arrays `usb_dev_id[]` and `pegasus_ids[]` are built by macro-including `pegasus.h` device entries. Module parameters are `loopback`, `mii_mode`, `devid`, and `msg_level`.

Control-message helpers are `get_registers()`, `set_registers()`, and `set_register()`, with `update_eth_regs_async()` issuing asynchronous register updates for receive mode changes. PHY access is implemented by `__mii_op()`, `read_mii_word()`, `write_mii_word()`, `mdio_read()`, and `mdio_write()`. EEPROM reads use `read_eprom_word()` and `get_node_id()`; optional EEPROM writes are compiled out unless `PEGASUS_WRITE_EEPROM` is enabled.

Device setup functions include `set_ethernet_addr()`, `reset_mac()`, `enable_net_traffic()`, `setup_pegasus_II()`, `mii_phy_probe()`, and `get_interrupt_interval()`. Data path functions include `read_bulk_callback()`, `rx_fixup()` tasklet retry, `write_bulk_callback()`, `intr_callback()`, and `pegasus_start_xmit()`. Netdev lifecycle is `pegasus_open()`, `pegasus_close()`, `pegasus_probe()`, and `pegasus_disconnect()`.

## Control Flow
Module init optionally parses `devid` and registers `pegasus_driver`. Probe rejects a known Belkin Bluetooth ID collision, verifies fixed endpoint addresses 1-in, 2-out, 3-interrupt-in, allocates an Ethernet netdev, allocates URBs, initializes a RX tasklet and carrier delayed work, installs netdev and ethtool ops, reads interrupt interval from EEPROM, resets the MAC, sets the Ethernet address from registers or EEPROM, applies Pegasus II quirks, probes MII PHY, disables WoL, registers the netdev, and starts delayed carrier polling.

Open allocates an RX SKB, writes the current MAC to hardware, submits RX and interrupt URBs, enables MAC traffic based on MII link partner advertisement, updates carrier, and starts the TX queue. TX prepends a 16-bit length in a fixed `tx_buff`, chooses a transfer count that avoids an exact 64-byte multiple, submits the bulk OUT URB, and frees the stack SKB. RX completion validates transfer status, decodes chip-specific packet length/status trailers, updates counters, passes valid packets to `netif_rx()`, allocates the next RX SKB, and resubmits. If allocation or submission fails, the tasklet retries.

Interrupt completion updates TX error counters from status bytes, accumulates missed RX packets, and resubmits the interrupt URB. Carrier polling reads `MII_BMSR` every two seconds and sets carrier. Suspend detaches, cancels carrier polling, and kills RX/interrupt URBs when running; resume reattaches, reuses completion handlers to resubmit URBs, and restarts carrier polling.

## State And Persistence Behavior
Runtime state includes URB pointers, a current RX SKB, a fixed TX buffer, cached Ethernet control registers, MII configuration, feature flags from the device table, detected chip type, PHY ID, WOL options, carrier work, and flags such as `PEGASUS_UNPLUG` and `PEGASUS_RX_URB_FAIL`. Persistent state is limited to EEPROM-derived MAC and interrupt interval; optional EEPROM writing is present but disabled. The dynamic `devid` parameter mutates the sentinel slots of the runtime ID arrays before USB registration.

## Dependencies And Integration Points
The file depends on USB core, netdevice, ethtool, MII helpers, tasklets, delayed work, module parameters, and `pegasus.h`. It integrates directly with the kernel network stack through `pegasus_netdev_ops`, with ethtool through `ops`, and with USB through `pegasus_driver`.

## Risks And Test Signals
Risk areas include fixed endpoint assumptions, device-table index coupling between `pegasus_ids[]` and `usb_dev_id[]`, legacy private ioctls, static TX buffer serialization, tasklet retry loops under low memory, limited stall recovery, and many vendor-specific GPIO/MII quirks. The RX callback manually adjusts `rx_skb->data` for chip `0x8513`, so length handling needs coverage. Tests should verify endpoint rejection, Belkin Bluetooth blacklist, MAC fallback to random address, MII probing, Pegasus II setup, RX length/status parsing, interrupt error counters, TX timeout unlinking, WoL set/get, suspend/resume resubmission, and `devid` parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.h -->
# sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.h

## Purpose
`pegasus.h` provides both the hardware constants and the USB device table source for the Pegasus driver. It is designed for double inclusion: normally it defines feature flags, register IDs, the `pegasus_t` runtime structure, vendor IDs, and `struct usb_eth_dev`; when `PEGASUS_DEV` is defined, it expands a long list of supported products.

## Important APIs, Types, And Constants
Feature flags include `PEGASUS_II` and `HAS_HOME_PNA`, plus GPIO reset defaults and driver state bits such as `PEGASUS_UNPLUG` and `PEGASUS_RX_URB_FAIL`. Register definitions cover Ethernet control (`EthCtrl0..2`, `EthID`), EEPROM (`EpromOffset`, `EpromData`, `EpromCtrl`), PHY (`PhyAddr`, `PhyData`, `PhyCtrl`), USB/status (`UsbStst`, TX/RX status), wakeup, GPIO, and Pegasus II-specific registers. USB control request constants are `PEGASUS_REQ_GET_REGS`, `PEGASUS_REQ_SET_REGS`, and their request types.

`typedef struct pegasus` is the central state object used by `pegasus.c`: it carries USB/netdev pointers, MII info, feature and runtime flags, message level, WoL options, device table index, interrupt interval, tasklet/work items, RX/TX/interrupt URBs, RX SKB, fixed TX buffer, cached Ethernet registers, PHY ID, and GPIO reset value. `struct usb_eth_dev` binds product name, vendor ID, product ID, and private feature flags.

## Control Flow And Usage
`pegasus.c` includes this header once normally, then includes it again under `PEGASUS_DEV` macro definitions to generate `usb_dev_id[]` and `pegasus_ids[]`. Product entries may use `PEGASUS_DEV_CLASS` for the Belkin ID collision where USB device class must also match. Feature flags from each table entry drive reset GPIO programming, Pegasus II setup, HomePNA/MII mode handling, and chip quirks.

## State And Persistence Behavior
The header itself has no executable state. Its product list is compiled into module ID tables and its private flags become runtime per-device behavior. The constants define hardware state read from or written to EEPROM, PHY, GPIO, Ethernet control, and wake registers.

## Dependencies And Integration Points
It is tightly coupled to `pegasus.c` and the USB module table generation pattern. It depends on surrounding kernel includes for USB, netdev, MII, tasklet, delayed work, URB, SKB, and integer types.

## Risks And Test Signals
The double-include macro pattern makes the product list compact but fragile: changing macro names or adding entries with mismatched feature flags affects both netdev behavior and USB matching. Device IDs with shared vendor/product pairs need class-sensitive entries or explicit blacklists. Tests should cover that every generated USB ID has a matching `usb_eth_dev` entry, vendor/product quirks select the right GPIO and Pegasus II behavior, HomePNA/MII flags work, and runtime `devid` extension does not overflow the sentinel slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/pegasus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/plusb.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/plusb.c

## Purpose
`plusb.c` is a very small `usbnet` minidriver for Prolific PL-2301, PL-2302, PL-25A1, and PL-27A1 USB host-to-host link cables. It relies almost entirely on usbnet's generic point-to-point handling and only provides a reset/handshake vendor request plus a USB ID table.

## Important APIs, Types, And Functions
The file defines Prolific handshake bits such as `PL_S_EN`, `PL_TX_READY`, `PL_RESET_OUT`, `PL_RESET_IN`, `PL_TX_C`, `PL_TX_REQ`, and `PL_PEER_E`. `pl_vendor_req()` sends a vendor write request with a value and index. `pl_set_QuickLink_features()` wraps request 3. `pl_reset()` tries to set suspend enable, reset both pipes, and peer-exists bits; failures are debug-logged but reset returns 0 because some units reject the request and still function.

The `prolific_info` `driver_info` declares `FLAG_POINTTOPOINT | FLAG_NO_SETINT` and supplies `.reset = pl_reset`. The USB ID table covers full-speed PL-2301/2302, high-speed PL-25A1 and variants, National Instruments/Belkin IDs, and SuperSpeed PL-27A1 variants.

## Control Flow
USB probe/disconnect/suspend/resume are all generic usbnet callbacks. On reset, usbnet calls `pl_reset()`, which sends the QuickLink feature request and returns success regardless of device response. There are no custom RX/TX fixups, no custom netdev ops, and no explicit endpoint discovery in this file.

## State And Persistence Behavior
The driver keeps no private state and writes no persistent storage. Runtime behavior is entirely usbnet-managed except for the reset feature bits sent to the device. The comments warn that the Prolific handshaking is weak and that reconnecting one end can require restarting both ends.

## Dependencies And Integration Points
The file depends on usbnet, USB core, netdevice, ethtool/MII headers included for common usbnet driver style, and module USB registration. It integrates by providing a `driver_info`, USB ID table, and `usb_driver` named `plusb`.

## Risks And Test Signals
The main risk is unreliable hardware handshaking and device wedge behavior under load. Since reset ignores vendor-request failure, a device may bind even if the requested pipe reset did not happen. Tests should cover every listed USB ID, reset request success and failure, usbnet point-to-point link creation, suspend/resume, unplug/replug behavior, and sustained traffic on PL-2301/2302/25A1/27A1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/plusb.c -->
