# Group Research: group_1480_plan9_sources_os_plan9_plan9_sys_src_9_pc_memory_c_sources_os_plan9_bd36f6d4ba17

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/memory.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/memory.c

PC bootstrap memory discovery and physical address map management. The file owns early RAM/UMB/UPA maps, BIOS signature searches, E820 probing, fallback physical RAM probing, and the public allocators used by low-level device and kernel setup code.

Key elements:
- Defines `Map` and `RMap` free-list style maps for RAM, upper memory blocks, writable UMB device memory, and unbacked physical address space.
- `mapfree`, `mapalloc`, `mapprint` implement sorted range insertion, coalescing, and aligned/specific allocation.
- `rampage` allocates early page-table pages directly from `rmapram`, before normal kernel allocators are ready.
- `umbscan`, `umbexclude`, `umbmalloc`, `umbrwmalloc` manage 640K-1M device/ROM/window memory.
- `sigsearch` scans EBDA/base memory/BIOS ROM for firmware tables such as MP and ACPI signatures.
- `lowraminit` adds conventional memory and the gap between kernel end and `MemMin`.
- `e820scan` invokes BIOS INT 15h E820 through `realmode`, sorts entries, and maps low 32-bit memory.
- `ramscan` is the fallback CMOS/probe path, dynamically building page tables while testing memory 1MB at a time.
- `meminit` sets special VGA/BIOS cache attributes, scans memory, and fills `conf.mem`.
- `upaalloc`, `upafree`, `upareserve` provide physical address space allocation for device BAR-like needs.

Interactions:
- Calls MMU helpers `mmuwalk`, `pdbmap`, `mmuflushtlb`, and early `rampage` is called from `mmu.c`.
- Uses `realmode` for E820 and `getconf` flags such as `*maxmem`, `*norealmode`, `*noe820scan`, `umbexclude`.
- PCI code reserves discovered BAR memory through `upareserve`.

Research notes:
- This is core to Plan 9 PC memory topology, not filesystem logic directly, but it is required substrate for storage drivers and DMA-capable devices.
- Only maps memory usable through the 32-bit KZERO window; addresses above 4GB are ignored/truncated in E820 processing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mmu.c

x86 MMU, segmentation, page-directory, device mapping, and temporary page mapping support for the Plan 9 PC kernel.

Key elements:
- Defines flat GDT descriptors for kernel/user code/data, 16-bit kernel code, and TSS.
- `mmuinit0` and `mmuinit` initialize GDT/IDT/TSS, install the recursive VPT mapping, mark kernel text read-only, and switch TSS/CR3.
- `memglobal` marks kernel mappings `PTEGLOBAL` when PGE is supported.
- `mmupdballoc`, `mmupdbfree`, `mmuptefree`, `mmuswitch`, `mmurelease`, `putmmu` implement per-process page directories and page-table page lifecycle.
- `mmuwalk` is the kernel page-table walker; before full MMU init it allocates tables with `rampage`.
- `vmap`, `vunmap`, `pdbmap`, `pdbunmap`, `vmapsync` manage global device mappings in the VMAP range.
- `kmap`, `kunmap` map physical `Page` objects into per-process temporary KMAP slots.
- `tmpmap`, `tmpunmap` provide a one-page temporary mapping for editing page directories.
- `kaddr`, `paddr`, `cankaddr` enforce/describe the KZERO direct map boundary.
- `countpagerefs`, `checkmmu` are debugging/accounting helpers.

Interactions:
- Depends on memory layout constants from `mem.h` and page allocation from port code.
- Supplies device memory mappings used by PCI, VGA, APIC, ACPI, and SCSI controller code.
- `memory.c` uses `pdbmap` and `mmuwalk` during bootstrap scanning.

Research notes:
- The VPT self-map is the central implementation detail: current page tables are edited via virtual addresses.
- VMAP mappings are mastered in `mach0->pdb` and lazily copied into process page directories on faults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mouse.c

PC mouse control and packet decoding for PS/2 and serial mice.

