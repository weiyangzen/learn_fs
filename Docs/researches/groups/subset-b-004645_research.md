# Research: subset-b-004645

Grouped research report for subset B work item `subset-b-004645`. Each source section is wrapped with reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis190.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis190.c

## Purpose
`sis190.c` is the PCI Ethernet driver for Silicon Integrated Systems SiS190 Fast Ethernet and SiS191 Gigabit Ethernet adapters. It binds PCI IDs `0x0190` and `0x0191`, maps the device MMIO register block, manages DMA descriptor rings, probes MII PHYs, programs receive filtering and link mode, and exposes normal Linux `net_device` and ethtool operations.

## Important APIs, Types, and Functions
- `struct sis190_private` is the driver state: MMIO base, PCI and netdev pointers, spinlock, RX/TX ring DMA addresses, descriptor arrays, SKB arrays, PHY work/timer state, `mii_if_info`, feature flags, negotiated link partner ability, and link state.
- `struct TxDesc` and `struct RxDesc` describe hardware DMA descriptors with little-endian packet size, status, address, and size/control fields.
- PCI entry points are `sis190_init_one()` and `sis190_remove_one()` through `module_pci_driver()`.
- Netdev operations are `sis190_open()`, `sis190_close()`, `sis190_start_xmit()`, `sis190_tx_timeout()`, `sis190_set_rx_mode()`, `sis190_mac_addr()`, and optional netpoll.
- PHY and MDIO helpers include `mdio_read()`, `mdio_write()`, `sis190_mii_probe()`, `sis190_default_phy()`, `sis190_set_speed_auto()`, and the Marvell/Broadcom/RGMII fixup paths.
- Ettool support includes register dump, message level, nway reset, and link ksettings via generic MII helpers.

## Control Flow
Probe allocates an Ethernet device, enables PCI bus mastering, requests MMIO BAR0, sets a 32-bit DMA mask, maps registers, masks interrupts, soft-resets the MAC, reads the MAC address from EEPROM or APC CMOS, initializes the hardware receive filter, probes PHY addresses 0-31, registers the netdev, forces carrier off, and starts autonegotiation. Open sizes RX buffers from MTU, allocates coherent TX/RX rings, fills RX descriptors, starts a PHY timer, requests the shared IRQ, and calls `sis190_hw_start()` to write descriptor base registers, clear WoL/filter registers, enable interrupts, enable DMA, and start the queue.

TX maps one linear SKB to a descriptor, sets ownership and checksum/pad bits, adds half-duplex collision/backoff controls when needed, advances `cur_tx`, kicks `TxControl`, and stops the queue when the ring becomes full. TX interrupts reclaim completed descriptors, unmap DMA, update stats, consume SKBs, and wake the queue. RX interrupts walk descriptors no longer owned by hardware, validate CRC/error bits, optionally copy small packets below `rx_copybreak`, unmap or recycle buffers, pass packets with `netif_rx()`, update stats, and refill descriptors. Link-change interrupts and the timer schedule `sis190_phy_task()`, which reads MII status, tracks autonegotiation/link state, selects MAC speed/duplex bits, applies RGMII delay workarounds, and updates carrier.

## State and Persistence
Persistent runtime state is in `struct sis190_private` plus hardware registers and PHY registers. Descriptor rings are coherent DMA allocations created on open and freed on close; SKB DMA mappings are per-packet. MAC address source is EEPROM or APC CMOS and is copied into `dev_addr` and the receive filter registers. There is no filesystem persistence. EEPROM/APC contents are only read, not written. The timer and work item persist while the interface is open; PHY list nodes persist from probe until remove.

## Dependencies and Integration Points
The driver depends on PCI, MMIO accessors, DMA mapping, `net_device`, `etherdevice`, generic MII/ethtool helpers, CRC32 multicast hashing, timers, workqueues, and netpoll when configured. It integrates with Linux networking through `net_device_ops`, ethtool, MII ioctls, PCI device matching, shared IRQ handling, and rtnl locking in PHY work.

