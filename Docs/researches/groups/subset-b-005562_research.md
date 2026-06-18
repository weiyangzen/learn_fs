# subset-b-005562 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_accel.c

Purpose: implements accelerated fbdev drawing for the Intel i810/i815 framebuffer. It wraps the i810 instruction ring and exposes `i810fb_fillrect`, `i810fb_copyarea`, `i810fb_imageblit`, `i810fb_sync`, `i810fb_load_front`, and `i810fb_init_ringbuffer` to the main driver.

Important APIs and functions: `wait_for_space()` polls the ring head against `par->cur_tail`, marks `LOCKUP`, and downgrades pixmap alignment on timeout. `wait_for_engine_idle()` flushes ring space then waits on `INSTDONE`. `begin_iring()`, `PUT_RING`, and `end_iring()` are the core command submission path. `source_copy_blit()`, `color_blit()`, and `mono_src_copy_imm_blit()` emit BLT packets for copies, fills, and 1bpp text/image expansion. `i810fb_iring_enable()` toggles the ring enable bit after `flush_cache()`.

Control flow: fb_ops callbacks validate acceleration is enabled, no lockup occurred, and depth is not 32bpp (`par->depth == 4`) before using hardware. Otherwise they fall back to `cfb_*`. Copy direction is adjusted for overlapping regions. Image blits only accelerate 1bpp glyph data and compute padded DWORD payload size before embedding bitmap data in the ring. Panning updates `DPLYBASE` directly when acceleration is disabled or via a parser/front-buffer command when active.

State and persistence: persistent state is in `struct i810fb_par`: `cur_tail`, `iring`, `fb`, `pitch`, `depth`, `blit_bpp`, `dev_flags`, and mapped MMIO. Lockups persist by setting `LOCKUP`, preventing future acceleration until mode/device reinitialization.

Dependencies and integration: depends on `i810_regs.h`, `i810.h`, `i810_main.h`, fbdev software helpers, MMIO accessors, and x86 `flush_cache()` when available. `i810_main.c` wires these functions into `fb_ops` and initializes AGP-backed ring memory.

Risks: polling has fixed retry counts and no scheduling delay; hardware stalls can burn CPU and permanently disable acceleration. Address arithmetic uses `fix.smem_start` physical offsets and assumes validated geometry. Ring space accounting must remain consistent with packet sizes. `mono_src_copy_imm_blit()` casts image data to `u32 *`, so caller padding/alignment assumptions matter.

Test signals: exercise fill/copy/image paths with acceleration on/off, 8/16/24/32 bpp, overlapping copy directions, y-pan, lockup fallback, and `fb_sync()`. Hardware or emulator tests should verify ring head/tail programming and that software fallback still renders after forced timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_dvt.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_dvt.c

Purpose: provides discrete, table-driven video timings for i810 when VESA GTF support is not selected. It maps supported resolutions/refreshes to complete VGA, PLL, watermark, and sync register values.

Important APIs and data: `std_modes[]` is the core table of `struct mode_registers` values for 640x480 through 1600x1200 at selected refresh rates. `round_off_xres()` clamps requested horizontal resolution to supported buckets. `round_off_yres()` derives 4:3 vertical resolution. `i810fb_find_best_mode()` chooses a table row by horizontal display register and nearest pixel clock not exceeding the request. `i810fb_encode_registers()`, `i810fb_fill_var_timings()`, and `i810_get_watermark()` are consumed by `i810_main.c`.

Control flow: check-var first rounds modes, then `i810fb_fill_var_timings()` converts the selected table entry back into fb_var margins, sync length, pixclock, and sync polarity. Set-par later calls `i810fb_encode_registers()` to copy the chosen table entry into `par->regs` and compute overlay active extents. Watermark selection is a simple lookup from the chosen table entry by memory frequency and bpp.

State and persistence: no dynamic storage is owned here. The file writes into `fb_var_screeninfo` and `i810fb_par->regs`, `ovract`, and watermarks selected elsewhere.

Dependencies and integration: depends on `i810.h` for `struct mode_registers` and `struct i810fb_par`, on `i810_regs.h` for register semantics, and on the main driver for validation, PLL programming, and register load.

Risks: supported modes are limited to table entries and 4:3 rounding, so unusual panels and custom timings are rejected or silently coerced. `i810fb_find_best_mode()` leaves `diff` unchanged for entries above the requested pixel clock, so selection behavior depends on table ordering. Sync polarity code uses bitwise complement tests that are easy to misread and should be regression tested.