Key elements:
- Supports mouse types `Mouseother`, `Mouseserial`, and `MousePS2`.
- `ps2mouseputc` decodes PS/2 3-byte packets and IntelliMouse/AccuPoint 4-byte packets, including stream resynchronization after long gaps.
- Shift plus right-button is mapped as middle-button behavior.
- Extra IntelliMouse/AccuPoint bytes are mapped to buttons 4/5 using simple wheel/sign logic.
- `ps2mouse`, `resetmouse`, `setres`, `setintellimouse`, `setaccelerated`, `setlinear` configure hardware through i8042 aux commands or serial mouse handlers.
- `mousectl` parses architecture control commands: `ps2`, `ps2intellimouse`, `serial`, `res`, `reset`, `accelerated`, `linear`, `hwaccel`, `intellimouse`.

Interactions:
- Feeds decoded events to `mousetrack`.
- Uses `i8042auxenable`, `i8042auxcmd`, `i8250mouse`, `i8250setmouseputc`.
- Shares screen/draw cursor definitions via `screen.h`.

Research notes:
- Input support only; no filesystem behavior.
- The code adapts packet size dynamically for mixed laptop TrackPoint/external-mouse scenarios.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mp.c

Intel MultiProcessor table parsing, APIC setup, SMP application-processor startup, interrupt routing, and MP shutdown/reset path.

Key elements:
- Parses MP configuration table entries into condensed `Bus`, `Apic`, and `Aintr` structures.
- `mkprocessor`, `mkbus`, `mkioapic`, `mkiointr`, `mklintr` build CPU, bus, I/O APIC, and interrupt route state.
- `mpintrinit` translates MP interrupt flags into APIC redirection-table bits.
- `checkmtrr` records and compares MTRR registers across CPUs.
- `squidboy` is the AP C entry point after trampoline startup; initializes Mach, MMU, CPU, LAPIC, timers, and scheduler.
- `mpstartap` builds AP page tables/Mach state, writes warm-reset vector and AP bootstrap parameters, then sends startup IPIs.
- `mpinit` initializes PIC/APIC, maps LAPIC, parses MP table, supplements CPU discovery with ACPI MADT, enables local APIC interrupts, starts APs, and sets `conf.copymode`.
- `mpintrenable` and `mpintrenablex` map Plan 9 interrupt controls to I/O APIC vectors and destinations.
- `mpshutdown` handles multiprocessor reboot/reset, including PCI reset, i8042 reset, and port `0xcf9` fallback.

Interactions:
- Uses structures and constants from `mp.h`.
- Calls `mpacpifunc` from `mpacpi.c` to discover CPUs missed by MP tables.
- Uses `vmap` for APIC MMIO, `intrenable` for local APIC vectors, and PCI helpers for PCI interrupt pins.

Research notes:
- ACPI support here is deliberately limited: MP tables remain the source for interrupt routing.
- Interrupt vector allocation uses unique APIC vectors to reduce lost-interrupt risk.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mp.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mp.h

Definitions for Intel MultiProcessor Specification tables and APIC state used by `mp.c`, APIC code, and ACPI MP supplement code.

Key elements:
- Defines raw MP floating pointer `_MP_`, configuration header `PCMP`, processor/bus/I/O APIC/interrupt entries, and extended MP entry structs.
- Enumerates MP table entry types, CPU/I/O APIC enable flags, interrupt polarity/trigger flags, interrupt delivery types, and bus address-space metadata.
- Defines condensed runtime `Bus`, `Aintr`, and `Apic` structures.
- Defines APIC register numbers and redirection/vector bits such as `ApicFIXED`, `ApicNMI`, `ApicLOW`, `ApicLEVEL`, `ApicIMASK`.
- Declares I/O APIC, LAPIC, MP init, interrupt-enable, and shutdown entry points.
- Exposes global `_mp_`.

Interactions:
- Included by `mp.c` and `mpacpi.c`.
- Runtime `Apic` state is shared between MP-table and ACPI-discovered CPUs.

Research notes:
- This is hardware topology metadata, not filesystem code.
- `MaxAPICNO` is 254; APIC ID 255 is reserved for physical broadcast.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.c

Minimal ACPI support for multiprocessor CPU discovery through RSDT/XSDT and MADT/APIC tables.

Key elements:
- Searches for `RSD PTR ` using `sigsearch`.
- Validates ACPI checksums for RSDP, RSDT/XSDT, and child tables.
- `mpacpiscan` maps ACPI descriptor tables with `vmap`, iterates table pointers, and dispatches valid tables.
- `mpacpitbl` handles `APIC` tables only.
- `mpacpicpus` walks MADT structures and processes local processor APIC entries.
- `mpacpiproc` enables usable local APIC processor records, maps the bootstrap LAPIC, records `bootapic`, and enables LAPIC through MSR `0x1b` if needed.
- `mpnewproc` and `apicset` populate shared `mpapic`/`machno2apicno` data.

