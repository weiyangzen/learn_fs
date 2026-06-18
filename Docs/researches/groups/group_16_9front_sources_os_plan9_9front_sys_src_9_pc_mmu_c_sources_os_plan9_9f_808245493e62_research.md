# Group Research: group_16_9front_sources_os_plan9_9front_sys_src_9_pc_mmu_c_sources_os_plan9_9f_808245493e62

Scope checked: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/mmu.c

Implements 32-bit x86 memory-management setup for the 9front PC kernel. The file defines flat GDT descriptors, per-CPU TSS setup, IDT/GDT loading, CR3 task switching, process page directory management, user PTE insertion, kernel/device mappings, temporary mappings, kmap mappings, and cache-attribute helpers.

Key mechanisms:
- Uses a self-mapped page directory at `VPT` so the kernel can edit current page tables through virtual addresses.
- `mmuinit()` marks kernel text read-only, installs VPT, allocates/configures the TSS, loads GDT/IDT, and switches to the kernel page directory.
- `mmuswitch()`, `flushmmu()`, `mmurelease()`, `putmmu()`, and `checkmmu()` manage per-process user mappings and page-table caches.
- `vmap()`/`vunmap()` maintain global device mappings in the `VMAP` range, with `vmapsync()` lazily copying master mappings from CPU0 page tables into current address spaces.
- `kmap()`/`kunmap()` provide temporary per-process page mappings in the `KMAP` region.
- `tmpmap()`/`tmpunmap()` provide single-page temporary mappings for editing page directories, with a fast path for physical pages already visible through `KZERO`.
- `patwc()` adjusts PAT bits for write-combining mappings, mainly framebuffer use.

Important dependencies include `Page`, `Proc`, `Mach`, `Tss`, `Segdesc`, paging macros from `mem.h`, and low-level routines such as `putcr3`, `invlpg`, `lgdt`, `lidt`, `ltr`, `newpage`, `freepages`, `rampage`, `procflushothers`, and MSR access.

Research notes:
- The file is central to address-space behavior but not filesystem-specific. Storage/display drivers in this group depend on `vmap()`, `vunmap()`, `KADDR()`, and cache-attribute helpers for MMIO and DMA-accessible memory.
- Safety invariants are enforced with panics: kmap reference balance, valid VMAP bounds, no overwriting existing device mappings, TMPADDR not already remapped, and valid kernel physical address conversions.
- The code assumes 32-bit physical addresses for `vmap()` by rejecting ranges where `(pa+size) >> 32` is nonzero.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mouse.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/mouse.c

Implements PC mouse control and packet decoding for serial mice, PS/2 mice, IntelliMouse-style extensions, and Synaptics touchpads/trackpoints.

Key behavior:
- `ps2mouseputc()` decodes 3-byte PS/2 packets and optional 4-byte IntelliMouse packets. It sign-extends deltas, maps button bits, handles shift-right as middle-click through the `b[]` map, detects packet desynchronization by elapsed time, and sends motion through `mousetrack()`.
- `synmouseputc()` decodes 6-byte Synaptics absolute packets, distinguishes trackpoint packets from touchpad packets, performs simple palm/edge filtering, scales absolute touchpad coordinates to screen geometry from `gscreen`, suppresses accidental taps based on motion thresholds, and emits relative pointer motion.
- Control commands are parsed by `mousectl()` using `Cmdtab`: `accelerated`, `linear`, `res`, `ps2`, `ps2intellimouse`, `serial`, `reset`, `hwaccel`, `touchpad`, and `synaptic`.
- PS/2 setup and mode changes use `i8042auxenable()` and `i8042auxcmd()`.
- Serial setup uses `uartmouse()`/`uartsetmouseputc()` and the existing serial decoders declared in `screen.h`.

Important state includes `mousetype`, `intellimouse`, `packetsize`, `resolution`, acceleration flags, `synaptic`, `disabletouch`, and the configured serial `mouseport`.

