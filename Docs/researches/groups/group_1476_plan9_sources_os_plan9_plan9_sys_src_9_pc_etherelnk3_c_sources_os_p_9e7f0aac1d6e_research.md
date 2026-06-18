# Group Research: group_1476_plan9_sources_os_plan9_plan9_sys_src_9_pc_etherelnk3_c_sources_os_p_9e7f0aac1d6e

Scope: subset A, `sources/os/plan9/plan9`.

Files read completely:
- `sources/os/plan9/plan9/sys/src/9/pc/etherelnk3.c` (2144 lines)
- `sources/os/plan9/plan9/sys/src/9/pc/etherga620.c` (1312 lines)

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherelnk3.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherelnk3.c

## Purpose

This file is the Plan 9 PC ethernet driver for 3Com EtherLink III, Fast EtherLink, and Fast EtherLink XL adapters. It supports ISA, EISA, PCI, PCMCIA, and CardBus-era devices, including 3C509, 3C579, 3C589/3C562, 3C59x Vortex, 3C90x Boomerang/Cyclone/Tornado-class boards, and related OEM variants.

The driver owns hardware discovery, EEPROM access, media selection, reset/setup, PIO and bus-master transmit/receive paths, interrupt handling, per-device statistics, and registration with the generic Plan 9 ethernet layer under `elnk3`, `3C509`, and `3C575`.

## Public Entry Points

- `etherelnk3link()` registers card names with `addethercard`.
- `etherelnk3reset()` is the generic ethernet reset/probe hook. It scans controllers once, binds an unused controller to an `Ether`, reads EEPROM identity and station address, selects media, allocates receive/transmit resources, configures thresholds, and installs callbacks.

Installed `Ether` callbacks:

- `attach()` enables RX/TX, interrupt masks, packet filters, CardBus interrupt acknowledgment, and receive DMA/list priming.
- `transmit()` starts either FIFO/PIO transmit or 3C90x descriptor-based download transmit.
- `interrupt()` handles adapter interrupts and dispatches RX/TX/statistics/error work.
- `ifstat()` formats driver and hardware statistics.
- `promiscuous()` and `multicast()` update receive filters.
- `shutdown()` resets the controller on shutdown.

## Hardware Model

The file defines the 3Com register-window architecture and command/status protocol:

- Common command/status registers at offsets `CommandR`/`IntStatusR`.
- Command opcodes for reset, RX/TX enable/disable, DMA start, interrupt enable/acknowledge, statistics, power, stall/unstall, thresholds, and filters.
- Window 0 setup/EEPROM registers.
- Window 1 operating FIFO/RX/TX status registers.
- Window 2 station address registers.
- Window 3 FIFO/internal config/media options registers.
- Window 4 diagnostics, media status, and bit-banged MII management.
- Window 5 interrupt/filter/threshold state.
- Window 6 statistics.
- Window 7 simple bus-master registers.
- 3C90x extended registers for upload/download descriptor rings.

`Ctlr` stores the selected I/O port, PCI/CardBus metadata, interrupt line, active/attached flags, current media, EEPROM command variant, receive-status format, bus-master mode, locks, current receive buffer, FIFO transmit state, 3C90x upload/download descriptor rings, interrupt/stat counters, queue high-water marks, and CardBus function-memory mapping.

## Discovery Paths

The driver supports multiple bus families:

- `tcm59Xpci()` scans PCI vendor `0x10B7` ethernet-class devices, requires I/O BAR access, allocates I/O space, resets TX/RX, acknowledges stale interrupts, records CardBus-specific EEPROM and function-memory details for device IDs `0x5157` and `0x6056`, and enables PCI bus mastering with `pcisetbme`.
- `tcm5XXeisa()` checks for an EISA machine signature, walks EISA slots, validates 3Com manufacturer/product IDs, enables matching boards, resets them, reads IRQ resources, and records controllers.
- `tcm509isa()` uses the 3Com ISA ID-port activation sequence. `idseq()` emits the magic LFSR identification sequence; `activate()` reads manufacturer/address configuration serially from `IDport`; matching adapters are tagged and activated unless in EISA mode.
- `tcm5XXpcmcia()` accepts caller-supplied PCMCIA types `3C589`, `3C562`, and `589E`.