## Risks and Edge Cases
- `sis190_start_xmit()` returns `NETDEV_TX_BUSY` on DMA mapping failure without freeing the SKB, so callers must retry and queue state must remain sane.
- RX buffer exhaustion is possible if allocation fails; descriptors are marked unusable and emergency logging reports a fully exhausted ring.
- The link work uses hardware-specific magic values for speed/duplex and RGMII delay; regression risk is high on rare PHY variants.
- APC MAC reads depend on ISA bridge side effects at ports `0x78/0x79`; failures fall back only if EEPROM read failed and a config bit requests APC.
- Interrupt masking/shutdown loops rely on posted-write flushing through `SIS_PCI_COMMIT()`.
- The driver is non-NAPI and calls `netif_rx()`, so heavy RX load depends on interrupt moderation and ring sizing.

## Test Signals
Useful signals are PCI probe/remove on both IDs, open/close with DMA allocation failure injection, RX/TX traffic with ring wrap, small-packet copy and large-packet unmap paths, multicast/promiscuous filter changes, MTU changes around `RX_BUF_SIZE`, PHY autonegotiation at 10/100/1000 half/full, link-change interrupts, ethtool register/MII operations, tx timeout recovery, suspend-like close/reopen cycles, and netpoll builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis190.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis900.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis900.c

## Purpose
`sis900.c` implements the Linux PCI Fast Ethernet driver for SiS 900 and SiS 7016 controllers. It handles early SiS chipset revisions with different MAC-address storage, software bit-banged EEPROM/MDIO access, MII PHY discovery and workarounds, descriptor-ring DMA, interrupt-driven RX/TX, Wake-on-LAN, ethtool, MII ioctls, multicast filtering, and PCI suspend/resume.

## Important APIs, Types, and Functions
- `struct sis900_private` stores PCI/MMIO handles, spinlock, PHY linked list, selected PHY, `mii_if_info`, link timer, descriptor rings, SKB arrays, DMA addresses, ring indices, EEPROM size, chipset revision, host bridge revision, and message mask.
- `struct mii_phy` represents detected PHYs with address, IDs, status, and HOME/LAN/MIX classification.
- `BufferDesc` is the three-word TX/RX descriptor format: link, command/status, and buffer pointer.
- Probe and remove are `sis900_probe()` and `sis900_remove()` under `sis900_pci_driver`.
- Runtime netdev operations are `sis900_open()`, `sis900_close()`, `sis900_start_xmit()`, `sis900_tx_timeout()`, `set_rx_mode()`, `sis900_set_config()`, and `mii_ioctl()`.
- Hardware accessors are `sw32`, `sw8`, `sr32`, and `sr16` over the register offsets defined in `sis900.h`.
- Ettool covers driver info, message level, link state/settings, nway reset, WoL, and EEPROM read.

## Control Flow
Probe enables the PCI device, sets a 32-bit DMA mask, allocates the netdev, requests and maps BAR0, allocates coherent TX/RX rings, initializes netdev and ethtool operations, chooses MAC-address retrieval based on revision (`sis900_get_mac_addr()`, `sis630e_get_mac_addr()`, `sis635_get_mac_addr()`, or `sis96x_get_mac_addr()`), falls back to a random address on invalid data, sets special access mode on 630ET, probes MII PHYs, records host bridge revision for equalizer workarounds, registers the netdev, and reports Wake-on-LAN capability.

Open resets the MAC, applies SiS630 equalizer rules, requests the shared IRQ, writes the receive filter MAC, initializes TX/RX rings and RX buffers, programs multicast mode, starts the queue, applies the EDB mode workaround, enables RX/TX interrupts and receive, checks media, and starts the periodic link timer. The interrupt handler loops up to `max_interrupt_work`, handling RX overrun/error/OK through `sis900_rx()` and TX underrun/error/descriptor completion through `sis900_finish_xmit()`. RX consumes descriptors with `OWN` set by hardware, validates error bits, accepts VLAN-sized frames when configured, unmaps the completed buffer, allocates a replacement, passes packets with `netif_rx()`, and refills holes. TX maps an SKB, gives the descriptor to hardware, updates ring indices, stops the queue on full, and completion unmaps/free SKBs and updates statistics.

The timer polls MII status, selects a default PHY if link is down, reads negotiated mode, updates MAC TX/RX config, applies equalizer workarounds, resets specific internal PHYs on link loss, and re-arms itself. Suspend stops queue/device and disables RX/TX; resume rebuilds filters/rings and reenables interrupts and media logic.