Interactions:
- Hooks into `mp.c` through exported `void (*mpacpifunc)(void) = mpacpi`.
- Uses `mpacpi.h` table structs and `mp.h` APIC structures.

Research notes:
- Explicitly avoids AML; it discovers processors but does not derive interrupt routing.
- It can add CPUs not present in the legacy MP table, but does not replace MP routing logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.h

ACPI table layout definitions used by minimal MP ACPI scanning and other PC firmware consumers.

Key elements:
- Defines common 36-byte SDT header embeddings for `Dsdt`, `Facp`, `Hpet`, `Madt`, and `Mcfg`.
- `Madt` includes LAPIC base address, flags, and variable MADT structures.
- `Mcfg` and `Mcfgd` describe PCI memory-mapped configuration regions.
- `Rsd` describes ACPI RSDP revision, RSDT address, XSDT address, and checksums.

Interactions:
- Included by `mpacpi.c`.
- Complements `sigsearch` from `memory.c` and `vmap` from `mmu.c`.

Research notes:
- Pure structure header; no behavior.
- Only MADT is used by the file group here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mpacpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mtrr.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/mtrr.c

Memory Type Range Register support for configuring x86 cache attributes, especially write-combining framebuffer mappings.

Key elements:
- Defines MTRR MSR numbers, memory types, capability/default-type bit fields, and 36-bit physical sanity limit.
- `physmask` derives physical address width via extended CPUID and caps to 36 bits.
- `mtrrdec` and `mtrrenc` convert variable MTRR MSR base/mask pairs to/from base/size/type.
- `mtrrget`, `mtrrput` read/write indexed variable MTRRs.
- `mtrrop` performs synchronized all-CPU MTRR update: disables PGE, disables caching, disables MTRRs, writes register, restores defaults/cache state.
- `mtrrclock` lets other CPUs execute pending operations from the clock interrupt.
- `mtrr` validates alignment, type support, slot availability, posts the operation, and updates all CPUs.
- `mtrrprint` formats default and variable MTRR cache ranges.

Interactions:
- `screen.c` calls `mtrr(..., "wc")` for linear VGA framebuffers and tolerates failure.
- MP startup validates MTRR consistency across CPUs in `mp.c`.

Research notes:
- Critical for performance of memory-mapped video and possibly device regions.
- Slot selection reuses invalid entries, matching base/size entries, or entries above 4GB.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/mtrr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/nomtrr.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/nomtrr.c

Stub implementation used when MTRR support is excluded.

Key elements:
- `mtrr` raises `error("mtrr support excluded")`.
- `mtrrprint` returns 0.

Interactions:
- Satisfies the same external interface as `mtrr.c`.
- Callers such as `screen.c` may wrap `mtrr` in `waserror` to harmlessly continue.

Research notes:
- Build-time alternative only; no hardware behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/nomtrr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/nv_dma.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/nv_dma.h

NVIDIA 2D DMA/register macro definitions imported from the XFree86 NV driver lineage.

Key elements:
- Contains NVIDIA copyright/license notice.
- Defines offsets and bit-field notation for surface format/pitch/offset, ROP, pattern, clipping, line drawing, blit, solid rectangle, mono/color expansion, and stretch blit objects.
- Includes max batch counts for line/rectangle/data command arrays.
- Encodes formats for 8/15/16/24-bit depths and YUYV/UYVY stretch blit formats.

Interactions:
- Header only; intended for NVIDIA VGA acceleration driver code in the same PC graphics subsystem.
- Uses unusual `FIELD 31:16` style macro names as documentation/constants for packed register fields.

Research notes:
- Graphics acceleration metadata only, not filesystem or storage logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/nv_dma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/pci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/pci.c

PC PCI enumeration, config-space access, BAR sizing/resource assignment, BIOS routing, device matching, reset, and power-management support.

