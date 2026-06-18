# Research: subset-b-004334

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/starfire.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/starfire.c

Purpose: this is the PCI netdev driver for the Adaptec Starfire 6915 Fast Ethernet adapter. It owns PCI probing, EEPROM MAC address discovery, MMIO register setup, firmware loading into the adapter frame processors, descriptor/completion-ring DMA, NAPI receive processing, MII/ethtool control, VLAN filtering, hardware checksum/scatter-gather support, and suspend/resume/remove lifecycle.

Important APIs, types, and functions: `struct netdev_private` is the private state for one adapter: coherent queue memory, RX/TX descriptor rings, completion queues, NAPI object, PCI/MMIO handles, spinlock, ring cursors, MII state, VLAN bitmap, interrupt-timer state, and TX threshold. Hardware layout is captured by `enum register_offsets`, interrupt/filter/DMA/descriptor bit enums, `struct starfire_rx_desc`, `rx_done_desc`, `starfire_tx_desc`, and `struct tx_done_desc`. The driver registers `netdev_ops`, `ethtool_ops`, `starfire_driver`, and module parameters such as `max_interrupt_work`, `rx_copybreak`, `intr_latency`, `small_frames`, `mtu`, and `enable_hw_cksum`. Core routines are `starfire_init_one()`, `netdev_open()`, `init_ring()`, `start_tx()`, `intr_handler()`, `__netdev_rx()`, `netdev_poll()`, `refill_rx_ring()`, `netdev_media_change()`, `netdev_error()`, `set_rx_mode()`, `netdev_ioctl()`, `netdev_close()`, `starfire_suspend()`, `starfire_resume()`, and `starfire_remove_one()`.

Control flow: PCI probe enables the device, validates BAR0 memory resources, allocates an Ethernet netdev, requests regions, ioremaps MMIO, enables bus mastering/MWI, advertises checksum, scatter-gather, VLAN, and high-DMA features as configured, reads the station address from EEPROM shadow registers, soft-resets the MII/TX mode and chip, initializes private state and MII callbacks, computes interrupt coalescing settings, installs netdev/NAPI/ethtool hooks, registers the netdev, then scans up to two MII PHYs. Open requests the shared IRQ, stops/resets the chip, lazily allocates one coherent block for TX completion queue, RX completion queue, TX ring, and RX ring, initializes rings and RX buffers, writes DMA/ring/completion register addresses including high-address registers, programs station/perfect-filter entries, programs TX mode, threshold and interrupt timer, enables NAPI and queueing, applies RX/VLAN/multicast filter state, negotiates PHY duplex, enables GPIO link-change and PCI interrupts, sets the VLAN ethertype, loads `adaptec/starfire_rx.bin` and `adaptec/starfire_tx.bin`, writes firmware words into GFP memory windows, and finally enables RX/TX plus GFP engines when hardware checksum is enabled. TX maps the skb linear area and fragments into descriptors, handles ring wrap with `TxRingWrap`, optionally requests TX completion interrupts periodically, pads checksum-partial frames for broken firmware, writes producer index after a memory barrier, and stops the queue near ring exhaustion. IRQ handling reads `IntrClear`, schedules NAPI for RX events while masking RX IRQs, consumes TX completion queue entries, unmaps DMA and frees skbs, wakes the queue when space returns, pulls hardware stats on overflow, handles link changes, and dispatches abnormal events. NAPI clears RX interrupts, drains RX completion descriptors up to budget, either copies short frames or hands mapped skb storage up, marks hardware checksums and VLAN tags, advances completion consumer index, refills missing RX descriptors, completes NAPI, and reenables RX IRQs when quiescent. Close disables queueing/NAPI/interrupts/RX/TX, frees IRQ, unmaps and frees all outstanding RX/TX skbs, but leaves the coherent queue block for reuse until remove.

