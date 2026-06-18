# Research: subset-b-004332

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.c

Purpose: PCI Ethernet driver for the 3Com 3CR990/3C990 Typhoon family with an onboard 3XP processor. It owns PCI probe/remove, firmware loading, DMA ring setup, NAPI receive, transmit descriptor construction, ethtool link/WOL controls, statistics, suspend/resume, and sleep/runtime image transitions.

Important APIs, types, and functions: `struct typhoon` is the private runtime state and `struct typhoon_shared` is the coherent DMA region consumed by the NIC. Key paths are `typhoon_init_one()`, `typhoon_open()`, `typhoon_close()`, `typhoon_start_tx()`, `typhoon_poll()`, `typhoon_interrupt()`, `typhoon_start_runtime()`, `typhoon_stop_runtime()`, `typhoon_download_firmware()`, `typhoon_boot_3XP()`, `typhoon_issue_command()`, `typhoon_rx()`, and `typhoon_tx_timeout()`. `typhoon_ethtool_ops` exposes driver info, ring sizes, WOL, and link settings.

Control flow: probe enables PCI, selects MMIO or PIO, allocates coherent shared rings, resets the 3XP, boots the sleep image, reads the MAC and image version, then sleeps the adapter before registering the netdev. Open requests firmware, wakes the card, installs IRQ/NAPI, downloads and boots the runtime image, programs packet size, MAC, transceiver, VLAN type, offload tasks, RX filter, and enables TX/RX. Interrupts only schedule NAPI; NAPI drains responses, completions, RX rings, and refills the free-buffer ring.

State and persistence: durable device state is hardware/firmware state plus the cached firmware pointer. Runtime state includes byte-offset ring cursors, coherent DMA indexes, RX SKB/DMA slots, command-response wait state, link speed/duplex, selected transceiver, WOL flags, offload mask, and saved statistics used while the sleep image cannot report full stats.

Dependencies and integration points: depends on PCI, DMA mapping, request_firmware for `3com/typhoon.bin`, NAPI, VLAN offload, ethtool, PCI PM, and the descriptor/register ABI in `typhoon.h`. The device advertises SG, IPv4 checksum, TSO, TX VLAN, RX VLAN stripping, and RX checksum.

Risks: command responses are polled with long non-preemptible waits; missed response races are patched with a self-interrupt. TX DMA map failures are not explicitly checked. The driver assumes 32-bit DMA despite 64-bit-looking firmware fields. RX DMA cannot use the usual 2-byte alignment workaround. Sleep/runtime transitions rely on precise 3XP status values and firmware behavior. WAKE_MAGIC is warned as incompatible with always-on VLAN offload.

Test signals: successful firmware request/download, probe MAC read, runtime boot, TX/RX traffic with checksum/VLAN/TSO, NAPI completions without stuck interrupts, tx-timeout recovery, multicast/promiscuous filter changes, ethtool link mode changes, stats continuity across close/open, suspend/resume with WOL, and clean failure if firmware is missing or invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.h

Purpose: hardware and firmware ABI header for the 3Com Typhoon 3XP driver. It defines the shared DMA layout, descriptor formats, command opcodes, response/stat structures, offload bits, wake-event bits, firmware image records, MMIO register offsets, boot commands, interrupt bits, and status values.

Important APIs, types, and functions: central data types are `struct basic_ring`, `struct transmit_ring`, `struct typhoon_indexes`, `struct typhoon_interface`, `struct tx_desc`, `struct tcpopt_desc`, `struct ipsec_desc`, `struct rx_desc`, `struct rx_free`, `struct cmd_desc`, `struct resp_desc`, `struct stats_resp`, `struct sa_descriptor`, `struct typhoon_file_header`, and `struct typhoon_section_header`. `INIT_COMMAND_NO_RESPONSE()` and `INIT_COMMAND_WITH_RESPONSE()` standardize command descriptor initialization.

