# Grouped Research: subset-b-003756

Grouped source-tree-aligned research for DRM tiny display drivers and TTM build manifests. Each source file section preserves the source path in the title and is delimited for deterministic splitting into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/arcpgu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/arcpgu.c

Purpose: This is the DRM/KMS driver for the Synopsys ARC PGU display controller. It exposes one simple display pipe backed by GEM DMA framebuffers, programs ARC PGU MMIO timing and framebuffer registers, and either attaches to a bridge described in device tree or creates a virtual connector for simulation platforms.

Important APIs, types, and functions: `struct arcpgu_drm_private` owns the embedded `drm_device`, MMIO base, pixel clock, `drm_simple_display_pipe`, and optional simulated connector. `arc_pgu_write()`/`arc_pgu_read()` wrap register access. `arc_pgu_supported_formats` accepts RGB565, XRGB8888, and ARGB8888, while `arc_pgu_set_pxl_fmt()` maps those formats to the controller's RGB565 versus XRGB8888 bit. `arc_pgu_mode_valid()` uses `clk_round_rate()` with a 0.5 percent tolerance. `arc_pgu_mode_set()` writes total, sync, active-area, polarity, stride, start, pixel format, and clock-rate state. Probe is split through `arcpgu_probe()`, `arcpgu_load()`, `drm_dev_register()`, and `drm_client_setup_with_fourcc()`.

Control flow: The platform driver allocates a managed DRM device, resolves `pxlclk`, initializes mode config, maps the register resource, optionally binds reserved framebuffer memory, sets a 32-bit DMA mask, discovers a bridge through OF graph endpoint 0, or falls back to a virtual connector. Atomic enable programs mode registers, enables the clock, and sets the controller enable bit. Atomic update writes the DMA address of the current framebuffer into `ARCPGU_REG_BUF0_ADDR`; disable clears enable and disables the clock. Remove unregisters DRM and shuts down atomic state/polling.

State and persistence: Persistent driver state is only in `arcpgu_drm_private`; hardware state lives in ARC PGU registers and the pixel clock. Reserved memory attachment persists through the device lifetime. The update path assumes scanout from DMA GEM object 0 and does not maintain a shadow copy.

Dependencies and integration points: Depends on platform resources, OF graph/bridge lookup, common DRM atomic/simple-pipe helpers, GEM DMA helpers, fbdev DMA helpers, clock framework, DMA API, and optional debugfs. Integration is via `snps,arcpgu` OF compatible and a bridge endpoint when real output hardware exists.

Risks: Clock validation is only as good as the clock provider's rounding behavior. `arc_pgu_set_pxl_fmt()` treats ARGB8888 like XRGB8888, so alpha is ignored. `mode_config.max_width`/`max_height` are 1920x1080 although the simulated connector advertises up to 8192x8192; mode validation relies on the overall DRM flow to reject out-of-config modes. Hardware register writes are mostly unchecked, and `ARCPGU_REG_STRIDE` is forced to zero.

Test signals: Useful tests include device-tree bridge attach versus simulated connector fallback, RGB565 and XRGB8888 fbdev startup, pixel-clock rejection for unrepresentable modes, debugfs clock readout, suspend/remove atomic shutdown, and a KMS atomic update verifying `BUF0_ADDR` changes to the GEM DMA address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/arcpgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/bochs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/bochs.c

Purpose: This PCI DRM driver supports the Bochs/QEMU stdvga DISPI interface and Simics-compatible variants. It offers one virtual connector/CRTC/primary plane, copies shadow GEM framebuffer damage into the linear framebuffer BAR, and programs VBE DISPI plus VGA registers for display modes and blanking.

Important APIs, types, and functions: `struct bochs_device` stores MMIO or I/O-port access, framebuffer mapping/base/size, QEMU extension size, current mode fields, and DRM objects. `bochs_uses_mmio()`, `bochs_vga_readb()`/`writeb()`, and `bochs_dispi_read()`/`write()` abstract MMIO versus port I/O. `bochs_hw_init()` discovers BAR2 MMIO/ports, validates DISPI ID, maps framebuffer BAR0, and enables native endian extension registers. `bochs_primary_plane_helper_atomic_update()` copies damaged rectangles using `drm_fb_memcpy()` and exposes a panic scanout buffer through `get_scanout_buffer`.

Control flow: Probe removes conflicting apertures, allocates a managed DRM device, enables PCI, stores drvdata, initializes hardware, builds KMS objects, registers DRM, and starts the DRM client. Mode setting writes DISPI x/y/bpp/virtual size/offset registers and enables LFB mode. Plane atomic updates iterate damage, copy shadow data to write-combined VRAM, reset scanout base to offset zero, and adjust endian format. Connector mode probing reads EDID from the MMIO aperture if present, otherwise creates no-EDID modes with module-param defaults.

State and persistence: The driver caches current resolution, bpp, stride, virtual height, framebuffer mapping, and extension size. Hardware persistence includes DISPI registers, VGA blanking attribute writes, QEMU endian register 0x604, and LFB content. There is no persistent software backing store beyond GEM shadow buffers owned by DRM helpers.

