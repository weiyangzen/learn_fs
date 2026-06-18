# Research Report: subset-b-005432

This grouped report covers the requested staging driver files in source-tree order. Each section preserves the source path in its title and is bounded by the reconciliation markers required for splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_reg.h -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_reg.h

Purpose: this header is the SM750/SM750LE register map used by the staging framebuffer driver and the DDK helper layer. It contains no executable logic; its role is to provide register offsets, masks, shifts, and symbolic field values for MMIO programming through `peek32()`/`poke32()` and related helpers.

Important definitions: the file starts with SM750LE 2D engine state registers (`DE_STATE1`, `DE_STATE2`) and generic system control definitions (`SYSTEM_CTRL`, `MISC_CTRL`, GPIO mux/data/direction, interrupt status/mask, clock gates, power mode, PLL controls). It defines panel display registers (`PANEL_DISPLAY_CTRL`, framebuffer address/width/window/timing registers, palette RAM, panel cursor registers), video/alpha overlay registers, CRT display and cursor registers, color-space conversion registers, hardware I2C registers, ZV capture blocks, DMA registers, and SM750LE-specific GPIO and display control offsets. The final `DEFAULT_I2C_SCL` and `DEFAULT_I2C_SDA` values are duplicated with `ddk750_swi2c.h` for the software I2C implementation.

Control flow and state: because this file is declarative, state is represented indirectly through hardware register fields. Consumers combine masks with values to preserve unrelated bits during read-modify-write operations. Persistent state lives in device registers and video memory, not in this header. The naming convention usually encodes block, register, field, and value, which is important because many fields share bit positions across panel and CRT blocks.

Dependencies and integration points: all macros rely on Linux `BIT()` being available through included driver headers. `sm750_hw.c`, `ddk750_chip.c`, `ddk750_display.c`, `ddk750_mode.c`, `ddk750_power.c`, `ddk750_swi2c.c`, and the cursor/accel code use these offsets to program MMIO. The SM750LE GPIO/I2C definitions are used by software I2C for DVI chip setup during hardware initialization.

Risks: the header mixes generic SM750, SM750LE, validation-chip, and old compatibility definitions, so incorrect chip-type checks can write legal-looking values to the wrong register semantics. Some mask names encode hardware widths but not value validation; callers must bound x/y dimensions, pitches, and memory offsets. Duplicated I2C defaults increase drift risk. Since this is a staging driver register map, any typo in an offset or mask causes hardware-visible corruption that normal unit tests will not catch.

Test signals: useful evidence is build coverage for all consumers, successful probe and mode-set on SM750 and SM750LE hardware, register trace comparison against vendor programming sequences, cursor/palette/blanking behavior, and software I2C access to the expected DVI device. Static checks should look for missing masks in read-modify-write paths and field values written without clearing existing masked bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.c -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.c

Purpose: this file implements a bit-banged I2C master over SM750 GPIO pins. It is used during SM750LE hardware initialization to configure an external DVI transmitter such as CH7301 when present.

Important APIs and functions: exported-to-driver functions are `sm750_sw_i2c_init()`, `sm750_sw_i2c_read_reg()`, and `sm750_sw_i2c_write_reg()`. Internal helpers are `sw_i2c_wait()`, `sw_i2c_scl()`, `sw_i2c_sda()`, `sw_i2c_read_sda()`, `sw_i2c_start()`, `sw_i2c_stop()`, `sw_i2c_write_byte()`, `sw_i2c_read_byte()`, `sw_i2c_ack()`, and the SM750LE-specific `sm750le_i2c_init()`.

Control flow: initialization validates GPIO numbers, chooses normal SM750 GPIO mux/data/direction registers or SM750LE data/direction registers, configures the pins as GPIO, enables GPIO power for non-LE chips, then sends repeated stop sequences to clear the bus. Write transfers issue start, device address, register index, data, and stop; each byte waits for an ACK by releasing SDA, clocking SCL, and polling SDA low with a retry loop. Read transfers write the target register index, issue a repeated start, send the read address, read one byte, and stop.

State and persistence: GPIO pin numbers and register offsets are module-global static variables. The bus electrical state persists in hardware GPIO direction/data registers, using open-drain behavior by driving low for zero and switching to input for high. No Linux I2C adapter is registered, so there is no bus locking outside this file.

Dependencies and integration points: depends on `ddk750_chip.h` for `peek32()`/`poke32()` and chip type, `ddk750_reg.h` for GPIO register definitions, `ddk750_power.h` for `sm750_enable_gpio()`, and `ddk750_swi2c.h` for public prototypes. `hw_sm750_inithw()` initializes GPIO 0/1 on SM750LE and probes/writes CH7301 registers through this API.

Risks: `sw_i2c_read_sda()` uses a suspicious comparison `(gpio_dir & dir_mask) != ~dir_mask`, which is effectively always true for normal masks and forces input each read; behavior works as a release operation but the condition is misleading. `sw_i2c_ack()` is a no-op, so multi-byte reads would not send real ACK/NACK sequencing. There is no external locking around global pin state or transfers. Timing is a CPU loop rather than calibrated delays. Read operations ignore ACK failures from address/register writes, returning whatever byte is sampled.

Test signals: CH7301 detection and configuration on SM750LE hardware is the primary runtime signal. Additional tests should include bus analyzer traces for start/stop/ACK timing, forced no-ACK behavior, probe across normal SM750 and SM750LE register sets, and suspend/resume validation because comments mention earlier timing/read problems after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.h -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.h

Purpose: this header exposes the software I2C helper API for the SM750 DDK layer and defines the default GPIO pins used for SCL and SDA.

