# Research: subset-b-004344

Grouped research for Apple BMAC/MACE Ethernet drivers and the Aquantia Atlantic driver files listed in work item `subset-b-004344`. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.c

Purpose: PowerMac `macio` network driver for Apple BMAC and BMAC+ Ethernet controllers behind DBDMA engines. It owns the Linux `net_device` lifecycle, maps the controller and TX/RX DMA channels, reads Open Firmware MAC properties and SROM station address data, and registers a normal Ethernet device.

Important APIs and types: `struct bmac_data` stores DMA MMIO pointers, ring command arrays, SKB rings, a software TX queue, multicast hash state, power-management flags, and a spinlock. The public integration surfaces are `bmac_netdev_ops`, `bmac_ethtool_ops`, the `macio_driver` `bmac_driver`, and module init/exit. Internal helpers include little-endian DBDMA accessors, `bmread()`/`bmwrite()`, MIF bit-banged PHY reads/writes, SROM bit clocking, ring constructors, interrupt handlers, and reset/start/timeout helpers.

Control flow: probe validates three resources and three interrupts, maps MMIO, disables the chip, prepares DBDMA command storage inside the private area, requests misc/TX/RX IRQs, powers the chip down until open, then registers the netdev. Open marks the device opened, resets/enables chip, initializes TX/RX rings, starts RX DMA, enables MACs/interrupts, and sends a dummy minimum frame because the hardware reportedly cannot receive until it transmits once. TX goes through a software `sk_buff_head`: `bmac_output()` enqueues, `bmac_start()` drains while DMA ring slots are available, and `bmac_txdma_intr()` completes SKBs and wakes the queue. RX DMA interrupt consumes completed descriptors, validates minimum length, strips FCS, passes packets through `eth_type_trans()`/`netif_rx()`, then rebuilds descriptors.

State and persistence: runtime state is entirely in `struct bmac_data`, hardware registers, DBDMA command rings, and SKBs. There is no disk persistence. Suspend/resume detach the device, stop timers/IRQs/DMA, free ring SKBs, power the chip off through `PMAC_FTR_BMAC_ENABLE`, then rebuild on resume if opened.

Dependencies and integration points: depends on PowerPC `macio`, Open Firmware properties, `pmac_call_feature`, DBDMA, Linux netdev/ethtool APIs, CRC helpers for multicast hashing, and Apple BMAC register constants from `bmac.h`.

Risks: old bus APIs (`virt_to_bus()`/`bus_to_virt()`) and raw DBDMA command manipulation are architecture-specific and fragile. RX fallback uses a global emergency buffer when allocation fails. Timeout recovery resets both DMA and MAC with in-flight state assumptions. SROM checksum verification currently returns success after reading, so station-address validation is minimal. Queueing plus DMA ring state requires lock correctness around interrupts, timeout, and close.

Test signals: build on PowerMac/mac-io configs, boot probe with BMAC and BMAC+ device-tree matches, `ip link set up/down`, sustained RX/TX, multicast/promiscuous mode changes, suspend/resume, IRQ error counters, and injected TX timeout or SKB allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.h

Purpose: register map and bit definitions for the Apple Big MAC controller used by `bmac.c`.

Important APIs/types: this header exports preprocessor constants only. It defines offsets for global interface registers (`XIFC`, `MIFCSR`, `SROMCSR`, `STATUS`, `INTDISABLE`), FIFO controls, TX registers (`TXRST`, `TXCFG`, collision counters), RX registers (`RXRST`, `RXCFG`, receive counters), multicast hash registers, MAC address registers, and error/interrupt masks.

Control flow: no executable control flow. The runtime driver uses these constants to reset TX/RX paths, program station address words, configure multicast hash filters, enable/disable interrupts, interpret error bits, and drive PHY/SROM sideband registers.

State and persistence: no state is stored here; it describes hardware state held in BMAC registers. Some masks are shared between status and interrupt-disable semantics, which is important because reads of `STATUS` clear latched conditions.

Dependencies/integration: consumed directly by `bmac.c`; comments note similarity to Sun HME. The register values assume the MMIO layout used by Apple macio BMAC hardware.

Risks: incorrect bit polarity can be serious because `INTDISABLE` uses disable-mask style values while `STATUS` uses event bits. Multiword MAC address register ordering must match the driver’s word writes. Header naming includes legacy/uncertain comments for some registers, so changes should be hardware-validated.

