# Group Research: group_18_9front_sources_os_plan9_9front_sys_src_9_pc_usbohci_c_sources_os_plan_36a44b0f3ca8

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbohci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/usbohci.c

## Role

Plan 9/9front USB Open Host Controller Interface driver. It binds PCI OHCI controllers into the generic USB HCI layer, owns OHCI endpoint/transfer descriptors, services root-hub port operations, and implements control, bulk, interrupt, and isochronous-output endpoint I/O.

## Main Interfaces

- Registers HCI type `ohci` through `usbohcilink()` and `addhcitype("ohci", reset)`.
- Fills generic `Hci` callbacks: `init`, `interrupt`, `epopen`, `epstop`, `epclose`, `epread`, `epwrite`, `seprintep`, `portenable`, `portreset`, `portpower`, `portstatus`, `shutdown`, and `debug`.
- PCI discovery matches USB serial-class devices with programming interface `0x10`, maps BAR0 MMIO, and records IRQ/TBDF/port base.

## Key Behavior

- Models OHCI hardware structures directly: endpoint descriptors (`Ed`), transfer descriptors (`Td`), host-controller communication area (`Hcca`), MMIO register block (`Ohci`), and a software periodic scheduling tree (`Qtree`).
- Uses pooled aligned ED/TD allocation, physical-address conversion helpers, and a 32-entry HCCA interrupt table for periodic scheduling.
- Maintains control and bulk ED lists through controller head registers, and schedules interrupt/isochronous EDs into a bandwidth-aware tree.
- Builds TD chains for normal endpoint I/O, waits for completion through `Rendez`, records data toggles/errors, clears stalls, and aborts active TDs on cancellation or close.
- Control transfers are assembled as setup, optional data, and status phases; bulk/interrupt transfers chunk requests into bounded TD groups.
- Isochronous support is output-oriented: it preallocates frame TDs, advances frame numbers, buffers samples, and reports underrun/error state. The file comment explicitly lists missing isochronous input streams as a bug.
- `interrupt()` processes writeback-done heads, root-hub status changes, unrecoverable errors, and scheduling overruns, then wakes endpoint waiters.
- Controller reset handles SMM ownership handoff, disables legacy support, initializes HCCA/list registers, enables OHCI lists and interrupts, powers ports, and puts the controller in operational state.

## Dependencies And Assumptions

- Depends on Plan 9 PCI, interrupt, memory-mapping, locking, and generic USB host-controller infrastructure from `../port/usb.h`.
- Uses `xspanalloc` for alignment-sensitive DMA-visible structures and assumes hardware can DMA the addresses produced by `ptr2pa`.
- Supports `*nousbohci` config opt-out and optional controller selection by `hp->port`.
- Uses many controller locks and timed sleeps; comments call out excessive delays/ilocks and incomplete bandwidth admission.

## Research Notes

- This is a core USB storage/input substrate file rather than a filesystem file. It is relevant to subset A because USB mass-storage and other device namespaces depend on this HCI transport.
- Root-hub port status is translated into generic hub status bits (`HPpresent`, `HPenable`, `HPslow`, change flags).
- Error strings map OHCI TD condition codes into user-visible endpoint errors such as CRC, stall, underrun, overrun, and timeout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbohci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbuhci.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/usbuhci.c

## Role

Plan 9/9front USB Universal Host Controller Interface driver. It binds legacy PCI UHCI controllers into the generic USB HCI layer and implements USB endpoint I/O over UHCI frame lists, queue heads, and transfer descriptors.

## Main Interfaces

- Registers HCI type `uhci` through `usbuhcilink()` and `addhcitype("uhci", reset)`.
- Fills generic `Hci` callbacks: `init`, `interrupt`, `epopen`, `epstop`, `epclose`, `epread`, `epwrite`, `seprintep`, `portenable`, `portreset`, `portstatus`, `shutdown`, and `debug`.
- PCI discovery matches USB serial-class UHCI devices with programming interface `0`, reserves BAR4 I/O ports, and records IRQ/TBDF/port base.

## Key Behavior

