# Group Research: group_1481_plan9_sources_os_plan9_plan9_sys_src_9_pc_sdata_c_sources_os_plan9__bd7f829d9773

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdata.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdata.c

Purpose: Plan 9 `SDifc` driver named `ata` for legacy ATA/ATAPI controllers on PC hardware. It supports legacy ISA-style ATA ports, PCI IDE controllers, ATA disks, ATAPI packet devices, PIO transfers, bus-master DMA, read/write-multiple, 28-bit and 48-bit LBA.

Main structures:
- `Ctlr`: ATA channel state, command/control ports, IRQ, PCI/bus-master data, current drive, interrupt counters, PRD table, register lock.
- `Drive`: per-device ATA/ATAPI identity, geometry, sector count, DMA/RWM capability flags, packet command buffer, fake SCSI sense/inquiry data, active transfer state.
- `Prd`: bus-master IDE physical region descriptor.

Key logic:
- `atapnp`, `ataprobe`, `atadrive`, `ataidentify` detect legacy and PCI IDE channels, distinguish ATA from ATAPI, parse identify words, and build `SDev` instances.
- `ataenable` allocates PRD memory for bus-master DMA, enables PCI bus mastering, registers interrupts, and enables channel interrupts.
- `atario` converts SD requests into ATA or ATAPI operations. It rewrites SCSI read/write(6) to read/write(10), forwards ATAPI packets, and emulates SCSI commands for ATA disks.
- `atagenio` handles ATA disk commands: test-unit-ready, request sense, inquiry, read capacity, read/write(10/16), mode sense, and split transfers by controller limit.
- `atageniostart` programs ATA registers for CHS/LBA/LBA48 and selects DMA, read/write multiple, or sector PIO.
- `atapktio` issues ATAPI packet commands with optional DMA and interrupt-driven packet/data phases.
- `atainterrupt` dispatches PIO read/write, packet, DMA, and standby completions, records status/error, clears current drive, and wakes waiters.
- `atawctl` exposes runtime controls: `dma on/off`, `rwm on/off`, `standby`, and `lba48always`.

Dependencies and integration:
- Uses Plan 9 SD layer via `SDifc sdataifc`.
- Uses PCI helpers (`pcimatch`, `pcicfgr*`, `pcisetbme`), ISA I/O allocation, interrupt registration, SCSI helper functions (`scsiverify`, `scsionline`, `scsibio`), and port I/O helpers (`inb`, `outb`, `inss`, `outss`).
- Contains controller-specific PCI quirks for Intel ICH, Promise, Silicon Image, VIA, AMD, NVIDIA, ATI, HighPoint, CMD, ServerWorks, and others.

Risks and notes:
- DMA setup assumes physically contiguous/valid PCI addresses and splits only by controller span; bad mappings or boundary assumptions can fail I/O.
- Many hardware timing loops are fixed microsecond/millisecond waits; marginal disks may time out or require reset.
- ATAPI DMA has fallback and disables DMA after repeated trouble, but error recovery is mostly abort/reset based.
- Several debug paths are compile-time gated by `DEBUG`; normal diagnostics are sparse unless flags change.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdiahci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdiahci.c

Purpose: Plan 9 `SDifc` driver named `iahci` for AHCI SATA controllers. It handles PCI discovery, AHCI HBA setup, SATA drive state management, read/write DMA commands, ATAPI packet commands, SMART, cache flush, hotplug/media-change detection, and reset/recovery.

Main structures:
- `Ctlr`: AHCI controller state, PCI device, mapped HBA registers, raw/active drive arrays, enabled flag, interrupt counters.
- `Drive`: per-port state, associated `SDunit`, AHCI port and memory structures, disk state, negotiated SATA mode, identity data, serial/model/firmware strings, media-change flag, interrupt-jabber tracking.
- `Aportc`/`Aportm` from `ahci.h`: command-list, FIS, command-table, and per-port runtime state used by this file.