Control flow: the header is declarative, but it directly drives driver flow: the host fills `typhoon_interface`, the 3XP updates `typhoon_indexes`, TX/RX/command/response rings are advanced by byte offsets, firmware is described by file and section headers, and boot/download handshakes use `TYPHOON_REG_*`, `TYPHOON_BOOTCMD_*`, and `TYPHOON_STATUS_*`.

State and persistence: all shared state is little-endian packed hardware state. The first four `typhoon_indexes` fields are host-written and NIC-read; the remaining fields are NIC-written and host-read. Descriptor `flags` encode type, validity, response/error state, and option subtype.

Dependencies and integration points: consumed by `typhoon.c` and tightly coupled to firmware `3com/typhoon.bin`. It assumes Linux endian helpers and packed layout semantics. The constants bridge Linux netdev concepts such as VLAN, checksum, TSO, link state, and wake events into 3XP command fields.

Risks: ABI layout changes would corrupt DMA communication. Many constants are little-endian expressions rather than plain integers, so comparisons and assignments must preserve endian expectations. IPsec structures are present even though the driver does not implement full IPsec offload. The comments state current 3XP versions only use low 32-bit bus addresses.

Test signals: compile-time structure use, successful firmware boot-record handoff, valid command/response processing, correct stats decoding, checksum/VLAN/TSO flags observed on traffic, link/WOL command behavior, and no sparse/endian warnings around descriptor fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390.c

Purpose: normal-I/O wrapper module for the generic NS8390 Ethernet core. It includes `lib8390.c` with default non-delayed I/O accessors and exports the conventional `ei_*` API used by many non-ISA or newer 8390-family drivers.

Important APIs, types, and functions: exports `ei_open()`, `ei_close()`, `ei_start_xmit()`, `ei_get_stats()`, `ei_set_multicast_list()`, `ei_tx_timeout()`, `ei_interrupt()`, optional `ei_poll()`, `ei_netdev_ops`, `__alloc_ei_netdev()`, and `NS8390_init()`. Each function is a thin wrapper around the internal `__ei_*` or `__NS8390_init()` implementation from `lib8390.c`.

Control flow: compilation literally includes `lib8390.c`, producing a copy of the generic core bound to the default `inb/outb`-style macros from `8390.h`. Board drivers link against this module, allocate netdevs with `alloc_ei_netdev()` or assign `ei_netdev_ops`, fill the `struct ei_device` callbacks and buffer pages, then call `NS8390_init()`.

State and persistence: this wrapper has no per-device state beyond what `lib8390.c` keeps in `struct ei_device` inside `netdev_priv()`. It does keep the included core's static message-level/version variables for this module instance.

Dependencies and integration points: depends on `lib8390.c` and `8390.h`; selected by Makefile entries such as APNE, NE2K PCI, PCMCIA PCNET, and STNIC. It exports symbols for loadable board drivers.

Risks: because `lib8390.c` is included, symbol names and static state are bound at compile time. Any macro changes before inclusion affect the generated core. Users needing ISA bus delays must use `8390p.c` instead.