Test signals: compile coverage through `bmac.c`; runtime validation through successful reset, interrupt enable/disable behavior, multicast filtering, and accurate statistics counter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.c

Purpose: PowerMac `macio` driver for the AMD/Apple MACE Ethernet controller using DBDMA for TX and RX.

Important APIs/types: `struct mace_data` stores MACE MMIO, TX/RX DBDMA registers and command rings, SKB rings, chip revision, AAUI/GPSI port selection, TX timeout state, and a spinlock. Primary functions include `mace_probe()`, `mace_reset()`, `mace_open()`, `mace_close()`, `mace_xmit_start()`, `mace_interrupt()`, `mace_rxdma_intr()`, and `mace_tx_timeout()`. Module parameter `port_aaui` can force the physical port.

Control flow: probe checks macio resources, obtains `mac-address` or `local-mac-address`, allocates one global dummy RX buffer, maps controller and two DBDMA channels, chooses port mode, resets the chip, requests controller/TX/RX IRQs, and registers the netdev. Open resets hardware, allocates RX SKBs and DBDMA descriptors, arms RX and TX descriptor loops, enables TX/RX, and masks receive-chip interrupts because RX completion is DMA-driven. TX fills a descriptor if the ring has space, starts at most `MAX_TX_ACTIVE` transfers, and arms a timer. The main MACE interrupt drains transmit statuses, handles underrun/collision/carrier/retry errors, includes a special two-byte runt workaround, completes SKBs, and starts later queued descriptors. RX DMA interrupt processes descriptors, handles missing status words, validates appended MACE receive status, adjusts frame length for Ethernet vs 802.3 FCS behavior, submits SKBs, and refills descriptors.

State and persistence: state is private driver memory plus hardware registers/descriptors; nothing persists across unload. Close disables MAC and DMA and frees rings. Timeout recovery resets TX/RX paths, discards or advances one failed packet, restarts RX DMA, and re-enables MAC.

Dependencies/integration: depends on `macio`, DBDMA, Open Firmware, netdev, CRC multicast hashing, and `mace.h` register definitions. It integrates with the kernel network stack via `net_device_ops`; no ethtool-specific ops are provided.

Risks: hardware workarounds are subtle, especially `BROKEN_ADDRCHG_REV` and the bad-runt TX workaround. The driver uses legacy bus mappings and busy-wait register loops. RX length correction depends on header interpretation and appended status bytes. The TX timeout timer and interrupt path share mutable state under a spinlock.

Test signals: compile for PowerMac MACE configs, boot/probe with correct chip revision, open/close, AAUI/GPSI port selection, multicast/promiscuous updates, TX underrun/collision recovery, RX under allocation pressure using `dummy_buf`, and timeout reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.h

Purpose: MACE register layout and bit definitions for both PowerMac DBDMA MACE and Macintosh 68k PSC-DMA MACE drivers.

Important APIs/types: `struct mace` models the byte-wide register layout with 16-byte spacing through `REG(x)`. Constants cover transmit control/status (`XMTFC`, `XMTFS`, `XMTRC`), receive status (`RCVFS`), FIFO counts, interrupt/mask bits, bus interface control, FIFO configuration, MAC control, physical layer selection, address programming, and test/loopback modes.

Control flow: no functions. Drivers use this map to soft-reset, select ports, program station and logical multicast addresses, interpret TX/RX status bytes, configure FIFO watermarks, enable TX/RX, and read counters that clear on access.

State and persistence: describes volatile MMIO state only. Some status registers clear on read, so driver order matters. The `REG()` layout encodes hardware spacing and must match bus access width.

Dependencies/integration: included by `mace.c` and `macmace.c`; the same constants support DBDMA and PSC-DMA implementations.

Risks: duplicate macro name `XMTSV` appears for both `XMTFS` and `PR` status meanings, intentionally same value but easy to misuse. Because counters clear when read, instrumentation can perturb state. Port selection and `ADDRCHG` handling are chip-revision sensitive.

Test signals: successful reset/interrupt handling in both MACE drivers, correct multicast filter loading, accurate TX/RX error statistics, and port link behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/macmace.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/macmace.c

Purpose: platform driver for Macintosh 68k onboard MACE Ethernet, using PSC Ethernet DMA rather than macio/DBDMA.

