# Group Research: group_11_9front_sources_os_plan9_9front_sys_src_9_pc_ether82557_c_sources_os_p_ebee00754ab7

Scope verified against `Docs/research_subset_a.md`: all files are within `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether82557.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether82557.c

Intel 82557/82558/82559 Fast Ethernet driver for Plan 9's PC Ethernet layer, registered as `i82557`.

Primary role:
- Drives Intel EtherExpress PRO/100-class PCI NICs and related 82562/82801 integrated 10/100 variants.
- Uses I/O-port CSR access, chip command/RU/CU units, EEPROM reads, MII/PHY management, receive frame descriptors, and command blocks for transmit/configuration.

Key structures:
- `Rfd`: receive frame descriptor with embedded packet data buffer.
- `Cb`: command block for transmit, configuration, individual address setup, multicast setup, and NOP.
- `Ctlr`: per-controller PCI, EEPROM, MII, receive ring, transmit command-block ring, configuration, statistics, and watchdog state.

Important behavior:
- `i82557pci()` scans Intel PCI vendor `0x8086`, filters supported device IDs, allocates I/O ports, and builds a controller list.
- `reset()` claims a controller, enables PCI bus mastering, resets the chip, loads CU/RU bases, allocates rings, reads EEPROM, configures PHY/media, starts CU, loads station address, and wires generic `Ether` callbacks.
- `attach()` unmasks interrupts, starts the receive unit, and optionally launches `watchdog()` for receiver lockup errata.
- `txstart()` fills command blocks from queued packets or pending configuration/address/multicast actions, then resumes the command unit.
- `receive()` walks completed RFDs, copies small packets or swaps large RFD buffers, queues good packets via `etheriq()`, and maintains a sentinel RFD to avoid hardware prefetch races.
- `interrupt()` acknowledges status, handles receive, RNR resume, transmit completions, underrun threshold tuning, and command queue refill.
- `ifstat()` dumps and resets hardware statistics through `DumpSC`, updates generic error counters, and prints EEPROM plus optional PHY registers.

Hardware and media details:
- EEPROM access is bit-banged through `hy93c46r()`, with dynamic address-size discovery and checksum validation against `0xBABA`.
- MII access uses `miir()`/`miiw()` through the controller MDI register.
- Includes DP83840[A] and Intel 82555 PHY handling, link-partner resolution, media override parsing, full-duplex configuration-byte updates, and a 10Mb half-duplex NOP workaround.

Research notes:
- The driver is self-contained and does not share code with the later Intel gigabit driver.
- Multicast is implemented by toggling multicast-all when multicast addresses exist, not by programming an exact multicast list.
- Shutdown performs a port reset and masks interrupts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether82557.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether82563.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether82563.c

Intel gigabit PCI/PCIe Ethernet driver covering 8256x/8257x/8258x, i210/i217/i218/i219, i350, and related Coraid HBA IDs, registered under many card names plus `igbepcie`.

Primary role:
- Provides a broad e1000/e1000e/igb-style driver using memory-mapped registers, descriptor rings, separate kernel processes for link, receive, transmit, and watchdog recovery.

Key structures:
- `Rd` and `Td`: receive and transmit descriptors.
- `Flash`: helper view for flash/ICH NVM reads.
- `Ctlrtype`: per-device type name, maximum MTU, and feature flags.
- `Ctlr`: per-controller mapped register base, descriptor memory, RX buffer pool, MII state, interrupt masks, per-process rendezvous objects, statistics, multicast table, flow-control thresholds, EEPROM cache, and recovery process pointers.

Device matrix:
- `didtype()` maps a large Intel device-ID table to internal types from `i82563` through `i350`.
- `cttab[]` defines maximum MTU and quirks such as flash EEPROM load, early receive threshold, 82575-style registers, packet-buffer allocation, flash MAC address, newer PHY paging, missing flow-control registers, and bad-checksum tolerance.

Important behavior:
- `i82563pci()` scans Intel PCI devices, handles a Coraid HBA subsystem-ID fixup, filters supported devices, and builds a controller list.
- `pnp()` claims a controller, maps MMIO, resets hardware, installs MII callbacks, populates `Ether`, and registers interrupts.
- `i82563attach()` allocates RX/TX descriptor memory and buffer pointer arrays, starts link/RX/TX/watchdog kprocs, and defers link-up to the link process.
- `i82563rproc()` initializes RX, enables receive interrupts, replenishes buffers from a private `Bpool`, validates descriptors, marks checksum-offload flags, and queues packets.
- `i82563tproc()` initializes TX, waits on output queue or interrupts, writes descriptors, and advances TDT.
- `i82563interrupt()` masks interrupts, dispatches link/RX/TX wakeups through rendezvous objects, and restores a reduced interrupt mask.
- `i82563wproc()` watches missed-packet counters and RX head movement; after repeated stuck RX indications it invokes recovery.

Reset/NVM handling:
- `i82563detach()` disables interrupts/RX/TX, balances packet buffer allocation for jumbo MTUs on some devices, performs device and EEPROM reset, and waits for reset completion.
- EEPROM sources include `eeload()` via `Eerd`, `fload()`/`fload32()` via flash registers, and `invmload()` for flashless i210/i211-style iNVM.
- `defaultea()` derives MAC address from flash/registers/EEPROM and adjusts the low byte for multi-port LAN ID.

Link handling:
- Copper PHY path uses `phylproc()` and `phyl79proc()` with MII bus integration and device-specific page-register functions.
- SerDes/PCS paths use `serdeslproc()` and `pcslproc()`.
- Speed counters are tracked for 10/100/1000/unknown.
- `phyerrata()` can reset a PHY port when link stays down on affected devices.

Control/stat interfaces:
- `i82563ifstat()` accumulates hardware statistics, prints interrupt/sleep counters, checksum stats, delay timers, key registers, type, speed counters, and EEPROM contents.
- `i82563ctl()` supports `rdtr`, `radv`, `pause`, `an`, and `recover`.

Research notes:
- Recovery is explicit and invasive: worker procs are posted notes, the code waits for them to exit, resets/deallocates under `alock`, then reattaches.
- Multicast hashing never clears bits due to hash collision ambiguity.
- RX checksum offload is enabled and reported into Plan 9 block flags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether82563.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether82598.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether82598.c

Intel 10GbE PCIe driver for 82598/82599-family controllers, registered as `i82598`.

Primary role:
- Implements a compact 10GbE driver with MMIO registers, MSI-X BAR mapping, descriptor rings, receive/transmit/link kprocs, EEPROM MAC loading, and simple interrupt demultiplexing.

Key structures:
- `Rd`: receive descriptor with address, length, checksum, status, errors, VLAN.
- `Td`: transmit descriptor with address, length, command/status.
- `Ctlr`: per-controller MMIO bases, MSI-X mapping, rings, block arrays, interrupt state, MAC address, multicast table, statistics, and speed counters.

Important behavior:
- `scan()` scans Intel vendor `0x8086` for 82598 and selected 82599/T540 IDs, maps register and MSI-X BARs, enables PCI, resets hardware, enables bus mastering, and stores up to four controllers.
- `pnp()` claims an inactive controller, writes receive address registers, fills generic `Ether` callbacks, and enables interrupts.
- `attach()` allocates aligned RX/TX descriptor storage and block-pointer arrays, initializes RX/TX, and starts link, receive, and transmit kprocs.
- `rxinit()` configures jumbo receive buffers, checksum control, descriptor ring base/length/head/tail, receive DMA thresholds, and RX enable.
- `rproc()` replenishes receive buffers, sleeps on RX interrupts, consumes done descriptors, sets checksum flags, and queues packets.
- `transmit()` is qlock-protected, cleans completed descriptors, queues up to eight packets per pass, and rings TDT.
- `lproc()` monitors `Links`, sets speed to 1000 or 10000, and updates link state.

Reset/NVM/statistics:
- `detach()` resets the NIC, applies ECC errata clearing, and clears receive-address, multicast, and VLAN filter tables.
- `eeread()` and `eeload()` read EEPROM, verify checksum including referenced sections, and extract station address with LAN ID adjustment.
- `readstats()` accumulates selected stat registers; `ifstat()` reports nonzero counters, speed buckets, and RX ring state.

Research notes:
- The driver is intentionally narrower than `ether82563.c`: no MII bus, limited control operations, and no multi-queue support despite hardware register definitions.
- `ctl()` always errors with `Ebadarg`.
- Multicast hashing follows Intel-style MTA indexing and does not clear possibly shared hash bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether82598.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether83815.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether83815.c

National Semiconductor DP83815 / SiS 900 Fast Ethernet PCI driver, registered as `83815`.

Primary role:
- Supports NatSemi DP83815/DP83816-style controllers and SiS 900 variants using I/O-port registers, descriptor rings, serial EEPROM/CMOS MAC retrieval, internal PHY negotiation, and interrupt-driven RX/TX.

Key structures:
- `Des`: descriptor with next pointer, command/status, buffer address, and associated `Block`.
- `Ctlr`: PCI/I/O state, ID, SROM data and MAC, duplex/media state, RX/TX descriptor rings and indices, transmit queue counters, error counters, system-error counters, and silicon revision.

Important behavior:
- `scanpci83815()` scans PCI network devices and accepts NatSemi `0x100B:0x0020` and SiS 900.
- `reset()` claims a controller, enables PCI, soft-resets, reads station address, writes receive filter address words, chooses media, initializes rings, and installs callbacks.
- `ctlrinit()` allocates aligned RX/TX descriptor rings, allocates RX buffers, links rings circularly, writes descriptor pointers, configures thresholds, unmasks interrupts, enables PHY interrupts, and enables global interrupts.
- `attach()` enables receive on first attach.
- `txstart()` queues output blocks into TX descriptors until the ring is nearly full and prompts transmit.
- `interrupt()` handles hardware errors, PHY link changes, receive completion/errors, transmit underrun, completed transmit descriptors, and unknown status logging.
- `ifstat()` reports per-driver counters, updates generic Ethernet error counters, shows TX queue high-water mark, and dumps SROM words.

EEPROM/MAC details:
- `eegetw()` bit-bangs serial EEPROM.
- `sissrom()` handles SiS 900 variants, including SiS 630 CMOS access through bridge registers and SiS 635 receive-filter-data extraction.
- NatSemi MAC decoding supports normal reversed/bit-straddled layout and a Soekris-specific DP83815/83816 revision path through `sokrisee()` and `ns403ea()`.

Research notes:
- Multicast callback is a no-op because the receive filter is configured to accept all multicast.
- The code contains special-case support for historical boards and chipset quirks, not just nominal DP83815.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether83815.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8390.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8390.c

Shared National Semiconductor DP8390/DP83901/DP83902 and clone Ethernet controller core.

Primary role:
- Provides common NIC logic for board-specific 8390/NE2000-style drivers, including remote DMA, shared-memory handling, RX ring processing, transmit, interrupt handling, multicast hash filters, and reset/attach callbacks.

Key interfaces:
- `dp8390reset(Ether*)`: initializes the core and installs generic Ethernet callbacks.
- `dp8390read(Dp8390*, void*, ulong, ulong)`: reads adapter RAM through remote DMA.
- `dp8390getea(Ether*, uchar*)`: reads station address registers.
- `dp8390setea(Ether*)`: writes station address registers.

Important behavior:
- `dp8390getea()`/`dp8390setea()` switch to register page 1, access PAR registers, then restore the command register.
- `_dp8390read()` and `dp8390write()` use DP8390 remote DMA; `dp8390write()` supports the dummy remote-read workaround used by some clones.
- `ringinit()` programs receive page start/stop/boundary/current pointers.
- `receive()` walks the card receive ring, reads the packet header, derives length from page pointers, validates ring state, handles wraparound copies, allocates a software block, and queues good packets.
- `txstart()` copies a queued packet into adapter memory or remote DMA, programs transmit byte count, starts TX, and marks `txbusy`.
- `overflow()` implements the datasheet overflow-recovery sequence.
- `interrupt()` masks interrupts while processing, handles overflow, RX, TX, and counter-overflow events, then restores the interrupt mask.
- `setfilter()`, `promiscuous()`, and `multicast()` maintain receive mode plus multicast address registers using CRC hash bits and per-bit reference counts.

Research notes:
- The code supports both remote-DMA I/O-port boards and shared-memory boards through `ctlr->ram`.
- Ring corruption causes a diagnostic print and ring reinitialization.
- Multicast is more precise than several newer drivers because it tracks hash-bit reference counts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8390.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8390.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ether8390.h

Header and x86 I/O glue for DP8390-family drivers.

Primary role:
- Defines `Dp8390`, shared constants, exported DP8390 core functions, and PC-specific register/data-port access helpers used by `ether8390.c` and board drivers such as `etherec2t.c`.

Key contents:
- `Dp8390` embeds a `Lock` and stores I/O base, data port, transfer width, shared-memory flag, dummy-remote-read flag, RX ring page pointers, TX busy/page state, multicast address shadow, and multicast hash reference counts.
- `Dp8390BufSz` is `256`, matching DP8390 page size.
- Exports `dp8390reset`, `dp8390read`, `dp8390getea`, and `dp8390setea`.

x86-specific helpers:
- `regr(c, r)` and `regw(c, r, v)` access byte registers at `ctlr->port + r`.
- `rdread()` reads remote-DMA data using `inss` for width 2 or `insb` for width 1.
- `rdwrite()` writes remote-DMA data using `outss` for width 2 or `outsb` for width 1.
- Unsupported transfer widths panic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ether8390.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherbcm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherbcm.c

Broadcom BCM57xx gigabit Ethernet driver, registered as `bcm`.

Primary role:
- Supports a large table of Broadcom BCM5700/570x/571x/572x/575x/576x/577x/578x/5906-family PCI NICs.
- Uses MMIO, Broadcom host status blocks, producer/return rings, DMA descriptor rings, PHY management, link interrupt handling, and a single-ring transmit/receive model.

Key structures:
- `Ctlr`: per-controller PCI device, mapped NIC registers, status block, receive return ring, receive producer ring, send ring, block pointer arrays, ring indices, active state, duplex state, and PHY number.
- Ring constants define 512-entry receive return, receive producer, and send rings.

Important behavior:
- `bcmpci()` scans network-class Broadcom PCI devices, filters a broad supported device list, maps BAR0, allocates rings/status memory, chooses PHY number, and links controllers.
- `bcmpnp()` claims an inactive controller, enables PCI/bus mastering, populates `Ether`, calls `bcminit()`, and registers interrupts.
- `bcminit()` performs a long device initialization sequence: arbitration, chip reset handshake, DMA setup, ring control blocks, status block address, coalescing settings, RX/TX engine enable, PHY reset, link setup, MAC hash/filter programming, MSI mode enable, and interrupt unmasking.
- `replenish()` allocates receive blocks and posts receive producer descriptors.
- `bcmreceive()` consumes receive return descriptors, maps them back to posted buffers, drops errored frames, and queues good packets.
- `bcmtransmit()` queues output blocks into send descriptors and advances the send producer index.
- `bcmtransclean()` frees completed transmit buffers based on status block producer indices.
- `bcminterrupt()` masks/acks via mailbox, handles error/link state bits, receives packets, cleans TX, restarts TX, and restores interrupt tag state.

Link and PHY handling:
- `miir()`/`miiw()` access the PHY through `MIComm`.
- `phyno()` handles BCM5717/5718/5719/5720 multi-function PHY numbering.
- `checklink()` reads PHY status/autonegotiation results, sets speed to 10/100/1000, sets duplex, updates MAC mode for GMII/MII, and updates Plan 9 link state.

Research notes:
- The file explicitly leaves out fatal error handling completeness, multiple rings, QoS, and checksum offload.
- Multicast callback is empty; initialization sets MAC hash registers to all ones, effectively broad multicast acceptance.
- Some register writes are device-family specific, especially BCM5717-series and BCM57765-series receive BD settings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherbcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherdp83820.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherdp83820.c

National Semiconductor DP83820 Gig-NIC 10/100/1000 Ethernet driver, registered as `DP83820`.

Primary role:
- Drives DP83820 PCI gigabit NICs with MMIO registers, descriptor rings, EEPROM MAC/configuration loading, MII PHY management, interrupt-driven RX/TX, and MIB statistics.

Key structures:
- `Desc`: transmit/receive descriptor with link pointer, buffer pointer, command/status, extended status, associated `Block`, and padding.
- `Ctlr`: per-controller PCI/MMIO state, EEPROM, cached config/interrupt masks, MII pointer, receive/transmit rings, buffer pool, TX/RX counters, and MIB counters.

Important behavior:
- `dp83820pci()` scans PCI network devices for NatSemi `0x100B:0x0022`, maps BAR1 MMIO, enables PCI, resets the controller, enables bus mastering, and links controllers.
- `dp83820pnp()` claims a controller, loads MAC address from EEPROM unless overridden, installs callbacks, and registers interrupts.
- `dp83820attach()` allocates descriptor memory, creates the MII bus unless TBI is enabled, enables PHY interrupts, and calls `dp83820init()`.
- `dp83820init()` halts current activity, grows an RX buffer pool, initializes RX/TX descriptor rings, programs station address and receive filter, configures RX/TX thresholds, clears/freezes MIBs, sets interrupt holdoff, enables interrupts, and starts RX/TX.
- `dp83820transmit()` cleans completed TX descriptors, accumulates TX errors, queues new output blocks, and kicks TX.
- `dp83820interrupt()` processes RX descriptors, restarts RX if idle, raises TX drain threshold on underrun, handles TX completion, accumulates MIB counters, and reconfigures media on PHY interrupts.

EEPROM/MII details:
- MII access is bit-banged through `Mear` using `mdiow()`/`mdior()` and exposed through `dp83820miimir()`/`dp83820miimiw()`.
- EEPROM is read through `atc93c46r()` with dynamic address-size discovery and checksum validation.
- MAC address is loaded from EEPROM words `0x0C` downward.
- `dp83820cfg()` derives duplex/speed from hardware status bits and updates RX/TX config, though comments note polarity/board-dependency concerns.

Research notes:
- The driver assumes little-endian and 32-bit host behavior.
- Promiscuous is stubbed and multicast is effectively always enabled through the receive filter.
- TBI is explicitly not handled beyond avoiding MII setup when `Tbien` is set.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherdp83820.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherec2t.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherec2t.c

PCMCIA NE2000-clone driver wrapper for Linksys/Accton/Netgear/SMC cards, registered as `EC2T`.

Primary role:
- Detects several PCMCIA Ethernet cards and configures the shared DP8390 core from `ether8390.c`/`ether8390.h`.
- Handles card-specific CIS matching, optional I/O-space MAC checksum probing, reset-port toggling, PROM/I/O MAC extraction, and DP8390 setup.

Supported card identifiers:
- `EC2T`, `PCMPC100`, `PCM100`, `EN2216`, `FA410TX`, `FA411`, `Network Everywhere`, `10/100 Port Attached`, `8041TX-10/100-PC-Card-V2`, and `SMC8022`.
- User options can provide `id=<name>` and `iochecksum`.

Important behavior:
- Defaults missing `Ether` settings to port `0x300`, IRQ `9`, memory offset `0x4000`, and size `16*1024`.
- Allocates a 0x20 I/O region, finds a matching PCMCIA special entry, allocates a `Dp8390`, and initializes width/data-port/ring geometry.
- Resets the card by reading then writing the reset register.
- Calls `dp8390reset()` before reading identification/MAC data.
- For checksum-style cards, reads 8 bytes from I/O space and requires the byte sum to be `0xFF`.
- For PROM-style cards, uses `dp8390read()` and requires marker bytes `0x57 0x57`.
- Loads the station address from the PROM/I/O buffer unless an address was already supplied, then calls `dp8390setea()`.

Research notes:
- This file is a thin board/personality layer over the shared DP8390 implementation.
- It uses remote DMA rather than shared memory (`ctlr->ram = 0`) and 16-bit transfers (`ctlr->width = 2`).
- Failure cleanup closes the PCMCIA special slot, frees the I/O region, and frees the controller.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherec2t.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherelnk3.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherelnk3.c

3Com EtherLink III / Fast EtherLink / Fast EtherLink XL driver, registered as `elnk3`, `3C509`, and `3C575`.

Primary role:
- Supports ISA, EISA, PCI, CardBus, and PCMCIA-era 3Com adapters including 3C509, 3C589, 3C59x, 3C90x, 3C575, and related device IDs.
- Handles both older PIO/FIFO operation and newer Vortex/Boomerang-style bus-master upload/download descriptor paths.

Key structures:
- `Pd`: upload/download packet descriptor with next pointer, control/status, buffer address/length, software next pointer, and `Block`.
- `Ctlr`: I/O port, PCI/IRQ state, busmaster mode, receive buffer, FIFO TX state, upload/download descriptor rings, statistics, media/transceiver config, EEPROM command mode, CardBus function mapping, and queue counters.

Discovery paths:
- `tcm59Xpci()` scans 3Com PCI network devices, accepts I/O BAR devices, handles special EEPROM command forms for 3C575/CardBus variants, maps CardBus function registers, and enables bus mastering.
- `tcm5XXeisa()` scans EISA slots for 3Com manufacturer/product IDs.
- `tcm509isa()` performs the 3Com ISA ID-sequence dance through `IDport`, reads EEPROM bit-serially, activates/tag cards, and records port/IRQ.
- `tcm5XXpcmcia()` accepts PCMCIA type strings such as `3C589`, `3C562`, and `589E`.

Important behavior:
- `etherelnk3reset()` claims a controller, reads EEPROM device ID and station address, selects busmaster mode, chooses/forces media, configures MII or fixed transceivers, initializes statistics, allocates buffers/rings, sets thresholds, and installs callbacks.
- `attach()` sets receive filters, interrupt masks, enables RX/TX, acknowledges CardBus interrupts when needed, and primes bus-master receive/upload rings.
- `txstart()` handles PIO FIFO transmission with `TxFree` threshold interrupts.
- `txstart905()` handles bus-master download descriptors, including download stalling/un-stalling while extending active lists.
- `receive()` handles FIFO or simple bus-master receive, logs RX error classes, discards bad frames, reads packet data, and queues received blocks.
- `receive905()` consumes upload descriptors, logs upload errors, replaces buffers, and queues received packets.
- `interrupt()` handles host errors, receive, upload complete, TX completion/errors, TX available, download complete, stats update, CardBus ack, and unexpected interrupt masks.
- `ifstat()` reports interrupt counts, timers, hardware statistics, upload/download queue metrics, stalls, and bad SSD counts.

Media and PHY handling:
- `autoselect()` probes available media and link beat for 100BaseTX/10BaseT fallback.
- `setxcvr()` programs old or newer transceiver selection fields and resets TX/RX.
- `miir()` bit-bangs MII reads through window 4 `PhysicalMgmt`.
- MII media resolution uses ANAR/ANLPAR plus options such as `fullduplex`, `100BASE-TXFD`, and `force100`.
- Coax mode enables the DC-DC converter; 10BaseT enables link beat/jabber guard; 100BaseTX/FX uses 1:1 RAM partition and link-beat configuration.

Research notes:
- The file preserves many generation-specific quirks: old `RxStatus` layouts, CardBus interrupt acknowledgement, 3C905B reset options, EEPROM read command variants, and known upload bugs.
- It uses register-window switching heavily and protects access with `wlock`.
- The code explicitly flags robustness, RxEarly/busmaster, auto-select, PCI latency/master enable, errata, and initialization cleanup as unresolved areas.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherelnk3.c -->