Test signals: verify each supported mode round-trips from var to register table and back, check memory-frequency watermark selection for 100 and 133 MHz paths, and validate fallback behavior for requests between supported resolutions or refreshes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_dvt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_gtf.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_gtf.c

Purpose: implements non-discrete timing generation for i810 when `CONFIG_FB_I810_GTF` is enabled. Unlike `i810_dvt.c`, this file computes CRT/VGA register fields from fbdev timing values and uses separate FIFO watermark tables.

Important APIs and data: watermark tables `i810_wm_*_{100,133}` map pixel frequencies to FIFO control values for 8/16/24 bpp at 100 or 133 MHz memory. `round_off_xres()` and `round_off_yres()` are no-ops in GTF mode, leaving mode selection to fbdev modelist/GTF validation. `i810fb_encode_registers()` converts `fb_var_screeninfo` into CRTC, sync, blanking, interlace, double-scan, polarity, and overlay registers. `i810_get_watermark()` picks the nearest frequency entry.

Control flow: main check-var validates or synthesizes fb_var timings, then `decode_var()` calls `i810_calc_dclk()` in `i810_main.c`, followed by this file's `i810fb_encode_registers()`. Horizontal values are rounded to character clocks, blanking windows are constrained to 127-character ranges, vertical extension registers carry high bits, and sync polarity is encoded in `msr`.

State and persistence: stores derived state into `par->regs`, `par->interlace`, `par->ovract`, and later `par->watermark`. It reads the existing `CR11` register to preserve protected bits while writing the vertical retrace end low bits.

Dependencies and integration: depends on i810 MMIO read helpers, fbdev timing validation, and the main driver's later `i810_load_*()` register programming. It is selected mutually with DVT through `CONFIG_FB_I810_GTF`.

Risks: hardware register packing is dense and relies on valid, range-checked fb_var values. Division by very small pixclock values is protected by higher-level validation, not here. The nearest watermark algorithm can choose an entry above or below the real clock; display FIFO underrun testing is important at high bpp/high clock.

Test signals: use modelist and GTF-derived modes across bpp values, interlaced/doublescan rejection/encoding, polarity combinations, and pixel clocks near watermark table boundaries. Compare programmed register fields against known-good XFree86/i810 values where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_gtf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.c

Purpose: main PCI fbdev driver for Intel 810/815 integrated graphics. It probes PCI devices, allocates AGP aperture-backed framebuffer/ring/cursor memory, validates modes, programs VGA and i810 display registers, exposes fb_ops, handles color maps, panning, cursor, blanking, suspend/resume, and cleanup.

Important APIs and functions: PCI binding uses `i810fb_pci_tbl` and `i810fb_driver`. Hardware programming is split across `i810_load_pll()`, `i810_load_vga()`, `i810_load_vgax()`, `i810_load_2d()`, `i810_load_color()`, `i810_load_pitch()`, and `i810_load_regs()`. Save/restore paths mirror this through `i810_save_vga_state()` and `i810_restore_vga_state()`. Mode logic uses `i810_round_off()`, `i810_check_params()`, `decode_var()`, `encode_fix()`, and timing helpers from `i810_dvt.c` or `i810_gtf.c`. fb_ops include open/release, check/set var, setcolreg, blank, pan, accel callbacks, cursor, sync, and mmap/read/write defaults.

Control flow: probe removes conflicting apertures, allocates `fb_info`, maps PCI aperture/MMIO, initializes defaults from module parameters, allocates AGP memory, initializes hardware, discovers EDID/modelist when I2C is enabled, validates an initial mode, initializes the ring buffer, registers the framebuffer, and stores PCI drvdata. Set-par decodes var into `par`, loads registers, initializes cursor, updates fixed info, and enables hardware acceleration flags if allowed. Open saves VGA state on first user; release restores it on last close. Suspend blanks and unbinds AGP memory; resume re-enables PCI, rebinds AGP memory, and reprograms mode.

State and persistence: `struct i810fb_par` carries mapped resources, AGP allocations, saved VGA state, mode registers, pitch/depth, cursor memory, pseudo palette, open count under `open_lock`, power state, EDID, and resource flags. Module parameters persist requested defaults such as `vram`, `voffset`, `bpp`, sync ranges, acceleration, MTRR, direct color, and DDC bus selection.

Dependencies and integration: integrates with PCI, fbdev core, AGP backend, aperture arbitration, VGA save/restore helpers, I2C/DDC helpers when configured, architecture write-combining, and acceleration/timing files. It includes `i810_regs.h`, `i810.h`, and `i810_main.h`.