## State and Persistence
Runtime state is held in the private structure, PHY linked-list allocations, DMA rings, SKB mappings, MAC/PHY registers, and timer. EEPROM contents, APC CMOS, PCI PMCSR, and `pmctrl` are persistent hardware/firmware state read or modified by MAC retrieval, ethtool EEPROM read, and WoL settings. No filesystem state is written.

## Dependencies and Integration Points
The file depends on PCI, DMA mapping, Linux networking, MII helpers, ethtool, timers, CRC32, bitops, user access headers for ioctl plumbing, and the register definitions in `sis900.h`. It integrates via PCI IDs, `net_device_ops`, ethtool ops, generic MII semantics, power-management callbacks, and Kconfig-controlled VLAN frame size support.

## Risks and Edge Cases
- RX ring initialization can leave descriptor holes when SKB allocation or DMA mapping fails, and comments note uncertain hardware behavior.
- `sis900_start_xmit()` relies on ring arithmetic and `tx_full`; mistakes can stop or overrun the queue.
- EEPROM/APC access is chipset-specific and includes shared EEPROM grant/done handshakes for SiS96x.
- Link management uses many PHY-specific workarounds for ICS1893, RTL8201, SiS630, and internal PHY reset behavior.
- WoL only supports magic and PHY events, rejecting secure/unicast/multicast/broadcast/ARP options.
- The interrupt handler runs RX and TX under one spinlock and is non-NAPI, so high packet rates can be bounded by `max_interrupt_work`.

## Test Signals
Build with PCI, MII, CRC32, PM, VLAN enabled/disabled. Exercise probe on multiple revision IDs, MAC read fallbacks, MII scan with no PHY and mixed HOME/LAN PHYs, link up/down timer paths, 10/100 half/full negotiation, RX error counters, VLAN-sized frames, TX timeout recovery, multicast hash sizes for old and 635/900B chips, ethtool EEPROM and WoL operations, legacy `ifmap` media changes, suspend/resume, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis900.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis900.h

## Purpose
`sis900.h` is the hardware definition header for the SiS 900/7016 Ethernet driver. It defines MMIO register offsets, bit masks, EEPROM and MDIO command encodings, descriptor status fields, PHY-specific MII registers, revision IDs, frame sizes, ring sizes, and PCI constants consumed by `sis900.c`.

## Important APIs, Types, and Data
- `enum sis900_registers` maps the 256-byte MMIO register block, including command/config, EEPROM/MDIO access, interrupt status/mask/enable, TX/RX descriptor pointers, TX/RX config, receive filter, and power-management registers.
- Command/config/status enums define bits for reset, RX/TX enable/disable, EEPROM access, interrupts, DMA burst, FIFO thresholds, receive filtering, and Wake-on-LAN.
- EEPROM definitions include address slots, serial commands, and SiS96x shared EEPROM grant/done bits.
- Descriptor status enums define common ownership/status bits plus TX collision/underrun/carrier errors and RX CRC/frame/length/multicast markers.
- MII sections define standard and SiS/ICS/AMD-specific register numbers and bit fields for control, status, autonegotiation, speed, duplex, and PHY output status.
- Revision IDs distinguish SiS630/635/96x/900B variants and host bridge revisions.
- Frame and ring constants define VLAN-aware `MAX_FRAME_SIZE`, `TX_BUF_SIZE`, `RX_BUF_SIZE`, `NUM_TX_DESC`, `NUM_RX_DESC`, and coherent ring byte sizes.

## Control Flow
The header has no executable flow. Its constants drive all register programming, descriptor interpretation, PHY negotiation, multicast hashing, power management, and Kconfig-sensitive VLAN sizing in `sis900.c`.

## State and Persistence
No state is owned by the header. It describes persistent hardware state locations such as EEPROM words, PCI power-management registers, PM wake-event registers, and descriptor ownership bits. Changes to values here affect how the driver reads and mutates those hardware states.

## Dependencies and Integration Points
The header is included by `sis900.c` and depends on kernel config symbols such as `CONFIG_VLAN_8021Q` through `IS_ENABLED()`. It integrates the driver with hardware specifications for SiS 7016, SiS 900, SiS 7014 PHY, SiS96x EEPROM arbitration, and related PHY vendors.

## Risks and Edge Cases
- Typographical enum names such as `sis900_reveive_config_register_bits` are harmless but indicate legacy API shape that should not be casually renamed.
- Bit definitions are tightly coupled to undocumented or old preliminary datasheets; incorrect masks can corrupt descriptor ownership, receive filtering, or power management.
- VLAN-enabled `MAX_FRAME_SIZE` changes RX acceptance behavior in the C file.
- Descriptor and register constants assume 32-bit DMA and a specific ring descriptor layout.

