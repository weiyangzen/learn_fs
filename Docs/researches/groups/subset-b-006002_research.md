<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/radeon.h -->
# sources/distributed-fs/ceph-client/include/video/radeon.h

## Purpose
This header is a Radeon register map for old Radeon framebuffer/display support. It defines MMIO aperture size, PCI/config offsets, display controller registers, overlay registers, command processor and 2D engine registers, PLL indices, memory-controller indirect indices, and many bit masks for clock, power, CRTC, panel, DAC, surface, blitter, AGP, and memory programming.

## Important APIs, Types, And Functions
- `RADEON_REGSIZE` declares the expected 16 KiB register aperture.
- Register offsets include config/PCI registers (`BUS_CNTL`, `CNFG_MEMSIZE`, `REG_MEM_BASE`), display and CRTC registers (`CRTC_GEN_CNTL`, `CRTC_H_TOTAL_DISP`, `CRTC_OFFSET`, `CRTC2_GEN_CNTL`), flat-panel/LVDS/TMDS registers, overlay/subpicture registers, command processor ring registers, scratch registers, and 2D blitter registers.
- Bit definitions cover enable/disable, reset, idle, endian, pixel-format, ROP, PLL, power-management, AGP, memory-controller, surface translation, and cursor/display state.
- PLL and indirect register names are exported both as simple indices (`pllPPLL_CNTL`, `pllSCLK_CNTL`, `ixR300_MC_*`) and detailed field masks (`PIXCLKS_CNTL__*`, `SCLK_CNTL__*`, `MCLK_CNTL__*`).

## Control Flow
There is no executable control flow in the header. Driver control flow is implied: map the Radeon MMIO region, compute mode/clock/memory values, write offsets with the masks here, poll idle/status bits such as `RBBM_STATUS`, `CRTC_VBLANK`, `GUI_ACTIVE`, and `RB2D_DC_BUSY`, and sequence display/PLL/power changes carefully. PLL access is indirect through `CLOCK_CNTL_INDEX`/`CLOCK_CNTL_DATA` with `PLL_WR_EN`.

## State And Persistence
State is hardware-resident in Radeon registers and survives until overwritten, reset, suspend, or device power loss. The header exposes no software persistence, but many masks control persistent display routing, panel power, clocks, memory timings, AGP behavior, cursor state, palette access, framebuffer offsets, and scratch registers used by firmware or drivers.

## Dependencies And Integration Points
Consumers are low-level Radeon fb/DRM code that uses Linux MMIO accessors and PCI resource mapping. Integration points include display mode setting, DPMS/power management, DDC/GPIO probing, PLL programming, 2D acceleration, video overlay, LVDS/TMDS/TV output, AGP/PCI bus setup, and suspend/resume restore tables.

## Risks And Edge Cases
Incorrect bit masks or write ordering can blank displays, lock the 2D engine, corrupt memory-controller timing, or hang the GPU. Several names alias the same offsets for different chip families, so code must select the right generation. Some constants are marked broken or duplicate (`RB2D_DSTCACHE_CTLSTAT_broken`, duplicate `SRC_PITCH_OFFSET`/`AGP_PLL_CNTL`), and read-modify-write must avoid reserved/write-sensitive bits.

## Test Signals
Useful signals are successful mode set on CRT/LVDS/TMDS outputs, correct pixel clock, stable suspend/resume, working palette/cursor, clean 2D acceleration with cache flushes, no GPU idle timeouts, valid DDC reads through GPIO registers, and no display corruption across endian and bpp modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/radeon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/s1d13xxxfb.h -->
# sources/distributed-fs/ceph-client/include/video/s1d13xxxfb.h

## Purpose
This header defines Epson S1D13xxx framebuffer register offsets, chip identifiers, and driver/platform data structures. It supports initialization of S1D13505, S1D13506, and S1D13806-style LCD/CRT framebuffer controllers.

## Important APIs, Types, And Functions
- `S1D_PALETTE_SIZE`, `S1D_FBID`, and `S1D_DEVICENAME` identify framebuffer resources.
- `S1DREG_*` constants cover revision, GPIO, clocks, SDRAM, LCD/CRT timing, cursor, BitBLT, palette lookup, power-save, and common display mode registers.
- `S1DREG_DELAYOFF` and `S1DREG_DELAYON` are pseudo-register markers for init tables that need delays.
- `struct s1d13xxxfb_regval` is an address/value pair for board-provided register initialization.
- `struct s1d13xxxfb_par` stores mapped registers, display type, product/revision, pseudo palette, and optional PM register/framebuffer snapshots.
- `struct s1d13xxxfb_pdata` supplies init tables and platform video/power hooks.

## Control Flow
The driver reads `S1DREG_REV_CODE`, validates product/revision, applies `initregs`, handles delay pseudo-entries, configures LCD/CRT clocks/timings/memory, and exposes fb operations. PM flow saves registers/screen contents into `regs_save`/`disp_save`, calls platform suspend/resume hooks, and restores controller state.

## State And Persistence
Hardware state lives in S1D registers and display memory. Driver state is in `s1d13xxxfb_par`, including pseudo palette and PM snapshots when enabled. Board policy persists only as platform data compiled or registered by board code.

## Dependencies And Integration Points
It integrates with Linux fbdev, platform-device data, MMIO register mapping, optional `CONFIG_PM`, board power/video hooks, palette handling, and hardware BitBLT support.

## Risks And Edge Cases
Register offsets are noted as tested on S1D13896, so using them across all S1D13xxx variants can be unsafe without chip-specific validation. Init-table delay markers share the same type as register addresses, making validation important. PM restore can corrupt display if saved sizes or register ordering are wrong.

## Test Signals
Probe should detect the expected product ID, apply init registers, display a stable mode, update palette and cursor state, execute solid fill BitBLT where used, and survive suspend/resume with content and timing restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/s1d13xxxfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sa1100fb.h -->
# sources/distributed-fs/ceph-client/include/video/sa1100fb.h

## Purpose
This header describes StrongARM SA-1100 LCD framebuffer board configuration. It provides RGB bitfield definitions and a platform descriptor used by the SA-1100 fb driver.

## Important APIs, Types, And Functions
- `RGB_4`, `RGB_8`, `RGB_16`, and `NR_RGB` index supported color-depth maps.
- `struct sa1100fb_rgb` stores fbdev red/green/blue/transparency bitfields for a depth.
- `struct sa1100fb_mach_info` carries pixel clock, resolution, bpp, sync timings, colormap flags, raw LCCR register values, optional RGB map overrides, and board callbacks for backlight, LCD power, and visual setup.

## Control Flow
The driver consumes `sa1100fb_mach_info` during probe or board setup, converts timings into LCD controller registers, selects RGB layout by bpp, applies `lccr0`/`lccr3`, and calls power/visual hooks during enable, blanking, or mode changes.

## State And Persistence
State is a board-provided descriptor plus SA-1100 LCD controller registers. The header itself persists no data. The callbacks represent external board state such as backlight rails, panel power, or GPIO visual mode.

## Dependencies And Integration Points
It depends on fbdev types from `<linux/fb.h>` and basic Linux types. Integration is with SA-1100 board files, LCD controller setup, colormap handling, and board-specific power GPIO/regulator logic.

## Risks And Edge Cases
Bad timing fields or raw LCCR values can damage or blank panels. Callback NULL handling matters on boards without power hooks. RGB override arrays must match the `NR_RGB` indexing contract.

## Test Signals
Expected signals are correct mode timing, color channel layout at each supported bpp, working blank/unblank/backlight control, stable colormap behavior for greyscale/inverse/static modes, and no panel glitches during visual changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sa1100fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/samsung_fimd.h -->
# sources/distributed-fs/ceph-client/include/video/samsung_fimd.h

## Purpose
This header defines Samsung S3C/Exynos FIMD framebuffer register offsets and bit helpers for display output, timing, windows, DMA buffers, interrupts, color keying, dithering, palette, blending, and v8 offset variants.