Dependencies and integration points: Uses PCI IDs for QEMU stdvga and Simics, `aperture_remove_conflicting_pci_devices()`, optional I/O port support, DRM shmem helpers, shadow-plane helpers, fbdev shmem, vblank timer helpers, EDID helpers, and DRM panic scanout. Module parameters `modeset`, `defx`, and `defy` control binding/default modes.

Risks: If I/O ports are unavailable and the device lacks MMIO register BARs, probe fails. EDID reads are limited to the area before VGA registers and silently fall back to synthetic modes. Framebuffer memory size mismatches are clamped after warning. Endian switching is format-dependent and relies on QEMU extension behavior. The plane update copies only reported damage, so incorrect damage clips can leave stale VRAM.

Test signals: Validate QEMU stdvga boot, Simics ID match, EDID and no-EDID mode paths, XRGB8888 and BGRX8888 endian output, mode rejection when framebuffer memory is insufficient, suspend/resume through mode config helpers, panic framebuffer readout, and removal/unplug racing with atomic commits through `drm_dev_enter()` guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/bochs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/cirrus-qemu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/cirrus-qemu.c

Purpose: This is a DRM driver for QEMU/Xen emulated Cirrus Logic GD5446 VGA hardware. It is intentionally minimal for virtual hardware: one virtual connector, one CRTC, one primary plane, shmem shadow framebuffers, and direct writes to VGA/Cirrus sequencer/CRTC/graphics registers plus VRAM.

Important APIs, types, and functions: `struct cirrus_device` owns DRM objects plus VRAM and MMIO mappings. Register helpers `rreg_seq()`, `wreg_seq()`, `rreg_crt()`, `wreg_crt()`, `wreg_gfx()`, and `wreg_hdr()` access the Cirrus register windows. `cirrus_mode_set()` programs horizontal/vertical timing registers and overflow bits. `cirrus_format_set()` selects C8/RGB565/RGB888/XRGB8888 hardware modes. `cirrus_pitch_set()` programs CRTC offset and extended pitch bits. Plane check enforces `CIRRUS_MAX_PITCH` and 4 MiB VRAM limits.

Control flow: PCI probe removes conflicting framebuffer apertures, enables the device, requests all BARs, allocates DRM state, maps VRAM BAR0 and MMIO BAR1, initializes fixed mode limits, creates the primary plane/CRTC/encoder/connector, registers the device, and launches fbdev/client setup. Atomic CRTC enable programs the display mode, unblanks VGA attribute output when I/O ports exist, and enables vblank timer accounting. Plane atomic update detects format/pitch changes, programs registers as needed, and copies damaged shadow framebuffer rectangles into VRAM.

State and persistence: The software state is small: DRM object state plus BAR mappings. Hardware state includes VGA/Cirrus CRTC timing, sequencer format bits, graphics mode, DAC header, pitch, start address, and VRAM contents. No explicit suspend/resume PM callbacks are present; normal remove/shutdown calls atomic shutdown.

Dependencies and integration points: Binds only to Cirrus GD5446 PCI IDs for Red Hat Qumranet/QEMU and Xen. Uses aperture conflict removal, `pcim_*` PCI management, DRM shmem/fbdev helpers, shadow-plane helpers, damage clips, vblank timer helpers, and `video/cirrus.h`/`video/vga.h` constants.

Risks: The file comments state the programming is only sufficient for emulated hardware and may not correctly drive real devices. The maximum mode dimensions are constrained by pitch and fixed VRAM size; bad pitch or height combinations are rejected. Register programming is unguarded beyond `drm_dev_enter()` in update/enable. There is no EDID path, so userspace sees synthetic modes with a 1024x768 preference.

Test signals: Exercise QEMU and Xen binding, all advertised formats, pitch rejection above `0x1ff << 3`, VRAM-size mode rejection, damage-only updates, format/pitch change commits, shutdown/remove atomic cleanup, and visual output for 16/24/32-bpp modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/cirrus-qemu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/gm12u320.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/gm12u320.c

Purpose: This USB DRM driver supports Grain Media GM12U320-based projector displays such as the Acer C120. It presents a fixed 848x480 XRGB8888 display, converts framebuffer data into packed 24-bpp USB data blocks for the real 854-pixel-wide projector, and drives the device with vendor-derived bulk command sequences.

Important APIs, types, and functions: `struct gm12u320_device` embeds the DRM device, simple pipe, connector, USB command/data buffers, and delayed-work framebuffer update state. `gm12u320_usb_alloc()` allocates one command buffer and twenty preformatted transfer blocks. `gm12u320_misc_request()` sends command/value/status transactions for device control, including eco mode. `gm12u320_copy_fb_to_blocks()` converts dirty XRGB8888 pixels to packed 24-bpp and updates block content. `gm12u320_fb_update_work()` performs the full USB data and draw transfer sequence and requeues idle refreshes.

Control flow: Probe accepts only USB interface 0, allocates DRM state, optionally sets the USB interface DMA device for buffer sharing, initializes delayed work and mode config, allocates USB buffers, applies eco mode, creates a fake VGA connector with EDID, creates a simple shadow display pipe, registers DRM, and starts client setup. Pipe enable marks the full framebuffer dirty with a longer first-frame timeout. Pipe update merges damage and queues work. The worker copies the current framebuffer reference into USB block buffers, sends each block via endpoint 3, reads endpoint 2 status, sends the draw command, reads status with a first-frame or normal timeout, toggles frame bit, and requeues within 2 seconds to keep the projector from showing its logo.