State and persistence: durable software state is per-device private data plus module parameters. The coherent descriptor/completion memory persists across down/up cycles and is freed only in remove. Ring cursors (`cur_rx`, `dirty_rx`, `rx_done`, `cur_tx`, `dirty_tx`, `reap_tx`, `tx_done`) track producer/consumer progress across open sessions after `init_ring()` resets them. Link state is kept in `mii_if`, `speed100`, `full_duplex`, `tx_mode`, and carrier state. VLAN state persists in `active_vlans` and is materialized into hardware filter slots by `set_rx_mode()`. Hardware counters are read into `dev->stats`, with `rx_dropped` accumulated from `RxDMAStatus`. Suspend detaches and closes only when the interface is running; resume reopens and reattaches. Remove unregisters the netdev, frees coherent memory, puts PCI device in D3hot, unmaps MMIO, releases PCI regions, and frees the netdev.

Dependencies and integration points: the file depends on PCI, netdevice/etherdevice, DMA mapping, firmware loader, NAPI, MII library, ethtool link settings, VLAN acceleration, CRC32 multicast hashing, and direct MMIO accessors. It binds PCI vendor/device `ADAPTEC:0x6915` and requires external firmware blobs named by `MODULE_FIRMWARE`. The MII callbacks are used by generic MII ioctl and ethtool paths. VLAN add/kill hooks update the driver bitmap and RX filter programming. Power management is through `SIMPLE_DEV_PM_OPS`.

Risks: open depends on firmware availability and 4-byte-aligned firmware lengths; missing firmware causes `netdev_close()` after partial initialization. The driver assumes a PHY exists in several open paths (`np->phys[0]`), so probe-time PHY discovery failures are risky if the interface can still be opened. Hardware checksum behavior is guarded by comments about broken firmware and IP-fragment checksum issues. TX mapping error rollback is manual and complex around wrapped/multi-fragment descriptors. Coherent queue memory is reused across opens, while skb mappings are recreated, so close/open ordering and timeout recovery must remain correct. IRQ/NAPI masking relies on MMIO posting flushes and shared-IRQ status checks. Some error paths return generic `-ENODEV`, making diagnosis coarse. The driver uses legacy `dev->stats` and debug globals, and `tx_timeout()` restarts the interface by closing and reopening it in watchdog context.

Test signals: useful validation is successful PCI probe with a valid EEPROM MAC, MII PHY discovery and ethtool link-setting changes, firmware load and GFP engine enable, RX/TX traffic with and without `enable_hw_cksum`, fragmented checksum-partial TX, VLAN tag receive/filter add/remove, multicast perfect-filter versus hash-filter behavior, NAPI budgeted RX under interrupt load, TX completion unmapping and queue wakeups, link-change interrupt handling, stats overflow handling, watchdog timeout recovery, suspend/resume while running, and remove freeing DMA memory without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/starfire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Kconfig

Purpose: this Kconfig fragment introduces the Analog Devices Ethernet vendor menu and the ADIN1110/ADIN2111 MAC-PHY driver option. It controls whether the ADI subtree appears in networking driver configuration and whether `adin1110.c` can be built.

Important APIs, types, and functions: the relevant symbols are `NET_VENDOR_ADI` and `ADIN1110`. `NET_VENDOR_ADI` is a boolean vendor gate, defaults to `y`, and depends on `SPI`. `ADIN1110` is a tristate prompt for "Analog Devices ADIN1110 MAC-PHY", depends on `SPI && NET_SWITCHDEV`, and selects `CRC8` and `PHYLIB`.

Control flow: Kconfig first offers the vendor gate. If `NET_VENDOR_ADI` is enabled, the nested `ADIN1110` option becomes visible. Selecting the driver as built-in or module causes the matching Makefile to include `adin1110.o` through `CONFIG_ADIN1110`.

State and persistence: there is no runtime state. Persistence is the kernel build configuration recorded in `.config`, which determines whether ADI questions are skipped and whether the driver is omitted, built in, or built as a module.