Important APIs/types: `struct mace_data` stores fixed MACE base, coherent TX/RX ring buffers and DMA addresses, PSC DMA slot/tail counters, chip id, and owning device. `struct mace_frame` describes PSC receive frame layout with padded MACE status bytes. Main operations are `mace_probe()`, `mace_open()`, `mace_close()`, `mace_xmit_start()`, `mace_interrupt()`, `mace_dma_intr()`, `mace_tx_timeout()`, and PSC DMA reset/load helpers.

Control flow: probe allocates netdev, uses fixed `MACE_BASE` and `MACE_PROM`, reads a bit-reversed PROM MAC address with checksum, sets IRQs, and registers. Open requests normal and DMA IRQs, allocates coherent TX/RX rings, disables/resets PSC DMA, arms both RX DMA sets, resets TX DMA, enables MAC, and masks receive-chip interrupts. TX copies the SKB into the coherent TX ring buffer, programs PSC write address/length/command, toggles the slot, frees the SKB, and relies on DMA/MACE interrupts to free capacity. RX DMA interrupt checks PSC status, resets on error, walks completed ring entries, converts `mace_frame` records into SKBs, and reloads or restarts the active PSC set. Normal MACE interrupt handles transmit status and error accounting.

State and persistence: no persistent state. Coherent DMA rings are allocated on open and freed on device remove; close disables DMA/MAC but does not free rings in this file’s close path, while remove frees them. PSC slot state is reset by `mace_rxdma_reset()` and `mace_txdma_reset()`.

Dependencies/integration: uses m68k Macintosh interrupt IDs, `mac_psc` register helpers, fixed hardware addresses, Linux platform driver model, DMA mapping API, and `mace.h`.

Risks: fixed physical/virtual addresses and PSC magic constants are hardware-specific. TX ring size is one, so queue stop/wake accounting is sensitive. `mace_close()` disables hardware but does not release IRQs or coherent buffers; remove assumes open-time allocations exist. The PSC mystery-status loop and dual-set RX logic are fragile. TX stats increment before DMA completion, so failed transmissions may overcount packets.

Test signals: boot on supported AV Macintosh models, PROM checksum validation, open/close/remove sequencing, one-buffer TX queue wakeups, PSC DMA error reset paths, RX frame status decoding, and watchdog timeout recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/macmace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Kconfig

Purpose: Kconfig menu entries for aQuantia/Marvell Ethernet drivers.

Important APIs/types: defines `NET_VENDOR_AQUANTIA` vendor menu bool and `AQTION` tristate driver option. `AQTION` depends on PCI and on either MACsec support being enabled or MACsec being disabled (`MACSEC || MACSEC=n`) so the driver can reference optional MACsec integration safely.

Control flow: no runtime control flow; controls visibility and build selection. When vendor support is enabled, `AQTION` exposes the Atlantic AQtion driver.

State and persistence: Kconfig state persists in kernel build configuration only.

Dependencies/integration: tied to `drivers/net/ethernet/aquantia/Makefile`, which descends into `atlantic/` when `CONFIG_AQTION` is selected.

Risks: dependency changes can accidentally hide the driver, build it without required PCI support, or break optional MACsec combinations.

Test signals: `make menuconfig` visibility, builds for `AQTION=m/y`, and builds with `MACSEC=y`, `MACSEC=m`, and `MACSEC=n` where valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Makefile

Purpose: top-level build hook for aQuantia Ethernet drivers.

Important APIs/types: single kbuild assignment `obj-$(CONFIG_AQTION) += atlantic/`.

Control flow: no runtime behavior. During kernel build, selecting `CONFIG_AQTION` recurses into the Atlantic subdirectory.

State and persistence: build metadata only.

Dependencies/integration: consumes the `AQTION` Kconfig symbol and delegates object composition to `atlantic/Makefile`.

Risks: minimal; wrong symbol or path would prevent the driver from building.

Test signals: `make M=drivers/net/ethernet/aquantia` includes the Atlantic subtree when `CONFIG_AQTION` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/Makefile

Purpose: kbuild object list for the Atlantic AQtion driver.

Important APIs/types: builds `atlantic.o` from core NIC, PCI, vector, ring, hardware utility, ethtool, drvinfo, filter, PHY, hardware generation, and MACsec API objects. Conditionally adds `aq_macsec.o` under `CONFIG_MACSEC` and `aq_ptp.o` under `CONFIG_PTP_1588_CLOCK`. Adds `-I$(src)` include path.

