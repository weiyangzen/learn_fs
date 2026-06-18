# Group Research: group_1478_plan9_sources_os_plan9_plan9_sys_src_9_pc_etherigbe_c_sources_os_pl_f2e189b16993

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherigbe.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherigbe.c

Intel PRO/1000-style gigabit Ethernet driver for Plan 9 PC kernels, covering 82543/82544/82540/82541/82545/82546/82547 variants. It registers as both `"i82543"` and `"igbe"` through `etherigbelink()` and fills the generic `Ether` callbacks for attach, transmit, interrupt, stats, control, promiscuous, multicast, and shutdown.

The driver is register-heavy: it defines Intel MMIO offsets, bit fields, EEPROM layout, receive/transmit descriptors, multicast table state, and a `Ctlr` containing PCI identity, mapped NIC registers, descriptor rings, MII state, EEPROM words, link state, receive buffer pool accounting, and statistics/watermarks. `igbepci()` scans PCI Ethernet devices, maps BAR0 with `vmap`, normalizes cache-line size, calls `igbereset()`, enables bus mastering, and queues controllers for `igbepnp()`.

Reset and hardware discovery are substantial. `igbedetach()` disables interrupts/RX/TX, issues device reset and EEPROM reset, and clears management ARP filtering on newer chips. `at93c46r()` reads the Microwire EEPROM through `at93c46io()` and validates the checksum against `0xBABA`; SPI EEPROM is explicitly unsupported. `igbereset()` extracts the MAC address, handles dual-port address adjustment and known 82541GI EEPROM quirks, initializes receive address registers and multicast table, applies special 82543GC EEPROM defaults, configures flow-control registers, and initializes MII unless the device reports TBI mode.

PHY management uses `ethermii.h` helpers. 82543GC lacks `Mdic`, so the driver bit-bangs MDIO through software-defined pins with `i82543miimir()`/`i82543miimiw()`. Later chips use `Mdic` through `igbemiimir()`/`igbemiimiw()`. `igbemii()` probes PHYs, configures chipset-specific PHY registers, resets the PHY, and starts advertised pause/autonegotiation. A link kernel process, `igbelproc()`, waits for link-change interrupts, calls `miistatus()`, updates speed/duplex/flow-control bits in `Ctrl` and collision distance in `Tctl`, then reenables `Lsc`.

Transmit uses a fixed descriptor ring (`Ntd=32`). `igbetxinit()` programs TX base/length/head/tail, clears pending blocks, sets inter-packet gap, interrupt delay, descriptor control thresholds, and enables transmit. `igbetransmit()` frees completed descriptors by comparing software head with hardware `Tdh`, dequeues blocks from `edev->oq`, programs data descriptors, optionally requests `Txdw`, advances `Tdt`, and reenables TX interrupts.

Receive uses `Nrd=128` descriptors and a per-controller private pool of `Nrb=512` blocks shared through a global freelist. `igbeattach()` allocates aligned RX/TX descriptor memory, block pointer arrays, receive blocks with `igberbfree`, and starts link and receive kernel processes. `igberproc()` initializes RX, enables receive, sleeps until RX interrupts, scans done descriptors, accepts only clean end-of-packet frames, deliberately disables checksum-offload trust due known bugs, passes packets to `etheriq()`, tracks watermarks, and replenishes descriptors via `igbereplenish()`.

Interrupt handling masks all interrupts, loops over `Icr & ctlr->im`, records link/RX/TX causes, wakes the appropriate rendezvous, updates the mask, and calls `igbetransmit()` for TX completion. `igbeifstat()` exposes hardware counters, EEPROM words, PHY registers, interrupt counters, checksum counters, delay timer, and watermarks. `igbectl()` currently supports `rdtr <value>` to tune the receive delay timer. Multicast hashes destination bytes into the 4096-bit Intel multicast table but never clears bits because multiple addresses can collide. Promiscuous mode toggles unicast/multicast promiscuous bits but comments that multicast promiscuous is temporarily kept enabled.

