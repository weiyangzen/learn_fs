# subset-b-004339 research

Grouped research report for the requested AMD Ethernet driver files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/a2065.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/a2065.c

Purpose: implements the Commodore/Ameristar A2065 Amiga Zorro-II Ethernet driver for an Am7990 LANCE controller. It registers as a Zorro driver, exposes a `net_device`, manages the A2065 shared RAM layout for initialization, RX and TX rings, and handles the shared Amiga ports IRQ.

Important APIs and functions: module lifecycle is `a2065_init_module`/`a2065_cleanup_module` around `zorro_register_driver`. Device lifecycle is `a2065_init_one` and `a2065_remove_one`. Netdev operations are `lance_open`, `lance_close`, `lance_start_xmit`, `lance_tx_timeout`, `lance_set_multicast`, address validation, and `eth_mac_addr`. Hardware helpers include `load_csrs`, `lance_init_ring`, `init_restart_lance`, `lance_rx`, `lance_tx`, `lance_reset`, `lance_tx_buffs_avail`, `lance_load_multicast`, and the multicast retry timer callback.

Control flow: probe reserves the LANCE register window and A2065 RAM window, allocates an Ethernet device, derives the MAC address from the Zorro ROM serial and vendor prefix, maps CPU-visible Zorro addresses, initializes private ring parameters and a multicast retry timer, and registers the netdev. Opening stops the controller, requests `IRQ_AMIGA_PORTS` shared with other Amiga port users, loads the CSR init-block address and CSR3 busmaster value, initializes descriptor rings, starts the queue, then issues LANCE INIT and START. RX interrupts acknowledge RINT, scan descriptors until the chip owns the next one, validate start/end/error bits, copy completed frames into skbs, update stats, and return descriptors to the chip. TX interrupts scan from `tx_old` to `tx_new`, reclaim descriptors, update errors/collisions, restart on carrier-loss auto-select, buffer, or underflow failures, and wake the queue when slots become free. Transmit pads to Ethernet minimum, copies skb data into board RAM, marks one TX descriptor owned by the chip, advances the producer index, possibly stops the queue, and kicks TDMD. Multicast changes stop and reinitialize the chip if no TX is pending; otherwise a short timer retries.

State and persistence: persistent software state is `struct lance_private`, including CPU and LANCE views of the init block, ring indexes, ring-size masks, CSR3 busmaster value, and the multicast timer. Packet buffers and descriptors live in the A2065 RAM window and are reinitialized on open, reset, multicast changes, and selected TX faults. The driver does not persist state beyond module lifetime; MAC address is reconstructed from Zorro ROM serial on probe.

Dependencies and integration points: depends on Linux netdevice, Ethernet helpers, skbuff, crc32 multicast hashing, Zorro bus APIs, Amiga interrupt and Zorro-II address macros, and local LANCE register definitions from `a2065.h`. It integrates with the networking stack through `register_netdev`, with Zorro autoloading through `MODULE_DEVICE_TABLE(zorro, ...)`, and with the hardware through MMIO-style volatile accesses to A2065 board registers and RAM.

Risks: `lance_init_ring` iterates TX entries with `i <= 1 << lp->lance_log_tx_bufs`, which writes one descriptor/buffer past the nominal TX ring size. Error and reset paths rebuild rings while packet state is in flight, which can drop queued packets. The driver uses volatile MMIO and local IRQ disabling rather than modern DMA mapping or lock primitives. Multicast updates require stopping the chip and may repeatedly defer while TX is active. The shared Amiga ports IRQ requires strict IRQ source filtering. Address conversion through `LANCE_ADDR((int)x)` is platform-specific and assumes 24-bit board-visible addresses.

Test signals: build coverage for Amiga/Zorro configurations, probe/remove on Commodore and Ameristar A2065 IDs, open/close IRQ request handling, packet RX/TX under load, TX timeout reset recovery, multicast/promiscuous mode transitions, and carrier/buffer/underflow error handling. Static analysis should flag the TX ring initialization bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/a2065.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/a2065.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/a2065.h

Purpose: provides A2065-specific LANCE register, descriptor, flag, and board-memory layout definitions consumed by `a2065.c`.

Important APIs and types: defines `struct lance_regs`, LANCE CSRs `LE_CSR0` through `LE_CSR3`, CSR0/CSR3 bit masks, mode flags, `struct lance_rx_desc`, `struct lance_tx_desc`, RX/TX descriptor flags and error flags, and the A2065 board offsets `A2065_LANCE`, `A2065_RAM`, and `A2065_RAM_SIZE`.

Control flow: no executable control flow. The C file uses these constants to program CSR addresses/data, build descriptor rings, interpret interrupt and descriptor status bits, and reserve/map the LANCE register and board RAM windows during Zorro probe.