- Defines UHCI I/O registers, port-status bits, TD/QH link/status/token bits, and software queue states.
- Owns aligned pools for `Td` and `Qh`; TDs include a small embedded buffer for tiny transfers and optional allocated buffers for larger transfers.
- Builds a 1024-entry UHCI frame list and dummy queue-head chain for control, interrupt, and bulk schedules. A terminal dummy TD loops to itself as a documented PIIX4 erratum workaround.
- Endpoint open allocates per-direction queue state for control, bulk, interrupt, or isochronous endpoints. Endpoint close/cancel aborts queued TDs and waits for hardware state to settle.
- Normal endpoint I/O builds TD chains, links them to a QH, kicks the controller, waits for interrupt/poll completion, updates data toggles, and maps UHCI status bits to errors.
- Control transfers are assembled as setup, optional data, and status phases. Bulk and interrupt transfers are chunked by maximum TD length and endpoint max packet size.
- Isochronous paths support both read and write, maintain per-frame TD pointers, buffer delay, frame-number tracking, and consecutive error accounting.
- Interrupt handling acknowledges controller status, walks active QHs and isochronous streams, transitions completed work to done state, and wakes sleepers. Missed work is handled by wait/poll paths.
- Reset disables legacy mode, stops the controller, issues global and host-controller resets, restores SOF timing, programs frame-list base, enables interrupts, and starts execution.

## Dependencies And Assumptions

- Depends on Plan 9 PCI, I/O-port allocation, interrupt, DMA-visible memory, and generic USB host-controller infrastructure.
- Uses 32-bit PCI window macros for hardware links and assumes DMA-visible frame/QH/TD allocations.
- Supports `*nousbuhci` config opt-out and optional controller selection by I/O port.
- File-level BUG comments note excessive delays/ilocks, incomplete per-frame bandwidth admission, and a simpler interrupt-endpoint schedule than OHCI/EHCI.

## Research Notes

- This is the companion legacy USB transport to `usbohci.c`, important for devices exposed higher in Plan 9 as files.
- Root-hub handling is two-port by default but `init()` probes additional UHCI ports by reading port-status registers.
- UHCI is I/O-port based, unlike OHCI’s MMIO register block.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/usbuhci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vga.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vga.c

## Role

Low-level Plan 9 PC VGA screen-console support. It initializes the framebuffer console image, writes kernel text to the active screen, handles scrolling, blanking, and exposes framebuffer segments for mapping.

## Main Interfaces

- `vgaimageinit(ulong chan)`: initializes the `Memimage` backing the VGA console.
- `vgascreenputs(char *s, int n)`: console text output entry point.
- `vgascreenwin(VGAscr *scr)`: updates the visible window rectangle for the active screen.
- `vgablank(VGAscr *scr, int blank)`: invokes a driver blank hook when present.
- `addvgaseg(char *name, ulong pa, ulong len)`: publishes physical framebuffer/MMIO regions as image segments.

## Key Behavior

- Creates black and white `Memimage` color tiles and binds the kernel screen image to `gscreen`.
- `vgascreenputc()` interprets newline, tab, backspace, carriage return, and ordinary UTF text rendering using `memimagestring`.
- Scrolls by copying the existing text area upward and clearing the final line when the cursor reaches the bottom.
- `vgascreenputs()` serializes drawing with `screenlock`, decodes runes, writes text, flushes the changed rectangle, and falls back to serial output when the screen is unavailable.
- `vgascreenwin()` computes the logical visible rectangle from configured screen width, actual size, and tilt settings.
- `addvgaseg()` records named physical display regions in the global image segment table.

## Dependencies And Assumptions

- Depends on Plan 9 draw/memdraw types, `VGAscr`, global `vgascreen[0]`, screen locks, cursor hooks, and flush callbacks.
- Assumes a single primary VGA screen for console output.
- `vgablank()` is a dispatcher; real blanking logic lives in chipset-specific VGA drivers.

## Research Notes

- This file is the bridge between kernel text output and the graphics driver modules in the rest of this group.
- It is not a filesystem implementation, but exposed framebuffer segments and `devvga` control files depend on this screen state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vga3dfx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vga3dfx.c

## Role

VGA support module for 3dfx graphics adapters, focused on linear framebuffer setup and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vga3dfxdev` named `3dfx`.
- Exports `VGAcur vga3dfxcur` named `3dfxhwgc`.
- Main routines: `tdfxenable`, `tdfxcurenable`, `tdfxcurdisable`, `tdfxcurload`, and `tdfxcurmove`.

## Key Behavior

- Validates PCI vendor `0x121A` and requires a memory BAR, then maps the linear framebuffer with `vgalinearpci`.
- Treats cursor registers as a small `Cursor3dfx` structure in MMIO.
- Loads the Plan 9 16x16 cursor into the adapter’s larger cursor bitmap format, tracks hotspot offsets, and handles negative/offscreen cursor positions by adjusting origin and offsets.
- Enables/disables cursor display through `vidProcCfg` bits and sets cursor colors/registers during enable.

## Dependencies And Assumptions

- Depends on PCI discovery already stored in `scr->pci`, `screen.h` VGA structures, and Plan 9 cursor bitmaps.
- Assumes the 3dfx cursor register layout and framebuffer mapping match the expected adapter generation.

## Research Notes

- No acceleration hooks are installed; this module only supplies device enable and hardware cursor operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vga3dfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaark2000pv.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaark2000pv.c

## Role

VGA support module for ARK Logic ARK2000PV adapters, including banked framebuffer paging and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaark2000pvdev` named `ark2000pv`.
- Exports `VGAcur vgaark2000pvcur` named `ark2000pvhwgc`.
- Main routines: `ark2000pvpage`, `ark2000pvenable`, `ark2000pvdisable`, `ark2000pvload`, and `ark2000pvmove`.