Controllers are appended to the global `ctlrhead`/`ctlrtail` list by `tcmadapter()`. `etherelnk3reset()` claims the first inactive controller matching the requested `ether->port`, or any inactive controller when no port is specified.

## Reset And Initialization Flow

`etherelnk3reset()`:

1. Performs one-time PCI/EISA/ISA scans.
2. Claims a controller or creates one for a matching PCMCIA card.
3. Fills `ether->ctlr`, `port`, `irq`, and `tbdf`.
4. Reads EEPROM device ID at offset `0x03`.
5. Selects mode:
   - `busmaster = 2` for PCI 3C90x-style descriptor upload/download devices.
   - `busmaster = 1` for 3C59x/Vortex simple bus-master receive devices.
   - `busmaster = 0` for older PIO devices and non-PCI fallback.
6. Reads or preserves the station address, then writes it into window 2.
7. Honors `media=` options and chooses transceiver/media through EEPROM/config bits or autoselection.
8. Configures MII, 100BaseTX/FX, 10BaseT, or 10Base2-specific media status and duplex settings.
9. Clears TX status and statistics.
10. Allocates either a single receive buffer or 3C90x upload/download descriptor rings.
11. Sets TX start and RX early thresholds.
12. Installs generic ethernet callbacks.

`resetctlr()` has extra handling for 905B/CardBus-style devices, including LED/reset-option tweaks for IDs `0x5157` and `0x6056`.

## Media And PHY Handling

The `media[]` table maps option strings to hardware transceiver encodings:

- `10BaseT`
- `10Base2`
- `100BaseTX`
- `100BaseFX`
- `aui`
- `mii`

`autoselect()` probes advertised media, prefers MII when present, otherwise tries 100BaseTX then 10BaseT by programming the transceiver and checking link beat. `setxcvr()` writes either old 3C5x9 address-config bits or newer internal-config transceiver bits. `setfullduplex()` enables full duplex in `MacControl`.

MII access is implemented by bit-banging `PhysicalMgmt`:

- `miimdo()` writes management bits.
- `miimdi()` reads management bits.
- `miir()` performs a full MII read transaction.
- `scanphy()` walks PHY addresses and returns the first plausible PHY, falling back to address 24.

MII negotiation results are used to set `ether->mbps` and full-duplex mode. Options such as `fullduplex`, `100BASE-TXFD`, and `force100` override advertised mode bits.

## Transmit Path

The driver has two transmit implementations:

- `txstart()` handles FIFO/PIO transmission. It drains `ether->oq`, checks `TxFree`, writes packet length and padded packet data to `Fifo`, and arms a `txAvailable` interrupt when FIFO space is insufficient.
- `txstart905()` handles 3C90x download descriptors. It frees completed descriptors by comparing against `DnListPtr`, fills descriptor entries from `ether->oq`, stalls/un-stalls the download engine when appending to a live list, updates queue high-water counters, and starts the download engine if idle.

`transmit()` serializes through `ctlr->wlock` and chooses descriptor or FIFO mode based on `ctlr->dnenabled`.

TX completion and errors are processed in `interrupt()`. Underrun raises the TX threshold; jabber, underrun, and max-collision conditions trigger TX reset and re-enable. Descriptor mode forces a download completion pass after reset.

## Receive Path

The file supports three receive models:

- PIO receive via `receive()`, reading packet data from `Fifo`.
- Simple bus-master upload via `startdma()` and `receive()`, using a single receive buffer and window 7 master registers.
- 3C90x descriptor upload via `receive905()`, walking upload descriptors completed by hardware.

`rbpalloc()` allocates receive blocks with 32-byte alignment for EISA bus mastering. `init905()` allocates and 8-byte-aligns upload and download descriptor arrays, creates receive blocks for upload descriptors, links upload descriptors in a ring, and initializes download-ring bookkeeping.

`receive()` loops while `RxStatus` says a packet is complete, accounts for old-style embedded RX errors or newer `RxError` values, discards errored or unallocatable packets, reads or finalizes data, restarts simple DMA when needed, delivers successful packets with `etheriq`, and rotates the receive buffer.

`receive905()` walks completed upload descriptors, tallies upload error bits, delivers good blocks, replaces delivered buffers, clears descriptor status, un-stalls upload, and tracks receive batching statistics.