Risks: error unwinding depends on `res_flags` and partially initialized allocations; AGP bind failures can leak unless all paths are maintained carefully. Mode validation mutates user vars and can shrink virtual resolution. Register programming temporarily disables DRAM refresh, so ordering is safety critical. Cursor memory is AGP physical memory and has alignment assumptions. Open/release VGA restore can race with console/power transitions if locking assumptions change.

Test signals: PCI probe/remove fault injection, mode changes for 8/16/24/32 bpp, EDID and no-EDID boot, DVT vs GTF builds, acceleration lockup fallback, blanking states, pan offsets, hardware cursor updates, suspend/resume with AGP rebind, and resource cleanup under each probe failure label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.h

Purpose: shared interface header for the i810 fbdev implementation. It declares cross-file timing, acceleration, ring-buffer, front-buffer, and optional I2C/DDC helpers used by `i810_main.c`.

Important APIs: timing hooks are `round_off_xres()`, `round_off_yres()`, `i810_get_watermark()`, `i810fb_encode_registers()`, and `i810fb_fill_var_timings()`, supplied by either `i810_dvt.c` or `i810_gtf.c`. Acceleration hooks are `i810fb_fillrect()`, `i810fb_copyarea()`, `i810fb_imageblit()`, `i810fb_sync()`, `i810fb_init_ringbuffer()`, and `i810fb_load_front()`. Optional I2C hooks are real declarations under `CONFIG_FB_I810_I2C` and inline stubs otherwise.

Control flow and integration: the header defines the compile-time timing lane via `IS_DVT`: DVT when `CONFIG_FB_I810_GTF` is off, GTF otherwise. It also provides `flush_cache()` as an x86 `wbinvd` inline for ring enabling and a no-op elsewhere.

State and persistence: this header owns no runtime state, but it shapes which implementation files satisfy symbols and how missing I2C support behaves. The I2C stub returns failure (`1`), causing main initialization to continue without EDID.

Dependencies: expects `struct fb_var_screeninfo` from fbdev and `struct i810fb_par` from `i810.h` to be visible before use by including C files.

Risks: because DVT/GTF provide the same symbol names, build configuration must include exactly one suitable implementation. `flush_cache()` uses a heavy whole-cache writeback/invalidate on x86; any future call sites should remain rare and hardware-specific.

Test signals: compile both `CONFIG_FB_I810_GTF` and non-GTF builds, with and without `CONFIG_FB_I810_I2C`, and ensure all declared symbols resolve and mode initialization follows the intended path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_regs.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_regs.h

Purpose: central register-offset definition file for Intel 810/815 graphics controller, VGA, overlay, BLT, clock, cursor, memory, and interrupt registers used by the i810 framebuffer driver.

Important content: defines MMIO offsets such as `IRING`, `PGTBL_ER`, `INSTDONE`, `FW_BLC`, `DRAMCH`, GPIOs, `DCLK_*`, GTT, overlay registers, BLT status registers, display/cursor registers (`PIXCONF`, `BLTCNTL`, `DPLYBASE`, `CUR*`), plus VGA I/O register indexes for sequencer, graphics, CRT controller, attribute controller, DAC/CLUT, and miscellaneous output.

Control flow and integration: this file has no executable code. It is consumed by `i810_main.c`, `i810_accel.c`, `i810_dvt.c`, and `i810_gtf.c` through read/write helper macros in `i810.h`. Register names are used directly in mode load/save, acceleration diagnostics, ring-buffer setup, blanking, palette programming, and cursor control.

State and persistence: none directly. These constants define the persistent hardware state locations that the driver saves, modifies, and restores.

Dependencies: guarded by `__I810_REGS_H__` and derived from the Intel 810 PRM. It assumes callers know whether an offset is MMIO or VGA I/O space.

Risks: wrong offsets or bit grouping affect hardware globally. The header mixes legacy VGA I/O ports with graphics-controller MMIO offsets, so accidental use with the wrong accessor family can corrupt programming. Some names reflect old documentation and are terse, increasing maintenance risk.

Test signals: build coverage through all i810 source files; runtime validation via register dump comparison during mode set, blank/unblank, cursor enable, and ring-buffer initialization. Static review should verify any new register use matches the accessor width and MMIO/I/O namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/imsttfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/imsttfb.c

