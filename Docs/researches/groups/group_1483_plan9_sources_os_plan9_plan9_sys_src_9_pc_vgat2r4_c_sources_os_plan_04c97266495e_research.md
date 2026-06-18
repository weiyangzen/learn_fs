# Group Research: group_1483_plan9_sources_os_plan9_plan9_sys_src_9_pc_vgat2r4_c_sources_os_plan_04c97266495e

Scope confirmed against `Docs/research_subset_a.md`: all files are under the included `sources/os/plan9/plan9` tree. Each listed file was read completely and is reported below in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgat2r4.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgat2r4.c

## Purpose
Driver support for the Number Nine Ticket to Ride IV VGA device, covering PCI/MMIO discovery, hardware cursor programming, accelerated rectangle fill/scroll, and display blanking.

## Main Interfaces
- Exports `VGAdev vgat2r4dev` named `t2r4`.
- Exports `VGAcur vgat2r4cur` named `t2r4hwgc`.
- Installs `scr->fill`, `scr->scroll`, and `scr->blank` during `t2r4drawinit`.
- Uses `scr->mmio`, `scr->pci`, `scr->gscreen`, `scr->paddr`, and `scr->apsize`.

## Implementation Notes
- `t2r4enable` locates PCI vendor `0x105D`, device `0x5348`, maps BAR 4, registers VGA segments, and calls `vgalinearpci`.
- Cursor register access is indirect through MMIO `IndexLo`, `IndexHi`, and `Data`.
- Cursor image conversion maps Plan 9 `Cursor` `clr`/`set` bitplanes into the device cursor RAM truth table.
- Hardware acceleration writes command-engine registers under `RBaseD`, with bounded polling in `waitforfifo`, `waitforcmd`, and `waitformem`.
- `t2r4drawinit` supports `RGB15`, `RGB16`, and `XRGB32`; unsupported channels disable acceleration callbacks.

## Dependencies And Risks
- Depends on Plan 9 VGA core structures from `screen.h`, PCI helpers, `vmap`, and low-level MMIO ordering.
- Hardware polling uses fixed spin limits and only logs timeout symptoms.
- Scroll has explicit small-horizontal-scroll workarounds for SGI flat panels.
- Cursor Y coordinates and hotspots are scaled by the device zoom register.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgat2r4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3020.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3020.c

## Purpose
Hardware cursor support for the TI TVP3020 Viewpoint Video Interface Palette, assumed to be attached to an S3 86C928.

## Main Interfaces
- Exports `VGAcur vgatvp3020cur` named `tvp3020hwgc`.
- Provides enable, disable, load, and move callbacks for the VGA cursor layer.

## Implementation Notes
- Indirect DAC access is selected through S3 CRTC register `0x55`, using the lower DAC register bits to choose VGA palette ports.
- `tvp3020enable` initializes cursor control, overscan/cursor colors, and S3 external cursor control bits.
- `tvp3020load` writes a 64x64 cursor RAM image, placing the 16x16 Plan 9 cursor in the top-left and zeroing the remainder.
- Cursor image bits are expanded into 2-bit-per-pixel X-Windows cursor mode.
- `tvp3020move` writes low/high X and Y cursor position registers.

## Dependencies And Risks
- Tight coupling to S3 VGA indexed registers `Crtx 0x45` and `0x55`.
- Assumes 16x16 Plan 9 cursor source and 64x64 hardware cursor RAM.
- Does not probe or validate the DAC; selection is by configured cursor device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3020.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3026.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3026.c

## Purpose
Hardware cursor support for the TI TVP3026 Viewpoint Video Interface Palette, assumed to be attached to an S3 Vision968.

## Main Interfaces
- Exports `VGAcur vgatvp3026cur` named `tvp3026hwgc`.
- Exports `tvp3026xo`, an indirect register writer likely shared with other TVP3026-related code.

## Implementation Notes
- Uses CRTC register `0x55` to select DAC indexed-register windows.
- `tvp3026enable` enables direct cursor control, writes overscan and cursor colors, and turns on 3-color cursor mode.
- `tvp3026load` writes separate 64x64 cursor planes: all `clr` bytes first, then all `set` bytes.
- Hardware origin is bottom-right-oriented, so load stores `scr->offset` as `64 + curs->offset`.
- `tvp3026move` adds `scr->offset` before writing cursor position registers.

## Dependencies And Risks
- Depends on S3 DAC routing behavior and the TVP3026 direct cursor registers.
- Cursor memory layout differs from TVP3020 and is not interchangeable.
- No runtime validation of DAC presence or cursor RAM behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3026.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgavesa.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgavesa.c

## Purpose
Generic VGA driver that relies on the VESA BIOS Extension to discover the current linear framebuffer and optionally uses a software backing screen flushed to the real framebuffer.

## Main Interfaces
- Exports `VGAdev vgavesadev` named `vesa`.
- Supplies `linear` callback `vesalinear`.
- Supplies `flush` callback `vesaflush`.

## Implementation Notes
- VBE calls use `/dev/realmodemem` and `/dev/realmode` to place a request buffer at `RMBUF` and invoke BIOS interrupt `0x10`.
- `vbecheck` requires VESA signature and VBE version 2 or newer.
- `vesalinear` asks for current mode, checks graphics and linear-framebuffer attributes, reads physical framebuffer address from mode info, and estimates usable framebuffer size.
- PCI BAR matching is used to grow the mapping to the real BAR size when possible; fallback heuristics round to at least 4 MiB and cap at 16 MiB.
- With `Usesoftscreen`, the hard framebuffer is hidden from the generic screen code and `vesaflush` copies dirty rectangles from software screen data.