Notable risks and limits: the header TODO says autonegotiation and fiber/TBI integration are incomplete and the driver is little-endian specific. SPI EEPROM access is not implemented. RX checksum offload is disabled because of known bugs. Receive buffers use a global freelist and `nrbfull`, so accounting is shared across controllers and depends on custom free callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherigbe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherm10g.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherm10g.c

Myricom 10G PCIe Ethernet driver for Plan 9, registered as `"m10g"`. Unlike the more conventional register-ring drivers in this group, this file is firmware-command centric: it includes firmware images from `etherm10g2k.i` and `etherm10g4k.i`, maps adapter SRAM, loads/boots firmware, and exchanges big-endian command/status structures with the card.

The `Ctlr` tracks PCI device, mapped RAM, EEPROM contents, MAC address, firmware command buffer, interrupt acknowledgment/deassertion pointers, coalescing pointer, done ring, TX state, small and large RX queues, DMA stats block, rendezvous objects, MSI mode flag, and link/RDMA status snapshots. `setmem()` maps BAR0, allocates aligned DMA-visible command/done/stat memory, copies EEPROM data from adapter SRAM, and calls `setpcie()` plus `parseeprom()`. `parseeprom()` extracts `MAC=` and `SN=` strings.

Firmware handling is central. `whichfw()` inspects PCIe capabilities and optional `myriforce` config to choose alignment/firmware, though it always returns 4 KiB in current logic. `loadfw()` copies the selected included firmware to adapter SRAM at `Fwoffset`; `bootfw()` submits the firmware boot command through `Fwsubmt`; `chkfw()` validates a firmware header and then boots firmware and disables RDMA command mode. `reset()` sends firmware commands to reset the device, configure interrupt queues, command offsets, coalescing, DMA stats, MAC address, flow control, and MTU, and runs DMA read/write test commands that print throughput.

Command paths use card-endian conversion helpers `pbit16`, `gbit16`, `pbit32`, and `gbit32`. `cmd()` sends scalar firmware commands through the command mailbox, waiting briefly for a DMA writeback response; `maccmd()` does the same for MAC address commands. Both use a controller command lock and raise `Etimeout` on no response. `dmatestcmd()` and `rdmacmd()` are specialized command helpers for DMA diagnostics and RDMA command toggling.

RX uses separate small and big buffer pools (`smpool` and `bgpool`) and firmware-owned RX rings. `open0()` obtains firmware ring offsets/sizes, allocates host shadows, populates free block pools, configures small/big buffer sizes, registers stats DMA, and brings Ethernet up. `replenish()` submits RX buffers to the card in batches of eight. `nextblock()` consumes done-ring entries, selects the small or big RX queue based on length, pulls the corresponding host block, marks packet checksum flags, adjusts for a 2-byte alignment pad, and returns a block for `etheriq()`. `m10rx()` replenishes both queues, sleeps on a done-entry predicate, and drains received blocks.

TX uses firmware send rings. `m10gtransmit()` dequeues output blocks, splits each packet into segments aligned to `tx.segsz`, writes `Send` descriptors with bus addresses/lengths/flags, records the block in `tx.bring` at the final segment, and submits descriptors to LANAI memory through `submittx()`. `txproc()` sleeps until stats show TX completions, then `txcleanup()` frees completed blocks and updates packet/byte counters.

Interrupt handling uses the DMA stats block. `m10ginterrupt()` ignores interrupts until state is `Runed` and stats are valid, wakes RX/TX rendezvous based on status, handles MSI versus legacy deassertion, waits for stats validity to clear, updates link/RDMA snapshots via `checkstats()`, and acknowledges interrupts. `m10gattach()` runs reset/open once, starts RX/TX kernel processes, and marks state `Runed`.