State and persistence: Persistent software state includes the eco-mode module parameter, command/data buffers, delayed work, a mutex-protected framebuffer reference, dirty rectangle, source iosys map, frame bit, and draw timeout. Hardware state is mostly implicit in the projector's USB protocol and eco setting. The update path takes and drops framebuffer references to keep source data alive across delayed work.

Dependencies and integration points: Uses USB bulk APIs and endpoints 1-4, DRM shmem helpers, simple display pipe shadow-plane helpers, fake EDID generation, fbdev shmem, damage helpers, and USB PM suspend/resume. The USB ID table matches vendor 0x1de1/product 0xc102. The `eco_mode` module parameter is user-visible.

Risks: The protocol constants are reverse-engineered and strict about transfer lengths; any short transfer is treated as I/O failure. The code stores `src_map.vaddr` directly with a TODO about mapping abstraction. Only one outstanding framebuffer reference is tracked; damage merging is coarse. The visible width differs from hardware width, requiring horizontal offset math. Disconnect/unload must cancel delayed work to avoid use-after-unplug; errors from unplug are intentionally suppressed.

Test signals: Validate probe only on interface 0, fixed EDID mode, eco-mode request on probe and resume, first-frame timeout behavior, idle refresh every 2 seconds, dirty rectangle merge, block-boundary conversion, disconnect while work is queued, and suspend/resume through DRM mode-config helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/gm12u320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/hx8357d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/hx8357d.c

Purpose: This SPI DRM driver supports HX8357D-based Adafruit YX350HV15-style panels. It is a MIPI DBI helper driver with fixed 320x480 mode, DMA GEM scanout, a primary SPI connector, and a panel-specific initialization sequence.

Important APIs, types, and functions: `struct hx8357d_device` wraps `mipi_dbi_dev` plus DRM plane/CRTC/encoder/connector. Plane, CRTC, connector, and mode config methods mostly use `DRM_MIPI_DBI_*` helper macros. `hx8357d_crtc_helper_atomic_enable()` is the main custom function: it powers on and conditionally resets, sends HX8357D controller commands for extension, RGB, COM voltage, oscillator, panel, power, standby, cycle, gamma, pixel format, TE, sleep exit, display on, rotation address mode, and backlight enable.

Control flow: Probe allocates a managed DRM device, requires a `dc` GPIO, resolves backlight, reads optional `rotation`, initializes SPI DBI, initializes DBI device metadata, configures exact mode bounds and preferred depth 16, builds plane/CRTC/encoder/SPI connector, resets mode config, registers DRM, stores drvdata, and runs client setup. Atomic enable skips the init table if `mipi_dbi_poweron_conditional_reset()` reports the display was already on, but always applies the rotation address mode and enables the backlight.

State and persistence: Persistent state is in `mipi_dbi_dev`: SPI DBI transport, optional reset/power state from helpers, rotation, backlight, and tx buffer. Hardware state persists in controller registers, notably MADCTL rotation and gamma/power setup. There is no local framebuffer state; common MIPI DBI helpers handle damage flushing.

Dependencies and integration points: Binds to `adafruit,yx350hv15` OF compatible or `yx350hv15` SPI ID. Depends on GPIO, SPI, backlight, DRM MIPI DBI, GEM DMA vmap helpers, fbdev DMA, and debugfs via `mipi_dbi_debugfs_init`.

Risks: Init command errors are not individually checked after most `mipi_dbi_command()` calls. Rotation mapping must match panel wiring. Required `dc` GPIO means platforms without a D/C line cannot bind. Timing delays are fixed and may be marginal on unusual hardware.

Test signals: Test boot/probe on matching DT, rotation 0/90/180/270, backlight enable after atomic enable, damage updates through DBI helpers, suspend/remove shutdown, and debugfs command/read behavior on SPI-capable panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/hx8357d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9163.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9163.c

Purpose: This SPI DRM driver supports Newhaven 1.8-inch 128x160 panels using the Ilitek ILI9163 controller. It follows the standard MIPI DBI tiny-driver pattern with fixed mode, primary plane, SPI connector, DMA GEM buffers, and a controller-specific power/gamma/frame-rate init sequence.

Important APIs, types, and functions: `struct ili9163_device` embeds `mipi_dbi_dev` and KMS objects. `ili9163_crtc_helper_atomic_enable()` performs conditional reset, sends gamma, frame-rate, power, VCOM, pixel-format, sleep-exit, display-on, MADCTL rotation/BGR setup, and backlight enable. Probe uses `mipi_dbi_spi_init()`, `drm_mipi_dbi_dev_init()`, and common `DRM_MIPI_DBI_*` plane/CRTC/connector/mode config helpers.

Control flow: Probe stores SPI drvdata early, gets optional reset and dc GPIOs, resolves backlight, reads `rotation`, initializes SPI DBI, initializes fixed 128x160 mode, configures exact mode bounds and preferred 16-bpp depth, builds KMS objects, registers DRM, and starts client setup. Atomic enable is entered under `drm_dev_enter()`, optionally runs hardware initialization, then always programs the rotation address mode and enables backlight. Remove and shutdown unplug and atomic-shutdown the DRM device.

