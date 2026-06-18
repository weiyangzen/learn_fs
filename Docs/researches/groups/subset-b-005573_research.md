# subset-b-005573 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/s3c-fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/s3c-fb.c

Purpose: implements the Samsung S3C/S3C2443 framebuffer platform driver for FIMD-style LCD controllers. It exposes one fbdev instance per configured hardware window, allocates DMA-backed framebuffer memory for each window, programs RGB panel timing, and provides palette, blanking, panning, and VSYNC wait support.

Important APIs/types/functions: core state is split between `struct s3c_fb` for the controller, `struct s3c_fb_win` for per-window fbdev state, variant descriptors `struct s3c_fb_variant` and `struct s3c_fb_win_variant`, and `struct s3c_fb_vsync`. The fbdev entry points are `s3c_fb_check_var`, `s3c_fb_set_par`, `s3c_fb_setcolreg`, `s3c_fb_blank`, `s3c_fb_pan_display`, and `s3c_fb_ioctl`; platform lifecycle is `s3c_fb_probe`, `s3c_fb_remove`, suspend/resume, and runtime PM hooks. Helpers such as `s3c_fb_calc_pixclk`, `s3c_fb_set_rgb_timing`, `shadow_protect_win`, and `s3c_fb_update_palette` translate fbdev state to hardware registers.

Control flow: probe obtains platform data, clocks, MMIO, and IRQ; configures GPIO and VIDCON polarity; clears all windows; programs timing; then probes each platform-enabled window. Window probe allocates a `fb_info`, DMA write-combined scanout memory, palette storage, default mode, cmap, and registers the framebuffer. Mode setting protects shadow registers, disables the window, enables output if needed, writes buffer start/end/stride and OSD geometry, selects WINCON bpp/burst/swap bits, sets color-key and blend configuration, and then unprotects the shadow registers. Panning only rewrites buffer start/end offsets. `FBIO_WAITFORVSYNC` enables a one-shot frame interrupt and waits on a queue with a 50 ms timeout.

State and persistence: persistent state lives in `platform_set_drvdata`, the controller register block, `enabled` and `output_on` flags, per-window palette buffers, pseudo palettes, and DMA framebuffer allocations. Runtime PM brackets register access and output enablement; system resume reconstructs timing, color-key state, and each window by rerunning `s3c_fb_set_par`.

Dependencies and integration: depends on fbdev core, DMA mapping, platform data from `linux/platform_data/video_s3c.h`, Samsung FIMD register definitions from `video/samsung_fimd.h`, clocks named `lcd` and sometimes `sclk_fimd`, platform IRQs, and CONFIG_FB_S3C build integration.

Risks: platform data is mandatory and many callbacks/fields are assumed valid. `pm_runtime_get_sync` return values are ignored. Palette updates directly toggle `WPALCON_PAL_UPDATE`, so races with active scanout are mitigated only by the hardware update bit. Error paths in window probe can return before freeing partially allocated fb_info or DMA memory. Register programming is variant-sensitive; wrong offsets or bpp masks can corrupt unrelated windows. VSYNC IRQ handling disables interrupts after every event, so missed wakeups or timeout behavior are important.

Test signals: boot/probe on supported S3C2443/S3C64xx boards, framebuffer registration for each configured window, mode changes across 1/2/4/8/16/18/19/24/25/28 bpp where supported, panning with x/y offsets, cmap updates, `FBIO_WAITFORVSYNC` timeout and success paths, suspend/resume, runtime PM blank/unblank, and teardown with multiple windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/s3c-fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/s3fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/s3fb.c

Purpose: implements a PCI fbdev driver for legacy S3 Trio and ViRGE VGA adapters. It maps PCI framebuffer memory, identifies chip variants, programs VGA/S3 extended timing registers and PLLs, supports palette and pseudo-palette color, and optionally exposes DDC through bit-banged I2C.