State and persistence: this header owns no runtime state. It defines the exact in-board RAM and register format that persists only while the hardware is active.

Dependencies and integration points: relies on kernel integer aliases and is tightly coupled to Am7990/LANCE hardware semantics and the A2065 Zorro-II layout. It is not a public subsystem API; it is local driver implementation data.

Risks: descriptor fields are raw endian-sensitive 16-bit and byte fields, so users must preserve the driver’s byte-swapping assumptions. The hardware offsets are fixed and valid only for A2065-compatible boards. Typo in the `mblength` comment is harmless, but reinforces that this is legacy hardware documentation rather than checked API metadata.

Test signals: compile-time validation through `a2065.c`, descriptor layout inspection on m68k, and runtime ring/status interpretation on real A2065 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/a2065.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/amd8111e.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/amd8111e.c

Purpose: implements the PCI driver for the AMD8111E 10/100 Ethernet controller. It provides netdev operations, NAPI RX, DMA descriptor management, MII/ethtool support, interrupt coalescing, dynamic inter-packet gap tuning, jumbo/VLAN options, WOL setup, and PCI power-management hooks.

Important APIs and functions: module binding is via `module_pci_driver(amd8111e_driver)` with `amd8111e_probe_one` and `amd8111e_remove_one`. Netdev operations include `amd8111e_open`, `amd8111e_close`, `amd8111e_start_xmit`, `amd8111e_tx_timeout`, `amd8111e_get_stats`, `amd8111e_set_multicast_list`, `amd8111e_set_mac_address`, `amd8111e_ioctl`, and `amd8111e_change_mtu`. Data-path helpers include `amd8111e_init_ring`, `amd8111e_free_skbs`, `amd8111e_restart`, `amd8111e_rx_poll`, `amd8111e_tx`, and `amd8111e_interrupt`. PHY and management helpers include `amd8111e_read_phy`, `amd8111e_write_phy`, MII accessors, `amd8111e_probe_ext_phy`, `amd8111e_set_ext_phy`, ethtool callbacks, WOL helpers, `amd8111e_calc_coalesce`, and `amd8111e_config_ipg`.

Control flow: PCI probe enables the device, requests PCI regions, checks memory BAR and PM capability, sets 32-bit DMA, allocates a netdev, maps MMIO with devm, reads the station address from `PADR`, applies per-card module parameters, installs netdev/ethtool/NAPI hooks, probes an external PHY from addresses 0x1e down to 0, initializes MII state, and registers the device. Open requests a shared IRQ, enables NAPI, resets hardware defaults, allocates coherent rings and skbs, programs ring base/length, MAC address, IPG, interrupt masks, VLAN/jumbo bits, coalescing timer, PHY autonegotiation, and RUN/INTREN. Interrupt handling masks interrupts, reads and acknowledges `INT0`, schedules NAPI for receive, reclaims TX completions, handles link-change status, and periodically recalculates coalescing. NAPI processes RX descriptors until budget or hardware ownership, drops malformed/runt frames, swaps in a fresh skb before passing the received skb through GRO, restores descriptor DMA address/count, and re-enables RX interrupts on completion. TX queues an skb into a descriptor, maps it for DMA, optionally fills VLAN insertion metadata, marks ownership with STP/ENP/FCS/LTINT, advances `tx_idx`, triggers transmit demand, and stops the queue when the ring slot is still occupied. Close stops the queue, disables NAPI and interrupts, stops hardware, frees skbs, disables carrier and dynamic IPG timer, frees IRQ, frees coherent rings, updates stats, and clears `opened`.

State and persistence: `struct amd8111e_priv` owns coherent TX/RX descriptor rings, DMA addresses, skbs, MMIO pointer, NAPI state, ring producer/consumer indexes, RX buffer length, option flags, PHY IDs/options, `mii_if_info`, driver RX error accumulator, coalescing counters, dynamic IPG timer state, and open state. Hardware state is held in MMIO registers and MIB counters, reset during open/restart/default initialization, and partially preserved only through ethtool-selected options. Module parameters `speed_duplex`, `coalesce`, and `dynamic_ipg` are indexed by global `card_idx`; `chip_version` is global for ethtool firmware-version reporting.

Dependencies and integration points: depends on PCI, DMA mapping, netdevice, NAPI, ethtool, MII helpers, VLAN helpers when enabled, CRC32 multicast hashing, uaccess-related ioctl types, and AMD8111E register/descriptor definitions from `amd8111e.h`. It integrates with legacy MII ioctl tools, ethtool link settings/register dump/WOL, PCI runtime suspend/resume style PM ops, netpoll when configured, and kernel VLAN acceleration feature flags.