Research notes:
- Depends on display state via `gscreen` for Synaptics coordinate scaling.
- Uses a `QLock` around control changes so command writes do not interleave controller reconfiguration.
- Touchpad logic is heuristic and device-specific, with dynamic edge calibration from observed min/max coordinates.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/mp.c

Implements multiprocessor/APIC initialization support and interrupt assignment for the 32-bit PC kernel. Tables are populated by MP-table or ACPI discovery elsewhere; this file consumes the condensed bus/APIC structures from `mp.h`.

Key behavior:
- Global topology state: `mpbus`, `mpbuslast`, ISA/EISA bus numbers, `mpioapic[]`, and `mpapic[]`.
- `mpintrinit()` converts MP interrupt table flags into APIC redirection-vector bits, resolving default polarity/trigger mode from bus type.
- `syncclock()` synchronizes TSC state when the architecture fast clock uses `tscticks()`.
- `mpinit()` initializes legacy PIC fallback, LAPIC, local LAPIC interrupts, starts application processors through `mpstartap()`, and sets `conf.copymode` for SMP/old CPUs.
- `allocvector()` allocates APIC vectors spaced by priority class to reduce lost-interrupt risk.
- `mpintrassign()` first tries MSI, then table-driven I/O APIC routing, then local APIC vectors, then EISA/ISA fallbacks.
- MSI support includes HyperTransport MSI mapping enablement on AMD/NVIDIA platforms.
- `mpshutdown()` parks APs, broadcasts INIT, and resets PCI.

Research notes:
- Storage drivers in this group depend indirectly on this file through `intrenable()` routing for PCI interrupts and MSI/I/O APIC configuration.
- The interrupt assignment code handles PCI bridge swizzling when firmware tables omit downstream buses.
- The round-robin CPU selector uses online APICs and physical destination mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mp.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/mp.h

Defines data structures, constants, and external interfaces for Intel MultiProcessor Specification and APIC support.

Content summary:
- Raw MP floating pointer and configuration table structures: `_MP_`, `PCMP`, `PCMPprocessor`, `PCMPbus`, `PCMPioapic`, `PCMPintr`, and extended entries for address-space mapping, bus hierarchy, and compatibility bus address-space modifiers.
- Size macros for each packed table format.
- Enumerations for MP table entry types, processor/I/O APIC flags, interrupt polarity, trigger mode, interrupt types, address-space types, and bus hierarchy modifiers.
- Condensed runtime topology structures:
  - `Bus`: bus type, bus number, default polarity/trigger, interrupt list.
  - `Aintr`: links an MP interrupt entry to an APIC and bus.
  - `Apic`: APIC identity, mapped registers, flags, I/O APIC redirection metadata, local interrupt slots, `machno`, and online state.
- APIC register and redirection-entry bit constants.
- External declarations for I/O APIC, LAPIC, MP initialization, interrupt assignment, and global topology arrays.

Research notes:
- This is a contract header shared by MP table parsers, ACPI code, LAPIC/I/O APIC code, and `mp.c`.
- It contains no executable logic, but it controls how interrupt routing metadata is represented for device drivers.
- `MaxAPICNO` is 254 because 255 is reserved for physical broadcast.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mtrr.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/mtrr.c

Implements x86 MTRR cache-type management and reporting. It reads fixed and variable MTRRs, constructs effective cache-type ranges, updates registers safely, and synchronizes changes across CPUs.

Key behavior:
- Defines MSR constants for variable MTRRs, default MTRR type, capabilities, and AMD K8 `TOM2` handling.
- `State` captures MTRR mask, capability/default registers, fixed registers, variable registers, and AMD top-of-memory state.
- `Range` describes effective physical ranges and cache types: uncacheable, write-combining, write-through, write-protected, and write-back.
- `gettype()` and `getnext()` compute effective memory type transitions from fixed, variable, default, and TOM2 rules.
- `getstate()` reads hardware MTRR state and detects usable support.
- `putstate()` updates MTRRs using the required sequence: raise IPL, disable cache, flush, disable PGE, disable MTRRs, write registers, flush again, re-enable MTRRs/cache/PGE.
- `mtrr()` validates and adds a requested cache range, tries to synthesize satisfiable fixed/variable register programming, and triggers CPU-wide synchronization.
- `mtrrattr()` and `mtrrprint()` expose current cache attributes.
- `mtrrclock()` runs from clock interrupts as a CPU barrier and applies pending MTRR state to all processors.
- `mtrrsync()` initializes CPU0 state or applies CPU0 state to other CPUs during identification.