Important APIs/types/functions: `struct s3fb_info` stores chip ID, revision, MCLK, saved VGA state, open count, pseudo palette, and optional DDC adapter/MMIO state. The fbdev entry points are `s3fb_open`, `s3fb_release`, `s3fb_check_var`, `s3fb_set_par`, `s3fb_setcolreg`, `s3fb_blank`, `s3fb_pan_display`, `s3fb_get_caps`, plus custom image/fill helpers for packed and interleaved 4 bpp. PCI lifecycle is `s3_pci_probe`, `s3_pci_remove`, suspend/resume, `s3fb_init`, and `s3fb_cleanup`.

Control flow: init parses module or boot options and registers the PCI driver unless modesetting is disabled. Probe rejects non-primary VGA devices, removes conflicting apertures, enables PCI, requests regions, maps BAR0 write-combined, determines the VGA I/O base, unlocks S3 registers, identifies undecided chips, derives VRAM and MCLK from CRTC/sequencer registers, optionally sets up DDC and EDID modes, chooses a mode, sizes virtual Y for scrolling, allocates a cmap, registers fbdev, and optionally registers a write-combine MTRR. `set_par` unlocks VGA/S3 registers, blanks the display, programs default VGA state, S3 linear framebuffer and timing extensions, mode-specific CR/SR bits, PLL, timings, DTPC, clears visible memory, and re-enables output.

State and persistence: open/release save and restore VGA mode/fonts/cmap around active users using `open_lock` and `ref_count`. Persistent runtime state includes mapped framebuffer, screen size, chip identity, DDC adapter registration, pseudo palette, and `wc_cookie`. Suspend only powers down when the framebuffer is open; resume unlocks registers, restores power bits, reprograms mode, and clears fb suspend.

Dependencies and integration: uses fbdev, PCI, aperture arbitration, `linux/svga.h` helpers, VGA register access from `video/vga.h`, console locking for PM, optional `CONFIG_FB_S3_DDC` I2C bit-banging, and optional MTRR/write-combining.

Risks: this driver directly manipulates global VGA legacy resources and explicitly lacks VGA arbitration beyond ignoring secondary devices. Many mode-setting paths are chip-specific magic values. Some accelerated 4 bpp helpers assume 8-pixel alignment and only fall back when wrappers detect unsupported shapes. `pci_disable_device` is intentionally commented out. `FBIOGTYPE` is not present; users rely on standard fbdev ops. DDC MMIO mapping uses framebuffer base plus a fixed offset and must match the chip.

Test signals: probe/remove on each PCI ID family, primary-vs-secondary VGA behavior, EDID and fallback mode selection, mode setting for text/1/2/4/8/16/24/32 bpp with chip-specific 24/32 restrictions, palette writes, panning, blank levels, open/release VGA restoration, suspend/resume while open and closed, and 4 bpp image/fill alignment fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/s3fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sa1100fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sa1100fb.c

Purpose: implements the StrongARM SA1100/SA1110 LCD controller fbdev platform driver. It consumes board-specific `sa1100fb_mach_info`, allocates DMA scanout memory, programs LCD controller timing and DMA base registers, manages palette placement, and sequences LCD/backlight power.

Important APIs/types/functions: fbdev operations are `sa1100fb_check_var`, `sa1100fb_set_par`, `sa1100fb_setcolreg`, `sa1100fb_blank`, and `sa1100fb_mmap`. Controller programming centers on `sa1100fb_activate_var`, `sa1100fb_enable_controller`, `sa1100fb_disable_controller`, `set_ctrlr_state`, `sa1100fb_task`, and optional `sa1100fb_freq_transition`. Probe setup is split between `sa1100fb_init_fbinfo`, `sa1100fb_map_video_memory`, and `sa1100fb_probe`.