Test signals: module builds, exported `ei_*` symbols resolve for dependent drivers, a dependent board driver can open, transmit, receive, handle interrupts, and poll through `ei_netdev_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390.h

Purpose: shared definitions for NS8390/NE2000-style Ethernet drivers. It declares the common packet header, exported delayed and non-delayed core APIs, per-board private state, register offsets, command bits, interrupt bits, RX/TX status bits, and default I/O macros.

Important APIs, types, and functions: `struct e8390_pkt_hdr` models the 4-byte packet-ring header. `struct ei_device` is the key per-netdev state with board callbacks `reset_8390`, `get_8390_hdr`, `block_output`, and `block_input`, packet memory limits, two-slot TX state, RX current page, register mapping, page lock, debug level, and platform-specific fields. The exported API families are `ei_*`/`NS8390_init()` and delayed `eip_*`/`NS8390p_init()`.

Control flow: board drivers allocate a netdev, populate `struct ei_device`, choose register mappings via `EI_SHIFT`, then let `lib8390.c` handle open/close, TX, RX, interrupts, multicast, statistics, and reinitialization. The register constants define how the core changes between page 0/page 1 and uses remote DMA.

State and persistence: persistent runtime state sits in `struct ei_device`: TX buffer occupancy, queued transmit count, `txing`, `dmaing`, `irqlock`, ring pages, multicast hash, interface selection, saved IRQ, and register offsets. The core expects the page register to be restored to page 0 when unlocked.

Dependencies and integration points: included by both core wrappers and architecture-specific drivers. It expects Linux netdevice, skbuff, ioport, and irqreturn types and is intentionally macro-customizable so unusual buses can override accessors and register spacing.

Risks: `ei_status` is a macro over `netdev_priv(dev)`, which can obscure per-device state. Incorrect `reg_offset`, `word16`, `bigendian`, page bounds, or callbacks will corrupt NIC packet memory. Default I/O macros are unsuitable for memory-mapped or delayed ISA variants unless overridden before including `lib8390.c`.

Test signals: correct compile for all users, `BUILD_BUG_ON(sizeof(struct e8390_pkt_hdr) == 4)` satisfaction in the core, stable RX/TX on 8-bit and 16-bit boards, multicast hash programming, and no page-lock regressions under SMP/IRQ load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390p.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390p.c

Purpose: ISA-delay wrapper module for the generic NS8390 Ethernet core. It builds the same core as `8390.c`, but predefines `ei_inb_p()` and `ei_outb_p()` to use delayed `inb_p()`/`outb_p()` accessors for old ISA-style devices.

Important APIs, types, and functions: exports the delayed API family `eip_open()`, `eip_close()`, `eip_start_xmit()`, `eip_get_stats()`, `eip_set_multicast_list()`, `eip_tx_timeout()`, `eip_interrupt()`, optional `eip_poll()`, `eip_netdev_ops`, `__alloc_eip_netdev()`, and `NS8390p_init()`.

Control flow: the file defines bus-delay I/O macros, includes `lib8390.c`, and wraps the resulting internal functions. Drivers using `alloc_eip_netdev()` get `eip_netdev_ops`; drivers that need custom netdev ops can still call the exported `eip_*` functions.

State and persistence: no independent per-device state exists here. The included core stores all runtime state in `struct ei_device`, while this module instance owns its static core debug/version variables.

Dependencies and integration points: selected by the Makefile for legacy ISA NE2000 support (`ne.o 8390p.o`). It integrates with the same `8390.h` callback contract as the normal wrapper.

Risks: wrong wrapper selection can break timing-sensitive ISA cards or unnecessarily slow newer cards. Since it includes `lib8390.c`, any preprocessor definitions before inclusion change the entire generated core.

Test signals: ISA NE2000 probe/open succeeds, delayed I/O accesses avoid timing failures, exported `eip_*` symbols resolve, and TX/RX/interrupt behavior matches the normal wrapper on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/8390p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Kconfig

Purpose: Kconfig menu for National Semiconductor 8390 and compatible Ethernet drivers. It gates the vendor submenu and declares platform, bus, and hardware choices for AX88796, XSurf 100, Hydra, ARM EtherH/EtherM, Macintosh 8390, ColdFire 8390, ISA NE2000, PCI NE2K, Amiga PCMCIA APNE, PCMCIA PCNET, STNIC, and Zorro8390.

Important APIs, types, and functions: this is build metadata rather than C code. Important symbols are `NET_VENDOR_8390`, `AX88796`, `AX88796_93CX6`, `XSURF100`, `HYDRA`, `ARM_ETHERH`, `MAC8390`, `MCF8390`, `NE2000`, `NE2K_PCI`, `APNE`, `PCMCIA_PCNET`, `STNIC`, and `ZORRO8390`.

Control flow: selecting `NET_VENDOR_8390` exposes the submenu. Each driver entry constrains architecture or bus support with `depends on`, pulls helper code with `select`, and documents the module name. `XSURF100` selects the AX88796 base driver and AX88796B PHY support, while AX88796 can optionally select `EEPROM_93CX6`.

State and persistence: persistent output is kernel configuration state. Tristate selections determine which object files the Makefile builds into the kernel or as modules.

Dependencies and integration points: integrates with `drivers/net/ethernet/8390/Makefile`, architecture symbols (`ZORRO`, `ARM`, `ARCH_ACORN`, `MAC`, `COLDFIRE`, `SUPERH`, `AMIGA_PCMCIA`), bus symbols (`PCI`, `PCMCIA`, `HAS_IOPORT`), and shared libraries (`CRC32`, `PHYLIB`, `MDIO_BITBANG`, `NETDEV_LEGACY_INIT`).

Risks: incorrect dependencies can expose uncompilable drivers on unsupported architectures. Missing `select CRC32` would break multicast hashing users. Confusing ISA `NE2000` with PCI `NE2K_PCI` remains a user-facing configuration risk.

Test signals: `allyesconfig`/`allmodconfig` across relevant architectures, menu visibility for `NET_VENDOR_NATSEMI`, expected module names, and successful dependency resolution for AX88796 PHY/EEPROM and legacy ISA/PCMCIA options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Makefile

Purpose: build map for the 8390 Ethernet driver directory. It connects Kconfig symbols to object files and, for drivers using the shared core wrapper, ensures the appropriate `8390.o` or `8390p.o` object is linked.

Important APIs, types, and functions: object mappings are `mac8390.o`, `apne.o 8390.o`, `etherh.o`, `ax88796.o`, `hydra.o`, `mcf8390.o`, `ne.o 8390p.o`, `ne2k-pci.o 8390.o`, `pcnet_cs.o 8390.o`, `stnic.o 8390.o`, `xsurf100.o`, and `zorro8390.o`.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` assignment. Some board drivers include `lib8390.c` directly and therefore build as a single object (`mac8390`, `etherh`, `ax88796`, `hydra`, `mcf8390`); others link against wrapper objects exporting `ei_*` or `eip_*`.

