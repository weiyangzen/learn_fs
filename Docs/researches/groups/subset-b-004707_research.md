# Research: subset-b-004707

Grouped source research for USB network drivers under `sources/distributed-fs/ceph-client/drivers/net/usb`. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/rndis_host.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/rndis_host.c

Purpose: Implements Linux host-side RNDIS over USB networking using the `usbnet` CDC binding. It negotiates RNDIS control messages, queries device parameters, sets packet filters, wraps outbound Ethernet frames in RNDIS data headers, unwraps inbound batches, and provides USB device matching for generic RNDIS, ActiveSync-like, Hytera, ZTE, and other RNDIS interfaces.

Important APIs and functions: `rndis_command()` is the central synchronous RNDIS request/response RPC helper over CDC encapsulated control messages, including optional interrupt-status polling and handling of indications and keepalives. `rndis_query()` builds RNDIS OID queries and validates response offsets and lengths. `generic_rndis_bind()` performs CDC binding, RNDIS init, MTU sizing, optional early init, physical-medium filtering, permanent MAC retrieval, and packet-filter enablement. `rndis_unbind()` sends `RNDIS_MSG_HALT` before CDC cleanup. `rndis_rx_fixup()` splits RNDIS batched packets and optionally applies ZTE destination-MAC repair. `rndis_tx_fixup()` prepends `struct rndis_data_hdr`. Exported symbols let other RNDIS-flavored drivers reuse the control and framing helpers.

Control flow: Probe is delegated to `usbnet_probe`, which calls the selected `driver_info.bind`. Bind allocates a control buffer, calls `usbnet_generic_cdc_bind`, sends `RNDIS_MSG_INIT`, clamps MTU if the device reports a smaller max transfer, optionally filters wireless/non-wireless devices through `RNDIS_OID_GEN_PHYSICAL_MEDIUM`, reads `RNDIS_OID_802_3_PERMANENT_ADDRESS`, then enables data flow with `RNDIS_OID_GEN_CURRENT_PACKET_FILTER`. Runtime RX iterates over one or more RNDIS packet messages in a single SKB, returning cloned packets via `usbnet_skb_return` and leaving the last packet for the caller. TX ensures headroom and writes one RNDIS packet header per SKB.

State and persistence: Uses `dev->xid` for request IDs, CDC state in `dev->data`, `dev->hard_mtu`, `dev->rx_urb_size`, netdev MTU/address, and `driver_info->data` flags for poll-status and ZTE fixups. No durable persistence exists; state lives in USB device RNDIS session state and the `usbnet` netdev until disconnect/unbind.

Dependencies and integration points: Depends on `linux/usb/usbnet.h`, `linux/usb/cdc.h`, and `linux/usb/rndis_host.h`; integrates with `usbnet_cdc_unbind`, `usbnet_generic_cdc_bind`, `usbnet_open/stop/start_xmit`, and CDC ZTE RX fixup helpers. Device matching is through `USB_INTERFACE_INFO`, `USB_VENDOR_AND_INTERFACE_INFO`, and `USB_DEVICE_AND_INTERFACE_INFO`.

Risks: RNDIS control responses are bounded to `CONTROL_BUFFER_SIZE`, so offset and length validation is critical. `rndis_command()` assumes no concurrent request is pending and retries unmatched IDs, which would be fragile if used outside serialized probe/disconnect paths. Device quirks around status polling, ActiveSync payload padding, keepalives, and ZTE MAC repair are protocol-specific. TX does not force a short final packet, matching a noted FIXME. Failure paths must release the CDC data interface and send halt where appropriate.

Test signals: Attach generic RNDIS, ActiveSync-like, poll-status, and ZTE devices; exercise init failure, physical-medium mismatch, MAC query failure, packet-filter failure, batched RX with malformed headers, keepalive response handling, MTU clamp behavior, and TX headroom/tailroom paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/rndis_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/rtl8150.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/rtl8150.c

Purpose: Standalone USB Ethernet driver for Realtek RTL8150-class 10/100 adapters and compatible vendor IDs. Unlike `usbnet`-based drivers in this group, it owns netdev registration, URB allocation/submission, interrupt status parsing, RX SKB pooling, tasklet rescheduling, and MII private ioctls directly.