## Dependencies And Risks
- Requires functioning real-mode BIOS call devices.
- The code comments note Bochs loses top bits of the mode number, so the linear-mode bit in current mode is not trusted.
- Software flush assumes word-aligned memmove spans based on `Memimage` layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgavesa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgavmware.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgavmware.c

## Purpose
VMware SVGA VGA driver providing linear framebuffer mapping, FIFO update commands, rectangle fill/copy acceleration, and hardware cursor support.

## Main Interfaces
- Exports `VGAdev vgavmwaredev` named `vmware`.
- Exports `VGAcur vgavmwarecur` named `vmwarehwgc`.
- Installs `scr->scroll`, `scr->fill`, and `flush` callbacks.

## Implementation Notes
- Probes PCI vendor `0x15AD` and supports device IDs `0x0710` and `0x0405`.
- Register access is via VMware index/data I/O ports, either fixed `0x4560` or from PCI BAR 0.
- `vmwarelinear` maps `Rfbstart` with twice `Rfbsize`, matching an empirical comment about larger modes.
- `vmwaredrawinit` maps FIFO MMIO from `Rmemstart/Rmemsize`, initializes FIFO control words, writes `Rconfigdone`, and adjusts screen data by `Rfboffset`.
- FIFO commands implement update, rectcopy, rectfill, and cursor definition/display/move.
- Cursor conversion builds 16-line AND/XOR masks from Plan 9 cursor bitplanes.

## Dependencies And Risks
- Global singleton `vm` means only one VMware VGA instance is represented.
- FIFO writer busy-waits via sync when space is exhausted.
- `vmwareblank` is a no-op, so display blanking is not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgavmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgax.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgax.c

## Purpose
Shared locked helpers for reading and writing VGA indexed registers.

## Main Interfaces
- Exports `vgaxi(long port, uchar index)` for indexed register reads.
- Exports `vgaxo(long port, uchar index, uchar data)` for indexed register writes.

## Implementation Notes
- Serializes access through static `Lock vgaxlock`.
- Supports sequencer, CRT controller, graphics controller, and attribute controller indexed ports.
- Attribute controller access resets flip-flop by reading `Status1`, handles palette indices below `0x10`, and restores display-enable bit `0x20`.
- For standard indexed registers it writes index to `port` and reads/writes `port+1`.

## Dependencies And Risks
- Returns `-1` for unsupported ports despite return type `int`; callers expecting unsigned byte data must handle this.
- Attribute controller sequencing is hardware-sensitive and intentionally conservative.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/wavelan.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/wavelan.c

## Purpose
Lucent/Orinoco WaveLAN IEEE 802.11 Hermes driver core for Plan 9 Ethernet devices, covering command/LTV access, attach/reset, TX/RX, WEP settings, scanning, stats, interrupts, timer recovery, power hooks, and control commands.

## Main Interfaces
- Exports CSR helpers `csr_outs`, `csr_ins`, `w_intdis`, `w_cmd`, `ltv_outs`, `ltv_ins`, `w_inltv`.
- Exports Ethernet callbacks: `w_attach`, `w_detach`, `w_interrupt`, `w_transmit`, `w_ifstat`, `w_ctl`, `w_promiscuous`, `w_multicast`, `w_power`.
- Exports `wavelanreset(Ether*, Ctlr*)`.
- Exports `wavenames[]` with recognized PCMCIA/card names.

## Implementation Notes
- CSR access supports either port I/O or PCI memory-mapped I/O; MMIO registers are indexed as 16-bit registers spaced like 32-bit slots.
- Hermes commands are synchronous: wait for `WCmdBusy` clear, issue command/parameter, wait for `WCmdEv`, validate status, and acknowledge.
- LTV helpers implement card configuration reads/writes for ESSID, channel, port type, MAC, power management, WEP keys, stats, and scan results.
- `w_enable` resets/initializes card operation, programs all controller settings, allocates transmit buffers, and enables interrupts.
- RX path reads `WFrame`, distinguishes RFC1042/tunnel/WMP from native 802.3, builds an Ethernet packet, queues it via `etheriq`, and smooths signal/noise.
- TX path dequeues `ether->oq`, constructs 802.11/SNAP framing when needed, writes frame and payload to allocated card memory, and starts reclaiming transmit.
- Interrupt handling processes RX, TX, allocation, info, TX error, and info-drop events, then tries to start another transmit.
- `w_timer` polls missed events, handles transmit watchdog timeouts by re-enabling the card, and periodically requests stats/scan info.
- `w_option` parses control commands for ESSID/station/channel/mode/IBSS/WEP keys/txkey/power management and `w_ctl` applies them by re-enabling the card.

## Dependencies And Risks
- File comments explicitly flag weak documentation, endian/alignment concerns, long interrupt-disabled sections, receive-watchdog concerns, and locking TODOs.
- WEP key parsing supports ASCII 5/13-byte and hex 10/26-digit forms; stat output hides key contents unless `SEEKEYS` is enabled.
- `w_detach` posts a note to kill the timer process and clears `ether->ctlr`; timer shutdown depends on observing that change.
- Multicast filtering is not implemented; enabling multicast falls back to promiscuous mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/wavelan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/wavelan.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/wavelan.h

## Purpose
Shared constants, Hermes register definitions, frame/LTV/stat structures, controller state, and function prototypes for the WaveLAN driver family.

