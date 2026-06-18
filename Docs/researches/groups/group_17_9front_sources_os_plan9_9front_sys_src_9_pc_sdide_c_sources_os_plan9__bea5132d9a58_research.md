# Group Research: group_17_9front_sources_os_plan9_9front_sys_src_9_pc_sdide_c_sources_os_plan9__bea5132d9a58

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdide.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sdide.c

## Role

Plan 9/9front SD block driver for legacy ATA/ATAPI IDE controllers, including PCI IDE compatibility/native modes, bus-master DMA, PIO, ATAPI packet devices, SCSI-emulated block requests, and raw ATA pass-through.

## Main Interfaces

- Exports `SDifc sdideifc` named `ide`.
- PnP path: `atapnp()` scans PCI storage controllers and falls back to legacy channels at `0x1f0/0x170`.
- Configured probe path: `ataprobew()` supports explicit controller configuration.
- Runtime callbacks: `ataenable`, `atadisable`, `ataonline`, `atario`, `atarctl`, `atawctl`, `ataclear`, `atastat`, and `ataataio`.

## Key Behavior

- Implements ATA register definitions, IDENTIFY parsing, CHS/LBA/LBA48 addressing, read/write multiple, bus-master PRD DMA, and ATAPI packet transfer.
- `atadrive()` detects ATA vs ATAPI, fills model/serial/firmware, sets FIS signature metadata, sector count, sector size, DMA capabilities, and SCSI inquiry strings.
- `atagenio()` translates standard SD/SCSI read-write commands through `sdfakescsi()` and `sdfakescsirw()`, chunks transfers by controller limits, and retries by disabling DMA or read/write multiple.
- `atapktio()` handles ATAPI packet commands with optional DMA and byte-count-limited PIO data phases.
- `ataataio()` handles raw ATA/FIS-like pass-through, sanitizing host-to-device FIS fields and supporting an out-of-band signature query command.
- Interrupt handling dispatches PIO, DMA, packet, no-data, and reset completions, with missed-interrupt polling fallback in `iowait()`.

## Dependencies And Assumptions

- Depends on Plan 9 SD, PCI, SCSI emulation, and `<fis.h>` ATA/FIS helper functions.
- DMA is passive: BIOS or prior firmware is assumed to have selected valid transfer modes.
- PRD setup assumes DMA buffers are suitably aligned and uses 32-bit PCI addresses.
- Device/controller quirks are encoded through a large PCI ID switch, including Intel ICH, Promise, SiI, VIA, AMD/ATI, Nvidia, Marvell, JMicron, and others.

## Research Notes

- This is the central fallback driver for non-AHCI ATA storage in the PC kernel.
- Error handling is intentionally pragmatic: timeouts abort with NOP or software reset, and repeated failures progressively fall back to simpler transfer modes.
- Several hardware quirks and comments show this driver is compatibility-oriented rather than a clean ATA abstraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdide.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdmv50xx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sdmv50xx.c

## Role

SD driver for Marvell 88SX50xx/60xx SATA host controllers, covering 4-port and 8-port PCI/PCI-X SATA I/II controllers with Marvell EDMA request/response rings.

## Main Interfaces

- Exports `SDifc sdmv50xxifc` named `mv50xx`.
- PnP path `mv50pnp()` matches Marvell vendor `0x11ab` and selected 5040/5041/5080/5081/6041/6081 devices.
- Runtime callbacks include `mv50enable`, `mv50disable`, `mv50verify`, `mv50online`, `mv50rio`, `mv50bio`, `mv50rctl`, `mv50wctl`, and `mv50ata`.

## Key Behavior

- Maps controller MMIO, models chip/drive EDMA register sets, allocates Tx/Rx command queues and PRD tables per drive.
- Maintains a hotplug state machine: `Dnull`, `Dnew`, `Dready`, `Derror`, `Dmissing`, and `Dreset`.
- `satakproc()` periodically checks port status, handles inserted/removed disks, resets unstable links, and identifies new drives.
- `identifydrive()` performs IDENTIFY via PIO registers, extracts geometry and strings, and enables EDMA.
- `mv50bio()` submits read/write SRBs, chunks transfers to 128 sectors because PRD count is 16-bit, waits for completion, and retries reset/re-enable paths.
- `mv50ata()` supports limited raw ATA pass-through for PIO/no-data protocols and FIS signature queries.