Important APIs and functions: `rtl8150_probe()` allocates `net_device`, private `struct rtl8150`, endpoint buffers, URBs, tasklet, and registers the netdev. `rtl8150_open()` submits RX and interrupt URBs, enables traffic, sets carrier, and starts the queue. `rtl8150_close()` disables traffic and kills URBs. `read_bulk_callback()`, `write_bulk_callback()`, and `intr_callback()` are the RX, TX, and status completion paths. `rx_fixup()` tasklet refills the RX SKB pool and retries RX URB submission. `get_registers()`/`set_registers()` and MII helpers perform vendor control transfers. `rtl8150_start_xmit()` pads frames and submits a single bulk-out URB.

Control flow: Probe verifies required bulk and interrupt endpoints, resets the device, fills a small RX SKB pool, reads or randomizes the MAC, stores interface data, and registers the netdev. Open selects an RX SKB from the pool, submits bulk-in and interrupt-in URBs, writes IDR with the MAC, programs CR/TCR/RCR, and starts TX. RX completion strips the trailing four bytes, passes packets with `netif_rx`, updates stats, pulls the next pooled SKB, and resubmits; allocation or submission failures schedule the tasklet. TX stops the queue, pads to Ethernet minimum and USB short-packet requirements, submits bulk-out, then wakes the queue in the completion callback. Interrupts update TX error counters and carrier state from device status bytes.

State and persistence: `struct rtl8150` stores URBs, current RX/TX SKBs, a four-entry RX SKB pool guarded by `rx_pool_lock`, the tasklet, flags such as `RTL8150_UNPLUG` and `RX_URB_FAIL`, interrupt buffer, PHY address, and USB/netdev pointers. MAC can be written to IDR and optionally EEPROM only when `EEPROM_WRITE` is compiled. Runtime state is volatile; no persistent writes are enabled by default.

Dependencies and integration points: Uses core USB control/bulk/interrupt URB APIs, netdev operations, ethtool link settings, MII register constants, `SIOCDEVPRIVATE` MII access, tasklets, and SKB allocation APIs. Device table covers Realtek, Melco, Micronet, Longshine, OQO, and Zyxel IDs.

Risks: The driver manually owns URB and SKB lifetimes, making disconnect, suspend/resume, and callback races important. `read_bulk_callback()` assumes `dev->rx_skb` is valid on resubmit paths. TX stores one `dev->tx_skb` pointer and must clear/free it if submission fails. MII control polling has fixed retry limits. `free_skb_pool()` does not null entries, but it is only used in teardown. Carrier state is derived both from CSCR reads and interrupt bytes.

Test signals: Probe/disconnect with missing endpoints, open/close cycles, suspend/resume while netif is running, RX allocation failure and URB submission failure paths, TX submission failure and timeout handling, multicast/promiscuous mode register writes, MII private ioctls with and without `CAP_NET_ADMIN`, and link status changes via interrupt URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/rtl8150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sierra_net.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/sierra_net.c

Purpose: USB-to-WWAN driver for Sierra Wireless Direct IP modems. It extends `usbnet` with Sierra HIP control/data headers, modem sync/restart handshake, link-sense indication parsing, generated per-interface MAC uniqueness, and IP-only TX/RX handling for CDC-like endpoints.

Important APIs and functions: `parse_hip()` decodes normal and extended HIP headers, including padded packets and length validation. `build_hip()` writes the TX HIP header from `tx_hdr_template`. `sierra_net_bind()` validates three endpoints, initializes `struct sierra_net_data`, configures WWAN netdev properties, sets MTU/RX URB size, and checks firmware attributes. `sierra_net_status()` handles CDC notifications and defers response reads. `sierra_net_kevent()` pulls encapsulated responses, processes LSI, restart, host sync, and ignored grant messages. `sierra_net_rx_fixup()` unwraps HIP-framed inbound IP packets. `sierra_net_tx_fixup()` validates linear Ethernet/IP SKBs, prepends HIP, and handles ZLP padding.