Key logic:
- `iapnp` scans PCI for Intel/ATI/Marvell/generic AHCI-like controllers, maps MMIO BAR, optionally forces Intel AHCI mode, configures HBA, and creates `SDev`s.
- `newctlr` maps implemented HBA ports into Plan 9 units, idles ports, and calls `configdrive`.
- `ahciconfigdrive`, `ahciidle`, `ahciquiet`, `ahcicomreset`, `ahciswreset`, and `ahciportreset` implement port initialization and reset paths.
- `satakproc` periodically runs `checkdrive` for all known drives, driving the state machine from missing/new/reset/error/offline to ready.
- `iainterrupt` reads HBA interrupt status, calls `updatedrive` for each active port, acknowledges interrupts, and detects interrupt storms.
- `iario` builds and submits AHCI read/write FIS commands for non-ATAPI disks. It handles SCSI flush commands and uses `sdfakescsi` for non-I/O SCSI emulation.
- `iariopkt` builds ATAPI packet commands for packet devices, including mode-sense handling through `sdmodesense`.
- `iarctl` and `iawctl` expose per-drive diagnostics/control: model/serial/firmware, SMART status, flags, registers, geometry, `change`, `flushcache`, `identify`, `mode`, `nop`, `reset`, `smart`, `smartenable`, `smartdisable`, and forced state.
- `iartopctl` reports controller-wide AHCI capability bits and port maps.

Dependencies and integration:
- Uses Plan 9 SD layer through `SDifc sdiahciifc`.
- Depends on `ahci.h`, PCI helpers, interrupt registration, `sdfakescsi`, `sdsetsense`, `sdmodesense`, and generic EHCI-style register memory coherence primitives.
- Uses a background kernel process for hotplug/spin-up polling.

Risks and notes:
- Uses only command slot 0 and caps normal disk I/O chunks to 128 sectors; it is simple rather than NCQ-oriented.
- Several reset and wait paths are timeout based and interact with a polling state machine; transient SATA link states can surface as retries or offline transitions.
- `resetdisk` marks `Ferror` under a condition that is logically always true (`state != Dready || state != Dnew`), likely intentional broad wakeup behavior but suspicious.
- Contains controller-specific Intel setup and generic fallback matching; unsupported AHCI variants may need quirks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdiahci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdmv50xx.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdmv50xx.c

Purpose: Plan 9 `SDifc` driver named `mv50xx` for Marvell 88SX50xx/60xx SATA controllers, especially multi-port fileserver cards. It implements controller discovery, EDMA ring setup, SATA PHY/reset handling, drive identify, interrupt completion, and read/write SD I/O.

Main structures:
- `Ctlr`: PCI/MMIO controller state, chips, drives, interrupt identity, mapped register windows.
- `Chip`: group of four ports, with `Arb` and `Edma` register blocks.
- `Drive`: per-port state, `SDunit`, bridge/EDMA register pointers, SATA mode/state, identity data, EDMA rings, outstanding SRB table and queue.
- `Srb`: software request buffer representing one read/write command.
- `Prd`, `Tx`, `Rx`: card-visible DMA descriptor, request, and response entries.

Key logic:
- `mv50pnp` scans Marvell vendor devices, accepts supported device IDs, maps BAR0, initializes chip/port register pointers, and creates an `SDev`.
- `mv50verify` configures a unit/drive, initializes EDMA memory, applies type-specific interrupt masks and PHY state, resets the disk, and unmasks interrupts.
- `resetdisk`, `phyerrata`, and `enabledrive` handle Marvell-specific EDMA reset and SATA PHY tuning.
- `identifydrive` issues ATA identify via programmed I/O, parses LLBA support, sector count, model/firmware/serial, fills inquiry data, and transitions the drive to ready.
- `startsrb` writes one EDMA request entry and PRD, fills ATA registers through `mvsatarequest`, advances the request ring, and tracks the SRB by command ID.
- `completesrb` drains response entries, marks SRBs done/error, wakes waiters, and starts queued SRBs.
- `mv50interrupt` decodes per-port interrupt cause, updates drive state, and drains completed SRBs.
- `satakproc` periodically runs `checkdrive`, handling new/missing/error/reset states and retrying mode/reset/identify.
- `mv50rio` accepts SCSI read/write(10), uses `sdfakescsi` for metadata commands, chunks I/O to 128 sectors, submits SRBs, waits for completion, and retries failed/no-completion requests.
- `mv50rctl` dumps model/serial/firmware, geometry, identity words, and controller/arb/bridge/EDMA registers.