Control flow: build-time only. It determines which optional feature objects are linked into the module/built-in driver.

State and persistence: none beyond build artifacts.

Dependencies/integration: integrates this subset with other Atlantic files not included here, including `aq_nic`, `aq_pci_func`, hardware-generation implementations, and MACsec register API.

Risks: optional feature source lists must match preprocessor guards in C files. Missing object entries can compile headers but fail link for feature paths.

Test signals: allmodconfig/allyesconfig builds, `CONFIG_MACSEC` and `CONFIG_PTP_1588_CLOCK` matrix builds, and module link symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_cfg.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_cfg.h

Purpose: central compile-time defaults and constants for Atlantic driver sizing, features, timing, and metadata.

Important APIs/types: defines default/max vectors and traffic classes, TX/RX descriptor counts, interrupt moderation modes and max usec value, queue/ring frame limits, RX refill thresholds, XDP page order, LRO/RSS defaults, PCI function capacities, service timer intervals, restart thresholds, flow-control and WOL defaults, autoneg/speed/MTU defaults, lock retry count, and driver name/description/author strings.

Control flow: no functions. These constants parameterize allocation, feature defaults, ethtool validation, ring sizing, and module metadata.

State and persistence: constants only; runtime values are copied into `aq_nic_cfg_s` elsewhere.

Dependencies/integration: included by `aq_common.h`, then broadly across Atlantic. `AQ_CFG_DRV_NAME` is used by module init, logs, ethtool, and hwmon naming.

Risks: changing descriptor, queue, or frame limits affects memory use, XDP constraints, ethtool ring bounds, and hardware programming expectations. The MTU default includes Ethernet header semantics used elsewhere.

Test signals: compile, driver load with default config, ethtool ring/coalesce validation, RSS queue setup, XDP MTU boundary tests, and WOL default behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_common.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_common.h

Purpose: common include hub and shared identifiers for Atlantic devices.

Important APIs/types: includes Ethernet, PCI, VLAN, `aq_cfg.h`, and utility definitions. Defines Aquantia PCI vendor ID, many AQtion device IDs, display NIC name, hardware revision selectors, and link speed/EEE bit masks.

Control flow: no executable logic.

State and persistence: constants only.

Dependencies/integration: included from most Atlantic files. Device IDs are used by PCI matching elsewhere; rate masks feed link settings, EEE ethtool conversion, and firmware configuration.

Risks: incorrect device IDs break probe matching. Speed bit changes must remain consistent with firmware and ethtool mapping. EEE mask composition is consumed directly by `aq_ethtool.c`.

Test signals: PCI ID table coverage, link speed advertisement tests, EEE get/set tests, and compile coverage across all Atlantic objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.c

Purpose: optional hwmon registration for Atlantic PHY and MAC temperature reporting.

Important APIs/types: defines hwmon callbacks `aq_hwmon_read()`, `aq_hwmon_read_string()`, `aq_hwmon_is_visible()`, `aq_hwmon_ops`, channel info, and `aq_drvinfo_init()`. When `CONFIG_HWMON` is not reachable, `aq_drvinfo_init()` is a no-op.

Control flow: init registers a devm hwmon device using the netdev name and `aq_nic_s` as driver data. Visibility hides PHY or MAC temperature channels unless corresponding firmware/hardware callbacks exist. Reads dispatch channel 0 to `aq_fw_ops->get_phy_temp`, and channel 1 to firmware `get_mac_temp` or hardware `hw_get_mac_temp`.

State and persistence: no persistent state; hwmon device is devm-managed under the PCI device. Temperature values are read live from firmware/hardware.

Dependencies/integration: depends on `aq_nic` for ops and PCI device, Linux hwmon framework, and firmware/hardware callback availability.

Risks: callbacks are dereferenced through `aq_nic->aq_fw_ops`/`aq_hw_ops`, so init must occur after those are populated. Missing callbacks must remain hidden to avoid unsupported reads. Temperature units follow hwmon expectations and firmware semantics.

Test signals: builds with and without `CONFIG_HWMON`, sysfs hwmon labels and temp inputs, callback absence visibility, and error propagation from firmware/hardware temperature reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.h

Purpose: declaration header for driver information initialization.

Important APIs/types: forward-declares `struct net_device` and declares `int aq_drvinfo_init(struct net_device *ndev);`.