State and persistence: no runtime state. The persistent effect is build composition, module contents, and whether the normal or delayed 8390 core is available.

Dependencies and integration points: paired with Kconfig and the 8390 core wrappers. `NE2000` intentionally uses `8390p.o` for ISA delays, while APNE, NE2K PCI, PCMCIA PCNET, and STNIC use normal `8390.o`.

Risks: omitting the wrapper object for a dependent driver causes unresolved `ei_*`/`eip_*` symbols. Adding `8390.o` to a driver that already includes `lib8390.c` would duplicate core code unnecessarily. Selecting `8390.o` versus `8390p.o` affects hardware timing.

Test signals: incremental and modular builds for each Kconfig symbol, `modpost` without unresolved symbols, correct module dependencies, and boot/probe tests for both direct-include and wrapper-linked drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/apne.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/apne.c

Purpose: Amiga 1200 PCMCIA NE1000/NE2000-compatible Ethernet driver using the exported normal 8390 core. It handles Amiga PCMCIA tuple parsing/configuration, fixed I/O window setup, IRQ wrapping, card probing, remote-DMA data movement, and module lifetime.

Important APIs, types, and functions: major paths are `apne_probe()`, `apne_probe1()`, `apne_reset_8390()`, `apne_get_8390_hdr()`, `apne_block_input()`, `apne_block_output()`, `apne_interrupt()`, `init_pcmcia()`, `apne_module_init()`, and `apne_module_exit()`. It fills `ei_status` callbacks and then calls `NS8390_init()`.