Control flow: probe validates platform LCD data and IRQ, allocates private state, maps registers, gets the LCD clock, requests IRQ, obtains an optional Shannon LCD-enable GPIO, allocates one DMA write-combined region, initializes var/fix defaults from platform data, checks bitfields, registers the framebuffer, and optionally registers a cpufreq notifier. `set_par` sets visual and line length, locates the palette at the end of the hidden first DMA page, calls any board visual hook, and calculates shadow LCCR/DBAR values. Actual enable/disable work is deferred through `sa1100fb_schedule_work` so blanking and re-enable requests run in task context.

State and persistence: `struct sa1100fb_info` persists fbdev state, controller shadows (`reg_lccr0` through `reg_lccr3`, `dbar1`, `dbar2`), palette and framebuffer DMA addresses, controller state, pending task state, waitqueue, mutex, board hooks, clock, and pseudo palette. The DMA allocation reserves the first page for palette data and exposes framebuffer memory after that page; mmap adjusts offsets to skip the palette page.

Dependencies and integration: depends on fbdev, DMA mapping, SA1100 machine headers/register macros, platform data in `video/sa1100fb.h`, board callbacks for power/backlight/visual selection, cpufreq notifiers when enabled, GPIO descriptors for optional Shannon hardware, platform IRQs, and a platform driver named `sa11x0-fb`.

Risks: `sa1100fb_init_fbinfo` panics on invalid platform timing fields, so bad board data is fatal. The driver comment says it cannot be unloaded; there is no remove path. Direct GPDR/GAFR manipulation bypasses generic GPIO abstractions for LCD data pins. Disable waits only about 20 ms for LCD done and does not explicitly test timeout status. CPU-frequency and blanking transitions share state and rely on the custom collapse rules in `sa1100fb_schedule_work`.

Test signals: probe with valid board data, invalid LCCR3/pixclock platform data, 4/8/16 bpp checks, cmap updates including inverse and grayscale, mmap of framebuffer and MMIO regions, blank/unblank state collapse, IRQ wake on LCD done, suspend/resume, cpufreq pre/post changes, and board power/backlight callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sa1100fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sa1100fb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sa1100fb.h

Purpose: private header for the SA1100 framebuffer driver. It defines LCD controller register offsets, the controller register shadow structure, the driver's private state layout, controller state-machine constants, and minimum supported resolutions.

Important APIs/types/functions: `struct sa1100fb_lcd_reg` groups the four LCCR shadow values. `struct sa1100fb_info` embeds `struct fb_info` and carries device, RGB descriptors, MMIO base, optional GPIO, DMA mapping fields, palette pointers, DBAR shadows, LCCR shadows, controller/task state, locking, waitqueue, work item, optional cpufreq notifier, board info pointer, clock, and pseudo palette. `TO_INF` converts embedded members back to private state. Constants `C_DISABLE`, `C_ENABLE`, `C_DISABLE_CLKCHANGE`, `C_ENABLE_CLKCHANGE`, `C_REENABLE`, `C_DISABLE_PM`, `C_ENABLE_PM`, and `C_STARTUP` encode the state machine used by `set_ctrlr_state`.

Control flow: this file has no executable control flow, but its constants directly determine register access in `sa1100fb.c`: `LCCR0`, `LCSR`, `DBAR1`, `DBAR2`, `LCCR1`, `LCCR2`, and `LCCR3` offsets are added to the mapped register base, while the `C_*` values drive deferred work transitions for blanking, PM, and clock changes.

State and persistence: documents the persistent storage contract for the driver. The first DMA page/palette location, framebuffer DMA address, LCCR shadow values, pending work state, and board-specific hooks all live in `struct sa1100fb_info` for the lifetime of the platform device.

Dependencies and integration: depends on declarations from the public SA1100 fb platform-data header for `struct sa1100fb_rgb`, `NR_RGB`, and `struct sa1100fb_mach_info`, plus kernel types such as `struct fb_info`, `struct clk`, `struct work_struct`, `wait_queue_head_t`, `struct mutex`, and optional `struct notifier_block`.

Risks: because this is a private layout embedded in `fb_info`, any change must match all `container_of` users in the C file. State constants are raw integers, so accidental reordering changes behavior. Register offsets assume SA1100 LCDC layout and should not be reused for other controllers.