`m10gifstat()` reports DMA stats, TX/RX counters, pool sizes, segment size, and coalescing value. `m10gctl()` supports debug toggling, interrupt coalescing, manual RX/TX wakeups, and dumping the RX ring. Promiscuous and multicast changes are forwarded to firmware commands (`Cpromisc`/`Cnopromisc`, `CSjoinmc`/`CSleavemc`). `m10gpci()` scans Myricom vendor devices, accepts several device IDs with comments that most are untested, maps memory, and appends controllers.

Notable risks and limits: detach frees the controller after unmapping and comments that this is a bad idea. PCIe extended capability access is explicitly noted broken because `pcicfgr32` cannot reach extended config space. The driver performs runtime DMA speed prints during reset. Buffering is described as bloated, and several device variants are accepted as untested.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherm10g.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethermii.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethermii.c

Shared MII/PHY helper implementation used by multiple Ethernet drivers. It depends on a caller-provided `Mii` object with controller pointer and `mir`/`miw` callbacks for device-specific PHY register access.

`mii()` probes PHY addresses selected by a bitmask. For each unprobed address it reads `Bmsr`, then `Phyidr1`/`Phyidr2`, builds the OUI, ignores invalid all-ones/all-zero identifiers, allocates a `MiiPhy`, initializes advertisement/flow-control/master-slave cache fields to `~0`, installs it in `mii->phy[]`, selects the first PHY as `curphy`, and updates mask/count. It returns a mask of PHYs found or already known in this probe.

`miimir()` and `miimiw()` are safe wrappers around the current PHY read/write callbacks. They reject nil MII/controller/current-PHY state. `miireset()` sets `BmcrR` in the current PHY control register and delays briefly.

`miiane()` configures autonegotiation advertisement. It checks that the PHY supports autonegotiation, chooses 10/100 advertisement bits either from caller input, cached PHY state, or capabilities in `Bmsr`, handles pause/asymmetric pause advertisement, and when extended status is present configures 1000BASE-T half/full-duplex advertisement in `Mscr` from caller input, cached state, or `Esr`. It writes `Mscr` and `Anar`, then sets `BmcrAne|BmcrRan` if not in reset.

`miistatus()` checks autonegotiation completion and link status, reading `Bmsr` twice because link status is sticky. It determines 1000/100/10 speed and duplex from master-slave status plus the intersection of advertised and link-partner abilities. For full-duplex links it resolves receive/transmit pause behavior from local and partner pause bits. It updates `MiiPhy` fields `link`, `speed`, `fd`, `rfc`, and `tfc`.

Notable risks: the helper assumes autonegotiation for status; callers that force link modes need external handling. Allocation failures during probe simply skip a PHY. It stores per-PHY cached advertisement state but does not free `MiiPhy` objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethermii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethermii.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethermii.h

Header for the shared MII helpers. It declares `Mii` and `MiiPhy`, standard MII register numbers, register bit masks, structure layouts, and external helper prototypes.

The register enums cover basic mode control/status (`Bmcr`, `Bmsr`), PHY identifiers, autonegotiation advertisement/link-partner registers, next-page registers, 1000BASE-T master-slave control/status, and extended status. Bit enums define reset, loopback, speed select, duplex, autonegotiation enable/restart, power-down/isolate, link and capability bits, pause/asymmetric pause, remote fault, acknowledge/next page, 1000BASE-T half/full advertisement, partner 1000BASE-T support, and extended 1000BASE-X/T capability bits.

`Mii` embeds a `Lock`, tracks number and mask of detected PHYs, stores up to 32 `MiiPhy*` entries plus `curphy`, and carries opaque `ctlr` plus device-specific read/write callbacks. `MiiPhy` stores parent MII, OUI, PHY address, cached advertisement/flow-control/master-slave values, and current link/speed/duplex/flow-control result fields.

Exports are `mii`, `miiane`, `miimir`, `miimiw`, `miireset`, and `miistatus`. The header is hardware-neutral and is intended for NIC drivers to provide only low-level MII register access.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethermii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethersink.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethersink.c

Minimal synthetic Ethernet sink driver, described as an Ethernet `/dev/null` useful as a bridging target for Ethernet-based VPNs. It registers as `"sink"` through `ethersinklink()`.