State and persistence: Persistent software state is inherited from `mipi_dbi_dev`: rotation, SPI transport, backlight, GPIOs, tx buffer, and mode. Hardware state includes ILI9163 power/VCOM/gamma/register settings and MADCTL orientation. No private framebuffer cache is kept in this file.

Dependencies and integration points: Binds to `newhaven,1.8-128160EF` or `nhd-1.8-128160EF`. Integrates with SPI, optional reset/dc GPIOs, backlight lookup, MIPI DCS command definitions, DRM GEM DMA vmap helpers, fbdev DMA, and MIPI DBI KMS helpers.

Risks: Optional `dc` is passed to `mipi_dbi_spi_init()`; command/data transport must still be supported by the hardware and helper path. Init command return values are not checked after most commands. The fixed mode and exact mode bounds reject any alternative timings. Rotation/BGR bit choices are panel-specific and can produce mirrored output if DT rotation is wrong.

Test signals: Validate fixed 128x160 mode exposure, all rotation values, reset GPIO sequencing through DBI helper, backlight enable, RGB565/XRGB8888 client startup path through DBI helpers, damage flushing, and remove/shutdown with active CRTC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9163.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9225.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9225.c

Purpose: This SPI DRM driver supports VOT V220HF01A-T/Ilitek ILI9225 176x220 panels. Unlike most DBI tiny drivers, it customizes both the DBI command transport and dirty-rectangle upload path because this controller uses 16-bit register/data commands and rotation-specific GRAM window programming.

Important APIs, types, and functions: `struct ili9225_device` wraps `mipi_dbi_dev` and KMS objects. `ili9225_command()` sends one 16-bit parameter for a controller register. `ili9225_fb_dirty()` converts/copies framebuffer damage when needed, maps damage rectangles through rotation, programs horizontal/vertical window and RAM address registers, and writes GRAM. `ili9225_plane_helper_atomic_update()` invokes this dirty path. `ili9225_dbi_command()` overrides the generic MIPI DBI SPI command function to send commands separately from data and use 16 bits per word for GRAM payloads when possible.

Control flow: Probe requires reset and `rs` GPIOs, reads rotation, initializes DBI over SPI, replaces `dbi->command`, initializes the fixed mode, sets up exact mode limits, creates plane/CRTC/encoder/SPI connector, registers DRM, stores drvdata, and starts client setup. Atomic enable hardware-resets the panel, sends a multistage power-up sequence, applies rotation-specific entry mode bits, initializes scan/window/gamma registers, and finally enables display. Atomic disable writes display and power-down commands without `drm_dev_enter()` so normal unload can still turn off the panel.

State and persistence: Software state is mostly DBI helper state plus fixed mode and rotation. The driver maintains no cached framebuffer; it relies on shadow-plane maps and conversion state. Hardware persistence includes ILI9225 GRAM window registers, entry mode rotation bits, gamma table, power control registers, and display control state.

Dependencies and integration points: Binds to `vot,v220hf01a-t`/`v220hf01a-t`. Uses SPI bus locking, GPIO D/C control through `rs`, DRM shadow-plane helpers, MIPI DBI plane checks, GEM DMA vmap/fbdev helpers, dma-buf namespace import, and MIPI DCS definitions.

Risks: The custom dirty path has hand-coded coordinate transforms; off-by-one rotation errors would corrupt update windows. It uses `src->vaddr` directly when no conversion is needed. Most init commands after the first are not error-checked. The disable path intentionally lacks dev-enter protection and assumes SPI remains available during normal shutdown.

Test signals: Test full-screen and partial damage for all rotations, RGB565 and XRGB8888 conversion paths, swap-bytes behavior, GRAM 16-bit transfer path, active disable/unload, and fixed 176x220 mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9225.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9341.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9341.c

Purpose: This SPI DRM driver supports Adafruit YX240QV29 240x320 panels using the Ilitek ILI9341 controller. It provides a fixed SPI connector, DBI-based primary plane/CRTC, and controller-specific power/gamma/display initialization.

Important APIs, types, and functions: `struct ili9341_device` wraps `mipi_dbi_dev` with KMS objects. `ili9341_crtc_helper_atomic_enable()` is the custom enable hook: it conditionally resets/powers the panel, disables display, programs power sequence, driver timing, pump, power/VCOM, pixel format, frame rate, gamma tables, DDRAM mode, display control, sleep exit, display on, rotation MADCTL plus BGR, and backlight enable. Other operations use common `DRM_MIPI_DBI_*` helpers.

Control flow: Probe allocates managed DRM state, gets optional reset/dc GPIOs, finds backlight, reads rotation, initializes SPI DBI, initializes fixed 240x320 mode, sets exact mode bounds and 16-bpp preferred depth, creates the primary plane, CRTC, encoder, and SPI connector, resets mode config, registers DRM, stores drvdata, and starts client setup. Atomic enable is guarded by `drm_dev_enter()` and avoids rerunning the init table when the display is already powered.

State and persistence: Persistent state lives in DBI helper structures: rotation, GPIOs, backlight, transport, tx buffer, and mode. Hardware controller state persists across display-on cycles on some boards, so the enable hook always reapplies MADCTL rotation after conditional reset.