Control flow: none.

State and persistence: none.

Dependencies/integration: included by Atlantic initialization code to register optional hwmon support without exposing hwmon internals.

Risks: low; signature must match both `CONFIG_HWMON` and stub implementations.

Test signals: compile with hwmon enabled/disabled and call-site link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.c

Purpose: ethtool control and reporting surface for Atlantic netdevices.

Important APIs/types: exports `const struct ethtool_ops aq_ethtool_ops`. Implements register dumps, link settings, driver info, statistics strings/data, LED identify, RSS get/set, RX NFC rule get/set, interrupt coalescing, WOL, timestamp info, EEE, pause parameters, ring sizing, message level, private loopback flags, PHY tunables, and module EEPROM access.

Control flow: ethtool callbacks translate userspace requests into `aq_nic_*`, `aq_hw_ops`, `aq_fw_ops`, PTP, MACsec, and filter helpers. Stats count and string generation are dynamic: base hardware stats plus per-queue/per-TC stats, optional PTP rings, and optional MACsec SC/SA stats. Ring parameter changes close/reopen the device when running. RSS updates write config then call hardware RSS programming. Coalescing accepts timing-based moderation and rejects unsupported frame-count combinations. Firmware-request operations such as LED, EEE, renegotiation, and flow control use `fwreq_mutex`.

State and persistence: modifies live `aq_nic_cfg_s` fields such as RSS key/table, interrupt moderation, WOL, EEE speeds, flow control, descriptor counts, msg level, private flags, and loopback settings. No disk persistence; settings last for device lifetime unless reapplied by upper layers.

Dependencies/integration: integrates with `aq_nic`, `aq_vec`, `aq_ptp`, `aq_filters`, `aq_macsec`, hardware and firmware ops, PCI, ethtool core, linkmode, and module EEPROM definitions.

Risks: dynamic stats counts must exactly match strings/data writers or userspace reads misalign. Some callbacks restart the interface and must preserve configuration. PTP TX/RX stats and MACsec stats are conditional on build/runtime state. Firmware/hardware EEPROM fallback must handle unsupported firmware cleanly. Private loopback allows only one loopback mode at a time and may restart for DMA network loopback.

Test signals: `ethtool -i/-S/-k/-K/-c/-C/-g/-G/-l/-n/-N/-x/-X/--show-eee/--set-eee`, WOL get/set, LED identify, PTP timestamp info, module EEPROM reads on fibre PHY, MACsec stats with active SAs, and running-interface ring/feature restart tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.h

Purpose: ethtool declarations and constants for Atlantic.

Important APIs/types: declares `extern const struct ethtool_ops aq_ethtool_ops`, defines private flag mask as Atlantic hardware loopback flags, and provides SFF-8472 I2C device/register constants used for optical module EEPROM detection and reads.

Control flow: none.

State and persistence: constants only.

Dependencies/integration: included by `aq_main.c` to attach ethtool ops and by `aq_ethtool.c` for EEPROM and private flag definitions.

Risks: private flag mask must track `aq_hw.h` loopback bit definitions. EEPROM constants must remain correct for SFF-8079/SFF-8472 module interpretation.

Test signals: compile, `ethtool --show-priv-flags`, loopback flag changes, and module info/eeprom reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.c

Purpose: implements RX classification filters for ethtool NFC and VLAN offload on Atlantic hardware.

Important APIs/types: uses `struct aq_rx_filter` hlist nodes from `aq_filters.h` and hardware filter tables in `aq_hw_rx_fltrs_s`. Public functions include count/get/add/delete/list/clear/reapply NFC rules, VLAN deletion by VID, VLAN filter update, and VLAN offload disable.

Control flow: add validates flow type, location, masks, queue action, duplicate matching, and feature enablement. Rules are classified as ethertype/L2, VLAN, or L3/L4. L2 rules program `hw_filter_l2_set/clear`; VLAN rules update the shared VLAN filter array and call `aq_filters_vlans_update()`; L3/L4 rules populate protocol/address/port commands and call hardware L3/L4 programming. The software hlist is kept ordered by location. Open and feature transitions reapply or clear rules. VLAN update rebuilds limited hardware slots so queue-assigned VLAN rules take precedence over plain active VLANs, toggles hardware VLAN filtering, and falls back to forced promiscuous behavior when active VLAN count exceeds hardware slots.