## Key Behavior

- Implements page switching through VGA graphics/controller registers, with separate handling for 8-bit and higher-depth modes.
- Configures cursor memory in the last 16 KiB of video memory and selects cursor storage blocks through extended CRT registers.
- Loads the Plan 9 cursor into the adapter’s 64x64 cursor pattern area, preserving/restoring the bank page when linear addressing is not used.
- Handles cursor motion with hotspot correction and negative-coordinate clipping.

## Dependencies And Assumptions

- Depends on standard VGA register helpers (`vgaxi`, `vgaxo`) and `VGAscr` storage fields.
- Assumes cursor memory is available at the configured high-memory storage offset.

## Research Notes

- This is a legacy banked VGA module; there is no linear aperture setup or drawing acceleration hook in the exported `VGAdev`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaark2000pv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgabt485.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgabt485.c

## Role

Hardware cursor support for Brooktree Bt485-compatible RAMDACs.

## Main Interfaces

- Exports `VGAcur vgabt485cur` named `bt485hwgc`.
- Main routines: indexed DAC register access helpers, `bt485enable`, `bt485disable`, `bt485load`, and `bt485move`.

## Key Behavior

- Implements Bt485 indexed I/O through palette/cursor address and control registers.
- Programs cursor mode 3, external operation mode, and cursor colors.
- Loads a 16x16 Plan 9 cursor into the Bt485 64x64x2 cursor RAM layout, clearing unused rows and columns.
- Maintains hotspot offsets with the DAC’s 64-pixel cursor origin bias and writes X/Y low/high position registers.

## Dependencies And Assumptions

- Depends on VGA DAC I/O helpers and Bt485-compatible register behavior.
- This file exports only a cursor driver, not a full `VGAdev`; it is used by chipset modules that pair with a Bt485 RAMDAC.

## Research Notes

- The implementation is DAC-oriented rather than PCI/chipset-oriented.
- Cursor color handling uses black/white palette entries and does not expose programmable cursor colors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgabt485.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaclgd542x.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaclgd542x.c

## Role

VGA support module for Cirrus Logic GD542x adapters, covering bank switching, optional PCI linear aperture setup, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaclgd542xdev` named `clgd542x`.
- Exports `VGAcur vgaclgd542xcur` named `clgd542xhwgc`.
- Main routines: `clgd542xpage`, `clgd542xlinear`, `clgd542xenable`, `clgd542xdisable`, `clgd542xload`, and `clgd542xmove`.

## Key Behavior

- Switches display banks by updating graphics register `0x09`, using depth-dependent bit placement.
- Uses `vgalinearpci()` for a PCI linear framebuffer when requested.
- Initializes hardware cursor registers, cursor colors, and cursor storage in the last 16 KiB of video memory.
- Loads cursor images through either the linear framebuffer or temporary bank switching, depending on current aperture state.
- Supports two cursor image slots to handle partially offscreen cursor positions.

## Dependencies And Assumptions

- Depends on Cirrus extended VGA registers and standard `VGAscr` fields such as `storage`, `vaddr`, and `apsize`.
- Assumes enough display memory is reserved for cursor storage.

## Research Notes

- The code takes care not to call generic color setters while the cursor lock is held, using direct palette writes instead.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaclgd542x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaclgd546x.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaclgd546x.c

## Role

VGA support module for Cirrus Logic GD546x adapters, with PCI linear framebuffer setup and MMIO-style hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaclgd546xdev` named `clgd546x`.
- Exports `VGAcur vgaclgd546xcur` named `clgd546xhwgc`.
- Main routines: `clgd546xenable`, `clgd546xlinear`, `clgd546xcurenable`, `clgd546xcurdisable`, `clgd546xcurload`, and `clgd546xcurmove`.

## Key Behavior