Risks: RX allocation failure clears descriptor flags but can reuse stale DMA address handling paths and increments a driver-local error counter only. DMA mapping return values are not checked with `dma_mapping_error`. `card_idx` can exceed `MAX_UNITS` if more devices are probed than module parameter slots. The WOL setter uses `else if`, so requesting both magic and PHY wake records only magic. `amd8111e_change_mtu` restarts hardware under lock while queues and NAPI may be active, increasing race sensitivity. The command-style register writes are easy to misread: writing a bit without the corresponding `VAL` bit clears or sets selected fields depending on byte semantics. Dynamic coalescing and dynamic IPG are timer/statistics driven and can cause latency or link-specific behavior regressions. Remove does not call `netif_napi_del`, relying on netdev teardown behavior in this snapshot.

Test signals: PCI probe/remove on AMD8111E hardware, DMA API debug for map/unmap symmetry, NAPI budget tests under RX load, TX ring-full and wake behavior, jumbo MTU changes up to 9000, VLAN RX/TX tag insertion/stripping when `CONFIG_VLAN_8021Q` is enabled, ethtool MII settings and WOL options, suspend/resume with and without WOL, interrupt coalescing latency/throughput checks, dynamic IPG timer behavior in half duplex, and static analysis for DMA mapping errors and module parameter bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/amd8111e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/amd8111e.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/amd8111e.h

Purpose: defines the AMD8111E controller register map, bit masks, descriptor formats, driver options, coalescing/IPG data structures, private device state, module parameter storage, and helper macro used by `amd8111e.c`.

Important APIs and types: key constants cover MMIO register offsets (`CMD0`, `INT0`, `INTEN0`, ring base/length registers, `PHY_ACCESS`, `PADR`, `LADRF`, MIB counters), command-style register `VAL` bits, interrupt masks, PHY/MIB/flow-control/PMAT fields, ring sizes, MTU limits, packet buffer sizes, option flags, coalescing limits, and IPG tuning bounds. Defines `struct amd8111e_tx_dr`, `struct amd8111e_rx_dr`, `struct amd8111e_link_config`, `struct amd8111e_coalesce_conf`, `struct ipg_info`, and the large `struct amd8111e_priv`. Also defines `amd8111e_writeq` for two 32-bit writes to 64-bit device register space and static module parameter arrays.

Control flow: no executable control flow except the macro-expanded `amd8111e_writeq`. The C file uses these definitions to interpret descriptors, program MMIO registers, expose ethtool register dumps, size rings and buffers, and maintain private runtime state.

State and persistence: the header declares compile-time constants plus translation-unit static variables `card_idx`, `speed_duplex`, `coalesce`, `dynamic_ipg`, and `chip_version` because it is included by the single implementation file. Runtime state is represented by `struct amd8111e_priv`, including descriptor memory, skb arrays, DMA addresses, NAPI, link/coalescing/IPG state, and MII information.

Dependencies and integration points: requires Linux networking, PCI, DMA, MII, timer, and endian types supplied by the including C file and kernel headers. It is local to the AMD8111E PCI driver and maps directly to controller documentation. Its descriptor structures are shared with hardware via coherent DMA and therefore encode little-endian fields explicitly.

Risks: placing static module parameter variables in a header would be unsafe if included by multiple C files, though this driver uses it as a private header. `amd8111e_writeq` type-puns a `u64` through `u32 *` and performs pointer arithmetic on an MMIO pointer, so strict-aliasing and sparse warnings are plausible. Many mask constants are hand-encoded and easy to misuse with command-style `VAL` semantics. Fixed ring sizes and `MAX_UNITS` parameter arrays require code changes for larger device counts.

Test signals: compile coverage with endian and sparse checks, descriptor layout checks against hardware documentation, ethtool register dump size validation, and runtime verification of command-style register programming, LADRF writes, MIB reads, and ring DMA operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/amd8111e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.c

Purpose: implements the Village Tronic Ariadne Amiga Zorro-II Ethernet driver for an Am79C960 PCnet-ISA-compatible controller and MC68230 board glue. It manages board RAM descriptor rings, PCnet CSR programming, media auto-select, interrupts, stats, and netdev registration.

Important APIs and functions: Zorro lifecycle is `ariadne_init_module`, `ariadne_cleanup_module`, `ariadne_init_one`, and `ariadne_remove_one`. Netdev operations are `ariadne_open`, `ariadne_close`, `ariadne_start_xmit`, `ariadne_tx_timeout`, `ariadne_get_stats`, `set_multicast_list`, `eth_validate_addr`, and `eth_mac_addr`. Internal helpers include endian conversion macros, `memcpyw`, `ariadne_init_ring`, `ariadne_rx`, `ariadne_interrupt`, and `ariadne_reset`.