State and persistence: rules persist in memory across device stop/start via `aq_nic->aq_hw_rx_fltrs.filter_list` and are reapplied on open. Active VLAN bitmap is in `aq_nic->active_vlans`. No disk persistence.

Dependencies/integration: called by `aq_main.c` open, VLAN ndo operations, feature changes, and `aq_ethtool.c` RX NFC callbacks. Requires `aq_hw_ops` filter callbacks and queue/TC config from `aq_nic_cfg_s`.

Risks: L3/L4 hardware cannot mix IPv4 and IPv6 filters, and IPv6 locations are restricted to paired slots. VLAN table has only 16 entries and can enter forced-promiscuous mode. Rule insertion updates software before hardware programming and rolls back on hardware errors, so rollback correctness matters. Duplicate detection compares full specs except location.

Test signals: `ethtool -K ntuple on/off`, add/delete/list rules for ETHER/TCP/UDP/SCTP/IPv4/IPv6, duplicate and invalid-location rejection, VLAN add/kill under hardware slot pressure, interface reopen with rules, and hardware callback failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.h

Purpose: public RX filter interface for Atlantic.

Important APIs/types: defines `enum aq_rx_filter_type` for ethertype, VLAN, and L3/L4 filters; defines `struct aq_rx_filter` with hlist node, type, and saved `ethtool_rx_flow_spec`; declares all RX NFC and VLAN filter management functions.

Control flow: none in header.

State and persistence: `struct aq_rx_filter` is the in-memory persistence unit for ethtool rules across hardware resets/reopens.

Dependencies/integration: includes `aq_nic.h` for NIC structures; used by `aq_main.c` and `aq_ethtool.c`.

Risks: structure layout is internal but shared across filter implementation. API callers rely on add/delete/reapply functions to keep software and hardware state synchronized.

Test signals: compile and all ethtool NFC/VLAN paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw.h

Purpose: central hardware abstraction contract for Atlantic chips and firmware.

Important APIs/types: defines hardware capabilities (`struct aq_hw_caps_s`), link status, statistics, hardware flags, media types, queue/filter limits, loopback private flags, chip feature bits, live hardware object (`struct aq_hw_s`), `struct aq_hw_ops` for chip-specific operations, and `struct aq_fw_ops` for firmware-mediated operations.

Control flow: no implementations, but this file defines the dispatch tables used throughout the driver. `aq_hw_ops` covers ring TX/RX, MAC address, reset/start/stop, IRQ, filters, multicast, interrupt moderation, RSS, traffic class rate limits, stats/registers, offloads, PTP, flow control, loopback, temperature, and module EEPROM. `aq_fw_ops` covers firmware init/reset, MAC retrieval, link speed/state/status, stats, temperatures, flow control, LED, power, PTP, EEE, PHY tunables, MACsec requests, and module EEPROM.

State and persistence: `struct aq_hw_s` contains atomic flags, MMIO base, firmware ops, link status, mailbox/RPC state, stats snapshots, interrupt moderation, chip feature bits, PTP offset, PHY id, and private chip data. This is live runtime state only.

Dependencies/integration: consumed by nearly every Atlantic source file. Hardware generation files fill `aq_hw_ops`; firmware utility files fill `aq_fw_ops`; `aq_main`, `aq_ethtool`, `aq_filters`, `aq_hw_utils`, and `aq_macsec` call through these tables.

Risks: this is a broad ABI inside the driver; signature changes have wide impact. Optional callbacks require defensive NULL checks. Flag constants mix hardware and NIC-level readiness semantics via macros referencing NIC flags, so include ordering and meaning must be consistent. Filter location constants define user-visible ethtool rule ranges.

Test signals: full Atlantic build, probe across supported chip revisions, ring TX/RX, firmware operations, PTP/MACsec optional paths, filter programming, loopback modes, and error flag propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.c

Purpose: common low-level hardware helper functions for Atlantic MMIO access, bitfield updates, descriptor-cache invalidation, error mapping, and TC queue geometry.

Important APIs/types: implements `aq_hw_write_reg_bit()`, `aq_hw_read_reg_bit()`, `aq_hw_read_reg()`, `aq_hw_write_reg()`, 64-bit read/write helpers, `aq_hw_invalidate_descriptor_cache()`, `aq_hw_err_from_flags()`, `aq_hw_num_tcs()`, and `aq_hw_q_per_tc()`.