Control flow: module init probes only on Amiga with PCMCIA present and a card inserted. It disables PCMCIA IRQs, validates the network function tuple, programs PCMCIA config/offset, requests I/O region `0x300`, resets the card, reads the station-address PROM through 8390 remote DMA, detects 8-bit versus 16-bit access and NE/Ctron variants, requests `IRQ_AMIGA_PORTS`, initializes `struct ei_device`, registers the netdev, and re-enables PCMCIA IRQs. The interrupt wrapper validates/acks Gayle PCMCIA interrupt state around `ei_interrupt()`.

State and persistence: global `apne_owned` prevents multiple claims and `apne_dev` stores the module device. Per-device state is in `struct ei_device`: word width, TX/RX pages, callbacks, and debug level. PCMCIA hardware configuration persists until module exit resets the card.

Dependencies and integration points: depends on Amiga hardware macros, Gayle/PCMCIA helpers, ISA-style port I/O, the exported `ei_*` core, `request_region()`, and `IRQ_AMIGA_PORTS`.

Risks: comments note early returns after tuple/config failures leave PCMCIA IRQ disabled. The driver uses fixed I/O base `0x300` and one global device. Remote-DMA operations depend on `ei_status.dmaing` discipline and 20 ms RDC timeouts. Manual config blocks are compile-time only.

Test signals: Amiga PCMCIA tuple detection, successful config-byte programming, reset ACK, valid MAC read, NE1000/NE2000 word-width detection, registered netdev, IRQ ack/reenable behavior, TX RDC completion, RX ring wrap handling, and clean module unload restoring IRQ/card state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/apne.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ax88796.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ax88796.c

Purpose: platform driver for ASIX AX88796 10/100 NE2000-compatible controllers. It embeds a renamed `lib8390.c` core, adds memory-mapped register access, platform data, optional reset-area mapping, MAC loading from PROM/93CX6/platform/device, PHYLIB integration through bit-banged MDIO, ethtool, and suspend/resume.

Important APIs, types, and functions: `struct ax_device` extends `struct ei_device` with MII bus, bitbang controls, MEMR state, link state, platform data, optional second mapping, and IRQ flags. Key functions are `ax_probe()`, `ax_init_dev()`, `ax_initial_check()`, `ax_reset_8390()`, `ax_get_8390_hdr()`, `ax_block_input()`, `ax_block_output()`, `ax_mii_init()`, `ax_mii_probe()`, `ax_open()`, `ax_close()`, `ax_suspend()`, and `ax_resume()`.

Control flow: probe allocates a renamed 8390 netdev, reads platform data/resources, derives register offsets, maps memory resources, and calls `ax_init_dev()`. Device init checks register behavior, initializes AX registers, reads a MAC from configured source or randomizes one, resets the core, fills page/callback state, initializes the NS8390 stopped, and registers the netdev. Open creates/registers the MDIO bitbang bus, requests IRQ with optional platform filtering, powers the PHY, connects the first PHY, starts PHY state, and opens the 8390 core.

State and persistence: runtime state includes memory mappings, register offsets, PHY link/speed/duplex, MEMR bit latch, running/resume flags, and all standard 8390 TX/RX/page-lock state. MAC selection persists in `dev_addr`; platform data owns board-specific flags and callbacks.

Dependencies and integration points: integrates with platform bus, `net/ax88796.h`, PHYLIB, MDIO bitbang, optional EEPROM_93CX6, ethtool, and `lib8390.c` via renamed symbols.

Risks: platform data is assumed present and correct. PM resume calls `ax_NS8390_init()` and then `ax_open()` when previously running, which can double-touch initialization paths if ordering changes. MDIO bus lifetime is per-open, so open failure unwind must stay exact. Resource-offset derivation from memory size is fragile for unusual mappings.

Test signals: platform probe with and without second reset resource, MAC source variants, PHY detection/link changes, filtered and shared IRQs, TX/RX in 8-bit and 16-bit modes, ethtool PHY settings, suspend/resume with interface up/down, and EEPROM reads when `AX88796_93CX6` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ax88796.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/etherh.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/etherh.c