## Important APIs, Types, And Functions
- `VIDCON0`/`VIDCON1`/`VIDCON2` fields configure output type, RGB/i80/TV/writeback paths, clock source/divider, scan mode, data width, polarity, and enable bits.
- `VIDTCON0`/`VIDTCON1`/`VIDTCON2` macros compose vertical/horizontal timing values and extended 12-bit active sizes.
- `WINCON(_win)` and `WINCONx_*`/`WINCON0_*`/`WINCON1_*` select per-window enable, local input, buffer auto-select, byte/word swaps, burst length, color formats, and alpha/blending behavior.
- `SHADOWCON`, `VIDOSD*`, `VIDW_BUF_*`, `VIDINTCON*`, `WKEYCON`, `DITHMODE`, `WINxMAP`, `WPALCON`, `BLENDEQx`, `BLENDCON`, and `DP_MIE_CLKCON` define shadow protection, window geometry, DMA start/end/stride, interrupt selection/status, color keying, dithering, palette format, blend equations, and DisplayPort/MIE clock control.

## Control Flow
Driver mode-set flow computes timing fields, selects a clock, programs global output in `VIDCON*`, configures each active window's format/geometry/DMA buffer, updates shadow registers, enables interrupts, and finally sets `VIDCON0_ENVID`/`VIDCON0_ENVID_F`. Plane updates use window-specific offsets and may protect/unprotect shadow state.

## State And Persistence
Display state is in FIMD hardware registers and DMA framebuffer memory. Window enable, DMA addresses, blend/palette/color-key state, interrupt enables, and shadow-protect bits persist until changed or reset. No software storage is declared in this header.

## Dependencies And Integration Points
This is consumed by Samsung fbdev/DRM display code and SoC-specific clock, DMA, interrupt, and panel/bridge code. The macros encode differences across S3C2443+, S3C64xx, S5PV210, Exynos, and FIMD v8 register layouts.

## Risks And Edge Cases
The bpp matrix shows unsupported per-window formats; using a valid value on the wrong window can fail silently. Active size helpers split extended bits, so off-by-one or missing `_E()` bits can truncate large modes. Shadow protection and buffer address updates must be ordered to avoid tearing or fetching invalid memory.

## Test Signals
Signals include clean mode set across supported SoCs, correct per-window formats and byte order, working overlays/alpha/color keying, no FIFO underruns, correct frame interrupts, palette updates with `WPALCON_PAL_UPDATE`, and large-resolution modes that validate extended active-size fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/samsung_fimd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sh_mobile_lcdc.h -->
# sources/distributed-fs/ceph-client/include/video/sh_mobile_lcdc.h

## Purpose
This header defines Renesas SH Mobile LCDC register bits and platform data structures for LCD channels, system-bus panels, backlight, transmitters, and overlays.

## Important APIs, Types, And Functions
- `_LDDCKR`, `_LDINTR`, `_LDSR`, `_LDCNT*`, `_LDRCNTR`, and `_LDDDSR` constants cover clock source, interrupts/status, controller enable/reset, and bus/data status.
- `LDMT1R_*`, `LDDFR_*`, `LDSM*`, and `LDPMR_*` encode interface type, polarity, dot-clock controls, input format, and pixel format.
- Interface enums map to RGB, YUV, and system-bus modes such as `RGB16`, `RGB24`, `SYS8A`, and `SYS16A`.
- `struct sh_mobile_lcdc_sys_bus_ops` provides index/data/read callbacks for system-bus panels.
- `struct sh_mobile_lcdc_panel_cfg`, `sh_mobile_lcdc_bl_info`, `sh_mobile_lcdc_overlay_cfg`, `sh_mobile_lcdc_chan_cfg`, and `sh_mobile_lcdc_info` describe panel dimensions, lifecycle hooks, backlight, overlays, channels, modes, transmitter devices, and global clock source.

## Control Flow
Probe consumes `sh_mobile_lcdc_info`, configures per-channel clock/interface flags, registers modes, optionally sets up system-bus operations, powers the panel, starts transfers, and programs overlays. Runtime flow toggles display/backlight hooks, handles LCDC interrupts, and updates channel framebuffers and transmitter devices.

## State And Persistence
State is split between LCDC registers, platform descriptors, framebuffer modes, overlay limits, panel callbacks, and optional backlight state. System-bus deferred I/O delay is a persistent policy in `sys_bus_cfg`.

## Dependencies And Integration Points
It depends on fbdev video modes and Linux platform devices. Integration points include panel code, HDMI/DSI transmitter devices, sys-bus panel command/data paths, backlight callbacks, clock trees, and overlay FourCC negotiation.

## Risks And Edge Cases
Polarity flags are panel-sensitive; incorrect values can blank or destabilize panels. System-bus callbacks can be NULL or slow and must match `interface_type`. Overlay maximum resolution and FourCC values must match hardware capabilities.

## Test Signals
Expected tests cover RGB and system-bus panels, display on/off callbacks, backlight brightness control, correct interrupt/status handling, supported FourCC overlays, external transmitter attachment, and suspend/resume register restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sh_mobile_lcdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sisfb.h -->
# sources/distributed-fs/ceph-client/include/video/sisfb.h

## Purpose
This header provides kernel-side SiS framebuffer identifiers and pulls in the UAPI interface for the SiS fb driver.

## Important APIs, Types, And Functions
- Includes `<linux/pci.h>` and `<uapi/video/sisfb.h>` for PCI and userspace-facing definitions.
- `UNKNOWN_VGA`, `SIS_300_VGA`, and `SIS_315_VGA` classify supported SiS VGA families.

## Control Flow
There is no control flow. Driver code uses the family constants after PCI/chip probing to dispatch generation-specific initialization and mode-setting paths.

## State And Persistence
The header declares no state. The family constants influence driver-private runtime state and capability selection.

## Dependencies And Integration Points
It integrates the SiS framebuffer driver with PCI probing and UAPI ioctls/structures in `uapi/video/sisfb.h`.

## Risks And Edge Cases
Misclassifying a chip family can select incompatible register sequences. Because the real UAPI lives elsewhere, changes must preserve compatibility with userspace.

## Test Signals
Probe logs should classify the correct family, expose expected UAPI behavior, and initialize modes on both 300- and 315-series hardware without selecting unknown fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sisfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sstfb.h -->
# sources/distributed-fs/ceph-client/include/video/sstfb.h

## Purpose
This header defines the 3Dfx Voodoo SST framebuffer driver's debug macros, PCI/register bit definitions, DAC/PLL constants, ioctls, and driver-private structures.

## Important APIs, Types, And Functions
- `dprintk`, `r_dprintk`, `f_dprintk`, and `v_dprintk` expand based on `SST_DEBUG`.
- Register offsets and bits describe PCI init, LFB/FBZ mode, clipping, FIFO/reset, video timing, DAC access, BitBLT, and hardware status.
- Default register macros (`FBIINIT*_DEFAULT`) encode baseline initialization.
- `SSTFB_SET_VGAPASS` and `SSTFB_GET_VGAPASS` are framebuffer ioctls for VGA passthrough.
- `struct pll_timing` stores PLL `m/n/p`.
- `struct dac_switch` abstracts DAC detection, PLL programming, and video-mode setup.
- `struct sst_spec` describes board default/max clocks.
- `struct sstfb_par` stores palette, timing-derived values, PLL, tile count, MMIO base, DAC operations, PCI device, card type/revision, and VGA passthrough state.

## Control Flow
Driver flow detects the DAC through `dac_switch.detect`, computes PLL timing, programs DAC/video registers using the constants here, configures FBI init registers, sets LFB format, and uses BitBLT commands for acceleration. The VGA passthrough ioctl toggles passthrough state through `vgapass` and related registers.

## State And Persistence
Persistent runtime state is in `sstfb_par`, MMIO registers, DAC registers, and the VGA passthrough setting. Palette and mode timing fields are cached in software while actual display behavior is hardware-resident.