Control flow: probe reserves the PCnet register window and Ariadne RAM window, allocates a netdev, builds a MAC address from the Zorro serial with prefix `00:60:30`, maps CPU-visible board addresses, installs netdev ops, and registers the device. Open resets the PCnet chip, verifies chip ID through CSR88/CSR89, initializes TX/RX rings in board RAM, programs CSR3/CSR4, logical filter, physical address registers, mode register, ring base and ring length registers, enables ISACSR2 media auto-select and LED behavior, starts the queue, requests the shared Amiga ports IRQ, then starts the chip. Interrupt handling loops over ERR/RINT/TINT conditions, acknowledges sources, services RX frames, reclaims TX descriptors, updates errors/collisions, restarts TX on FIFO errors, and re-enables interrupts. RX copies completed frames from word-oriented board memory to skbs. TX pads short frames, writes descriptor fields in ownership-safe order, copies skb data via `memcpyw`, triggers TDMD, and stops the queue if the next descriptor is busy. Stats read CSR112 missed-frame count. Multicast changes stop the chip, rebuild rings, set promiscuous mode or a coarse all/none logical filter, and restart.

State and persistence: `struct ariadne_private` keeps arrays of descriptor and buffer pointers, TX/RX producer and dirty indexes, and a `tx_full` flag. Board RAM contains `struct lancedata`, which is reinitialized on open, reset, and multicast changes. The MAC is reconstructed from Zorro ROM serial and not persisted by the driver. Hardware missed-frame counts are copied into netdev stats on stats/close.

Dependencies and integration points: depends on Zorro bus APIs, Amiga interrupt and address macros, Linux netdevice/skbuff/Ethernet helpers, bitops, and register definitions from `ariadne.h`. It integrates with the networking stack through `register_netdev` and with module autoload through the Ariadne Zorro ID table.

Risks: TX ring size is five, not a power of two, so pointer arithmetic uses modulo and dirty-index normalization carefully; regressions here can wedge the queue. The multicast implementation does not compute per-address hash bits and relies on upper-layer filtering for nonzero multicast lists. RX allocation failure logic preserves descriptors only until ring pressure is high, which can drop frames under memory pressure. IRQ is shared and handled by polling CSR interrupt state. The code uses raw volatile board memory and old-style local IRQ disabling rather than DMA APIs.

Test signals: Zorro probe/remove on Ariadne hardware, PCnet chip-ID validation, RX/TX with sustained traffic, TX FIFO error restart, queue stop/wake behavior when the five-entry TX ring fills, multicast/promiscuous mode transitions, missed-frame stats reads, and shared IRQ filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.h

Purpose: defines Ariadne board register maps, PCnet-ISA CSR/ISACSR offsets and bit masks, descriptor structures, MC68230 register layout, and board memory offsets for `ariadne.c`.

Important APIs and types: provides `struct Am79C960`, swapped CSR constants, CSR0/CSR3/CSR4/CSR15/ISACSR bit definitions, `struct RDRE`, `struct TDRE`, RX/TX/error flags, `struct MC68230`, and Ariadne offsets for LANCE registers, PIT, boot ROM, and RAM.

Control flow: no executable control flow. The C file uses these definitions when probing, programming the PCnet chip, setting ring pointers, interpreting descriptor status, configuring media auto-select/LEDs, and reserving Zorro resources.

State and persistence: the header stores no state. Its structures describe hardware register and board RAM layout that persists only on the physical device.

Dependencies and integration points: assumes Linux/m68k fixed-width aliases like `u_short` and `u_char`. It is coupled to Ariadne Zorro-II hardware, the Am79C960 PCnet-ISA chip, and MC68230 board glue, and is local to the Ariadne driver.

Risks: many CSR constants are pre-byte-swapped, so using them outside the intended endian path would program incorrect registers. Descriptor and register structures use volatile fields and exact padding assumptions. The boot ROM offset is documented as guessed, so consumers should not rely on it without hardware confirmation.

Test signals: compile coverage with `ariadne.c`, hardware smoke tests for CSR access and descriptor interpretation, and verification that swapped constants program expected PCnet registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/ariadne.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/atarilance.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/atarilance.c

Purpose: implements an Atari m68k LANCE Ethernet driver for Riebl and PAM VME/internal cards. It probes fixed memory/I/O address candidates, distinguishes board variants, manages shared-memory descriptor rings, handles Atari VME/autovector IRQs, and exposes a single netdev.

Important APIs and functions: module lifecycle is `atarilance_module_init`/`atarilance_module_exit` around `atarilance_probe`. Main helpers are `lance_probe1`, `addr_accessible`, `lance_open`, `lance_init_ring`, `lance_start_xmit`, `lance_interrupt`, `lance_rx`, `lance_close`, `set_multicast_list`, `lance_set_mac_address`, `lance_tx_timeout`, and `slow_memcpy`. Netdev ops bind open, stop, transmit, set_rx_mode, set_mac_address, tx_timeout, and validation.