## Main Interfaces
- Defines LTV type constants such as `WTyp_Stats`, `WTyp_Scan`, `WTyp_Mac`, `WTyp_NetName`, `WTyp_Crypt`, `WTyp_Keys`.
- Defines Hermes CSR registers and event bits: `WR_Cmd`, `WR_EvSts`, `WR_IntEna`, `WEvs`, etc.
- Defines frame constants for 802.11/802.3 offsets and SNAP encapsulation.
- Defines `WStats`, `WScan`, `WFrame`, `WKey`, `Wltv`, `Stats`, and `Ctlr`.
- Declares public driver routines implemented by `wavelan.c`.

## Implementation Notes
- `Ctlr` embeds a `Lock`, configuration state, transmit buffers, WEP key data, PCI/MMIO fields, and both software and card-provided stats.
- Default radio settings include managed mode, AP density, RTS threshold disabled at `2347`, and automatic transmit rate.
- WEP supports four keys with 5-13 byte valid key lengths and a 14-byte stored key slot.
- `Wltv` is a compact union matching the card’s length-type-value control records.

## Dependencies And Risks
- Layouts are hardware ABI structures; padding and endianness are important.
- `BADPTR`-style validation is not here; callers assume the shared layout matches card command payloads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/wavelan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/x86watchdog.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/x86watchdog.c

## Purpose
Implements a software-configured x86 watchdog using CPU performance counters and local APIC NMIs.

## Main Interfaces
- Exports `Watchdog x86watchdog`.
- Exports `x86wdstat(char*, char*)`.
- Exports `x86watchdoglink()` to register with `addwatchdog`.

## Implementation Notes
- Supports Intel P6, Intel P4, AMD K6/Athlon-family, and AMD64-family performance-counter models.
- `x86wdenable` wires the caller to CPU 0, checks CPUID vendor/family and required APIC/MSR/TSC features, resets relevant counters, enables local APIC NMI, and arms a roughly one-second counter overflow.
- `interval` caps the reload value at 31 bits for high-frequency CPUs.
- `x86wddisable` returns to CPU 0, disables local APIC NMI, and clears model-specific event selectors.
- `x86wdrestart` rewrites the counter reload and increments restart ticks.
- `x86wdstat` reports enabled/disabled plus restart count.

## Dependencies And Risks
- CPU 0 affinity is required because counters are local; `runoncpu` panics if it cannot switch.
- P4 handling has an early return if required MSR bit is absent, after `inuse` is already set.
- Low-level MSR programming is model-specific and assumes the APIC NMI path handles overflow correctly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/x86watchdog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/bindpc -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/bindpc

## Purpose
Plan 9 `rc` helper script to bind files from sibling `../pc` into a boot build directory and create suffixed stub bindings.

## Main Interfaces
- Invoked as `bindpc pfx sfx`.
- Uses Plan 9 commands `rfork`, `bind`, `ls`, `grep`, and `aux/stub`.

## Implementation Notes
- Exits early if `etherigbe.c` already exists, avoiding repeated setup.
- Deduces current boot directory name and binds it copy-before-change.
- Finds files matching prefix but excluding dotted files, `mkfile`, and existing suffixes.
- Creates blank stub files in `/tmp/blank`, binds them into the current directory, then binds real files over suffixed names.
- Finally binds `../pc` into the boot directory.

## Dependencies And Risks
- Plan 9 namespace script, not portable shell.
- Uses `/tmp/blank` as a shared staging path.
- Existing-file early exit may skip updates if stale bindings are present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/bindpc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/bootld.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/bootld.c

## Purpose
Streaming kernel loader for the PC bootstrap environment. It recognizes Plan 9 exec images, ELF32, ELF64, and gzip-wrapped Plan 9 kernels, loads segments into target memory, and jumps to the kernel.

## Main Interfaces
- Exports `bootpass(Boot *b, void *vbuf, int nbuf)`.
- Exports `impulse()`, `warp9(ulong entry)`, and `prstackuse(int)`.
- Uses external assembly helpers `pagingoff` and `warp64`.

## Implementation Notes
- Maintains a state machine in `Boot.state` with states defined in `dat.h`.
- Provides endian-swapping helpers for ELF headers and program headers.
- ELF32/ELF64 paths read the ELF header, program headers, skip padding without rewind, stream `LOAD` segments to physical addresses, zero BSS tails, and record entry.
- Plan 9 exec path handles `I_MAGIC` and `S_MAGIC`, loads text and data, zeroes BSS, and then boots.
- Gzip path buffers compressed input up to `Kernelmax`, probes the uncompressed exec header with `gunzip`, decompresses full text+data, page-aligns data, and boots.
- `impulse` drains UART output, raises SPL, disables buffered serial output, shuts down devices, and turns interrupts off before transfer.
- Boot transfer uses Multiboot register conventions for ELF/Plan 9 handoff.

## Dependencies And Risks
- Streaming ELF loader cannot rewind, so `LOAD` segments whose file offsets precede `curoff` fail.
- Kernel size and entry are checked against low-memory and `Kernelmax` constraints.
- Gzip decompression uses a fixed allocation and assumes the uncompressed payload is a Plan 9 boot image.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/bootld.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/cga.tiny.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/cga.tiny.c

## Purpose
Tiny CGA text console implementation for the decompressor/early boot environment.

## Main Interfaces
- Exports `cgainit()`.
- Exports `cgaputc(int c)`.