## Dependencies And Integration Points
It integrates with fbdev, PCI devices, kernel ioctl encoding, DAC-specific helpers, register accessors in the implementation, and optional debugging.

## Risks And Edge Cases
Some registers are write-sensitive: the comment on `FBIINIT6_DEFAULT` warns that writing back read values can alter DAC pin drivers. Incorrect FIFO/reset/video sequencing can hang the card. Endian swizzle bits, 16/24bpp selection, and Voodoo1/Voodoo2 clock differences are common failure points.

## Test Signals
Test signals include DAC detection, stable PLL/mode programming, working VGA passthrough ioctls, correct 16/24bpp LFB output, BitBLT copy/fill success, no FIFO busy timeouts, and debug logs that align with register writes when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sstfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sticore.h -->
# sources/distributed-fs/ceph-client/include/video/sticore.h

## Purpose
This header defines the HP PA-RISC STI graphics firmware interface used by console/framebuffer code. It models STI ROM data, global configuration, firmware call argument blocks, font/block-move operations, and the in-kernel `sti_struct` wrapper.

## Important APIs, Types, And Functions
- Constants define ROM counts, region count, monitor limits, font types, alternate code types, and `STI_WAIT`.
- `region_t` maps STI region descriptors; `REGION_OFFSET_TO_PHYS()` converts region offsets against HPA.
- `struct sti_glob_cfg*`, `sti_init_*`, `sti_conf_*`, `sti_font_*`, and `sti_blkmv_*` mirror firmware ABI argument and result blocks.
- `struct sti_rom` and `struct sti_rom_font` model firmware ROM tables and font descriptors.
- `struct sti_cooked_font`, `sti_cooked_rom`, `sti_all_data`, and `sti_struct` hold converted fonts, firmware entry addresses, region mappings, locks, PCI/device handles, low-memory call data, and selected font.
- Public functions include `sti_get_rom()`, `sti_font_convert_bytemode()`, `sti_call()`, `sti_putc()`, `sti_set()`, `sti_clear()`, and `sti_bmove()`.

## Control Flow
Generic STI code discovers ROMs, parses regions/fonts, allocates `sti_all_data` in suitable memory, initializes firmware through `init_graph`, queries display config through `inq_conf`, and serializes firmware calls with `sti_struct.lock`. Console operations call `sti_putc`, `sti_clear`, and `sti_bmove`, which prepare ABI blocks and invoke `sti_call`.

## State And Persistence
`sti_struct` persists ROM metadata, selected font, regions, global config, firmware entry points, call mode, device path, and shared call buffers. Firmware and device state persist in hardware and STI global memory. `save_addr` and `sti_mem_addr` reserve firmware reentry/global storage.

## Dependencies And Integration Points
It depends on PA-RISC IO translation (`virt_to_phys`, `<asm/io.h>`), spinlocks, PCI/device infrastructure, console/fb code, and low-memory allocation constraints on 64-bit kernels.

## Risks And Edge Cases
The comments warn that STI calls returning busy can require spin-locked wait loops with high interrupt latency. ABI structures must match firmware layout exactly. 32-bit STI code on 64-bit kernels requires low memory. Bad region mapping or font conversion can crash firmware calls.

## Test Signals
Signals include successful ROM discovery, valid `inq_conf` dimensions, visible console text through `sti_putc`, clear/block-move behavior, correct font dimensions/CRC selection, no firmware call busy hangs, and working 32-bit and 64-bit STI call paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sticore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tdfx.h -->
# sources/distributed-fs/ceph-client/include/video/tdfx.h

## Purpose
This header defines 3Dfx Banshee/Voodoo3-style framebuffer register offsets, bit masks, I2C/DDC bit positions, VGA port constants, and kernel-private driver state.

## Important APIs, Types, And Functions
- Register offsets cover `membase0` init, PLL, DAC, video processor, cursor, overlay, 2D engine, and 3D command spaces.
- Bit masks cover 2D ROP/commands, busy/retrace status, CLUT behavior, memory type, VGA disable/extended timing, video processor enable, cursor enable, pixel format, and DAC 2x mode.
- DDC/I2C masks in `VIDSERPARPORT` drive bit-banged monitor probing.
- `struct banshee_reg` stores VGA and extension registers for save/restore.
- `struct tdfxfb_i2c_chan` wraps an I2C adapter and bit-bang algorithm data.
- `struct tdfx_par` stores max pixel clock, pseudo palette, mapped registers, I/O base, write-combine cookie, and optional I2C channels.

## Control Flow
Driver flow maps registers, saves/restores VGA/Banshee state, computes PLLs, programs screen size/stride/video processor, controls hardware cursor, uses 2D command registers for fill/blit, and optionally bit-bangs DDC/I2C over `VIDSERPARPORT`.

## State And Persistence
State lives in `tdfx_par`, saved `banshee_reg`, MMIO registers, VGA legacy ports, CLUT/palette, write-combine mapping, and optional I2C adapters. Hardware state persists across driver operations until reset or restored.

## Dependencies And Integration Points
It depends on Linux I2C and i2c-algo-bit when `CONFIG_FB_3DFX_I2C` is enabled, fbdev driver code, VGA register access, MMIO, and PCI resource setup.

## Risks And Edge Cases
Legacy VGA constants are explicitly not multihead-safe. Incorrect write-combine handling can corrupt framebuffer access. 2D command launch must respect `STATUS_BUSY`. I2C bit masks share one serial port register and need careful direction/value handling.

## Test Signals
Signals include mode set and restore, DDC reads on both optional channels, correct cursor and palette behavior, 2D fill/blit completion, no busy timeouts, and clean suspend/resume of saved VGA/extension registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tdfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tgafb.h -->
# sources/distributed-fs/ceph-client/include/video/tgafb.h

## Purpose
This header defines DEC 21030 TGA framebuffer hardware constants, RAMDAC register programming helpers, and driver-private display state.

## Important APIs, Types, And Functions
- `TGA_TYPE_8PLANE`, `TGA_TYPE_24PLANE`, and `TGA_TYPE_24PLUSZ` classify framebuffer variants.
- Offsets define ROM, registers, 8-plane/24-plane/24+Z framebuffer bases, TGA control registers, copy engines, clock and RAMDAC access.
- Timing masks define horizontal/vertical register composition.
- RAMDAC constants cover BT485, BT463, and BT459 register/address spaces.
- `struct tga_par` stores device pointer, mapped memory/register/framebuffer bases, type/revision, blank state, mode timing, PLL frequency, bpp, sync-on-green, and palette.
- Inline helpers `TGA_WRITE_REG`, `TGA_READ_REG`, `BT485_WRITE`, `BT463_LOAD_ADDR`, `BT463_WRITE`, `BT459_LOAD_ADDR`, and `BT459_WRITE` perform MMIO/RAMDAC accesses.

## Control Flow
The driver maps TGA memory, selects the framebuffer offset and RAMDAC path by `tga_type`, computes timing/PLL registers, writes display and RAMDAC registers through the inline helpers, and uses valid/blank/cursor bits to control output.

## State And Persistence
Persistent state is in `tga_par`, MMIO registers, RAMDAC palettes/cursor registers, and framebuffer memory. `vesa_blanked` caches current blanking mode while actual blank/video/cursor state is hardware-resident.

## Dependencies And Integration Points
It integrates with fbdev, Linux device infrastructure, MMIO `readl`/`writel`, DEC TGA hardware, and RAMDAC-specific mode/palette/cursor setup.

## Risks And Edge Cases
Wrong RAMDAC path or framebuffer offset for a TGA type will write the wrong device region. Timing masks split active/back/front/sync fields and require exact composition. Inline MMIO helpers have no locking, so callers must serialize register access where needed.

## Test Signals
Expected signals include correct variant detection, stable 8-plane and 24-plane modes, working palette/cursor writes for BT485/BT463/BT459, valid blank/unblank state, and successful copy/fill paths where implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tgafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/trident.h -->
# sources/distributed-fs/ceph-client/include/video/trident.h