## Test Signals
Compile `sis900.c` with VLAN both enabled and disabled, verify descriptor status decoding in RX/TX paths, exercise all revision-gated branches, and run sparse/build checks after any register or bit-mask change. Hardware tests should confirm reset, interrupts, EEPROM, MDIO, receive filter, and WoL registers still behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sis/sis900.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Kconfig

## Purpose
This Kconfig file declares the SMSC/Western Digital Ethernet vendor menu and the selectable driver options in this directory: `SMC91X`, `EPIC100`, `SMSC911X`, `SMSC911X_ARCH_HOOKS`, and `SMSC9420`.

## Important APIs, Types, and Data
- `NET_VENDOR_SMSC` is a boolean vendor gate, defaulting to `y`, with broad architecture and bus dependencies.
- `SMC91X` is a tristate for SMC 91C9x/91C1xxx devices, selecting `CRC32` and `MII`, depending on suitable embedded/platform architectures and `!OF || GPIOLIB`.
- `EPIC100` is a PCI tristate for SMC EtherPower II 9432 / SMC83c17x hardware, selecting `CRC32` and `MII`.
- `SMSC911X` is a HAS_IOMEM embedded Ethernet driver option selecting `CRC32`, `MII`, and `PHYLIB`.
- `SMSC911X_ARCH_HOOKS` is a dependent internal-style boolean for architecture hooks.
- `SMSC9420` is a PCI tristate selecting `CRC32`, `PHYLIB`, and `SMSC_PHY`.

## Control Flow
Kconfig flow is menu gating only. If `NET_VENDOR_SMSC` is disabled, the nested driver choices are hidden. Enabled driver symbols feed the adjacent Makefile to include the corresponding objects or subdrivers in the build.

## State and Persistence
The file contributes persistent kernel configuration state in `.config`. It has no runtime state. Its selections may indirectly enable library code and PHY support in the built kernel.

## Dependencies and Integration Points
The options integrate the SMSC drivers into the kernel networking vendor hierarchy and Kbuild. Help text points users to relevant networking and module documentation. The `SMSC911X_ARCH_HOOKS` option creates an architecture-to-driver extension point.

## Risks and Edge Cases
- Architecture and bus dependencies control option visibility; missing `PCI`, `HAS_IOMEM`, `GPIOLIB`, or architecture symbols can hide drivers even when source exists.
- `select` pulls in dependencies without prompting, which can change build contents.
- `SMC91X` has an OF/GPIOLIB dependency because DT-based reset/power GPIO handling is compiled in when Open Firmware matching is used.

## Test Signals
Run targeted `oldconfig`/`allmodconfig` checks for supported and unsupported architectures, verify each symbol builds as module and built-in where allowed, and confirm Makefile object inclusion matches the selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Makefile

## Purpose
This Makefile maps SMSC Ethernet Kconfig symbols to the driver objects built from this directory.

## Important APIs, Types, and Data
- `obj-$(CONFIG_SMC91X) += smc91x.o`
- `obj-$(CONFIG_EPIC100) += epic100.o`
- `obj-$(CONFIG_SMSC9420) += smsc9420.o`
- `obj-$(CONFIG_SMSC911X) += smsc911x.o`

## Control Flow
Kbuild expands each `obj-$()` assignment according to the final kernel configuration. A built-in `y` includes the object in vmlinux or the parent object list; an `m` builds it as a module; an unset symbol omits it.

## State and Persistence
There is no runtime state. The file affects only the build graph derived from `.config`.

## Dependencies and Integration Points
It consumes symbols declared in `smsc/Kconfig` and integrates the four SMSC drivers into the kernel's recursive build system.

## Risks and Edge Cases
- A mismatch between Kconfig symbol names and object rules would silently skip a selected driver.
- Adding a new source file for an existing module would require object aggregation rather than a single `foo.o` rule.
- The ordering is simple and has no conditional subdirectories, so future multi-file drivers need careful Kbuild expansion.

## Test Signals
Build with each symbol as `m` and `y`, verify expected `.o` or `.ko` outputs, and confirm no object is built when the symbol is unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/epic100.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/epic100.c