Dependencies and integration points: Binds to `adafruit,yx240qv29` or `yx240qv29`. Uses SPI, optional GPIOs, backlight, MIPI DCS/DBI helpers, GEM DMA vmap helpers, fbdev DMA, DRM managed object lifetime, and debugfs through `mipi_dbi_debugfs_init`.

Risks: Command return values are not checked individually. Fixed init values are panel-board-specific. Incorrect rotation property maps to mirrored or rotated output. The exact mode bounds prevent alternate timings or panel variants without code changes.

Test signals: Validate probe and display enable on matching DT, 0/90/180/270 rotation, backlight behavior, suspend/remove shutdown, RGB565 fbdev startup, XRGB8888 damage conversion through DBI helpers, and debugfs register access when reads are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9486.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9486.c

Purpose: This SPI DRM driver supports Waveshare/PiScreen 3.5-inch displays with an ILI9486 controller behind an SPI-to-16-bit parallel bus converter. It uses MIPI DBI KMS helpers but overrides command transport so controller commands and parameters are expanded/swapped for the converter.

Important APIs, types, and functions: `struct ili9486_device` embeds `mipi_dbi_dev` and KMS objects. `waveshare_command()` allocates a temporary big-endian 16-bit buffer, sends the command as two 8-bit bytes, expands short configuration parameters to 16-bit bus words, and uses 16 bits per word for memory writes when byte swapping is not required. `ili9486_crtc_helper_atomic_enable()` sends ILI9486 initialization commands, gamma tables, display-on, rotation MADCTL mapping, and backlight enable.

Control flow: Probe requires reset and dc GPIOs, finds backlight, reads rotation, initializes SPI DBI, replaces `dbi->command` with `waveshare_command`, disables read commands, initializes fixed 480x320 mode, creates exact mode config and KMS objects, registers DRM, stores drvdata, and starts client setup. Atomic enable conditionally resets/powers the panel, programs the controller, then always applies rotation and backlight. Remove and shutdown use DRM unplug and atomic shutdown.

State and persistence: Software state is DBI helper state plus the overridden command callback. Hardware persistence includes converter/controller command formatting assumptions, ILI9486 gamma/power/interface registers, and MADCTL rotation. No local framebuffer cache exists; DBI helper upload paths perform conversion and transfer.

Dependencies and integration points: Binds to `waveshare,rpi-lcd-35`, `ozzmaker,piscreen`, or SPI IDs `ili9486`, `rpi-lcd-35`, `piscreen`. Uses SPI bus locking, GPIO D/C, backlight, MIPI DBI/DCS helpers, DRM GEM DMA vmap helpers, fbdev DMA, and managed DRM lifetime.

Risks: `waveshare_command()` allocates memory on every command and assumes short config payloads are no more than 32 bytes for expansion. Reads are disabled, so diagnostics and readback-dependent helpers cannot work. Rotation mapping is unusual because of board wiring/converter orientation. Init command errors are mostly ignored by the enable hook.

Test signals: Validate command formatting on a Waveshare/PiScreen adapter, large memory-write path with 16-bpp pixels, all rotation values, read-command-disabled behavior, fixed 480x320 mode, backlight enable, and active remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/ili9486.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/mi0283qt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/mi0283qt.c

Purpose: This SPI DRM driver supports Multi-Inno MI0283QT 320x240 panels, using ILI9341-style command definitions with board-specific initialization. It follows the MIPI DBI tiny-driver pattern but includes a required power regulator and system sleep PM hooks.

Important APIs, types, and functions: `struct mi0283qt_device` wraps `mipi_dbi_dev` and KMS objects. `mi0283qt_crtc_helper_atomic_enable()` runs conditional DBI power/reset, sends power sequence, timing, pump, power/VCOM, pixel-format, frame-rate, gamma, DDRAM, display-control, sleep-exit, display-on, rotation MADCTL, and backlight commands. Probe uses `devm_regulator_get(dev, "power")`, `mipi_dbi_spi_init()`, `drm_mipi_dbi_dev_init()`, and common DBI KMS helpers.

Control flow: Probe gets optional reset/dc GPIOs, requires the `power` regulator and backlight, reads rotation, initializes SPI DBI and the fixed mode, configures exact mode bounds and preferred 16-bpp depth, builds plane/CRTC/encoder/SPI connector, registers DRM, stores drvdata, and starts client setup. The enable hook always reapplies rotation because some PiTFT/ili9340-style boards only reset on power-on. PM suspend/resume delegates to DRM mode-config helpers.

State and persistence: Persistent state is in DBI helper data: regulator, backlight, rotation, SPI transport, optional GPIOs, and mode. Hardware state can persist across reboot-like sequences if reset GPIO does not fully reset the panel, which is why MADCTL is always set on enable.

Dependencies and integration points: Binds to `multi-inno,mi0283qt` or `mi0283qt`. Integrates with regulator, backlight, SPI, optional GPIOs, MIPI DBI/DCS, DRM GEM DMA vmap/fbdev helpers, debugfs, and system sleep PM.