Dependencies and integration points: the file integrates with the kernel networking drivers Kconfig hierarchy. Its dependency on `SPI` reflects the MAC-PHY transport, `NET_SWITCHDEV` reflects the driver's bridge/FDB offload hooks, `CRC8` supports optional SPI/data CRC handling, and `PHYLIB` supports the internal ADIN1100 PHY instances exposed through an MDIO bus.

Risks: the vendor gate depends on `SPI`, so all ADI Ethernet options are hidden on builds without SPI even if a future ADI Ethernet driver did not use SPI. `ADIN1110` selects switchdev and phylib dependencies indirectly but does not express OF/GPIO/regulator dependencies because those are optional or provided by broader kernel APIs. Configuration testing should verify module builds when `NET_SWITCHDEV` is available.

Test signals: expected signals are `CONFIG_NET_VENDOR_ADI=y` making the vendor menu visible, `CONFIG_ADIN1110=m` producing `adin1110.ko`, successful dependency resolution for `CRC8` and `PHYLIB`, and absence of the option when `SPI` or `NET_SWITCHDEV` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Makefile

Purpose: this Makefile connects the Analog Devices Ethernet Kconfig symbol to the actual driver object.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_ADIN1110) += adin1110.o`, which lets kbuild include the ADIN1110 driver when the symbol is built-in or modular.

Control flow: when `CONFIG_ADIN1110=y`, `adin1110.o` is linked into the kernel image through the networking driver build. When `CONFIG_ADIN1110=m`, kbuild emits it as a module. When unset, no object in this directory is built.

State and persistence: there is no runtime state. The persistent effect is entirely in the build graph selected by `.config`.

Dependencies and integration points: it depends on the surrounding kbuild infrastructure and the `ADIN1110` symbol declared in the same directory's Kconfig. It keeps the source-tree mapping direct: `adin1110.c` compiles to `adin1110.o`.

Risks: no conditional subdirectories or composite objects exist, so the main risks are stale symbol names or missing Kconfig inclusion from the parent directory. A rename of the C file or symbol must update this line.

Test signals: `make drivers/net/ethernet/adi/` or a full kernel build should compile `adin1110.o` only when `CONFIG_ADIN1110` is enabled, and `modinfo adin1110.ko` should expose the metadata from `adin1110.c` in modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/adin1110.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/adin1110.c

Purpose: this is the SPI network driver for Analog Devices ADIN1110 single-port 10BASE-T1L MAC-PHY and ADIN2111 two-port MAC-PHY switch. It implements register/FIFO SPI framing with optional CRC, exposes internal ADIN1100 PHYs through a synthetic MDIO bus, creates one netdev per port, handles TX/RX through workqueues and a threaded IRQ, and integrates ADIN2111 bridge offload with switchdev, STP state, and small hardware FDB slots.

Important APIs, types, and functions: `struct adin1110_cfg` distinguishes ADIN1110 from ADIN2111 by port count and expected PHY ID. `struct adin1110_priv` stores the SPI device, SPI serialization mutex, RX-mode spinlock, mii bus, append-CRC flag, chip config, TX FIFO space, IRQ mask, forwarding flag, per-port pointers, and a cacheline-aligned 2048-byte transfer buffer. `struct adin1110_port_priv` stores a port netdev, bridge pointer, PHY device, TX/RX-mode work items, stats counters, TX queue, port number, STP state, and config pointer. Register I/O is handled by `adin1110_read_reg()`, `adin1110_write_reg()`, `adin1110_set_bits()`, `adin1110_read_fifo()`, and `adin1110_write_fifo()`. Network integration is through `adin1110_netdev_ops`, `adin1110_ethtool_ops`, `adin1110_net_open()`, `adin1110_net_stop()`, `adin1110_start_xmit()`, `adin1110_tx_work()`, `adin1110_irq()`, and stats/port-name helpers. PHY/MDIO integration is through `adin1110_register_mdiobus()`, `adin1110_mdio_read()`, `adin1110_mdio_write()`, and `phy_connect()`. Switchdev integration is through `adin1110_netdevice_nb`, `adin1110_switchdev_notifier`, `adin1110_switchdev_blocking_notifier`, bridge join/leave helpers, STP state helpers, and FDB add/delete worker functions.

Control flow: module init first registers netdevice and switchdev notifiers, then registers the SPI driver; init rollback unregisters notifiers if SPI registration fails. Probe allocates private state, selects chip config from SPI ID driver data, forces 8-bit SPI mode 0, initializes locks, enables CRC8 handling when `adi,spi-crc` is present, optionally toggles a reset GPIO under SPI bus lock, waits for hardware reset completion, verifies the MAC-side PHY ID register, writes a software reset, registers an MDIO bus that proxies Clause 22 accesses through `ADIN1110_MDIOACC`, then creates port netdevs. Netdev creation reads the port MAC address from device properties, initializes work items and skb TX queue, configures immutable netns, PHY interface, carrier-off state, `IFF_UNICAST_FLT`, and connects each internal PHY by address. A threaded low-level IRQ is requested once and each port netdev is registered. Opening a port locks SPI, configures MAC FCS append, enables TX-ready/RX-ready/SPI-error interrupt sources by writing inverted `IMASK1`, reads TX space, sets default forwarding STP state, installs the unicast MAC slot, syncs `CONFIG1`, starts the PHY, and starts the queue. TX checks cached FIFO space, stops the queue and returns busy if insufficient, otherwise deducts needed space, enqueues the skb, and schedules `tx_work`; the worker serializes on the SPI mutex, writes frame size, constructs a SPI write frame with an internal port header, pads to Ethernet minimum size and 4-byte FIFO alignment, writes the FIFO, updates software stats, and frees skbs. The threaded IRQ serializes SPI, reads `STATUS1`, warns on SPI CRC write errors, refreshes `tx_space` from half-word units, drains up to 64 frames per ready port by reading frame-size registers and FIFO data, clears status sources, unmasks by writing status bits, unlocks, then wakes all queues if TX space is available. RX allocates an skb sized for rounded FIFO data plus header, performs SPI full-duplex read, strips SPI and internal frame headers, assigns protocol, marks switch-forwarded multicast/broadcast frames when forwarding is active, calls `netif_rx()`, and updates counters.

State and persistence: persistent per-chip state includes optional CRC mode, cached TX space, current IRQ mask, forwarding enablement, registered notifiers, mii bus identity, per-port bridge membership, STP state, RX flags copied from netdev flags, and software packet/byte counters. Hardware persistent state includes `CONFIG1/CONFIG2`, MAC filter slots and masks, interrupt masks/status, cut-through forwarding, and the hardware FDB slots from `ADIN_MAC_FDB_ADDR_SLOT` through `ADIN_MAC_MAX_ADDR_SLOTS - 1`. The SPI transfer buffer is shared for all register/FIFO operations and protected by `priv->lock`; RX-mode flags are captured under `state_lock` and applied asynchronously under the SPI mutex. Devm resources own netdevs, IRQ, MDIO bus, and PHY disconnect actions. Module exit unregisters notifiers and the SPI driver.

Dependencies and integration points: the driver depends on SPI core, optional reset GPIO, device properties/OF IDs `adi,adin1110` and `adi,adin2111`, CRC8, unaligned big-endian helpers, PHYLIB, MII bus APIs, ethtool PHY link settings, netdevice APIs, workqueues, threaded IRQs, and switchdev/bridge notifier APIs. The internal PHYs are discovered through the driver's MDIO bus and connected with `PHY_INTERFACE_MODE_INTERNAL`. Bridge integration listens for `NETDEV_CHANGEUPPER`, switchdev FDB add/delete events, and blocking STP attribute changes; ADIN2111 hardware forwarding is enabled only when both ports are in the same bridge and both are forwarding.

Risks: the SPI transfer buffer is shared and correctness depends on every register/FIFO path holding the mutex, including helper paths reached from IRQ, workqueues, MDIO, and switchdev. `adin1110_start_xmit()` checks and decrements `tx_space` without taking the SPI mutex, so queue-stop/wake behavior depends on IRQ refreshes and serialized workqueue drainage rather than exact hardware reservation. The stop path disables RX IRQs with a port-dependent mask expression that is easy to audit carefully because port 0 and port 1 use different ready bits. FDB hardware space is small and linear-scanned, with no VID distinction in hardware programming beyond switchdev metadata. Bridge offload is deliberately disabled for STP blocking states, allowing only BPDUs by rewriting the port MAC slot. Optional CRC mode must match hardware pin configuration; mismatches surface as register read/write failures or SPI error warnings. RX uses `netif_rx()` from threaded IRQ context and does not use NAPI, so burst behavior is constrained by `ADIN1110_MAX_FRAMES_READ` and threaded IRQ scheduling. Probe relies on SPI IDs for `driver_data`; OF-only matching must still result in a usable SPI device ID path.

Test signals: validate probe for both compatible/ID pairs, optional `adi,spi-crc` operation, reset GPIO timing, PHY ID verification, MDIO read/write polling, PHY connection at addresses 1 and 2, per-port netdev registration and immutable namespace behavior, open/stop interrupt-mask transitions, TX FIFO busy and queue wakeup behavior, RX frame parsing and FCS/header stripping, multicast/broadcast/promisc filter programming, netdev stats64 counters, bridge join/leave, STP blocking versus forwarding transitions, cut-through forwarding enablement on ADIN2111, FDB add/delete/offload notification, and module unload unregistering all notifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/adin1110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Kconfig

Purpose: this Kconfig fragment exposes the Aeroflex Gaisler GRETH Ethernet MAC driver option.

Important APIs, types, and functions: the relevant symbol is `GRETH`, a tristate prompt for "Aeroflex Gaisler GRETH Ethernet MAC support". It depends on `SPARC` and selects `PHYLIB` and `CRC32`.

Control flow: when the architecture is SPARC, the user may choose `GRETH` as built-in, module, or disabled. The matching Makefile uses `CONFIG_GRETH` to build `greth.o`.

State and persistence: there is no runtime state. Persistent behavior is the kernel `.config` selection that controls whether the platform driver is compiled.

Dependencies and integration points: `SPARC` reflects the primary GRLIB/LEON deployment environment and the driver's use of SPARC-specific platform/IDPROM details. `PHYLIB` supports MDIO/PHY integration, and `CRC32` supports multicast hash filtering in the driver.

Risks: the hard `SPARC` dependency prevents test builds on other architectures even though much of the driver is generic platform/netdev code. Any future non-SPARC GRETH deployment would need Kconfig loosening plus audit of `ofdev->archdata.irqs` and IDPROM fallback usage.

Test signals: expected signals are menu visibility only on SPARC, `CONFIG_GRETH=m` producing `greth.ko`, automatic selection of PHYLIB/CRC32, and a clean build of `greth.c` with the selected architecture headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Makefile

Purpose: this Makefile connects the GRETH Kconfig symbol to the GRETH driver object.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_GRETH) += greth.o`.