Control flow: module init allocates one netdev and scans `lance_addr_list`. Each candidate tests memory and I/O accessibility with a temporary bus-error vector, performs read/write checks, validates CSR0 behavior, stops the chip, classifies PAM versus old/new Riebl, requests an IRQ, obtains or synthesizes the MAC address, initializes the LANCE init block and ring descriptors, records the interrupt vector in board memory or PAM I/O, and returns for `register_netdev`. Open initializes rings, restores big-endian CSR3 after STOP, writes CSR1/CSR2 init-block address, starts INIT, waits for IDON, then starts interrupts and the queue. TX pads short packets, applies a PAM even-length workaround, copies data through either normal or slow memcpy into board memory, marks descriptor ownership last, kicks TDMD, and stops the queue if the next descriptor is busy. Interrupt handling holds `devlock`, acknowledges CSR0 sources, drains RX, reclaims TX, handles errors, restarts on FIFO/memory errors, and wakes the queue. RX copies valid complete frames to skbs and returns descriptors to the chip. Multicast configuration stops the chip and either sets promiscuous mode or coarse all/none logical filters. Riebl MAC changes are allowed only while closed and are written back to the reserved board memory area with a magic value.

State and persistence: `struct lance_private` stores board type, I/O and shared-memory pointers, ring indexes, copy function, TX-full flag, and a spinlock. Riebl cards have a reserved area in board memory containing MAC and magic; `lance_set_mac_address` can persist that value for future sessions. PAM MACs are read through EEPROM/RAM mapping. The driver keeps one global `atarilance_dev`.

Dependencies and integration points: depends on Atari machine detection, Atari IRQ/VME registration, low-level m68k bus-error handling, netdevice/skbuff helpers, and raw MMIO/shared-memory access. It integrates with the networking stack as a legacy single-device module and with Atari hardware through fixed address probing rather than a discoverable bus model.

Risks: probe temporarily installs a bus-error handler and writes to candidate physical addresses; mistakes can corrupt memory on unsupported machines. Several probe failure paths after IRQ allocation return failure without unregistering VME interrupt allocation. `set_multicast_list` returns early when `netif_running(dev)` is true, which appears inverted relative to its comment and may prevent live multicast changes. Close stops hardware but leaves IRQ freeing to module exit, unlike open-time request. Old Riebl cards use a default MAC unless users set one. Shared-memory reserved-area avoidance is custom and easy to break if packet buffer sizes change.

Test signals: Atari-only boot/probe on each address class, bus-error-safe negative probing, Riebl/PAM MAC discovery, open/close and module unload IRQ behavior, RX/TX under traffic, PAM odd-length TX workaround, multicast/promiscuous changes, TX timeout recovery, and Riebl MAC persistence across close/reopen or reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/atarilance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.c

Purpose: implements the Alchemy Au1x00 on-chip Ethernet MAC platform driver. It maps MAC, enable, and DMA-register resources, allocates coherent packet buffers, registers an MDIO bus, attaches a PHY through phylib, and implements netdev RX/TX around the controller’s four hardware RX and TX descriptor registers.

Important APIs and functions: platform lifecycle is `au1000_probe`, `au1000_remove`, and `module_platform_driver`. Netdev operations are `au1000_open`, `au1000_close`, `au1000_tx`, `au1000_multicast_list`, `phy_do_ioctl_running`, `au1000_tx_timeout`, `eth_mac_addr`, and validation. PHY/MDIO helpers include `au1000_mdio_read`, `au1000_mdio_write`, `au1000_mdiobus_read`, `au1000_mdiobus_write`, `au1000_mdiobus_reset`, `au1000_mii_probe`, and `au1000_adjust_link`. Hardware helpers include `au1000_enable_mac`, `au1000_hard_stop`, `au1000_enable_rx_tx`, `au1000_reset_mac`, `au1000_reset_mac_unlocked`, `au1000_setup_hw_rings`, `au1000_init`, `au1000_rx`, `au1000_tx_ack`, and stats helpers. Ettool support is limited to driver info, link, message level, and PHY link settings.

Control flow: probe validates three memory resources plus IRQ, reserves regions, allocates a netdev and coherent buffer slab, ioremaps MAC/enable/MACDMA resources, sets up fixed hardware descriptor pointers, reads platform data for MAC address and PHY selection or falls back to random MAC/no-data defaults, creates and registers an MDIO bus, attaches a PHY if found, initializes free buffer descriptors, assigns RX/TX buffers to hardware descriptor registers, resets the MAC, and registers the netdev. Open requests IRQ, initializes hardware registers, starts the PHY, and starts the queue. RX IRQ handling drains all descriptors with `RX_T_DONE`, updates stats, copies good frames into newly allocated skbs, returns the same coherent buffer to hardware, and advances `rx_head`. TX acknowledges completed descriptors from `tx_tail`, updates error stats, clears done bits, and wakes the queue. TX path checks whether the current hardware TX register is busy, copies skb data into a preassigned coherent buffer, pads to Ethernet minimum, updates stats immediately, writes length and DMA-enable status, frees the skb, and advances `tx_head`. Link adjustment changes full/half duplex by stopping RX/TX, updating MAC control, and reenabling. Close stops the PHY, resets hardware under lock, stops the queue, and frees IRQ.