## Dependencies And Assumptions

- Depends on Plan 9 SD and `<fis.h>` helpers for ATA identity and FIS handling.
- Uses many Marvell-specific magic values and errata workarounds for PHY calibration, SATA I/II mode toggling, and error handling.
- Uses 32-bit DMA addresses in PRDs.
- ATAPI/queued DMA support is not a focus; request handling is centered on disk read/write and limited pass-through.

## Research Notes

- The driver is heavily hotplug-aware compared with `sdide.c`.
- EDMA queue management is simple and bounded: 31 active slots plus a software pending list.
- Comments and branch names make clear that several behaviors were reverse-engineered or errata-driven.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdmv50xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdmylex.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sdmylex.c

## Role

SD/SCSI host adapter driver for Mylex MultiMaster and compatible BusLogic BT-* controllers, including 24-bit mailbox mode and 32-bit extended mailbox mode. The 24-bit path also supports Adaptec AHA-154xx-style adapters.

## Main Interfaces

- Exports `SDifc sdmylexifc` named `mylex`.
- PnP path `mylexpnp()` scans PCI Mylex devices, EISA IDs, and ISA `scsi` config entries of type `aha1542`.
- Main I/O callback `mylexrio()` dispatches to `mylex24rio()` or `mylex32rio()`.

## Key Behavior

- Defines 24-bit and 32-bit mailbox formats plus corresponding CCB layouts.
- `mylexprobe()` resets the adapter, probes extended setup support, unlocks AHA BIOS mailbox protection when needed, reads adapter ID/DMA/IRQ, and determines narrow vs wide target count.
- `mylex24rio()` builds 24-bit CCBs, stages buffers above 24-bit DMA space through temporary memory, submits through outgoing mailboxes, and waits for interrupt completion.
- `mylex32rio()` builds extended 32-bit CCBs with target/LUN/tag fields and optional tagged queueing.
- Request-sense optimization caches a completed check-condition CCB so a subsequent REQUEST SENSE can return embedded sense data without another adapter command.
- Interrupt paths walk incoming mailboxes, clear mailbox codes, set CCB completion flags, and wake sleepers.

## Dependencies And Assumptions

- Depends on Plan 9 SD/SCSI infrastructure and low-level I/O port access.
- 24-bit mode requires controller and DMA memory below 16 MiB unless a staging buffer is used.
- CCB count is fixed at `NMbox-1`; a TODO notes dynamic allocation is not implemented.
- Wide support is attempted only in the 32-bit path.

## Research Notes

- This is a classic mailbox SCSI driver rather than an ATA/SATA driver.
- The code carefully preserves the synchronous SD request contract: callers do not regain buffers until DMA completion.
- Initialization includes many compatibility paths for old BIOS/ISA/EISA adapter behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdmylex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdodin.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sdodin.c

## Role

SD driver for Marvell Odin II 88SE64xx SATA/SAS controllers. It supports SATA disks, ATAPI packet devices, SAS SSP devices, hotplug state tracking, raw SATA pass-through, and enclosure LED integration.

## Main Interfaces

- Exports `SDifc sdodinifc` named `odin`.
- PnP path `mspnp()` matches Marvell vendor `0x11ab`, device `0x6485`.
- Runtime callbacks include `msenable`, `msdisable`, `msverify`, `msonline`, `msrio`, `msrctl`, `mswctl`, `mswtopctl`, and `msataio`.

## Key Behavior

- Initializes Odin delivery/completion queues, command headers, FIS receive buffer, command tables, and port register windows.
- Uses per-drive state flags for missing, no-power, new, ready, error, reset, offline, and port reset.
- `mskproc()` periodically calls `checkdrive()` to handle PHY status, spin-up, reset, identify/probe, removal, and retry timing.
- SATA path builds ATA register FISes with PRDT entries and uses `<fis.h>` helpers for read/write, identify, set-features, set-transfer-mode, and flush-cache commands.
- ATAPI path builds packet FISes and reports actual transfer length through received FIS data.
- SAS path builds open-address frames and SSP command IUs, parses response/sense data, reads inquiry/VPD/capacity, and maps SAS devices into SD units.
- Interrupt handler processes central, port, command-set, and completion interrupts, wakes command waiters, and marks commands for retry/reset/error based on completion and port error state.
- LED support adds a per-unit `led` file and drives SGPIO LED patterns through `../port/led.h` helpers.