## Purpose
This header defines Trident framebuffer debug/output macros, supported PCI IDs, LCD policy constants, VGA extension register indices, graphics-engine offsets, and common ROP values.

## Important APIs, Types, And Functions
- `TRIDENTFB_DEBUG` controls `debug()` logging; `output()` logs with the `tridentfb` prefix.
- PCI IDs cover Cyber, TGUI, ProVIDIA, Image, Blade3D, and CyberBlade families.
- `LCD_STRETCH`, `LCD_CENTER`, and `LCD_BIOS` select laptop panel scaling policy.
- Register constants cover sequencer (`3C4`), CRTC (`3x4`), graphics (`3CE`) extensions, LCD/TV registers, memory clock, I2C, cursor, and graphics engine registers.
- `ROP_S`, `ROP_P`, and `ROP_X` define source, pattern, and XOR raster operations.

## Control Flow
The driver uses PCI IDs to select chipset behavior, unlocks protected registers via key registers, programs clocks/memory/LCD scaling through extension indices, and uses graphics engine registers for acceleration. Debug macros add trace points when enabled at compile time.

## State And Persistence
No software state is declared. State is held in VGA extension registers, graphics-engine registers, LCD policy variables in the implementation, and PCI/chip detection results.

## Dependencies And Integration Points
It integrates with Trident fbdev implementation, PCI probing, VGA indexed register access, laptop LCD scaling, I2C/DDC register handling, and graphics acceleration.

## Risks And Edge Cases
Some comments note mismatched "real" PCI IDs; detection code must handle aliases. Many registers share indices across old/new chips, so generation gating is required. LCD stretch/center/BIOS policy can conflict with panel native timing.

## Test Signals
Probe should identify each supported chipset, unlock and program extension registers, read DDC where available, set LCD scaling modes, and complete graphics-engine copy/fill operations with expected ROP results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/trident.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/udlfb.h -->
# sources/distributed-fs/ceph-client/include/video/udlfb.h

## Purpose
This header defines the DisplayLink USB framebuffer driver's private state, deprecated damage/EDID ioctls, URB pool structures, compression thresholds, transfer limits, and deferred I/O timing.

## Important APIs, Types, And Functions
- `DLFB_IOCTL_RETURN_EDID` and `DLFB_IOCTL_REPORT_DAMAGE` support existing DisplayLink X server behavior.
- `struct dloarea` reports damaged rectangles.
- `struct urb_node` and `struct urb_list` manage USB URBs with list, lock, semaphore limit, availability/count, and transfer size.
- `struct dlfb_data` stores USB device, fb info, URB pool, backing buffer, virtual/active/lost-pixels state, EDID, SKU limits, palettes, blank mode, render mutex, damage rectangle/lock/work item, fb ops, mmap count, render metrics, current mode, and deferred-free list.
- Transfer constants define request IDs, `BULK_SIZE`, `MAX_TRANSFER`, `WRITES_IN_FLIGHT`, vendor descriptor size, URB timeouts, bpp, pixel command limits, RLX/RLE/RAW minimum sizes, and deferred I/O delays.

## Control Flow
Framebuffer writes mark damaged areas, workqueue processing compares against the backing buffer, compresses changed pixels into DisplayLink commands, obtains URBs from `urb_list`, submits USB bulk transfers, updates metrics, and tracks failures through `lost_pixels`. Ioctls return EDID or report explicit damage.

## State And Persistence
Runtime state is extensive in `dlfb_data`: backing framebuffer copy, damage bounds, EDID, current mode, URB availability, USB activity, blank state, mmap count, deferred frees, and sysfs metrics. Device persistence is limited to USB device state and monitor EDID.

## Dependencies And Integration Points
It integrates with USB core, fbdev, workqueues, mutex/spinlock/semaphore/atomic primitives, deferred I/O, sysfs metrics, EDID handling, and existing DisplayLink userspace.

## Risks And Edge Cases
Damage bounds are shared between rendering and ioctl paths and must be protected by `damage_lock`. USB disconnect uses `virtualized` and `usb_active`; code must update the backing buffer without submitting URBs when inactive. Compression thresholds and transfer limits must avoid overrun while keeping URBs full enough for performance.

## Test Signals
Signals include correct EDID return, damage ioctl refresh, no lost pixels under heavy mmap/fb writes, bounded URB in-flight counts, stable disconnect/reconnect handling, accurate byte/cpu metrics, and deferred I/O behavior at both normal and disabled delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/udlfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/uvesafb.h -->
# sources/distributed-fs/ceph-client/include/video/uvesafb.h

## Purpose
This header defines the uvesafb kernel-side VBE/VESA structures, mode flags, userspace task wrapper, palette entry, mode-selection flags, and driver-private state.

## Important APIs, Types, And Functions
- `struct vbe_crtc_ib` models a packed VBE CRTC info block with horizontal/vertical timing, flags, pixel clock, and refresh rate.
- `struct vbe_mode_ib` models a packed VBE mode info block covering VBE 1.0 through 3.0 fields, including windowing, resolution, memory model, direct color masks, linear framebuffer address, image pages, max pixel clock, mode ID, and depth.
- `VBE_MODE_*` and `VBE_MODE_MASK` identify supported color graphics linear-framebuffer modes.
- `UVESAFB_DEFAULT_MODE`, `UVESAFB_TIMEOUT`, and `UVESAFB_TASKS_MAX` define fallback mode, userspace reply timeout, and concurrency limit.
- `struct uvesafb_pal_entry` and DAC port constants support palette programming.
- `struct uvesafb_ktask` wraps a UAPI task with buffer, completion, and acknowledgement.
- `struct uvesafb_par` stores VBE info, mode list, CRTC data, PMI state, original/saved VBE state, refcount, selected mode, MTRR handle, and ypan behavior.

## Control Flow
The driver asks userspace to execute VBE BIOS calls via `uvesafb_ktask`, waits up to `UVESAFB_TIMEOUT`, parses mode blocks, selects a mode by exact-resolution/depth flags, optionally applies CRTC settings, maps the linear framebuffer, saves original state, and restores saved/original state during suspend or unload.

## State And Persistence
Persistent driver state includes VBE mode tables, saved BIOS state, PMI pointers, current mode index, CRTC settings, MTRR registration, and atomic reference count. Hardware state is in VBE firmware-controlled video registers and DAC palette.

## Dependencies And Integration Points
It depends on `uapi/video/uvesafb.h`, completion/atomic primitives in implementation, userspace helper infrastructure, VBE BIOS, fbdev, MTRR support, and x86/VESA-compatible firmware.

## Risks And Edge Cases
Packed structures must match VBE ABI exactly. Userspace helper timeouts or bad acknowledgements block mode setup. `nocrtc`, `ypan`, and PMI palette flags change hardware paths and need validation. Mode blocks from firmware can be malformed or unsupported despite advertised attributes.

## Test Signals
Signals include successful helper round trips, valid mode list parsing, exact resolution/depth selection, framebuffer mapping at `phys_base_ptr`, palette updates with and without PMI, ypan/ywrap behavior, saved state restoration, and timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/uvesafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/vga.h -->
# sources/distributed-fs/ceph-client/include/video/vga.h

## Purpose
This header provides standard VGA port/register constants, state save/restore declarations, and inline helpers for MMIO or I/O-port based VGA register access.

## Important APIs, Types, And Functions
- Constants define VGA framebuffer physical base/size, data/index ports, register counts, misc/CRTC/attribute/sequencer/graphics indices and masks, and state-save flags.
- `struct vgastate` describes a VGA state snapshot request: MMIO base, memory window, flags, depth, register counts, and opaque saved state.
- `save_vga()` and `restore_vga()` are exported state-management functions.
- Inline helpers cover raw MMIO/I/O reads and writes (`vga_mm_r`, `vga_io_r`, `vga_r`, `vga_w`), fast 16-bit writes on little-endian systems, and indexed CRTC, sequencer, graphics, and attribute controller access.