Key elements:
- Supports PCI config mechanisms 1 and 2, plus optional BIOS32 PCI service access.
- `pcicfginit` detects config mode, scans buses, optionally uses BIOS32, applies `*pcimaxbno`, `*pcimaxdno`, `*nobios`, `*pcibios`, `*nopcirouting`, and optionally prints inventory.
- `pcilscan` enumerates devices/functions, reads IDs/class/header/BARs, detects multifunction devices, recursively scans PCI-PCI bridges, and sets `pcivga`.
- `pcibarsize` probes BAR sizes by writing all ones and restoring the original value.
- `pcibusmap` assigns I/O and memory resources when firmware did not.
- `$PIR` routing support scans BIOS memory, matches known southbridges, and fixes PCI interrupt line registers.
- Raw and BIOS config accessors back public `pcicfgr8/16/32` and `pcicfgw8/16/32`.
- `pcimatch`, `pcimatchtbdf`, `pciipin` provide device lookup.
- `pcireservemem` reserves memory BAR ranges from the UPA allocator.
- `pcihinv` prints PCI inventory.
- `pcireset` clears bus mastering for non-bridge devices.
- Command helpers set/clear I/O enable, bus master enable, and memory-write-invalidate.
- `pcigetpms`, `pcisetpms` walk PCI capabilities for standard power management state.

Interactions:
- Storage driver `sd53c8xx.c`, SMBus driver `piix4smbus.c`, VGA code, and MP interrupt routing all depend on PCI lookup/config helpers.
- Uses `upareserve` from `memory.c` to protect BAR physical ranges.

Research notes:
- Foundational for block/storage hardware discovery in this subset.
- File comment says it needs a rewrite; code mixes enumeration, resource allocation, IRQ routing, and power management.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/pcmciamodem.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/pcmciamodem.c

PCMCIA modem auto-link helper for known modem card names.

Key elements:
- Lists known modem product strings, including IBM, Xircom, Motorola, Sierra/Novatel/Psion style cards.
- `pcmciamodemlink` searches `serialN=type=com` ISA config lines for explicit port/IRQ settings.
- Defaults first unconfigured card to COM2, port `0x2f8`, IRQ 3.
- Calls `pcmspecial` to bind a matching PCMCIA card to the ISA serial configuration.
- Reserves I/O space with `ioalloc` and prints discovered slot/port/IRQ.

Interactions:
- Depends on PCMCIA support and serial/i8250 setup elsewhere.
- Uses Plan 9 ISA configuration parsing.

Research notes:
- Peripheral convenience support only.
- No filesystem relevance except enabling modem devices as system I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/pcmciamodem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/piix4smbus.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/piix4smbus.c

Intel PIIX4 SMBus controller support.

Key elements:
- Matches Intel vendor `0x8086`, PIIX4 power-management function `0x7113`.
- Defines SMBus PCI config registers and I/O register bits for host/slave status/control, command, address, and data.
- `proto` maps Plan 9 SMBus transaction types to PIIX4 protocol bits, direction, command presence, and byte count.
- `transact` serializes with `qlock`, waits for host idle, attempts `Kill` on stuck transactions, programs address/command/data, starts transaction, polls completion/error bits, and reads returned data.
- `piix4smbus` finds the PCI device, disables SMBus, uses BIOS base if available or allocates I/O ports, disables interrupts, aborts pending work, enables the controller, and returns an `SMBus` interface.

Interactions:
- Uses PCI config helpers from `pci.c`.
- Exposes an `SMBus` protocol object consumed by higher-level SMBus/I2C-like device code.

Research notes:
- Hardware management bus support; may affect sensors/EEPROM/power devices, not filesystem logic directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/piix4smbus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/plan9l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/plan9l.s

Small x86 assembly helpers for entering user mode and optimized syscall interrupt dispatch.

Key elements:
- Defines `touser`: constructs an interrupt-return frame with user data/code selectors, user stack, IF flag, and PC `UTZERO+32`, loads user segment registers, and executes `IRETL`.
- Defines `_syscallintr`: fast syscall vector handler that saves segment/general registers, switches DS/ES to kernel selectors, calls `syscall`, restores registers, removes trap metadata, and returns via `IRETL`.

Interactions:
- Must match syscall vector `0x40` from `io.h`.
- Complements trap/syscall handling in lower-level PC assembly and kernel trap code.

Research notes:
- Process/user transition substrate only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/plan9l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/psaux.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/psaux.c