## Dependencies And Assumptions

- Depends on Plan 9 SD/SCSI, PCI, `<fis.h>`, and LED infrastructure.
- Uses 32-bit PCI DMA high-address stubs (`Pciwaddrh(a) 0`), so it assumes usable low DMA addressing.
- Several comments mark uncertain hardware behavior and “wormhole” register accesses.
- Command concurrency is one command object per port, not a deep queue per disk.

## Research Notes

- This is the richest storage driver in this group: it bridges ATA-like SATA, packet ATAPI, and SAS SSP command models.
- Error classification intentionally separates “no verdict” retry paths from definite I/O errors.
- The file doubles as controller support and enclosure-management glue through SGPIO LEDs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdodin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdvirtio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sdvirtio.c

## Role

SD driver for legacy PCI virtio block and virtio SCSI devices.

## Main Interfaces

- Exports `SDifc sdvirtioifc` named `virtio`.
- PnP path `viopnp()` scans vendor `0x1af4`, legacy device range `0x1000..0x103f`, revision `0`, and subsystem type block (`2`) or SCSI (`8`).
- Runtime callbacks include `vioenable`, `viodisable`, `vioverify`, `vioonline`, `viorio`, and `viobio`.

## Key Behavior

- Implements legacy virtqueue layout with descriptor, avail, and used rings allocated page-aligned by `mkvqueue()`.
- `viopnpdevs()` resets devices, reads features, sets acknowledge/driver status, discovers queues, and writes queue physical page numbers.
- `vioblkreq()` builds simple block request chains: request header, optional data buffer, and one-byte status.
- `vioscsireq()` builds virtio SCSI command descriptors, including target/LUN, CDB, optional data buffer, response, sense, and residual handling.
- `viointerrupt()` handles queue completions and falls back to polling completions in `vqio()` if interrupts are missed.
- Block flush commands are translated from SCSI SYNCHRONIZE CACHE opcodes to virtio block type `4`.

## Dependencies And Assumptions

- Depends on Plan 9 PCI and SD/SCSI interfaces.
- Implements the legacy I/O-port virtio interface, not modern PCI capabilities.
- Does not negotiate feature bits beyond reading device features.
- Uses simple direct descriptor chains; no indirect descriptors or multi-segment scatter/gather.

## Research Notes

- The opening comment says “ethernet,” but the file implements block/SCSI storage.
- The block path caps BIOS-style transfer chunks at 32 sectors.
- Stack-allocated request/response structures are safe only because submission waits synchronously for completion before returning.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdvirtio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/segdesc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/segdesc.c

## Role

Architecture debug/control file support for reading and writing per-process x86 GDT and LDT segment descriptors through `/dev/arch` files.

## Main Interfaces

- `segdesclink()` registers arch files `gdt` and `ldt`.
- `gdtread/gdtwrite` operate on the process GDT slots.
- `ldtread/ldtwrite` operate on the process LDT allocation.

## Key Behavior

- Defines textual descriptor types and flag templates for data, code, TSS, LDT, call gates, task gates, interrupt gates, and trap gates.
- Text record format is fixed-width: index, type, flags, DPL, base, and limit.
- `descread()` decodes `Segdesc` entries into type/flag strings.
- `descwrite()` parses records, constructs descriptor words, grows the LDT as needed, updates descriptors, and flushes the MMU for the current process.

## Dependencies And Assumptions

- Depends on x86 descriptor constants such as `SEGP`, `PROCSEG0`, and `NPROCSEG`.
- Write path rejects present system segments unless they are user DPL 3 code/data segments.
- LDT indices are capped below 8192.

## Research Notes