- Uses `vgalinearpci()` for linear framebuffer mapping.
- Maps cursor control through a `Cursor546x` register structure.
- Stores a 64x64 cursor bitmap in display memory, converts Plan 9 cursor mask/set data into the adapter format, and tracks hotspot offsets.
- Enables/disables and moves the hardware cursor by writing cursor control, address, color, and X/Y registers.

## Dependencies And Assumptions

- Depends on PCI-backed VGA screen state and a known GD546x cursor register block.
- Requires `scr->storage` to point to display memory reserved for cursor data.

## Research Notes

- No drawing acceleration hooks are exported; this module is cursor and aperture setup only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaclgd546x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgact65545.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgact65545.c

## Role

VGA support module for Chips & Technologies CT65545-family adapters, covering bank switching and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgact65545dev` named `ct65540` with a comment noting it is really CT65545.
- Exports `VGAcur vgact65545cur` named `ct65545hwgc`.
- Main routines: `ct65545page`, `ct65545enable`, `ct65545disable`, `ct65545load`, and `ct65545move`.

## Key Behavior

- Implements page switching through extended sequencer registers.
- Initializes cursor control registers, color entries, and cursor storage location.
- Converts and writes the Plan 9 cursor bitmap into adapter cursor memory.
- Moves the cursor with hotspot correction and offscreen clipping.

## Dependencies And Assumptions

- Depends on VGA sequencer/CRT indexed register helpers and `VGAscr` cursor storage fields.
- Assumes CT65545-compatible cursor register behavior despite the exported device name.

## Research Notes

- This is a compact legacy VGA module with no PCI probing or acceleration path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgact65545.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgacyber938x.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgacyber938x.c

## Role

VGA support module for Trident Cyber938x adapters, providing bank switching, PCI linear aperture setup, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgacyber938xdev` named `cyber938x`.
- Exports `VGAcur vgacyber938xcur` named `cyber938xhwgc`.
- Main routines: `cyber938xpage`, `cyber938xlinear`, `cyber938xcurenable`, `cyber938xcurdisable`, `cyber938xcurload`, and `cyber938xcurmove`.

## Key Behavior

- Switches framebuffer banks through Trident extended registers.
- Uses `vgalinearpci()` to configure linear memory.
- Loads the Plan 9 cursor into a 64x64 hardware cursor area in display memory.
- Programs cursor address, X/Y position, colors, and enable bits using Cyber938x CRT registers.

## Dependencies And Assumptions

- Depends on Trident-specific extended VGA register semantics.
- Assumes cursor storage has been reserved in display memory via `scr->storage`.

## Research Notes

- The exported `VGAdev` has no enable/disable/drawinit hooks; it supplies page and linear-aperture functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgacyber938x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaet4000.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaet4000.c

## Role

VGA support module for Tseng ET4000 adapters, including banked framebuffer paging and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaet4000dev` named `et4000`.
- Exports `VGAcur vgaet4000cur` named `et4000hwgc`.
- Main routines: `et4000page`, `et4000enable`, `et4000disable`, `et4000load`, and `et4000move`.

## Key Behavior

- Programs ET4000 page registers for banked VGA memory access.
- Initializes cursor mode, cursor color, and cursor memory pointers.
- Loads Plan 9 cursor bitmap data into the ET4000 hardware cursor representation.
- Handles cursor movement with hotspot and negative-coordinate correction.

## Dependencies And Assumptions

- Depends on ET4000 extended VGA registers and standard Plan 9 VGA helper routines.
- Assumes banked display memory and reserved cursor storage.

## Research Notes

- This is a legacy non-PCI-specific module; it provides no linear aperture or acceleration hook.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaet4000.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgageode.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgageode.c

## Role

VGA support module for AMD/NS Geode graphics, covering framebuffer/MMIO setup and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgageodedev` named `geode`.
- Exports `VGAcur vgageodecur` named `geodehwgc`.
- Main routines: `geodeenable`, `geodelinear`, `geodecurenable`, `geodecurdisable`, `geodecurload`, and `geodecurmove`.

## Key Behavior

- Validates Geode PCI state, maps display/MMIO regions, and adds a named `geodevid` VGA segment for the video memory BAR.
- Uses `vgalinearpci()` for the framebuffer aperture.
- Writes cursor bitmap data and cursor position/control registers through Geode display-controller MMIO.
- Enables and disables the cursor by toggling display-controller cursor-enable bits.

## Dependencies And Assumptions

- Depends on Geode PCI BAR layout, including the video memory BAR used by `addvgaseg`.
- Assumes the MMIO register array is mapped in `scr->mmio`.

## Research Notes