Dependencies and integration:
- Uses Plan 9 SD layer through `SDifc sdmv50xxifc`.
- Relies on PCI matching, MMIO mapping, interrupt registration, `sdfakescsi`, Plan 9 kernel sleeps/wakeups, and physical address macros.

Risks and notes:
- EDMA PRD byte count is 16-bit, so I/O is limited to 128 sectors per SRB.
- PHY errata code contains hardware magic and revision-specific behavior; it is fragile but likely necessary for these controllers.
- `enabledrive` assigns `d->bridge->status = 0x113` inside an `if`, forcing `Dnew`; this is noteworthy and may be deliberate hardware forcing, but reads like a bug.
- No ATAPI path is implemented; only disk read/write and faked SCSI metadata are handled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdmv50xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdmylex.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdmylex.c

Purpose: Plan 9 `SDifc` driver named `mylex` for Mylex MultiMaster/BusLogic BT-series SCSI host adapters, supporting both 24-bit and 32-bit mailbox/CCB modes. It also supports AHA-1542-like 24-bit mailbox behavior.

Main structures:
- `Ctlr`: adapter I/O port, SCSI ID, bus mode, IRQ, wide mode, PCI device, mailbox state, CCB free list, and cached check-condition CCBs.
- `Mbox24`/`Mbox32`: outgoing/incoming mailbox formats for 24-bit and 32-bit controllers.
- `Ccb24`/`Ccb32`: command control blocks for 24-bit and 32-bit commands, including CDB, sense storage, DMA address fields, status fields, rendezvous, and free-list link.

Key logic:
- `mylexpnp` probes PCI Mylex devices, EISA signatures, and ISA `scsi` config entries of type `aha1542`.
- `mylexprobe` resets the controller, detects 24-bit vs 32-bit mode using extended setup inquiry, unlocks some AHA BIOS-protected mailbox interfaces, reads adapter SCSI ID/DMA/IRQ, and creates an `SDev`.
- `mylex24enable` allocates 24-bit-addressable mailbox/CCB memory, seeds the CCB free list, and initializes the board mailbox interface.
- `mylex32enable` allocates 32-bit mailbox/CCB memory, sets sense pointers, optionally enables wide mode, and initializes extended mailboxes.
- `mylexrio` dispatches requests to `mylex24rio` or `mylex32rio`, rejecting the adapter target ID and unsupported narrow targets.
- `mylex24rio` builds a 24-bit CCB, stages data through low memory if the request buffer is above 24-bit addressability, posts an outgoing mailbox, waits for completion, handles residual length and check-condition sense caching.
- `mylex32rio` builds a 32-bit CCB, includes target/LUN/tag fields, posts a mailbox, waits for completion, handles residual length and sense caching.
- `mylex24interrupt` and `mylex32interrupt` clear adapter interrupts, scan incoming mailboxes, recover the CCB pointer, mark it done, and wake the sleeping request.

Dependencies and integration:
- Uses Plan 9 SD layer through `SDifc sdmylexifc`.
- Uses generic SCSI verification/online/bio helpers; this driver passes CDBs directly to the adapter rather than translating to ATA.
- Uses port I/O, PCI/EISA/ISA discovery helpers, DMA/physical address macros, and Plan 9 rendezvous wait/wakeup.