`reset()` only accepts devices with a non-nil type, sets link speed to 1000 Mbps, installs no-op attach/transmit callbacks, disables IRQ and interrupt handling, clears stat/promiscuous/multicast hooks, installs a custom control hook, and uses the `Ether` itself as `arg`. It does not allocate hardware or buffers.

`ctl()` supports one command: `ea <ether-address>`. It parses the command, validates the address with `parseether`, and updates both `ether->ea` and `ether->addr`. Any other command raises `Ebadctl`. `nop()` is used for attach/transmit.

The file intentionally drops all transmitted packets and never receives packets. Its only mutable behavior is setting the visible Ethernet address.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethersink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethersmc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethersmc.c

SMC EtherEZ / SMC91cXX PCMCIA Ethernet driver. It registers `"smc91cXX"` and uses I/O ports plus PCMCIA tuple support rather than PCI discovery.

The file defines SMC91cXX banked registers, interrupt bits, MMU commands, receive/transmit status bits, packet header sizes, and an `Smc91xx` controller state with lock, revision, attach state, one pending TX block, TX allocation timestamp, and error/stat counters. `SELECT_BANK()` switches the chip register bank using the bank-select register.

`reset()` sets default IRQ/port if absent, reads an optional `id=` card type, opens a PCMCIA special slot, reserves I/O ports, allocates controller state, powers up and validates the chip ID, forces 16-bit mode, reads revision, reads the MAC address from the PCMCIA function-extension tuple if not already set, calls `chipreset()`, and installs generic `Ether` callbacks. On failure it releases I/O and PCMCIA resources.

`chipreset()` soft-resets RX/TX, writes the Ethernet address into bank 1 address registers, enables auto-release/error/counter interrupts, and resets the chip MMU. `chipenable()` enables normal TX/RX and masks in receive, receive-overrun, and EPH interrupts. `attach()` enables the chip once under the controller lock.

TX is MMU-allocation based. `txstart()` either resumes a saved block or dequeues a block, requests chip packet memory with `McAlloc`, handles `ArFailed` by enabling allocation interrupt and saving the block with timestamp, writes packet header and payload through the data port, enables TX error/empty interrupts, enqueues the packet, and frees the block. `transmit()` handles stalled saved allocations by resetting the chip after `TxTimeout`.

RX is FIFO based. `receive()` checks for RX FIFO empty, reads packet status and length from chip memory, updates generic Ethernet error counters on bad frames or allocation failure, otherwise copies payload into a new block, handles odd frame length, calls `etheriq()`, increments `inpackets`, and releases the packet from the MMU.

Interrupt handling saves/restores bank and pointer registers, masks interrupts while processing, loops over active masked causes, and dispatches receive, TX error, TX empty, allocation completion, RX overrun, and EPH events. `txerror()` reads TX status, updates lost-carrier/late-collision/16-collision counters, re-enables transmit, frees the failed packet, and restores packet selection. `eph_irq()` drains counter rollover state, re-enables TX after errors, and toggles control bits to clear link-error interrupts.

Promiscuous mode toggles `RcrPromisc`. Multicast handling does not hash addresses; it toggles all-multicast acceptance based on `ether->nmaddr`. `ifstat()` reports chip revision family and SMC-specific counters.

Notable risks: this is PCMCIA-only and depends on `pcmspecial` and CIS tuple data. The RX length expression relies on C operator precedence and appears intended to subtract header size from masked length. Multicast filtering is coarse all-multicast behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethersmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethervgbe.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethervgbe.c

VIA Velocity VT6122 gigabit Ethernet driver, registered as `"vgbe"`. Comments say register information came from the FreeBSD driver and list many TODOs: 64/48-bit DMA, autonegotiation, thresholds, dynamic ring sizing, link status changes, shutdown, promiscuous mode, error reporting, checksum offload, and jumbo frames.