Purpose: Acorn expansion-card driver for I-cubed EtherH and ANT EtherM NS8390 Ethernet boards. It embeds `lib8390.c`, maps ecard MEMC/IOC resources, handles card-specific register spacing and DMA windows, supports 10BASE-T/BNC media selection, and exposes ethtool link settings.

Important APIs, types, and functions: `struct etherh_priv` stores mapped control/data windows and media state; `struct etherh_data` describes per-product offsets, supported media, and ring pages. Key paths are `etherh_probe()`, `etherh_remove()`, `etherh_open()`, `etherh_close()`, `etherh_setif()`, `etherh_getifstat()`, `etherh_reset()`, `etherh_block_input()`, `etherh_block_output()`, `etherh_get_header()`, `etherh_set_link_ksettings()`, and ecard IRQ enable/disable ops.

Control flow: module init prepares EtherH/EtherM register offset tables and registers an ecard driver. Probe requests ecard resources, allocates a netdev with extra private data, maps MEMC and optionally IOCFAST, configures IRQ control, obtains MAC from ecard chunks or system serial, fills `struct ei_device` callbacks/pages, resets and initializes the 8390 stopped, then registers the netdev. Open requests IRQ, optionally auto-detects TP versus BNC, sets media, resets, and opens the core.

State and persistence: per-device state includes mapped control byte shadow, product ID, supported media mask, chosen `if_port`, automedia flag, ecard IRQ data, and standard 8390 state. The control-port shadow persists across media/IRQ changes.

Dependencies and integration points: depends on ARM Acorn ecard APIs, MEMC/IOC mappings, ethtool, netdevice, and the included 8390 core. Product tables cover ANT EtherM and EtherLan 500/600/600A.

Risks: EtherM MAC generation from system serial can fail or produce assumptions external to the card. Some cards lack hard reset; `etherh_reset()` mainly stops the chip and optionally toggles media. Remote-DMA transfer paths rely on exact offsets and 16-bit word mode. Auto-media uses short delays and hardware heartbeat/status bits.

Test signals: ecard probe/remove, MAC acquisition, IRQ enable/disable via ecard ops, TP/BNC selection through ifmap and ethtool, automedia fallback, TX/RX with ring wrap, RDC timeout recovery, and correct register offset tables for EtherH versus EtherM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/etherh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/hydra.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/hydra.c

Purpose: Zorro-II Amiga Hydra Systems Amiganet driver using an embedded 8390 core. It supports a memory-mapped NS8390 clone with onboard RAM, 10BASE-2/AUI connectors, Zorro resource discovery, and direct board-memory packet transfers.

Important APIs, types, and functions: main paths are `hydra_init_one()`, `hydra_init()`, `hydra_open()`, `hydra_close()`, `hydra_reset_8390()`, `hydra_get_8390_hdr()`, `hydra_block_input()`, `hydra_block_output()`, `hydra_remove_one()`, and module init/exit. The driver supplies `hydra_netdev_ops` backed by internal `__ei_*` functions.

Control flow: the Zorro driver claims the 64 KiB board resource, allocates a 8390 netdev, reads the MAC from the board address PROM, sets word and big-endian mode, requests shared `IRQ_AMIGA_PORTS`, fills `ei_status` pages/callbacks/register offsets, initializes the core stopped, registers the netdev, and stores driver data. TX/RX packet movement copies directly between Zorro memory and SKBs, with wrap handling on input.

State and persistence: device state is mostly `struct ei_device`: big-endian word mode, register-offset table, TX/RX pages, and callbacks. No real hardware reset state exists; `hydra_reset_8390()` logs that reset is unavailable.

Dependencies and integration points: depends on Amiga/Zorro APIs, Zorro-II address translation, `IRQ_AMIGA_PORTS`, `z_memcpy_toio/fromio`, and included `lib8390.c`.