Important APIs: `sm750_sw_i2c_init(clk_gpio, data_gpio)` initializes GPIO-backed bit-banged I2C; `sm750_sw_i2c_read_reg(addr, reg)` reads one register from an I2C slave; `sm750_sw_i2c_write_reg(addr, reg, data)` writes one slave register. `DEFAULT_I2C_SCL` and `DEFAULT_I2C_SDA` default to GPIO 30 and 31.

Control flow and state: the header does not store state, but its API controls static state in `ddk750_swi2c.c` for selected GPIO pins and register-bank offsets. Consumers call init before read/write; the implementation does not enforce that contract except through whatever values the static defaults currently hold.

Dependencies and integration points: included by `ddk750_swi2c.c` and indirectly used from SM750 hardware initialization. It is part of the staging framebuffer driver's private DDK interface rather than Linux's I2C subsystem.

Risks: the default GPIO definitions are duplicated in `ddk750_reg.h`, and the API takes raw 8-bit addresses/registers without documenting whether `addr` is a shifted 8-bit address or a 7-bit address. The header exposes no locking or adapter object, so concurrent users would share a single implicit bus configuration.

Test signals: build coverage is enough for syntax; behavioral signals come from `ddk750_swi2c.c` tests, especially verifying that callers use shifted addresses consistently and call initialization with valid pins before transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_swi2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750.c -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750.c

Purpose: this is the PCI framebuffer driver entry point for Silicon Motion SM750. It registers `sm750fb`, parses module/boot options, maps the device, initializes hardware, creates one or two framebuffer devices, and implements the Linux `fb_ops` callbacks for mode setting, colormap, blanking, panning, acceleration, and hardware cursor.

Important APIs and functions: module lifecycle is `lynxfb_init()`/`lynxfb_exit()` around a `pci_driver` with `lynxfb_pci_probe()` and `lynxfb_pci_remove()`. Framebuffer setup is handled by `sm750fb_setup()`, `sm750fb_framebuffer_alloc()`, `sm750fb_framebuffer_release()`, `sm750fb_set_drv()`, and `lynxfb_set_fbinfo()`. Fbdev callbacks include `lynxfb_ops_check_var()`, `lynxfb_ops_set_par()`, `lynxfb_ops_setcolreg()`, `lynxfb_ops_blank()`, `lynxfb_ops_pan_display()`, `lynxfb_ops_fillrect()`, `lynxfb_ops_copyarea()`, `lynxfb_ops_imageblit()`, and `lynxfb_ops_cursor()`. Suspend/resume callbacks call fbdev suspend handling and reinitialize hardware.

Control flow: probe removes conflicting apertures, enables the PCI device, allocates `struct sm750_dev`, hooks acceleration functions unless disabled, parses SM750-specific options, maps MMIO/VRAM through `hw_sm750_map()`, optionally adds write-combining with `arch_phys_wc_add()`, clears VRAM, stores drvdata, initializes hardware, and registers framebuffer instances based on the dual-view option. Each framebuffer receives a CRTC/output mapping based on dataflow, cursor memory at the end of its video memory partition, selected fbops with or without acceleration/cursor, a mode from the extended/VESA databases, fix/var metadata, and a colormap.

State and persistence: global module state includes `g_hwcursor`, `g_noaccel`, `g_nomtrr`, `g_fbmode[]`, `g_settings`, `g_dualview`, and `g_option`. Per-device state lives in `struct sm750_dev`, including PCI identity, mapped registers/memory, acceleration hooks, framebuffer count, MTRR handle, init parameters, panel type, dataflow, and spinlock. Per-framebuffer state lives in `struct lynxfb_par`, CRTC/output structures, pseudo palette, and cursor fields. Hardware-visible state includes mode registers, display routing, palette RAM, cursor memory, and 2D engine registers.

Dependencies and integration points: depends on Linux PCI, fbdev, aperture conflict handling, console locking, MTRR/write-combining, and the SM750 helper files. It calls `hw_sm750_*` functions for device mapping, mode, blanking, panning, palette, and acceleration setup. Accelerated fbops call `sm750_accel.c` via function pointers; cursor fbops call `sm750_cursor.c`.

Risks: option parsing uses colon-separated strings even though the module description example uses commas. `g_hwcursor` is global but used for both heads as a bitmask and also as a boolean when selecting fbops. Dual-view memory is split by halving `vidmem_size`, with comments noting offset/padding limitations. `lynxfb_set_fbinfo()` calls `lynxfb_ops_check_var()` at exit but ignores its return. Accelerated operations use a device spinlock but call MMIO routines that can busy-wait, which can increase interrupt latency. Remove always deletes the MTRR handle and unmaps resources but BAR0 was not requested in `hw_sm750_map()`, only BAR1 was requested.

Test signals: probe/remove on SM750 and SM750LE, single and dual framebuffer registration, boot/module option parsing, VESA and extended modes, 8/16/32 bpp validation, cursor enable/disable and shape updates, accelerated fill/copy/mono blits, panning, blanking, suspend/resume, and repeated load/unload under console activity are important. Static checks should cover unchecked return paths and global option lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750.h -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750.h

Purpose: this private header defines the core data model shared by the SM750 framebuffer files, along with constants, enums, and prototypes for the hardware abstraction layer.

Important types and definitions: `FB_ACCEL_SMI` identifies the accelerator. Default chip clocks are `DEFAULT_SM750_CHIP_CLOCK` and `DEFAULT_SM750LE_CHIP_CLOCK`. Enums describe panel type (`sm750_24TFT`, `sm750_dualTFT`, `sm750_doubleTFT`), display dataflow, CRTC channel, and output paths. `struct init_status` mirrors hardware init parameters. `struct lynx_accel` stores MMIO bases and 2D function pointers. `struct sm750_dev` is the per-PCI-device object. `struct lynx_cursor`, `struct lynxfb_crtc`, `struct lynxfb_output`, and `struct lynxfb_par` define per-framebuffer display state.