Purpose: PCI framebuffer driver for IMS TwinTurbo cards with IBM 624 or TI TVP3030 RAMDACs. It programs scan timing, RAMDAC PLL/pixel format, palette, panning, blanking, simple 2D acceleration, debug ioctls, and PCI resource lifecycle.

Important APIs and types: `struct imstt_regvals` stores timing and PLL values; `struct imstt_par` stores mapped device-controller registers, RAMDAC colormap registers, RAMDAC type, and pseudo palette. Mode helpers compute or select register values for IBM/TVP RAMDACs, then `set_imstt_regvals()` writes timing, refresh, stride, endian/byte-swap, and pixel format registers. fb_ops include check-var, set-par, setcolreg, pan, blank, fillrect, copyarea, imageblit fallback, ioctl, mmap/read/write defaults.

Control flow: probe removes conflicting apertures, allocates fb_info, reserves PCI BAR0, determines RAMDAC type from PCI id and Open Firmware name, maps framebuffer/MMIO/cmap windows, and calls `init_imstt()`. Initialization sizes VRAM, clears it, initializes RAMDAC registers, selects a default or PowerMac NVRAM mode, validates supported timing, sets fixed info, programs mode, allocates cmap, and registers fbdev. Mode setting validates bpp/resolution/virtual size, computes register values, selects RGB555/565, writes RAMDAC and controller registers, and updates pixclock.

State and persistence: persistent state includes hardware mappings, selected RAMDAC type, cached mode register values, pseudo palette, and fbdev cmap. Boot options can set inverse/font and PowerMac vmode/cmode in non-module builds.

Dependencies and integration: uses PCI, Open Firmware node lookup, fbdev core, PowerMac NVRAM/macmodes when configured, `aperture_remove_conflicting_pci_devices`, I/O accessors, and user copy helpers for private ioctls.

Risks: private ioctls expose raw register access to userspace and need privilege/context review. Busy-wait loops on BLT status have no timeout. `setclkMHz()` loops until exact integer MHz match for supported hard-coded modes. Probe error unwinding must match mappings. Endianness correction is hardware-specific and easy to regress on non-PowerPC.

Test signals: probe both TT128 and TT3D paths, IBM-vs-TVP register init, supported modes at 8/16/24/32 bpp, panning bounds, blank/unblank, accelerated fill/copy including overlap, ioctl bounds checks, PowerMac NVRAM defaults, and failure injection for each ioremap/register step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/imsttfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/imxfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/imxfb.c

Purpose: platform framebuffer driver for Freescale i.MX1/i.MX21 LCD controllers. It reads display timing from device tree, allocates DMA framebuffer memory, programs LCDC timing and pixel format registers, controls clocks/regulator-backed LCD power, and exposes basic fbdev operations.

Important APIs and types: `struct imx_fb_videomode` extends `fb_videomode` with `pcr`, `aus_mode`, and bpp. `struct imxfb_info` stores mapped registers, clocks, controller type, panel type, DMA buffer addresses, mode list, colormap behavior, LCDC register defaults, and LCD regulator state. Key functions are `imxfb_check_var()`, `imxfb_set_par()`, `imxfb_activate_var()`, `imxfb_enable_controller()`, `imxfb_disable_controller()`, DT parsing in `imxfb_of_read_mode()`, LCD ops, probe/remove, and PM suspend/resume.

Control flow: probe sets up fb_info, parses one native display phandle, computes framebuffer size, acquires clocks, briefly toggles `ipg` to reset an already-running controller, maps registers, allocates write-combined DMA memory, adds the videomode, initializes var/fix/cmap, registers an LCD device, registers framebuffer, and enables the controller. Check-var ignores arbitrary requested modes and forces the native DT mode, computes the pixel clock divider from `clk_per`, selects RGB bitfields and panel type from PCR bits, and stores `fbi->pcr`/`lauscr`. Set-par updates visual, line length, palette size, and writes LCDC timing registers.

State and persistence: runtime state is in `imxfb_info`, including `enabled`, `lcd_pwr_enabled`, cached PCR/PWMR/LSCR/DMACR/LAUSCR values, DMA address, and DT colormap flags. `fb_mode` is a file-static boot option but is reset during probe after fb_info initialization.

Dependencies and integration: uses platform/of matching, `of_get_fb_videomode`, clocks `ipg`/`ahb`/`per`, DMA API, regulator consumer API, LCD class, fbdev core, and PM helpers.