## Control Flow
Callers choose MMIO when `regbase` is non-NULL or I/O ports when available. Indexed helpers write the register index then read/write the data port, with optional combined 16-bit writes under `VGA_OUTW_WRITE`. State save/restore routines use `vgastate.flags` to capture mode, fonts, text, and colormap.

## State And Persistence
The VGA device retains register, palette, font, and framebuffer state. `vgastate.vidstate` points to saved software snapshots used across mode changes or driver handoff.

## Dependencies And Integration Points
It depends on Linux IO accessors, architecture VGA definitions, byte order, and optional `CONFIG_HAS_IOPORT`. It is shared by VGA-compatible framebuffer/DRM/console drivers.

## Risks And Edge Cases
I/O ports may be unavailable on some architectures, so MMIO fallback must be valid. Fast 16-bit index/data writes are little-endian only. Attribute controller access has flip-flop behavior in VGA hardware, so callers must follow VGA sequencing expectations. Register count defaults must match allocated snapshot sizes.

## Test Signals
Signals include successful save/restore around driver handoff, correct font and colormap preservation, working MMIO-only and I/O-port paths, valid indexed register reads/writes, and no corruption from fast-write mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/videomode.h -->
# sources/distributed-fs/ceph-client/include/video/videomode.h

## Purpose
This header defines a subsystem-independent video mode representation and conversion helpers from display timing data.

## Important APIs, Types, And Functions
- `struct videomode` stores pixel clock, horizontal active/front/back/sync values, vertical active/front/back/sync values, and display flags.
- `videomode_from_timing()` converts one `struct display_timing` into a `videomode`.
- `videomode_from_timings()` selects an indexed entry from `struct display_timings` and converts it.

## Control Flow
The helper functions are called by display drivers after reading firmware or device-tree timing tables. They normalize timing data into the compact `videomode` structure used by panels, bridges, and controllers.

## State And Persistence
The header declares no persistent state. The resulting `videomode` is caller-owned and usually becomes part of mode-setting state.

## Dependencies And Integration Points
It depends on `<video/display_timing.h>` and Linux types. Integration points include device-tree display timings, panel drivers, fbdev/DRM mode conversion, and controller-specific timing register programming.

## Risks And Edge Cases
Invalid timing indexes should be surfaced by `videomode_from_timings()`. Drivers must handle flags and units correctly; pixel clock is in Hz while some hardware registers use kHz, periods, or divisors.

## Test Signals
Tests should compare converted timing fields against known device-tree entries, verify out-of-range indexes fail, and confirm downstream mode programming receives the expected polarity/edge flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/videomode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/acpi.h -->
# sources/distributed-fs/ceph-client/include/xen/acpi.h

## Purpose
This header connects ACPI sleep and interrupt routing behavior to Xen Dom0/PVH support. It provides hooks for notifying the hypervisor about ACPI sleep and querying or setting up GSI routing.

## Important APIs, Types, And Functions
- `get_gsi_from_sbdf_t` is a callback type for mapping PCI segment/bus/device/function encoding to a GSI.
- Under `CONFIG_XEN_DOM0`, exported functions notify Xen about normal and extended sleep, set up PVH GSI routing, query PCI GSI trigger/polarity, register the SBDF callback, and resolve GSI from SBDF.
- `xen_acpi_suspend_lowlevel()` bypasses native CPU context save because Xen handles CPU context.
- `xen_acpi_sleep_register()` installs Xen ACPI prepare-sleep hooks and low-level suspend only for `xen_initial_domain()`.
- Without Dom0 support, stubs return `-1` or do nothing.

## Control Flow
During ACPI initialization in a Xen initial domain, `xen_acpi_sleep_register()` replaces ACPI prepare-sleep callbacks with Xen-aware versions and points `acpi_suspend_lowlevel` at the Xen suspend helper. PCI/GSI code calls the Xen helpers to communicate routing to the hypervisor.

## State And Persistence
State is in global ACPI callback pointers and the registered SBDF-to-GSI callback in the implementation. Sleep state is communicated to Xen rather than persisted here.

## Dependencies And Integration Points
It depends on ACPI core, Xen domain detection, Xen hypervisor support, PCI devices, and Dom0/PVH interrupt routing code.

## Risks And Edge Cases
Hooks must only be installed in the Xen initial domain. Stub functions returning `-1` require callers to handle non-Xen builds. The function prototype names `pm1b_cnd` in one declaration, likely a typo, but ABI remains by position.

## Test Signals
Signals include ACPI S3 requests notifying Xen, PVH GSI setup succeeding with correct trigger/polarity, SBDF callback registration/use, and non-Xen or non-Dom0 builds taking the stub path safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypercall.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/hypercall.h

## Purpose
This ARM Xen header declares Linux hypercall entry points and small wrappers for platform and suspend operations.

## Important APIs, Types, And Functions
- `privcmd_call()` exposes a generic privileged hypercall path with five arguments.
- `HYPERVISOR_*` declarations cover version, console I/O, grant table, scheduler, event channel, HVM, memory, physdev, vcpu, vm assist, device-model, platform, and multicall operations.
- `HYPERVISOR_platform_op()` sets `interface_version` before calling `HYPERVISOR_platform_op_raw()`.
- `HYPERVISOR_suspend()` builds a `sched_shutdown` with `SHUTDOWN_suspend` and invokes `SCHEDOP_shutdown`; `start_info_mfn` is unused on ARM.

## Control Flow
Callers construct Xen public ABI structures, pass them through the declared hypercall functions, and check negative return codes. Suspend flow is a scheduler shutdown request rather than a platform-specific CPU-state save.

## State And Persistence
No state is stored here. Hypercalls mutate Xen-managed domain state, event channels, grants, memory maps, scheduling state, or platform state depending on command.

## Dependencies And Integration Points
It depends on Xen public `xen.h`, `sched.h`, `platform.h`, Linux bug handling, and ARM hypercall implementation code. It is consumed by Xen event, grant, memory, HVM, and console subsystems.

## Risks And Edge Cases
Incorrect ABI structures or counts can corrupt hypercall results. `HYPERVISOR_platform_op()` must set the correct interface version. ARM suspend intentionally ignores `start_info_mfn`, so shared code must not rely on x86 semantics.

## Test Signals
Signals include successful Xen version query, console I/O, event-channel operations, grant table operations, platform ops with version set, and suspend/resume behavior through `SCHEDOP_shutdown`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypercall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypervisor.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/hypervisor.h

## Purpose
This header exposes ARM Xen early boot globals and initialization hooks.

## Important APIs, Types, And Functions
- `HYPERVISOR_shared_info` points to Xen's shared info page.
- `xen_start_info` points to Xen start information.
- `xen_early_init()` is declared under `CONFIG_XEN` and stubbed otherwise.
- CPU hotplug registration hooks are empty inline functions when `CONFIG_HOTPLUG_CPU` is enabled.

## Control Flow
ARM Xen boot code calls `xen_early_init()` during early initialization to establish Xen shared state. CPU hotplug paths may call the arch register/unregister hooks, but this architecture implementation is a no-op in the header.

## State And Persistence
Persistent state is the shared-info and start-info pointers maintained by the Xen ARM implementation. The header itself stores no data.

## Dependencies And Integration Points
It depends on Linux init annotations and Xen architecture code. Consumers include early boot, event handling, time, and memory setup paths needing shared Xen data.

## Risks And Edge Cases
Non-Xen builds get a no-op early init, so callers must not assume Xen state exists. Shared info pointers must be initialized before consumers dereference them.

## Test Signals
Signals include early boot detecting Xen, valid shared-info mapping, safe non-Xen stub behavior, and CPU hotplug paths building cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/interface.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/interface.h

## Purpose
This header defines ARM Xen guest ABI helper types: aligned handles, pfn/long integer widths, primitive guest handles, maximum vCPU count, and pvclock structures.