- This module is small and hardware-specific; it has no drawing acceleration hook.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgageode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgahiqvideo.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgahiqvideo.c

## Role

VGA support module for Chips & Technologies HiQVideo adapters, including PCI validation, linear aperture setup, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgahiqvideodev` named `hiqvideo`.
- Exports `VGAcur vgahiqvideocur` named `hiqvideohwgc`.
- Main routines: `hiqvideoenable`, `hiqvideolinear`, `hiqvideocurenable`, `hiqvideocurdisable`, `hiqvideocurload`, and `hiqvideocurmove`.

## Key Behavior

- Validates PCI vendor `0x102C`, selects device-specific behavior, and configures extended registers for display memory size and aperture mode.
- Uses `vgalinearpci()` and publishes a `hiqvideoscreen` segment for the mapped framebuffer.
- Programs cursor memory address, cursor mode, colors, and X/Y position through extended index/data registers.
- Converts the Plan 9 cursor into the adapter’s cursor bitmap layout and stores it in display memory.

## Dependencies And Assumptions

- Depends on HiQVideo extended register ports (`Xrx`) and PCI BAR state.
- Assumes display memory size can be derived from adapter register bits and that cursor storage is in framebuffer memory.

## Research Notes

- No drawing acceleration hook is installed; the module handles setup and cursor functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgahiqvideo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgai81x.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgai81x.c

## Role

VGA support module for Intel i81x integrated graphics, focused on aperture sizing, display blanking, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgai81xdev` named `i81x`.
- Exports `VGAcur vgai81xcur` named `i81xhwgc`.
- Main routines: `i81xenable`, `i81xblank`, `i81xcurenable`, `i81xcurdisable`, `i81xcurload`, and `i81xcurmove`.

## Key Behavior

- Reads PCI configuration and graphics control bits to determine aperture/framebuffer size.
- Maps framebuffer memory with `vgalinearaddr`.
- Implements blanking by toggling display-control register bits.
- Stores the hardware cursor image in display memory and writes cursor position/base/control registers.
- Converts the Plan 9 cursor into the i81x cursor bitmap format and tracks hotspot offsets.

## Dependencies And Assumptions

- Depends on Intel i81x PCI BAR/control layout and MMIO registers mapped through `scr`.
- Assumes cursor storage is available in mapped video memory.

## Research Notes

- The exported `VGAdev` does not provide a linear callback because mapping is performed in `i81xenable`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgai81x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaigfx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaigfx.c

## Role

VGA support module for newer Intel integrated graphics (`igfx`), providing PCI framebuffer setup, blanking, and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaigfxdev` named `igfx`.
- Exports `VGAcur vgaigfxcur` named `igfxhwgc`.
- Main routines: `igfxenable`, `igfxdrawinit`, `igfxblank`, `igfxcurenable`, `igfxcurdisable`, `igfxcurload`, and `igfxcurmove`.

## Key Behavior

- Allocates cursor storage inside the framebuffer, maps the PCI linear aperture with `vgalinearpci()`, and installs `igfxblank` through `drawinit`.
- Selects cursor register blocks by PCI device generation, then writes cursor base, control, and position registers.
- Loads the Plan 9 cursor as ARGB-like 32-bit cursor pixels in framebuffer memory.
- Handles blanking by toggling generation-specific display-plane/control registers.

## Dependencies And Assumptions

- Depends on Intel integrated graphics PCI device IDs and generation-specific cursor/display register offsets.
- Assumes `scr->pci`, `scr->vaddr`, and `scr->storage` are valid after enable.

## Research Notes

- This module is more modern than `vgai81x.c` but still limited to framebuffer/cursor/blanking support, not 2D acceleration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaigfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgamach64xx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgamach64xx.c

## Role

VGA support module for ATI Mach64-family adapters, including PCI adapter identification, linear aperture setup, hardware cursor, display blanking, LCD blanking, and optional 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vgamach64xxdev` named `mach64xx`.
- Exports `VGAcur vgamach64xxcur` named `mach64xxhwgc`.
- Main routines: `mach64xxenable`, `mach64xxlinear`, `mach64xxdrawinit`, `mach64blank`, `mach64lcdblank`, cursor routines, `mach64hwfill`, and `mach64hwscroll`.

## Key Behavior