- This is not normal memory-management setup code; it is a controlled inspection/modification interface.
- Permission checks are important because descriptor writes can otherwise install privileged gates or system segments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/segdesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/squidboy.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/squidboy.c

## Role

Multiprocessor application-processor startup code for 32-bit x86 PC kernels.

## Main Interfaces

- `mpstartap(Apic *apic)` prepares and starts an AP through the universal startup algorithm.
- Static `squidboy(Apic *apic)` is the C entry point reached by the AP bootstrap code.

## Key Behavior

- Allocates AP page tables, clones the bootstrap processor page directory, and installs a private `Mach` mapping at `MACHADDR`.
- Creates and registers the AP `Mach` structure, page directory, and GDT storage.
- Writes the AP bootstrap handoff data: C entry address, page directory physical address, and APIC pointer.
- Sets the BIOS warm-reset vector, writes the NVRAM shutdown code, and sends INIT/SIPI through `lapicstartap()`.
- AP entry initializes machine state, MMU, CPU ID, clock, LAPIC, timers, floating-point state, and enters `schedinit()`.

## Dependencies And Assumptions

- Depends on AP bootstrap assembly layout at `APBOOTSTRAP+0x08`.
- Assumes the AP bootstrap physical address is in the low warm-reset segment expected by the code.
- Uses LAPIC/APIC support from `mp.h` and platform clock hooks.

## Research Notes

- This file is small but critical: it bridges low-memory AP bootstrap assembly into the normal kernel scheduler.
- Startup waits up to roughly 100 ms for `apic->online`, updating TSC sync data when TSC is the fast clock.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/squidboy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/trap.c

## Role

Core x86 trap, interrupt, page-fault, syscall, notification, and register-state handling for the PC kernel.

## Main Interfaces

- `trapinit0()` builds the early IDT before malloc is available.
- `trapinit()` installs special handlers after IRQ setup.
- `trap()` is the common trap/interrupt dispatcher except for direct syscall entry.
- `syscall()`, `notify()`, `noted()`, `execregs()`, `forkchild()`, and register helpers define user/kernel transition state.

## Key Behavior

- Initializes all 256 IDT entries from `vectortable`; breakpoint and syscall vectors are DPL 3.
- Dispatches hardware IRQs through `irqhandled()` before exception handling.
- User exceptions post debug notes using `usertrap()`.
- Kernel trap handling has special fixups for segment-register restore faults, `iret` faults, RDMSR/WRMSR faults, and `_peekinst`.
- `fault386()` handles page faults, including `vmapsync()` for kernel mappings and user fault-note delivery.
- Debug-register exceptions post watchpoint notes based on DR6/DR7 state.
- `notify()` builds the user notification frame; `noted()` restores or saves user state based on note action.
- `setregisters()` preserves privileged flags while allowing devproc-style register updates.

## Dependencies And Assumptions

- Depends on x86 vectors, segment selectors, low-level CR/DR/MSR helpers, Plan 9 process notes, and scheduler state.
- Assumes syscall enters directly from assembly and has already built a valid `Ureg`.
- Stack dumping uses kernel text-range heuristics and can be disabled with `*nodumpstack`.

## Research Notes

- The file contains both early-boot fatal trap support and mature user-process exception semantics.
- Kernel fault fixups are tightly coupled to assembly labels used by fork return, segment loads, MSR access, and safe probing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uartaxp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/uartaxp.c

## Role

`PhysUart` driver for AvanstarXp PCI multiport UART cards using an on-board control program and shared control blocks.

## Main Interfaces

- Exports `PhysUart axpphysuart` named `AvanstarXp`.
- PnP path `axppnp()` scans PCI communication devices and matches vendor/device `0x114f/0x6001`.
- Provides standard UART operations: enable, disable, kick, break, baud, bits, stop, parity, modem control, RTS/DTR, status, and FIFO stub.

## Key Behavior