## Important APIs, Types, And Functions
- `uint64_aligned_t` forces 8-byte alignment for ABI handle storage.
- `__DEFINE_GUEST_HANDLE`, `DEFINE_GUEST_HANDLE_STRUCT`, `DEFINE_GUEST_HANDLE`, `GUEST_HANDLE`, and `set_xen_guest_handle()` build Xen guest pointer handle types that work across 32/64-bit guests.
- `__HYPERVISOR_platform_op_raw` aliases the platform hypercall name.
- `xen_pfn_t`, `xen_ulong_t`, and `xen_long_t` are fixed 64-bit ABI types.
- Primitive guest handles are defined for char/int/void/uint64/uint32/pfn/ulong.
- `MAX_VIRT_CPUS` is one for this interface.
- `struct pvclock_vcpu_time_info` and `struct pvclock_wall_clock` provide packed time structures.

## Control Flow
There is no runtime control flow. Hypercall code populates guest handles with `set_xen_guest_handle()` before passing ABI structures to Xen.

## State And Persistence
No state is stored here. The structures define memory layout for shared ABI state exchanged with Xen.

## Dependencies And Integration Points
It depends on Linux integer types and is included by Xen public/arch interfaces and hypercall users. The guest-handle macros are central to grant, event, memory, and platform structures.

## Risks And Edge Cases
ABI packing/alignment must not change. `set_xen_guest_handle()` clears 64-bit storage before assigning the pointer, avoiding stale high bits on 32-bit guests; bypassing it risks invalid handles. `MAX_VIRT_CPUS` constrains this older ARM interface.

## Test Signals
Signals include compile-time ABI compatibility, correct handle layout on 32- and 64-bit ARM, hypercalls accepting handles, and pvclock readers handling packed structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/page.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/page.h

## Purpose
This header defines ARM Xen address translation helpers for pseudo-physical, guest, bus, and machine addresses, plus foreign grant mapping hooks and SWIOTLB decision support.

## Important APIs, Types, And Functions
- `xmaddr_t` and `xpaddr_t` wrap Xen machine and pseudo-physical addresses; `XMADDR()` and `XPADDR()` build them.
- `phys_to_machine_mapping_valid()` is always true and `INVALID_P2M_ENTRY` marks missing mappings.
- `pfn_to_gfn()` and `gfn_to_pfn()` are identity mappings on ARM.
- `pfn_to_bfn()` consults `phys_to_mach`/`__pfn_to_mfn()` when a non-empty mapping exists, otherwise falls back to identity.
- `virt_to_gfn()`, `gfn_to_virt()`, and `percpu_to_gfn()` convert kernel/percpu addresses to Xen page granularity.
- `arbitrary_virt_to_machine()` `BUG()`s because ARM guests are HVM for this path.
- Foreign mapping functions manage grant table map/unmap P2M entries.
- `__set_phys_to_machine*`, `set_phys_to_machine()`, and `xen_arch_need_swiotlb()` expose P2M updates and DMA bounce decisions.

## Control Flow
Grant mapping code calls `set_foreign_p2m_mapping()` after map hypercalls and `clear_foreign_p2m_mapping()` during unmap. DMA setup calls `xen_arch_need_swiotlb()` to decide whether a device address needs Xen SWIOTLB bouncing. Address helpers are inline conversion paths used by grant and DMA code.

## State And Persistence
Persistent state is the `phys_to_mach` red-black tree for non-identity bus mappings and architecture-maintained P2M entries. The header does not allocate state itself.

## Dependencies And Integration Points
It depends on ARM page and pgtable headers, Linux PFN/DMA/device types, Xen core detection, and grant-table structures. It integrates with Xen SWIOTLB, grant mapping, DMA APIs, and page conversion helpers.

## Risks And Edge Cases
Linux pages may span multiple non-contiguous 4 KiB Xen pages, so callers must not treat Linux pages and Xen frames as interchangeable. Direct PV-only helpers call `BUG()` on ARM. `pfn_to_bfn()` fallback to identity is correct only when no override mapping exists.

## Test Signals
Signals include correct grant map/unmap P2M updates, DMA bouncing decisions for non-direct mappings, valid conversions for normal/percpu addresses, and no PV-only helper use on ARM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/swiotlb-xen.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/swiotlb-xen.h

## Purpose
This header provides ARM Xen detection logic for enabling Xen SWIOTLB DMA operations.

## Important APIs, Types, And Functions
- `xen_swiotlb_detect()` returns false outside Xen, true for direct-mapped Xen domains, true for legacy initial-domain cases without explicit not-direct-mapped feature, and false otherwise.

## Control Flow
DMA setup code calls `xen_swiotlb_detect()` during device initialization. The function checks `xen_domain()`, `xen_feature(XENFEAT_direct_mapped)`, `xen_feature(XENFEAT_not_direct_mapped)`, and `xen_initial_domain()`.

## State And Persistence
No state is stored. It reads Xen feature state populated elsewhere.

## Dependencies And Integration Points
It depends on Xen feature setup and Xen domain detection. It is used by ARM Xen DMA ops selection.

## Risks And Edge Cases
Feature availability differs across Xen versions; the legacy initial-domain fallback preserves behavior when explicit feature bits are absent. Incorrect detection can either miss necessary bounce buffering or impose unnecessary SWIOTLB overhead.

## Test Signals
Signals include expected true/false results for non-Xen, direct-mapped, not-direct-mapped, and legacy Dom0 configurations, followed by correct DMA behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/swiotlb-xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/xen-ops.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/xen-ops.h

## Purpose
This header wires ARM devices to Xen DMA operations when Xen SWIOTLB is required.

## Important APIs, Types, And Functions
- `xen_setup_dma_ops(struct device *dev)` assigns `dev->dma_ops = &xen_swiotlb_dma_ops` under `CONFIG_XEN` when `xen_swiotlb_detect()` is true.

## Control Flow
Device setup calls `xen_setup_dma_ops()`. In Xen builds, the helper detects the SWIOTLB condition and installs Xen-aware DMA operations; otherwise it does nothing.

## State And Persistence
It mutates per-device DMA ops state. No global state is declared.

## Dependencies And Integration Points
It depends on `<xen/swiotlb-xen.h>`, `<xen/xen-ops.h>`, `struct device`, and Xen SWIOTLB DMA ops. It integrates with platform/OF/PCI device initialization.

## Risks And Edge Cases
Calling this too late can leave devices with stale DMA ops. Assigning Xen DMA ops unnecessarily can reduce performance; failing to assign them can cause devices to DMA to addresses Xen cannot translate.

## Test Signals
Signals include per-device `dma_ops` set under Xen direct-mapped/legacy Dom0 conditions, unchanged ops outside Xen, and successful DMA mapping/unmapping under Xen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/xen-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/balloon.h -->
# sources/distributed-fs/ceph-client/include/xen/balloon.h

## Purpose
This header declares Xen balloon memory-management state and APIs for changing domain memory targets and allocating/freeing ballooned pages.

## Important APIs, Types, And Functions
- `RETRY_UNLIMITED` encodes no retry limit.
- `struct balloon_stats` tracks current and target pages, target unpopulated pages, low/high balloon pages, total pages, schedule delay, max delay, retry count, and max retry count.
- `balloon_stats` is the global stats instance.
- `balloon_set_new_target()` updates the target allocation.
- `xen_alloc_ballooned_pages()` and `xen_free_ballooned_pages()` manage pages taken from or returned to the balloon.
- `xen_balloon_init()` is real under `CONFIG_XEN_BALLOON` and a no-op otherwise.

## Control Flow
Balloon control paths set a target, worker logic inflates/deflates toward it, and grant/DMA/users needing unpopulated pages call the allocation helpers. Initialization registers balloon machinery only when configured.

## State And Persistence
`balloon_stats` persists domain memory accounting and retry scheduling state. Allocated ballooned pages persist until returned through `xen_free_ballooned_pages()`.

## Dependencies And Integration Points
It integrates with Xen memory reservation hypercalls, Linux page allocation, memory hotplug/pressure behavior, grant table page allocation, and optional balloon driver configuration.

## Risks And Edge Cases
Incorrect accounting can leak pages or over-balloon the domain. Retry values and schedule delays must avoid livelock under memory pressure. Stub `xen_balloon_init()` means callers must tolerate disabled balloon support.