Control flow: Probe delegates to `usbnet_probe`, then starts the status interrupt URB and initiates a double SYNC. The sync timer resends MSYNC until a restart indication clears it. Status notifications set event bits and schedule work; work reads `USB_CDC_GET_ENCAPSULATED_RESPONSE`, parses HIP, and either updates link state from LSI, responds to HSYNC, or stops sync retry on restart. Data RX parses one or more extended IP-in HIP frames, rewrites the synthetic Ethernet header, clones intermediate packets, and returns the last to `usbnet`. TX only accepts packets when `link_up` is true, the packet is linear Ethernet, and the EtherType is IPv4 or IPv6.

State and persistence: `struct sierra_net_data` stores link state, TX HIP context template, sync/shutdown messages, interface number, work flags, work item, timer, and backpointer to `usbnet`. `iface_counter` is an atomic process-wide counter used to make generated MAC addresses unique with the interface number. All state is runtime-only; the modem is told shutdown on unbind.

Dependencies and integration points: Uses `usbnet_get_endpoints`, `usbnet_status_start/stop`, CDC encapsulated control requests, Linux timers/workqueues, netdev carrier/link APIs, WWAN `FLAG_WWAN`, and IP/UDP/Ethernet header helpers. Device IDs match Sierra and AT&T Direct IP interfaces 7, 10, and 11 for selected products.

Risks: HIP length parsing is security-sensitive because control and data packets can batch or be padded. LSI parsing assumes known UMTS single or dual-stack layouts and rejects unsupported protocols/link types. `sierra_net_tx_fixup()` drops silently through `usbnet` accounting when link is down or headroom is insufficient. Timer/work teardown ordering in unbind must prevent use-after-free. MAC uniqueness via an 8-bit counter is explicitly limited for many simultaneous interfaces.

Test signals: Firmware attribute mismatch, missing status endpoint, sync retry and restart response, HSYNC response, LSI link-up/down cases including idle/no coverage, malformed HIP headers, batched RX packets, IPv4/IPv6 TX, non-IP TX drop, ZLP tail byte path, and unbind while timer/work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sierra_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.c

Purpose: `usbnet` driver for SMSC/Microchip LAN75xx USB 2.0 Gigabit Ethernet devices. It programs vendor registers, MII/PHY, EEPROM, multicast hash filters, checksum and TSO framing, FIFO/burst settings, Wake-on-LAN, suspend modes, and RX/TX descriptor fixups for LAN7500/LAN7505-class adapters.

Important APIs and functions: `smsc75xx_read_reg()`/`smsc75xx_write_reg()` and `_nopm` variants wrap vendor control messages. MDIO helpers poll `MII_ACCESS` under `dev->phy_mutex`. EEPROM helpers read/write byte addresses with busy/timeout polling. `smsc75xx_dataport_write()` writes VLAN/hash/filter RAM through the dataport. `smsc75xx_reset()` performs device ready wait, lite/PHY reset, MAC/FIFO/burst/RFE/PHY/MAC enablement. `smsc75xx_bind()` allocates `struct smsc75xx_priv`, initializes features, MAC, reset, netdev, and ethtool hooks. PM helpers select suspend modes and program WOL filters. `smsc75xx_rx_fixup()` and `smsc75xx_tx_fixup()` process hardware command words.

Control flow: Bind gets USB endpoints, allocates private state, enables checksum features, waits for readiness, reads MAC from device tree/EEPROM/random, then runs a full reset. Reset programs burst capacity by USB speed and `turbo_mode`, bulk-in delay, FIFO endpoints, interrupt clearing, LED defaults when no EEPROM loaded, flow control defaults, RFE receive filtering, checksum engines, multicast filter, PHY initialization and interrupt enable, MAC auto-speed/duplex, TX/RX enablement, and max frame length. Link interrupts defer `EVENT_LINK_RESET`, which clears PHY interrupt status and recalculates flow control from negotiated pause advertisement. RX iterates command pairs, drops descriptor errors, validates size, removes FCS, sets checksum state, and clones intermediate packets. TX prepends two command words, enabling checksum and LSO when applicable.

