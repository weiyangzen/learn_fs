# Group Research: group_1482_plan9_sources_os_plan9_plan9_sys_src_9_pc_usbohci_c_sources_os_plan_ba3fdfd66bd4

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbohci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbohci.c

Plan 9 USB Open Host Controller Interface driver. It registers the `ohci` HCI type through `usbohcilink()` and connects PCI OHCI controllers to the generic USB host-controller layer.

Key responsibilities:
- Scans PCI USB controllers with programming interface `0x10`, maps MMIO registers, disables legacy support, resets the controller, and initializes HCCA, endpoint descriptors, transfer descriptors, and the periodic scheduling tree.
- Exports generic HCI callbacks: `init`, `dump`, `interrupt`, `epopen`, `epclose`, `epread`, `epwrite`, `seprintep`, root-hub `portenable`, `portreset`, `portstatus`, `shutdown`, and `debug`.
- Implements pooled OHCI ED/TD allocation with poison-on-free double-free checks.
- Handles control, bulk, interrupt, and isochronous output endpoints.
- Builds a 32-entry periodic frame tree for interrupt/iso scheduling and tracks rough bandwidth per tree node.
- Processes done TDs from the HCCA done list in interrupt context and wakes blocked endpoint I/O.

Important behavior:
- Non-iso transfers use a dummy-tail TD model; new TDs are chained before moving the ED tail pointer.
- Control transfers run setup, data, and status phases as separate `epio` operations because comments note combined TD chains cause CRC/timeout failures on some devices.
- Bulk writes are chunked to at most `Tdatomic * ep->maxpkt` per operation to avoid babble errors.
- Interrupt endpoints throttle reads/writes against `pollival`.
- Isochronous output preallocates per-frame TDs and buffers, starts about 10 frames ahead, and wakes writers when enough TDs are available.
- Root-hub status converts OHCI port bits to generic hub-port flags and clears change bits as it reports them.
- `*nousbohci` disables attachment.

Dependencies:
- Uses Plan 9 kernel PCI, MMIO mapping, blocks, rendezvous/qlock/ilock, USB endpoint structures from `../port/usb.h`, and generic HCI registration via `addhcitype`.
- Assumes kernel physical/virtual conversion via `PADDR`/`KADDR` and 32-bit descriptor addresses.

Notable risks:
- File header lists missing isochronous input, excessive delays/ilocks, weak bandwidth admission control, inefficient buffering, and missing power-overrun warnings.
- `epgettd` panics for transfers over two pages and manually aligns large buffers to avoid more than one physical page crossing.
- Interrupt processing caps done-list traversal at 1024 TDs and prints if exceeded.
- Some reset/port-reset paths busy-wait without timeout or scheduling backoff.
- Bandwidth accounting is coarse, not per-frame exact.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbohci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbuhci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbuhci.c

Plan 9 USB Universal Host Controller Interface driver. It registers `uhci` and drives PCI UHCI controllers through I/O-port registers and a 1024-entry frame list.

Key responsibilities:
- Scans PCI USB UHCI controllers, reserves I/O ports, resets hardware, builds a UHCI frame list, and creates dummy queue heads for control, interrupt, bulk, and a loopback workaround queue.
- Exports generic HCI callbacks for initialization, dumping, interrupts, endpoint open/close, endpoint read/write, endpoint formatting, root-hub port control/status, shutdown, and debugging.
- Maintains pooled 16-byte-aligned TD and QH objects.
- Implements control, bulk, interrupt, and both read/write isochronous endpoints.
- Processes interrupt completions by scanning all active iso streams and queue heads because UHCI gives no direct completed-queue identity.