Control flow: register reads check for all-ones values and confirm against an alive-check register; if both are all ones, the device is marked unplugged. 64-bit access uses native `readq/writeq` when hardware supports 64-bit operations, otherwise lo/hi helpers. Descriptor cache invalidation triggers a hardware toggle then polls for completion. TC helpers translate configured TC mode into counts/queues.

State and persistence: mutates `aq_hw_s.flags` for unplug/hardware errors and writes MMIO registers. No persistent storage.

Dependencies/integration: called by chip-specific hardware layers and higher-level helpers. Depends on `aq_nic_cfg_s` capability data and `hw_atl_llh` low-level descriptor-cache functions.

Risks: all-ones MMIO detection is a common unplug signal but can misclassify if alive-check address is wrong. `aq_hw_write_reg_bit()` relies on masks/shifts supplied by generated low-level code. Descriptor-cache poll timeout return is not directly captured in the shown code, so callers mainly see existing flag-derived errors.

Test signals: MMIO read/write smoke tests, hot-unplug/error simulation, descriptor-cache invalidation after reset paths, TC mode setup for 1/4/8 TC configurations, and 32-bit vs 64-bit register access builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.h

Purpose: declarations and small utility macros for Atlantic hardware helpers.

Important APIs/types: defines `LODWORD`, `HIDWORD`, sleep/log macros, forward-declares `struct aq_hw_s`, and declares register access, bit access, descriptor-cache invalidation, error translation, and TC geometry helpers.

Control flow: none.

State and persistence: none.

Dependencies/integration: includes `linux/iopoll.h` and `aq_common.h`; used by hardware generation code and higher-level Atlantic files.

Risks: `AQ_HW_SLEEP(_US_)` maps to `mdelay`, so callers must avoid long delays in inappropriate contexts. Logging macros hardcode the driver name prefix.

Test signals: compile coverage, call-site timing review, and register helper tests through hardware operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.c

Purpose: hardware MACsec offload implementation for Atlantic, exposing Linux `macsec_ops` and programming the MACsec Security System records.

Important APIs/types: implements locked `macsec_ops` wrappers for SecY, TX/RX SC, TX/RX SA add/update/delete, device open/stop, and stats. Uses `struct aq_macsec_cfg`, `aq_macsec_txsc`, `aq_macsec_rxsc`, and MSS API record types. Public helpers initialize/free/enable MACsec, run periodic work, count active SAs/SCs, and append ethtool stats.

Control flow: init checks firmware link capabilities for MACsec, allocates config, enables `NETIF_F_HW_MACSEC`, and installs ops. Adding a SecY rejects XPN, selects SA/SC packing based on `MACSEC_NUM_AN`, allocates a TX SC slot, and programs egress class/SC records if carrier/running. TX/RX SA add stores keys in driver memory and writes SA/key records when active. RX SC setup programs two preclass records: SCI-present and SCI-absent matching. Delete/clear paths can clear hardware, software, or both. Enable optionally sends firmware MACsec config, installs PAE ethertype bypass records, then reapplies all saved SC/SA state. Work checks TX SA PN expiration and notifies macsec core. Stats read common, SC, and SA counters and update software next-PN fields.

State and persistence: MACsec state persists in memory in `nic->macsec_cfg` across link/device transitions and is reapplied by `aq_macsec_enable()`/device-open hooks. Keys are stored in per-SA arrays and zeroed in temporary hardware record buffers with `memzero_explicit`, but the persistent key copies remain until config is freed or overwritten. All ops are serialized by `macsec_mutex`.

Dependencies/integration: depends on `CONFIG_MACSEC`, Linux macsec core, `aq_nic`, firmware MACsec request op, and `macsec/macsec_api.c` MSS hardware programming. `aq_ethtool.c` uses its counters and stats writer.

Risks: key lifetime and memory clearing require care because persistent key arrays are not explicitly scrubbed on free. Hardware slot packing depends on `MACSEC_NUM_AN`; changes to MACsec core assumptions can affect SC/SA index math. Many hardware operations are gated on carrier/running, so deferred reapply paths must be correct. Stats functions dereference RCU-protected SA pointers and update PN under SA locks. Some helper return values are ignored in apply paths.