## Interrupt Handling

`interrupt()`:
- Validates interrupt status and counts bogus interrupts.
- Saves/restores the current register window.
- Reads timer counters for profiling.
- Handles `hostError` by reading FIFO diagnostics, treating all-ones status/diagnostic on ejectable CardBus IDs as probable ejection, resetting TX or RX paths depending on diagnostic bits, and printing diagnostics.
- Dispatches receive work for `transferInt` and `rxComplete`.
- Acknowledges and handles 3C90x upload completion.
- Processes TX completion stack and TX errors.
- Handles FIFO `txAvailable` and descriptor `dnComplete`.
- Refreshes hardware statistics on `updateStats`.
- Acknowledges currently unused `rxEarly`.
- Panics on unhandled interrupt-mask bits.
- Acknowledges the interrupt latch and CardBus function interrupt when applicable.

The handler uses `ctlr->wlock` to serialize register-window changes and shared TX/RX state.

## Statistics And Control Surface

`statistics()` snapshots window-6 counters into `ctlr->stats`, including upper bits for frame counts and `BadSSD` for MII/100Base media. `ifstat()` forces a statistics refresh and emits:

- interrupt and bogus-interrupt counts
- timer totals
- hardware counters such as collisions, overruns, good frames, bytes received/transmitted
- upload/download queue and interrupt counters when descriptor paths are enabled
- bad SSD count

Receive filter control is intentionally simple. `promiscuous()` and `multicast()` recompute `SetRxFilter` from broadcast, individual, multicast-present, and promiscuous flags. Multicast does not program a hardware address table; it toggles the aggregate multicast receive bit when `ether->nmaddr` is nonzero.

## Dependencies

This driver depends on Plan 9 PC kernel facilities and ethernet abstractions:

- `u.h`, `lib.h`, `mem.h`, `dat.h`, `fns.h`, `io.h`, `error.h`, `netif.h`, `etherif.h`
- Port I/O helpers: `inb`, `ins`, `inl`, `outb`, `outs`, `outl`, `insl`, `outsl`
- PCI helpers: `pcimatch`, `pcisetbme`, `Pcidev`, BAR metadata
- I/O allocation: `ioalloc`, `iofree`
- Memory mapping: `vmap`
- Kernel allocation/block APIs: `malloc`, `free`, `iallocb`, `freeb`, `Block`
- Queue and network delivery: `qget`, `etheriq`
- Timing and ordering: `delay`, `microdelay`, `coherence`
- Generic ethernet registration: `addethercard`

## Review Notes

- The file is hardware-protocol dense. Register-window selection is protected with `wlock` in operational paths, but helper routines assume callers have selected or restored windows correctly.
- The `rxUnderrun` recovery path in `interrupt()` assigns `s = (port+RxFilter) & 0x000F` after selecting window 5. This looks like it intended to preserve the RX filter value but does not read `RxFilter`; review before relying on RX-underrun recovery.
- `shutdown()` prints unconditionally and then resets the controller, which can be noisy during normal halt/reboot.
- `init905()` panics if receive-ring block allocation fails after allocating descriptor memory. That matches kernel-driver expectations but means reset is not graceful under memory pressure.
- CardBus function memory from `vmap` is stored in `ctlr->cbfn`; no unmap path is present in this file.
- Error recovery comments acknowledge uncertainty around active TX reset, bus-master RX restart, and robustness for underrun/host-error cases.
- Autoselection is explicitly described as a limited heuristic. Media-sensitive changes should be validated on representative old 3Com adapters rather than by static review alone.

## Research Guidance

When changing this file, preserve the distinction among PIO, simple bus-master, and 3C90x descriptor paths. Most logic is keyed by `ctlr->busmaster`, `ctlr->upenabled`, `ctlr->dnenabled`, and `ctlr->rxstatus9`; mixing those paths can break older ISA/EISA devices while appearing correct on PCI devices. Changes to reset, interrupt handling, or media selection should be checked against 3C509/3C589-style old register semantics and 3C90x extended descriptor semantics separately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherelnk3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherga620.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherga620.c

## Purpose