Important behavior:
- QHs move through software states `Qidle`, `Qinstall`, `Qrun`, `Qdone`, `Qclose`, and `Qfree`.
- Non-iso I/O builds a TD chain, attaches it to the QH, waits for interrupt/timeout, then copies input data and frees TDs.
- Control transfers run setup, data, and status phases as separate transfers, matching the OHCI driver’s reliability workaround.
- Iso I/O installs TDs directly into frame-list slots at `pollival` spacing and uses circular `tdi`/`tdu` pointers to track hardware/user progress.
- The frame list defaults every frame to the dummy control QH; iso TDs are inserted in front of that frame entry.
- Root-hub helpers manipulate `PORTSC` bits and translate them to generic hub-port flags.
- `*nousbuhci` disables attachment.

Dependencies:
- Uses Plan 9 PCI, I/O port access, DMA address macros, USB endpoint/HCI structures, block/rendezvous locking primitives, and generic HCI registration.
- Assumes UHCI DMA objects are reachable through `PCIWADDR` and the controller can use the allocated physical pages.

Notable risks:
- File header notes too many delays/ilocks, missing per-frame bandwidth admission, interrupt endpoints not using a real scheduling tree, and missing power-overrun warnings.
- Interrupt handler linearly scans all QHs and iso streams on every interrupt.
- Iso close walks frame-list chains and panics if expected TDs are missing.
- `portstatus` error path calls `iunlock` in its `waserror` branch even though the lock may not be held at that point.
- Several waits are busy loops or fixed sleeps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/usbuhci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vga.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vga.c

Common PC VGA screen-console support for Plan 9.

Key responsibilities:
- Initializes replicated black background and white console-color `Memimage` objects with `vgaimageinit`.
- Implements kernel console drawing into the active VGA screen through `vgascreenputs`.
- Handles newline, carriage return, tab, backspace, UTF-8 rune decoding, scrolling, and flush-region tracking.
- Installs the VGA console window and `screenputs` function via `vgascreenwin`.
- Provides generic VGA blanking through sequencer/CRTC registers, though comments say it disrupts modes on tested cards.
- Registers physical video/MMIO segments with `addvgaseg`.
- Draws a diagnostic `cornerstring` at the screen origin.

Dependencies:
- Uses Plan 9 draw/memdraw APIs, `VGAscr`, `screenputs`, `drawlock`, VGA indexed register helpers, and physical segment registration.
- Protects console writes with `vgascreenlock` and opportunistically takes `drawlock`.

Notable risks:
- `xbuf` bounds check uses `sizeof(xbuf)` rather than element count, making the test too permissive in C terms.
- Interrupt-context printing silently drops output if it cannot take `vgascreenlock`.
- `vgablank` is explicitly marked unreliable for preserving video mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vga3dfx.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vga3dfx.c

3dfx Banshee/Voodoo3 VGA aperture and hardware cursor support.

Key responsibilities:
- Detects PCI vendor `0x121A` devices `0x0003` and `0x0005`.
- Maps MMIO BAR0, registers `3dfxmmio`, enables the linear PCI framebuffer, and registers `3dfxscreen`.
- Estimates framebuffer size from DRAM strap registers and reserves the last 1 KiB for cursor storage.
- Implements a 64x64 hardware cursor using the 3dfx cursor MMIO register block.

Important behavior:
- Cursor image is written into framebuffer memory at `scr->storage`.
- Cursor planes are encoded in 128-bit rows with plane 0 in the low 64 bits and plane 1 in the high 64 bits.
- Cursor coordinates use a bottom-right origin adjustment, storing `63 + curs->offset`.

Exports:
- `VGAdev vga3dfxdev` named `3dfx`.
- `VGAcur vga3dfxcur` named `3dfxhwgc`.