Research notes:
- `screen.c` calls `mtrr(..., "wc")` for framebuffer write-combining after `vmap()`.
- The range fitting logic is conservative: it rejects unsatisfiable or unaligned ranges and checks the synthesized state before committing.
- CPU synchronization uses static `Ref` barriers and assumes all active CPUs pass through `mtrrclock()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mtrr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/nv_dma.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/nv_dma.h

Header of NVIDIA/XFree86-originated DMA register definitions for NV graphics acceleration. The file is primarily a collection of register offsets, field-position comments/macros, format values, and maximum transfer counts.

Content summary:
- Begins with NVIDIA copyright/license notice and XFree86 CVS provenance.
- Defines offsets and format values for objects such as:
  - `SURFACE_*`
  - `ROP_SET`
  - `PATTERN_*`
  - `CLIP_*`
  - `LINE_*`
  - `BLIT_*`
  - `RECT_*`
  - `RECT_EXPAND_*`
  - `STRETCH_BLIT_*`
- Many field names use a `31:16`/`15:0` notation as descriptive register bit ranges, not C expressions suitable for standalone use.
- Intended consumers are NVIDIA display acceleration code that writes command/data words to the GPU command interface.

Research notes:
- This is vendored hardware definition material rather than native Plan 9 logic.
- It has no functions or state; its significance is as a hardware contract for graphics code.
- The license notice requires retaining NVIDIA attribution in user documentation and internal comments when used.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/nv_dma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pcibios.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/pcibios.c

Implements PCI BIOS32-based PCI configuration access as a fallback or requested mode.

Key behavior:
- `pcibiosinit()` opens the BIOS32 `$PCI` service, issues PCI BIOS installation check function `0xB101`, verifies the returned signature, determines max device number and max bus number, and installs BIOS-backed config accessors.
- `pcicfgrw8bios()`, `pcicfgrw16bios()`, and `pcicfgrw32bios()` wrap PCI BIOS calls for byte/word/dword read and write.
- Read operations use BIOS function numbers `0xB108`, `0xB109`, and `0xB10A`.
- Write operations use `0xB10B`, `0xB10C`, and `0xB10D`.
- BIOS call registers encode bus/device/function in `ebx`, config register in `edi`, and data in `ecx`.

Research notes:
- `pcipc.c` calls `pcibiosinit()` when raw PCI config mechanisms are unavailable or `*pcibios` is set.
- On success, global function pointers `pcicfgrw8/16/32` are replaced so the rest of PCI code is agnostic to config-access method.
- The code ignores commented-out BIOS status checks on `ci.eax & 0xFF`, relying mainly on `bios32ci()` success.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pcibios.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pcipc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/pcipc.c

Implements PC PCI configuration-space access setup, PCI routing-table handling, southbridge IRQ link programming, PCI resource reservation/allocation, and PCI bus discovery.

Key behavior:
- Raw config accessors support PCI configuration mechanism #1 via ports `0xCF8/0xCFC` and mechanism #2 via `0xCF8/0xCFA`.
- `pcicfginit()` selects config mode unless BIOS mode is forced, scans PCI buses up to `pcimaxbno`, resets CardBus bridges encountered on bus 0, optionally allocates all bus windows when `*nobios` is set, reserves existing BAR resources, and applies PCI IRQ routing.
- `$PIR` parsing in `pcirouting()` validates checksum, finds the interrupt router southbridge, chooses matching chipset handlers, and updates device `PciINTL` values.
- Southbridge handler tables cover Intel PIIX/ICH/PCH families, VIA, OPTi, ALi, SiS, Cyrix, AMD, NVIDIA, ATI/AMD, ServerWorks, and others.
- `pcireserve()` reserves already assigned I/O/memory BARs and allocates address space for unassigned BARs using parent bridge windows when possible.
- `pcicfginit()` honors `*nobios`, `*pcibios`, `*nopcirouting`, `*pcimaxbno`, `*pcimaxdno`, and `*pcihinv`.

Research notes:
- This file is foundational for all PCI storage/display drivers in this group: AHCI, MMC, SCSI, VGA, and BIOS fallback all depend on correct PCI enumeration and BAR assignment.
- Some bridge entries intentionally have `nil` get/set handlers, meaning the router is recognized but not reprogrammed by this code.
- Resource reservation distinguishes I/O BARs from memory BARs and uses `ioreserve`, `ioreservewin`, `upaalloc`, and `upaallocwin`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pcipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pcmciamodem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/pcmciamodem.c

Small PCMCIA modem autodetection/link helper.

Key behavior:
- Contains a static list of modem CIS/product strings, including IBM, Xircom, Motorola, Sierra/Novatel/Psion-style cellular modem names.
- `pcmciamodemlink()` walks known modem names and available `serialN=type=com` ISA configuration entries.
- If no explicit serial config is found and COM2 has not already been assigned, it defaults the first found modem to IRQ 3 and port `0x2F8`.
- Calls `pcmspecial()` to bind a matching PCMCIA card to the chosen `ISAConf`.
- Reserves the serial I/O port with `ioalloc()` and prints the detected slot, port, and IRQ.

Research notes:
- This is legacy laptop/modem support, not filesystem or storage code.
- The loop deliberately avoids assigning default COM2 to more than one modem.
- It assumes a laptop with PCMCIA usually has only one COM port unless plan9.ini supplies explicit serial configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pcmciamodem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pmmc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/pmmc.c

Implements a PCI SD/MMC host-controller driver through the Plan 9 `SDio` interface. It targets SDHCI-like controllers and includes Ricoh-specific support.

Key behavior:
- Defines SD host-controller register offsets, normal interrupt bits, error interrupt bits, present-state bits, transfer-mode bits, and command-response encodings.
- `pmmcinit()` scans PCI devices for class `08/05` SD host controllers or Ricoh 5U822/5U823 devices, maps MMIO BAR0 with `vmap()`, enables the PCI device, and applies Ricoh SD2.0/base-clock quirks.
- `mmcinterrupt()` acknowledges normal/error interrupts, records card insertion/removal, accumulates wait status, and wakes sleepers.
- `resetctlr()` disables interrupts, resets the controller, sets timeout, enables interrupt masks, powers the card, and starts a 400 kHz clock.
- `pmmccmd()` builds SD command register fields, handles response types, checks card presence and command/data inhibit bits, writes command/argument/mode registers, waits for completion, and extracts 48-bit/136-bit responses.
- `pmmciosetup()` records block size/count; `pmmcio()` transfers data using PIO through `Rdat0`.
- `pmmcbus()` switches 1-bit/4-bit width and adjusts clock rate.
- `pmmclink()` registers the driver with `addmmcio()`.

Research notes:
- The driver uses PIO, not SDMA/ADMA, despite exposing DMA-related registers.
- Timeout/error paths reset command/data lines through `softreset(c, 0)`.
- Filesystem relevance is via block-device access for SD/MMC media.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/pmmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/rebootcode.s

Small x86 assembly routine used during reboot/kernel replacement.

Behavior:
- Entry `main(SB)` receives destination, source, and byte count.
- Disables paging by clearing CR0 PG bit and clears CR3.
- Sets stack pointer below the entry point.
- If destination/entry is zero, parks the CPU in an infinite `HLT` loop.
- Copies the new kernel image from source to destination, choosing forward or backward copy depending on overlap.
- Jumps directly to the physical entry point after the copy.
- Comment notes that the true virtual entry is `KZERO|AX`, but this code jumps before the new kernel enables its MMU.

Research notes:
- This code is deliberately physical-address oriented because paging is disabled before the copy.
- Its overlap logic is memmove-like: forward copy when safe, backward copy when source end overlaps destination.
- It is platform boot/reboot infrastructure, not a storage/filesystem component.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/screen.c

Implements PC screen/framebuffer setup and common VGA drawing integration.

Key behavior:
- Maintains global `gscreen` and single `VGAscr vgascreen[1]`.
- Supports screen rotation through `tiltpt()`, `tiltrect()`, `tiltsize()`, `actualscreensize()`, and `setactualsize()`.
- `setscreensize()`/`setscreensize0()` create either a software `Memimage` or a direct framebuffer-backed `Memimage`, initialize pitch/depth metadata, reload draw state, restore cursor, and export boot-screen configuration.
- `screenaperture()` allocates/matches physical framebuffer aperture space and maps it with `vmap()`.
- `attachscreen()` exposes screen memory to draw clients; `flushmemscreen()` copies software-screen damage to linear or paged framebuffers and handles tilted output.
- Palette helpers `getcolor()`, `setpalette()`, and `setcolor()` manage VGA DAC colors for indexed modes.
- Cursor helpers rotate hardware cursor bitmaps when needed and delegate to the active `VGAcur`.
- `hwdraw()` opportunistically uses device fill/scroll acceleration for suitable draw operations.
- `vgalinearaddr()`/`vgalinearpci()` map framebuffers, apply PAT write-combining via `patwc()`, and request MTRR write-combining with `mtrr()`.
- `bootscreeninit()` attaches to a bootloader-provided framebuffer from `*bootscreen`; `bootscreenconf()` records current framebuffer configuration for reboot.

Research notes:
- This file ties together PCI BAR discovery, MMIO mapping, MTRR/PAT cache attributes, draw device state, mouse cursor state, and boot environment propagation.
- It limits framebuffer mapping to 64 MB even if the PCI region is larger.
- Rotation forces `softscreen`, then flushes transformed pixels to the physical framebuffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/screen.h

Shared declarations for mouse, VGA, screen, draw, cursor, and low-level VGA support.

Content summary:
- Declares mouse interfaces from `devmouse.c`: cursor state, tracking, acceleration, serial mouse decoders, and last-event timing.
- Defines generic VGA register port constants and palette constants.
- Provides `VGAMEM()`, `vgai()`, and `vgao()` helpers/macros for VGA memory and port I/O.
- Defines display-driver structures:
  - `VGAdev`: device operations for enable/disable/page/linear/drawinit/fill/overlay/flush.
  - `VGAcur`: cursor operations for enable/disable/load/move.
  - `VGAscr`: active screen state, including device, PCI device, cursor, framebuffer physical/virtual address, aperture size, bpp, pitch, geometry, MMIO, palette, memimage backing, acceleration hooks, blanking hook, softscreen, and tilt.
- Declares common screen APIs from `screen.c`, draw integration hooks, VGA helpers, and software cursor functions.
- Defines `ishwimage()` to test whether a `Memimage` uses the active hardware screen data.

Research notes:
- This header is the main contract between generic screen code and hardware-specific VGA/display drivers.
- It also bridges mouse code to screen code through cursor and tracking declarations.
- The framebuffer mapping fields in `VGAscr` are populated by `screen.c` and consumed by device drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sd53c8xx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sd53c8xx.c

Implements a Plan 9 SCSI disk interface driver for NCR/Symbios/LSI Logic 53c8xx PCI SCSI controllers.

Key behavior:
- Defines controller register layout (`Ncr`), DMA/script data structures (`Dsa`, `Movedata`), negotiation state, chip feature flags, burst encodings, and supported chip variants.
- Includes generated SCRIPTS microcode from `sd53c8xx.i` and patches it through `na_fixup()` using physical script/register addresses and DSA offsets.
- `sd53c8xxpnp()` scans PCI vendor `0x1000`, matches supported chip variants, maps register BARs with `vmap()`, uses local RAM for scripts when available, otherwise allocates host memory, initializes the DSA sentinel list, and creates `SDev` instances.
- `sd53c8xxenable()` enables bus mastering, initializes sync timing tables, records BIOS setup, resets the bus, and registers interrupts.
- `synctabinit()`, `chooserate()`, `setsync()`, `setasync()`, and `setwide()` implement wide/synchronous transfer negotiation.
- `sd53c8xxinterrupt()` handles script interrupts, DMA interrupts, SCSI interrupts, reselection, phase mismatch, parity, timeout, unexpected disconnect, illegal instruction, bus fault, and many script diagnostic events.
- Read/write phase mismatch recovery accounts for DMA FIFO and SCSI FIFO residues, advances transfer descriptors, and restarts scripts at recovery labels.
- `sd53c8xxrio()` is the main SCSI request path: allocates a DSA, serializes per target, builds identify/WDTR/SDTR messages, sets command/data/status move descriptors, starts or signals the script engine, waits up to 600 seconds, handles check condition by issuing request sense, computes residual length, and frees the DSA.

Research notes:
- Filesystem relevance is direct: this is a block-storage path exposed through `SDifc`, using `scsibio` for block I/O.
- The code is tightly coupled to 32-bit DMA address assumptions via `PCIWADDR`, `PCIWINDOW`, and `KADDR`.
- There is extensive recovery logic for hardware/script edge cases, especially phase mismatches and residual accounting.
- Known-problem comments mention possible read/write mismatch recovery failure on 53c1010.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sd53c8xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdiahci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/sdiahci.c

Implements an AHCI SATA/ATAPI storage driver for Intel/AMD and related PCI AHCI controllers.

Key behavior:
- Defines controller and drive limits, controller families, drive states, SATA modes, debug flags, and runtime structures for `Ctlr` and `Drive`.
- `iapnp()` scans PCI devices, identifies AHCI-capable controllers by vendor/device/class, maps AHCI BARs with `vmap()`, performs BIOS handoff, applies Intel/AMD setup quirks, initializes HBA state, maps implemented ports to `Drive` objects, configures ports, initializes enclosure LEDs, and registers `SDev`s.
- `iaenable()` registers controller interrupts, enables HBA interrupts, and starts background kernel processes for drive polling and LED updates.
- Port setup uses `ahciconfigdrive()`, `setupfis()`, command-list/table allocation, FIS receive area setup, COMRESET, power/spin-up handling, interrupt enables, and command engine start.
- Drive state machine uses `updatedrive()`, `configdrive()`, `resetdisk()`, `newdrive()`, `checkdrive()`, and `satakproc()` to handle hotplug, PHY changes, errors, resets, slow initialization, retries, and hung commands.
- ATA identify and setup flow uses AHCI command FIS helpers from `fis.h`/`ahci.h`, sets transfer mode, disables APM when supported, and extracts model/firmware/serial/WWN/sector size.
- I/O path:
  - `ahcibio()` handles block reads/writes in chunks, with larger chunks for LBA48 and controller-specific limits.
  - `iario()` handles SCSI emulation, flush cache, and regular disk requests.
  - `iariopkt()` handles ATAPI packet requests.
  - `iaataio()` handles raw ATA/FIS protocol requests with sanitization.
- LED/enclosure support implements IBPI-style blinking through AHCI enclosure management or ESB-specific registers.
- Control/status paths expose per-drive and top-level status, modes, flags, registers, geometry, alignment, missed IRQs, debug toggles, forced state, forced mode, and transfer mode.

Research notes:
- Filesystem relevance is direct: this is a primary SATA block-device backend for Plan 9’s `sd` layer.
- It supports SATA disks and ATAPI devices, hotplug, cache flush, raw ATA, and SCSI-compatible block I/O.
- Error handling is state-machine driven: failed commands may return retry/check/eio, trigger software reset, disable DMA for hung devices, or move the drive into reset/portreset/offline states.
- It depends heavily on PCI enumeration, MMIO mapping, interrupt routing, DMA-accessible command structures, AHCI register definitions, and Plan 9 `SDifc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/sdiahci.c -->