Control flow: kbuild links `greth.o` into vmlinux for `CONFIG_GRETH=y`, builds `greth.ko` for `CONFIG_GRETH=m`, and skips it when unset.

State and persistence: there is no runtime state. The persistent output is the build artifact selected by `.config`.

Dependencies and integration points: it integrates with the parent networking driver kbuild tree and with `aeroflex/Kconfig`. The object name directly corresponds to `greth.c` and its local header `greth.h`.

Risks: the file is intentionally minimal. The main maintenance risk is symbol/object drift if the driver or Kconfig symbol is renamed.

Test signals: enabling `CONFIG_GRETH` should compile `drivers/net/ethernet/aeroflex/greth.o`, and modular builds should produce module metadata from `greth.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/greth.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/greth.c

Purpose: this is the platform netdev driver for Aeroflex Gaisler GRETH 10/100 and 10/100/1G Ethernet MAC IP from GRLIB. It handles OF platform probing, big-endian APB register and descriptor access, MDIO/PHY attachment, NAPI interrupt mitigation, descriptor-ring DMA, separate 10/100 copy-buffer and gigabit scatter-gather paths, multicast filtering, checksum offload, ethtool register/link operations, and cleanup.

Important APIs, types, and functions: the driver uses `struct greth_private`, `struct greth_regs`, and `struct greth_bd` from `greth.h`. Register access is wrapped in `GRETH_REGLOAD`, `GRETH_REGSAVE`, `GRETH_REGORIN`, and `GRETH_REGANDIN`; descriptors use `greth_read_bd()` and `greth_write_bd()`. Core paths are `greth_of_probe()`, `greth_open()`, `greth_close()`, `greth_init_rings()`, `greth_clean_rings()`, `greth_start_xmit()` for 10/100, `greth_start_xmit_gbit()` for gigabit, `greth_interrupt()`, `greth_poll()`, `greth_rx()`, `greth_rx_gbit()`, `greth_clean_tx()`, `greth_clean_tx_gbit()`, `greth_set_mac_add()`, `greth_set_multicast_list()`, `greth_mdio_init()`, `greth_mdio_read()`, `greth_mdio_write()`, `greth_mdio_probe()`, `greth_link_change()`, `greth_of_remove()`, and the ethtool helpers. Module parameters are `greth_debug`, `macaddr`, and `greth_edcl`.

Control flow: platform probe allocates an Ethernet netdev, initializes message level and spinlock, maps the APB register resource with `of_ioremap()`, records the IRQ from OF archdata, resets the controller and waits up to 10 ms for reset deassertion, samples hardware capability bits for PHY address, gigabit, multicast, EDCL, and MDIO interrupt support, disables EDCL speed/duplex FSM if present, initializes and registers an MDIO bus, attaches the first discovered PHY, optionally starts autoneg immediately for EDCL, allocates coherent TX and RX descriptor rings, selects a MAC address from module parameter, OF property, or SPARC IDPROM fallback, writes ESA registers, clears interrupts, enables SG/IP checksum/RX checksum/HIGHDMA features and the gigabit TX routine when the hardware advertises gigabit, enables multicast callbacks if supported, installs netdev/ethtool operations, registers the netdev, and adds NAPI. Open allocates and maps RX/TX buffers through `greth_init_rings()`, requests the IRQ, starts the queue, clears status, enables NAPI, IRQs, TX, and RX. IRQ handling checks both status and interrupt-enable bits, disables IRQs under `devlock`, and schedules NAPI. Poll cleans TX and receives packets through the gigabit or 10/100 path, then reenables RX IRQ alone or RX+TX IRQ depending on pending TX cleanup needs; if status races with reenable, it restarts polling before completing NAPI.

State and persistence: runtime state is kept in ring arrays, skb pointers, fixed-buffer pointers, DMA addresses, descriptor indices (`tx_next`, `tx_last`, `tx_free`, `rx_cur`), PHY link/speed/duplex, capability flags, and netdev stats. The 10/100 path allocates fixed kmalloc buffers for each RX and TX descriptor and copies TX/RX payloads between skbs and DMA buffers. The gigabit path maps skb linear data and fragments directly for TX and swaps in a newly allocated RX skb for each received frame. Descriptor rings are coherent and persist from probe to remove, while packet buffers are allocated on open and freed on close. Link-change state is updated from PHY callbacks under `devlock` and written into GRETH control bits. Remove frees coherent descriptor rings, stops PHY if attached, unregisters MDIO and netdev, unmaps registers, and frees the netdev.

Dependencies and integration points: the file depends on OF platform devices, SPARC archdata/IDPROM fallback, DMA mapping, PHYLIB/MDIO bus APIs, ethtool, NAPI, netdevice, CRC32 multicast hashing, endian conversion, and GRLIB GRETH register semantics. OF matching uses legacy names `"GAISLER_ETHMAC"` and `"01_01d"`. The driver exposes register dumps through ethtool and defers link mode control to PHYLIB. Hardware offloads are advertised only for gigabit-capable MACs.

Risks: `greth_netdev_ops` is a global mutable structure whose `.ndo_start_xmit` and `.ndo_set_rx_mode` are changed during probe based on one device's capabilities; mixed GRETH devices with different capabilities could interfere. The driver uses `ofdev->archdata.irqs[0]` instead of the more generic platform IRQ helpers, reinforcing the SPARC coupling. The 10/100 path uses descriptor physical addresses with `phys_to_virt()` after DMA mapping fixed buffers, which is architecture-sensitive. Gigabit fragment mapping error cleanup walks descriptors with simple arithmetic and may be fragile around ring wrap. MDIO wait uses jiffies polling without sleeps and returns `-1` for invalid reads. EDCL autoneg waits in a busy loop for up to six seconds. NAPI setup happens after `register_netdev()`, while most drivers add NAPI before registration. Error paths free rings and MDIO but do not always mirror every normal-remove step, so probe failure coverage matters.

Test signals: validate OF probe/reset, register mapping and IRQ delivery, MDIO register access and PHY attach, EDCL autoneg behavior, link speed/duplex writes for 10/100/1000, open/close buffer allocation cleanup, 10/100 copy TX/RX traffic, gigabit SG TX with fragments and checksum offload, RX checksum marking, multicast hash and allmulti/promisc modes, NAPI completion/race restart behavior, TX queue stop/wake under ring pressure, ethtool register dumps, invalid MAC rejection/fallback, and remove/unload without DMA or MDIO leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/greth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/greth.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/greth.h

Purpose: this header defines the GRETH hardware contract used by `greth.c`: register bits, descriptor flags, ring sizes, buffer sizing, APB register layout, buffer descriptor layout, and the driver's private per-device state structure.

Important APIs, types, and functions: the register/descriptor constants include reset/MDIO flags (`GRETH_RESET`, `GRETH_MII_BUSY`, `GRETH_MII_NVALID`), control bits (`GRETH_CTRL_FD`, `GRETH_CTRL_PR`, `GRETH_CTRL_SP`, `GRETH_CTRL_GB`, `GRETH_CTRL_MCEN`, `GRETH_CTRL_DISDUPLEX`), TX/RX descriptor ownership/wrap/interrupt/length bits, TX and RX error/status bits, checksum status bits, ring counts (`GRETH_TXBD_NUM`, `GRETH_RXBD_NUM`), and buffer sizes (`GRETH_TX_BUF_SIZE`, `GRETH_RX_BUF_SIZE`, `MAX_FRAME_SIZE`). `struct greth_regs` models the APB register block, `struct greth_bd` models each descriptor, and `struct greth_private` is the netdev private state shared across probe, open, IRQ/NAPI, TX/RX, PHY, and remove paths.

Control flow: the header itself has no executable control flow. Its constants drive `greth.c` decisions about enabling TX/RX/IRQs, wrapping descriptor rings, checking completion/error bits, computing multicast hashes, exposing hardware capabilities, and selecting 10/100 versus gigabit behavior.

State and persistence: `struct greth_private` defines persistent runtime state: RX/TX skb arrays, fixed DMA buffer arrays and lengths, ring indices, mapped register pointer, coherent descriptor ring pointers and DMA addresses, IRQ, device/netdev pointers, NAPI, spinlock, MDIO bus, PHY link state, message mask, PHY address, and capability flags for multicast, gigabit, MDIO interrupts, and EDCL. The descriptor and register structs define the in-memory/MMIO state exchanged with hardware.

Dependencies and integration points: the header includes `<linux/phy.h>` for PHY-related types used by private state and relies on PAGE_SIZE for buffer-page macros. It is local to the Aeroflex driver and is included by `greth.c`; no exported kernel API is declared.

Risks: descriptor counts and coherent ring allocation sizes in `greth.c` assume `GRETH_TXBD_NUM` and `GRETH_RXBD_NUM` of 128 with 8-byte descriptors; changing these constants requires auditing allocation sizes. The buffer-per-page macros contain the misspelled `PPGAE` name and are not actively used by `greth.c`. `MAX_FRAME_SIZE` is fixed at 1520, so jumbo frame support is absent despite gigabit support. The private structure mixes 10/100 fixed buffers and gigabit skb mappings, so callers must branch consistently on `gbit_mac`.

Test signals: compile-time users should include this header without duplicate definitions, descriptor constants should match GRLIB GRETH documentation, ring wrap should occur at descriptor 127, `sizeof(struct greth_regs)` should match ethtool register dump expectations, and `struct greth_private` fields should be initialized by probe/open before IRQ, NAPI, or PHY callbacks use them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/greth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Kconfig

Purpose: this Kconfig fragment introduces the Agere Ethernet vendor menu and the ET-1310 Gigabit Ethernet driver option.

Important APIs, types, and functions: the relevant symbols are `NET_VENDOR_AGERE` and `ET131X`. `NET_VENDOR_AGERE` is a boolean vendor gate, defaults to `y`, and depends on `PCI`. `ET131X` is a tristate prompt for "Agere ET-1310 Gigabit Ethernet support", depends on `PCI`, and selects `PHYLIB` and `CRC32`.

Control flow: enabling the vendor gate makes the ET131X prompt visible. Selecting `ET131X` controls whether the companion Makefile builds `et131x.o` built-in or as a module.

State and persistence: there is no runtime state. The persistent artifact is the kernel build configuration selecting or omitting the Agere driver.

Dependencies and integration points: `PCI` reflects the ET-1310 adapter bus, `PHYLIB` supports PHY management in the driver, and `CRC32` supports Ethernet CRC/hash-style filtering logic. The help text names the module `et131x`.

Risks: the vendor gate hides all Agere options when PCI is disabled, which is appropriate for the present driver but should be revisited if non-PCI Agere devices are added. Configuration drift between the `ET131X` symbol, Makefile object name, and help text would break builds or user expectations.

Test signals: `CONFIG_NET_VENDOR_AGERE=y` should expose the ET131X prompt on PCI-capable builds, `CONFIG_ET131X=m` should produce `et131x.ko`, selected dependencies should be set, and the option should disappear when PCI support is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Makefile

Purpose: this Makefile connects the Agere ET-131x Kconfig symbol to the driver object.

Important APIs, types, and functions: the sole rule is `obj-$(CONFIG_ET131X) += et131x.o`.

Control flow: kbuild links or modules `et131x.o` according to `CONFIG_ET131X`, and excludes it when the symbol is unset.

State and persistence: there is no runtime state. The persistent effect is the build artifact selected by kernel configuration.

Dependencies and integration points: it integrates with `agere/Kconfig` and the parent networking driver Makefiles. It assumes the ET-131x implementation is in `et131x.c` in the same directory.

Risks: the file is minimal; the main risk is symbol/object mismatch if the driver is renamed or split into multiple objects without updating kbuild.

Test signals: enabling `CONFIG_ET131X` should compile `drivers/net/ethernet/agere/et131x.o`; modular builds should emit `et131x.ko` as promised by the Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Makefile -->