Test signals: builds with `CONFIG_MACSEC`, `ip macsec` add/update/delete for SecY/RXSC/TXSA/RXSA, link down/up reapply, hardware offload packet encryption/decryption, PAE bypass, PN wrap notification, ethtool MACsec stats count/string alignment, and key deletion/free memory review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.h

Purpose: MACsec offload declarations and state structures for Atlantic.

Important APIs/types: under `CONFIG_MACSEC`, defines maximum SC/SA counts, hardware SC/SA packing enum, common/RX-SA/TX-SA/TX-SC stats structures, `aq_macsec_txsc`, `aq_macsec_rxsc`, and `aq_macsec_cfg`. Declares `aq_macsec_ops` and init/free/enable/work/stat-count functions.

Control flow: header only.

State and persistence: `aq_macsec_cfg` is the in-memory state root: busy bitmaps, TX/RX SC arrays, per-SA key copies, software macsec object pointers, and cached counters.

Dependencies/integration: includes Linux `netdevice.h` and macsec core only when enabled; used by `aq_macsec.c`, `aq_ethtool.c`, and NIC lifecycle code.

Risks: fixed `AQ_MACSEC_MAX_SC` and `AQ_MACSEC_MAX_SA` define hardware/stat limits. Stored software pointers must remain valid under macsec core lifetime rules. Persistent key arrays need explicit lifecycle scrutiny.

Test signals: compile with MACsec on/off, ethtool stats with varying active SC/SA counts, and MACsec lifecycle operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.c

Purpose: main Atlantic Linux netdev module entry and `net_device_ops` implementation.

Important APIs/types: exports XDP static key `aq_xdp_locking_key`, workqueue scheduler `aq_ndev_schedule_work()`, netdev allocator `aq_ndev_alloc()`, open/close functions, and module init/exit. Defines `aq_ndev_ops` with open, stop, start_xmit, multicast, MTU, MAC address, features, VLAN, TC, BPF/XDP, XDP xmit, and hardware timestamp operations.

Control flow: module init creates a single-thread workqueue then registers PCI driver; exit unregisters PCI and destroys the workqueue. Allocation creates a multiqueue Ethernet netdev and attaches netdev/ethtool ops. Open initializes NIC, reapplies saved RX NFC rules, updates VLAN filters, then starts the NIC. Close stops and deinitializes. TX diverts PTP timestamped or PTP UDP/L2 traffic to PTP queues when PTP datapath is up, otherwise uses normal NIC transmit. Feature changes clear ntuple/VLAN rules when disabling features, update config, restart for LRO/VLAN strip/insert changes, and reprogram RX checksum offload. XDP setup enforces MTU constraints for non-frag XDP programs, disables LRO if needed, swaps BPF program, updates static key, and restarts if RX mode changes.

State and persistence: stores runtime config in `aq_nic_s`/`aq_nic_cfg_s`, active VLAN bitmap, XDP program pointer, workqueue, and netdev features. State persists only across netdev close/open inside driver memory.

Dependencies/integration: coordinates `aq_nic`, PCI registration, ethtool ops, PTP, filters, hardware utilities, vector/XDP code, Linux TC mqprio, hwtstamp, and BPF APIs.

Risks: `aq_ndev_start_xmit()` inspects IP/UDP headers for PTP without visible skb protocol/linearization checks in this file, relying on stack assumptions. Feature restarts call close/open and must handle errors without leaving stale config. XDP program swaps require correct refcount/static-branch handling. VLAN kill path has special `-ENOENT` handling to update plain VLAN filters.

Test signals: module load/unload, PCI probe through dependent code, open/close error unwind, PTP traffic transmit, MTU/XDP constraints, feature toggles, VLAN add/kill, mqprio TC setup with max/min rates, hwtstamp get/set, and XDP attach/detach/xmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.h

Purpose: main Atlantic netdev interface declarations.

Important APIs/types: includes common/NIC headers, declares static key `aq_xdp_locking_key`, and exposes work scheduling, netdev allocation, open, and close functions.

Control flow: none.

State and persistence: declaration of `aq_xdp_locking_key` represents global runtime branch state controlled by XDP attach/detach in `aq_main.c`.

Dependencies/integration: used by Atlantic files needing open/close or work scheduling, and by XDP/ring paths checking the static key.

Risks: global static key must be incremented/decremented in balanced fashion or XDP locking behavior can be wrong across devices.

Test signals: compile, XDP attach/detach across multiple devices, and workqueue scheduling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.h -->