The driver uses I/O-port access macros and fixed ring sizes (`RxCount=256`, `TxCount=256`, `RxSize=2048`). It defines Velocity command, EEPROM, MII, RX/TX, DMA, timer, configuration, and interrupt registers. `Ctlr` holds PCI device, port, init lock, debug flags, MII pointer, MAC address, RX/TX rings and block arrays, TX lock/count, and basic stats.

MII access is constrained to PHY address 1. `vgbemiir()`/`vgbemiiw()` write MII address/data/command registers and poll command bits until clear. `vgbereset()` soft-resets the controller, reloads EEPROM, reads MAC address registers, clears/masks interrupts, forces 32-bit address high registers to zero, starts the MAC, clears RX/TX queue run bits, enables RX/TX engines, allocates an MII structure, and probes PHY 1.

`vgbepci()` scans PCI Ethernet devices for VIA vendor/device `1106:3119`, requires I/O BAR0 with size 256, reserves the port, allocates a controller, and appends it to the controller list. `vgbepnp()` selects an inactive controller, calls `vgbereset()`, populates `Ether` fields, and installs attach/transmit/interrupt/ifstat/shutdown/control/multicast callbacks. Promiscuous callback exists but is not wired in.

`vgbeattach()` runs once. It allocates aligned RX and TX rings, allocates one RX block per RX descriptor through `vgbenewrx()`, programs RX MAC filtering for multicast/broadcast/unicast, loads RX ring base/count/index/residue, initializes DMA and TX MAC config, loads TX ring base/count/index, enables flow control, starts RX/TX queues, marks initialized, unmasks interrupts, and wakes the RX queue.

Receive completion scans the entire RX ring. `vgberxeof()` ignores descriptors still owned by hardware, accepts descriptors marked `Goodframe`, derives length from status, advances the stored block write pointer, passes it to `etheriq()`, increments RX stats, then returns descriptor ownership to hardware. The block is reused by setting `block->free = noop`, so ownership and lifetime depend on the networking stack returning it without actually freeing memory.

Transmit uses a single-fragment descriptor. `vgbetransmit()` starts from hardware `TxDscIdx`, finds free descriptors with no software block and no hardware ownership, dequeues blocks, stores them in `tx_blocks`, fills descriptor status/control and first fragment address/length, increments `tx_count`, and wakes the TX queue. `vgbetxeof()` scans TX descriptors, frees software blocks for descriptors no longer owned by hardware, updates stats, and wakes the queue if work remains.

`vgbeinterrupt()` masks interrupts, reads/acks `Isr`, filters to `Isr_Mask`, increments interrupt stats, optionally dumps decoded interrupt bits, calls RX/TX completion handlers, prints notable events, and on RX/TX DMA stall clears the global interrupt mask and returns. `vgbeifstat()` reports simple TX/TX-error/RX/intr counters. `vgbectl()` supports software reset/restart plus debug commands `dumpintr`, `dumprx`, `dumptx`, and `dumpall`.

Notable risks: RX blocks are reused with a no-op free routine and are not replaced after delivery, which requires careful external ownership expectations. Promiscuous mode is stubbed and not registered. Multicast is assumed already enabled. DMA address high registers are zeroed, so only 32-bit DMA is supported. Many TODOs remain in comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethervgbe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethervt6102.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethervt6102.c

VIA VT6102 Fast Ethernet / Rhine II and Rhine III driver, registered as `"vt6102"` and `"rhine"`. It uses PCI I/O ports, MII helpers, and chained descriptors with cache-line-aligned storage.

The file defines VIA Rhine registers, RX/TX config/control bits, interrupt bits, MII and EEPROM bits, descriptor layout, descriptor status/control flags, ring sizes (`Nrd=64`, `Ntd=64`), receive buffer size, and transmit bounce-copy size. `Ctlr` stores PCI identity, I/O port, MAC address, attach allocation, cache-line size, RX/TX descriptor rings, TX lock/head/tail/use count, command/interrupt state, MII state/link rendezvous, and RX/TX/stat counters.