- Validates ATI PCI vendor `0x1002`, matches a table of Mach64 device IDs/types, records revision capability, and maps PCI linear framebuffer with `vgalinearpci()`.
- Defines extensive Mach64 register constants and helpers for MMIO/IO register access plus LCD register access.
- Hardware cursor logic stores cursor image data in display memory, programs cursor offset/color/position, and handles partial offscreen movement.
- Initializes the 2D engine by resetting it, setting pitch/offset, data path, scissor, pixel depth, and default mix/ROP state.
- `mach64hwfill()` accelerates solid rectangle fills; `mach64hwscroll()` accelerates screen-to-screen rectangle copies with direction handling.
- Installs acceleration hooks only for supported formats/depths and sets blanking hooks for CRT/LCD variants.

## Dependencies And Assumptions

- Depends on ATI Mach64 PCI IDs, MMIO register layout, and Plan 9 `VGAscr` acceleration callbacks.
- Rejects unsupported pixel formats through the shared `Eunsupportedformat` error string.
- FIFO/idle wait loops assume hardware eventually drains; timeouts are limited but still hardware-sensitive.

## Research Notes

- This is one of the richer VGA files in the group because it includes both cursor and 2D acceleration.
- LCD blanking support is separate from CRT blanking and uses Mach64 LCD-indexed registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgamach64xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgamga2164w.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgamga2164w.c

## Role

VGA support module for Matrox MGA 2064/2164-class adapters, with framebuffer aperture setup and TVP3026 RAMDAC hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgamga2164wdev` named `mga2164w`.
- Exports `VGAcur vgamga2164wcur` named `mga2164whwgc`.
- Main routines: `mga2164wenable`, `tvp3026enable`, `tvp3026disable`, `tvp3026load`, and `tvp3026move`.

## Key Behavior

- Validates Matrox PCI vendor, distinguishes MGA2064 from later devices, and maps the appropriate framebuffer BAR with `vgalinearaddr`.
- Uses TVP3026 DAC cursor registers for cursor enable, disable, load, and move.
- Loads a 64x64 cursor image into the RAMDAC cursor RAM and programs cursor colors/hotspot bias.
- Handles cursor positioning with negative-coordinate correction.

## Dependencies And Assumptions

- Depends on Matrox PCI device IDs and TVP3026 RAMDAC indexed register behavior.
- Assumes either an 8 MiB or 16 MiB framebuffer aperture depending on device class.

## Research Notes

- The file is a predecessor to the richer MGA4xx module; it does not install acceleration hooks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgamga2164w.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgamga4xx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgamga4xx.c

## Role

VGA support module for Matrox MGA G200/G400/G450/G550-style adapters, including PCI aperture setup, DAC cursor support, blanking, and 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vgamga4xxdev` named `mga4xx`.
- Exports `VGAcur vgamga4xxcur` named `mga4xxhwgc`.
- Main routines: `mga4xxenable`, `mga4xxdrawinit`, `mga4xxblank`, `mga4xxfill`, `mga4xxscroll`, and `dac4xx*` cursor routines.

## Key Behavior

- Uses PCI BAR0 for framebuffer mapping, with larger size for MGA4xx/MGA550 devices.
- Maps MMIO, exposes Matrox register helpers, and programs extended CRTC/DAC cursor registers.
- Loads hardware cursor data into framebuffer memory, sets cursor base address, colors, and X/Y position.
- Implements blanking by manipulating sequencer/CRTC-style control bits.
- Initializes the 2D drawing engine and installs solid fill and screen scroll callbacks.
- `mga4xxfill()` programs drawing registers for rectangle fill; `mga4xxscroll()` performs bitblt copies with direction and pitch handling.

## Dependencies And Assumptions

- Depends on Matrox PCI IDs, BAR layout, MMIO register definitions, and supported framebuffer depths.
- Acceleration setup assumes a linear framebuffer and valid `scr->mmio`.

## Research Notes

- This file is a representative Plan 9 VGA acceleration module: driver setup ultimately installs function pointers into `VGAscr`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgamga4xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vganeomagic.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vganeomagic.c

## Role