Risks: only one native DT mode is supported, so mode switching is intentionally constrained. The pixel-clock divisor warns and clamps when requested clock is too high. Power regulation is separate from controller enable; consumers may expect LCD power ops to be called. DEBUG_VAR logs invalid ranges but does not fail. The 32 bpp path advertises 24-bit fields for 18-bit hardware compatibility.

Test signals: DT parse success/failure, bpp 8/16/32 on i.MX1 vs i.MX21, PCR divider boundary conditions, static/inverse/grayscale cmap flags, regulator enable/disable, suspend/resume, blank/unblank, DMA allocation failure, and clock acquisition/enable failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/imxfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/Makefile

Purpose: Kbuild fragment for the Kyro framebuffer driver.

Important content: `obj-$(CONFIG_FB_KYRO) += kyrofb.o` enables the module/built-in object when the config symbol is selected. `kyrofb-objs` composes the final object from `STG4000Ramdac.o`, `STG4000VTG.o`, `STG4000OverlayDevice.o`, `STG4000InitDevice.o`, and `fbdev.o`.

Control flow and integration: build order ensures the public functions declared in `STG4000Interface.h` and called from `fbdev.c` are linked into one `kyrofb` driver. The object list makes the STG4000 helper files private implementation units of the driver rather than independent modules.

State and persistence: no runtime state.

Dependencies: requires `CONFIG_FB_KYRO` and the surrounding kernel Kbuild system. All listed object names must match source files in the same directory.

Risks: missing a helper object causes link failures for RAMDAC, VTG, overlay, or core PLL symbols. Adding new Kyro helper files requires updating this list.

Test signals: `make drivers/video/fbdev/kyro/` or a kernel build with `CONFIG_FB_KYRO=m/y` should compile and link `kyrofb.o` without unresolved STG4000 symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000InitDevice.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000InitDevice.c

Purpose: low-level STG4000/Kyro initialization support. It programs SDRAM timings, computes PLL divider values, resets major hardware blocks, and sets the core clock through PCI configuration space.

Important APIs and functions: `InitSDRAMRegisters()` selects SDRAM arbiter/config/refresh values from subsystem id memory type and chip speed bits plus PCI revision. `ProgramClock()` searches PLL feedback/pre-divider/output-divider combinations for a requested clock within about 0.4 percent and returns the chosen clock plus F/R/P fields. `SetCoreClockPLL()` masks interrupts, disables core threads, resets register/TA blocks, initializes SDRAM, computes the 100 MHz core PLL, writes staged PLL mode words through PCI config register `0x70`, and finally asserts a broad software reset.

Control flow: `fbdev.c` calls `SetCoreClockPLL()` during probe and remove. The sequence depends on `pSTGReg` register macros and `pci_read/write_config_word()`. The PLL write sequence uses long busy-loop delays between config writes to satisfy hardware timing.

State and persistence: hardware state includes SDRAM controller registers, software reset bits, thread enables, interrupt mask, TA configuration, and PCI core PLL config. Static `CorePllControl` defines the PCI config offset.

Dependencies and integration: includes `STG4000Reg.h` for register layout/macros and `STG4000Interface.h` for exported declarations. Uses PCI subsystem id/revision to infer RAM properties.

Risks: delay loops are CPU-speed dependent and not sleepable. `ProgramClock()` assumes requested values in specific units and mutates output pointers only on success. Bad subsystem id returns `-EINVAL`, but caller currently does not strongly propagate/display all failure details. Reset sequencing is hardware-critical and can blank or destabilize the card.

Test signals: validate PLL output for known target clocks, subsystem id memory-type matrix, PCI config write ordering, failure on invalid memory/chip-speed indexes, and probe/remove behavior on real STG4000 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000InitDevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Interface.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Interface.h

Purpose: internal interface header connecting Kyro fbdev front-end code with STG4000 RAMDAC, timing generator, core PLL, and overlay helper implementation files.

Important APIs: declares `InitialiseRamdac()`, `DisableRamdacOutput()`, `EnableRamdacOutput()`, `DisableVGA()`, `StopVTG()`, `StartVTG()`, `SetupVTG()`, `ProgramClock()`, `SetCoreClockPLL()`, `ResetOverlayRegisters()`, `CreateOverlaySurface()`, `SetOverlayBlendMode()`, `SetOverlayViewPort()`, and `EnableOverlayPlane()`.

Control flow and integration: `fbdev.c` calls these helpers during mode set, overlay ioctl handling, probe, and remove. The helpers take `volatile STG4000REG __iomem *` and, for timing, `struct kyrofb_info` from `<video/kyro.h>`.