Raw PS/2 auxiliary port arch-file interface for user-level mouse handling.

Key elements:
- Maintains global queue `psauxq`.
- `psauxputc` enqueues raw aux bytes from i8042 callback.
- `psauxread` reads bytes from the queue.
- `psauxwrite` sends command bytes to the aux device via `i8042auxcmds`.
- `psauxlink` opens a nonblocking queue, enables aux callback, and registers architecture file `psaux` with exclusive `0660` permissions.

Interactions:
- Shares draw/cursor includes with mouse/screen code but bypasses decoded kernel mouse handling.
- Uses i8042 aux support.

Research notes:
- Explicit BUG note: shift state is ignored.
- Provides raw input path for user-space daemons.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/psaux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ptclbsum386.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ptclbsum386.s

386 assembly implementation of `ptclbsum`, an optimized 16-bit folded checksum routine.

Key elements:
- Accepts address and length.
- Handles odd byte alignment and word alignment before entering bulk loops.
- Processes data in 32-byte, 8-byte, 2-byte, and trailing 1-byte phases.
- Uses add-with-carry accumulation into AX.
- Folds high 16 bits into low 16 bits until stable.
- Byte-swaps result depending on original address alignment.

Interactions:
- Likely used by networking/checksum code rather than storage.
- Architecture-specific performance helper.

Research notes:
- Pure assembly checksum routine; no filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ptclbsum386.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/realmode.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/realmode.c

Kernel bridge for executing BIOS calls by temporarily returning the processor to real mode.

Key elements:
- `realmode` locks global real-mode access, copies input `Ureg` to the low real-mode register block, copies low assembly code, identity-maps low memory, disables interrupts/PIC/APIC, calls `realmode0`, restores mappings/CR3/interrupts, and returns registers.
- Obeys `*norealmode`.
- `rtrapread`/`rtrapwrite` expose a `realmode` arch file for controlled VBE INT 10h calls.
- `rmemread`/`rmemwrite` expose `realmodemem`, allowing reads below 1MB and writes only to the real-mode buffer page or VGA framebuffer range.
- `realmodelink` registers both arch files.

Interactions:
- `memory.c` uses `realmode` for E820 BIOS calls.
- VGA/APM paths may also use real-mode BIOS services.

Research notes:
- Not VM86; it fully disables hardware interrupts during BIOS execution.
- Security/robustness is managed by narrow arch-file validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/realmode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/rebootcode.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/rebootcode.s

MMU-off kernel relocation and jump code used during reboot/loading a new kernel image.

Key elements:
- Entry `main` receives destination, source, and byte count.
- Disables paging by clearing CR0 PG and zeroing CR3.
- Copies source to destination with overlap handling: forward if safe, backward if overlapping.
- Jumps to the physical entry point after relocation.
- Notes that virtual `KZERO|AX` entry cannot be used until new kernel assembly re-enables MMU.

Interactions:
- Used by reboot/new-kernel handoff logic elsewhere.
- Depends on `mem.h` constants.

Research notes:
- Minimal assembly relocation stub; important for kernel lifecycle, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/screen.c

Generic PC screen/VGA framebuffer, palette, acceleration hook, linear framebuffer, blanking, and software cursor implementation.

Key elements:
- Global screen state: `gscreen`, `gscreendata`, `vgascreen[0]`, default arrow cursor, physical screen rectangle.
- `screensize` initializes or reallocates the memory image backing the screen, choosing soft screen memory or mapped framebuffer, then clears and flushes it.
- `screenaperture` allocates/maps a physical aperture with `upaalloc`/`vmap` when a driver lacks a preconfigured linear region.
- `attachscreen` exposes framebuffer metadata to draw clients.
- `flushmemscreen` copies soft-screen updates to paged VGA memory or delegates to driver flush.
- `getcolor`, `setpalette`, `setcolor` manage DAC palette state.
- `cursoron`, `cursoroff`, `setcursor` delegate to the active cursor implementation.
- `hwdraw` dispatches simple fill/scroll operations to VGA driver acceleration hooks while avoiding software cursor artifacts.
- `blankscreen` delegates blanking to driver or generic VGA blank.
- `vgalinearpciid`, `vgalinearpci`, `vgalinearaddr` locate/map linear PCI framebuffers and request write-combining MTRR.
- Software cursor path maintains backing store and cursor images; `swcursorclock` refreshes cursor on timer.