Test signals: compile coverage for SA1100 fbdev, structure field use under CONFIG_CPU_FREQ on and off, and runtime validation of all state transitions that consume the `C_*` constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sa1100fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/Makefile

Purpose: Kbuild fragment for the S3 Savage framebuffer driver. It declares the composite `savagefb.o` object and conditionally includes optional I2C/DDC and acceleration implementation files.

Important APIs/types/functions: the important build symbols are `CONFIG_FB_SAVAGE`, `CONFIG_FB_SAVAGE_I2C`, and `CONFIG_FB_SAVAGE_ACCEL`. `savagefb-y` always includes `savagefb_driver.o`; `savagefb-$(CONFIG_FB_SAVAGE_I2C)` adds `savagefb-i2c.o`; `savagefb-$(CONFIG_FB_SAVAGE_ACCEL)` adds `savagefb_accel.o`.

Control flow: there is no runtime flow. Kbuild links only the selected objects into `savagefb.o`, which means functions declared in `savagefb.h` are either provided by optional objects or compiled out by preprocessor fallbacks in the main driver/header.

State and persistence: no runtime state. The persistent effect is the build-time composition of driver capabilities.

Dependencies and integration: included from the fbdev build tree when `drivers/video/fbdev/Makefile` descends into the Savage directory. It relies on Kconfig selecting optional I2C and acceleration symbols consistently with preprocessor guards in the C sources.

Risks: if Kconfig allows code paths that call optional symbols without the corresponding object, link failures would occur; this is partly mitigated by `#if defined(CONFIG_FB_SAVAGE_I2C)` blocks and non-accel fallbacks. The object order makes the main driver the base unit.

Test signals: kernel builds with `CONFIG_FB_SAVAGE` alone, with I2C only, with acceleration only, with both options, and with the driver disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb-i2c.c

Purpose: optional DDC2/I2C support for the S3 Savage fbdev driver. It creates a bit-banged I2C adapter over chip-specific GPIO/DDC registers and reads monitor EDID for mode selection.

Important APIs/types/functions: exported-to-driver helpers are `savagefb_create_i2c_busses`, `savagefb_delete_i2c_busses`, and `savagefb_probe_i2c_connector`. GPIO algorithms are split between `savage4_gpio_setscl/setsda/getscl/getsda` for MMIO-style registers and `prosavage_gpio_setscl/setsda/getscl/getsda` for VGA CRTC-register style DDC. `savage_setup_i2c_bus` fills `struct i2c_adapter` and `struct i2c_algo_bit_data`.

Control flow: bus creation stores `par` in `par->chan`, selects a DDC register and bit callbacks by chipset, raises SCL/SDA, and registers the bit-bang adapter. Savage4 may choose `CR_SERIAL2` instead of `CR_SERIAL1` based on revision and CR A6. EDID probing first uses `fb_ddc_read` if the adapter exists, then falls back to firmware EDID via `fb_firmware_edid`. Delete unregisters the adapter if it was registered and clears `chan.par`.

State and persistence: adapter state persists in `struct savagefb_par.chan` for the lifetime of the framebuffer. The I2C callbacks mutate hardware DDC output bits and read input bits from either MMIO or VGA register space; no EDID is cached in this file.

Dependencies and integration: depends on `CONFIG_FB_SAVAGE_I2C`, I2C bit algorithm support, fbdev DDC helpers, PCI device parentage, MMIO established by the main driver, and register helpers/macros from `savagefb.h`.

Risks: `strcpy` copies the adapter name without a local bounds check, relying on the passed string size. Bit operations are not protected by a bus-specific hardware lock beyond I2C core serialization. Unsupported chips silently leave `chan.par = NULL`, so callers must tolerate no EDID. Chip register selection is hardware-specific and easy to regress.