Control flow and state: the header establishes the contracts consumed by `sm750.c` and `sm750_hw.c`: fbdev setup fills `lynxfb_par`, mode setting passes CRTC/output pointers to `hw_sm750_*`, and acceleration is dispatched through `lynx_accel` function pointers. `ps_to_hz()` converts fbdev picosecond pixel clocks to Hz for timing programming.

Dependencies and integration points: relies on Linux fbdev, PCI, IO memory, and `do_div()`. Prototypes declared here are implemented in `sm750_hw.c`, while acceleration and cursor functions are declared in their own headers. The structures are private to the driver and not part of a stable external ABI.

Risks: several fields are plain `int` or `unsigned long` for addresses/offsets even though video memory and PCI resource sizes may be resource-sized. `struct init_status` is cast to `struct initchip_param` in `sm750_hw.c`, so layout compatibility with another header is an implicit contract. Shared global state such as `mmio750` is not represented here, which can obscure initialization ordering.

Test signals: compile-time coverage across 32-bit and 64-bit builds, mode tests using all bpp cases, dual-view dataflow permutations, and suspend/resume should exercise most fields. Struct-layout changes should be validated against the DDK init parameter structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.c -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.c

Purpose: this file implements SM750 2D drawing engine operations used by accelerated framebuffer callbacks: rectangle fill, screen-to-screen copy, and monochrome image blit.

Important functions: low-level helpers `write_dpr()`, `read_dpr()`, and `write_dp_port()` access drawing-engine registers and the data port. `sm750_hw_de_init()` initializes masks, stretch format, clipping, color compare, and transparency. `sm750_hw_set2dformat()` programs the pixel format. `sm750_hw_fillrect()`, `sm750_hw_copyarea()`, and `sm750_hw_imageblit()` program the engine for fbdev acceleration. `de_get_transparency()` preserves selected transparency bits during host writes.

Control flow: each operation waits for engine readiness through `accel->de_wait()`, writes base addresses, pitches converted from bytes to pixels, window width, source/destination coordinates, dimensions, colors, ROP values, and command bits, then starts the operation by setting `DE_CONTROL_STATUS`. Copy operations compute direction for overlapping same-surface blits and adjust coordinates for bottom-to-top or right-to-left transfers. Image blits use host-write mode and stream packed monochrome data through the data port line by line.

State and persistence: the drawing engine state persists in DPR registers. `struct lynx_accel` carries MMIO base pointers and wait function pointers set during probe/hardware init. There is no local locking; `sm750.c` protects accelerated fbops with `sm750_dev->slock`.

Dependencies and integration points: used through `struct lynx_accel` hooks assigned in `lynxfb_pci_probe()`. Register offsets and bit definitions come from `sm750_accel.h`. The wait implementation is chip-specific and supplied by `sm750_hw.c` for SM750 versus SM750LE.

Risks: `sm750_hw_imageblit()` casts potentially unaligned source bytes to `unsigned int *`, which can fault or behave poorly on strict-alignment architectures. The `remain[4]` buffer is not zero-initialized before copying trailing bytes, so padding bytes written to the data port may contain stack data. Engine busy waits can spin for a large count. Division by `Bpp` assumes nonzero validated bpp. Copy direction only considers some overlap geometry and maps vertical and horizontal reverse directions to the same control bit, relying on hardware interpretation.

Test signals: accelerated console scrolling, `fbtest` rectangle/copy/mono glyph paths, overlapping copy cases in all directions, 8/16/32 bpp modes, forced engine-busy timeout behavior, and strict-alignment builds are important. Comparing accelerated output with software cfb fallbacks can catch pitch, ROP, and endian issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.h -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.h

Purpose: this header defines the SM750 2D engine register offsets, fields, ROP constants, blit direction constants, and public acceleration prototypes.

Important definitions: `HW_ROP2_COPY` and `HW_ROP2_XOR` are fbdev ROP values used by the driver. `DE_BASE_ADDR_TYPE1` and `DE_PORT_ADDR_TYPE1` identify the SM718/750/502 drawing engine MMIO layout used by `hw_sm750_map()`. Registers include `DE_SOURCE`, `DE_DESTINATION`, `DE_DIMENSION`, `DE_CONTROL`, `DE_PITCH`, foreground/background colors, stretch format, color compare/masks, clipping, pattern registers, window widths, source/destination bases, alpha, wrap, and status.

Control flow and state: the header is declarative. Consumers use these constants to compose command register writes that transition the hardware drawing engine through idle, configured, and active states. The prototypes are implemented in `sm750_accel.c` and are installed into `struct lynx_accel`.

Dependencies and integration points: included by `sm750.c`, `sm750_hw.c`, and `sm750_accel.c`. It relies on Linux integer types and `BIT()`. It is tied to the private fbdev driver; no generic DRM acceleration interface is exposed.

Risks: direction constants define `TOP_TO_BOTTOM` and `LEFT_TO_RIGHT` as `0`, and reverse directions as `1`, which is compact but loses axis distinction outside local context. The header documents older chip base layouts that are not selected dynamically in this driver, so future reuse could choose wrong offsets. Field widths require callers to validate coordinates and pitches before masking truncates them.