State and persistence: `struct au1000_private` stores a free list of `db_dest` buffer descriptors, arrays of fixed RX/TX hardware descriptor register pointers, in-use RX/TX buffer descriptors, ring heads/tails, full flag, PHY selection/configuration, MDIO bus pointer, mapped register pointers, coherent buffer base and DMA address, spinlock, link-change cache, and message level. No state persists beyond device lifetime except platform-provided MAC/PHY configuration.

Dependencies and integration points: depends on platform resources named by board code, Au1xxx platform headers, DMA coherent allocation, phylib/MDIO, Linux netdevice/skbuff/ethtool/MII APIs, CRC32 multicast hashing, and MIPS-specific headers. It integrates with platform data `struct au1000_eth_platform_data`, phylib link adjustment, and platform autoload alias `platform:au1000-eth`.

Risks: RX allocation failure uses `continue` before returning the descriptor to hardware, which can leave that RX descriptor done and stall progress on that slot. The `phy1_search_mac0` fallback loop appears to break immediately when `mac_id == 1`, preventing the intended MAC0 bus search in this snapshot. Probe error handling calls `au1000_reset_mac(dev)` after some paths where mapped registers exist, but several resource-release paths rely on all earlier mappings being valid. TX statistics are incremented before hardware completion, so failed transmissions are counted as packets/bytes. The fixed four-descriptor hardware rings have little buffering; queue-full behavior needs careful interrupt completion. Remove releases resources by re-fetching resource indices and uses variable names that can obscure MACDMA versus base resource release.

Test signals: platform probe/remove with valid and missing resources, MDIO bus registration and PHY attach, PHY-less operation, link up/down duplex transitions, RX/TX ring wrap, TX busy/wake behavior, RX allocation-failure fault injection, multicast hash/promiscuous/allmulti programming, DMA coherent operation on Au1xxx cache configurations, and suspend-like close/open reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.h

Purpose: defines private constants, buffer descriptor types, hardware descriptor register layouts, MAC register layout, and driver-private state for the Au1x00 Ethernet platform driver.

Important APIs and types: constants include MAC register size, four RX/TX DMA descriptors, four RX/TX buffers, maximum buffer size, TX timeout, minimum packet size, and multicast filter limit. Defines `struct db_dest`, `struct tx_dma`, `struct rx_dma`, `struct mac_reg`, and `struct au1000_private`.

Control flow: no executable code. `au1000_eth.c` uses the structures to allocate coherent buffers, map fixed hardware DMA descriptor registers, address MAC registers by field, and store per-device PHY/ring state.

State and persistence: `struct au1000_private` captures all per-netdev runtime state: free buffer descriptors, descriptor register arrays, in-use buffer arrays, head/tail/full state, MAC ID, MAC enable state, cached link/speed/duplex, MDIO bus, PHY configuration, mapped register pointers, coherent buffer addresses, lock, and debug message level. No persistent storage is defined.

Dependencies and integration points: assumes Linux `u32`, `dma_addr_t`, `spinlock_t`, and `struct mii_bus` declarations from including files. It mirrors Au1x00 MAC/MACDMA hardware register layout and is private to the platform driver.

Risks: fixed descriptor and buffer counts are tied to hardware and leave little room for bursts. `struct mac_reg` field ordering must match the hardware register block exactly. `vaddr` is a `void *` used with byte arithmetic in the C file, which relies on compiler extensions accepted by kernel builds.

Test signals: compile and sparse coverage, register-offset validation against hardware documentation, and runtime RX/TX buffer assignment on Au1x00 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/declance.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/declance.c

Purpose: implements the DECstation LANCE Ethernet driver for IOASIC onboard LANCE, PMAD-AA TURBOchannel modules, and PMAX onboard LANCE variants. It handles variant-specific shared-memory layouts, descriptor padding, DMA setup, interrupts, multicast filtering, and netdev registration.