## Implementation Notes
- Writes directly to CGA text memory at physical `0xB8000`.
- Reads and writes CRTC cursor registers through ports `0x3D4/0x3D5`.
- Handles newline, tab, backspace, ordinary characters, cursor movement, and scrolling.
- Uses fixed 80x25 geometry and grey-on-black attribute.

## Dependencies And Risks
- Assumes text-mode CGA-compatible framebuffer at `0xB8000`.
- No locking or bounds beyond simple scroll behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/cga.tiny.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/conf.c

## Purpose
Parses `plan9.ini` or PXE configuration, supports boot menus, manages boot arguments in low memory, reads BIOS-provided memory/APM tables, and provides configuration lookup/prompting for the bootstrap.

## Main Interfaces
- Exports `getstr`, `askbootfile`, `isconf`, `getconf`, `readlsconf`, `addconf`, `changeconf`, and `dotini`.
- Defines global `Chan *conschan`.

## Implementation Notes
- `getstr` prompts on `#c/cons`, supports default values, timeout defaults, and queued-key detection through `kbdq`.
- Menu parsing recognizes `[menu]`, `menuitem=`, `menudefault=`, and `menuconsole=`, then rewrites the active config into `BOOTARGS`.
- `readlsconf` parses low-memory records written by real-mode assembly: `APM\0` records are skipped here, `MAP\0` records populate `mmap`.
- `dotini` normalizes line endings, spaces, comments, blank lines, and tabs before menu parsing and `name=value` extraction.
- Boot args are stored at `CONFADDR`, with an `id` prefix unless already present.
- `changeconf` deletes an existing matching key line and appends a replacement.

## Dependencies And Risks
- Global arrays have `MAXCONF` capacity and only warn for too many lines.
- `getconf` prompts if a key has multiple values.
- Menu parsing mutates the input buffer and uses global menu state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dat.h

## Purpose
Central bootstrap data definitions for the PC boot kernel: machine/process structures, configuration storage, memory-map structures, boot loader state, Multiboot layout, and shared globals.

## Main Interfaces
- Defines `BOOTLINE`, `BOOTARGS`, `BOOTARGSLEN`, `MAXCONF`, `confname`, `confval`, and `nconf`.
- Defines PC kernel-ish structures used by the boot environment: `Lock`, `Label`, `FPsave`, `Conf`, `Mach`, `PCArch`, `ISAConf`, `Mbi`, `Mod`, `MMap`, `Boot`.
- Defines boot state constants used by `bootld.c`.
- Declares major globals such as `arch`, `machp`, `m`, `mmap`, `nmmap`, `multibootheader`, `conschan`, `memstart`, and `memend`.

## Implementation Notes
- The file imports `../port/portdat.h` after defining PC-specific prerequisite types.
- `Boot` contains the current loader state, exec header scratch, entry, and active buffer pointers.
- Multiboot flags and structures match the handoff built before jumping to the loaded kernel.
- `BADPTR(x)` treats addresses below `0x80000000` as invalid kernel pointers in this bootstrap context.

## Dependencies And Risks
- This header is shared by many boot files and must remain ABI-consistent with assembly and `mem.h`.
- Some structures mirror full kernel layouts only as much as the bootstrap needs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/devbios.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/devbios.c

## Purpose
Read-only bootstrap device for BIOS INT 13h EDD/LBA disk access, exposed as a Plan 9 device and usable as a `Bootfs` disk backend.

## Main Interfaces
- Exports `biosinit0`, `biossize`, `biossectsz`, `biosread0`, `biosseek`, and `biosgetfspart`.
- Defines `Dev biosdevtab`.
- Provides `sectread` for single-sector BIOS reads.

## Implementation Notes
- Probes BIOS disk count from BDA `0x475`, then scans drive IDs starting at `0x80`.
- Requires extended disk-drive support with fixed disk and EDD capability bits.
- Uses real-mode INT `0x13` via `realmode(Ureg*)`, with requests staged below 64 KiB.
- `sectread` uses `BIOSXCHG` as low-memory exchange buffer and a `Dap` packet for extended reads.
- `extgetsize` uses BIOS function `0x48` to fill sector size and total sector count.
- Device namespace exposes a top-level `bios` directory and `data` file; writes fail because the device is read-only.
- `biosgetfspart` constructs a `Bootfs` and calls `dosinit` on a named partition, typically `9fat`.

## Dependencies And Risks
- Comments warn that BIOS implementations can hang or time out, especially VMware.
- Reset is present but avoided because it hangs some BIOSes.
- Real-mode buffers must remain below 64 KiB and avoid segment-boundary hazards.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/devbios.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dir.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dir.c

## Purpose
Directory/stat utility code for the bootstrap namespace, including stat conversion, union directory reading, and rewriting directory entries for active mount/bind points.

## Main Interfaces
- Exports `dirchstat`, `dirpackage`, `unionread`, `unionrewind`, `mountrockread`, `mountrewind`, and `mountfix`.

## Implementation Notes
- `dirchstat` obtains a channel stat buffer, grows once if needed, and converts with `convM2D`.
- `dirpackage` validates a packed stat buffer sequence and converts it into an array of `Dir`.
- `unionread` walks mounted union elements using `c->uri` and `c->umc`, skipping unreadable components.
- `mountfix` scans directory stat entries and, when an entry is a mount point, stats the mounted channel but preserves the original entry name.
- Overflow entries produced by mount rewriting are saved in `c->dirrock` and returned by later reads through `mountrockread`.