## Purpose
`epic100.c` is the PCI Fast Ethernet driver for SMC83c170/83c175 EPIC/100 and EPIC/C controllers, including SMC EtherPower II 9432 and related CardBus hardware. It manages PCI resources, MII PHY access, DMA descriptor rings, NAPI RX/TX completion, multicast filtering, ethtool/MII control, media monitoring, and PCI power management.

## Important APIs, Types, and Functions
- `struct epic_private` stores RX/TX rings, SKB arrays, DMA addresses, locks, NAPI object, ring indices, interrupt mask, RX buffer size, MMIO base, PCI device, chip flags, timer, FIFO threshold, multicast filter cache, PHY list, MII state, and queue/media flags.
- `struct epic_tx_desc` and `struct epic_rx_desc` are host-endian DMA descriptors; big-endian systems program descriptor byte swapping in `GENCTL`.
- PCI entry points are `epic_init_one()` and `epic_remove_one()`.
- Netdev operations are `epic_open()`, `epic_close()`, `epic_start_xmit()`, `epic_tx_timeout()`, `epic_get_stats()`, `set_rx_mode()`, and `netdev_ioctl()`.
- NAPI and interrupt paths are `epic_interrupt()`, `epic_poll()`, `epic_rx()`, `epic_tx()`, and `epic_rx_err()`.
- PHY helpers are `mdio_read()`, `mdio_write()`, `check_media()`, and MII-backed ethtool operations.

## Control Flow
Probe enables PCI, validates BAR size, requests regions, allocates the netdev, maps the selected BAR, initializes MII callbacks, allocates coherent TX/RX rings, applies module media/duplex options, powers the chip enough to read MII and MAC registers, reads the MAC from LAN registers, discovers PHY addresses, powers down MII-capable chips, sets netdev operations/NAPI/watchdog, registers the device, and reports resources.

Open resets the chip, enables NAPI, requests the IRQ, initializes rings and RX buffers, applies documented TEST1 magic, powers MII where required, programs endian/GENCTL behavior, writes MAC registers, chooses duplex from forced media or link partner, writes TX/RX descriptor base registers, starts RX, starts the queue, enables interrupts, and starts a media timer. Interrupts acknowledge normal non-NAPI events immediately, schedule NAPI for RX/TX events while masking those sources, and handle uncommon counter overflow, TX underrun, and PCI bus errors. Polling reclaims TX, receives packets up to budget, handles RX overflow/full, and reenables NAPI interrupts when complete.

TX pads short packets, maps the SKB, fills descriptor fields with ownership last, advances `cur_tx`, stops the queue near `TX_QUEUE_LEN`, and kicks `TxQueued`. TX completion checks success/error bits, updates stats, unmaps DMA, frees SKBs, and wakes the queue. RX consumes descriptors no longer owned by hardware, copies small packets below `rx_copybreak` or takes ownership of the mapped SKB, passes packets with `netif_receive_skb()`, then refills descriptors.

## State and Persistence
Persistent runtime state is in `epic_private`, coherent rings, SKB mappings, cached multicast filter, MII state, and hardware registers. Module parameters persist for the loaded module: `debug`, per-card `options`, per-card `full_duplex`, and `rx_copybreak`. Hardware error counters are latched in device registers and accumulated into `dev->stats`. There is no filesystem persistence.

## Dependencies and Integration Points
The driver depends on PCI, DMA mapping, NAPI, Linux netdev, MII helpers, ethtool, timers, spinlocks, CRC32 multicast hashing, and PM callbacks. It integrates with Kconfig through `CONFIG_EPIC100`, with generic MII ioctl/ethtool paths, and with netpoll indirectly through NAPI-safe interrupt handling.

## Risks and Edge Cases
- Descriptor endianness is unusual: descriptors are host-endian and hardware byte-swaps on big-endian systems.
- RX initialization and refill lack explicit DMA mapping error checks in some allocation paths, so mapping failures are a risk area.
- The multicast hash path is effectively bypassed for multicast due to a documented chip bug, accepting all multicasts.
- PCI bus errors trigger pause/restart from interrupt context; restart must preserve ring indices correctly.
- Ettool and ioctl power the device up temporarily when the interface is down and must power it down symmetrically using `ethtool_ops_nesting`.