This file is the Plan 9 PC ethernet driver for Netgear GA620/GA620T and compatible Alteon Tigon 2 gigabit ethernet adapters, including Alteon AceNIC, DEC DEGPA-SA, and SGI AceNIC variants. It handles PCI discovery, memory-mapped register access, adapter reset, serial EEPROM MAC reads, embedded firmware upload, host/NIC ring setup, transmit/receive processing, firmware event handling, runtime tuning controls, and generic `Ether` registration as `GA620`.

The driver includes `etherga620fw.h`, which supplies the Tigon 2 firmware sections and load/start addresses used during reset.

## Public Entry Points

- `etherga620link()` registers `GA620` through `addethercard`.
- `ga620pnp()` is the reset/probe hook registered with the ethernet layer. It discovers PCI controllers if needed, binds an inactive controller, fills `Ether` identity fields, applies EEPROM or overridden MAC address, initializes runtime structures, and installs callbacks.

Installed `Ether` callbacks:

- `ga620attach()` currently has no extra attach-time work.
- `ga620transmit()` drains queued outbound packets into the send ring.
- `ga620interrupt()` services receive, transmit-completion, event, and replenishment work.
- `ga620ifstat()` reports firmware statistics and driver tunables.
- `ga620ctl()` accepts text commands to tune checksum/coalescing behavior.
- `ga620promiscuous()` and `ga620multicast()` issue firmware commands for receive mode.
- `ga620shutdown()` detaches/resets the adapter.

## Hardware And Firmware Interface

The driver models a firmware-driven NIC interface rather than programming packet movement entirely through raw MAC registers. It defines:

- Memory-mapped CSRs such as `Mhc`, `Mlc`, `Ps`, CPU state/PC registers, mailbox producer/consumer registers, MAC/link registers, DMA configuration, coalescing registers, command ring window, and local-memory window.
- Tigon 2 control bits for endian mode, hard reset, interrupt state, EEPROM bit-banging, SRAM size, PCI command behavior, CPU halt/state, operating mode, local-memory window, and link negotiation.
- Descriptor and control structures shared with firmware:
  - `Host64`
  - event ring element `Ere`
  - command word `Cmd`
  - receive buffer descriptor `Rbd`
  - send buffer descriptor `Sbd`
  - ring control block `Rcb`
  - general information block `Gib`

`Ctlr` stores PCI identity, BAR mapping, EEPROM MAC address, the NIC register pointer, GIB pointer, event/send/receive rings, block side tables, ring indexes mirrored from firmware, interrupt/timing counters, and runtime coalescing/checksum tunables.

Register access goes through:

- `csr32r(ctlr, reg)`
- `csr32w(ctlr, reg, value)`

The implementation assumes the mapped BAR can be treated as an array of 32-bit CSRs.

## PCI Discovery And Reset

`ga620pci()` scans PCI ethernet-class devices and accepts specific vendor/device IDs:

- Netgear GA620 fiber: `vid 0x1385`, `did 0x620A`
- Netgear GA620T copper: `vid 0x1385`, `did 0x630A`
- Alteon AceNIC fiber / DEC DEGPA-SA: `vid 0x12AE`, `did 0x0001`
- Alteon AceNIC copper: `vid 0x12AE`, `did 0x0002`
- SGI AceNIC: `vid 0x10A9`, `did 0x0009`

For a match, it maps BAR0 with `vmap`, allocates a `Ctlr`, records the physical BAR and PCI device, stores the CSR base in `ctlr->nic`, calls `ga620reset()`, and appends successful controllers to the global controller list.

`ga620detach()` performs a hard reset while accounting for unknown endian state by writing reset bits in both byte orders, enables little-endian mode and clear-interrupt behavior, waits for CPU A to halt after EEPROM/flash load, then halts CPU A and CPU B.

`ga620reset()`:
1. Calls `ga620detach()`.
2. Configures SRAM as 512KB banks and synchronous SRAM timing.
3. Initializes PCI state, including read/write command behavior and optional write-and-invalidate cache-line sizing.
4. Sets operating mode to fatal-error reporting, no jumbo fragmentation, byte-swapped DMA data, and word-swapped buffer descriptors.
5. Reads the station address byte-by-byte from AT24C32 serial EEPROM offsets `0x8E` through `0x93`.
6. Uploads firmware text, rodata, data, and zeroed sbss/bss sections into NIC local memory using `ga620lmw()`.