## Dependencies And Risks
- Implements a subset of full Plan 9 directory semantics in the boot environment.
- Error handling intentionally skips failing union components.
- `mountfix` can stash overflow entries but cannot fully solve too-small caller buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/diskload.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/diskload.c

## Purpose
Disk boot orchestration for `9boot`: discovers storage devices, reads partition tables, finds `9fat`/`plan9.ini`, determines a kernel, and streams it through `bootpass`.

## Main Interfaces
- Exports `bootloadproc(void*)`.
- Provides `partboot(char *path)` and internal disk/FAT boot helpers.
- Provides `dirread0`/`dirread` wrappers around device directory reads with mount/union fixups.

## Implementation Notes
- Binds `#S` into `/dev`, opens `#S`, lists disks, reads each disk ctl file, and calls `readparts`.
- `trydiskboot` initializes `#S/<disk>/9fat`, reads `plan9.ini` when present, parses it with `dotini`, reconfigures serial console, and picks `bootfile`.
- If no `bootfile` is configured, it tries to find a single `9pc`, `9k8`, or `9k10` kernel in the FAT root; otherwise it tries a raw `kernel` partition and finally prompts.
- `trybootfile` accepts `disk!part!file` or `disk!part` syntax, initializes FAT as needed, and loads either from file or partition directly.
- `partboot` streams raw partition bytes to `bootpass`.
- `bootloadproc` loops through discovered disks and eventually prompts forever on failure.

## Dependencies And Risks
- Assumes `#S` storage device namespace and partition ctl format.
- `findonekernel` returns only if exactly one plausible kernel exists.
- FAT root state is global/static in places, matching a simple one-boot-at-a-time model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/diskload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dosboot.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dosboot.c

## Purpose
Minimal read-only FAT12/FAT16/FAT32 filesystem implementation used by the bootstrap loader to read `plan9.ini` and kernel files.

## Main Interfaces
- Exports `dosinit(Bootfs*, char*)`.
- Exports `dosread`, `doswalk`, `dosdirread`, and `dosreadseg`.

## Implementation Notes
- Maintains a 16-entry cluster cache keyed by `Dos*` and sector.
- `getclust` reads clusters from the underlying `Bootfs` device channel using `myreadn`.
- `fatwalk` decodes FAT12, FAT16, or FAT32 chain entries and recognizes end-of-chain markers.
- `fileaddr` maps logical file clusters to physical sectors, with special contiguous handling for FAT12/16 root directories.
- `dosread` reads file bytes cluster-by-cluster, respecting file length for non-directories.
- `doswalk` converts a path component into 8.3 uppercase form and scans directory entries.
- `dosdirread` builds a lower-case file-name array from directory entries.
- `dosinit` validates the boot-sector jump, parses BPB fields, determines FAT type, computes FAT/root/data addresses, and initializes `Bootfs.root`, `read`, and `walk`.

## Dependencies And Risks
- Long filenames are not supported; only 8.3 names are recognized.
- FAT heuristics reject unreasonable BPBs but are intentionally small.
- The cluster cache allocation path does not free buffers in this boot-only environment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dosboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dosfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dosfs.h

## Purpose
Shared FAT boot filesystem structures, partition constants, and `Bootfs` abstraction declarations.

## Main Interfaces
- Defines `Dospart`, `Dosfile`, `Dos`, `Dosboot`, `Dosdir`, `File`, and `Bootfs`.
- Declares `fsread`, `fsboot`, `fswalk`, and `dosinit`.
- Defines FAT partition type constants and DOS attribute bits.

## Implementation Notes
- `Bootfs` embeds `Dos` as its first union member, allowing casts between `Dos*` and `Bootfs*` in `dosboot.c`.
- `File` contains a union currently used for `Dosfile`.
- `Bootfs` can either use a device channel or callback-style disk read/seek functions used by BIOS backends.
- Defines `BADPTR(x)` for simple high-kernel-address validation.