## Test Signals
Test PCI probe/remove, NAPI RX/TX traffic, ring wrap at 256 descriptors, TX queue stop/wake near `TX_QUEUE_LEN`, FIFO underrun threshold increase, PCI bus error restart, multicast/promiscuous mode, small-packet copy path, MTU-driven RX buffer size, MII reads while down via ioctl/ethtool, forced duplex module options, suspend/resume, and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/epic100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc9194.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc9194.h

## Purpose
`smc9194.h` is a legacy register and macro header for SMC91xxx Ethernet chipsets, originally factored from older SMC9194 driver code. It documents the banked register model, basic types, control/status bits, chip IDs, packet status flags, and direct I/O-port helper macros for SMC91C9x-era hardware.

## Important APIs, Types, and Data
- Defines simple aliases `byte`, `word`, and `dword`.
- `SMC_IO_EXTENT` is 16 bytes, reflecting the chip's bank-switched I/O window.
- Bank 0 definitions cover transmit control (`TCR`), EPH status, receive control (`RCR`), counters, memory info, and memory configuration.
- Bank 1 definitions cover config/base/MAC address/general/control registers and EEPROM/power/auto-release bits.
- Bank 2 definitions cover MMU commands, packet number/allocation register, FIFO ports, packet pointer, data ports, interrupt status, and interrupt mask.
- Bank 3 definitions cover multicast hash registers, management, revision, and early receive.
- `chip_ids[]` and `interfaces[]` provide printable names for recognized chips and TP/AUI media.
- Macros `SMC_SELECT_BANK`, `SMC_DELAY`, `SMC_ENABLE_INT`, and `SMC_DISABLE_INT` perform direct port I/O using an expected `ioaddr` variable.

## Control Flow
The header has no standalone runtime flow, but its macros emit register I/O directly. Users select banks by writing `BANK_SELECT`, then read/write bank-local registers. Interrupt enable/disable macros switch to bank 2, update `INT_MASK`, and write it back.

## State and Persistence
No C-owned state is maintained except static const string tables. The definitions target persistent hardware state: banked registers, EEPROM access bits, MMU packet memory, interrupt masks, and receive/transmit mode registers.

## Dependencies and Integration Points
This header assumes low-level port I/O primitives such as `inw`, `outw`, `inb`, and `outb`, plus a local `ioaddr` symbol. In this source tree, the active unified `smc91x.c` includes `smc91x.h` instead; this header remains useful as legacy documentation or for older driver variants.

## Risks and Edge Cases
- Macros are not concurrency-safe and have implicit `ioaddr` dependencies, unlike the lock-aware macros in the unified driver.
- The static arrays in a header can create separate copies in each translation unit that includes it.
- Bank switching is global device state; callers must restore expected banks and serialize against interrupt handlers.
- Some constants are marked unavailable on SMC9192 or specific chip variants.

## Test Signals
If used by a driver, tests should verify bank switching, interrupt mask updates, MMU command sequencing, chip revision decoding, RX/TX status decoding, and compile coverage on architectures that provide port I/O. For the current tree, a build grep confirming no active include may be sufficient to treat it as legacy collateral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc9194.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.c

## Purpose
`smc91x.c` is the platform driver for SMSC/SMC 91C9x and 91C1xxx single-chip Ethernet controllers, including LAN91C94 and LAN91C111. Unlike PCI ring-DMA NICs, these chips expose bank-switched registers and internal packet memory managed by an MMU. The driver handles platform/DT/ACPI discovery, optional GPIO reset/power control, bus-width configuration, packet-memory TX/RX, PHY configuration, interrupts, ethtool, EEPROM access, suspend/resume, and architecture-specific hooks.

## Important APIs, Types, and Functions
- `struct smc_local` is defined in `smc91x.h` and stores MMIO base, optional data chip-select mapping, platform config, locks, tasklet, work item, MII state, current TCR/RCR/RPC modes, PHY type, pending TX SKB, DMA channel on PXA, and message level.
- Platform entry points are `smc_drv_probe()`, `smc_drv_remove()`, `smc_drv_suspend()`, and `smc_drv_resume()` in `smc_driver`.
- Core device control functions are `smc_reset()`, `smc_enable()`, `smc_shutdown()`, `smc_open()`, `smc_close()`, and `smc_timeout()`.
- Data path functions include `smc_hard_start_xmit()`, `smc_hardware_send_pkt()`, `smc_tx()`, `smc_rcv()`, and `smc_interrupt()`.
- PHY functions include serial MII bit-banging (`smc_mii_out()`, `smc_mii_in()`, `smc_phy_read()`, `smc_phy_write()`), detection, reset, fixed/autoneg configuration, powerdown, media checks, and PHY interrupt handling.
- Ettool supports driver info, message level, link settings, nway reset, link state, and EEPROM get/set.

