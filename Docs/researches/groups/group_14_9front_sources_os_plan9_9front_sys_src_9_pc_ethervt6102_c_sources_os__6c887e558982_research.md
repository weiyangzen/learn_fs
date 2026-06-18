# Group Research: group_14_9front_sources_os_plan9_9front_sys_src_9_pc_ethervt6102_c_sources_os__6c887e558982

Scope checked against `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervt6102.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervt6102.c

Implements the Plan 9/9front Ethernet driver for VIA VT6102 Rhine II and compatible Rhine III PCI Fast Ethernet controllers. It registers as both `vt6102` and `rhine`.

Key elements:
- Defines I/O register offsets, control/status bits, descriptor status bits, and FIFO/DMA threshold constants for the Rhine device family.
- Uses a `Ds` descriptor structure whose first four fields are hardware-visible: `status`, `control`, `addr`, and `branch`; software fields track `Block`, bounce buffers, and ring links.
- Maintains `Ctlr` state for PCI identity, port I/O base, RX/TX descriptor rings, interrupt mask state, MII link state, counters, and TX alignment statistics.
- `vt6102pci()` scans PCI Ethernet devices for VIA IDs `0x1106:0x3065` and `0x1106:0x3106`, allocates I/O space, enables PCI, resets hardware, and links controllers into a global list.
- `vt6102reset()` performs device detach/reset, reloads EEPROM MAC address, configures DMA and RX/TX thresholds, accepts broadcast/multicast traffic, and initializes generic MII support.
- `vt6102attach()` allocates aligned RX/TX descriptor memory, RX buffers, and per-TX bounce buffers, then programs RX/TX descriptor base registers and starts the device.
- `vt6102transmit()` reclaims completed TX descriptors, handles TX engine stop cases after abort/underflow, aligns outgoing packets using a small bounce prefix when needed, and kicks transmit demand.
- `vt6102receive()` consumes RX descriptors, accounts receive errors, strips Ethernet CRC, delivers packets with `etheriq()`, and replants buffers.
- `vt6102interrupt()` disables interrupts while servicing, handles link state change, RX, TX, and underflow conditions, dynamically raises TX FIFO threshold on underflow, and reenables the adjusted mask.
- `vt6102lproc()` sleeps on link-change interrupts, polls MII status, and updates full-duplex control.
- `vt6102ifstat()` exposes driver counters, threshold values, and PHY registers.

Filesystem relevance: none directly. This is kernel network hardware support, but it demonstrates Plan 9 driver patterns: PCI probing, DMA-safe descriptor rings, interrupt masking, MII PHY integration, kernel process link management, and `Ether` callback registration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervt6102.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervt6105m.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervt6105m.c

Implements a separate Ethernet driver for the VIA VT6105M Rhine III-M Fast Ethernet controller, registered as `vt6105M`.

Key elements:
- Closely resembles `ethervt6102.c` but targets PCI ID `0x1106:0x3053` and adds Rhine III-M-specific registers, checksum bits, queue wake register definitions, and debug register dumping.
- Uses hardware descriptor rings with `Ds` containing hardware fields plus software `Block` and ring links. RX descriptors include checksum offload control/status bits.
- Defines larger rings than VT6102: `Nrd = 196`, `Ntd = 128`, with receive buffer size `ETHERMAXTU + Crcsz + Bslop`.
- Uses a `Bpool` for receive buffers instead of allocating each RX block directly. This reduces repeated allocation overhead and keeps receive buffers aligned.
- `vt6105Mreset()` resets power management state, reloads EEPROM MAC address, configures DMA as store-and-forward style (`DmaSAF`), accepts broadcast/multicast, initializes MII, and triggers autonegotiation if link status is unavailable.
- `vt6105Mattach()` allocates descriptor memory, grows the RX block pool, sets up RX descriptors with IP/TCP/UDP checksum request bits, configures TX descriptors, starts the NIC, waits briefly for link, enables TX/RX, and launches the link process.
- `vt6105Mreceive()` handles checksum offload results by setting `Btcpck`, `Budpck`, and `Bipck` flags before passing packets to `etheriq()`.
- `vt6105Mtransmit()` queues packets directly without the VT6102 bounce-prefix split logic, uses `Tdctl` to suppress most TX interrupts, and tracks max TX ring occupancy and timing.
- `vt6105Minterrupt()` services RX, TX, link, and error causes, accounts abort/underflow counters, raises TX FIFO threshold on underflow, and uses cycle accounting.
- `vt6105Mifstat()` reports error counters, RX/TX interrupt counters, checksum counts, total cycle time, register snapshots, and PHY registers.
- `edev->maxmtu` is set to `ETHERMAXTU + Bslop`, and `edev->mbps` is set to 1000 as a queue-sizing workaround even though the hardware is Fast Ethernet.

Filesystem relevance: none directly. It is a kernel PCI Ethernet driver and is useful as an example of 9front DMA rings, block pools, RX checksum offload propagation, interrupt deferral, and MII link management.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervt6105m.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherwavelan.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherwavelan.c

Provides PCMCIA and PCI bus attachment glue for the WaveLAN/Prism wireless driver core in `wavelan.h` and related files.

Key elements:
- `wavelanpcmciareset()` allocates a `Ctlr`, applies default I/O port and IRQ values when absent, reserves I/O ports, locates a PCMCIA card either by explicit `id=` option or known `wavenames`, calls shared `wavelanreset()`, and applies remaining options with `w_option()`.
- If PCMCIA setup fails, it frees I/O space, releases the controller, clears `ether->ctlr`, and returns `-1`.
- Defines a small PCI device table for Intersil Prism2.5 `0x1260:0x3873` and an untested Linksys WPC-11 `0x1737:0x0019`.
- `wavelanpciscan()` scans matching PCI devices, validates that BAR0 is a 4 KB memory-mapped register window, maps it with `vmap()`, stores `mmb`, and chains controllers.
- `wavelanpcireset()` picks the first inactive scanned PCI controller, enables PCI, records IRQ/TBDF, performs a hard reset through `WR_PciCor`, waits for command-busy to clear, calls `wavelanreset()`, applies options, and enables bus mastering.
- `etherwavelanlink()` registers two card names: `wavelan` for PCMCIA and `wavelanpci` for PCI.

Filesystem relevance: none directly. The file is small but shows how 9front separates bus-specific discovery/reset from a shared device core and how Plan 9 Ethernet options are passed through to hardware-specific configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherwavelan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherwpi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherwpi.c

Implements the Intel PRO/Wireless 3945ABG `wpi` driver, integrating PCI MMIO hardware setup, firmware loading, DMA rings, 802.11 command handling, and the generic 9front Wi-Fi layer.

Key elements:
- Registers as `wpi` and matches Intel PCI IDs `0x8086:0x4222` and `0x8086:0x4227`.
- Defines register maps for device control, flow handler RX/TX DMA, peripheral registers, firmware boot memory, and NIC internal scheduling/power-management state.
- `Ctlr` tracks PCI/MMIO state, firmware image, EEPROM calibration data, RX/TX queues, shared DMA status page, Wi-Fi state, channel/BSSID/AID, node IDs, power state, and recovery flags.
- `wpiinit()` powers the NIC, validates EEPROM signature, reads MAC address, regulatory domain, channel max power, and calibration power groups, then powers the NIC off.
- `readfirmware()` loads firmware from `/boot/wpi-3945abg` as Eve or `/lib/firmware/wpi-3945abg`, parses it into init/main/boot text and data sections using `crackfw()`.
- `reset()` initializes RX/TX rings, powers on, sets adapter configuration from EEPROM/revision data, programs RX DMA, TX scheduler, TX DMA queues, interrupt masks, and firmware wake flags.
- `boot()` DMA-loads init firmware sections, copies boot microcode into NIC SRAM, waits for alive interrupts, loads main firmware sections, and runs `postboot()`.
- `qcmd()` is the central command/TX queue builder. It waits for queue space, fills command and transmit descriptors, attaches an optional packet block, updates host write pointer, and handles broken-controller state.
- `cmd()` sends synchronous commands through queue 4 and waits for completion using `flushq()`.
- `rxon()` configures station receive mode, BSSID/channel/AID, filters, LED state, TX power tables, broadcast node, and associated BSS node.
- `transmit()` is the Wi-Fi TX callback. It updates RXON state if BSS/channel changed, selects rate and node ID, sets ACK/RTS flags, builds command 28, and queues the packet.
- `receive()` processes firmware notifications and RX descriptors, reclaims TX blocks, handles RX done packets, validates frame status, replants RX buffers, and passes frames to `wifiiq()`.
- `wpiinterrupt()` masks interrupts, acknowledges device and flow-handler interrupts, runs receive processing, marks fatal firmware errors, wakes waiters, and restores interrupt mask.
- `wpirecover()` periodically attempts recovery when `ctlr->broken` is set and RF kill permits operation.
- `wpiattach()` attaches Wi-Fi state, loads firmware, resets and boots firmware, applies options, and starts recovery.
- `wpictl()` supports a `reset` control command by marking the controller broken; otherwise it delegates to `wifictl()`.

Filesystem relevance: indirect only through firmware file reads. This is primarily a firmware-driven wireless network driver and a useful example of Plan 9 device code that loads firmware through kernel name lookup and device read paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherwpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherx550.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherx550.c

Implements a compact Intel X553/X550-AT 10GBASE-T PCI Express Ethernet driver, registered as `iX550`.

Key elements:
- Matches Intel PCI ID `0x8086:0x15c8`.
- Defines MMIO register offsets for control/status, NVM readiness, interrupt control, RX/TX DMA rings, filters, multicast table, VLAN table, checksum control, link status, and MAC frame sizing.
- Uses Intel-style RX descriptors `Rd` and TX descriptors `Td`, plus arrays of `Block*` for packet ownership.
- `Ctlr` tracks PCI/MMIO mappings, descriptor rings, RX/TX indexes, interrupt masks, link/RX/TX rendezvous state, MAC address, multicast table, hardware stats, and speed counters.
- `scan()` maps BAR0 register space and BAR4 MSI-X space, enables PCI, resets the device, enables bus mastering, and stores controllers in `ctlrtab`.
- `detach()` saves the receive address, masks interrupts, issues a full reset, clears extra receive address slots, multicast table, VLAN filter table, and driver-load bit.
- `reset()` waits for EEPROM/configuration/DMA readiness, detaches/resets, clears stats, configures interrupt vector mapping, and programs interrupt throttling.
- `attach()` allocates aligned RX/TX descriptor memory and block pointer arrays, initializes RX/TX rings, marks driver load, and launches link, RX, and TX kernel processes.
- `rxinit()` configures broadcast accept, RX checksum, split/replication buffer size, max frame size, jumbo enable, descriptor base/length, RXDCTL, and RX enable.
- `replenish()` allocates page-aligned receive buffers and fills RX descriptors up to the hardware head.
- `rproc()` replenishes RX descriptors, waits for RX interrupts, consumes completed RX descriptors, sets IP checksum flags, and queues packets to `etheriq()`.
- `txinit()` zeros TX descriptors, programs TX base/length/head/tail, enables TX descriptor control and DMA TX.
- `transmit()` reclaims completed TX descriptors, sends up to eight queued packets per call, and enables TX interrupts when the ring is full or lock contention occurs.
- `interrupt()` masks interrupts, reads causes, wakes link/RX/TX processes, and reenables the remaining mask.
- `lproc()` tracks link status and speed based on `Links`.
- `multicast()` hashes multicast addresses into the 4096-bit multicast table but intentionally does not clear bits on removal because multiple addresses can collide.
- `ifstat()` reports hardware counters, speed transition counts, and RX ring state.

Filesystem relevance: none directly. This file is a PCIe 10GbE driver and illustrates modern Plan 9 Ethernet ring setup, deferred worker processing, checksum flag propagation, and multicast hash filtering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherx550.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etheryuk.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etheryuk.c

Implements the Marvell Yukon-2 family Ethernet driver, registered as `yuk`, covering several Marvell and D-Link PCI IDs.

Key elements:
- Supports devices listed in `vtab`, including `88e8040`, `88e8053`, `88e8055`, `88e8056`, `88e8057`, `88e8071`, `dge-560t`, `dge-550sx`, and `dge-550t`.
- Contains a large register map for PCI config, global CSR, GMAC, PHY, queues, prefetch units, RAM buffers, status rings, timers, and error sources.
- `Chipid` and `idtab` classify Yukon variants and feature flags such as gigabit, new PHY, advanced power, new little-endian checksum format, fiber, and RAM buffering.
- Uses hardware status ring entries represented by `Status`; rings are tracked by `Sring` with write/read pointers, count, mask, and descriptor array.
- `Ctlr` stores PCI state, MMIO views at byte/word/dword widths, ring state, TX/RX block ownership arrays, block pool, multicast list, feature/type/revision data, port number, MAC address, and per-worker rendezvous events.
- `scan()` discovers supported PCI devices and stores lightweight controller records; `setup()` maps MMIO, reads MAC address, allocates aligned status/TX/RX rings, resets and initializes the hardware, and enables bus mastering.
- `identify()` derives Yukon type and revision from chip registers and feature tables, then detects fiber PHYs from PMD type.
- `reset()` disables ASF, resets bus/master state, powers hardware, configures timers/status rings, clears descriptor ownership, resets statistics/status engines, and handles advanced power-management quirks.
- `macinit()` resets MAC/PHY, powers PHY, initializes autonegotiation, clears MIB counters, configures collision/flow/RX/serial mode, programs MAC addresses, initializes FIFO/RAM behavior, and resets per-port RX/TX init state.
- `phyinit()` configures PHY-specific settings, autonegotiation advertisements, gigabit/fiber controls, FE+ workarounds, and PHY interrupt masks.
- `raminit()` partitions on-chip RAM between RX and TX queues when available, otherwise configures FIFO thresholds/store-forward behavior.
- `tproc()` initializes TX ring and sends packets from `e->oq` by writing address and packet descriptors, including 64-bit address descriptors when needed.
- `rproc()` initializes RX ring, enables RX, then continually replenishes receive descriptors from a `Bpool`.
- `sring()` consumes the hardware status ring, dispatches RX checksum notifications, RX completion, and TX completion index updates.
- `rx()` matches RX completion status to an owned buffer, checks status/error flags, sets checksum flags from `cksum()`, and delivers good packets with `etheriq()`.
- `txcleanup()` frees transmitted packet blocks up to a completed hardware index and wakes the TX producer.
- `interrupt()` reads `Isrc2`, which masks interrupts, and wakes `iproc`; `iproc()` handles PHY link changes, hardware errors, queue errors, and status-ring events.
- Error handlers `hwerror()`, `macintr()`, and `eerror()` clear/diagnose hardware, MAC, and queue/prefetch problems, with optional descriptor dumps from `yukdump.h`.
- `multicast()` maintains a linked list of active multicast addresses and rebuilds the 64-bit GMAC hash filter.
- `ctl()` supports `debug` toggling and a `descriptorfu` diagnostic command.

Filesystem relevance: none directly. It is a complex Ethernet driver that demonstrates Plan 9 PCI/MMIO hardware setup, status-ring DMA, block-pool RX replenishment, PHY/autonegotiation management, and deferred interrupt processing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etheryuk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/floppy.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/floppy.h

Defines PC-specific floppy controller structures, register constants, setup functions, and small platform hooks for the generic floppy code.

Key elements:
- Declares generic floppy functions expected elsewhere: `floppyintr()`, `floppyon()`, `floppyoff()`, and `floppysetdef()`.
- `FDrive` records drive type, selected floppy format, device number, last access time, current cylinder, recalibration state, version, max retries, target CHS, transfer length, and a track cache.
- `FController` embeds a `QLock` for exclusive controller access and tracks drive array, selected drive, current data rate, command/status buffers, reset/confused state, rendezvous for command completion, and motor bitmask.
- `FType` describes a floppy media geometry and timing profile: sector size, sectors per track, heads, step rate, tracks, gaps, rate code, plus derived fields such as controller byte code, capacity, and track size.
- Defines I/O ports for PC floppy controller registers: status A/B, digital output, main status, data, disk-change input, and data-rate select.
- Defines command opcodes for recalibrate, seek, sense, read, read ID, specify, write, format, multi-head, and dump registers.
- Defines status bits for readiness, controller direction, busy state, disk change, seek completion, command execution, and overrun.
- `pcfloppyintr()` adapts the PC interrupt signature to the generic `floppyintr()`.
- `floppysetup0()` reserves floppy I/O port ranges and assumes up to two drives when reservation succeeds.
- `floppysetup1()` reads NVRAM equipment byte `0x10` to determine drive types, applies defaults, and enables IRQ `IrqFLOPPY`.
- `floppyeject()` powers the drive, bumps the drive version, and powers it off; the comment notes platform uncertainty.
- `floppyexec()` is a stub that returns the input byte count.

Filesystem relevance: direct but low-level. It supports the block-device side of floppy access by defining controller/drive geometry and PC I/O integration used by higher-level floppy device code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/floppy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/fns.h

Declares the PC architecture function surface for the 9front kernel, after including shared port-layer declarations from `../port/portfns.h`.

Key elements:
- Covers architecture setup and reset: `archinit()`, `archreset()`, `mach0init()`, `trapinit()`, `trapinit0()`, `links()`, `meminit()`, `mmuinit()`, and related boot/memory configuration helpers.
- Declares BIOS32 helpers, real-mode entry, NVRAM access, ACPI/RSD search helpers, and configuration/environment routines.
- Declares CPU identification, CPUID access, cycle counters, delay loops, TSC/i8253 timer routines, MTRR/PAT support, cache/memory barriers, and random buffer generation.
- Declares FPU process lifecycle routines: `fpuinit()`, `fpuprocsetup()`, `fpuprocfork()`, `fpuprocsave()`, `fpuprocrestore()`, plus low-level FP save/restore hooks.
- Declares x86 control/debug register accessors and mutators: CR0-CR4, XCR0, DR registers, TLB flush macro, GDT/IDT/LDT/TSS loaders, and page invalidation.
- Declares DMA, ISA config, PCI config, PCMCIA mapping/special matching, I/O port input/output, interrupt/trap enable/disable, and memory mapping functions.
- Declares console/screen initialization, keyboard/controller routines, serial console allocation, i8253 timer routines, and process context hooks.
- Provides PC-specific macros: `userureg()`, `KADDR()`, `PADDR()`, `dmaflush()`, `evenaddr()`, and `kmapinval()`.
- Many declarations are function pointers selected at runtime, such as `cmpswap`, `coherence`, `cycles`, `fpsave`, `fprestore`, and PCI config accessors.

Filesystem relevance: indirect. This header is central architecture glue used by storage, filesystem, network, and driver code throughout the PC kernel because it exposes low-level I/O, DMA, interrupts, memory mapping, and process context operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/fpu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/fpu.c

Implements x86 floating-point unit initialization, trap handling, process FP state save/restore, and compatibility conversion between x87 and SSE-style `FPsave` layout.

Key elements:
- Defines CR4 feature bits for OS FXSAVE/FXRSTOR, unmasked SIMD exceptions, and XSAVE, though `putxcr0()` is a stub in this file.
- Imports low-level assembly helpers for SSE save/restore, x87 save/restore, and `ldmxcsr()`.
- Uses the SSE/FXSAVE-format `FPsave` structure as the common in-memory representation even on legacy x87-only systems.
- `fpx87save()` calls the raw x87 save routine, converts the x87 tag word into an FXSAVE tag byte, maps x87 state fields to FXSAVE-style fields, copies 80-bit x87 registers into 16-byte slots, and clears padding/MXCSR fields.
- `fpx87restore()` reconstructs the x87 tag word from the FXSAVE-style tag byte and register contents, maps fields back to legacy x87 save layout, and calls the raw restore routine.
- `mathnote()` translates FP status bits into a Plan 9 note such as invalid operation, division by zero, overflow, underflow, precision loss, stack overflow, or stack underflow.
- `matherror()` handles x87 coprocessor errors, clears the external interrupt latch for non-on-chip FPUs, saves FP state, marks it inactive, and posts a note.
- `simderror()` handles SIMD exceptions using MXCSR low status bits.
- `mathemu()` handles device-not-available traps for lazy FPU activation. It initializes first use, restores inactive FP state, saves note-time FP state when required, and checks pending unmasked exceptions before restore.
- `mathinit()` registers traps for coprocessor error, device-not-available, segment overrun, and SIMD error; on family 3 CPUs it also enables IRQ13.
- `fpuinit()` runs per CPU during identification, disables XSAVE, selects SSE or x87 save/restore based on CPUID `Sse|Fxsr`, updates CR4, and turns the FPU off for lazy use.
- `fpuprocsetup()` resets a process to `FPinit`, disables FPU, and frees any saved FP allocation chain.
- `fpuprocfork()` saves the parent active state if needed and copies FP state into the child.
- `fpuprocsave()` saves active FP state on context switch or frees state for moribund processes.
- `fpunotify()`, `fpunoted()`, and `notefpsave()` support Plan 9 note delivery with nested FP state copies so debuggers/handlers can inspect or modify saved FP context.

Filesystem relevance: none directly. It is core process/CPU state management, but it affects all kernel execution by implementing lazy FPU ownership and user-process FP exception delivery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/fpu.c -->