Notable risks:
- Memory-size detection is hardware-strap-specific and assumes Banshee/Voodoo3 layout.
- Cursor support depends on linear framebuffer being valid because cursor data is written through `scr->vaddr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vga3dfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaark2000pv.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaark2000pv.c

ARK2000PV VGA bank switching and hardware cursor support.

Key responsibilities:
- Provides `page` callback using sequencer registers `0x15` and `0x16`.
- Enables, disables, loads, and moves a 32x32 X11-style hardware cursor.
- Computes cursor storage from sequencer register `0x10` and uses the last cursor block in video memory.
- Supports both banked and linear framebuffer cursor-memory access.

Important behavior:
- Cursor colors are programmed through sequencer registers `0x26` to `0x2B`.
- Cursor image is written as interleaved AND/XOR-style bytes, with unused portions transparent.
- Negative cursor positions are handled by programming origin offsets so the cursor is not partially offscreen.

Exports:
- `VGAdev vgaark2000pvdev` named `ark2000pv`.
- `VGAcur vgaark2000pvcur` named `ark2000pvhwgc`.

Notable risks:
- Comments say cursor data layout was determined by trial and error.
- Banked cursor loading temporarily changes display page and relies on `scr->devlock` for serialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaark2000pv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgabt485.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgabt485.c

Brooktree Bt485 RAMDAC hardware cursor support, assumed attached to an S3 86C928.

Key responsibilities:
- Provides indirect Bt485 DAC register read/write helpers using S3 CRTC register `0x55`.
- Enables/disables the DAC cursor and S3 external cursor-operation mode.
- Programs cursor colors and loads 64x64x2 cursor RAM.
- Moves cursor through Bt485 cursor X/Y registers.

Important behavior:
- Special access path is used for `Status` and `Cmd3` through command/index register sequencing.
- Cursor RAM is loaded as two 64x64 planes; the Plan 9 16x16 cursor is placed at the top-left.
- Cursor hotpoint assumes a bottom-right origin and adds 64 to offsets.
- Enables both Bt485 cursor mode and S3 DAC cursor control bits.

Exports:
- `VGAcur vgabt485cur` named `bt485hwgc`.

Notable risks:
- Header marks 64x64x2 cursor as always used and interlaced mode unsupported.
- Driver assumes a specific S3/Bt485 wiring and CRTC register semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgabt485.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd542x.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd542x.c

Cirrus Logic GD542x/GD543x/GD5446/GD5480/CL-GD7543 bank switching, linear aperture, and hardware cursor support.

Key responsibilities:
- Provides bank switching through graphics register `0x09`, with mode-dependent shift width.
- Enables linear PCI aperture with Cirrus vendor ID `0x1013`.
- Determines cursor storage from chip ID and memory-size/control registers.
- Implements a 64x64 hardware cursor with alternate shifted cursor image for negative X/Y positions.

Important behavior:
- Cursor colors are written through palette access after setting sequencer register `0x12`.
- Cursor image can be accessed via banked memory or linear aperture depending on sequencer register `0x07`.
- `clgd542xmove` switches between cursor image 0 and image 1 when the cursor is partly offscreen.

Exports:
- `VGAdev vgaclgd542xdev` named `clgd542x`.
- `VGAcur vgaclgd542xcur` named `clgd542xhwgc`.

Notable risks:
- Memory-size inference varies by many chip IDs and falls back silently for unknown chips.
- Uses `scr->set`/`scr->clr` saved cursor data for shifted cursor regeneration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd542x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd546x.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd546x.c

Cirrus Logic GD546x VGA MMIO and hardware cursor support.

Key responsibilities:
- Detects Cirrus PCI devices `0xD0`, `0xD4`, and `0xD6`.
- Maps MMIO BAR1 and registers `clgd546xmmio`.
- Enables linear framebuffer through `vgalinearpci`.
- Implements hardware cursor control through the MMIO cursor register block at offset `0xE0`.

Important behavior:
- Cursor palette writes require setting `PaletteState` bit `0x08`.
- Cursor storage uses the last 2 KiB of framebuffer, allowing two cursor images.
- Cursor data bits are reversed per byte before being stored.
- Negative cursor positions use the hardware preset register rather than regenerating shifted images.

Exports:
- `VGAdev vgaclgd546xdev` named `clgd546x`.
- `VGAcur vgaclgd546xcur` named `clgd546xhwgc`.

Notable risks:
- `scr->storage = ((Seq14 & 7)+1)*1024*1022` is unusual and assumes a specific memory-size encoding.
- Hardware cursor requires MMIO and framebuffer mapping to have succeeded.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaclgd546x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgact65545.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgact65545.c

Chips & Technologies 65545 hardware cursor and page-switch support.

Key responsibilities:
- Provides page switching through I/O ports `0x3D6/0x3D7`.
- Enables/disables cursor through extended I/O ports around `0xA3D0`.
- Allocates cursor storage just beyond the visible framebuffer, aligned to 1024 bytes.
- Generates two 64x64 cursor images for normal and negative-offset cases.

Important behavior:
- Cursor color register is programmed as `0xFFFF0000`.
- Cursor image is encoded as AND/XOR bytes.
- `ct65545move` selects shifted cursor image 1 when X or Y is negative and programs the cursor address register accordingly.

Exports:
- `VGAdev vgact65545dev` named `ct65540`; comment says this is really 65545.
- `VGAcur vgact65545cur` named `ct65545hwgc`.

Notable risks:
- Device name mismatch is explicitly called out as a bug.
- Uses fixed legacy I/O ports and assumes framebuffer memory after visible screen is available.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgact65545.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgacyber938x.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgacyber938x.c

Trident Cyber938x bank switching, linear aperture, optional MMIO mapping, and hardware cursor support.

Key responsibilities:
- Bank-switches through ports `0x3D8/0x3D9`.
- Enables linear PCI aperture for vendor `0x1023`.
- Heuristically maps a 128 KiB MMIO BAR when BAR1 size matches.
- Registers framebuffer and MMIO physical segments.
- Implements 32x32 hardware cursor through CRTC registers.

Important behavior:
- Cursor storage is placed immediately after visible framebuffer contents and programmed in 1 KiB units.
- Cursor loading supports both banked and linear framebuffer access.
- Cursor colors use CRTC registers `0x48` to `0x4F`.
- Negative positions are handled through cursor origin registers.

Exports:
- `VGAdev vgacyber938xdev` named `cyber938x`.
- `VGAcur vgacyber938xcur` named `cyber938xhwgc`.

Notable risks:
- MMIO detection is explicitly described as heuristic and based on XFree86 guidance.
- Cursor comments mention a chip-specific bit needed on 9382, but the named `CursorON` constant just uses `0xC8`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgacyber938x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaet4000.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaet4000.c

Tseng ET4000 bank switching and hardware sprite cursor support.

Key responsibilities:
- Provides page switching through ports `0x3CD` and `0x3CB`.
- Enables/disables the ET4000 sprite cursor through indexed IMA registers at ports `0x217A/0x217B`.
- Programs sprite geometry, cursor storage address, row offset, color depth, and enable bit.
- Loads a 64x64 cursor image into display memory through banked access.

Important behavior:
- Cursor storage is 1024-byte aligned after visible framebuffer and is programmed in doubleword units.
- Cursor data uses two-bit pixel encoding for sprite color, transparent, and invert modes.
- `et4000move` waits for vertical blank before changing cursor coordinates to avoid visible jerkiness.
- `canlock` in move returns failure if the device lock is busy.

Exports:
- `VGAcur vgaet4000cur` named `et4000hwgc`.
- `VGAdev vgaet4000dev` named `et4000`.

Notable risks:
- Comment says cursor pixel encoding is likely wrong for third-edition color values.
- Cursor load changes bank page and does not appear to restore previous page beyond setting the cursor page for the operation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaet4000.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgahiqvideo.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgahiqvideo.c

Chips & Technologies HiQVideo/HiQV32 linear framebuffer and hardware cursor support.

Key responsibilities:
- Detects PCI vendor `0x102C` devices `0x00C0`, `0x00E0`, `0x00E4`, and `0x00E5`.
- Determines video-memory size from device type or extension register `0x43`.
- Enables linear PCI framebuffer and registers `hiqvideoscreen`.
- Uses the last 4 KiB of framebuffer as cursor storage, stored in `scr->mmio`.
- Implements 32x32 hardware cursor through extension registers at `0x3D6/0x3D7`.

Important behavior:
- Cursor enable and storage address are programmed through XR registers `0xA0`, `0xA2`, and `0xA3`.
- Cursor color programming temporarily toggles XR `0x80`.
- Negative cursor coordinates are encoded with high-bit flags in position registers.
- `hiqvideolinear` is a no-op because enable already maps the linear framebuffer.

Exports:
- `VGAdev vgahiqvideodev` named `hiqvideo`.
- `VGAcur vgahiqvideocur` named `hiqvideohwgc`.

Notable risks:
- Uses `scr->mmio` as a pointer into framebuffer cursor storage, not MMIO registers, which differs from most VGA drivers.
- Only selected HiQVideo IDs are supported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgahiqvideo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgai81x.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgai81x.c

Intel i81x/i830M integrated graphics framebuffer, DPMS blanking, GTT setup, and hardware cursor support.

Key responsibilities:
- Detects supported Intel PCI display IDs including i810/i815-style devices and IBM R31 i830M.
- Maps MMIO BAR1 and registers `i81xmmio`.
- Allocates and installs a graphics translation table through MMIO register `0x2020`.
- Maps framebuffer BAR0 and allocates backing pages, populating device page tables.
- Allocates an uncached page for cursor data and marks its PTE uncached.
- Implements DPMS blanking and 32x32 2bpp hardware cursor.

Important behavior:
- Framebuffer aperture size is capped to 8 MiB.
- Cursor base register uses the physical address of the uncached system-memory cursor page.
- Cursor move uses hardware negative-coordinate flags in position bits.
- Enabling installs `scr->blank = i81xblank` and sets `hwblank`.

Exports:
- `VGAdev vgai81xdev` named `i81x`.
- `VGAcur vgai81xcur` named `i81xhwgc`.

Notable risks:
- Directly manipulates MMU PTE flags for the cursor page.
- Allocated framebuffer backing memory is not freed and is bound to device page-table setup.
- GTT setup assumes register offsets and page-table format for these old Intel chips.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgai81x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgamach64xx.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgamach64xx.c

ATI Mach64 CT/ET/GT/VT/LT-family VGA driver with linear framebuffer mapping, hardware cursor, optional panning, 2D acceleration, LCD blanking, and video overlay support.

Key responsibilities:
- Detects supported ATI PCI device IDs and records chip family metadata.
- Enables I/O register base and maps linear framebuffer; maps the MMIO register page at the end of the aperture and marks it uncached.
- Provides register access abstraction for legacy I/O, normal MMIO, and bank-1 overlay registers.
- Implements 64x64 hardware cursor, including panning support through CRTC offset/pitch changes.
- Initializes 2D engine and exports hardware fill/scroll for supported MMIO configurations.
- Provides LCD-specific blanking for LT/LTPro/Mobility chips.
- Implements overlay control commands: `openctl`, `closectl`, `configure`, `enable`, and `status`.
- Copies overlay video frames into the allocated overlay buffer on write.

Important behavior:
- Cursor data is placed after visible framebuffer contents, aligned to 64-bit units.
- Cursor is placed in the top-right of the 64x64 array and coordinate programming compensates with `CurHVoff`.
- `initengine` resets and initializes the GUI engine, derives PLL reference clock from VGA BIOS data, and determines revision class from `ConfigChipId`.
- Fill and scroll wait on FIFO/idle and handle 24-bit modes specially.
- Overlay supports YUYV configuration input but programs `SCALE_IN_YVYU422`.
- Overlay buffer is placed after cursor storage if no overlay buffer has been assigned.

Exports:
- `VGAdev vgamach64xxdev` named `mach64xx`.
- `VGAcur vgamach64xxcur` named `mach64xxhwgc`, with `doespanning` set.

Notable risks:
- Global overlay state (`ovl_chan`, dimensions, format, buffer) is shared rather than per-screen.
- Overlay format handling is narrow and partly inconsistent in naming/programming.
- Reads VGA BIOS tables directly at `0xC000`, which assumes PC BIOS availability and table layout.
- Busy waits for FIFO/idle can print timeout diagnostics but do not recover hardware.
- `mach64blank` is present but disabled because comments say it corrupts timings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgamach64xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgamga2164w.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgamga2164w.c

Matrox Millennium/Millennium II MGA-2064W/MGA-2164W framebuffer mapping and TI TVP3026 RAMDAC cursor support.

Key responsibilities:
- Detects Matrox PCI IDs `MGA2164AGP`, `MGA2164`, and `MGA2064`.
- Maps MMIO from the appropriate BAR depending on chip and maps a linear framebuffer aperture.
- Registers `mga2164wmmio` and `mga2164wscreen` segments.
- Implements TVP3026 DAC cursor disable/load/move/enable through MMIO DAC registers at offset `0x3C00`.

Important behavior:
- MGA2064 uses BAR0 for MMIO and BAR1 for an 8 MiB framebuffer; newer variants use BAR1 for MMIO and BAR0 for a 16 MiB framebuffer.
- Cursor RAM is 64x64 with two planes and uses TVP3026 three-color mode.
- Cursor offsets add 64 for bottom-right origin behavior.

Exports:
- `VGAdev vgamga2164wdev` named `mga2164w`.
- `VGAcur vgamga2164wcur` named `mga2164whwgc`.

Notable risks:
- No draw acceleration is exported despite MMIO mapping.
- Cursor support assumes the TVP3026 DAC layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgamga2164w.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgamga4xx.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgamga4xx.c

Matrox G200/G400/G450/G550 VGA driver with framebuffer sizing, DAC cursor, DPMS blanking, and 2D acceleration.

Key responsibilities:
- Detects Matrox PCI IDs `MGA4xx`, `MGA550`, and `MGA200`.
- Maps a 16 KiB MMIO window and linear framebuffer.
- Probes actual video memory by writing/checking 2 MiB boundaries after enabling MGA mode.
- Implements DAC cursor controls through MMIO DAC registers at `0x3C00`.
- Implements DPMS blanking with sequencer and CRTC extension registers.
- Initializes 2D engine state and exports fill/scroll acceleration.

Important behavior:
- Cursor storage is placed at the last 4 KiB of the detected aperture.
- Cursor base address is programmed in 1 KiB units through indirect DAC cursor-address registers.
- Fill uses solid `DWGCTL` trap/rectangle operation; scroll uses bitblt with overlap direction handling.
- `mga4xxdrawinit` sets pitch, memory access format for 8/16/24/32 bpp, fill, scroll, and blank callbacks.

Exports:
- `VGAdev vgamga4xxdev` named `mga4xx`.
- `VGAcur vgamga4xxcur` named `mga4xxhwgc`.

Notable risks:
- Memory-size probe is described as “sketchy” and writes into framebuffer memory.
- FIFO wait has a very small fixed timeout and only prints on timeout.
- Acceleration assumes supported depth and silently returns without acceleration for others.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgamga4xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vganeomagic.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vganeomagic.c

NeoMagic MagicGraph/MagicMedia VGA driver with linear framebuffer, hardware cursor, and 2D acceleration.

Key responsibilities:
- Detects supported NeoMagic PCI IDs and selects cursor-register offset, video-memory size, and MMIO BAR/offset.
- Maps MMIO, registers `neomagicmmio`, maps linear framebuffer, and registers `neomagicscreen`.
- Places two 1 KiB cursor images at the end of video memory.
- Implements 64x64 cursor image generation, negative-position shifted image generation, and cursor register programming.
- Initializes NeoMagic blitter state and exports hardware fill/scroll for supported depths and widths.

Important behavior:
- Older 128ZV uses an MMIO region offset from BAR0; later devices use BAR1.
- Cursor address bits are rearranged before writing the cursor address register.
- Blitter mode depends on screen depth and width; 24 bpp is explicitly not supported for acceleration.
- Fill and scroll use MMIO blit registers with busy/FIFO polling.

Exports:
- `VGAdev vganeomagicdev` named `neomagic`.
- `VGAcur vganeomagiccur` named `neomagichwgc`.

Notable risks:
- Comments note MMIO layout may differ for older chips.
- `waitforidle` and `waitforfifo` timeout diagnostics are commented out, so hangs can be quiet.
- 24 bpp acceleration is intentionally disabled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vganeomagic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vganvidia.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vganvidia.c

NVIDIA PCI VGA driver with framebuffer/MMIO setup, hardware cursor, DMA command ring initialization, DPMS blanking, and 2D fill/scroll acceleration.

Key responsibilities:
- Detects NVIDIA PCI display devices with vendor `0x10DE`.
- Maps MMIO BAR0, registers `nvidiammio`, maps linear framebuffer, and registers `nvidiascreen`.
- Determines video-memory size through generation-specific register or PCI config paths.
- Implements hardware cursor for old PRAMIN-based and newer framebuffer-based cursor storage layouts.
- Implements DMA command ring management using macros from `nv_dma.h`.
- Initializes acceleration objects and exports rectangle fill and screen-to-screen blit.
- Implements DPMS blanking through sequencer and CRTC registers.

Important behavior:
- Newer chips place cursor storage near the end of aperture and program CRTC cursor-location registers.
- DMA ring is placed near the end of video memory; if outside mapped aperture, it maps that physical region explicitly.
- `nvdmawait` handles ring wrap by writing skip markers and moving PUT pointer.
- `nvidiadrawinit` resets graphics, installs blank/fill/scroll callbacks, and sets `hwblank`.

Exports:
- `VGAdev vganvidiadev` named `nvidia`.
- `VGAcur vganvidiacur` named `nvidiahwgc`.

Notable risks:
- Uses a single global `nv` DMA state, so multi-card state would collide.
- If DMA buffer mapping fails, it disables `hwaccel` and `hwblank` globally.
- Busy waits for DMA idle and PGRAPH idle can time out but do not reset/recover.
- Some source derives from NVIDIA sample code with its own copyright notice.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vganvidia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaradeon.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaradeon.c

ATI Radeon [789]xxx VGA driver with MMIO/framebuffer setup, hardware cursor, DPMS blanking, and dormant 2D acceleration helpers.

Key responsibilities:
- Detects supported Radeon devices using `/sys/src/cmd/aux/vga/radeon.h` PCI ID table.
- Maps MMIO BAR2, registers `radeonmmio`, maps the PCI framebuffer, and registers `radeonscreen`.
- Provides MMIO and PLL access helpers.
- Implements 64x64 ARGB-style hardware cursor stored near the end of the aperture.
- Implements DPMS blanking via `CRTC_EXT_CNTL`.
- Defines 2D engine reset/init, fill, and scroll functions.

Important behavior:
- Cursor storage is one MiB below the end of aperture and is accessed through `KADDR(scr->paddr + storage)`.
- Cursor move handles negative coordinates with hardware offset registers and adjusts `CUR_OFFSET`.
- `radeondrawinit` supports 8/15/16/32 bpp, resets 2D engine, sets pitches/offsets, and installs fill/scroll/blank callbacks.
- In the exported `VGAdev`, acceleration-related callbacks after `radeondrawinit` are guarded by `#ifdef HW_ACCEL`; `HW_ACCEL` is commented out.