`vt6102pci()` scans PCI Ethernet class devices for VIA IDs `1106:3065` and `1106:3106`, reserves I/O BAR0, allocates a controller, derives descriptor alignment from PCI cache-line size, rejects too-small alignment, initializes TX FIFO threshold, calls `vt6102reset()`, enables bus mastering, and queues the controller. `vt6102pnp()` selects an inactive controller, populates `Ether`, sets speed to 100 Mbps, and installs callbacks.

Reset starts with `vt6102detach()`, which clears power-management/WOL state for newer revisions and soft-resets the controller. `vt6102reset()` reloads EEPROM, reads the MAC address, configures DMA and RX/TX FIFO thresholds, enables broadcast/all-multicast receive, sets multicast filters to all ones, clears TX loopback/threshold bits, allocates `Mii`, wires `vt6102miimir()`/`vt6102miimiw()`, and probes PHYs. Autonegotiation call is present but commented out.

`vt6102attach()` allocates descriptor and TX bounce-buffer memory, constructs a circular RX descriptor chain with aligned receive blocks and a circular TX descriptor chain, programs RX/TX descriptor base registers, interrupt mask, and command register, then starts a link kernel process. RX descriptors point to allocated blocks and are owned by NIC except for the terminal descriptor setup.

TX completion and enqueue are handled together in `vt6102transmit()`. It frees completed descriptors, records TX error statistics, handles abort/invalid/underflow cases by waiting for TX engine shutdown and restarting descriptor address, then dequeues blocks. If packet data is not 4-byte aligned, it copies a prefix into a per-descriptor bounce buffer and may split the packet across two descriptors; aligned packets use one descriptor. The function tracks aligned/split/copied counts and requests an interrupt when the ring nears full.

`vt6102receive()` walks completed RX descriptors, records RX error bits, otherwise allocates a replacement block, subtracts Ethernet CRC from length, delivers the old block to `etheriq()`, installs the new block, and re-links descriptor ownership through the previous descriptor. `vt6102interrupt()` masks interrupts, acknowledges status, handles link, RX, and TX causes, adjusts TX FIFO threshold upward on underflow, calls receive/transmit handlers, panics on unexpected unhandled bits, and restores the interrupt mask.

`vt6102lproc()` waits on source-change interrupts, calls `miistatus()`, updates the full-duplex bit in the command register, reenables link interrupt, and sleeps. Promiscuous mode toggles `Prom`; multicast is coarse because all-multicast is already enabled. `vt6102ifstat()` reports RX/TX error counters, descriptor/cache stats, interrupt/link counters, TX alignment stats, threshold, and PHY registers.

Notable risks: comments note unresolved link interrupt behavior, incomplete init/reset organization, and untested TX FIFO threshold adjustment. Multicast filtering accepts all multicast. Autonegotiation is not actively started in reset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethervt6102.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethervt6105m.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethervt6105m.c

VIA VT6105M / Rhine III-M Fast Ethernet driver, registered as `"vt6105M"`. It is closely related to `ethervt6102.c` but tailored for device ID `1106:3053`, with a larger receive ring, a reusable receive block pool, checksum flag handling, longer timeouts, and more diagnostics.

The file defines the Rhine III-M register set, including extra configuration, power management, and MII interrupt registers, plus RX/TX descriptors and status/control bits. `Ctlr` tracks descriptor rings, command/interrupt state, MII/link process state, extensive counters, max TX descriptor use, timing accumulation, TX error categories, interrupt error causes, and RX checksum-success counts. `Nrd=196`, `Ntd=64`, and receive buffers include CRC plus slop.

A global receive block pool is managed by `vt6105Mrbfree()` and `vt6105Mrballoc()`. Blocks are reset to a fixed tail-based receive area, checksum flags are cleared, and new blocks are allocated lazily with the custom free callback. This differs from the VT6102 driver, which allocates replacement receive blocks directly.