Test signals: build coverage, 2D engine register dumps before/after operations, and output validation for fills, copies, and monochrome blits across bpp and pitch alignments. Static analysis should verify all command writes set the required status/command bits and clear incompatible fields when formats change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.c -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.c

Purpose: this file implements hardware cursor programming for SM750-family devices. It controls cursor enable, position, colors, and conversion of fbdev 1-bpp cursor data into the hardware cursor memory format.

Important functions: `sm750_hw_cursor_enable()` writes the cursor image offset and enable bit; `sm750_hw_cursor_disable()` clears the cursor address register; `sm750_hw_cursor_set_size()` updates software width/height; `sm750_hw_cursor_set_pos()` writes the location register; `sm750_hw_cursor_set_color()` writes RGB565 foreground/background colors; `sm750_hw_cursor_set_data()` and `sm750_hw_cursor_set_data2()` pack color/mask bitmaps into 2-bit hardware cursor entries in IO memory.

Control flow: `sm750.c` configures each cursor's MMIO base to the channel-specific cursor block and places cursor image memory near the end of the CRTC video-memory allocation. Fbdev cursor updates disable the cursor, optionally update size, position, color map, and shape/image, then re-enable it if requested. Data packing loops over source bytes, computes 2-bit pixel codes, writes 16-bit units to cursor memory, and advances to a hardware row stride based on maximum cursor width.

State and persistence: cursor state is split between `struct lynx_cursor` fields (`w`, `h`, `vstart`, `offset`, `mmio`) and hardware cursor registers/image memory. Position and color persist in MMIO registers until changed or hardware reset.

Dependencies and integration points: called by `lynxfb_ops_cursor()` in `sm750.c`. It uses `struct lynx_cursor` from `sm750.h`, Linux IO accessors, fbdev ROP values, and local cursor register offsets that mirror panel/CRT cursor register layouts.

Risks: `sm750_hw_cursor_set_pos()` masks negative x/y values without setting the documented left/top sign bits, so off-screen cursor positioning may be wrong. `sm750_hw_cursor_set_data2()` advances rows when `!(i & (pitch - 1))`, which also triggers at `i == 0` and appears inconsistent with `set_data()`. Widths not divisible by 8 make `pitch = w >> 3` truncate. Cursor memory size is fixed from max dimensions, but source dimensions rely on prior validation in fbdev callback.

Test signals: hardware cursor movement near screen edges, negative positions, 1/8/16/64 pixel widths, ROP copy versus XOR shapes, color-map changes, dual-head cursor independence, and suspend/resume cursor memory clearing should be validated. Comparing set_data and set_data2 output can expose row-stride bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.h -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.h

Purpose: this small header declares the SM750 hardware cursor operations consumed by the framebuffer driver.

Important APIs: prototypes cover cursor enable/disable, size, position, color, and two cursor data packing variants: `sm750_hw_cursor_set_data()` and `sm750_hw_cursor_set_data2()`.

Control flow and state: this file has no state or executable logic. The API operates on `struct lynx_cursor`, whose definition is provided by `sm750.h`; include ordering therefore matters because the header does not forward-declare the structure.

Dependencies and integration points: included by `sm750.c` and `sm750_cursor.c`. It is private to the staging driver and is wired into fbdev through `lynxfb_ops_cursor()`.

Risks: the header exposes two data-packing functions without documenting their difference or expected bit order. It also relies on external definitions of `u8`, `u16`, `u32`, and `struct lynx_cursor`, so standalone inclusion is fragile.

Test signals: compile coverage for include ordering and runtime cursor behavior through the fbdev cursor callback are sufficient for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_hw.c -->
## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_hw.c

Purpose: this file provides the chip-specific hardware layer for SM750 fbdev: PCI BAR mapping, device initialization, display routing, CRTC timing setup, palette programming, blanking, drawing-engine reset/wait, and panning.

Important functions: `hw_sm750_map()` maps BAR1 MMIO and BAR0 video memory, initializes acceleration MMIO bases, sets global `mmio750`, and detects VRAM size. `hw_sm750_inithw()` fills default clocks, calls DDK init, handles SM718 PCI burst, configures CRT/panel options, initializes SM750LE DVI over software I2C, and initializes acceleration. Mode functions are `hw_sm750_output_set_mode()`, `hw_sm750_crtc_check_mode()`, and `hw_sm750_crtc_set_mode()`. Other exported helpers are `hw_sm750_set_col_reg()`, `hw_sm750le_set_blank()`, `hw_sm750_set_blank()`, `hw_sm750_init_accel()`, `hw_sm750le_de_wait()`, `hw_sm750_de_wait()`, and `hw_sm750_pan_display()`.

Control flow: mapping requests BAR1, `ioremap()`s the 2 MiB register window, sets DDK chip type, obtains VRAM size from hardware, and maps VRAM write-combined. Hardware init computes default clocks, invokes `ddk750_init_hw()`, sets DAC/DPMS and panel type for non-LE chips, or opens the SM750LE display and optionally programs CH7301. Mode setting converts fbdev timings to a DDK `mode_parameter`, selects primary or secondary PLL, calls `ddk750_set_mode_timing()`, and writes panel or CRT framebuffer address, pitch, window, plane, and pixel format registers. Blanking writes DPMS/data/blank bits depending on output path and chip type. Panning writes adjusted framebuffer base addresses.

State and persistence: hardware state is MMIO and VRAM; software state is carried in `struct sm750_dev`, `lynxfb_crtc`, and `lynxfb_output`. The global `mmio750` is the DDK access base used by `peek32()`/`poke32()` in other files. Drawing-engine readiness is polled from different registers for SM750 and SM750LE.