Test signals: builds with I2C enabled, adapter registration logs for Savage4/ProSavage/Twister/Savage2000, EDID read success and firmware fallback, clean adapter deletion on probe failure/remove, and mode selection changes in the main driver based on EDID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb.h

Purpose: shared private header for the S3 Savage fbdev driver. It defines PCI IDs, chipset group helpers, MMIO/BCI constants, display-type tags, timing/register snapshots, the driver's private state, VGA/MMIO accessors, optional acceleration stubs, and cross-file function prototypes.

Important APIs/types/functions: `savage_chipset` classifies hardware families. `struct xtimings` holds derived mode timing. `struct savage_reg` stores VGA, S3 extended, streams, and MIU register snapshots for mode programming and restore. `struct savagefb_i2c_chan` stores the optional DDC adapter. `struct savagefb_par` is the persistent per-device state used by all Savage source files. Inline helpers such as `savage_in/out*`, `vga_in/out*`, `VGArCR`, `VGAwCR`, `VGAenablePalette`, and `VerticalRetraceWait` centralize register access.

Control flow: this header does not own a runtime sequence, but its inline helpers are the primitive operations used by probe, mode setting, acceleration, blanking, and I2C. `BCI_SEND` advances `par->bci_ptr` while writing command words, so acceleration control flow depends on resetting `bci_ptr` before command emission.

State and persistence: `struct savagefb_par` persists PCI device pointer, chipset, DDC channel, current/saved/initial register snapshots, VGA state for open/release restore, open count, PM state, display type, clocks, mapped video/MMIO resources, BCI command buffer pointers, wait callbacks, panel dimensions, software palette cache, current depth, and virtual width.

Dependencies and integration: included by `savagefb_driver.c`, `savagefb-i2c.c`, and `savagefb_accel.c`. It depends on Linux I2C, mutex, VGA, fbdev EDID support, MMIO accessors, and Kconfig symbols `CONFIG_FB_SAVAGE_ACCEL` and `SAVAGEFB_DEBUG`.

Risks: macros perform unguarded MMIO writes and some, like `BCI_SEND`, have side effects. `vga_in32` returns `u8` despite using `savage_in32`, which is suspicious if ever used for 32-bit data. Busy-wait loops in `VerticalRetraceWait` and wait callbacks can hang on broken hardware. The header couples optional modules tightly to the exact private structure layout.

Test signals: compile all Savage configurations, run mode setting and acceleration paths that exercise BCI macros, I2C paths that use `struct savagefb_i2c_chan`, PM/open-release restore using register snapshots, and static analysis for inline type mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_accel.c

Purpose: optional hardware acceleration implementation for Savage fbdev. It emits BCI 2D commands for synchronization, rectangle copy, solid fill, and 1 bpp monochrome image blits.

Important APIs/types/functions: exported fbdev callbacks are `savagefb_sync`, `savagefb_copyarea`, `savagefb_fillrect`, and `savagefb_imageblit`. `savagefb_rop` maps fbdev ROP_COPY/ROP_XOR to hardware ROP codes. The code relies on `BCI_SEND`, `BCI_CMD_*`, `BCI_X_Y`, `BCI_W_H`, `BCI_CLIP_LR`, and the chipset-specific `SavageWaitIdle`/`SavageWaitFifo` callbacks initialized by the main driver.

Control flow: each operation exits early for zero-sized work. Copy computes direction bits and adjusts source/destination corners for overlap-safe copies, waits for four FIFO slots, and sends source, destination, and size. Fill resolves the color through pseudo_palette for truecolor modes, sets ROP and solid-source command bits, waits for FIFO space, and sends color/location/size. Imageblit falls back to `cfb_imageblit` unless depth is 1, computes foreground/background colors, rounds width to 32 pixels, waits for all command/data words, and streams the bitmap data.

State and persistence: no independent state is allocated. Operations mutate hardware command FIFO and `par->bci_ptr`; persistent acceleration parameters such as depth, virtual width, BCI base, and wait callbacks live in `struct savagefb_par`.