Risks and notes:
- 24-bit mode requires bounce buffering for high physical addresses; allocation failure returns `SDmalloc`.
- Number of CCBs is fixed at `NMbox-1`; TODO notes mention dynamic allocation was not implemented.
- No disable/clear hooks are provided in the `SDifc`, so teardown is minimal compared with newer drivers.
- Several initialization waits are busy loops with no timeout beyond prior reset polling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sdmylex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/trap.c

Purpose: Core x86 PC trap, interrupt, syscall, note, and process-register handling for the Plan 9 kernel.

Main structures/globals:
- `vctl[256]`: vector table of registered trap/interrupt handlers.
- `vctllock`: protects handler registration/removal.
- `intrtimes[256][Ntimevec]`: histogram of interrupt service times.
- External/implicit core structures: `Ureg`, `Mach`, `Proc`, `Tos`, `Vctl`.

Key logic:
- `trapinit0` builds the IDT very early, before malloc, installing interrupt gates for all vectors and giving user privilege to breakpoint and syscall vectors.
- `trapinit` registers special handlers for breakpoint, page fault, double fault, and unexpected vector 15; enables NMI; exposes `irqalloc`.
- `intrenable` creates a `Vctl`, asks `arch->intrenable` for a vector, chains compatible handlers on shared vectors, and records ISR/EOI callbacks.
- `intrdisable` removes a registered interrupt handler and disables the hardware IRQ when no handlers remain.
- `trapenable` registers non-IRQ trap handlers below `VectorPIC`.
- `trap` is the central dispatcher: handles registered vectors, calls ISR/handler/EOI, accounts interrupt time, posts notes for user exceptions, fans out unknown interrupts to all registered IRQ handlers as a spurious fallback, and panics on kernel traps.
- `fault386` handles page faults using CR2, delegates VM sync for kernel vmaps, calls `fault`, and posts debug notes or panics.
- `syscall` validates syscall entry from user mode, handles tracing, copies user args, dispatches `systab`, stores return value/error state, processes `noted`, notes, and delayed scheduling.
- `notify` builds the user-space note frame and redirects execution to the process notify handler.
- `noted` validates and restores a user-provided `Ureg` after note handling, with `NCONT`, `NRSTR`, `NSAVE`, `NDFLT`, and invalid-argument behavior.
- Helpers include `dumpregs`, stack dumping, `validalign`, `execregs`, `userpc`, `setregisters`, `kprocchild`, `forkchild`, `setkernur`, and `dbgpc`.

Dependencies and integration:
- Tightly integrated with x86 architecture hooks (`arch->intrenable`, IDT vectors, CR registers), Plan 9 scheduler/proc/note/syscall systems, page fault machinery, and `devarch` file exposure.
- Includes generated syscall tables from `../port/systab.h`.

Risks and notes:
- Interrupt sharing depends on matching ISR/EOI callbacks for chained handlers.
- Unknown interrupt fallback calls every registered interrupt routine, which can help shared/spurious cases but may be costly or surprising.
- User note restoration carefully preserves protected flags/segments, but invalid user frames lead to process suicide.
- Several panic paths intentionally dump registers/stack for kernel faults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartaxp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartaxp.c

Purpose: `PhysUart` driver named `AvanstarXp` for Avanstar Xp PCI multiport UART cards. The card runs downloaded control firmware and exposes a global control block plus per-channel control blocks in mapped local memory.

Main structures:
- `Gcb`: global control block with command/status words, service request bitmaps, board type, control program version, and CCB layout metadata.
- `Ccb`: per-channel control block with baud/data/line protocol, input/output circular buffer descriptors, modem/error/status fields, and command/status words.
- `Cc`: embeds `Uart` and tracks channel number, CCB pointer, and controller.
- `Ctlr`: PCI device, mapped registers/memory, GCB pointer, interrupt mask, and up to 16 channels.