Dependencies and integration points: depends on PCI, IO mapping, fbdev timing structures, `ddk750.h`/DDK functions, `ddk750_reg.h` through included DDK headers, `ddk750_swi2c` for LE DVI setup, and `sm750_accel`. It is called by `sm750.c` during probe, resume, mode changes, blanking, colormap, panning, and acceleration setup.

Risks: `modparm.vertical_sync_polarity` uses `FB_SYNC_HOR_HIGH_ACT` and `horizontal_sync_polarity` uses `FB_SYNC_VERT_HIGH_ACT`, which looks swapped. `hw_sm750_pan_display()` ORs the new address into the existing address register instead of replacing the masked address bits, so stale bits may remain. Only BAR1 is requested before BAR0 VRAM is mapped. Busy waits spin for a very large fixed loop. `ddk750_init_hw()` receives a cast from `struct init_status` to another DDK structure, relying on layout identity. SM750LE DVI programming is hard-coded for one external chip and board path.

Test signals: probe mapping and cleanup, VRAM size detection, mode-set timing on primary and secondary CRTCs, polarity-sensitive modes, panning with nonzero offsets, blanking states, palette programming in 8 bpp, SM750LE CH7301 initialization, acceleration reset/wait, and suspend/resume are key. Register traces should confirm masked writes replace rather than accumulate address fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/Kconfig

Purpose: this Kconfig file gates VC04 services staging configuration and sources the BCM2835 audio subdirectory configuration when `BCM_VIDEOCORE` is enabled.

Important definitions: it contains a single `if BCM_VIDEOCORE` block that includes `drivers/staging/vc04_services/bcm2835-audio/Kconfig`.

Control flow and state: Kconfig inclusion is conditional; no runtime state exists. If the VideoCore framework is disabled, the audio driver option is not presented from this path.

Dependencies and integration points: integrated into the kernel staging Kconfig hierarchy. It delegates all audio-specific dependency decisions to the nested Kconfig file.

Risks: moving the audio Kconfig path or changing the parent symbol without updating this source line would silently hide `SND_BCM2835`. The file currently only includes audio services, so additional VC04 services require explicit source statements.

Test signals: `make menuconfig`/`oldconfig` with `BCM_VIDEOCORE=y` should show BCM2835 audio; with it disabled, the option should be absent. Kconfig lint and allmodconfig coverage verify the include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/Makefile -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/Makefile

Purpose: this Makefile descends into the BCM2835 audio subdirectory when the ALSA BCM2835 driver is enabled.

Important definitions: `obj-$(CONFIG_SND_BCM2835) += bcm2835-audio/` links the child directory into the kernel build for built-in or module configurations.

Control flow and state: build-system state depends on `CONFIG_SND_BCM2835`; there is no runtime state.

Dependencies and integration points: paired with `bcm2835-audio/Makefile`, which defines the final `snd-bcm2835` object composition.

Risks: if `SND_BCM2835` is selected but the parent staging directory is not reached, the module will not build. There is no entry for other VC04 services in this file.

Test signals: `make M=drivers/staging/vc04_services` and full kernel builds with `CONFIG_SND_BCM2835=m/y` should include the child directory and produce `snd-bcm2835`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Kconfig

Purpose: this Kconfig entry defines the staging ALSA driver for BCM2835 built-in audio over the VideoCore VCHIQ messaging interface.

Important definitions: `config SND_BCM2835` is tristate, depends on `(ARCH_BCM2835 || COMPILE_TEST) && SND`, selects `SND_PCM`, and selects `BCM2835_VCHIQ` when `HAS_DMA` is available. Help text states that both 3.5mm and HDMI audio are handled through firmware running on VideoCore.

Control flow and state: build-time selection controls whether the module is built and whether supporting PCM and VCHIQ symbols are selected. No runtime state exists in this file.

Dependencies and integration points: sourced only under `BCM_VIDEOCORE` by the parent Kconfig. The selected symbol drives both parent and child Makefiles.

Risks: `select BCM2835_VCHIQ if HAS_DMA` assumes VCHIQ is valid whenever DMA is present; unusual COMPILE_TEST configs may still expose missing dependencies elsewhere. The staging location implies the driver may not meet normal subsystem quality expectations.

Test signals: Kconfig resolution under Raspberry Pi, COMPILE_TEST, module, and built-in configurations; full build with ALSA disabled should keep the option unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Makefile -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Makefile

Purpose: this Makefile builds the BCM2835 ALSA audio module object.

Important definitions: `obj-$(CONFIG_SND_BCM2835) += snd-bcm2835.o` declares the module/built-in object, and `snd-bcm2835-objs := bcm2835.o bcm2835-ctl.o bcm2835-pcm.o bcm2835-vchiq.o` composes it from probe/card creation, mixer controls, PCM callbacks, and VCHIQ transport.

Control flow and state: build composition is fixed once `CONFIG_SND_BCM2835` is enabled. No runtime behavior exists here.

Dependencies and integration points: paired with `bcm2835-audio/Kconfig` and parent `vc04_services/Makefile`.

Risks: adding a source file without updating `snd-bcm2835-objs` will compile locally only if referenced elsewhere, not into the final module. Object order can matter for initcall/linking only if symbols have duplicate or weak definitions, which is not apparent here.

Test signals: module build should produce one `snd-bcm2835` object containing symbols from all four C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-ctl.c -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-ctl.c

Purpose: this file implements ALSA mixer and IEC958 controls for the BCM2835 audio driver and propagates control changes to active VideoCore audio streams.