Dependencies and integration: built only with `CONFIG_FB_SAVAGE_ACCEL` and selected by `savagefb_ops` in the main driver. Requires the main driver's `SavageSetup2DEngine` to have configured BCI, global bitmap descriptor, clipping, and wait functions.

Risks: FIFO wait requests are based on calculated command sizes; incorrect size can overflow the BCI FIFO. `rect->rop` indexes `savagefb_rop` without local bounds checking, relying on fbdev callers to pass valid ROP values. `image->data` is cast to `u32 *`, so alignment and padding assumptions matter. Busy-waiting on broken hardware can stall the caller.

Test signals: accelerated console scroll/copy, fillrect with COPY and XOR, truecolor and pseudocolor fills, monochrome font/image blits with non-32-pixel widths, fallback for non-1bpp image data, and `fb_sync` waiting for idle after command submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_driver.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_driver.c

Purpose: main PCI fbdev driver for S3 Savage adapters. It handles PCI probe/remove, MMIO and framebuffer mapping, chip/VRAM/panel detection, mode validation and register programming, palette handling, panning/blanking, optional acceleration setup, optional EDID-assisted mode selection, and power management.

Important APIs/types/functions: fbdev operations are `savagefb_open`, `savagefb_release`, `savagefb_check_var`, `savagefb_set_par`, `savagefb_setcolreg`, `savagefb_pan_display`, and `savagefb_blank`. Hardware programming is built around `vgaHWInit`, `savagefb_decode_var`, `savagefb_set_par_int`, `savage_get_default_par`, `savage_set_default_par`, `SavageCalcClock`, `common_calc_clock`, `savage_init_hw`, `savage_map_mmio`, and `savage_map_video`. PCI and module lifecycle is `savagefb_probe`, `savagefb_remove`, PM hooks, `savagefb_init`, and `savage_done`.

Control flow: init parses `savagefb` options and registers the PCI driver. Probe removes conflicting apertures, allocates fb_info/private state, enables PCI and regions, initializes fb_info and chipset wait callbacks, maps MMIO, detects and resets hardware, maps VRAM, optionally reads EDID, chooses a default/panel/EDID/user mode, maximizes virtual Y, clamps virtual dimensions for acceleration, validates mode, computes sync frequencies, registers the framebuffer, and stores driver data. Mode setting decodes fb var into a `savage_reg` snapshot, chooses DAC limits, waits for idle, protects VGA sequencing, writes generic VGA registers, extended timing, PLL and memory registers, re-enables streams at retrace, sets up BCI if enabled, restores cmap, and updates fix fields.

State and persistence: persistent state is in `struct savagefb_par`: chip family, mapped MMIO and video regions, write-combine cookie, register snapshots, open count, PM state, display type, clocks, panel limits, BCI state, and palette cache. Open/release saves/restores VGA and Savage registers around active users. Suspend stores PM state, optionally blanks/powers down and restores saved registers; resume re-enables MMIO, reinitializes hardware, and reapplies the mode.

Dependencies and integration: depends on PCI, fbdev, aperture conflict removal, console locking for PM, VGA/MMIO helpers from `savagefb.h`, optional `CONFIG_FB_SAVAGE_I2C` EDID support, optional `CONFIG_FB_SAVAGE_ACCEL`, and PCI IDs for Savage3D/4/2000/MX/IX/ProSavage/Twister/SuperSavage families.

Risks: the driver is dominated by hardware magic values and busy-wait loops without timeouts. `savagefb_release` decrements `open_count` without guarding against zero. Probe error cleanup calls `fb_alloc_cmap(&info->cmap, 0, 0)` where deallocation would be expected. Several comments mark incomplete validation, untested paths, and hardware workarounds. Mode validation may shrink real resolution instead of failing when VRAM is insufficient. MMIO disable appears to set the enable bit for Savage4+ rather than clearing it, which deserves caution before changes.