State and persistence: no state is declared here, but the interfaces expose hardware programming that mutates RAMDAC, VTG, PLL, overlay, and stream-control registers.

Dependencies: includes Linux PCI definitions and `<video/kyro.h>`, and expects `STG4000REG` plus overlay enums from `STG4000Reg.h` to be visible in including translation units before function use.

Risks: all functions are global within the linked object, with no namespace prefix beyond descriptive names. Unit contracts are implicit: pixel clocks, widths, offsets, and polarities must use the units expected by each helper. Overlay APIs rely on prior `CreateOverlaySurface()` state maintained inside `STG4000OverlayDevice.c`.

Test signals: compile-link coverage for `CONFIG_FB_KYRO`; mode set should call RAMDAC/VTG helpers in order; overlay ioctls should fail before surface creation and succeed after valid creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000OverlayDevice.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000OverlayDevice.c

Purpose: programs STG4000 video overlay surfaces, scaling/decimation, blending, viewport, and overlay enable registers for the Kyro framebuffer driver's private overlay ioctls.

Important APIs and data: `ResetOverlayRegisters()` disables/clears overlay address, size, decimation, pixel format, scaling, and blend mode. `CreateOverlaySurface()` validates dimensions, calculates linear or planar strides, writes Y/U/V addresses, stores static overlay dimensions/stride/format, and returns byte strides. `SetOverlayBlendMode()` programs graphics, color key, alpha, and combined modes. `SetOverlayViewPort()` calculates source/destination clipping, vertical decimation, horizontal decimation/scaling, line-store stride, overlay size, window start/end, pixel-format excess pixels, and scaler registers. `EnableOverlayPlane()` turns on overlay stream bits.

Control flow: `fbdev.c` first calls `ResetOverlayRegisters()` during each video mode set. Overlay create ioctl calls `CreateOverlaySurface()` once per mode and then default global alpha blend. Viewport ioctl disables RAMDAC output, calls `SetOverlayViewPort()`, enables overlay plane, and re-enables output.

State and persistence: file-static `ovlWidth`, `ovlHeight`, `ovlStride`, and `ovlLinear` persist the last created overlay and are required by viewport programming. Device-wide offsets and returned strides are kept in `fbdev.c`'s `deviceInfo`.

Dependencies and integration: uses `STG4000Reg.h` read/write/bit macros and overlay blend enums. It assumes framebuffer memory layout is managed by the caller and that overlay offsets are already aligned sufficiently.

Risks: static overlay state makes the implementation effectively single-device/single-overlay. Planar UV size expression `(inWidth + 1 / 2)` is suspicious because integer precedence makes `1 / 2` zero. Scaling math has many divisions and boundary cases; some invalid viewport cases are rejected by caller, but not all. Hardware comments note uncertain blend semantics.

Test signals: valid/invalid overlay dimensions, linear and planar stride/UV offset calculations, one-overlay-only behavior, viewport zero/underflow rejection, downscale/upscale cases, alpha/color-key modes, and visual verification of YUV alignment and clipping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000OverlayDevice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Ramdac.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Ramdac.c

Purpose: configures the STG4000 RAMDAC for primary display mode, pixel format, stride, pixel PLL, cursor defaults, video window defaults, burst control, CRC trigger, digital video port, and stream output enable/disable.

Important APIs: `InitialiseRamdac()` accepts display depth, width, height, sync polarities, and an in/out pixel clock pointer. It supports 16 and 32 bpp, computes physical pixel depth, primary surface size using a 128-bit pixel bus, calls `ProgramClock()` to choose DAC PLL fields, writes `DACPLLMode`, clears primary/cursor/video-window/border/CRC/video-port registers, and sets burst control. `DisableRamdacOutput()` and `EnableRamdacOutput()` clear/set graphics stream bit 0 in `DACStreamCtrl`.

Control flow: mode setting in `fbdev.c` stops VTG/output, disables VGA, calls `InitialiseRamdac()`, sets VTG timings, resets overlay, then enables RAMDAC and starts VTG.

State and persistence: changes persistent DAC pixel format, primary size/address, PLL mode, cursor address/control, video window, border color, burst control, CRC trigger, digital video port, and stream control. `*pixelClock` is overwritten with the actual clock returned by PLL search.

Dependencies and integration: depends on `ProgramClock()` from `STG4000InitDevice.c`, register layout/macros in `STG4000Reg.h`, and `kyrofb_info` timing flow in `fbdev.c`.