Important functions: `snd_bcm2835_ctl_info()`, `snd_bcm2835_ctl_get()`, and `snd_bcm2835_ctl_put()` implement volume, mute, and playback device control behavior. `bcm2835_audio_set_chip_ctls()` iterates active substreams and sends updated controls. IEC958 controls are handled by `snd_bcm2835_spdif_default_info/get/put()` and `snd_bcm2835_spdif_mask_info/get()`. `create_ctls()` installs controls, while `snd_bcm2835_new_headphones_ctl()` and `snd_bcm2835_new_hdmi_ctl()` expose route-specific control sets.

Control flow: ALSA queries control metadata, reads current values under `chip->audio_mutex`, and writes validated values back under the same mutex. On change, all open streams receive `bcm2835_audio_set_ctls()`. HDMI gets both regular mixer controls and IEC958 default/mask controls; headphones get regular controls only.

State and persistence: control state is stored in `struct bcm2835_chip` fields `volume`, `mute`, `dest`, and `spdif_status`. These values persist for the ALSA card lifetime and are applied to streams when controls change and again during PCM prepare.

Dependencies and integration points: depends on ALSA core/control/TLV APIs, IEC958 definitions, and transport function `bcm2835_audio_set_ctls()` from `bcm2835-vchiq.c`. Control objects are created from `bcm2835.c` after PCM creation.

Risks: mute semantics are inverted at the transport layer: `CTRL_VOL_MUTE` is 0 and `CTRL_VOL_UNMUTE` is 1, so `if (!chip->mute)` sends the mute volume. Control updates are serialized on `audio_mutex` but send VCHIQ messages while holding it, which can block other ALSA operations. `PCM_PLAYBACK_DEVICE` is supported by generic callbacks but is not included in the declared control arrays, so it is effectively unused here.

Test signals: `amixer` get/set for volume and switch, HDMI IEC958 status changes including non-audio passthrough, updating controls while streams are active, validation of min/max boundaries, and route-specific card creation are important. Transport errors should be visible in logs without corrupting cached control values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-pcm.c -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-pcm.c

Purpose: this file implements ALSA PCM playback callbacks for BCM2835 audio, including regular PCM and HDMI IEC958/SPDIF playback paths.

Important data and functions: hardware capability tables are `snd_bcm2835_playback_hw` and `snd_bcm2835_playback_spdif_hw`. Runtime callbacks are `snd_bcm2835_playback_open_generic()`, regular/SPDIF open wrappers, `snd_bcm2835_playback_close()`, `snd_bcm2835_pcm_prepare()`, `snd_bcm2835_pcm_transfer()`, `snd_bcm2835_pcm_ack()`, `snd_bcm2835_pcm_trigger()`, and `snd_bcm2835_pcm_pointer()`. `bcm2835_playback_fifo()` is called from VCHIQ completion callbacks to advance playback state. `snd_bcm2835_new_pcm()` creates PCM devices and installs ops.

Control flow: open serializes on `audio_mutex`, rejects duplicate opens, allocates a `bcm2835_alsa_stream`, opens a VCHIQ audio instance, assigns runtime hardware constraints, stores the stream, and marks the substream open. Prepare sends controls and audio parameters to firmware, initializes indirect playback bookkeeping, buffer/period sizes, atomic playback position, and interpolation time. ALSA ack transfers newly available bytes from the DMA buffer through `bcm2835_audio_write()`. Trigger starts, stops, or drains firmware playback. Pointer reports indirect playback position and adjusts runtime delay by interpolating time since the last firmware completion.

State and persistence: stream state lives in dynamically allocated `struct bcm2835_alsa_stream` and includes indirect PCM state, `draining`, atomic byte position, period offset, buffer/period size, interpolation timestamp, VCHIQ instance, and index. `chip->opened` is a bitmask for active substreams; SPDIF open rejects any already-open stream. PCM buffers are managed through `snd_pcm_set_managed_buffer_all()`.

Dependencies and integration points: depends on ALSA PCM and indirect PCM helpers, `bcm2835.h`, and transport functions from `bcm2835-vchiq.c`. `bcm2835.c` calls `snd_bcm2835_new_pcm()` for each ALSA card/route.

Risks: `chip->opened` uses substream numbers and SPDIF's exclusive handling may be too broad or too narrow depending on card layout. Completion callbacks can call `bcm2835_playback_fifo()` asynchronously, so correct ALSA locking is critical. `runtime->delay` interpolation writes a negative frame count based on elapsed time, which should be checked against ALSA delay expectations. Drain path is marked questionable in transport code. The source pointer in transfer uses `runtime->dma_area + rec->sw_data` and assumes managed buffer is valid and contiguous for VCHIQ transfer.

Test signals: playback across U8/S16, 1-8 channels, 8 kHz to 192 kHz, HDMI SPDIF at 44.1/48 kHz, period constraints/alignment, xrun handling when firmware reports too many bytes, drain/stop behavior, concurrent open rejection, and position/delay reporting under long playback are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-vchiq.c -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-vchiq.c

Purpose: this file implements the transport between ALSA streams and the VideoCore audio service over VCHIQ. It opens VCHIQ services, sends audio control/config/start/stop/write messages, handles firmware callbacks, and transfers PCM data through either bulk or queued kernel messages.

Important types and functions: `struct bcm2835_audio_instance` stores service handle, completion, mutex, stream pointer, result, max packet, and peer version. Context lifecycle is `bcm2835_new_vchi_ctx()` and `bcm2835_free_vchi_ctx()`. Per-stream lifecycle is `bcm2835_audio_open()` and `bcm2835_audio_close()`. Messaging helpers are `bcm2835_audio_lock()`, `bcm2835_audio_unlock()`, `bcm2835_audio_send_msg_locked()`, `bcm2835_audio_send_msg()`, and `bcm2835_audio_send_simple()`. Runtime APIs include `bcm2835_audio_set_ctls()`, `bcm2835_audio_set_params()`, `bcm2835_audio_start()`, `bcm2835_audio_stop()`, `bcm2835_audio_drain()`, and `bcm2835_audio_write()`.