Test signals: PCI probe/remove for each ID class, MMIO/VRAM mapping resource choices, EDID/user/default/panel mode selection, 8/16/32 bpp validation and programming, LCD panel limit rejection, panning x/y offsets, palette and pseudo_palette updates, acceleration on/off builds, open/release save/restore, suspend/resume/hibernate/freeze paths, and failure injection for each probe cleanup label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.c

Purpose: helper library for SPARC SBUS framebuffer drivers. It provides common fb var initialization from Open Firmware properties, mmap mapping through SBUS physical/IOSPACE descriptors, native SPARC fb ioctls, and compat ioctl translation for 32-bit user space.

Important APIs/types/functions: exported helpers are `sbusfb_fill_var`, `sbusfb_mmap_helper`, `sbusfb_ioctl_helper`, and, under CONFIG_COMPAT, `sbusfb_compat_ioctl`. `sbusfb_mmapsize` interprets positive map sizes, `SBUS_MMAP_EMPTY`, and negative framebuffer-size multipliers. The ioctl helper handles `FBIOGTYPE`, `FBIOPUTCMAP_SPARC`, and `FBIOGETCMAP_SPARC`.

Control flow: `sbusfb_fill_var` zeroes var and fills dimensions from OF `width`/`height` properties with 1152x900 defaults. `sbusfb_mmap_helper` validates shared mapping, computes requested offset, marks the VMA decrypted and noncached, walks requested pages, finds matching map entries by virtual offset, computes SBUS PFNs with `MK_IOSPACE_PFN`, and remaps each segment. Native colormap ioctls copy index/count/user pointers, convert between 8-bit SPARC cmap components and fbdev 16-bit components, and call `fb_set_cmap` or copy from `info->cmap`. Compat ioctl either forwards simple commands to the driver's native ioctl or translates 32-bit cmap structures.

State and persistence: no private persistent state. It reads OF properties, uses caller-owned map tables and fb_info cmap state, and mutates user-visible mappings or color maps through core fbdev helpers.

Dependencies and integration: used by SBUS fbdev drivers via exported symbols and the `FB_DEFAULT_SBUS_OPS` macros in `sbuslib.h`. Depends on SPARC fb ioctl definitions from `asm/fbio.h`, Open Firmware property access, memory remapping primitives, user access helpers, and CONFIG_COMPAT for 32-bit translations.

Risks: mmap silently skips pages that do not match any map entry and still returns success if no remap fails, so callers must provide complete maps. The `FBIOGTYPE` path writes `fb_cmsize` twice, first zero and then `fb_size`, which looks intentional or historical but is surprising. User pointer validation is per-access. Map size arithmetic depends on sentinel values and negative multipliers.

Test signals: SBUS framebuffer mmap with multiple map entries, unmatched offsets, invalid non-shared VMAs, native SPARC cmap get/put bounds checks, compat cmap get/put from 32-bit processes, and exported-symbol build coverage for CONFIG_COMPAT on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.h

Purpose: public-private interface for SBUS framebuffer helper routines. It declares the SBUS mmap table shape, mmap sentinel constants, exported helper prototypes, compat ioctl prototype, and convenience macros for initializing `struct fb_ops` in SBUS drivers.

Important APIs/types/functions: `struct sbus_mmap_map` maps a user-visible offset (`voff`) to physical offset (`poff`) and size. `SBUS_MMAP_FBSIZE(n)` encodes sizes as multiples of framebuffer size, while `SBUS_MMAP_EMPTY` marks empty entries. Function declarations cover var initialization, mmap helper, ioctl helper, and compat ioctl. `FB_DEFAULT_SBUS_OPS(prefix)` expands to fb read/write, cfb drawing, prefixed ioctl/mmap callbacks, and optional compat ioctl.

Control flow: no runtime flow exists here. The macros determine which function pointers an SBUS driver's `fb_ops` receives at compile time. Under CONFIG_COMPAT, ioctl macro expansion includes `.fb_compat_ioctl = sbusfb_compat_ioctl`; otherwise only the native prefixed ioctl is assigned.