## Dependencies And Risks
- Structure layout coupling is intentional and fragile; `Dos` must stay at the start of `Bootfs`.
- FAT32 fields are present in `Dosboot` but only needed subset is consumed by `dosboot.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/dosfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/expand.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/expand.c

## Purpose
Tiny decompressor/launcher that expands a gzipped boot loader appended after its data segment and transfers control to the protected-mode loader.

## Main Interfaces
- Entry `_main()`.
- Provides tiny runtime helpers `malloc`, `free`, `puts`, `print`, and `exits`.
- Provides A20 helpers `i8042a20`, `a20init`.
- Uses `gunzip` from included `inflate.guts.c`.

## Implementation Notes
- Copies appended payload from `edata` to `Bootkernaddr`, clears BSS, initializes CGA output, and optionally decompresses gzip data from `Unzipbuf`.
- Validates Plan 9 exec magic (`I_MAGIC` or `S_MAGIC`) after byte swapping.
- `run` aligns the data segment to page boundary, prints entry, and calls the entry directly.
- A20 detection writes test values at `0` and `1MB`; enable path first tries keyboard controller command `0xD1`, then system control port A.
- Implements a minimal `%x`, `%p`, `%d`, `%s` formatter over CGA.

## Dependencies And Risks
- Assumes fixed boot memory layout from `mem.h`.
- `malloc` is a bump allocator with no free.
- If A20 cannot be enabled, it prints and spins forever.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/expand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/expand.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/expand.h

## Purpose
Small header for the decompressor/tiny boot environment.

## Main Interfaces
- Defines `ROUND`, `PGROUND`, `HOWMANY`, and `ROUNDUP`.
- Declares `cgainit`, `cgaputc`, `inb`, and `outb`.

## Implementation Notes
- Replaces normally available Plan 9 kernel rounding macros for the standalone decompressor.
- Provides just enough declarations for `expand.c` and `cga.tiny.c`.

## Dependencies And Risks
- Must stay consistent with `mem.h` page size and the assembly I/O helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/expand.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/fns.h

## Purpose
Bootstrap-specific function declaration header layered on top of `../pc/fns.h`.

## Main Interfaces
- Declares boot, BIOS, config, directory, filesystem, PXE, random, stub, and libip helper functions.
- Declares `bootpass`, `askbootfile`, `dotini`, `readlsconf`, `mkmultiboot`, `warp64`, and related routines.

## Implementation Notes
- Bridges normal PC kernel prototypes with the reduced boot environment.
- Provides declarations for local stand-ins like `namecopen`, `readfile`, `myreadn`, and directory packaging.
- Includes a local forward declaration for `File`.

## Dependencies And Risks
- Used by C files that share code with the full kernel but need boot-specific shims.
- Prototype drift against copied PC/kernel code would create subtle build or ABI errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/fs.c

## Purpose
Generic boot filesystem adapter that walks paths and streams files into the kernel loader.

## Main Interfaces
- Exports `nextelem`, `fswalk`, `fsboot`, and `fsread`.

## Implementation Notes
- `nextelem` extracts slash/space-delimited path components into a fixed `NAMELEN` buffer.
- `fswalk` starts from `fs->root` and repeatedly calls the filesystem-specific `walk` method.
- `fsboot` walks to a file, allocates an 8 KiB buffer, reads through `fsread`, and feeds chunks to `bootpass`.
- End-of-file is signaled by `bootpass(b, nil, 0)` to attempt boot.
- `fsread` validates the `File` and filesystem read callback with `BADPTR`.

## Dependencies And Risks
- Path syntax is deliberately simple.
- Always returns `-1` after attempting to boot because successful boot does not return.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.c

## Purpose
Boot-kernel wrapper that includes gzip/deflate support.

## Main Interfaces
- Compiles `inflate.guts.c` into the boot environment.

## Implementation Notes
- Includes kernel/boot headers and `<flate.h>`.
- The actual `gunzip` implementation and helpers live in `inflate.guts.c`.

## Dependencies And Risks
- This file is mostly a compilation-context shim; behavior depends on included code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.guts.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.guts.c

## Purpose
Shared gzip wrapper around Plan 9 flate decompression, included by both `expand.c` and `inflate.c` under different headers.

## Main Interfaces
- Defines `gunzip(uchar *out, int outn, uchar *in, int inn)`.

## Implementation Notes
- Defines a minimal `Biobuf` with base/current/end pointers.
- Builds a CRC table, initializes flate, parses gzip header, inflates through `inflate`, and verifies trailer CRC and uncompressed length.
- `header` handles gzip flags: extra field, original name, comment, and header CRC.
- `crcwrite` updates CRC and copies as much as fits in the output buffer, but advances the output pointer by the full decompressed count.
- `getc` returns `-1` on input exhaustion and prints `EOF`.

## Dependencies And Risks
- Uses Plan 9 `<flate.h>` APIs `inflateinit`, `inflate`, `mkcrctab`, `blockcrc`, and `flateerr`.
- `crcwrite` can report decompressed length beyond output capacity, making callers responsible for interpreting short buffers carefully.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.guts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/iso9660.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/iso9660.h

## Purpose
ISO 9660 and High Sierra CD-ROM on-disk structure definitions for bootstrap filesystem code.

## Main Interfaces
- Defines endian byte-array aliases: `Byte2L`, `Byte2M`, `Byte4LM`, `Byte8LM`, etc.
- Defines volume descriptor constants and `Voldesc`.
- Defines directory record `Drec`.
- Defines `struct Isofile`.

## Implementation Notes
- `VOLDESC` is sector 16 and `Cdsec` is 2048.
- `Voldesc` covers ECMA `CD001` and High Sierra layouts.
- `Drec` models directory records with both normal fields and a small flags view.
- `Isofile` stores format, block size, true and Plan 9 directory offsets, and the current directory record.

## Dependencies And Risks
- Header-only ABI definitions; correctness depends on matching packed on-disk byte layouts.
- Multi-endian fields are left as raw byte arrays for parser conversion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/iso9660.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/ktzero.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/ktzero.s

## Purpose
Defines the `_KTZERO` text symbol used to expose the kernel text-zero address to C.

## Main Interfaces
- `TEXT _KTZERO(SB), $0`.

## Implementation Notes
- `dat.h` declares `extern void _KTZERO(void);` and defines `KTZERO` as the symbol address.
- The symbol acts as an address marker rather than executable logic.

## Dependencies And Risks
- Must link at the intended bootstrap text base for address calculations to be meaningful.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/ktzero.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/l.s

## Purpose
Non-startup x86 assembly support for the protected-mode boot kernel: paging-off handoff, BIOS32 calls, CPU/system-register helpers, atomics, trap entry stubs, interrupt vectors, and SPL primitives.

## Main Interfaces
- Exports `pagingoff`, `bios32call`, `cgapost2`, `ltr`, `invlpg`, `wbinvd`, `lcycles`, `cpuid`, `fpoff`, `fpinit`, `tas`, `_xinc`, `_xdec`, `xchgw`, `cmpswap486`, `mul64fract`, `gotolabel`, `setlabel`, `halt`, `vectortable`, `forkret`, and many register/SPL helpers.
- Defines interrupt-vector call table entries for 0x00-0xFF.

## Implementation Notes
- `pagingoff` double-maps `KZERO` at physical 0, flushes CR3, switches to an identity-mapped path, disables paging, sets Multiboot registers, and jumps to the kernel entry.
- `bios32call` performs a far call through a BIOS32 pointer and copies register state in/out of `BIOS32ci`.
- `cpuid` first checks EFLAGS ID/AC toggling to distinguish 386/486/no-CPUID cases.
- FPU helpers manipulate CR0 EM/TS/NE bits and initialize x87 control word.
- Trap entry saves segment and general registers, switches DS/ES to kernel data selector, calls `trap`, then restores and `IRETL`s.
- `halt` only executes HLT when no runnable processes are ready.

## Dependencies And Risks
- Assembly offsets and vector-entry sizes are known by C trap setup.
- `pagingoff` depends on page-directory layout and Multiboot handoff conventions.
- Some instruction encodings are emitted manually for assembler compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l16r.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/l16r.s

## Purpose
16-bit real-mode startup path for a protected-mode bootstrap image loaded by a primary bootstrap sector.

## Main Interfaces
- Entry symbol `_start16r`.
- Transfers control to `_start32p`.

## Implementation Notes
- Disables interrupts, sets DS/SS, sets a low stack, and tries BIOS A20 enable.
- Sets/validates CGA text mode and prints a startup message through BIOS INT 10h.
- Resets floppy system and turns off the motor.
- Writes APM and E820 memory-map records to `BIOSTABLES` for later parsing by `readlsconf`.
- Loads a basic GDT, sets CR0 protected-mode bit, loads segment registers, and far-jumps to 32-bit protected startup.
- Uses Plan 9 `x16.h` macros to force correct 16-bit encodings under an assembler that assumes protected mode.

## Dependencies And Risks
- BIOS calls may not preserve ES/DI, which the code explicitly works around.
- E820 collection is capped to the `mmap[32+1]` capacity expected by C code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l16r.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l32p.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/l32p.s

## Purpose
32-bit protected-mode startup stage that builds initial page tables, maps low memory and `KZERO`, maps the Mach page, enables paging, and jumps to virtual startup.

## Main Interfaces
- Entry `_start32p`.
- Internal `_start32pg` and `_startpg`.
- Transfers control to `_start32v`.

## Implementation Notes
- Contains a minimal GDT and GDTR pointer for callers entering directly in protected mode.
- Clears pages for bootstrap page directory/page tables plus Mach and GDT pages.
- Populates `LOWPTEPAGES` worth of page tables to map the first `MemMin` bytes.
- Creates double mappings for physical low memory and `KZERO` virtual memory before enabling paging.
- Sets CR3 and CR0 paging/write-protect bits, then jumps into the paged address space.

## Dependencies And Risks
- The code has hand-unrolled page-directory setup for the configured `LOWPTEPAGES`.
- Assumes alignment and memory layout constants from `mem.h`.
- Comments note that offset-sensitive jump bytes must be updated if nearby code layout changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l32p.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l32v.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/l32v.s

## Purpose
Virtual-address startup and core x86 assembly runtime for the boot kernel after paging is enabled.

## Main Interfaces
- Entry `_start32v`, then calls `main`.
- Exports low-level I/O port helpers, descriptor/register helpers, MSR/TSC helpers, barriers, interrupt stubs, and SPL routines.
- Provides `idle`, `hlt`, and disabled legacy `_warp9` code.

## Implementation Notes
- Clears BSS, records `mach0pdb`, `memstart`, `mach0m`, `mach0gdt`, initializes global `m`, and switches stack into the Mach page.
- Provides `inb/ins/inl/outb/outs/outl` and string port I/O helpers used by C drivers.
- Exposes `putidt`, `lgdt`, `lidt`, `putcr3`, `getcr0/getcr2/getcr3/getcr4`, `putcr4`, `rdmsr`, `wrmsr`, `_cycles`.
- Interrupt stubs push trap numbers/error codes and funnel through `intrcommon` to C `trap`.
- SPL routines manipulate EFLAGS interrupt-enable bit directly.

## Dependencies And Risks
- Must remain ABI-consistent with `main.c`, `trap` code, and `Mach` layout.
- Many entry stubs are manually enumerated; missing vectors fall to `intrbad` or generic handling depending on C setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l32v.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l64p.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/l64p.s

## Purpose
Assembly handoff helper for jumping from the 32-bit boot environment to a 64-bit/AMD64 kernel entry.

## Main Interfaces
- Exports `_warp64`, surfaced to C as `warp64(uvlong)`.

## Implementation Notes
- Disables interrupts and saves the target entry in `BP`.
- Double-maps `KZERO` at virtual 0 in the current page directory and flushes CR3.
- Jumps to identity-mapped code, clears the paging bit in CR0, and continues in physical address space.
- Loads Multiboot pointer and magic into `BX` and `AX`, then jumps to the saved entry.

## Dependencies And Risks
- Assumes page-directory layout and `multibootheader` are valid.
- The actual long-mode transition is expected to be handled by the target kernel entry path, not here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/l64p.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/ldecomp.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/ldecomp.s

## Purpose
Real-mode assembly entry for the decompressor image, loaded at `0x10000` or `0x7c00`, that prepares basic BIOS data and switches to protected mode before calling `_main`.

## Main Interfaces
- Entry symbol `origin`.
- Provides `_cgaputs`, `outb`, `inb`, `mb586`, `wbinvd`, and `splhi`.

## Implementation Notes
- Disables interrupts, normalizes DS/SS, sets stack at the origin, enables A20 through BIOS, and forces CGA mode 3.
- Prints `9boot ` using BIOS INT 10h.
- Writes APM and E820 records to `BIOSTABLES`, mirroring the full real-mode startup path.
- Loads a simple GDT, sets protected mode with LMSW encoding, loads segment selectors, sets a high stack, and far-jumps to `_main`.
- Defines a minimal GDT with data, 32-bit code, and 16-bit code descriptors.

## Dependencies And Risks
- Uses manual opcode bytes for protected-mode transition instructions.
- BIOS table layout must match `conf.c` parsing.
- This is decompressor-specific and deliberately smaller than the full boot runtime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/ldecomp.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/main.c

## Purpose
Main protected-mode bootstrap kernel entry and runtime setup for disk/PXE loading the next 386 or AMD64 kernel.

## Main Interfaces
- Exports `main`, `mach0init`, `machinit`, `init0`, `userinit`, `confinit`, `procsetup`, `procrestore`, `procsave`, `reboot`, `exit`, `isaconfig`, `cistrcmp`, `cistrncmp`, `idlehands`, and `trimnl`.
- Calls `bootloadproc` from the initial kernel process.

## Implementation Notes
- `main` enables A20, initializes Mach state, I/O, serial defaults, formatting, screen, traps, MMU, keyboard/timers, CPU ID, BIOS memory maps, memory config, architecture, process system, devices, pages, and scheduler.
- Detects missing PCI VGA and switches to serial-only screen output for headless Soekris-like systems.
- `init0` creates basic root/dot channels, initializes devices, starts alarm kproc, opens console, and enters `bootloadproc`.
- `userinit` creates a minimal kernel process with no user text/stack and schedules `init0`.
- `confinit` sizes bootstrap process/page/image/swap pools conservatively for loader use.
- `reboot` is inherited-style kernel reboot logic: moves to CPU0, shuts down other CPUs/devices, maps low memory, copies reboot trampoline, and jumps.

## Dependencies And Risks
- This is a reduced kernel runtime; many full-kernel paths are disabled or stubbed.
- Initialization ordering is critical: page initialization must follow memory and pool setup, and device loading happens after namespace/proc setup.
- `conf.npage` is forced from `MemMax`, not dynamically sized from all detected memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/mem.h

## Purpose
Shared memory layout, paging, segmentation, and bootstrap address constants for C and assembly.

## Main Interfaces
- Defines page/word sizes, `KZERO`, `KSEGM`, virtual regions, stack sizes, low-memory fixed buffers, boot kernel/decompression addresses, memory scan limits, segment selectors, descriptor flags, PTE flags, and paging index macros.
- Defines constants such as `CONFADDR`, `BIOSXCHG`, `BIOSTABLES`, `Bootkernaddr`, `Unzipbuf`, `Mallocbase`, `MemMin`, `MemMax`, `Kernelmax`, and `LOWPTEPAGES`.

## Implementation Notes
- Reserves the bottom 64 KiB for real-mode return paths and fixed exchange structures.
- Merges `MACHADDR` and `CPU0MACH` because the bootstrap only uses one processor.
- Maps the boot decompressor and kernel staging areas at fixed physical addresses.
- Declares GDT selector layout used by all assembly stages.
- Provides page-directory/page-table index macros used by C and assembler.

## Dependencies And Risks
- Comments explicitly state some invariants, such as `PDX(TMPADDR) == PDX(MACHADDR)`.
- Constants must match loaded-kernel expectations for `CONFADDR`.
- Assembly files depend directly on selector and address values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/memory.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/memory.c

## Purpose
Bootstrap physical/virtual memory map management, initial page-table extension, UMB scanning, and allocation helpers.

## Main Interfaces
- Exports `mapprint`, `memdebug`, `mapfree`, `mapalloc`, `rampage`, `meminit`, `umbmalloc`, `umbfree`, `umbrwmalloc`, `umbrwfree`, `upaalloc`, `upafree`, `upareserve`, `memorysummary`, and `mapping`.

## Implementation Notes
- Maintains resource maps for unbacked physical address space, RAM, upper memory blocks, and read/write UMB device memory.
- `mapfree` inserts/coalesces ranges; `mapalloc` allocates by optional address and alignment.
- `rampage` allocates a page directly from RAM for page-table construction.
- `umbscan` scans `0xD0000-0xF0000` for ROM signatures, writable device memory, and floating-bus free UMB space, then applies `umbexclude`.
- `lowraminit` reserves already-used low memory, frees RAM above `Mallocbase`, and frees unbacked address space above `MemMax`.
- `map` updates resource maps and creates kernel virtual mappings for RAM/UMB regions.
- `meminit` double-maps low memory, sets VGA write-through and BIOS uncached attributes, scans UMBs, initializes low RAM maps, and fills `conf.mem`.

## Dependencies And Risks
- Designed for bootstrap needs, not full physical memory discovery; `MemMax` bounds mapping.
- Fixed-size map arrays can lose ranges and print warnings.
- UMB probing writes test bytes into candidate memory and must avoid ROM/device side effects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pcboot/memory.c -->