Exports:
- `VGAdev vgaradeondev` named `radeon`.
- `VGAcur vgaradeoncur` named `radeonhwgc`.

Notable risks:
- The expression in `radeonwaitfifo` relies on C precedence and appears likely wrong: `INREG(...) & RBBM_FIFOCNT_MASK >= entries`.
- Overlay control/write/flush are stubs.
- Acceleration code exists but is not fully exported unless compiled with `HW_ACCEL`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgaradeon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgargb524.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgargb524.c

IBM RGB524 RAMDAC hardware cursor support, assumed attached to S3 Vision964/968-class hardware.

Key responsibilities:
- Selects DAC register bank through S3 CRTC register `0x55`.
- Provides indexed RGB524 register write helper.
- Enables/disables a 32x32 mode-2 X-Windows-style hardware cursor.
- Loads cursor RAM array through auto-increment indexed DAC access.
- Programs cursor colors, hotpoint, and X/Y position.

Important behavior:
- Cursor array starts at indexed register `0x100`.
- Cursor data packs four two-bit cursor pixels per byte.
- Hotpoint registers store negative Plan 9 cursor offsets.
- Move writes raw point coordinates; hotpoint handles offset correction.

Exports:
- `VGAcur vgargb524cur` named `rgb524hwgc`.

Notable risks:
- Assumes RGB524 is wired behind S3 CRTC RS2 selection.
- No `VGAdev` mapping or framebuffer setup is provided here; it is cursor-only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgargb524.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgas3.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgas3.c