State and persistence: `struct smsc75xx_priv` stores the current `rfe_ctl`, WOL options, multicast hash table, dataport mutex, RFE spinlock, deferred multicast work, suspend flags, and backpointer. EEPROM writes through ethtool are persistent if accepted with `LAN75XX_EEPROM_MAGIC`; MAC from EEPROM/device tree persists outside the driver. Runtime registers, PHY state, filter RAM, and suspend flags are volatile.

Dependencies and integration points: Depends on `smsc75xx.h` register definitions, `usbnet`, MII helpers, ethtool EEPROM/WOL, device-tree MAC retrieval, workqueues, CRC16/CRC32/bitrev helpers, runtime PM `_nopm` USB control paths, and netdev feature flags for RXCSUM/IP/IPV6 checksum offload.

Risks: Register sequencing is strict and many steps abort bind/reset on first failure. `smsc75xx_set_features()` notes a race after releasing `rfe_ctl_lock` before writing the register. Suspend code mixes autosuspend and system suspend, relies on `_nopm` reads, and has a TODO for resume after system-suspend failure. WOL filter CRC/mask programming is bitfield-sensitive. RX size arithmetic subtracts padding/FCS and must reject malformed hardware descriptors. Gigabit PHY workaround waits up to long timeouts.

Test signals: LAN7500/LAN7505 probe at high/full speed, `turbo_mode` on/off, EEPROM get/set with wrong and right magic, device-tree MAC override, multicast/promisc/allmulti transitions, MTU changes up to jumbo limit, RX checksum on/off and descriptor errors, TX checksum and GSO/LSO, PHY link reset and flow control negotiation, autosuspend modes for link up/down/interface down, WOL options for PHY/magic/broadcast/multicast/ARP/unicast, resume/reset-resume, and disconnect with deferred multicast work pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.h

Purpose: Hardware register and bitfield map for SMSC/Microchip LAN75xx USB Gigabit Ethernet devices. It defines TX/RX command word fields, system control/status registers, MAC registers, MII access registers, WOL filter registers, PHY vendor registers, USB vendor request IDs, and interrupt endpoint status bits consumed by `smsc75xx.c`.

Important APIs and types: The header exposes macros rather than functions. Important groups include `TX_CMD_A/B_*` and `RX_CMD_A/B_*` descriptor fields, `HW_CFG`, `PMT_CTL`, `INT_STS`, `DP_SEL/DP_CMD/DP_ADDR/DP_DATA`, `BURST_CAP`, `INT_EP_CTL`, `E2P_CMD/E2P_DATA`, `RFE_CTL`, FIFO/flow registers, `MAC_CR/MAC_RX/MAC_TX/FLOW`, address/filter registers, `WUCSR/WUF_CFGX/WUF_MASKX`, optional offload registers, PHY interrupt/mode/special registers, and `USB_VENDOR_REQUEST_*`.

Control flow: No executable flow exists. The constants define how the C driver sequences reset, configures FIFOs and receive filtering, accesses EEPROM/PHY/dataport RAM, parses RX command words, emits TX command words, and programs wake filters.

State and persistence: No direct state. It encodes hardware ABI values; incorrect constants persist as bad runtime device programming. EEPROM-related constants gate persistent EEPROM access from the driver.

Dependencies and integration points: Included only by `smsc75xx.c`. It relies on kernel USB request direction/type macros and `BIT()` for interrupt endpoint fields.

Risks: Bit mask mistakes affect hardware control directly. Some similarly named interrupt bits use trailing underscores in hardware names, so call sites must match the exact macro set. RX/TX command length and checksum fields must align with packet fixup code. WOL filter address spacing is encoded by macros that suspend code uses for repeated writes.

Test signals: Compile coverage of all register users, reset/init traffic on real LAN75xx hardware, EEPROM read/write, multicast hash programming, RX/TX descriptor parsing, WOL filter programming, and PHY interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc75xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.c