Risks: only 16/32 bpp are accepted; callers must reject other depths. Width must be compatible with bus-divisor math or primary size fields can underflow/truncate. Sync polarity arguments are accepted but not used in this function; polarity is handled in VTG setup. PLL failure handling depends on `ProgramClock()` returning nonzero valid fields.

Test signals: mode set at all accepted depths and common widths, actual pixel clock feedback, stream disable/enable state, cursor disabled by default, and failure for unsupported bpp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Ramdac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Reg.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Reg.h

Purpose: STG4000 register map and bit-manipulation support for the Kyro framebuffer driver.

Important content: defines `STG_WRITE_REG()` and `STG_READ_REG()` around `writel/readl`, bit helpers `SET_BIT`, `CLEAR_BIT`, and range-clearing macros, enums for LUT use, primary pixel formats, overlay blend modes, and overlay pixel formats, plus the large `STG4000REG` struct mapping device registers and reserved gaps from thread/core controls through TA/3D/SDRAM and DAC/overlay/video-port registers.

Control flow and integration: all STG4000 helper C files take a local parameter named `pSTGReg`, allowing the register macros to expand directly. `fbdev.c` maps PCI BAR1 to `STG4000REG __iomem *` and passes it into helper functions.

State and persistence: no software state, but this struct defines the persistent MMIO register address space used for resets, PLL programming, RAMDAC setup, VTG timing, overlay, stream control, SDRAM config, and interrupts.

Dependencies: kernel builds include `<asm/page.h>` and `<asm/io.h>` for MMIO access. The macros assume a visible variable `tmp` for clear operations, which is a non-obvious local naming contract in callers.

Risks: C bitfield-clearing macros loop over bit indexes and mutate `tmp` or `usTemp` by name, making them fragile and side-effect prone. The register struct must match hardware offsets exactly; padding errors corrupt all downstream accesses. `volatile` plus `__iomem` typing is old style and limits static checking.

Test signals: compile all helpers with sparse where possible, compare `offsetof(STG4000REG, member)` against hardware documentation for critical registers, and smoke-test mode set/overlay paths that cover DAC, VTG, PLL, and SDRAM fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000VTG.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000VTG.c

Purpose: controls STG4000 VGA reset and DAC video timing generator (VTG) start/stop and timing register programming.

Important APIs: `DisableVGA()` toggles the VGA reset bit in `SoftwareReset` with a short busy delay. `StopVTG()` sets horizontal/vertical sync generator stop bits and clears enable bit 31 in `DACSyncCtrl`. `StartVTG()` sets bit 31 and clears stop bits. `SetupVTG()` translates `struct kyrofb_info` timing fields into horizontal and vertical DAC timing registers and sync polarity bits.

Control flow: called from Kyro mode set after RAMDAC/output shutdown. `SetupVTG()` calculates display start, borders, front/back porch starts, total counts, and special margins for 640x480 at 60/72 Hz, then writes `DACHorTim1-3`, `DACVerTim1-3`, and `DACSyncCtrl`.

State and persistence: mutates `SoftwareReset`, `DACSyncCtrl`, and DAC timing registers. It does not cache software state.

Dependencies and integration: relies on `struct kyrofb_info` fields populated by `kyrofb_set_par()` in `fbdev.c` and register macros from `STG4000Reg.h`.

Risks: polarity comments contain at least one duplicated/mismatched description, so behavior should be verified against real sync polarity expectations. Border math assumes valid totals and porch values. Busy delay is fixed and CPU-speed dependent. No explicit validation is done inside `SetupVTG()`.

Test signals: mode set across `kyro_modedb`, especially 640x480 special cases, all sync polarity combinations, VTG stop/start sequencing during blank mode changes, and register dumps for total/display/front/back timing fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000VTG.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/fbdev.c

Purpose: fbdev-facing PCI driver for STG4000/Kyro/PowerVR3 graphics. It owns PCI probing, framebuffer registration, mode database, fb_ops, color pseudo-palette, private overlay ioctls, write-combining, and calls lower-level STG4000 helper files for hardware programming.

Important APIs and types: static `kyro_fix`/`kyro_var` provide defaults. `kyro_modedb[]` lists supported VESA-like modes. `device_info_t` holds the mapped register base and overlay allocation offsets/strides; `deviceInfo` is global. fb_ops include check-var, set-par, setcolreg, ioctl, and default IO memory ops. Private ioctl commands come from `<video/kyro.h>`.