S3 VGA driver for bank switching, linear aperture setup, hardware cursor, ViRGE acceleration, blanking, and delegation to Savage acceleration.

Key responsibilities:
- Provides S3 bank-switching through CRTC registers `0x35` and `0x51`.
- Maps linear framebuffer for S3 PCI devices and registers `s3screen`.
- Maps Savage MMIO apertures for selected Savage/ProSavage/SuperSavage devices.
- Implements S3 hardware cursor in Microsoft Windows format.
- Implements ViRGE hardware fill/scroll for selected chips through MMIO registers in the linear aperture.
- Installs blanking and delegates Savage-family acceleration setup to `savageinit` from `vgasavage.c`.

Important behavior:
- Some chip IDs bypass bank switching or cursor bank-locking because they use linear storage.
- Cursor enable/disable waits for vertical sync active to avoid cursor-fetch hangs on 80x chips.
- Cursor image is AND/XOR interleaved words; negative X offset is rounded to even due to a hardware edge bug.
- `s3drawinit` enables acceleration only for known ViRGE and Savage IDs.

Exports:
- `VGAdev vgas3dev` named `s3`.
- `VGAcur vgas3cur` named `s3hwgc`.

Notable risks:
- Comments say other ViRGE chips may work but are not enabled because FIFO size is unknown.
- Wait counters record linear/FIFO/idle timeouts but do not actively recover.
- `hwblank` is deliberately not enabled for S3 blanking because it is “not known to work well.”
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgas3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgasavage.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgasavage.c