Control flow: device probe creates one VCHIQ context via `vchiq_initialise()` and `vchiq_connect()`. Opening a PCM stream allocates an audio instance, opens the `AUDS` service with version negotiation and `audio_vchi_callback`, sends an open message, reads peer version, and chooses bulk transfer for old peers or forced bulk, otherwise 4000-byte queued messages. Synchronous messages initialize a completion, queue a message, and wait up to 10 seconds for `VC_AUDIO_MSG_TYPE_RESULT`. Write sends a `VC_AUDIO_MSG_TYPE_WRITE` descriptor with cookies, then transfers sample bytes via bulk transmit or packetized kernel messages. Completion callbacks validate cookies and call `bcm2835_playback_fifo()` with the completed byte count.

State and persistence: `struct bcm2835_vchi_ctx` owns the shared `vchiq_instance`. Each open ALSA stream owns one service handle and per-stream completion/result state. Firmware-visible audio state includes controls, format, running/stopped state, queued audio payloads, and write completion cookies. Service use/release calls bracket locked operations.

Dependencies and integration points: depends on Raspberry Pi VCHIQ core (`vchiq_arm.h`, `vchiq_bus` device parent state), message definitions in `vc_vchi_audioserv_defs.h`, and PCM/control callbacks in other audio files. The callback path integrates with ALSA through `bcm2835_playback_fifo()`.

Risks: the async packetized write path updates `status` inside a loop but does not break on the first failure, so a later successful chunk could overwrite an earlier error. Pointer arithmetic on `void *src` is a GNU C extension. Synchronous message waits can block for 10 seconds. `bcm2835_audio_drain()` is explicitly marked as not working as expected. Close deinitializes the service even if close message returns an error. Context cleanup assumes `vchiq_shutdown()` is safe and warns on failure.

Test signals: service open/close, peer version negotiation, forced bulk mode, packetized and bulk writes, timeout/error handling for result messages, invalid completion cookie logging, playback position advancement from firmware completions, drain behavior, and suspend/remove while streams are active should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835-vchiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835.c -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835.c

Purpose: this is the VCHIQ bus driver entry point for the BCM2835 ALSA audio driver. It creates ALSA cards for enabled output routes, allocates shared VCHIQ context, configures DMA mask, and registers with the VCHIQ device bus.

Important data and functions: module parameters are `enable_hdmi`, `enable_headphones`, and `num_channels`. `struct bcm2835_audio_driver` describes route-specific card creation. Static route descriptors define HDMI and headphones cards. `bcm2835_devm_add_vchi_ctx()` creates a devres-managed VCHIQ context. `snd_add_child_device()` creates one ALSA card, PCM device(s), and controls. `snd_add_child_devices()` distributes channel count across enabled route devices. `snd_bcm2835_alsa_probe()` is the VCHIQ probe callback.

Control flow: on probe, the driver sets a 32-bit DMA mask, clamps invalid channel counts to `MAX_SUBSTREAMS`, creates the shared VCHIQ context, then creates enabled child ALSA cards. Each card allocation initializes `bcm2835_chip`, attaches the shared VCHIQ context, sets card names, creates PCM(s) and controls through route-specific callbacks, registers the card, stores drvdata, and registers a devm action to free the card. HDMI creates a regular PCM plus an IEC958 PCM; headphones creates a regular PCM only.

State and persistence: module parameters control which cards appear and how channels are divided. Per-card persistent state is `struct bcm2835_chip`, including ALSA card/PCM pointers, route/mixer state, open stream bitmask, mutex, and VCHIQ context pointer. Devres manages VCHIQ context and card cleanup for the VCHIQ device lifetime.

Dependencies and integration points: depends on ALSA core, DMA API, Raspberry Pi VCHIQ bus, and helper functions implemented in `bcm2835-pcm.c`, `bcm2835-ctl.c`, and `bcm2835-vchiq.c`. It registers for VCHIQ device ID `"bcm2835-audio"` through `module_vchiq_driver()`.

Risks: `dev_set_drvdata(dev, chip)` is called for each child card on the same parent device, so later cards overwrite earlier drvdata. Channel distribution gives the entire remainder to the first enabled device. `enable_hdmi` defaults false while headphones defaults true, which affects expected card enumeration. Probe creates multiple ALSA cards but errors after a later card may rely on devres/manual cleanup interactions. PM callbacks are stubs.

Test signals: probe with headphones only, HDMI only, both routes, invalid `num_channels`, channel distribution, card registration names, devres cleanup on probe failure, module unload, and VCHIQ device binding all matter. User-visible checks include `aplay -l`, PCM open for route devices, and mixer controls for each card.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835.h -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835.h

Purpose: this private header defines shared BCM2835 audio structures, route/control enums, volume conversion helpers, constants, and cross-file function prototypes.

Important definitions and types: `MAX_SUBSTREAMS` is 8, with `AVAIL_SUBSTREAMS_MASK` of `0xff`. Volume/mute constants and `alsa2chip()`/`chip2alsa()` macros translate ALSA dB-ish values to firmware volume format. `enum snd_bcm2835_route` defines auto/headphones/HDMI routes; `enum snd_bcm2835_ctrl` defines internal control IDs. `struct bcm2835_vchi_ctx` wraps a VCHIQ instance. `struct bcm2835_chip` stores card, PCM, device, stream pointers, mixer state, open mask, mutex, and VCHIQ context. `struct bcm2835_alsa_stream` stores one stream's ALSA, indirect PCM, position, period, and VCHIQ instance state.