`vt6105Mpci()` scans PCI Ethernet devices for VT6105M, reserves I/O BAR0, allocates a controller, derives descriptor alignment, sets the TX FIFO threshold to store-and-forward, calls `vt6105Mreset()`, enables bus mastering, and queues controllers. `vt6105Mpnp()` selects an inactive controller, fills `Ether`, sets `mbps` to 1000 as a buffer-size workaround, sets `maxmtu` to `ETHERMAXTU+Bslop`, and installs callbacks.

Reset uses `vt6105Mdetach()` to clear WOL/power state and soft-reset the chip with `Maxus` timeout, which comments say is needed for slow Soekris 5501 resets. `vt6105Mreset()` reloads EEPROM, reads the MAC address, configures DMA/RX/TX thresholds, enables broadcast/all-multicast receive, sets multicast filters to all ones, clears TX config bits, creates MII state, probes PHYs, and starts autonegotiation if immediate `miistatus()` fails.

`vt6105Mattach()` allocates aligned descriptor space with `mallocalign`, builds RX descriptors with checksum-interest bits (`Ipkt|Tcpkt|Udpkt`) and receive blocks from the pool, builds a circular TX ring, programs descriptor base registers and interrupt mask, waits up to about 3.5 seconds for link status, enables TX/RX, and starts the link process. The link process temporarily disables TX/RX while updating full-duplex state, then reenables link interrupts and sleeps.

TX uses one descriptor per packet rather than the VT6102 prefix-bounce split path. `vt6105Mtransmit()` frees completed descriptors, counts abort/invalid/underflow details, restarts the descriptor address after certain TX errors, dequeues output blocks, fills descriptor address/control, uses `Tdctl` in branch fields to suppress interrupts except near ring full, wakes TX, tracks max occupancy, and accumulates cycle timing. `vt6105Minterrupt()` adds more timing accounting, counts abort/underflow/TX-unavailable interrupt causes, adjusts TX FIFO threshold upward on underflow, and calls TX/RX handlers.

`vt6105Mreceive()` handles RX errors, otherwise obtains a replacement block, propagates hardware checksum results into Plan 9 block flags (`Btcpck|Budpck`, `Bipck`) when `Tuok`/`Ipok` are set, subtracts CRC length, delivers the old block, installs the replacement, and returns descriptor ownership via the previous descriptor. `vt6105Mifstat()` reports RX/TX stats, interrupt/link counters, TX occupancy/timing, register snapshots, receive pool size, checksum-success counters, and PHY registers.

Promiscuous mode toggles `Prom`; multicast is coarse because all multicast is already accepted. Notable risks: comments flag cleanup work, unclear receive allocation slop, unresolved link interrupts, and descriptor structure carrying non-hardware fields that should be separated for 64-bit cleanliness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ethervt6105m.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherwavelan.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherwavelan.c

Bus attachment glue for the WaveLAN/Prism wireless Ethernet driver. The hardware operations and core protocol logic live in `wavelan.h` and functions such as `wavelanreset()` and `w_option()`; this file provides PCMCIA and PCI reset/probe paths and registers `"wavelan"` and `"wavelanpci"`.

`wavelanpcmciareset()` allocates a `Ctlr`, sets default I/O base and IRQ when unspecified, reserves I/O ports, locates a PCMCIA card either from explicit `id=` option or by trying names from `wavenames`, calls `wavelanreset()`, then converts option strings from `key=value` to `key value` form and passes them to `w_option()`. On failure it frees I/O and controller state and clears `ether->ctlr`.

The PCI path recognizes two vendor/device pairs: Intersil Prism2.5 `1260:3873` and Linksys WPC-11 `1737:0019` marked untested. `wavelanpciscan()` scans PCI, requires BAR0 MMIO size 4096, maps the register window with `vmap`, stores the PCI device and mapped memory in a controller list, and enables bus mastering.

`wavelanpcireset()` selects an inactive PCI controller, fills IRQ/TBDF, performs a hard reset through `WR_PciCor` with delays and busy polling, calls shared `wavelanreset()`, then applies options with `w_option()`. It does not reserve I/O ports because PCI uses mapped MMIO.