Important APIs and functions: module lifecycle is `dec_lance_init`/`dec_lance_exit`, with platform probing through `dec_lance_platform_probe`/`dec_lance_platform_remove` and TURBOchannel probing through `dec_lance_tc_probe`/`dec_lance_tc_remove`. Core device setup is `dec_lance_probe`. Netdev operations include `lance_open`, `lance_close`, `lance_start_xmit`, `lance_tx_timeout`, `lance_set_multicast`, validation, and `eth_mac_addr`. Hardware/data helpers include `load_csrs`, `cp_to_buf`, `cp_from_buf`, `lance_init_ring`, `init_restart_lance`, `lance_rx`, `lance_tx`, `lance_interrupt`, `lance_dma_merr_int`, `lance_reset`, and multicast retry/load helpers.

Control flow: initialization registers the TC driver and probes onboard platform LANCE when available. `dec_lance_probe` allocates a netdev, selects memory/register/IRQ/ESAR layout by type, sets buffer CPU and LANCE-visible pointers with variant-specific stride/padding, configures IOASIC DMA for ASIC LANCE, validates the Ethernet station address ROM, installs netdev ops and a multicast retry timer, registers the netdev, and chains onboard devices in `root_lance_dev`. Open stops the chip, clears mode/filter, initializes rings, loads CSR init-block address, requests the main IRQ and optional DMA memory-error IRQ, enables IOASIC DMA if needed, starts the queue, and initializes/restarts the chip. IRQ handling acknowledges CSR0, clears errors, drains RX, reclaims TX, restarts on memory errors, and re-enables interrupts. RX/TX copy routines abstract PMAD linear buffers, PMAX halfword-only buffers, and IOASIC 16-byte-valid/16-byte-gap packing. Multicast updates stop and reinitialize the chip when TX is idle or defer via timer while TX is active.

State and persistence: `struct lance_private` stores device type, optional DMA IRQ, register pointer, lock, RX/TX indexes, CSR3 busmaster value, multicast timer, owning netdev, and arrays of CPU and LANCE-visible RX/TX buffer addresses. `root_lance_dev` chains platform devices for cleanup. Hardware state includes IOASIC DMA enable bit, LANCE CSRs, ESAR PROM contents, and shared memory rings; no driver-managed persistent storage is written.

Dependencies and integration points: depends on DECstation MIPS headers, IOASIC registers and locks, TURBOchannel bus support when configured, netdevice/skbuff/Ethernet helpers, CRC32 multicast hashing, and raw CKSEG1 address mapping. It integrates with both legacy platform probing and the TC driver model.

Risks: variant-specific pointer math and padded structure access macros are fragile; incorrect `type` selection corrupts descriptor interpretation. IOASIC onboard memory start is a documented hack at CKSEG1 `0x00020000`, with explicit zeroing for a KN04 crash workaround. The ESAR PROM validation expression uses chained inequality logic that may not catch all corrupt patterns. `dec_lance_init` returns TC registration status; if TC registration succeeds but platform probe finds no device, module init still succeeds. Multicast updates stop/restart hardware and can drop packets. DMA memory-error handling logs the address but does not perform full recovery.