## Test Signals
Signals include target changes reflected in stats, successful page allocation/free cycles, stable behavior under low/high memory pressure, bounded retry scheduling, and no-op initialization when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/balloon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/events.h -->
# sources/distributed-fs/ceph-client/include/xen/events.h

## Purpose
This header declares Linux Xen event-channel APIs that bind Xen ports, VIRQ/IPI/PIRQ sources, and interdomain channels to Linux IRQs and handlers.

## Important APIs, Types, And Functions
- Binding APIs include `bind_evtchn_to_irq*`, `bind_evtchn_to_irqhandler*`, `bind_virq_to_irq*`, `bind_ipi_to_irqhandler()`, and interdomain late-EOI helpers.
- `unbind_from_irqhandler()` tears down IRQ bindings and closes the event channel.
- `xen_irq_lateeoi()` sends delayed EOI with `XEN_EOI_FLAG_SPURIOUS` where appropriate.
- Priority APIs map to FIFO event priorities.
- `evtchn_make_refcounted()`, `evtchn_get()`, and `evtchn_put()` manage userspace-exposed channel references.
- `notify_remote_via_evtchn()` sends `EVTCHNOP_send`; `notify_remote_via_irq()` maps from IRQ.
- Resume, pending/poll, callback vector, upcall, PIRQ/GSI/MSI, destroy, and debug interrupt APIs provide the rest of event lifecycle.
- `xen_evtchn_close()` closes a port and `BUG()`s on hypercall failure.
- `xen_fifo_events` reports FIFO ABI usage.

## Control Flow
Drivers bind a Xen port or virtual/physical interrupt to a Linux IRQ, optionally register a handler, receive upcalls through `xen_evtchn_do_upcall()`, notify peers via event sends, and unbind on teardown. Late-EOI channels require explicit `xen_irq_lateeoi()` after handling. Resume code rebinds or reconstructs event-channel state.

## State And Persistence
State is maintained by the Xen event subsystem: port-to-IRQ mappings, refcounts, IRQ priority, pending/masked bits in Xen shared structures, FIFO/2-level mode, and PIRQ/GSI/MSI allocations. The header declares interfaces only.

## Dependencies And Integration Points
It depends on Linux IRQ/MSI infrastructure, Xen event-channel public ABI, architecture hypercalls/events, Xenbus devices, PCI/MSI when enabled, and Xen callback/upcall setup.

## Risks And Edge Cases
Event-channel teardown must avoid use-after-close when userspace refcounts exist. Late EOI must not be omitted or events can stall. `xen_evtchn_close()` treats close failure as fatal. MSI/PIRQ paths require Dom0 privileges and correct sharing semantics.

## Test Signals
Signals include successful bind/unbind for evtchn/VIRQ/IPI/interdomain/PIRQ/MSI, delivery through handlers, late-EOI completion, pending poll behavior, remote notifications, resume rebinding, priority changes under FIFO mode, and refcounted userspace channels surviving expected lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/features.h -->
# sources/distributed-fs/ceph-client/include/xen/features.h

## Purpose
This header exposes Xen feature discovery state and a simple feature-test helper.

## Important APIs, Types, And Functions
- `xen_setup_features()` populates feature bits from Xen.
- `xen_features` stores `XENFEAT_NR_SUBMAPS * 32` feature bytes.
- `xen_feature(int flag)` returns the requested feature byte.

## Control Flow
Boot/setup code calls `xen_setup_features()`, and later code branches on `xen_feature(XENFEAT_*)` for mapping, DMA, event, and other behavior.

## State And Persistence
`xen_features` is persistent global feature state for the running domain.

## Dependencies And Integration Points
It depends on Xen public feature definitions. Consumers include SWIOTLB detection, PV/HVM feature gating, event channel setup, and memory mapping paths.

## Risks And Edge Cases
Callers must not query out-of-range flags. Feature state must be initialized before use or defaults can select the wrong compatibility path.

## Test Signals
Signals include populated feature arrays after Xen setup, correct branch decisions for direct/not-direct mapping, and stable behavior when older Xen versions omit newer bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/grant_table.h -->
# sources/distributed-fs/ceph-client/include/xen/grant_table.h

## Purpose
This header declares Linux Xen grant-table APIs for granting foreign domains access to local pages, mapping foreign grants, managing grant references, allocating grant pages, DMA grant allocation, batching map/copy operations, and iterating grant-sized chunks.

## Important APIs, Types, And Functions
- `INVALID_GRANT_REF`, `INVALID_GRANT_HANDLE`, and `NR_GRANT_FRAMES` define sentinel and initial shared-table sizing.
- `struct gnttab_free_callback` schedules callbacks when free grant references become available.
- `struct gntab_unmap_queue_data` describes asynchronous unmap work, callbacks, map arrays, pages, count, and age.
- Lifecycle APIs include `gnttab_init()`, optional suspend/resume, grant foreign access, ending/trying to end access, and freeing pages after access ends.
- Reference-pool APIs allocate, claim, release, free, and callback-wait for grant references or sequences.
- Mapping helpers `gnttab_set_map_op()` and `gnttab_set_unmap_op()` prepare ABI operations with PV/HVM host address differences.
- Architecture hooks map shared/status frames and auto-xlat frames.
- Page APIs allocate/free pages, manage page caches, mark grant pages private, map/unmap refs sync or async, and batch map/copy with retry of `GNTST_eagain`.
- `struct xen_page_foreign` stores foreign page origin in `page->private`.
- Iteration helpers split arbitrary page ranges into Xen page-sized grant chunks and count grants with `gnttab_count_grant()`.

## Control Flow
Granting flow allocates or claims references, grants a frame to a domain, hands out the ref, and later ends access only when the peer is no longer using it. Mapping flow builds map ops, performs hypercalls, sets foreign P2M mappings, uses returned handles/addresses, then unmaps synchronously or queues async unmap work. Batch operations retry transient paged-out grants until statuses settle.

## State And Persistence
Persistent state includes grant reference pools, shared/status grant tables, free callbacks, page caches, auto-xlat frames, page-private foreign metadata, asynchronous unmap queues, and hypervisor grant entries. Foreign access can outlive the API call until the remote domain releases it.

## Dependencies And Integration Points
It depends on Xen public grant ABI, Xen features/page helpers, architecture hypervisor/page mapping, Linux page flags, delayed work, spinlocks, DMA types, and optional grant DMA allocation. It integrates with Xenbus front/back drivers, net/block grants, balloon/unpopulated pages, DMA, and suspend/resume.

## Risks And Edge Cases
`gnttab_end_foreign_access()` may return before the peer stops accessing the page; pages cannot be reused until final release. Host address preparation differs for `GNTMAP_contains_pte`, PV, and HVM. Linux pages may contain multiple Xen grant chunks. Batch retry can wait up to about 32 seconds, so callers must account for latency. `page->private` storage differs by word size.

## Test Signals
Signals include correct grant allocation/free accounting, successful foreign access and revocation, map/unmap of local and foreign refs, async unmap callback completion, no page reuse while grants are active, batch retry handling for `GNTST_eagain`, correct grant counts for unaligned ranges, and suspend/resume restoration of shared tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/grant_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvc-console.h -->
# sources/distributed-fs/ceph-client/include/xen/hvc-console.h

## Purpose
This header exposes Xen HVC console boot/runtime console hooks and raw console output helpers.

## Important APIs, Types, And Functions
- `xenboot_console` is the boot console instance.
- Under `CONFIG_HVC_XEN`, `xen_console_resume()`, `xen_raw_console_write()`, and `xen_raw_printk()` are available.
- Without HVC Xen support, all helpers are inline no-ops, with `xen_raw_printk()` preserving printf format checking.

## Control Flow
Console code can write raw strings or formatted messages to the Xen console and resume console state after suspend. Non-HVC builds compile away the calls.

## State And Persistence
Console state is maintained by HVC/Xen console implementation, not this header. The boot console object persists externally.