Purpose: `usbnet` driver for SMSC/Microchip LAN95xx USB 2.0 Ethernet devices, including LAN9500/9500A/9512/9530/9730/89530 and compatible 10BASE-T1 devices. It programs vendor registers, exposes a phylib-backed MDIO bus, maps PHY interrupts through an irqdomain, supports EEPROM/WOL/ethtool selftests, and handles RX/TX descriptor fixups with checksum offload.

Important APIs and functions: `smsc95xx_read_reg()`/`write_reg()` select normal or `_nopm` USB control functions based on `pdata->pm_task`. `smsc95xx_mdio_read/write()` and `smsc95xx_mdiobus_*` bridge hardware MII access into a registered `mii_bus`. `smsc95xx_bind()` allocates private data, resets hardware, creates an irqdomain and MDIO bus, discovers/connects the PHY, detects revision features, and installs netdev/ethtool ops. `smsc95xx_reset()` initializes burst, RX offset, LEDs, flow control, VLAN, checksum offload, multicast, interrupts, and TX/RX paths. PM helpers program suspend modes and WOL filters. `smsc95xx_rx_fixup()` and `smsc95xx_tx_fixup()` parse/prepend hardware headers and checksum metadata.

Control flow: Bind gets endpoints, allocates `struct smsc95xx_priv`, enables IPv4 TX checksum and RX checksum, sets `EVENT_NO_IP_ALIGN`, reads the MAC, runs reset, builds IRQ resources for PHY interrupt delivery, registers an MDIO bus, locates a PHY, detects feature flags from `ID_REV`, connects phylib, and returns to `usbnet`. Runtime link interrupts call `generic_handle_domain_irq` for the PHY IRQ; phylib link-change callback updates MAC duplex/flow control and defers link-change work. RX walks batched frames with a 32-bit status header plus IP alignment, updates error counters, applies RX checksum by reading the trailer, removes checksum/FCS, clones intermediate packets, and returns the last. TX builds command words and optionally a checksum preamble, falling back to software checksum for small packets that hardware cannot handle.

State and persistence: `struct smsc95xx_priv` stores MAC control shadow, multicast hash registers, WOL options, pause settings, feature flags, suspend flags, PHY/MDIO/IRQ objects, `pm_task`, and phylib device. EEPROM writes through ethtool persist when `LAN95XX_EEPROM_MAGIC` matches. PHY, irqdomain, and mdiobus registrations persist until unbind; register and suspend state is runtime-only.

Dependencies and integration points: Depends on `smsc95xx.h`, `usbnet`, phylib, MDIO bus APIs, IRQ domains, ethtool selftest helpers from `net/selftests.h`, device-tree MAC retrieval, CRC/bitrev helpers, and runtime PM. USB device table includes many Microchip alternate IDs plus SYSTEC and EVB-LAN8670 devices.

Risks: The PM path uses `pm_task` to choose no-PM control transfers; stale or missing assignment would deadlock or wake incorrectly. IRQ domain and MDIO resource unwinds must stay ordered. TX checksum has a known hardware limitation for checksums in the last four bytes and uses a software workaround. RX size and padding calculations must reject malformed frames. Some revisions lack remote wakeup; `manage_power` prevents autosuspend by holding autopm when needed. WOL filter packing differs between 4-filter and 8-filter devices and is easy to misprogram.

Test signals: Probe/unbind with internal and external PHY, MDIO register reads/writes, phylib link changes, interrupt endpoint PHY IRQ, all supported chip IDs and feature detection, EEPROM get/set, ethtool register dump/selftest/pause settings, multicast/promisc/allmulti async writes, RX/TX checksum enabled/disabled including small TCP ACK workaround, autosuspend for link up/down/interface down, system suspend WOL patterns/magic/PHY, reset-resume, and remote-wakeup-incapable revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.h

Purpose: Hardware register and bitfield definitions for SMSC/Microchip LAN95xx USB Ethernet devices. It defines TX command words, RX status fields, SCSR/MAC/PHY registers, WOL registers, checksum offload controls, vendor-specific PHY registers, USB vendor request IDs, and interrupt endpoint bits used by `smsc95xx.c`.