Test signals: boot/probe on IOASIC, PMAX, and PMAD-AA hardware or emulation, ESAR PROM validation, IOASIC DMA enable/disable and memory-error IRQ behavior, RX/TX across each buffer-packing type, multicast/promiscuous changes with deferred timer, TX timeout/reset, TC probe/remove resource release, and allmodconfig builds with and without `CONFIG_TC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/declance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.c

Purpose: implements the HP300 DIO LANCE Ethernet front-end using the generic `7990.h` LANCE core. It handles DIO bus discovery, HP-specific register/NVRAM access, board-level interrupt enable/disable, and netdev registration.

Important APIs and functions: module lifecycle is `hplance_init_module`/`hplance_cleanup_module` around `dio_register_driver`. DIO lifecycle is `hplance_init_one` and `hplance_remove_one`. Board setup is `hplance_init`. Register access callbacks are `hplance_writerap`, `hplance_writerdp`, and `hplance_readrdp`. Netdev operations use wrapper `hplance_open`/`hplance_close` plus generic `lance_start_xmit`, `lance_set_multicast`, optional `lance_poll`, and address helpers.

Control flow: probe allocates a netdev, reserves the DIO memory region, calls `hplance_init`, registers the netdev, and stores drvdata. `hplance_init` resets the board through DIO ID space, reads the Ethernet address from NVRAM as one nibble per byte, fills the embedded generic `struct lance_private` with base address, init-block RAM, IRQ, endian CSR3 value, ring sizes, and callback function pointers. Open calls generic `lance_open`, then enables board-level interrupts by writing `LE_IE` to the DIO status register. Close disables board-level interrupts and delegates to generic `lance_close`. Register callbacks loop until the DIO status register reports `LE_ACK`.

State and persistence: `struct hplance_private` only embeds the generic LANCE state. The MAC address is read from NVRAM but not modified. LANCE init block and buffers live in the DIO memory window at `HPLANCE_MEMOFF`.

Dependencies and integration points: depends on the HP DIO bus API, HP-specific DIO address/ID semantics from `hplance.h`, Linux netdevice helpers, raw big-endian I/O accessors, and the generic `7990.h` LANCE implementation. It integrates with DIO device IDs through `DIO_ID_LAN`.

Risks: register access busy-waits indefinitely for `LE_ACK`; a broken board could hang in the callback. Board-level interrupt status handling is minimal and delegates most work to generic LANCE code. The driver assumes DIO NVRAM nibble layout and fixed memory offsets. Init-block `lance_init_block` is shared through included generic code, so ring-size constants must match the available 16 KB board RAM.

Test signals: DIO probe/remove, NVRAM MAC extraction, generic LANCE open/RX/TX/multicast paths, board interrupt enable/disable, and fault testing for missing `LE_ACK` if hardware simulation is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.h

Purpose: defines HP300 DIO LANCE register offsets, status bits, and memory/NVRAM offsets used by `hplance.c`.

Important APIs and types: constants include DIO registers `HPLANCE_ID` and `HPLANCE_STATUS`, status bits `LE_IE`, `LE_IR`, `LE_LOCK`, `LE_ACK`, `LE_JAB`, and offsets `HPLANCE_IDOFF`, `HPLANCE_REGOFF`, `HPLANCE_MEMOFF`, and `HPLANCE_NVRAMOFF`.

Control flow: no executable code. The C driver uses these definitions to reset the board, poll ACK after LANCE register accesses, enable board interrupts, locate the generic LANCE register block and init memory, and read the MAC address from NVRAM.

State and persistence: no software state. The header describes fixed board register and NVRAM locations; the NVRAM MAC contents persist on the device.

Dependencies and integration points: local to HP DIO LANCE support and paired with generic `7990.h` register offsets. It assumes DIO-specific IPL extraction is handled elsewhere.

Risks: all offsets are hard-coded for HP300 DIO hardware. `LE_JAB` is documented uncertainly as loss of TX clock, so diagnostics using it should be treated cautiously. Infinite ACK polling risk lives in the C code that consumes `LE_ACK`.

Test signals: compile coverage through `hplance.c`, hardware validation of MAC nibble offsets, and register-access ACK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/mvme147.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/mvme147.c

Purpose: implements the MVME147 onboard LANCE Ethernet front-end using the generic `7990.h` LANCE core. It sets up one machine-specific netdev, allocates DMA-capable RAM for the generic LANCE init block and buffers, provides big-endian register callbacks, and controls PCC LAN interrupts.

Important APIs and functions: module lifecycle is `m147lance_init`/`m147lance_exit` around `mvme147lance_probe`. Netdev operations are wrapper `m147lance_open` and `m147lance_close` plus generic `lance_start_xmit`, `lance_set_multicast`, `lance_tx_timeout`, and address helpers. Register callbacks are `m147lance_writerap`, `m147lance_writerdp`, and `m147lance_readrdp`.

Control flow: probe runs only on `MACH_IS_MVME147` and only once, allocates a netdev, reads the board Ethernet address suffix from `ETHERNET_ADDRESS` with OUI `08:00:3e`, allocates 32 KB of DMA pages, fills embedded generic LANCE private state with base address, CPU and LANCE views of the init block, big-endian CSR3 busmaster value, IRQ, ring sizes, and register callbacks, then registers the netdev. Open delegates to generic `lance_open`, clears pending PCC LAN interrupts, and enables IRQ 4 bits in `m147_pcc->lan_cntrl`. Close disables PCC LAN interrupts and delegates to generic close. Exit unregisters the netdev, frees DMA pages, and frees the device.

State and persistence: `struct m147lance_private` embeds generic LANCE state and stores the allocated RAM address. The driver has one global `dev_mvme147_lance`. No persistent storage is written; the MAC source is board firmware/hardware memory.

Dependencies and integration points: depends on MVME147 machine detection and hardware definitions from `asm/mvme147hw.h`, generic LANCE support from `7990.h`, big-endian I/O helpers, and Linux netdevice APIs. It integrates with the platform as a single legacy module rather than a discoverable bus driver.

Risks: probe uses `__get_dma_pages(GFP_ATOMIC, 3)` during module init, which may fail under memory pressure. The generic LANCE init block is passed as both CPU and device-visible address, assuming identity visibility suitable for MVME147. Exit assumes `dev_mvme147_lance` is a valid netdev; if init failed and exit were invoked unexpectedly this would be unsafe, though module core normally calls exit only after successful init. Interrupt control is board-specific magic values with minimal abstraction.

Test signals: module load only on MVME147, MAC derivation from `ETHERNET_ADDRESS`, successful 32 KB buffer allocation, generic LANCE RX/TX/multicast/timeout behavior, PCC interrupt enable/disable, and module unload resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/mvme147.c -->