Interactions:
- Uses PCI helpers for video BAR discovery.
- Uses `vmap`, `upaalloc`, and `mtrr`.
- Interfaces with draw/memdraw and device-specific VGA drivers through `VGAdev`/`VGAcur`.

Research notes:
- Graphics subsystem support; not filesystem-specific.
- Framebuffer mapping behavior depends on low-level memory/MMU/PCI code in this same group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/screen.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/screen.h

Shared declarations and types for PC screen, VGA devices, cursors, mouse linkage, and draw integration.

Key elements:
- Defines `Cursorinfo`.
- Declares mouse tracking and serial mouse packet functions.
- Defines generic VGA port constants and palette constants.
- Defines `VGAdev` driver operations: enable/disable/page/linear/drawinit/fill/overlay/flush.
- Defines `VGAcur` cursor operations: enable/disable/load/move.
- Defines `VGAscr`, the main VGA screen state, including PCI pointer, framebuffer address/size, MMIO, colormap, current screen image, acceleration hooks, blanking, and driver-private ID.
- Declares screen, cursor, software cursor, draw, and VGA helper functions.
- Defines `ishwimage` helper macro.

Interactions:
- Included by `screen.c`, `mouse.c`, `psaux.c`, and VGA driver files.
- Bridges PC-specific VGA code with portable draw/devmouse code.

Research notes:
- Header-only graphics/input contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sd53c8xx.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/sd53c8xx.c

Plan 9 SCSI disk interface driver for NCR/Symbios/LSI Logic 53c8xx PCI SCSI controllers.

Key elements:
- Supports 53c810/815/825/860/875/885/895/896/1010/1011 variants through `variant[]`, with feature flags for wide, ultra, ultra2, prefetch, local RAM, big FIFO, differential, and clock multipliers.
- Defines memory-mapped NCR register layout `Ncr`, DMA move descriptors `Movedata`, request descriptor `Dsa`, controller state `Controller`, negotiation states, and transfer states.
- Includes generated SCRIPT microcode from `sd53c8xx.i`; `na_fixup` patches script-relative, register-relative, and external references.
- DSA management uses a controller-visible linked list with a sentinel `dsaend` to avoid controller walks through address zero.
- `synctabinit`, `chooserate`, `setsync`, `setasync`, `setwide`, `buildsdtrmsg`, `buildwdtrmsg`, and `msgsm` implement synchronous and wide SCSI negotiation.
- `softreset`, `busreset`, and `reset` initialize controller and SCSI bus state.
- `calcblockdma`, `read_mismatch_recover`, `write_mismatch_recover`, and `advancedata` handle DMA segmentation and phase-mismatch recovery.
- `sd53c8xxinterrupt` handles script interrupts, SCSI/DMA interrupts, phase mismatches, timeouts, parity/unexpected disconnects, script diagnostics, wakeups, and script restart/continue decisions.
- `sd53c8xxrio` is the main SCSI request path: allocates DSA, serializes per target, builds identify/negotiation/command/data/status descriptors, starts or signals SCRIPT execution, waits, handles timeout/reset, computes residual length, records target capabilities from INQUIRY, and issues REQUEST SENSE on check condition.
- `sd53c8xxpnp` discovers matching PCI devices, maps registers and optional local RAM, allocates/fixes SCRIPT memory, creates `SDev` instances, and links them.
- `sd53c8xxenable` enables bus mastering, initializes sync tables, captures BIOS settings, resets bus, and installs interrupt handler.
- Exports `SDifc sd53c8xxifc` with Plan 9 storage hooks: pnp, enable, verify, online, rio, bio.

Interactions:
- Heavy dependency on PCI enumeration/config and `vmap`.
- Implements a block-storage path through Plan 9 `sd` SCSI layer.
- Uses DMA address macros and controller-visible physical addressing assumptions for 386.
- Interrupt routing depends on PCI interrupt line/APIC/PIC setup.

Research notes:
- This is the most filesystem-relevant file in the group because it provides disk I/O substrate for SCSI storage.
- Known-problem comment notes read/write mismatch recovery may fail on 53c1010s.
- Driver is tightly coupled to generated NCR SCRIPT code and hardware phase behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/sd53c8xx.c -->