Risks: lack of hardware reset limits recovery from stuck NIC state. All devices share the Amiga ports IRQ. Endianness is manually handled in header reads with `WORDSWAP()`. Resource cleanup must use physical address translation matching the virtual base arithmetic.

Test signals: Zorro product match, resource claim/release, valid PROM MAC, netdev registration, shared IRQ delivery, TX/RX through direct board memory, RX ring wrap, big-endian header decoding, and graceful behavior on tx-timeout despite no reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/hydra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/lib8390.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/lib8390.c

Purpose: reusable NS8390 Ethernet core shared by many board drivers. It implements generic netdev open/close, TX queueing, two-slot transmit buffering, interrupt handling, RX ring draining, RX overrun recovery, statistics, multicast hash programming, netdev allocation, chip initialization, and transmit triggering.

Important APIs, types, and functions: internal entry points are `__ei_open()`, `__ei_close()`, `__ei_start_xmit()`, `__ei_interrupt()`, `__ei_poll()`, `__ei_tx_timeout()`, `__ei_get_stats()`, `__ei_set_multicast_list()`, `____alloc_ei_netdev()`, and `__NS8390_init()`. Helper paths include `ei_tx_intr()`, `ei_tx_err()`, `ei_receive()`, `ei_rx_overrun()`, `do_set_multicast_list()`, `make_mc_bits()`, and `NS8390_trigger_send()`.

Control flow: board drivers provide reset, packet-header read, block input, and block output callbacks in `struct ei_device`. Open locks the page register and initializes the chip running. TX pads short frames, masks card IRQs, disables the Linux IRQ, selects one of two TX slots, copies data through board `block_output`, and triggers the chip if idle. Interrupts loop over ISR bits up to `MAX_SERVICE`, dispatching RX, TX complete/error, overrun recovery, counters, and RDC acks. RX reads 8390 packet headers, validates next-page math, allocates SKBs, copies packet data through board callbacks, and advances the boundary.

State and persistence: all per-device state is `struct ei_device` plus `dev->stats`: TX slot lengths and queue count, `txing`, `irqlock`, `dmaing`, ring pages, current page, multicast filter bytes, word/endian mode, and page lock. The core assumes lock holders restore page 0.

Dependencies and integration points: included directly or via `8390.c`/`8390p.c`; relies on accessor macros and `EI_SHIFT` supplied by the including file/header. Integrates with netdevice, IRQ APIs, CRC32 multicast hashing, SKB allocation, and board packet-memory callbacks.

Risks: locking is subtle because the 8390 page register and slow remote DMA are shared by TX, RX, stats, and multicast paths. IRQ masking uses `disable_irq_nosync*` to avoid SMP/APIC races. RX overrun recovery must follow National Semiconductor sequencing with a 10 ms delay. Bad clone hardware can expose bogus headers/pages. The core is included multiple times with different macro bindings, making changes broad and easy to miscompile.

Test signals: concurrent TX/RX/stat/multicast operations under SMP, two-slot transmit sequencing, tx-timeout reset/reinit, RX overrun recovery, multicast/promiscuous/allmulti filter programming, counter accumulation, netpoll if enabled, and regression tests across delayed I/O, MMIO, memory-window, endian-swapped, and platform callback users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/lib8390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/mac8390.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/mac8390.c

Purpose: Macintosh NuBus and NuBus-like NS8390 Ethernet driver. It embeds the 8390 core and supports Apple, Asante, Farallon, Cabletron, Dayna, Interlan, and Kinetics variants with different resource discovery, register maps, packet-memory layouts, access widths, and copy routines.

Important APIs, types, and functions: central paths are `mac8390_device_probe()`, `mac8390_rsrc_init()`, `mac8390_ident()`, `mac8390_initdev()`, `mac8390_open()`, `mac8390_close()`, `mac8390_memsize()`, `mac8390_testio()`, `mac8390_no_reset()`, `interlan_reset()`, and the `sane_*`, `dayna_*`, and `slow_sane_*` block/header functions.