Important APIs and types: The header is macro-only. Key groups include `TX_CMD_A/B_*`, `RX_STS_*`, `ID_REV_*` chip IDs, `INT_STS`, `RX_CFG`, `TX_CFG`, `HW_CFG`, `PM_CTRL`, `LED_GPIO_CFG`, `AFC_CFG`, `E2P_CMD/E2P_DATA`, `BURST_CAP`, `STRAP_STATUS`, `INT_EP_CTL`, `MAC_CR`, `ADDRH/ADDRL`, `HASHH/HASHL`, `MII_ADDR/MII_DATA`, `FLOW`, `VLAN1/2`, `WUFF/WUCSR`, `COE_CR`, PHY EDPD/mode/interrupt/special registers, and `INT_ENP_*`.

Control flow: No executable flow. The definitions drive the C driver's reset sequence, MDIO bus access, EEPROM access, packet descriptor parsing, checksum offload programming, PHY interrupt bridging, and WOL filter packing.

State and persistence: No direct state. EEPROM and WOL constants influence persistent EEPROM access and suspend wake behavior, while chip-ID constants select feature availability at runtime.

Dependencies and integration points: Included by `smsc95xx.c`; relies on kernel USB direction/type and `BIT()` macros. Its chip-ID list is paired with the USB product table and revision detection in the C file.

Risks: LAN95xx has several revisions with different wake-filter and remote-wakeup capabilities, so incorrect chip-ID or feature masks can enable unsupported behavior. RX/TX field width errors would corrupt packet framing. PM and WOL bit names are close to LAN75xx but not identical, so sharing assumptions across headers would be risky.

Test signals: Build all `smsc95xx.c` users, verify reset and register dumps on multiple chip revisions, test checksum offload bits, MDIO/PHY interrupt delivery, EEPROM commands, WOL filter programming on 4-filter and 8-filter parts, and RX/TX descriptor parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/smsc95xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9700.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/sr9700.c

Purpose: `usbnet` driver for CoreChip SR9700 USB 1.1 10 Mbps half-duplex Ethernet adapters. It provides simple vendor register access, EEPROM reading, fixed link settings, multicast mode programming, MAC programming, PHY reset, and SR9700-specific RX/TX framing.

Important APIs and functions: `sr_read()`/`sr_write()` and register helpers issue vendor control transfers defined in `sr9700.h`. EEPROM helpers poll `SR_EPCR` and read 16-bit words for ethtool. `sr9700_bind()` gets endpoints, installs netdev/ethtool ops, resets the device/PHY, reads MAC from `SR_PAR`, sets RX URB size, and enables broadcast/multicast policy. `sr9700_rx_fixup()` parses one or more packets with a three-byte RX header and four-byte CRC trailer. `sr9700_tx_fixup()` prepends a two-byte length header. `sr9700_status()` updates carrier from interrupt status.

Control flow: Bind configures the `usbnet` netdev, sets hard header overhead, resets `SR_NCR`, reads the MAC loaded from EEPROM or default PAR, toggles `SR_PRR` for PHY reset, and calls `sr9700_set_multicast`. Runtime ethtool link reads `SR_NSR` and reports fixed 10/Half no-autoneg. RX validates the magic/status byte, computes length excluding CRC, returns code `2` for the last adjusted packet, and copies earlier batched packets to fresh SKBs. TX reserves two header bytes, adjusts the advertised length if the resulting USB packet would be exactly maxpacket-sized, and returns the SKB to `usbnet`.

State and persistence: The driver uses only `usbnet` state plus hardware registers. EEPROM is read-only through ethtool in this build; a write helper exists but is `__maybe_unused`. MAC can be changed at runtime via async PAR writes and netdev state. Link carrier is derived from `SR_NSR` or interrupt bytes.

Dependencies and integration points: Depends on `sr9700.h`, `usbnet`, ethtool, netdev multicast helpers, and core USB vendor control transfers. Device IDs cover SR9700 and SR9702 interface 1 when interface 0 is virtual CD-ROM.