Risks: Missing `power` regulator fails probe. Init commands are not individually checked. Panel-specific gamma/power values may not suit close variants. Exact mode bounds forbid alternate timings. Resume returns success after calling helper resume but does not propagate possible errors.

Test signals: Probe with regulator/backlight present, suspend/resume cycle, rotation mapping after resume, RGB565 client setup, damage uploads through DBI helpers, shutdown/remove while active, and behavior when optional reset/dc GPIOs are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/mi0283qt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/panel-mipi-dbi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/panel-mipi-dbi.c

Purpose: This is a generic SPI DRM driver for MIPI DBI-compatible display panels whose mode, pixel format, and controller initialization sequence are supplied by device tree plus a firmware binary. It avoids a panel-specific C file for simple DBI panels while preserving the standard tiny DRM KMS object layout.

Important APIs, types, and functions: `struct panel_mipi_dbi_config` defines the firmware format: 15-byte magic, version, and command stream. `panel_mipi_dbi_check_commands()` validates magic, version, command lengths, and delay encoding. `panel_mipi_dbi_commands_from_fw()` names firmware as `<first-compatible>.bin`. `panel_mipi_dbi_commands_execute()` runs commands, treating DCS NOP with one parameter as a millisecond delay. `panel_mipi_dbi_get_mode()` parses `panel-timing`, constrains timing fields to DBI-compatible bounds, and sets DBI offsets. `panel_mipi_dbi_get_format()` maps DT `format` strings to RGB565 or RGB888 plus XRGB8888 fallback.

Control flow: SPI probe allocates DRM/DBI state, parses the fixed panel mode, gets `power` and `io` regulators, backlight, optional reset and nonexclusive dc GPIO, initializes SPI DBI, optionally disables reads for `write-only`, loads/validates firmware commands, determines format and tx buffer size, initializes DBI device state, creates exact mode config and KMS objects, registers DRM, stores drvdata, and starts client setup with RGB565 or RGB888 fourcc. Atomic enable powers/resets through DBI helpers, executes firmware commands only after a real reset/power-on, and enables backlight.

State and persistence: Persistent state includes DBI helper state, regulators, optional GPIOs, backlight, mode offsets, pixel format/bpp, tx buffer, and `driver_private` command list. Hardware state comes entirely from the firmware command stream plus DBI power/reset helper behavior.

Dependencies and integration points: Binds to `panel-mipi-dbi-spi`. Depends on OF `panel-timing`, firmware loader, regulators named `power` and `io`, backlight, SPI, MIPI DBI helpers, DRM GEM DMA vmap/fbdev helpers, and system sleep PM. Multiple panels may share a dc GPIO only when on the same SPI bus due to nonexclusive GPIO acquisition.

Risks: Missing or malformed firmware prevents probe. The firmware name is derived from the first compatible string and limited by the local buffer. Only simple timing shapes are accepted: width/height required, no flags, no front/sync values beyond back porch and pixel clock semantics. Firmware commands are trusted after validation but not semantically checked. Write-only panels lose readback/debug capability.

Test signals: Validate firmware magic/version/overflow rejection, delay command execution, RGB565 and RGB888 format selection, old DT default format path, panel-timing bounds, write-only mode, regulator/backlight sequencing, suspend/resume, and successful split between multiple compatibles with distinct firmware files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/panel-mipi-dbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/pixpaper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/pixpaper.c

Purpose: This custom SPI DRM driver supports the Mayqueen PIXPAPER color e-ink panel. It exposes a fixed 122x250 XRGB8888 DRM display while programming a 128-pixel-wide e-paper controller buffer and converting each visible pixel into a 2-bit white/black/yellow/red packed format.

Important APIs, types, and functions: `struct pixpaper_panel` owns DRM objects, SPI device, and reset/busy/dc GPIOs. `pixpaper_wait_for_panel()` polls the busy GPIO with a 10-second timeout. `pixpaper_send_cmd()` and `pixpaper_send_data()` send one-byte SPI transactions with D/C GPIO control and an error accumulator. `pixpaper_panel_hw_init()` resets the panel and writes a long sequence of documented and reverse-engineered registers. `pack_pixels_to_byte()` thresholds XRGB8888 pixels into four 2-bit panel pixels per byte. `pixpaper_plane_atomic_update()` streams the packed frame and triggers power-on/display refresh.

Control flow: Probe allocates DRM state, forces SPI mode 0 and 8 bits per word, applies a default SPI speed if DT omitted it, sets a 32-bit DMA mask, gets reset/busy/dc GPIOs, performs hardware init immediately, initializes DRM mode config, creates a shadow primary plane for XRGB8888, CRTC, encoder, SPI connector, registers DRM, and starts client setup. CRTC enable sends power-on and waits. CRTC disable sends power-off. Plane update enters the DRM device, validates framebuffer visibility, sends data-start, loops over all 250 rows and 32 bytes per row, sends packed bytes with busy waits, powers on, and sends display-refresh with AC VCOM.

State and persistence: Software state is mostly DRM state plus GPIO/SPI handles; there is no cached previous frame or partial update tracking. Hardware state includes the many power/PLL/resolution/VCOM/timing/unknown registers, panel power state, and e-paper image memory. Error propagation is stored in a small `pixpaper_error_ctx` during command sequences.