Notable risks: this file assumes external definitions from `wavelan.h` for `Ctlr`, defaults, register access, and reset/option behavior. The Linksys PCI ID is explicitly untested. Option parsing mutates `ether->opt[]` strings in place by replacing `=` with space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherwavelan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/floppy.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/floppy.h

PC floppy-controller declarations and PC-specific setup helpers. Despite the `.h` suffix, this file includes structure definitions, register/command constants, and small function bodies used by the floppy driver.

It declares `FDrive`, `FController`, and `FType`. `FDrive` stores selected media type, BIOS drive type, device number, last touched time, current cylinder, recalibration/confusion state, retry limit, target CHS/length for transfers, and track cache metadata. `FController` embeds a `QLock`, tracks up to four drives, selected drive, data rate, command/status buffers, reset/confusion state, command-completion rendezvous, and motor bitmask. `FType` describes media geometry and formatting parameters plus derived fields for controller byte-code, capacity, and track size.

The enum defines standard PC floppy I/O ports (`0x3f0`-`0x3f7`), digital output/input and main status bits, floppy commands such as recalibrate, seek, sense, read, read ID, specify, write, format, multi-head, dump registers, status-byte masks, and overrun bit.

`pcfloppyintr()` adapts the PC interrupt signature and calls the static driver-level `floppyintr()`. `floppysetup0()` reserves the floppy I/O port ranges and sets `ndrive=2` if successful. `floppysetup1()` reads NVRAM equipment byte `0x10`, extracts drive types for drives 0 and 1, calls `floppysetdef()`, and enables the floppy IRQ through `intrenable()`. `floppyeject()` powers the drive on, bumps its version, and powers it off; the comment says eject is unknown on Safari. `floppyexec()` is a stub that returns the byte count argument.

This header is tightly coupled to the surrounding floppy implementation through static forward declarations for `floppyintr`, `floppyon`, `floppyoff`, and `floppysetdef`. It also depends on PC I/O allocation, NVRAM, and interrupt APIs from `fns.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/floppy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/fns.h

PC architecture function prototype header for the Plan 9 kernel. It includes `../port/portfns.h` and declares the platform-specific services used throughout the PC kernel and by the Ethernet/floppy files in this group.

The prototypes cover boot/architecture setup, BIOS32 calls, CGA posting, clock interrupts, CPU identification, CPUID, cycle counters, delays, DMA setup/count/done/end, floating-point save/restore/init, control-register access, configuration lookup, halt, keyboard/mouse/serial setup, PIT and PIC operations, interrupt/trap enable/disable, port I/O (`inb`, `ins`, `inl`, `outb`, `outs`, `outl`, block string I/O variants), I/O port allocation/reservation/free, ISA config, physical/virtual address mapping, GDT/IDT/TSS operations, memory/MMU/MTRR helpers, NVRAM read/write, PCI config and matching helpers, PCMCIA helpers, process save/restore/setup, MSR access, real-mode call, screen initialization, syscall formatting, temporary page mapping, user transition, TLB flush macro, user-register macro, cache flush no-op, and endian helpers for little-endian BIOS data.

It also declares function pointers for CPU-dependent primitives such as `cmpswap`, `coherence`, `cycles`, `fpsave`, `fprestore`, and `screenputs`. Macros include `PTR2UINT`, `UINT2PTR`, Plan 9 `waserror()` expansion, `KADDR`, `PADDR`, `BIOSSEG`, `L16GET`, and `L32GET`.

For this group, key dependencies are PCI functions (`pcimatch`, `pcisetbme`, `pcisetpms`, config reads/writes), I/O port functions (`ioalloc`, `iofree`, `in*`, `out*`), mapping (`vmap`, `vunmap`, `PCIWADDR` via included headers), delay/microdelay sources from broader headers, PCMCIA functions (`pcmspecial`, `pcmcistuple`, `pcmspecialclose`), interrupt registration (`intrenable`), and NVRAM for floppy setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/fns.h -->