State and persistence: no direct state. The map table structure describes persistent static tables normally owned by individual SBUS framebuffer drivers, and the macros encode a standard operations contract.

Dependencies and integration: consumed by SPARC/SBUS fbdev drivers and implemented by `sbuslib.c`. It assumes fbdev core drawing helpers (`fb_io_read`, `fb_io_write`, `cfb_fillrect`, `cfb_copyarea`, `cfb_imageblit`) are available wherever the macros are used.

Risks: macro expansion requires drivers to define functions named `prefix_sbusfb_ioctl` and `prefix_sbusfb_mmap`; mismatches become compile errors. Size sentinels rely on unsigned/negative conversion conventions that must match `sbusfb_mmapsize`. Using default cfb drawing may be inappropriate for unusual framebuffer layouts unless the driver overrides it.

Test signals: compile SBUS drivers with and without CONFIG_COMPAT, verify macro-generated fb_ops fields point to the expected prefixed functions, and mmap tables using positive, empty, and framebuffer-relative sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sbuslib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sh7760fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sh7760fb.c

Purpose: platform fbdev driver for the SH7760/SH7763 integrated LCD controller. It programs panel timing from platform data, allocates DMA-coherent framebuffer memory that satisfies LCDC address constraints, handles blank/unblank power sequencing, and provides truecolor pseudo-palette support.

Important APIs/types/functions: private state is `struct sh7760fb_par`, containing MMIO base, IRQ, platform display data, framebuffer DMA address, rotation flag, pseudo palette, device/resource pointers, and a VSYNC completion. fbdev operations are `sh7760fb_blank`, `sh7760fb_check_var`, `sh7760_setcolreg`, and `sh7760fb_set_par`; lifecycle helpers are `sh7760fb_alloc_mem`, `sh7760fb_free_mem`, `sh7760fb_probe`, and `sh7760fb_remove`.

Control flow: probe validates MMIO resource and platform data, allocates fb_info/private state, reserves and maps MMIO, disables LCD interrupts, optionally requests the IRQ then disables it, copies default mode to `info->var`, allocates framebuffer memory, initializes fixed RGB565 bitfields and cmap, sets `LDCNTR_DON2`, registers the framebuffer, and stores driver data. `set_par` derives horizontal/vertical counters from the default mode, validates color format from `lddfr`, handles optional rotation and endian bit, powers down the LCDC, writes clock/polarity/depth/power/timing/stride/start-address registers, computes DSTN lower-half address if needed, updates line_length and var, then unblanks the panel.

State and persistence: platform data drives all fixed hardware choices (`lddfr`, `ldmtr`, `ldickr`, power registers, default mode, rotation, blank callback). Framebuffer memory is DMA coherent and stored in `screen_base`, `screen_size`, and `par->fbdma`; hardware start-address registers persist until reprogrammed. `par->rot` records whether rotation survived validation.

Dependencies and integration: depends on `asm/sh7760fb.h` for register offsets, bit definitions, DMA mask, and platform data; fbdev core; DMA coherent allocation; platform resources; optional IRQ completion; and the platform driver name `sh7760-lcdc`.

Risks: comments mark rotation, grayscale, and DSTN paths as untested. The IRQ completion is initialized only by zeroed allocation and the IRQ is disabled after request, so VSYNC infrastructure is effectively unused by fb_ops. `fix.smem_start` is set to the CPU virtual `screen_base` rather than `par->fbdma`, which is unusual for fbdev. DMA address mask validation is SH-specific and can reject otherwise valid allocations. `check_var` performs minimal validation and forces bpp from platform register settings.

Test signals: probe/remove with valid and missing platform data, DMA allocation below/above required address mask, set_par for each `LDDFR_*` depth, blank/unblank power-state wait and timeout, platform blank callback ordering, rotation with xres <= 320 and > 320, RGB565 pseudo-palette writes, and DSTN lower-address calculation if hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sh7760fb.c -->