Key logic:
- `axppnp` scans PCI communication devices for AvanstarXp ID `114f:6001`.
- `axpalloc` maps PCI runtime registers and local memory, resets the adapter, downloads `uartaxpcp` firmware from `uartaxp.i`, starts it, waits for ready, validates board type, and builds channel `Uart`s.
- `axpenable` enables interrupts when requested, asserts DTR/RTS, configures modem control ownership, sets output low watermark, and enables Tx/Rx.
- `axpdisable` drops DTR/RTS, disables Tx/Rx, flushes buffers, and unregisters interrupt when no channels remain enabled.
- `axpinterrupt` handles global doorbell interrupts and atomically drains input, output, command, modem, and error service request bitmaps with `xchgw`.
- `axprecv` drains the card input ring into `uartrecv`; `axpkick` fills the output ring from staged UART output.
- Control methods implement baud, bits, stop, parity, break, modem control, RTS/DTR, FIFO no-op, and status reporting.

Dependencies and integration:
- Implements Plan 9 `PhysUart axpphysuart`.
- Uses `devuart` helpers (`uartrecv`, `uartkick`, `uartstageoutput`), PCI/MMIO mapping, interrupt registration, and the bundled firmware array `uartaxpcp`.

Risks and notes:
- Correct operation depends on downloading and starting card firmware successfully.
- Channel commands either busy-wait before interrupts are enabled or sleep on command service interrupts afterward.
- Error-service handling appears to read `cc->ccb->ms` while checking communication errors, which is unusual because error bits are defined for `ces`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartaxp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uarti8250.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/uarti8250.c

Purpose: Generic `PhysUart` driver named `i8250` for 8250-compatible serial ports, including COM1/COM2 and other wrappers that allocate i8250 controller state.

Main structures:
- `Ctlr`: I/O base, IRQ, PCI tag, interrupt-enabled flag, sticky register shadows, FIFO capability/status, and lock.
- Static `i8250ctlr[2]`/`i8250uart[2]`: built-in COM1 and COM2 definitions.

Key logic:
- Register constants define standard 8250/16450/16550-compatible UART registers and bits.
- `i8250enable` detects FIFO support, optionally registers the interrupt handler, enables received-data and THR-empty interrupts, sets modem IRQ-enable bit, asserts DTR/RTS, and clears pending interrupt events.
- `i8250disable` drops DTR/RTS, disables FIFO and interrupts, and unregisters IRQ if active.
- `i8250interrupt` loops until no pending interrupt, handling modem status changes, THR-empty transmit, and received data/line status/timeouts.
- `i8250kick` writes staged output while THR is empty, bounded to 128 bytes per call.
- `i8250fifo`, `i8250baud`, `i8250bits`, `i8250stop`, `i8250parity`, `i8250break`, `i8250modemctl`, `i8250rts`, `i8250dtr`, and `i8250status` implement `devuart` operations.
- `i8250getc`/`i8250putc` provide polled console I/O.
- `i8250alloc` lets ISA/PCI glue create additional i8250-compatible ports.
- `i8250config`, `i8250console`, `i8250mouse`, and `i8250setmouseputc` wire console and mouse serial uses.

Dependencies and integration:
- Implements Plan 9 `PhysUart i8250physuart`.
- Used directly for COM1/COM2 and indirectly by `uartisa.c` and `uartpci.c`.
- Depends on port I/O, interrupt registration, and `devuart` queue/staging helpers.

Risks and notes:
- FIFO changes can flush hardware FIFOs; code waits for transmitter empty but receive-side loss is still acknowledged as unavoidable.
- Uses sticky shadow registers because some UART registers are write-only or stateful.
- Console configuration is driven by the `console` config string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartisa.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartisa.c

Purpose: ISA bus wrapper `PhysUart` named `UartISA` that discovers configured ISA UARTs and exposes them through the generic i8250 backend.