Control flow and state: the header defines the state passed among probe/card creation, PCM callbacks, control callbacks, and VCHIQ transport. `bcm2835_chip` is card-scoped; `bcm2835_alsa_stream` is open-substream-scoped; `bcm2835_vchi_ctx` is VCHIQ-device-scoped.

Dependencies and integration points: includes Linux device/VCHIQ/wait headers and ALSA core/PCM/indirect PCM headers. Prototypes bind the four source files into one module: PCM creation and callbacks, control creation, VCHIQ context lifecycle, audio service commands, write completion handling, and buffer retrieval declaration.

Risks: `bcm2835_audio_retrieve_buffers()` is declared but not implemented in the requested source set, suggesting stale API surface or implementation elsewhere absent from this module. Volume conversion macros use `uint` and arithmetic negation/shifts that should be checked for type and range behavior. The open bitmask assumes no more than eight substreams and maps directly to substream numbers.

Test signals: compile coverage for all cross-file prototypes, sparse/type checks for volume macros, open/close paths that populate and clear `alsa_stream[]`, and route/control state propagation are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/bcm2835.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/vc_vchi_audioserv_defs.h -->
## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/vc_vchi_audioserv_defs.h

Purpose: this header defines the host-to-VideoCore audio service protocol messages used by the BCM2835 VCHIQ audio transport.

Important definitions: protocol versions are `VC_AUDIOSERV_MIN_VER` 1 and `VC_AUDIOSERV_VER` 2. Write completion cookies are fourcc values `BCMA` and `DATA`. `enum vc_audio_msg_type` defines result, complete, config, control, open, close, start, stop, write, and max message types. Payload structs cover config, control, open/close/start/stop, write, result, and completion. `struct vc_audio_msg` is the tagged union sent over VCHIQ.

Control flow and state: `bcm2835-vchiq.c` fills `vc_audio_msg` instances and sends them through VCHIQ. Synchronous commands wait for `VC_AUDIO_MSG_TYPE_RESULT`; audio payload writes expect later `VC_AUDIO_MSG_TYPE_COMPLETE` with matching cookies and a byte count.

Dependencies and integration points: depends on VCHIQ fourcc macros and Linux integer types via including code. It is private to the BCM2835 audio module and firmware ABI.

Risks: message structs cross a firmware boundary, so field sizes, signedness, endianness, and layout padding are ABI-sensitive. The enum comments are generic and several payload comments say "Configure audio" even for non-config operations, so the source is not self-documenting enough for protocol changes. Cookie validation protects completions only after the service accepts data.

Test signals: interoperability with firmware service version 1 and 2, config/control/open/start/stop/write round trips, completion cookie mismatch handling, and compile-time layout checks if available. Firmware protocol changes should be tested with both bulk and packetized write modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/vc_vchi_audioserv_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/staging/vme_user/Kconfig

Purpose: this Kconfig file defines staging support for the VME bus framework, bridge drivers, and a userspace VME access driver.

Important definitions: `menuconfig VME_BUS` is a bool depending on PCI and describes the bridge framework. Inside `if VME_BUS`, `VME_TSI148` is a DMA-dependent tristate for Tundra TSI148 PCI/X bridges, `VME_FAKE` is a virtual bridge for development, and `VME_USER` is a userspace access driver compatible with older vmelinux-style interfaces.

Control flow and state: selection controls which VME framework and device driver objects are built. Enabling `VME_BUS` alone builds framework support but not necessarily a hardware bridge or userspace device driver.

Dependencies and integration points: paired with `vme_user/Makefile`, which builds `vme.o`, `vme_user.o`, `vme_tsi148.o`, and `vme_fake.o` according to these symbols. The help text warns users that a specific bridge driver is needed for actual hardware.

Risks: `VME_BUS` depends only on PCI, while fake bridge may not need PCI in principle; this keeps the whole framework PCI-gated. `VME_USER` has no extra dependency beyond `VME_BUS`, so users can enable it without a real bridge. Staging status suggests ABI and cleanup concerns.

Test signals: Kconfig builds with each symbol as built-in/module where applicable, dependency resolution when `HAS_DMA` is absent, menu visibility, and allmodconfig coverage for VME components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/Makefile -->
## sources/distributed-fs/ceph-client/drivers/staging/vme_user/Makefile

Purpose: this Makefile builds the VME bus framework, userspace access driver, and optional bridge drivers according to Kconfig symbols.

Important definitions: `obj-$(CONFIG_VME_BUS) += vme.o`, `obj-$(CONFIG_VME_USER) += vme_user.o`, `obj-$(CONFIG_VME_TSI148) += vme_tsi148.o`, and `obj-$(CONFIG_VME_FAKE) += vme_fake.o`.

Control flow and state: the build system includes each object based on the matching configuration symbol. Runtime behavior is in the corresponding C files, not here.

Dependencies and integration points: paired with `vme_user/Kconfig` and the staging driver sources in the same directory. `vme.o` provides the core API used by both bridge and userspace drivers.

Risks: object names are simple one-to-one entries; adding new bridge sources requires explicit Makefile and Kconfig updates. Building `vme_user.o` without a functioning bridge may create a module that loads but cannot provide useful access.

Test signals: build matrix for `VME_BUS`, `VME_USER`, `VME_TSI148`, and `VME_FAKE` as built-in and modules; module dependency checks should ensure userspace access links against the framework symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/vme_user/Makefile -->