Risks: The chip lacks multicast filtering, so any multicast subscription requires all-multicast reception. RX framing accepts only `RSR_MF` and has tight length checks; malformed or short packets drop the batch. TX length adjustment for USB padding is device-specific. EEPROM access requires even offset/length. Fixed 10/Half reporting intentionally ignores hardware status registers beyond link.

Test signals: SR9700/SR9702 probe, MAC read/change, EEPROM read with odd and even offsets, multicast/promisc/allmulti mode, link interrupt up/down, RX batches with valid/malformed headers and CRC trailer lengths, TX maxpacket multiple padding, USB 1.1 throughput, and suspend/resume through generic `usbnet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9700.h -->
# sources/distributed-fs/ceph-client/drivers/net/usb/sr9700.h

Purpose: Register map and protocol constants for CoreChip SR9700 USB 1.1 Ethernet devices. It defines network, TX/RX, flow-control, EEPROM, wakeup, PHY reset, SDRAM pointer, ID, USB status/control registers, vendor command IDs, request types, EEPROM length, and packet overhead sizes.

Important APIs and types: Macro groups include `SR_NCR/NSR/TCR/TSR/RCR/RSR`, overflow and flow-control registers, `SR_EPCR/EPAR/EPDR` EEPROM fields, `SR_WCR`, `SR_PAR`, `SR_PRR`, TX/RX SDRAM pointer registers, `SR_VID/PID/CHIPR`, USB status/control fields, `SR_RD_REGS`, `SR_WR_MULTIPLE_REGS`, `SR_WR_SINGLE_REG`, `SR_REQ_RD_REG`, `SR_REQ_WR_REG`, `SR_EEPROM_TIMEOUT`, `SR_EEPROM_LEN`, `SR_TX_OVERHEAD`, and `SR_RX_OVERHEAD`.

Control flow: No executable flow. The C driver uses these definitions to reset hardware, read EEPROM/MAC, program RX filters, parse status interrupts, and frame RX/TX packets.

State and persistence: No direct state. EEPROM-related constants control persistent storage access; other values describe volatile device registers.

Dependencies and integration points: Included by `sr9700.c`; relies on USB request direction/type macros from kernel headers included before or alongside it.

Risks: This is a dense 8-bit register map; wrong bit masks directly misprogram packet filtering, PHY reset, or EEPROM access. Packet overhead constants must remain synchronized with RX/TX fixup logic.

Test signals: Compile `sr9700.c`, exercise reset/PHY/MAC/EEPROM paths, validate link/status bit interpretation, and send/receive framed packets with expected overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9700.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9800.c -->
# sources/distributed-fs/ceph-client/drivers/net/usb/sr9800.c

Purpose: `usbnet` driver for CoreChip SR9800 USB 2.0 Ethernet adapters, modeled after ASIX-style devices. It implements vendor command access, AX-like length/complement packet framing, multicast hash filtering, MII access, EEPROM/WOL ethtool hooks, PHY power/reset sequencing, link reset medium programming, and USB speed-dependent bulk-in sizing.

Important APIs and functions: `sr_read_cmd()`/`sr_write_cmd()` and async variants wrap vendor control transfers. `sr_rx_fixup()` parses batched frames with a 32-bit length/complement header. `sr_tx_fixup()` prepends the same style of header and optional padding sentinel. `sr_set_multicast()` builds the 8-byte hash table or promiscuous/all-multicast RX control. `sr_mdio_read/write()` switch between software and hardware MII. `sr_get_phyid()`, `sr_get_wol()`, `sr_set_wol()`, `sr_get_eeprom()`, and `sr_set_mac_address()` implement ethtool/netdev support. `sr9800_reset()`, `sr9800_phy_powerup()`, `sr9800_set_default_mode()`, and `sr9800_bind()` perform hardware bring-up.

Control flow: Bind sets EEPROM length, gets endpoints, programs LED muxes, reads MAC, initializes MII callbacks and PHY ID, selects embedded/external PHY mode, powers the PHY, disables RX, reads PHY ID, sets default medium/IPG/RX control, sets high-speed or full-speed bulk-in size, and returns to `usbnet`. Reset toggles GPIO/EEPROM reload and PHY reset modes, clears RX control, repeats reset phases, restores default mode, and rewrites the MAC. Link reset uses MII media state to update medium mode for speed and duplex. RX loops over headers, verifies length complement, validates size against MTU plus Ethernet/VLAN header, copies each packet to a new SKB, and ensures final offset matches SKB length. TX adjusts headroom/tailroom, writes length/complement header, appends a `0xffff0000` padding word when needed, and records one TX packet for usbnet stats.

State and persistence: `struct sr_data` is overlaid on `dev->data` and stores multicast filter bytes, temporary MAC buffer, PHY/LED modes, and EEPROM length. MAC changes update netdev state and asynchronously write node ID. EEPROM is read through ethtool with `SR_EEPROM_MAGIC`; WOL monitor mode persists in device registers across runtime but not necessarily power loss. Most state is volatile USB device register state.

Dependencies and integration points: Depends on `sr9800.h`, `usbnet`, MII/ethtool helpers, CRC32 multicast hashing, VLAN header sizing, and generic `usbnet_mii_ioctl`. Device table matches USB VID/PID `0x0fe6:0x9800`.

Risks: The RX header length/complement check is critical for malformed USB data. `sr_read_medium_status()` may return a negative error encoded as `u16` and callers log it without full error handling. `dev->data` overlay must stay within the documented five-unsigned-long space. PHY reset sequences rely on long sleeps and embedded PHY address conventions. TX padding calculation uses `dev->maxpacket - 1`, so unusual endpoint values would be risky.

Test signals: Probe on high-speed and full-speed links, LED and bulk-in size programming, embedded/external PHY paths, MII reads/writes and link reset speed/duplex modes, multicast/promisc/allmulti hash writes, WOL get/set, EEPROM reads with even length, MAC change while down, RX malformed complement/length cases, TX padding sentinel, reset/resume through `usbnet`, and sustained multi-packet RX batches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9800.h -->
# sources/distributed-fs/ceph-client/drivers/net/usb/sr9800.h

Purpose: Command, bitfield, default-value, and private-data definitions for CoreChip SR9800 USB 2.0 Ethernet devices. It maps vendor commands for MII, EEPROM, RX control, node ID, multicast filter, medium/monitor mode, GPIO, software reset, PHY selection, bulk-in size, and LED muxing.

Important APIs and types: Macro groups include `SR_CMD_*` command IDs, `SR_RX_CTL_*`, `SR_MONITOR_*`, `SR_MEDIUM_*`, `SR_GPIO_*`, `SR_SWRESET_*`, `SR_LED_MUX_*`, USB request flags, multicast limits, IPG defaults, `SR9800_MEDIUM_DEFAULT`, `SR_DEFAULT_RX_CTL`, EEPROM magic/length, `DRIVER_FLAG`, bulk-in size table `SR9800_BULKIN_SIZE`, `struct sr_data`, and packed interrupt payload `struct sr9800_int_data`.

Control flow: No executable flow beyond the static bulk-in size table. The C driver uses these definitions to frame packets, configure link mode, reset PHY/MAC, program WOL, set LED behavior, and size RX URBs.

State and persistence: No direct state except the static lookup table. `struct sr_data` defines the runtime layout stored inside `usbnet.dev->data`; EEPROM and monitor-mode constants influence persistent or semi-persistent device settings when the C driver reads/writes them.

Dependencies and integration points: Included by `sr9800.c`; relies on USB request macros, `FLAG_*` usbnet flags, and Ethernet constants made available by included kernel headers.

Risks: `struct sr_data` must not exceed `usbnet`'s small inline data storage, as noted by the file comment. Bulk-in byte-count/threshold values are hardware-specific. Command IDs and reset bits mirror ASIX-style semantics but are SR9800-specific; cross-driver assumptions can misconfigure hardware.

Test signals: Compile `sr9800.c`, validate size of `struct sr_data`, probe/reset hardware, confirm bulk-in size table selection, verify interrupt payload link parsing, and exercise all command groups through MAC, MII, EEPROM, multicast, WOL, and TX/RX paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/usb/sr9800.h -->
