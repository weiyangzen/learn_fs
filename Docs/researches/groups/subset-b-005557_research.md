# Research: subset-b-005557

Grouped research for framebuffer-related sources under `sources/distributed-fs/ceph-client/drivers/video/fbdev/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/au1200fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/au1200fb.c

## Purpose
`au1200fb.c` is the platform fbdev driver for the AMD/Alchemy Au1200 LCD controller. It exposes up to four LCD windows/planes as separate framebuffer devices, allocates DMA-coherent backing memory per plane, programs panel timings, and provides a legacy private ioctl for changing screen/window/panel registers at runtime.

## Important APIs, Types, and Functions
Key local types are `struct au1200fb_device`, `struct window_settings`, `struct panel_settings`, and the ioctl payload structs `au1200_lcd_global_regs_t`, `au1200_lcd_window_regs_t`, and `au1200_lcd_iodata_t`. The main fbdev operations are `au1200fb_fb_check_var()`, `au1200fb_fb_set_par()`, `au1200fb_fb_setcolreg()`, `au1200fb_fb_blank()`, `au1200fb_fb_mmap()`, and `au1200fb_ioctl()`. Hardware programming is centered on `au1200_setpanel()`, `au1200_setmode()`, `au1200_setlocation()`, `set_global()`, and `set_window()`.

## Control Flow
`au1200fb_drv_probe()` reads platform data, parses `au1200fb` boot/module options, chooses a panel and window configuration, allocates one `fb_info` plus DMA framebuffer per active plane, initializes fb metadata, registers each framebuffer, installs the shared LCD interrupt, and finally calls `au1200_setpanel()` to start output. Mode setting recalculates fb metadata and writes window control registers. Blank, suspend, and remove paths call `au1200_setpanel(NULL, pd)` to shut down the controller before cleanup or power state transitions.

## State and Persistence
Driver state is mostly global: `_au1200fb_infos`, `lcd`, `device_count`, `window_index`, `panel_index`, `win`, `panel`, `noblanking`, and `nohwcursor`. Per-plane persistent runtime state lives in `struct au1200fb_device` and in the shared `windows[]` geometry table, which is mutated when defaults are expanded to panel size and when `au1200_setlocation()` records positions. The private ioctl directly persists changes into MMIO registers and, for panel selection, updates `panel_index`.

## Dependencies and Integration Points
The driver depends on fbdev core, platform-device probing, Au1x00 platform data from `<asm/mach-au1x00/au1200fb.h>`, the Au1200 register layout from `au1200fb.h`, DMA coherent allocation/mmap helpers, the common clock framework for `lcd_intclk`, and board callbacks `panel_init`, `panel_shutdown`, and `panel_index`. It integrates with userspace through `/dev/fb*`, fbdev colormaps, mmap, and the private `AU1200_LCD_FB_IOCTL`.

## Risks and Edge Cases
The file is legacy-style and has broad global mutable state, so multiple devices would be unsafe. Several comments mark incomplete behavior: off-screen clipping, virtual resolution, STN/mono formats, hardware cursor, panel-change validation, and clock assumptions. `au1200fb_fb_check_var()` chooses RGB bitfields from `win->w[0]` even for other planes, which can mismatch plane formats. The ioctl allows raw register-like changes with minimal validation. Probe failure cleanup assumes partially allocated `fb_info` objects can be unregistered, which is typical but worth checking if refactored.

## Test Signals
Useful signals are successful registration of the expected number of `AU1200` framebuffers, correct panel boot output, mmap access to DMA memory, colormap/pseudo-palette behavior for 16/32 bpp, private ioctl round trips for screen/window/panel state, suspend/resume restoring panel and plane registers, and no IRQ storms after the handler clears `intstatus`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/au1200fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/au1200fb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/au1200fb.h

## Purpose
`au1200fb.h` defines the Au1200 LCD controller MMIO register layout and bit masks used by `au1200fb.c`. It is a hardware contract header rather than a standalone module.

## Important APIs, Types, and Functions
The central type is `struct au1200_lcd`, which maps the controller register block at `AU1200_LCD_ADDR`, including global screen/timing/PWM/FIFO registers, four `window[]` register sets, palette RAM, and cursor pattern RAM. The header provides masks and value-building macros for screen size/type, background color, window enable, color key, window control registers, buffer control, interrupts, horizontal/vertical timing, clock control, PWM, hardware cursor, FIFO, and output mask fields.

## Control Flow
There is no executable control flow. Runtime code casts `AU1200_LCD_ADDR` to `struct au1200_lcd *` and uses the masks to read-modify-write registers. The `_N()` macros encode hardware fields that store dimensions or counters as shifted values, often with a hardware `N - 1` convention.

## State and Persistence
The structure mirrors volatile device state. Writes persist only in the LCD controller until reset or power loss. Palette and cursor arrays are also MMIO-backed hardware state. The `uint8` and `uint32` aliases are local legacy typedef-style macros.

## Dependencies and Integration Points
This header is tightly coupled to Au1200 LCD silicon and to the fbdev driver that programs it. It assumes the platform's physical/uncached address mapping convention for `0xB5000000`. It also relies on consumers observing MMIO ordering with barriers; the header itself does not provide accessors.

## Risks and Edge Cases
Direct volatile struct MMIO can be brittle across compiler, endian, or architecture changes compared with `readl()`/`writel()`. Several bit masks encode overlapping fields and must be used carefully in read-modify-write paths. Macros such as FIFO interrupt flags repeat shift positions for different FIFOs, so consumers should verify against the hardware manual before extending.

## Test Signals
Compile coverage on Au1200 targets is the primary signal. Hardware tests should confirm screen dimensions, timing, clock, PWM, palette, window size/position, and interrupt bits are programmed as expected by observing display output and register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/au1200fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/broadsheetfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/broadsheetfb.c

## Purpose
`broadsheetfb.c` is an architecture-independent fbdev driver for E-Ink Broadsheet display controllers. It owns the generic controller protocol, framebuffer, deferred I/O update policy, panel timing table, and waveform-flash sysfs path while delegating physical bus operations to a board-specific `struct broadsheet_board`.

## Important APIs, Types, and Functions
`struct panel_info` records width, height, display timing, LUT format, and pixel clock values. Low-level helpers include GPIO and MMIO command/data variants: `broadsheet_send_command()`, `broadsheet_send_cmdargs()`, `broadsheet_burst_write()`, `broadsheet_write_reg()`, and `broadsheet_read_reg()`. Waveform SPI flash support is implemented by `broadsheet_setup_for_wfm_write()`, `broadsheet_write_spiflash()`, and `broadsheet_loadstore_waveform()`. Display updates use `broadsheet_init_display()`, `broadsheetfb_dpy_update()`, `broadsheetfb_dpy_update_pages()`, and deferred I/O callbacks.

## Control Flow
`broadsheetfb_probe()` obtains board callbacks, selects a panel index from `board->get_panel_type()`, allocates a vmalloc framebuffer, sets 8-bit grayscale fb metadata, initializes deferred I/O, allocates a 16-entry grayscale colormap, asks the board to set up interrupts and controller resources, initializes/identifies the controller, registers the framebuffer, and creates the write-only `loadstore_waveform` sysfs file. Writes to the framebuffer are collected by fbdefio and later converted into full or partial Broadsheet image load/update command sequences.

## State and Persistence
Persistent runtime state lives in `struct broadsheetfb_par`: board callbacks, `fb_info`, panel index, I/O lock, waitqueue, and function pointers for register access. Framebuffer contents are system memory and are pushed explicitly to the E-Ink controller. Waveform flashing persists firmware data into controller-attached SPI flash at offset `0x886`; this is the only durable hardware state modified by the driver.

## Dependencies and Integration Points
The driver depends on `video/broadsheetfb.h` for command constants, board callback types, and `struct broadsheetfb_par`. It integrates with platform-device binding named `broadsheetfb`, fbdev deferred sysmem operations, firmware loading of `broadsheet.wbf`, board-specific IRQ/setup/cleanup hooks, and either GPIO-style or MMIO-style board data transfers.

## Risks and Edge Cases
The waveform rewrite path is sensitive: sector head/tail preservation and offset math must be correct to avoid corrupting flash. Some flash reads in `broadsheet_spiflash_rewrite_sector()` use absolute-looking lengths/offsets that deserve hardware review. Deferred page coalescing rounds y coordinates to multiples of four and can over-update. Display updates hold `io_lock` around long waits, so responsiveness depends on controller latency. Partial/full updates assume 8-bit grayscale packed as two 4-bit pixels after nibble shifting.

## Test Signals
Signals include successful probe on GPIO and MMIO board implementations, correct panel selection for 6/37/97 panel types, visible initial full-screen update, deferred I/O producing bounded partial updates, firmware size validation for `broadsheet.wbf`, SPI flash write/verify on both supported flash signatures, and remove-path cleanup of fbdefio, sysfs, board resources, and module references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/broadsheetfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/bt431.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/bt431.h

## Purpose
`bt431.h` provides inline register helpers for the Brooktree Bt431 cursor generator, notably for DECstation framebuffer hardware that uses one or two aligned Bt431 chips.

## Important APIs, Types, and Functions
`struct bt431_regs` maps the 32-bit-aligned indirect register and cursor-map ports. `bt431_select_reg()`, `bt431_read_reg()`, `bt431_write_reg()`, `bt431_read_cmap()`, and `bt431_write_cmap()` perform indirect access. Higher-level helpers are `bt431_enable_cursor()`, `bt431_erase_cursor()`, `bt431_position_cursor()`, `bt431_set_cursor()`, and `bt431_init_cursor()`. Command and cursor RAM constants define the hardware address space and cursor modes.

## Control Flow
All operations are inline MMIO sequences. Register access writes low and high address bytes, then reads or writes the autoincrementing register/cursor-map port. Cursor upload iterates the fixed 64 by 64 cursor RAM, combines mask/data according to the requested ROP, and writes zero outside the requested cursor dimensions.

## State and Persistence
State is hardware-resident: indirect register address, command register, cursor position, window registers, and 512 words of cursor RAM. The helpers do not keep a software shadow, so callers must serialize access if multiple paths can manipulate the same chip.

## Dependencies and Integration Points
The header depends on Linux integer types, barrier primitives, `DIV_ROUND_UP()`, and ROP constants. It is intended to be included by framebuffer drivers that own the mapped Bt431 MMIO region and provide locking at a higher level.

## Risks and Edge Cases
The hardware requires 16-bit replicated byte writes and the comments note that compiler-split byte writes would be wrong, so refactoring must preserve helper variables and volatile access. `bt431_position_cursor()` embeds magic timing offsets from MACH sources; different boards may need different constants. Cursor dimensions larger than 64 or malformed mask/data buffers are not validated.

## Test Signals
Tests should exercise register read/write, cursor enable/erase, cursor position alignment, XOR and normal cursor uploads, and operation on both single and paired Bt431 configurations under caller-provided locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/bt431.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/bt455.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/bt455.h

## Purpose
`bt455.h` provides inline helpers for the Brooktree Bt455 grayscale RAMDAC/color-map device. It is a small hardware-access header used by framebuffer drivers that need byte-wide, 32-bit-aligned Bt455 palette and overlay access.

## Important APIs, Types, and Functions
`struct bt455_regs` maps the cmap address, cmap data, clear/reset, and overlay ports. `bt455_select_reg()` chooses a 4-bit color-map entry, `bt455_reset_reg()` resets overlay addressing, `bt455_read_cmap_next()` and `bt455_write_cmap_next()` perform the multi-cycle grayscale access, and entry wrappers provide indexed color-map and overlay writes.

## Control Flow
The helpers are straight-line MMIO sequences with memory barriers around device cycles. Reads discard dummy cycles around the data nibble; writes send a zero, the low 4-bit grayscale value, then another zero, matching the Bt455 protocol.

## State and Persistence
State is entirely in the RAMDAC: selected color-map index, 4-bit grayscale entries, and overlay state. No software shadow is maintained.

## Dependencies and Integration Points
The header depends on Linux types and barrier primitives. It is designed for inclusion by low-level framebuffer drivers that map the Bt455 registers and provide external synchronization.

## Risks and Edge Cases
Only the low nibble of grayscale values is preserved. Incorrect barrier removal or conversion to normal memory writes could break hardware sequencing. There is no bounds check on the register index beyond the hardware-masked low 4 bits.

## Test Signals
Useful checks are palette readback/writeback for all 16 entries, overlay color updates, correct grayscale ramp display, and absence of bus faults on the target aligned register mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/bt455.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/bw2.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/bw2.c

## Purpose
`bw2.c` is the Open Firmware/platform fbdev driver for Sun BWTWO monochrome framebuffers. It maps the one-bit framebuffer and BWTWO control registers, initializes monitor timing when firmware did not provide dimensions, and implements blanking plus SBUS mmap/ioctl compatibility.

## Important APIs, Types, and Functions
Key types are `struct bw2_regs`, `struct bt_regs`, and `struct bw2_par`. fbdev operations are supplied through `bw2_ops`, especially `bw2_blank()`, `bw2_sbusfb_mmap()`, and `bw2_sbusfb_ioctl()`. `bw2_do_default_mode()` chooses timing register tables based on status register monitor/type bits, and `bw2_init_fix()` fills fixed fb metadata.

## Control Flow
`bw2_probe()` allocates `fb_info`, fills var from OF properties, maps registers at `BWTWO_REGISTER_OFFSET`, optionally programs default timing, maps framebuffer RAM, unblanks video, initializes fix info, registers the framebuffer, and stores driver data. Removal unregisters and unmaps resources. Module init skips registration if `bw2fb` options disable the driver.

## State and Persistence
Per-device state includes a spinlock, mapped register pointer, blanked flag, and SBUS IO-space identifier. Hardware state includes timing registers, control video enable bit, and framebuffer RAM. No colormap is involved because the device is mono.

## Dependencies and Integration Points
The file depends on platform OF resources, `sbuslib.h` helpers, `asm/fbio.h` compatibility constants, and `sbus_readb()/sbus_writeb()` accessors. It presents Sun fbio-compatible mmap/ioctl behavior through `sbusfb_mmap_helper()` and `sbusfb_ioctl_helper()`.

## Risks and Edge Cases
Default timing depends on status bits and hard-coded tables; unknown monitor IDs fail probe. `BWTWO_SR_ID_NOCONN` returns success without programming timing, leaving behavior to firmware. The driver assumes resource 0 contains both framebuffer and registers at fixed offsets.

## Test Signals
Expected signals are successful OF match on `bwtwo`, correct mono visual and line length, blank/unblank toggling the video bit, mmap of the one-bit framebuffer through SBUS offsets, fbio type `FBTYPE_SUN2BW`, and correct default timing on ECL, analog, multisync, and 1600x1280 displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/bw2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p.h

## Purpose
`c2p.h` declares the public chunky-to-planar conversion entry points used by framebuffer drivers that need to copy 8-bit chunky image data into planar or interleaved-planar framebuffers.

## Important APIs, Types, and Functions
The exported declarations are `c2p_planar()` and `c2p_iplan2()`. Both accept destination/source pointers, destination x/y offsets, width/height, line strides, and bits per pixel. `c2p_planar()` also receives `dst_nextplane`; `c2p_iplan2()` is specialized for two-byte interleave.

## Control Flow
There is no implementation here. Consumers include the header and link against `c2p_planar.c` or `c2p_iplan2.c`, where the conversion loops split rectangles into aligned full and masked partial blocks.

## State and Persistence
The functions declared here are stateless. They transform caller-provided source memory into caller-provided framebuffer memory and maintain no global data.

## Dependencies and Integration Points
The header depends only on `<linux/types.h>`. It forms the source-level contract between generic fbdev drawing paths and the C2P implementation modules.

## Risks and Edge Cases
The API trusts callers to provide valid dimensions, strides, bpp, and addressable memory. Misstated bpp or stride can corrupt framebuffer memory because the implementations do no broad validation.

## Test Signals
Build/link tests should verify both symbols resolve. Functional tests should compare known chunky input patterns against expected planar/interleaved output for aligned rectangles and unaligned left/right edges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_core.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_core.h

## Purpose
`c2p_core.h` contains shared bit-transpose primitives for fast chunky-to-planar conversion. It is intended to be included by concrete conversion implementations and assumes big-endian bit ordering.

## Important APIs, Types, and Functions
Internal helpers include `_transp()`, `get_mask()`, `transp8()`, `transp4()`, `transp4x()`, and `comp()`. The transpose helpers operate on arrays of 32-bit words and are parameterized by block dimensions. `comp()` merges a newly converted partial word with an existing framebuffer word using a mask.

## Control Flow
The concrete converters call a series of transpose stages that exchange bit groups between words. `get_mask()` selects canonical bit masks for 1, 2, 4, 8, or 16-bit groups, while invalid compile-time constants trigger `BUILD_BUG()`.

## State and Persistence
There is no persistent state. All operations mutate caller-supplied temporary arrays during a conversion block.

## Dependencies and Integration Points
The header depends on `linux/build_bug.h` and Linux integer types through includers. It is included by `c2p_planar.c` and `c2p_iplan2.c`, and its big-endian assumption aligns with those files' use of unaligned big-endian loads/stores.

## Risks and Edge Cases
The transpose sequences are subtle and rely on exact masks, word order, and endian semantics. Porting to little-endian output or changing store order requires golden-vector tests. `BUILD_BUG()` only protects constant invalid cases; dynamic misuse could be harder to diagnose if wrappers are changed.

## Test Signals
Golden output vectors for 1, 2, 4, and 8 bpp planar formats, plus masked partial-block cases, are the strongest signals. Compiler coverage should include optimization levels that inline these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_iplan2.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_iplan2.c

## Purpose
`c2p_iplan2.c` implements and exports `c2p_iplan2()`, converting 8-bit chunky pixels into interleaved planar framebuffer memory with two bytes of interleave. It supports 2, 4, or 8 planar bits per pixel.

## Important APIs, Types, and Functions
`c2p_16x8()` performs the core conversion of 16 chunky pixels in four 32-bit words. `perm_c2p_16x8[]` maps converted word order to output order. `store_iplan2()` writes full converted blocks; `store_iplan2_masked()` preserves untouched edge bits with `comp()`. `c2p_iplan2()` is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
The exported function computes the destination byte offset from `dy`, `dst_nextline`, and the 16-pixel-aligned part of `dx`. Each scanline is split into a possible single masked block, or leading masked block, full 16-pixel blocks, and trailing masked block. Temporary `pixels[]` are filled from source, transposed, and written as big-endian 32-bit output words.

## State and Persistence
The conversion is stateless except for modifying destination framebuffer memory. Partial writes preserve existing destination bits through read-modify-write masks, so destination contents matter at unaligned edges.

## Dependencies and Integration Points
The file depends on `c2p.h`, `c2p_core.h`, `linux/unaligned.h`, export/module infrastructure, and `memcpy()/memset()`. Drivers with interleaved planar formats call it directly or via generic helper paths.

## Risks and Edge Cases
Input arguments are trusted. Invalid `bpp`, strides, or dimensions can overrun memory. Edge masks depend on `dx % 16` and `(dst_idx + width) % 16`; zero-width or exact-boundary behavior should be guarded by callers or tests. The output assumes big-endian planar bit order.

## Test Signals
Compare output against golden interleaved-planar buffers for 2, 4, and 8 bpp, including `dx` offsets from 0 to 15, widths smaller than one block, exact 16-pixel multiples, and multi-line stride padding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_iplan2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_planar.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_planar.c

## Purpose
`c2p_planar.c` implements and exports `c2p_planar()`, converting 8-bit chunky pixels into standard planar framebuffer memory with separate planes.

## Important APIs, Types, and Functions
`c2p_32x8()` converts 32 chunky pixels stored in eight 32-bit words. `perm_c2p_32x8[]` defines the output plane order after transposition. `store_planar()` writes full blocks to successive planes using `dst_nextplane`, and `store_planar_masked()` merges partial edge blocks. `c2p_planar()` is GPL-exported.

## Control Flow
The function aligns `dx` to a 32-pixel destination word, computes leading and trailing masks, and processes each line as a single masked block or a leading edge, full 32-pixel blocks, and trailing edge. Each block is copied into a temporary union, transposed through `c2p_32x8()`, and stored to each requested plane.

## State and Persistence
No driver state is kept. The function writes destination framebuffer memory and performs read-modify-write for masked first/last words to preserve pixels outside the requested rectangle.

## Dependencies and Integration Points
Dependencies are `c2p.h`, `c2p_core.h`, unaligned big-endian access helpers, and module export support. It integrates with planar fbdev drawing paths where chunky software images must be converted for legacy planar framebuffers.

## Risks and Edge Cases
The implementation assumes valid caller-provided bpp in the 1-to-8 range, addressable plane memory, and compatible endian output. Invalid strides or `dst_nextplane` can corrupt unrelated planes. Boundary mask behavior should be regression-tested for `dx + width` exactly divisible by 32.

## Test Signals
Golden-vector tests should cover 1 through 8 bpp, every unaligned `dx % 32`, exact and non-exact block widths, multiple scanlines with source/destination stride padding, and preservation of untouched bits at left and right edges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/c2p_planar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.c

## Purpose
`carminefb.c` is a PCI fbdev driver for Fujitsu Carmine devices. It initializes the GPU/DRAM controller, maps register and display-memory BARs, and exposes up to two independent 32-bit truecolor framebuffers, one per display.

## Important APIs, Types, and Functions
Key types are `struct carmine_hw`, `struct carmine_resolution`, and `struct carmine_fb`. fbdev callbacks are `carmine_check_var()`, `carmine_set_par()`, and `carmine_setcolreg()`. Hardware setup is divided between `init_hardware()`, `carmine_init_display_param()`, and `set_display_parameters()`. PCI lifecycle functions are `carminefb_probe()`, `carminefb_remove()`, `carminefb_init()`, and `carminefb_cleanup()`.

## Control Flow
Module init rejects disabled modesetting or no selected display, then registers the PCI driver. Probe removes conflicting aperture drivers, enables the PCI device, reserves and maps config and memory BARs, caps the large memory BAR to the two-display framebuffer requirement, runs DRAM/display initialization, allocates display 0 and/or display 1 framebuffers, and stores `struct carmine_hw` as PCI driver data. Mode setting validates against two built-in modes and writes display timing/layer registers when the mode changes.

## State and Persistence
Per-device state tracks mapped register memory, mapped screen memory, and up to two `fb_info` objects. Per-framebuffer state tracks display register base, screen offset, current/new mode, resolution table pointer, and pseudo-palette. Hardware state includes DRAM controller settings, display clock/output enable, layer origins, timing registers, and framebuffer memory contents.

## Dependencies and Integration Points
The driver depends on PCI, aperture conflict removal, fbdev IOMEM ops, `carminefb.h` DRAM defaults, and `carminefb_regs.h` offsets. Module parameters `fb_mode`, `fb_mode_str`, and `fb_displays` control initial mode/display selection. It binds Fujitsu vendor `0x10cf`, device `0x202b`.

## Risks and Edge Cases
Only 640x480 and 800x600 are supported. DRAM timing defaults are compile-time configuration dependent and board-sensitive. `carmine_setcolreg()` stores big-endian pseudo-palette entries, so endian behavior must match hardware and fbdev expectations. Probe uses global `carminefb_fix`, so concurrent devices would share mutable fix fields. Cleanup comments include a typo about display selection but logic chooses an existing fb for BAR release.

## Test Signals
Signals include correct PCI bind, BAR reservation/mapping, visible 32-bit output on selected displays, correct behavior for both module mode-selection paths, successful rejection of unsupported modes, pseudo-palette color correctness on big/little endian hosts, and clean remove after one-display and two-display configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.h

## Purpose
`carminefb.h` defines Carmine PCI BAR numbers, display-memory sizing, display-selection flags, and board-specific DRAM initialization constants consumed by `carminefb.c`.

## Important APIs, Types, and Functions
The file has no functions. Important constants are `CARMINE_MEMORY_BAR`, `CARMINE_CONFIG_BAR`, `MAX_DISPLAY`, `CARMINE_DISPLAY_MEM`, `CARMINE_TOTAL_DISPLAY_MEM`, `CARMINE_USE_DISPLAY0`, and `CARMINE_USE_DISPLAY1`. DRAM defaults are selected by `CONFIG_FB_CARMINE_DRAM_EVAL` or `CONFIG_CARMINE_DRAM_CUSTOM`.

## Control Flow
Compile-time configuration controls which DRAM timing macro set is visible. Runtime initialization in `init_hardware()` writes these constants to Carmine DCTL and CTL registers.

## State and Persistence
The header defines constants only. Runtime persistence is in hardware registers and display memory after the driver writes these values.

## Dependencies and Integration Points
It is included by the Carmine PCI fbdev driver and must be consistent with `carminefb_regs.h`. The memory sizing assumes two 800x600x32-bit framebuffers.

## Risks and Edge Cases
If neither DRAM configuration block is enabled, required `CARMINE_DFLT_*` macros are absent and the driver will not compile. The custom config symbol name differs from the eval symbol prefix, so Kconfig consistency is important. The fixed display-memory size constrains supported modes.

## Test Signals
Compile tests should cover each DRAM configuration. Hardware tests should verify DRAM init completes, framebuffer memory is stable, and both display-memory offsets are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb_regs.h

## Purpose
`carminefb_regs.h` defines Carmine register block offsets, display-layer offsets, bit masks, shifts, and default control values used to program display timing, layers, DRAM control, writeback, graphics interrupts, and clock/reset state.

## Important APIs, Types, and Functions
The header has no functions. Key groups include top-level block bases (`CARMINE_GRAPH_REG`, `CARMINE_DISP0_REG`, `CARMINE_DISP1_REG`, `CARMINE_WB_REG`, `CARMINE_DCTL_REG`, `CARMINE_CTL_REG`), display enable/mode bits (`CARMINE_DEN`, `CARMINE_L0E`, `CARMINE_EXT_CMODE_DIRECT24_RGBA`), timing shifts, layer origin/display/window registers, DCTL state masks, and control register offsets.

## Control Flow
No executable flow exists. `carminefb.c` composes register addresses as `mapped_base + block + offset` and writes values with `writel()`.

## State and Persistence
The constants describe hardware state layout. Values written through these offsets persist in Carmine hardware until reset, power loss, or driver teardown.

## Dependencies and Integration Points
This header is coupled directly to the Carmine register map and the sequences in `init_hardware()`, `carmine_init_display_param()`, and `set_display_parameters()`. It must also align with the display-memory layout in `carminefb.h`.

## Risks and Edge Cases
Register maps are dense and some layer 6/7 offsets live far from layers 0-5, so manual edits can easily introduce address mistakes. Bit shifts and masks need hardware-manual validation before adding modes or overlay support. Incorrect DCTL timing constants can prevent DRAM initialization.

## Test Signals
Compile coverage plus hardware register readback is important. Functional signals include display timing correctness, layer 0 enable, clock/reset behavior, successful DRAM state transition, and no unexpected graphics/VRAM interrupt mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cg14.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cg14.c

## Purpose
`cg14.c` is the Open Firmware/platform fbdev driver for Sun CGfourteen framebuffers. It supports pseudocolor operation, MDI compatibility ioctls, pixel-mode switching, color-map programming, panning reset behavior, and complex SBUS mmap views for framebuffer, CLUT, cursor, and planar/chunky regions.

## Important APIs, Types, and Functions
Important types are `struct cg14_regs`, `struct cg14_cursor`, `struct cg14_dac`, `struct cg14_xlut`, `struct cg14_clut`, and `struct cg14_par`. fbdev callbacks are `cg14_setcolreg()`, `cg14_pan_display()`, `cg14_sbusfb_mmap()`, and `cg14_sbusfb_ioctl()`. Helpers include `__cg14_reset()`, `cg14_init_fix()`, `cg14_unmap_regs()`, and static mmap table `__cg14_mmap_map`.

## Control Flow
`cg14_probe()` allocates `fb_info`, fills var info from OF, maps register, CLUT, cursor, and RAM resources, builds an adjusted mmap map depending on resource placement and 4MB/8MB VRAM size, initializes mode/ramsize, resets to 8-bit pixel mode, allocates and installs the colormap, registers the framebuffer, and stores device data. Ioctls handle MDI reset/config/pixel-mode locally and delegate other fbio commands to `sbusfb_ioctl_helper()`.

## State and Persistence
Per-device state stores lock, register mappings, blank flag, iospace, mmap map copy, current MDI mode, and RAM size. Hardware-persistent state includes MCR pixel mode, CLUT entries, cursor registers, VRAM contents, and mapped VBC/control registers. `cg14_pan_display()` uses panning as a hook to reset graphics mode.

## Dependencies and Integration Points
The driver depends on OF platform resources, `sbuslib.h`, Sun fbio/MDI constants, `copy_to_user()`/`get_user()`, and SBUS accessors. It exposes legacy mmap offsets such as `CG14_REGS`, `CG14_CLUT*`, `MDI_CURSOR_MAP`, and MDI planar/chunky maps.

## Risks and Edge Cases
Pixel-mode changes are accepted only for 8/16/32-bit MDI modes but fbdev var remains primarily pseudocolor 8-bit. Mmap map adjustment depends on relative resource starts and 8MB detection. Blank flag exists but no fb_blank callback is wired. Register definitions include many undocumented or partially understood areas.

## Test Signals
Signals include OF match on `cgfourteen`, correct 4MB/8MB mmap sizing, color-map writes visible on display, MDI_GET_CFGINFO and MDI_SET_PIXELMODE behavior, reset to 8-bit mode on pan/display switch, and successful mmap of all legacy regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cg14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cg3.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cg3.c

## Purpose
`cg3.c` is the Open Firmware/platform fbdev driver for Sun CGthree color framebuffers and cgRDI variants. It maps 8-bit framebuffer memory, manages the Brooktree-style DAC colormap, programs default timing tables when firmware lacks dimensions, and implements blanking plus SBUS compatibility mmap/ioctl paths.

## Important APIs, Types, and Functions
Key types are `struct cg3_regs`, `struct bt_regs`, `enum cg3_type`, and `struct cg3_par`. fbdev operations are `cg3_setcolreg()`, `cg3_blank()`, `cg3_sbusfb_mmap()`, and `cg3_sbusfb_ioctl()`. Initialization helpers include `cg3_rdi_maybe_fixup_var()`, `cg3_do_default_mode()`, and `cg3_init_fix()`.

## Control Flow
`cg3_probe()` allocates fb state, fills var from OF, detects cgRDI and optional `params`, computes linebytes and smem length, maps registers and RAM, unblanks, optionally programs default timing/DAC values, allocates and installs a 256-entry colormap, initializes fix info, registers the framebuffer, and stores driver data. Remove unregisters, frees cmap, unmaps, and releases fb state.

## State and Persistence
`struct cg3_par` stores a lock, register mapping, software colormap shadow, flags, and IO-space ID. Hardware state includes control video enable, timing registers, DAC control, DAC color map, and framebuffer contents. The software colormap shadow exists because hardware palette loads are grouped in an unusual 4-entry/3-word pattern.

## Dependencies and Integration Points
The driver depends on OF resources, SBUS helpers/accessors, `sbuslib.h`, Sun fbio type `FBTYPE_SUN3COLOR`, and fbdev colormap installation. It binds both `cgthree` and `cgRDI`.

## Risks and Edge Cases
Palette writes are nontrivial and depend on the shadow buffer staying coherent. Unknown status register IDs fail timing setup. cgRDI parameter parsing is permissive and only recognizes `WxH-` prefixes. The driver assumes fixed register/RAM offsets within resource 0.

## Test Signals
Signals include visible 8-bit pseudocolor output, correct colormap changes for arbitrary indices, blank/unblank toggling video, cgRDI resolution override from OF params, 66Hz/76Hz/RDI timing table selection, SBUS mmap at `CG3_MMAP_OFFSET`, and correct fbio type/size reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cg3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cg6.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cg6.c

## Purpose
`cg6.c` is the fbdev driver for Sun CGsix/GX/TGX accelerated 8-bit framebuffers. It maps the Brooktree DAC, FBC, TEC, THC, FHC, ROM/RAM regions, initializes the accelerator/display controller, provides hardware fill/copy/monochrome image operations, and exposes legacy SBUS mmap/ioctl compatibility.

## Important APIs, Types, and Functions
Core types include `struct cg6_tec`, `struct cg6_thc`, `struct cg6_fbc`, `struct bt_regs`, and `struct cg6_par`. fbdev callbacks include `cg6_setcolreg()`, `cg6_blank()`, `cg6_fillrect()`, `cg6_copyarea()`, `cg6_imageblit()`, `cg6_sync()`, and `cg6_pan_display()`. Initialization helpers are `cg6_bt_init()`, `cg6_chip_init()`, `cg6_init_fix()`, and `cg6_unmap_regs()`.

## Control Flow
`cg6_probe()` allocates fb state, fills OF var info, computes framebuffer size with optional double-buffer multiplier, maps all hardware blocks, sets acceleration flags and fbops, maps RAM, initializes DAC/FBC/TEC/THC state, unblanks video, allocates/sets colormap, registers the framebuffer, and stores driver data. Drawing operations lock, wait for FBC idle via `cg6_sync()`, program FBC registers, and trigger rectangle, blit, or font rendering.

## State and Persistence
Per-device state stores mapped hardware blocks, spinlock, blanked flag, and IO-space ID. Hardware state includes DAC palette, accelerator mode/clip/ALU registers, cursor position, timing/video bits, FHC revision/workaround settings, and VRAM. The driver hides the hardware cursor when switching out of graphics mode through pan-display handling.

## Dependencies and Integration Points
The file depends on OF platform resources, SBUS helpers, `sbuslib.h`, Sun fbio constants, generic `cfb_imageblit()` fallback for deep images, and fbdev hardware-acceleration flags. It binds `cgsix` and `cgthree+`.

## Risks and Edge Cases
Accelerator register programming is timing-sensitive; `cg6_sync()` has a finite polling limit but callers do not surface timeout details. Old FHC revisions require hardware workarounds. The monochrome imageblit path packs source bytes manually and must match font bit ordering. Double-buffer sizing multiplies smem length by four based on an OF property.

## Test Signals
Signals include correct GX/GX+/TGX/TGX+ identification, palette changes, blank/unblank video bit behavior, accelerated fill/copy/text rendering correctness, fallback for images with depth greater than one, mmap of all CG6 regions, no hangs in `cg6_sync()`, and correct remove cleanup of every mapped block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cg6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/chipsfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/chipsfb.c

## Purpose
`chipsfb.c` is a PCI fbdev driver for the Chips & Technologies 65550 framebuffer, historically used on PowerBook-class systems. It programs VGA-style indexed registers through fixed I/O ports, maps the framebuffer aperture, supports 800x600 at 8 or 16 bpp, and optionally coordinates with PowerMac backlight support and PCI suspend/resume.

## Important APIs, Types, and Functions
Register macros `write_xr/read_xr`, `write_fr/read_fr`, `write_cr/read_cr`, `write_gr/read_gr`, `write_sr/read_sr`, and `write_ar/read_ar` wrap port I/O. fbdev callbacks are `chipsfb_check_var()`, `chipsfb_set_par()`, `chipsfb_setcolreg()`, and `chipsfb_blank()`. Hardware tables use `struct chips_init_reg`, applied by `chips_hw_init()`. Lifecycle functions are `chipsfb_pci_init()`, `chipsfb_remove()`, suspend/resume hooks, `chips_init()`, and `chipsfb_exit()`.

## Control Flow
`chipsfb_pci_init()` removes conflicting aperture drivers, enables PCI, validates BAR0 memory, allocates `fb_info`, requests BAR0, enables memory and I/O in PCI command register, optionally turns on PMac backlight, maps the aperture, initializes fb metadata and hardware registers, and registers the framebuffer. Mode setting rewrites line length and color-mode registers for 8-bit pseudocolor or 15/16-bit truecolor. Removal unregisters, unmaps, and releases the PCI region.

## State and Persistence
The driver keeps little per-device state beyond `fb_info`; hardware state is programmed into VGA/extension/flat-panel registers and RAMDAC palette ports. The fixed `chipsfb_fix` assumes 1MB of visible framebuffer memory, while mapping may cover 2MB. Suspend marks the fb suspended and relies on console lock coordination.

## Dependencies and Integration Points
Dependencies include PCI, aperture conflict handling, fbdev IOMEM ops, fixed legacy VGA I/O ports, optional `CONFIG_PMAC_BACKLIGHT`, and architecture-specific framebuffer mapping (`ioremap_wc()` on PPC). It binds PCI vendor/device IDs for CT 65550.

## Risks and Edge Cases
The code explicitly supports only one chip because fixed I/O ports are global. Memory-size detection is not implemented and the fix info assumes 1MB despite some systems having 2MB. `chipsfb_blank()` delegates to fbdev colormap blacking rather than powering down hardware. 16 bpp is programmed as 15-bit 555 color, which may surprise users expecting RGB565.

## Test Signals
Signals include successful bind to CT 65550, visible 800x600 output, palette writes in 8 bpp, correct pseudo/truecolor metadata after bpp changes, no conflict with aperture owners, PMac backlight activation where configured, suspend/resume console behavior, and clean removal with BAR release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/chipsfb.c -->