Control flow: probe removes conflicting apertures, enables PCI, requests BARs, allocates fb_info, maps MMIO and framebuffer, enables write-combining unless disabled, sets panning/wrapping steps, calls `SetCoreClockPLL()`, selects a mode via `fb_find_mode()`, allocates cmap, programs mode with `kyrofb_set_par()`, clears framebuffer memory, registers fbdev, and stores drvdata. Set-par derives Kyro timing fields from fb_var, calls `kyro_dev_video_mode_set()`, updates line length and visual. Mode set stops VTG/RAMDAC, disables VGA, initializes RAMDAC, sets VTG, resets overlay, and restarts output. Ioctls create overlay, set viewport, or return overlay offsets/strides.

State and persistence: per-fb `struct kyrofb_info` stores timing and pseudo-palette. Global `deviceInfo` stores register pointer and overlay allocation state, so this driver effectively assumes one card. Module/boot options control mode, panning, wrapping, and MTRR/write-combining.

Dependencies and integration: uses PCI managed region helpers, fbdev core, aperture arbitration, architecture WC API, user copy helpers, and the STG4000 interface. It depends on `<video/kyro.h>` for `struct kyrofb_info` and ioctl payloads.

Risks: global `deviceInfo` is not multi-device safe. `deviceInfo.ulNextFreeVidMem` uses `xres*yres*bits_per_pixel` without dividing bpp by 8, overestimating primary memory and affecting overlay placement. Probe failure path returns `-EINVAL` for many resource failures, obscuring root cause. `SetCoreClockPLL()` return is ignored. No remove-time devm unmap is needed, but framebuffer release order must stay compatible with registered fbdev state.

Test signals: probe/remove, mode database selection and fallback, 16/32 bpp checks, line length, panning/wrap options, overlay ioctl create/view/stride/offset paths, multi-card static-state analysis, and failure injection for mapping/register_framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/leo.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/leo.c

Purpose: Open Firmware platform framebuffer driver for Sun LEO/SX graphics on SBUS-style systems. It maps the LEO register/framebuffer windows, initializes window IDs and draw engine state, exposes fbdev color/blank/pan operations, and delegates SBUS mmap/ioctl handling.

Important APIs and types: hardware structs model cursor, LX kernel command register, LC/LD register banks, SS1 misc, and `struct leo_par` caches mapped register pointers, CLUT data, extent, flags, and IO-space id. fb_ops are built with `FB_DEFAULT_SBUS_OPS(leo)`, plus `leo_setcolreg()`, `leo_blank()`, and `leo_pan_display()`. Private helpers include `leo_wait()`, `leo_switch_from_graph()`, `leo_wid_put()`, `leo_init_wids()`, `leo_init_hw()`, and `leo_unmap_regs()`.

Control flow: probe allocates fb_info, reads OF geometry through `sbusfb_fill_var()`, maps LC/LD/LX/cursor/framebuffer regions at fixed offsets, initializes WIDs, programs hardware to a cfb-compatible state, unblanks, allocates cmap, initializes fixed info, registers framebuffer, and stores drvdata. `leo_pan_display()` is mainly a hook to recover from graphics mode; it rejects nonzero offsets/modes. `leo_setcolreg()` updates cached CLUT data, writes all 256 CLUT entries through LX command registers, then triggers update bits. Blanking toggles `LEO_KRN_CSR_ENABLE`.

State and persistence: `leo_par` persists mapped windows, the 256-entry CLUT cache, current extent, blank flag, and OF IO flags. Hardware WID/CLUT/cursor state is initialized at probe and may be reasserted when panning back from graphics mode.

Dependencies and integration: uses OF platform matching name `SUNW,leo`, `sbuslib` helpers for var filling, mmap, and ioctl, SBUS read/write accessors, fbdev core, and `<asm/fbio.h>` constants. `leo_mmap_map[]` exposes multiple hardware regions to userspace according to Sun fb mappings.

Risks: register polling waits up to 0.3 seconds under spinlock in color/WID paths, which can create latency. Color updates rewrite the whole CLUT for every entry change. Fixed offsets and mappings assume exact LEO hardware layout. `leo_switch_from_graph()` performs substantial engine programming during pan. Only no-offset panning is supported.

Test signals: OF probe with expected resources, mmap offset translation, FBIO ioctl helper behavior, color map updates, blank/unblank, pan with zero and nonzero offsets, graphics-to-console recovery, WID initialization, and cleanup after partial mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/leo.c -->