Dependencies and integration points: Binds to `mayqueen,pixpaper` or `pixpaper`. Uses SPI, GPIO reset/busy/dc, DRM shmem helpers, shadow-plane helpers, fixed connector modes, fbdev shmem, and DMA mask setup. The driver imports the DMA_BUF namespace.

Risks: Several register values are explicitly undocumented and derived from userspace examples; changing them can destabilize or damage panels. Busy-wait timeout only warns in `pixpaper_wait_for_panel()` and then continues. Color thresholds are simplistic and map unknown colors to white. Plane update performs full-frame synchronous SPI transfer for every damage event. Initialization occurs at probe, so failed panel hardware blocks DRM registration.

Test signals: Validate hardware init sequence on real panel, busy timeout diagnostics, full-frame update timing, color threshold mapping for black/white/red/yellow, fixed 122x250 mode with 128-byte row padding, power on/off commits, default SPI speed fallback, and remove with active display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/pixpaper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/repaper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/repaper.c

Purpose: This SPI DRM driver supports Pervasive Displays RePaper branded monochrome e-ink panels using the G2 COG controller. It exposes several fixed-size panel models, converts XRGB8888 to mono, and drives multi-stage e-paper update waveforms with temperature-dependent timing.

Important APIs, types, and functions: `struct repaper_epd` stores DRM simple-pipe objects, SPI/GPIOs, optional thermal zone, model geometry, channel-select table, stage timing, line buffer, current mono frame, and update state flags. SPI helpers `repaper_spi_transfer()`, `repaper_write_buf()`, `repaper_write_val()`, `repaper_read_val()`, and `repaper_read_id()` implement the controller protocol. Pixel staging helpers `repaper_even_pixels()`, `repaper_odd_pixels()`, `repaper_all_pixels()`, and `repaper_one_line()` construct controller line buffers. `repaper_fb_dirty()` converts the framebuffer to mono and performs clear/full/partial waveform sequences.

Control flow: Probe determines model from OF or SPI ID, coerces a 32-bit DMA mask if needed, allocates DRM state, initializes mode config, acquires panel-on/discharge/reset/busy and optional border GPIOs, resolves optional thermal zone, selects model mode/channel/timing/layout, allocates line/current-frame buffers, creates SPI connector and simple display pipe, registers DRM, and starts client setup. Pipe enable powers up GPIOs, toggles reset, waits for busy, checks COG ID, verifies status, writes channel/power/oscillator registers, starts charge pumps, and marks the next update non-partial. Pipe update converts and runs waveform stages. Pipe disable writes a nothing frame, border handling, powers down charge pumps/oscillator, and discharges the panel.

State and persistence: Persistent software state includes current mono frame for partial updates, `cleared` and `partial` flags, temperature-factored stage time, model geometry, line buffer, and GPIO state. Hardware state includes COG power rails, charge pumps, display memory, border state, and panel waveform history, which makes correct sequencing important.

Dependencies and integration points: Binds to four `pervasive,*` compatibles or SPI IDs. Uses SPI, GPIOs, optional Linux thermal zone named by `pervasive,thermal-zone`, DRM simple KMS, GEM DMA vmap/fbdev helpers, shadow-plane helpers, mono conversion helpers, and fixed connector modes.

Risks: E-paper waveform timing is temperature-sensitive; missing/failed thermal reads fall back to prior timing. The driver cannot do true partial dirty rectangles, so it always converts/updates the full frame. SPI transfer allocates bounce buffers for headers/short stack data. The disable path intentionally skips `drm_dev_enter()` and assumes SPI is still usable. Incorrect model selection would break line buffer layout/channel select and panel safety.

Test signals: Validate each model geometry and channel-select table, COG ID read, charge-pump DC/DC success path and failure path, temperature timing factors, first clear sequence, subsequent partial update against `current_frame`, bottom-line extra-frame quirk, border GPIO handling, and shutdown discharge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/repaper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/sharp-memory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/sharp-memory.c

Purpose: This SPI DRM driver supports multiple Sharp Memory LCD panels. It exposes fixed model modes, converts XRGB8888 framebuffer lines to monochrome, sends Sharp memory-display update/clear/maintain messages, and supports software, external, or PWM VCOM generation.

Important APIs, types, and functions: `struct sharp_memory_device` owns DRM objects, SPI handle, mode, optional enable GPIO, VCOM state, optional software kthread or PWM, tx buffer metadata, and a mutex for SPI/tx-buffer synchronization. `sharp_memory_spi_write()` reverses bit order in-place before `spi_write()`, matching the panel protocol. `sharp_memory_update_display()`, `sharp_memory_maintain_display()`, and `sharp_memory_clear_display()` build command buffers. `sharp_memory_fb_dirty()` expands any dirty rectangle to full lines. `sharp_memory_sw_vcom_signal_thread()` toggles the VCOM bit once per second in software mode.

Control flow: Probe sets up SPI, coerces 32-bit DMA if needed, allocates DRM state, stores drvdata, initializes mode config, gets optional enable GPIO, selects mode from SPI/OF match data, computes pitch and tx buffer size, initializes the mutex, parses required `sharp,vcom-mode`, starts a software VCOM kthread or PWM if requested, sets exact mode bounds, initializes plane/CRTC/encoder/SPI connector, enables damage clips, registers DRM, and starts client setup. CRTC enable clears display and asserts enable GPIO; disable clears and deasserts. Plane update merges damage and sends line updates only while CRTC is active. Remove unplugs/shuts down DRM and stops VCOM generation.