## Control Flow
Platform probe allocates a netdev, merges platform data, OF properties, or defaults into bus-width/config flags, handles optional DT power/reset GPIOs, requests the register memory resource, obtains IRQ flags, requests optional attribute memory, enables the device through attribute-space ECOR/ECSR when present, maps the main register window, and calls `smc_probe()`. `smc_probe()` validates the bank-select signature, checks base-address consistency, identifies the chip revision, reads the MAC, resets the chip, autodetects IRQ if needed, initializes netdev/ethtool/tasklet/work/MII state, detects PHYs on 91C100-class devices, powers down, requests IRQ, optionally requests a PXA DMA channel, and registers the netdev.

Open sets default TCR/RCR/RPC modes, resets and enables the device, configures the PHY synchronously or checks 10baseT carrier, and starts the queue. TX first asks the chip MMU to allocate packet memory; if allocation is immediate it calls the TX tasklet function directly, otherwise it stores `pending_tx_skb`, stops the queue, and enables allocation interrupts. `smc_hardware_send_pkt()` writes packet headers/data/control word into chip memory, enqueues the packet, updates stats, enables TX interrupts, and frees the SKB. RX interrupt handling reads packet number/status/length from the RX FIFO, validates errors and VLAN-length exceptions, copies packet data out of chip memory into a new SKB, releases the MMU packet, and calls `netif_rx()`.

The interrupt handler masks interrupts, loops up to `MAX_IRQ_LOOPS`, and dispatches TX completion/error, RX, allocation, TX-empty statistics, RX overrun, EPH, PHY, and unsupported early-RX events while preserving the packet pointer register. Close stops queue/carrier, shuts the chip down, kills the tasklet, and powers down the PHY. Suspend detaches and shuts down; resume re-enables the platform device, resets/enables, reconfigures PHY if running, and reattaches.

## State and Persistence
State lives in `smc_local`, banked hardware registers, MMU packet memory, PHY registers, pending TX SKB, tasklet/work scheduling, interrupt mask, and EEPROM words. The driver can write EEPROM through ethtool, making that a true persistent hardware mutation. Platform data and DT properties determine persistent board-specific assumptions such as bus width, register shift, LED modes, and GPIO wiring.

## Dependencies and Integration Points
The driver depends on `smc91x.h` for hardware abstraction macros, platform bus, OF/ACPI matching, GPIO consumer APIs, IRQ APIs, workqueues/tasklets, MII helpers, ethtool, CRC32, optional PXA DMA and Assabet/Neponset hooks, and Linux netdev. Integration points include platform resources named `smc91x-regs`, `smc91x-attrib`, and `smc91x-data32`, compatible strings `smsc,lan91c94` and `smsc,lan91c111`, ACPI ID `LNRO0003`, module parameters `nowait` and `watchdog`, and generic netdev operations.

## Risks and Edge Cases
- Bank switching is shared device state; comments explicitly warn that bank 2 must be preserved while interrupts/tasklets can race.
- TX uses one `pending_tx_skb`; the code asserts no second pending packet and relies on queue stop/wake discipline.
- EEPROM set support can permanently change device contents and lacks a magic guard in this file.
- IRQ autodetection is legacy and may fail, requiring a provided IRQ.
- Platform config must expose at least one supported bus width; wrong `reg-io-width`, `reg-shift`, or NOWAIT settings can make the device inaccessible.
- PHY reset sleeps while temporarily dropping the spinlock, so callers must tolerate state changes around reset.

## Test Signals
Test platform, OF, and ACPI probe paths; optional GPIO reset/power timing; 8/16/32-bit access configurations; IRQ trigger selection; open/close; RX/TX with MMU allocation immediate and deferred; TX timeout reset; RX overrun and EPH interrupts; PHY present and absent paths; ethtool link settings and EEPROM read/write; suspend/resume while running and stopped; module parameters `nowait` and `watchdog`; netpoll builds; and PXA/Neponset conditional builds where relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.c -->