S3 Savage-family 2D acceleration and blanking support used by `vgas3.c`.

Key responsibilities:
- Defines Savage MMIO packed-register offsets, status bits, draw commands, bitmap descriptors, and status register variants.
- Provides `savageinit(VGAscr*)` for selected Savage4, ProSavage, SuperSavage, SavageIX, and SavageMX device IDs.
- Resets the 2D engine, disables BCI paths, enables 32-bit MMIO writes, enables linear access and graphics engine, and configures bitmap descriptors.
- Installs hardware fill, scroll, and blank callbacks on `VGAscr`.

Important behavior:
- Uses different idle-status register/mask logic for Savage4/ProSavage versus SuperSavage/SavageIX/SavageMX.
- Fill programs foreground/background colors, mix registers, rectangle position/size, and a fill draw command.
- Scroll selects direction based on rectangle overlap and issues a bitblt draw command.
- Blanking controls monitor DPMS through sequencer register `0xD` and LCD power through sequencer register `0x31`.
- `savageinit` programs GBD twice due to empirical hardware behavior noted in comments.

Dependencies:
- Not a standalone `VGAdev`; `vgas3.c` calls `savageinit`.
- Requires `scr->mmio` and `scr->id` to already be set by S3 setup.

Notable risks:
- Header comments explain several hardware interfaces were abandoned due to poor/contradictory documentation.
- Unsupported Savage IDs print and return without acceleration.
- `hwblank` is set to 0 after installing `savageblank`, so global hardware blank enable is intentionally conservative.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/vgasavage.c -->