- Defines global control block (`Gcb`) and per-channel control block (`Ccb`) layouts shared with the adapter firmware.
- `axpalloc()` maps PCI runtime registers and local memory, resets the adapter, downloads `uartaxpcp` from `uartaxp.i`, starts it, verifies board type, and creates up to 16 `Uart` channels.
- Channel commands are issued by writing `Ccb.cc` and waiting for firmware to clear it, either by polling or sleeping on command-service interrupts.
- Transmit path writes bytes into the adapter output circular buffer and updates `obwp`.
- Receive interrupt path drains adapter input circular buffers and calls `uartrecv()`.
- Interrupt handler uses doorbell status and xchg-cleared service request registers for input, output, command, modem, and error events.
- Modem-control code tracks CTS/DSR/DCD and hangup conditions.

## Dependencies And Assumptions

- Depends on the generated/included firmware image `uartaxp.i`.
- Requires PCI memory BAR0 and BAR2 mappings.
- Shared service request fields must be accessed using `xchgw()`, as noted by the file.
- FIFO control is a no-op because buffering is handled by adapter firmware/shared memory.

## Research Notes

- Unlike the simple 8250 driver, this is a firmware-mediated multiport serial driver.
- Initialization has several board-seating/distribution-panel failure messages, indicating hardware deployment experience shaped the driver.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uartaxp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uarti8250.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/uarti8250.c

## Role

Generic `PhysUart` implementation for 8250-compatible serial ports, including COM1/COM2 defaults and reusable allocation support for ISA/PCI frontends.

## Main Interfaces

- Exports `PhysUart i8250physuart` named `i8250`.
- `i8250pnp()` returns built-in COM1/COM2 UARTs.
- `i8250alloc()` allocates controller state for external ISA/PCI-discovered ports.
- `i8250console()` selects a boot console from the `console` configuration variable.

## Key Behavior

- Implements standard 8250 register access, sticky write state for interrupt/line/modem control, baud divisor programming, parity/stop/data-bit settings, break signaling, DTR/RTS, modem control, and FIFO trigger setup.
- Detects FIFO availability once by enabling FIFO and reading `Iir`.
- Interrupt handler drains modem, transmit-empty, receive-data, line-status, and timeout interrupts until no interrupt is pending.
- Receive path records overrun/parity/framing/break errors and only passes clean non-break bytes to `uartrecv()`.
- Enable path installs interrupts, sets `Ier/Mcr`, asserts DTR/RTS, and manually invokes the interrupt handler to clear stale pending events after PIC reset.

## Dependencies And Assumptions

- Uses I/O port access and Plan 9 UART core helpers such as `uartstageoutput`, `uartkick`, and `uartrecv`.
- Default COM1/COM2 ports are `0x3f8/0x2f8` with IRQs `4/3`.
- FIFO changes can flush receive data; the code waits for transmitter empty but cannot fully protect RX bytes.

## Research Notes

- This is the base implementation reused by `uartisa.c` and `uartpci.c`.
- The driver supports polling `getc/putc` for console use as well as interrupt-driven operation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uartisa.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/uartisa.c

## Role

ISA discovery wrapper that creates additional 8250-compatible UARTs from kernel configuration.

## Main Interfaces

- Exports `PhysUart isaphysuart` named `UartISA`.
- PnP callback `uartisapnp()` scans `uart2` through `uart5` ISA configuration entries.

## Key Behavior

- Accepts config entries with type `isa`, nonzero port, and nonzero IRQ.
- Defaults frequency to `1843200` if unspecified.
- Allocates I/O port space, creates a controller with `i8250alloc()`, allocates a `Uart`, and binds it to `i8250physuart`.
- Names created ports `COM3` and above based on controller number.

## Dependencies And Assumptions

- Depends entirely on the generic 8250 implementation for runtime behavior.
- Uses `isaconfig()` and `ioalloc()`; it does no probing beyond configured resources.

## Research Notes

- This file is discovery glue, not a UART implementation.
- `isaphysuart` has only `.pnp`; all operational callbacks are nil because returned UARTs use `i8250physuart`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uartisa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uartpci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/uartpci.c

## Role

PCI discovery wrapper for selected 8250-compatible serial cards and serial-over-LAN devices.

## Main Interfaces

- Exports `PhysUart pciphysuart` named `UartPCI`.
- PnP callback `uartpcipnp()` scans PCI communication devices and creates UARTs backed by `i8250physuart`.

## Key Behavior