Control flow: the NuBus driver scans network Ethernet function resources, identifies supported card type from software/hardware IDs, reads MAC and memory/register offsets from resources where reliable or falls back to hardcoded card maps, probes shared-memory size, selects access method and register offsets, fills `ei_status`, initializes the core stopped, registers the netdev, and requests IRQ on open. Data movement is direct shared-memory copy rather than remote-DMA port I/O, with separate functions for 32-bit sane, 16-bit sane, and Dayna's spaced word layout.

State and persistence: per-device state includes card type, memory start/end, ring memory bounds, register offset table, access width, reset callback, and standard 8390 state. No separate private struct is used beyond `struct ei_device`.

Dependencies and integration points: depends on NuBus resource APIs, Macintosh IRQ helpers, low-level hardware probing (`hwreg_present`), IO memory copy helpers, and the included 8390 core.

Risks: many old cards have unreliable or incomplete resources, so hardcoded addresses remain. Memory probing writes test patterns into card RAM. Asante cards are forced to 16-bit despite passing 32-bit tests because 32-bit mode can corrupt system memory. Several cards lack reset. Endian and sparse-memory layouts require exact copy routines.

Test signals: NuBus resource discovery on each vendor, MAC read, memory-size probing, access mode detection, correct register offset selection, TX/RX including ring wrap for each copy strategy, IRQ request/free, Interlan reset, and avoiding macsonic-owned Sonic cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/mac8390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/mcf8390.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/mcf8390.c

Purpose: platform driver for NS8390-compatible Ethernet on ColdFire boards. It embeds `lib8390.c`, supports ColdFire-specific odd-offset register mappings and byte/word swapping, reads the NE2000 station PROM, implements remote-DMA callbacks, and registers a platform netdev.

Important APIs, types, and functions: platform entry points are `mcf8390_probe()` and `mcf8390_remove()`. Device setup and callbacks are `mcf8390_init()`, `mcf8390_reset_8390()`, `mcf8390_get_8390_hdr()`, `mcf8390_block_input()`, `mcf8390_block_output()`, and `mcf8390_dmaing_err()`. `mcf8390_netdev_ops` maps netdev methods to internal `__ei_*` core functions.

Control flow: probe obtains IRQ and memory resource, claims the memory range, allocates a 8390 netdev, sets base address and IRQ, then calls `mcf8390_init()`. Init resets the chip, programs a remote-DMA PROM read sequence, reads every other byte from the dataport as MAC, switches to word mode, requests IRQ, fills `ei_device` pages/callbacks/register offsets, initializes the 8390 stopped, registers the netdev, and logs address/IRQ/MAC.

State and persistence: per-device state is standard `struct ei_device`: word16 mode, TX/RX pages, callbacks, page lock, and DMA state. Compile-time `NE2000_ODDOFFSET` changes accessor behavior globally for the included core.

Dependencies and integration points: depends on platform bus resources, ColdFire `asm/mcf8390.h` definitions for byte types and swapping, inb/outb or custom odd-offset accessors, IRQ APIs, and the included 8390 core.

Risks: error path in `mcf8390_probe()` releases the memory region and frees the netdev but does not clear platform driver data. The header count conversion uses `cpu_to_le16()` rather than the more common little-endian-to-CPU pattern, which is worth scrutiny on endian-sensitive ColdFire configurations. Odd-offset and swapping macros are board-critical. Remote-DMA timeout recovery resets and reinitializes while holding core assumptions.

Test signals: platform resource probe, reset ACK, PROM MAC read, odd-offset builds, TX/RX in word mode, RDC timeout handling, IRQ request/free, netdev registration/removal, and endian validation of RX packet lengths on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/mcf8390.c -->