## EEPROM And Local Memory Access

`at24c32io()` is a compact interpreter for serial EEPROM bit operations using `Mlc` bits:

- `C`/`c` clock high/low
- `D` output next data bit
- `E`/`e` enable/disable output
- `I` sample input
- `O`/`o` data high/low
- `:`/`;` define an 8-bit loop

`at24c32r()` performs a random byte read from the AT24C32 EEPROM by issuing start, dummy write of device and address bytes, repeated start, read command, byte read, and stop.

`ga620lmw()` writes or clears NIC local memory through the `Wba`/`Lmw` aperture. It handles window-boundary splitting, uses 32-bit stores, and is used for all firmware sections.

## Runtime Initialization

`ga620init()` configures the runtime host/firmware interface:

- Writes the MAC address to `Mac`.
- Allocates the general information block (`Gib`).
- Allocates the event ring in host memory and points firmware at event producer indexes.
- Clears and initializes the command ring in NIC communications memory.
- Allocates the send ring in host memory, enables optional checksum/coalescing flags, records send consumer indexes, and allocates a parallel `Block*` array for send buffers.
- Allocates the receive standard ring and enables optional receive checksum flags.
- Disables jumbo and mini receive rings.
- Allocates the receive return ring and points firmware at receive-return producer indexes.
- Points firmware statistics refresh at `gib->statistics`.
- Programs DMA read/write configuration.
- Sets transmit buffer ratio.
- Sets default coalescing/timer values:
  - `rct = 1`
  - `sct = 0`
  - `st = 1000000`
  - `smcbd = Nsr/4`
  - `rmcbd = 4`
- Enables DMA assist logic.
- Configures gigabit and 10/100 link negotiation registers.
- Sets interface index and MTU.
- Unmasks interrupts through `Mi` and `Hi`.
- Starts firmware by writing `CPUApc = tigon2FwStartAddr` and clearing `CPUhalt`.

The ring sizes are fixed in enums: event ring 256, command ring 64, send ring 512, standard receive ring 512, jumbo ring 256, mini ring 1024, and receive-return ring 2048. Only the standard receive ring is actively replenished; jumbo and mini rings are disabled.

## Transmit Path

`_ga620transmit()` owns actual transmit work under `ctlr->srlock`:
1. Frees completed send blocks between the host cleanup index `sci[2]` and firmware-updated send consumer index `sci[0]`.
2. Computes the usable send-ring space by leaving one descriptor free.
3. Drains `edev->oq` into send descriptors.
4. Converts block addresses to PCI host addresses with `sethost64()`.
5. Stores `BLEN(bp)<<16 | Fend` into each descriptor.
6. Records each `Block*` in `ctlr->srb`.
7. Updates the send producer index `Spi`.

`ga620transmit()` is the `Ether` callback wrapper. Interrupt handling also calls `_ga620transmit()` so completions and pending outbound packets are serviced together.

## Receive Path

`ga620replenish()` tops up the receive standard ring to `NrsrHI` by allocating `ETHERMAXTU+4` blocks, writing receive descriptors, storing the block pointer in `opaque`, incrementing `nrsr`, and updating `Rspi`.

`ga620receive()` consumes receive-return descriptors while `rrrci != rrrpi[0]`:

- Retrieves the returned descriptor and length.
- Delivers valid nonzero non-error frames with `etheriq`.
- Frees errored or zero-length blocks.
- Clears `opaque`.
- Decrements the source ring fill count based on `Frjr`, `Frmr`, or standard-ring default.
- Advances the receive-return consumer index.

Frame-level errors are not manually tallied in the receive path because firmware statistics are exposed through `ga620ifstat()`.

## Event And Interrupt Handling

`ga620interrupt()` first checks the `Is` bit in `Mhc`. If set, it:
- Records cycle count timing.
- Increments interrupt count.
- Writes `Hi = 1` to mark host interrupt handling.
- Loops over receive completions, transmit cleanup/fill, event processing, and receive-ring replenishment.
- Temporarily clears `Hi` when no work is found on the first idle pass.
- Requires two idle checks before leaving.
- Adds elapsed cycles to `ctlr->ticks`.

`ga620event()` consumes firmware event ring entries and handles:

- `0x01` firmware operational: sends command `0x01` to mark host stack up and command `0x0B` to start link negotiation.
- `0x04` statistics updated: no local action.
- `0x06` link-state changed: updates `edev->mbps` for gigabit or 10/100 and prints link up/down messages.
- `0x07` and unknown events: print diagnostics.

Event consumer index `Eci` is updated after events are processed.

## Runtime Controls And Statistics

`ga620ctl()` parses text commands:

- `coalupdateonly on|off`: toggles `CoalUpdateOnly` in the send-ring control block.
- `hardwarecksum on|off`: toggles TCP/UDP checksum and no-pseudo-header checksum flags in send and receive standard ring controls.
- `rct <n>`: writes receive coalesced ticks.
- `sct <n>`: writes send coalesced ticks.
- `st <n>`: writes statistics ticks.
- `smcbd <n>`: writes send max coalesced BDs.
- `rmcbd <n>`: writes receive max coalesced BDs.

Invalid commands return `-1`; successful commands return the input byte count.

`ga620ifstat()` prints nonzero entries from the 256-entry firmware statistics block, then prints interrupt count, interrupt-mask value `mi`, accumulated handler cycles, checksum/coalescing flags, and coalescing/timer tunables.

`ga620promiscuous()` sends firmware command `0x0A` with flag `1` to enable or `2` to disable promiscuous mode. `ga620multicast()` sends firmware command `0x0E` with flag `1` when adding a multicast address; removal is ignored and individual multicast addresses are not tracked in this file.

## Dependencies

This driver depends on:

- Plan 9 kernel headers: `u.h`, `lib.h`, `mem.h`, `dat.h`, `fns.h`, `io.h`, `error.h`, `netif.h`
- Generic ethernet declarations from `etherif.h`
- Embedded firmware data from `etherga620fw.h`
- PCI discovery/configuration: `pcimatch`, `pcicfgr8`, `pcicfgw8`, `Pcidev`, PCI BAR metadata
- Memory mapping: `vmap`, `vunmap`
- DMA address helpers: `PCIWADDR`
- Allocation helpers: `malloc`, `free`, `xspanalloc`, `iallocb`, `freeb`
- Queue and packet delivery: `qget`, `etheriq`
- Timing: `microdelay`, `cycles`
- Command parsing/stat helpers: `parsecmd`, `readstr`, `snprint`
- Generic ethernet registration: `addethercard`

## Review Notes

- The driver is tightly coupled to firmware structure layout. Any change to `Gib`, `Rcb`, `Rbd`, `Sbd`, ring sizes, command/event meanings, or byte-swap settings must be validated with the included firmware image.
- `ga620pci()` does not unmap BAR memory if `ga620reset()` fails after `vmap`; it frees the controller but leaves the mapping.
- `ga620pci()` also calls `error(Enomem)` if `Ctlr` allocation fails after `vmap`, but the `vunmap()` just before that is present only for the allocation-failure branch, not for later reset failure.
- `ga620init()` uses `waserror()` to free several allocations on failure, but only the pointers initialized before the error are covered. The receive-return ring allocation happens immediately before `poperror()`, so later initialization failures would not be handled by that cleanup block.
- Runtime `ga620ctl()` mutates shared firmware-visible ring control blocks and CSR tunables without explicit locking against interrupts or firmware access.
- `ga620attach()` is intentionally empty; firmware startup is driven during `ga620init()` and operational events rather than attach.
- `ga620shutdown()` prints unconditionally before detaching, which can be noisy during ordinary shutdown.
- The mini and jumbo receive rings are defined but disabled. MTU/jumbo changes require more than changing `IfMTU`.
- `ga620multicast()` enables multicast on additions but ignores removals and does not maintain a filter list.

## Research Guidance

Treat this file as a host/firmware contract. The highest-risk edits are in ring initialization, endian/DMA configuration, interrupt-loop quiescence, producer/consumer index handling, and firmware command/event interpretation. For behavioral changes, inspect `etherga620fw.h` and any firmware-generation provenance before changing shared structures or constants. For performance tuning, prefer runtime `ga620ctl()` parameters first, then validate with receive-ring fill levels, send completion behavior, and interrupt coalescing statistics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherga620.c -->