- `uartpci()` maps I/O BAR space, enables PCI device access, allocates `n` UART records, and creates one `i8250` controller per channel using fixed register spacing.
- Supports StarTech, Oxford/OxSemi, SIIG, Perle PCI-Fast/Ultraport, PLX-bridged serial cards, Intel AMT SOL, and Intel chipset KT controller IDs.
- Handles subsystem-ID-based card selection for generic Oxford and PLX bridge devices.
- `ultraport16si()` performs extra register writes to put Ultraport16si channels into RS-232 mode before binding them.

## Dependencies And Assumptions

- Depends on PCI config access, I/O BAR allocation, and `i8250alloc()`.
- Only supports I/O-port BARs, not MMIO UART register blocks.
- Device support is ID-table-driven and conservative.

## Research Notes

- Like `uartisa.c`, this is enumeration/binding glue over `uarti8250.c`.
- The global `perlehead/perletail` list is used as the accumulated returned UART chain for all matched PCI devices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/uartpci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbehci.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/usbehci.h

## Role

Shared EHCI host-controller definitions for the PC USB 2.0 driver.

## Main Interfaces

- Defines debug print macros tied to `ehcidebug` and endpoint debug flags.
- Declares controller-related opaque types and core structures used by EHCI implementation files.
- Declares `ehcilinkage()`, `ehcimeminit()`, and `ehcirun()`.

## Key Contents

- EHCI capability, operational, status, interrupt, command, port-status, and debug-port bit definitions.
- Typed link constants for iTD, QH, siTD, and FSTN schedule entries.
- Hardware register structures:
  - `Ecapio`: capability registers.
  - `Edbgio`: EHCI debug port registers.
  - `Eopio`: PC operational registers including command/status/intr/frame-list/config/portsc.
- `Ctlr` structure tracks PCI/MMIO identity, operational registers, frame list, async QH list, periodic tree, isochronous state, interrupt counters, DMA allocation hooks, and polling state.

## Dependencies And Assumptions

- Depends on Plan 9 USB endpoint structures and PC PCI/MMIO conventions.
- Operational register layout is PC-specific and assumes EHCI MMIO register spacing.
- 64-bit-capable controller support exists as a register bit, but high address handling is mostly delegated to implementation.

## Research Notes

- This header is the main hardware contract for EHCI code in this directory and `../port` USB code.
- It combines generic EHCI constants with PC-specific operational register mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbehcipc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/usbehcipc.c

## Role

PC-specific PCI discovery, reset, BIOS handoff, and HCI registration glue for the EHCI USB 2.0 driver.

## Main Interfaces

- `usbehcilink()` registers HCI type `ehci` with `addhcitype()`.
- `reset(Hci *hp)` claims an inactive EHCI controller and links it to the generic EHCI HCI implementation.
- Provides HCI `shutdown` and `debug` callbacks.

## Key Behavior

- `scanpci()` finds PCI USB EHCI controllers by class/subclass/programming-interface, maps MMIO BAR0, and builds a static controller list.
- `ehciecap()` walks EHCI extended PCI capabilities.
- `getehci()` performs BIOS-to-OS handoff through legacy support semaphores unless `*noehcihandoff` is set, then disables EHCI SMIs.
- `ehcireset()` disables interrupts, stops the controller, routes ports away while setting up, resets the host controller, clears high address segment when 64-bit capable, and records frame-list size.
- `reset()` honors `*nousbehci`, enables PCI, fills `Hci` port/IRQ/TBDF/port count, initializes EHCI memory, enables bus mastering, installs generic EHCI linkage, and registers interrupts.
- `shutdown()` disables interrupts, resets the controller, stops it, and clears frame-list base.

## Dependencies And Assumptions

- Depends on `../port/usb.h`, `usbehci.h`, PCI enumeration, MMIO mapping, and generic EHCI functions from other files.
- Assumes BAR0 is MMIO and skips I/O BAR controllers.
- Uses only one active claim per scanned controller.

## Research Notes

- This file is platform glue; transfer scheduling and endpoint mechanics live elsewhere.
- BIOS handoff and SMI disabling are the most important PC-specific safety steps before the generic EHCI driver starts running.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbehcipc.c -->