Key logic:
- `uartisapnp` scans `isaconfig("uart", ctlrno, &isa)` for controller numbers 2 through 5.
- Accepts only entries of type `isa` with nonzero port and IRQ, defaulting frequency to 1.8432 MHz.
- `uartisa` allocates the I/O range, allocates a `Uart`, creates an i8250 controller via `i8250alloc`, names it `COM%d`, and points `uart->phys` at `i8250physuart`.

Dependencies and integration:
- Delegates all runtime UART operations to `i8250physuart`.
- Uses ISA config parsing, I/O allocation, and `i8250alloc`.

Risks and notes:
- The `isaphysuart` vtable contains only `pnp`; returned UARTs must use `i8250physuart` for actual operation.
- Starts at controller number 2, leaving built-in COM1/COM2 to `uarti8250.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartisa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartox.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartox.c

Purpose: `PhysUart` driver named `OXPCIe95x` for Oxford Semiconductor OXPCIe95x PCIe multiport UARTs.

Main structures:
- `Ctlr`: PCI device, mapped MMIO registers, interrupt mask, name, and up to 16 ports.
- `Port`: embeds `Uart`, points to controller and per-port MMIO window, tracks FIFO trigger level and modem output state.

Key logic:
- `oxpnp` scans Oxford vendor `0x1415` devices, recognizes OXPCIe952/954/958 IDs, maps BAR0, reads UART count, creates one `Port` per UART, and chains them into the UART list.
- `oxenable` registers the shared interrupt when first port is enabled, enables per-port interrupt mask, enters 950 enhanced mode, enables Rx status/THRE/Rx-ready interrupts, asserts DTR/RTS, and enables FIFO.
- `oxdisable` drops DTR/RTS, disables FIFO and per-port interrupts, and unregisters the shared IRQ when no ports remain enabled.
- `oxinterrupt` checks global interrupt status and handles receive, transmit-empty, and modem-status events for enabled ports.
- `oxkick` writes staged output while THR empty.
- `oxbaud` supports standard baud rates by programming table-derived DLM/DLL values.
- `oxbits`, `oxstop`, `oxparity`, `oxmodemctl`, `oxrts`, `oxdtr`, `oxdobreak`, `oxstatus`, and `oxfifo` implement UART operations.

Dependencies and integration:
- Implements Plan 9 `PhysUart oxphysuart`.
- Uses PCI/MMIO mapping, interrupt registration, and `devuart` helpers.

Risks and notes:
- Baud support is limited to explicit table values from the device datasheet.
- The interrupt handler uses a single interrupt-status read per port and does not loop until all pending causes are drained.
- FIFO support is tailored to 950-mode 128-byte FIFOs and only controls receive trigger levels.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartpci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartpci.c

Purpose: PCI wrapper `PhysUart` named `UartPCI` that recognizes specific PCI serial adapters and exposes their ports through the generic i8250 backend.

Key logic:
- `uartpcipnp` scans PCI communication devices, including some "other" serial class variants, and matches known StarTech, Oxford, SIIG, PLX/Perle, and Ultraport boards.
- `uartpci` allocates I/O BAR space, creates `n` `Uart` objects, allocates per-port i8250 controller state, assigns per-device frequency, names the ports, and appends them to a global Perle/PCI UART list.
- `ultraport16si` writes board-specific registers to force RS232 mode before exposing 16 ports as i8250-like UARTs.
- Subsystem IDs are used for Oxford and PLX/Perle devices to distinguish board layouts and oscillator frequencies.

Dependencies and integration:
- Delegates all actual serial operations to `i8250physuart`.
- Uses PCI config reads, I/O allocation, `i8250alloc`, and the Plan 9 UART list convention.

Risks and notes:
- Only known device/subsystem IDs are supported; unknown Oxford/Perle variants are printed and skipped.
- Some matched cards expose multiple BARs/port groups and are appended to a shared list.
- The `pciphysuart` vtable only provides `pnp`; returned UARTs use `i8250physuart`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uartpci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uncached.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/uncached.h

Purpose: PC-specific note for the port layer that uncached memory is not required on this architecture.

Content:
- The file contains only a comment stating that processor accesses, memory caches, and DMA are coherent on PC hardware, so uncached memory is unnecessary.

Dependencies and integration:
- Intended as an architecture override/header included by code that otherwise may need uncached memory handling on non-coherent platforms.

Risks and notes:
- The assumption is broad for the supported Plan 9 PC target. Drivers still use explicit `coherence()` where required for device-visible descriptor updates.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/uncached.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbehci.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbehci.h

Purpose: PC-specific/shared header for the EHCI USB 2.0 host-controller driver. It overrides debug macros, forward-declares EHCI-private structures, defines the controller and operational register structures used by PC EHCI code, and declares linkage functions.

Main structures:
- `Poll`: lock/rendezvous pair with `must`/`does` counters for polling coordination.
- `Ctlr`: EHCI controller runtime state, including PCI device, capability/operational registers, periodic frame list, async QH list, interrupt tree, iso list, load counters, interrupt counters, request count, and poll state.
- `Eopio`: EHCI operational register layout, including command, status, interrupt enable, frame index, segment, frame-list base, async link, config, and port status/control array.

Key declarations:
- Debug macros depend on `ehcidebug` and per-endpoint debug.
- Externs: `ehcidebug`, `ehcidebugcapio`, `ehcidebugport`.
- Functions supplied elsewhere: `ehcilinkage`, `ehcimeminit`, `ehcirun`.

Dependencies and integration:
- Used by `usbehcipc.c` and the generic EHCI implementation under `../port`.
- Depends on EHCI capability register definitions from `portusbehci.h` and USB/HCI structures.

Risks and notes:
- `Eopio` uses a one-element flexible-style `portsc[1]`; code must rely on actual mapped register space for all ports.
- `Ctlr` mixes interrupt, async, periodic, and isochronous state and must be used under the documented locks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbehcipc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbehcipc.c

Purpose: PC-specific EHCI host-controller discovery/reset glue for Plan 9 USB. It scans PCI for EHCI controllers, maps registers, claims legacy BIOS ownership, resets/configures the controller, initializes generic EHCI memory/linkage, and registers the `ehci` HCI type.

Main logic:
- `scanpci` finds PCI USB controllers with programming interface `0x20`, maps BAR0, validates IRQ, allocates `Ctlr`, records capability and operational register pointers, enables PCI bus mastering and power state, and stores controllers in `ctlrs`.
- `getehci` walks the EHCI extended capability list to find legacy support, requests OS ownership from BIOS, waits for BIOS semaphore clear, disables SMIs, and clears config routing.
- `ehcireset` stops the controller, disables legacy mode, reclaims from BIOS, clears 64-bit segment register if needed, resets the controller unless it is the debug controller, sets interrupt threshold, and records frame-list size.
- `reset` honors `*maxehci` and `*nousbehci`, selects an inactive controller matching optional `hp->port`, fills `Hci` port/IRQ/TBDF/nports fields, calls `ehcireset`, `ehcimeminit`, and `ehcilinkage`, and installs shutdown/debug callbacks.
- `shutdown` resets/stops the controller and clears frame-list base.
- `usbehcilink` registers the HCI type name `ehci`.

Dependencies and integration:
- Uses Plan 9 USB HCI layer (`addhcitype`, `Hci`), generic EHCI code via `ehcilinkage`/`ehcimeminit`/`ehcirun`, PCI helpers, MMIO mapping, and power/bus-master setup.
- Includes `../port/usb.h`, `../port/portusbehci.h`, and local `usbehci.h`.

Risks and notes:
- `scanpci` is one-shot via `already`; controllers appearing later are not discovered.
- `maxehci` defaults to `Nhcis` but can limit active controllers; comments note some systems wedge with multiple EHCI controllers.
- Legacy BIOS handoff has a bounded wait and logs timeout but continues with SMI disabling/control clearing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbehcipc.c -->