VGA support module for NeoMagic laptop graphics adapters, including PCI device matching, cursor MMIO setup, framebuffer mapping, and 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vganeomagicdev` named `neomagic`.
- Exports `VGAcur vganeomagiccur` named `neomagichwgc`.
- Main routines: `neomagicenable`, `neomagicdrawinit`, `neomagiccurenable`, `neomagiccurdisable`, `neomagiccurload`, `neomagiccurmove`, `neomagichwfill`, and `neomagichwscroll`.

## Key Behavior

- Validates NeoMagic PCI vendor `0x10C8`, switches on supported device IDs, determines MMIO BAR, cursor-register offset, and video memory size.
- Uses the top of video memory for two cursor images and maps the PCI framebuffer through `vgalinearpci()`.
- Represents cursor registers with `CursorNM`, writes cursor color, address, enable, and position fields, and handles offscreen cursor adjustment.
- Defines NeoMagic blitter registers and flags, waits for FIFO/idle, and accelerates solid fills and screen-to-screen scrolls.
- `neomagicdrawinit()` maps MMIO/register space and installs fill/scroll callbacks for supported modes.

## Dependencies And Assumptions

- Depends on NeoMagic device-specific BAR and cursor offset choices.
- Acceleration assumes MMIO registers are mapped and the selected depth is supported by the blitter path.

## Research Notes

- The file reserves two cursor images so partial offscreen cursor moves can rewrite a shifted cursor without corrupting the normal image.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vganeomagic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vganvidia.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vganvidia.c

## Role

VGA support module for NVIDIA adapters, including framebuffer/MMIO setup, hardware cursor support, DMA-assisted graphics engine setup, blanking, and 2D fill/scroll acceleration.

## Main Interfaces

- Exports `VGAdev vganvidiadev` named `nvidia`.
- Exports `VGAcur vganvidiacur` named `nvidiahwgc`.
- Main routines: `nvidiaenable`, `nvidialinear`, `nvidiadrawinit`, `nvidiablank`, cursor routines, `nvidiahwfill`, `nvidiahwscroll`, and DMA helpers.

## Key Behavior

- Maps NVIDIA MMIO and framebuffer regions from PCI BARs, records device ID, and publishes named `nvidiammio` and `nvidiascreen` segments.
- Determines video memory size from PCI/configuration state and maps linear framebuffer access.
- Stores hardware cursor data in framebuffer memory, writes cursor position/address/control registers, and handles offscreen cursor positioning.
- Sets up a DMA push buffer/ring for graphics commands, including put/get pointers and kickoff/wait helpers.
- Resets/initializes selected graphics objects and methods, then uses them for accelerated rectangle fill and screen scroll.
- Installs blanking, fill, and scroll callbacks from `nvidiadrawinit()`.

## Dependencies And Assumptions

- Depends on NVIDIA-specific MMIO, PFIFO/PGRAPH/DMA register behavior and PCI BAR layout.
- Several helper routines are exported without `static`, suggesting coupling with local debugging or related driver code.
- DMA initialization can fail if the push buffer cannot be mapped.

## Research Notes

- The file carries an NVIDIA license header and contains more vendor-specific engine setup than most legacy VGA modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vganvidia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaradeon.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaradeon.c

## Role

VGA support module for ATI Radeon adapters, covering PCI/MMIO setup, hardware cursor support, blanking, optional 2D acceleration, optional overlay hooks, and framebuffer flush.

## Main Interfaces

- Exports `VGAdev vgaradeondev` named `radeon`.
- Exports `VGAcur vgaradeoncur` named `radeonhwgc`.
- Main routines: `radeonenable`, `radeonlinear`, `radeondrawinit`, `radeonblank`, cursor routines, `radeonfill`, `radeonscroll`, `radeonovlctl`, `radeonovlwrite`, and `radeonflush`.

## Key Behavior

- Includes Radeon register definitions from `/sys/src/cmd/aux/vga/radeon.h`.
- Maps Radeon PCI framebuffer/MMIO resources, records device ID, and uses `vgalinearpci()` for linear framebuffer access.
- Provides register helpers for MMIO and PLL indexed access.
- Loads a hardware cursor image in display memory, sets cursor colors, address, enable state, and position.
- Implements blanking by updating CRTC/display control registers.
- When `HW_ACCEL` is enabled at compile time, initializes DP/GUI master control, waits for FIFO/idle, accelerates fills and scrolls, and exposes overlay control/write/flush hooks in `VGAdev`.

## Dependencies And Assumptions

- Depends on ATI Radeon PCI state, MMIO register layout, and the external Radeon header.
- Acceleration and overlay hooks are compile-time gated by `HW_ACCEL`.
- Requires correct cache/flushing behavior for framebuffer writes and overlay updates.

## Research Notes

- This is a compact but broad Radeon module: cursor, blanking, acceleration, overlay, and flush support all live in one file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgaradeon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgargb524.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgargb524.c

## Role

Hardware cursor support for IBM RGB524-compatible RAMDACs.

## Main Interfaces

- Exports `VGAcur vgargb524cur` named `rgb524hwgc`.
- Main routines: `rgb524enable`, `rgb524disable`, `rgb524load`, `rgb524move`, and indexed DAC helpers.

## Key Behavior

- Selects RAMDAC register banks and indexed cursor registers through RS2/index/data access.
- Programs cursor mode, cursor control, color registers, and cursor hotpoint bias.
- Loads the Plan 9 cursor into the RGB524 64x64 cursor RAM layout.
- Moves the cursor by writing indexed X/Y position registers with offscreen/hotspot correction.

## Dependencies And Assumptions

- Depends on IBM RGB524 RAMDAC register semantics and VGA DAC I/O helpers.
- Exports only a cursor driver, intended to be combined with a separate chipset `VGAdev`.

## Research Notes

- Like `vgabt485.c`, this file is RAMDAC-specific rather than PCI adapter-specific.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgargb524.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgas3.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgas3.c

## Role

VGA support module for S3 adapters, including bank switching, linear aperture setup, hardware cursor support, blanking, ViRGE acceleration, and delegation to the Savage acceleration module.

## Main Interfaces

- Exports `VGAdev vgas3dev` named `s3`.
- Exports `VGAcur vgas3cur` named `s3hwgc`.
- Main routines: `s3page`, `s3linear`, `s3enable`, `s3disable`, `s3load`, `s3move`, `s3drawinit`, `s3blank`, `hwfill`, and `hwscroll`.

## Key Behavior

- Validates S3 PCI vendor `0x5333` for linear setup and uses `vgalinearpci()` for PCI framebuffer mapping.
- Implements bank switching through S3 CRT registers, with different bit layouts for older chips and higher-depth modes.
- Loads a Microsoft-Windows-format hardware cursor image into display memory and handles offscreen positioning with cursor offsets.
- Works around hardware timing by avoiding cursor toggles during selected vertical/horizontal blank intervals.
- Provides FIFO/idle wait helpers for the S3 graphics engine and optional ViRGE solid fill/screen scroll acceleration.
- `s3drawinit()` reads S3 chip ID registers, installs blanking, enables ViRGE acceleration for known chips, and calls external `savageinit()` for Savage/ProSavage/SuperSavage IDs.

## Dependencies And Assumptions

- Depends on S3 extended VGA registers, PCI BAR layout, and chip IDs shared with `vgasavage.c`.
- Some acceleration paths are deliberately disabled for unknown ViRGE variants because FIFO depth is unknown.

## Research Notes

- This file is both an S3 driver and the dispatch point into `vgasavage.c` for newer S3-derived chips.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgas3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgasavage.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgasavage.c

## Role

S3 Savage/ProSavage acceleration and blanking helper used by `vgas3.c`. It installs drawing callbacks for supported Savage-family chip IDs.

## Main Interfaces

- Exports `savageinit(VGAscr *scr)` for use by `s3drawinit()`.
- Main internal routines: `savagewaitidle`, `savagefill`, `savagescroll`, and `savageblank`.

## Key Behavior

- Defines Savage and SuperSavage register constants, chip IDs, command bits, and a FIFO-depth table for supported adapters.
- `savageinit()` accepts known Savage4, ProSavage, SavageIX/MX, and SuperSavage IDs, sets up MMIO/register pointers, configures pitch and bitmap descriptor state, and installs acceleration hooks.
- `savagewaitidle()` waits for engine idle using chip-specific FIFO/status behavior.
- `savagefill()` accelerates solid rectangle fill by programming foreground color, clipping, destination, dimensions, and command registers.
- `savagescroll()` accelerates screen-to-screen copies with direction handling for overlapping source/destination rectangles.
- `savageblank()` controls display blanking through sequencer/CRTC register state.

## Dependencies And Assumptions

- Depends on `vgas3.c` to identify the chip and provide `scr->id`, framebuffer, and MMIO mapping.
- Comments warn that new chip IDs must also update `savagewaitidle`, because FIFO/status behavior is chip-specific.

## Research Notes

- This file intentionally has no `VGAdev` export; it is an extension module invoked by the S3 driver.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgasavage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgasoft.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/vgasoft.c

## Role

Software cursor fallback for the Plan 9 VGA layer.

## Main Interfaces

- Exports `VGAcur vgasoftcur` named `soft`.
- Main routines: `swenable`, `swdisable`, `swload`, and `swmove`.

## Key Behavior

- `swenable()` marks the screen as using a software cursor and loads the default cursor.
- `swdisable()` clears software cursor state.
- `swload()` copies cursor data into `scr->Cursor`.
- `swmove()` updates `scr->pos`.

## Dependencies And Assumptions

- Depends only on generic `VGAscr` cursor fields and the global default `cursor`.
- Actual drawing/erasing of the software cursor is handled elsewhere in the screen layer.

## Research Notes

- This tiny module provides a universal fallback when no chipset hardware cursor is selected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/vgasoft.c -->