State and persistence: Persistent software state includes selected mode, VCOM mode, current VCOM bit, tx buffer contents, mutex, optional kthread/PWM, and enable GPIO. Hardware state includes display memory, VCOM drive, and panel enable. Because `sharp_memory_spi_write()` bit-reverses the buffer in-place, callers repopulate command/data before each transfer.

Dependencies and integration points: Binds to many Sharp `ls*` SPI IDs and OF compatibles. Uses SPI, GPIO, PWM, kthread, bit reversal, DRM GEM DMA vmap/fbdev helpers, shadow-plane helpers, mono conversion helpers, fixed connector modes, and the `sharp,vcom-mode` DT property.

Risks: Missing or invalid `sharp,vcom-mode` fails probe. Software VCOM thread starts before DRM registration and must be stopped on remove; failed `kthread_run()` is not explicitly checked as an error pointer. In-place bit reversal means tx buffer data cannot be reused after write without repopulation. Dirty updates always cover full lines, not arbitrary rectangles. PWM disable is manual on remove.

Test signals: Validate every model match-data mode, software/external/PWM VCOM paths, kthread stop on remove, line-damage expansion, bit-reversed SPI command bytes, clear on enable/disable, enable GPIO polarity, and XRGB8888-to-mono conversion for full and partial-line updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tiny/sharp-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/Makefile

Purpose: This kbuild file defines the object composition of the DRM TTM memory-management module and wires optional TTM KUnit tests into the build.

Important APIs, types, and functions: The primary kbuild variable is `ttm-y`, which collects core TTM object files: translation tables, buffer objects, buffer-object utilities and VM integration, module glue, execbuf utilities, range/resource/pool/device/system managers, and backup handling. `ttm-$(CONFIG_AGP)` conditionally adds `ttm_agp_backend.o`. `obj-$(CONFIG_DRM_TTM) += ttm.o` builds the aggregate module/object when TTM is enabled. `obj-$(CONFIG_DRM_TTM_KUNIT_TEST) += tests/` descends into the test directory when configured.

Control flow: Kbuild expands `ttm-y` into the linked contents of `ttm.o`. If AGP support is enabled, the AGP backend becomes part of that aggregate. If `CONFIG_DRM_TTM` is not enabled, no core TTM object is emitted from this Makefile. If KUnit testing is enabled, the nested tests Makefile is processed independently.

State and persistence: There is no runtime state in the Makefile. The persistent contract is build composition: changing object order or conditional membership changes what symbols are linked into `ttm.o` and whether tests are visible to KUnit.

Dependencies and integration points: Integrates with Linux kbuild, `CONFIG_DRM_TTM`, `CONFIG_AGP`, and `CONFIG_DRM_TTM_KUNIT_TEST`. Source objects named here implement the shared TTM API used by DRM drivers such as amdgpu, nouveau, i915, qxl, and others.

Risks: Omitting an object from `ttm-y` can create link-time missing symbols or subtler feature loss. Adding test descent without the right config would increase build scope unexpectedly. The AGP backend is correctly conditional; making it unconditional would break non-AGP builds.

Test signals: Build matrices should cover DRM_TTM as built-in and module, AGP enabled/disabled, and KUnit test enabled/disabled. Link output should contain exactly the expected TTM objects for each config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/Makefile

Purpose: This kbuild file lists the KUnit test objects for DRM TTM. It is entered from the parent TTM Makefile when `CONFIG_DRM_TTM_KUNIT_TEST` is enabled.

Important APIs, types, and functions: The only rule appends several objects to `obj-$(CONFIG_DRM_TTM_KUNIT_TEST)`: `ttm_device_test.o`, `ttm_pool_test.o`, `ttm_resource_test.o`, `ttm_tt_test.o`, `ttm_bo_test.o`, `ttm_bo_validate_test.o`, `ttm_mock_manager.o`, and `ttm_kunit_helpers.o`. The first six are test suites; the last two provide shared mock manager/helper infrastructure used by those suites.

Control flow: Kbuild compiles and links these test objects only when the KUnit config is selected. Because the parent directory already gates traversal on the same config, this file is doubly guarded by the config variable.

State and persistence: There is no runtime state. The durable effect is the test build manifest: adding/removing an object changes which TTM behavior receives KUnit coverage and which helper symbols are available to test suites.

Dependencies and integration points: Integrates with Linux kbuild and KUnit. The tests depend on the parent TTM core build products and local mock/helper objects. The SPDX line indicates GPL-2.0 and MIT licensing for the test build file.

Risks: Removing `ttm_mock_manager.o` or `ttm_kunit_helpers.o` can break multiple suites at link time. Adding a new test source without listing it here leaves it unbuilt. Because this file is config-gated, test failures may be invisible in non-KUnit build matrices.

Test signals: Enable `CONFIG_DRM_TTM_KUNIT_TEST` and run the KUnit suites for device, pool, resource, TT, BO, and BO validation. Also run a non-KUnit build to confirm the test directory contributes no objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/Makefile -->