## Dependencies And Integration Points
It integrates with Linux console infrastructure, Xen console backend/hypercalls, suspend/resume, and early boot logging.

## Risks And Edge Cases
Raw console writes may be used in fragile early/error paths, so format validation and no-op stubs are important. Callers must not assume output happens when `CONFIG_HVC_XEN` is disabled.

## Test Signals
Signals include visible early Xen console output, raw printk formatting, resume restoring console operation, and clean builds/behavior with HVC Xen disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvc-console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvm.h -->
# sources/distributed-fs/ceph-client/include/xen/hvm.h

## Purpose
This header provides small wrappers around Xen HVM parameter hypercalls and callback-vector setup.

## Important APIs, Types, And Functions
- `param_name()` maps known `HVM_PARAM_*` indices to names for logging and returns `reserved`/`unknown` for gaps/out-of-range values.
- `hvm_get_parameter()` fills `struct xen_hvm_param`, calls `HYPERVISOR_hvm_op(HVMOP_get_param)`, logs failures, and returns the value.
- `HVM_CALLBACK_VECTOR(x)` composes a vector callback descriptor using type `HVM_CALLBACK_VIA_TYPE_VECTOR` shifted into the high bits.
- `xen_setup_callback_vector()` and `xen_set_upcall_vector()` set callback vectors globally/per CPU.

## Control Flow
HVM setup calls `hvm_get_parameter()` for Xen-provided PFNs/event channels and callback configuration, then configures event upcalls through vector helpers. Errors are logged with parameter names.

## State And Persistence
No state is stored in the header. Hypervisor HVM parameters and callback vector registration persist in Xen/domain state.

## Dependencies And Integration Points
It depends on Xen HVM param ABI and ARM/x86 hypercall wrappers. Consumers include HVM boot, Xenstore/console setup, event callback setup, and per-CPU upcall configuration.

## Risks And Edge Cases
`param_name()` only lists a subset of parameters; newer indices log as reserved/unknown. Callers must handle negative hypercall returns. Callback vector composition uses high-bit type fields, so integer width must remain 64-bit.

## Test Signals
Signals include successful retrieval of store/console/callback parameters, meaningful error logs for invalid indices, callback vector setup on boot and CPU bring-up, and event upcalls delivered through the configured vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/callback.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/callback.h

## Purpose
This Xen public header defines callback registration ABI constants and structures for guest callback entry points.

## Important APIs, Types, And Functions
- `CALLBACKTYPE_*` values identify event, failsafe, syscall, deprecated sysenter, NMI, sysenter, and syscall32 callbacks, mostly x86-specific.
- `CALLBACKF_mask_events` requests event masking during callbacks where applicable.
- `CALLBACKOP_register` and `CALLBACKOP_unregister` select callback hypercall operations.
- `struct callback_register` contains type, flags, and `xen_callback_t address`.
- `struct callback_unregister` contains type and padding.

## Control Flow
Guest setup code builds a register or unregister structure and passes it to the Xen callback op hypercall. Xen then uses the registered callback address for event, failsafe, syscall, or NMI delivery.

## State And Persistence
Callback registrations persist in hypervisor domain state until changed, unregistered, or domain shutdown.

## Dependencies And Integration Points
It depends on `xen/interface/xen.h` for `xen_callback_t`. It integrates with architecture entry code, event delivery, NMI/syscall handling, and Xen callback hypercalls.

## Risks And Edge Cases
Some callbacks cannot be unregistered and can return `-EINVAL`. Several callback types are deprecated or architecture-specific; using them on unsupported hypervisor/guest combinations will fail. Event masking semantics do not apply uniformly.

## Test Signals
Signals include successful callback registration, event delivery through the registered address, expected `-EINVAL` on unsupported unregister/type attempts, and correct behavior with `CALLBACKF_mask_events`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/elfnote.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/elfnote.h

## Purpose
This Xen public header defines numeric ELF note types used by Xen loaders, guests, crash notes, and dump-core files.

## Important APIs, Types, And Functions
- Notes `XEN_ELFNOTE_INFO` through `XEN_ELFNOTE_PHYS32_RELOC` describe guest metadata such as entry address, hypercall page, virtual base, paddr offset, Xen version, guest OS/version, loader, PAE mode, feature strings, symbol table need, hypervisor hole low bound, L1 MFN masks, suspend cancellation, initial P2M, initrd mapping support, supported features, PVH 32-bit entry, and PVH relocation constraints.
- `XEN_ELFNOTE_MAX` tracks the highest regular note.
- Crash notes `XEN_ELFNOTE_CRASH_INFO` and `XEN_ELFNOTE_CRASH_REGS` identify kexec/kdump data.
- Dump-core notes identify Xen dump-core marker, header, Xen version, and format version.

## Control Flow
Build/link code emits notes into a PT_NOTE segment named `Xen`; Xen tooling and hypervisors parse them when loading or dumping guests. Runtime kernel code generally consumes the consequences rather than calling functions from this header.

## State And Persistence
Notes are persistent metadata embedded in ELF binaries or dump files. They inform hypervisor load decisions and crash/dump interpretation.

## Dependencies And Integration Points
It integrates with Xen domain builders, kernel linker scripts, PV/PVH boot protocols, kexec/kdump, dump-core tooling, and feature negotiation.

## Risks And Edge Cases
Incorrect numeric note values or malformed descriptors can make kernels unbootable under Xen. Some notes are x86-only, and legacy `__xen_guest` compatibility semantics differ from modern notes. PVH relocation constraints must match actual binary relocation ability.

## Test Signals
Signals include ELF note inspection showing expected `Xen` notes, successful Xen/PVH boot, correct feature negotiation on old and new Xen versions, usable kdump crash notes, and dump-core tools recognizing header/version notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/elfnote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/event_channel.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/event_channel.h

## Purpose
This Xen public header defines the event-channel hypercall ABI: port type, operation numbers, argument structures, status values, 2-level channel capacity, and FIFO event-channel layout.

## Important APIs, Types, And Functions
- `evtchn_port_t` is a 32-bit port identifier and has a guest-handle type.
- Operation structures cover allocate unbound, bind interdomain, bind VIRQ, bind PIRQ, bind IPI, close, send, status, bind VCPU, unmask, reset, FIFO control initialization, FIFO array expansion, and priority setting.
- `struct evtchn_status` reports channel state and associated remote domain/port, PIRQ, or VIRQ.
- `struct evtchn_op` is the legacy union wrapper for selected operations.
- `EVTCHN_2L_NR_CHANNELS` derives two-level ABI capacity from `xen_ulong_t`.
- FIFO constants define priorities, event-word bits (`PENDING`, `MASKED`, `LINKED`, `BUSY`), link width/mask, maximum channels, and `struct evtchn_fifo_control_block`.

## Control Flow
Guests allocate or bind ports, optionally bind them to VCPUs, unmask them, send notifications, query status, close/reset them, or initialize FIFO control pages. The Linux `xen/events.h` layer wraps these ABI structures in IRQ APIs.

## State And Persistence
Event-channel state persists in Xen: port allocation, channel type/status, remote endpoint, VCPU binding, mask/pending bits, FIFO queues, priorities, and control/array pages.

## Dependencies And Integration Points
It depends on Xen base types and guest handles. It is the shared ABI for Linux event handling, Xenbus, console, block/net front/back drivers, userspace event-channel devices, and hypervisor tooling.

## Risks And Edge Cases
Privilege restrictions apply to binding physical IRQs or querying other domains. VIRQ/IPI bindings are tied to VCPUs and cannot be moved like normal channels. FIFO setup requires correct page GFNs/offsets and link-bit handling. Closing interdomain channels changes the remote endpoint to unbound, which peers must handle.

## Test Signals
Signals include successful alloc/bind/send/close/status operations, VCPU binding behavior, reset closing channels, FIFO control initialization and priority delivery, correct status transitions, and permission failures for unprivileged cross-domain/PIRQ operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/event_channel.h -->
