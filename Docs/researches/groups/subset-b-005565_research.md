# subset-b-005565 Research

Grouped source research for framebuffer drivers in `sources/distributed-fs/ceph-client/drivers/video/fbdev`, covering the N411 Hecuba board shim, NeoMagic PCI framebuffer, OpenCores/Open Firmware framebuffer drivers, the NVIDIA fbdev driver family, and OMAP fbdev build configuration. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/n411.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/n411.c

## Purpose

`n411.c` is a small board-specific platform-device shim for the N411 Hecuba/Apollo electronic paper display kit. It adapts module-supplied I/O port addresses for data/control GPIO lines into the generic `hecubafb` board callback interface, then instantiates a `hecubafb` platform device with those callbacks. The source was read as a complete 208-line file.

## Important APIs, Types, and Functions

The key integration object is `static struct hecuba_board n411_board`, populated with `.init`, `.set_ctl`, `.set_data`, and `.wait_for_ack`. `n411_set_ctl()` drives `HCB_CD_BIT` and `HCB_DS_BIT` using inverted port values and the global `ctl` latch. `n411_get_ctl()` reads the secondary control port, `n411_set_data()` writes the data port, and `n411_wait_for_ack()` polls `HCB_ACK_BIT` with a short `udelay(1)` loop. `n411_init_control()` validates initial ACK state and seeds WUP/RW/CD/DS control bits; `n411_init_board()` sends `APOLLO_INIT_DISPLAY` and optionally `APOLLO_ERASE_DISPLAY`. `n411_init()` validates `dio_addr`, `cio_addr`, and `c2io_addr`, requests `hecubafb`, allocates the platform device, attaches board data, and registers it. Module parameters are `nosplash`, `dio_addr`, `cio_addr`, `c2io_addr`, and `splashval`.

## Control Flow

Module load fails early unless all three I/O addresses are provided. It requests the generic `hecubafb` module, allocates a `platform_device` named `hecubafb`, copies `n411_board` into platform data, and adds the device. The generic Hecuba driver later calls back into this file to initialize the controller, toggle control lines, output data bytes, and wait for ACK transitions. Module exit unregisters the platform device.

## State and Persistence Behavior

No persistent storage is used. Global module state consists of I/O addresses, `splashval`, `nosplash`, and the `ctl` byte that mirrors the current control latch sent to `cio_addr`. Hardware-visible state is the current external GPIO/control state and the display contents after optional erase/splash initialization.

## Dependencies and Integration Points

The file depends on legacy port I/O (`inb`, `outb`), module parameters with `module_param_hw(..., ioport, ...)`, and `video/hecubafb.h` for command constants and board callback definitions. Its only runtime consumer is the generic `hecubafb` platform driver, which must bind to the platform device and interpret the supplied `hecuba_board`.

## Risks and Edge Cases

The ACK wait path times out after roughly 500 microseconds and only logs an error; it cannot report failure to the caller because the callback returns `void`. Control-line polarity is encoded in `n411_set_ctl()`, so wrong board wiring or incorrect module I/O addresses can silently drive the wrong pins. I/O ports are not requested in this shim, so conflicts rely on module parameter discipline and lower layers. The splash erase sends `splashval` without clamping to the documented 0/1 values.

## Test Signals

Useful signals are build coverage with `CONFIG_FB_HECUBA`/`n411`, module-load failures when any I/O address is missing, successful `hecubafb` platform binding, ACK timeout logging on disconnected hardware, and a real-board smoke test that verifies `APOLLO_INIT_DISPLAY`, optional erase, data writes, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/n411.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/neofb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/neofb.c

## Purpose

`neofb.c` is a PCI fbdev driver for NeoMagic MagicGraph chips from NM2070 through NM2380. It provides VGA-compatible mode programming, LCD/CRT routing, panel stretching/centering, framebuffer and MMIO mapping, colormap management, panning, blanking/DPMS, VGA state save/restore, and hardware acceleration for Neo2200-class chips. The source was read as a complete 2227-line file.

## Important APIs, Types, and Functions

The driver uses `struct neofb_par`, `Neo2200`, `biosMode`, and `NEO_BC*` constants from `include/video/neomagic.h`. User-facing fbdev operations are collected in `neofb_ops`: `neofb_open`, `neofb_release`, `neofb_check_var`, `neofb_set_par`, `neofb_setcolreg`, `neofb_pan_display`, `neofb_blank`, `neofb_sync`, `neofb_fillrect`, `neofb_copyarea`, and `neofb_imageblit`. Mode support is driven by `neoFindMode()` BIOS-mode tables and `neoCalcVCLK()` PLL search. VGA register generation/restoration is handled by `vgaHWInit()`, `vgaHWProtect()`, `vgaHWRestore()`, `neoUnlock()`, and `neoLock()`. Neo2200 acceleration is implemented by `neo2200_accel_init()`, `neo2200_sync()`, `neo2200_fillrect()`, `neo2200_copyarea()`, and `neo2200_imageblit()`. Probe/remove are `neofb_probe()` and `neofb_remove()`, registered through `neofb_driver` and the `neofb_devices` PCI ID table.

## Control Flow

Module/init command-line parsing sets `internal`, `external`, `libretto`, `nostretch`, `nopciburst`, and `mode_option`, then registers the PCI driver unless global modesetting is disabled. Probe removes conflicting apertures, enables the PCI device, allocates `fb_info`, maps MMIO, reads NeoMagic display/panel registers, derives VRAM/clock/cursor capabilities, maps framebuffer memory, chooses an initial mode, allocates a cmap, and registers the framebuffer. `neofb_check_var()` validates dot clock, panel dimensions, supported LCD mode sizes, color layout, and available VRAM. `neofb_set_par()` unlocks NeoMagic extended registers, blanks the display, computes VGA and extended register values, configures LCD/CRT routing, stretching and centering, computes VCLK3, restores VGA state, programs palettes and NeoMagic extension registers, re-locks, updates line length, and initializes Neo2200 acceleration when available. Runtime fbdev calls pan by writing CRTC start address registers plus extended address bits, blank by combining VGA sequencer, LCD, and DPMS bits, and accelerate fill/copy/imageblit for Neo2200+ while falling back to `cfb_*` for unsupported chips or image formats. Remove unregisters the framebuffer, unmaps video/MMIO, frees the mode database and cmap, and releases the `fb_info`.

## State and Persistence Behavior

Per-device state lives in `struct neofb_par`: saved VGA state/refcount, panel size, LCD/CRT routing, stretching/centering registers, PLL parameters, PCI burst flag, `neo2200` MMIO pointer, pseudo palette, and write-combining cookie. The driver saves VGA mode/fonts on first open and restores them on last release. It does not persist data across unloads; persistent effects are limited to hardware registers and framebuffer contents while the device is active. `PanelDispCntlRegRead` is used to preserve Fn-key or firmware display routing changes across blank/unblank cycles.

## Dependencies and Integration Points

The driver integrates with PCI, aperture conflict removal, fbdev core APIs, generic VGA helpers, architecture I/O port access, write-combined framebuffer mapping, and optional Toshiba SMM backlight hooks under `CONFIG_TOSHIBA`. It relies on `vesa_modes`, `fb_find_mode`, and the NeoMagic hardware header for register layout and blitter constants. Acceleration depends on MMIO layout for NM2200/NM2230/NM2360/NM2380.

## Risks and Edge Cases

The code programs legacy VGA I/O ports and NeoMagic extension registers directly, so it is sensitive to primary-display assumptions, firmware state, and concurrent firmware hotkeys. `neo2200_sync()` spins without a timeout, which can hang if the blitter never clears busy. `neofb_check_var()` silently reduces virtual or visible resolution to fit VRAM rather than always rejecting, which can surprise callers. Hardware acceleration has known 24-bpp mono image constraints and falls back for narrow images. Some features are explicitly unfinished, including 32-bpp support and hardware cursor support. Panel detection supports only 640x480, 800x600/480, and 1024x768 panels unless disabled.

## Test Signals

Important coverage includes PCI probe/remove for every listed NeoMagic ID, mode validation for LCD-only and CRT-only paths, Libretto 800x480 mode selection, blank/unblank and DPMS register behavior, first-open/last-release VGA restore, panning after X or console use, accelerated fill/copy/imageblit on NM2200+ with software fallback comparison, and suspend-like hotkey display-route changes across blank/unblank.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/neofb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/Makefile

## Purpose

This Makefile defines the object composition for the legacy NVIDIA fbdev driver. It builds `nvidiafb.o` when `CONFIG_FB_NVIDIA` is enabled and conditionally includes I2C and backlight support. The source was read as a complete 13-line file.

## Important APIs, Types, and Functions

The important build variables are `obj-$(CONFIG_FB_NVIDIA) += nvidiafb.o`, `nvidiafb-y`, `nvidiafb-$(CONFIG_FB_NVIDIA_I2C)`, `nvidiafb-$(CONFIG_FB_NVIDIA_BACKLIGHT)`, and `nvidiafb-objs`. The base object list is `nvidia.o nv_hw.o nv_setup.o nv_accel.o nv_of.o`; optional pieces are `nv_i2c.o` and `nv_backlight.o`.

## Control Flow

There is no runtime flow. Kbuild resolves the object list from configuration symbols, compiles the selected sources, and links them into one `nvidiafb.o` module or built-in object.

## State and Persistence Behavior

The file owns no runtime state. Its state is build-time object selection based on Kconfig symbols.

## Dependencies and Integration Points

It integrates with Linux Kbuild and the `CONFIG_FB_NVIDIA`, `CONFIG_FB_NVIDIA_I2C`, and `CONFIG_FB_NVIDIA_BACKLIGHT` symbols. The unconditional inclusion of `nv_of.o` means Open Firmware EDID probing is always linked into the NVIDIA fbdev driver, while I2C/backlight functionality is gated by config.

## Risks and Edge Cases

The object grouping must match declarations in `nv_proto.h`; enabling a prototype without linking the corresponding object would create link failures, while missing optional stubs would break configurations without I2C/backlight. Because `nvidiafb-objs := $(nvidiafb-y)` aliases a conditional variable, changes must preserve Kbuild's expected `*-objs` naming.

## Test Signals

Build-test `CONFIG_FB_NVIDIA=y/m` with and without `CONFIG_FB_NVIDIA_I2C` and `CONFIG_FB_NVIDIA_BACKLIGHT`, and verify that `nvidiafb.o` links with no unresolved references in each combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_accel.c

## Purpose

`nv_accel.c` implements 2D acceleration for `nvidiafb` by writing DMA command buffers in framebuffer memory and kicking the NVIDIA FIFO. It accelerates fbdev sync, copyarea, fillrect, and monochrome imageblit, with software fallbacks when the card locks up or an operation is unsupported. The source was read as a complete 418-line file.

## Important APIs, Types, and Functions

Exported entry points are `NVResetGraphics()`, `nvidiafb_sync()`, `nvidiafb_copyarea()`, `nvidiafb_fillrect()`, and `nvidiafb_imageblit()`. Internal helpers include `nvidiafb_safe_mode()` for lockup fallback, `NVFlush()` and `NVSync()` polling FIFO/PGRAPH idle state, `NVDmaKickoff()`, `NVDmaWait()`, `NVSetPattern()`, `NVSetRopSolid()`, `NVSetClippingRectangle()`, and `nvidiafb_mono_color_expand()`. It depends on DMA register tags from `nv_dma.h` and DMA macros from `nv_local.h`, especially `NVDmaStart`, `NVDmaNext`, `WRITE_PUT`, and `READ_GET`.

## Control Flow

`NVResetGraphics()` places the DMA command buffer after `FbUsableSize`, writes object/context setup entries with a `SKIPS` guard area, initializes FIFO pointers, chooses surface/pattern/rect/line formats from current bpp, sets pitch/offsets, installs default ROP and clipping, and kicks the FIFO. Runtime accelerated operations first ensure the fb is running and the driver is not in lockup mode. Copy writes source point, destination point, and size. Fill resolves the fbdev color to a packed color, optionally switches ROP, emits a solid rectangle command, and restores copy ROP. Mono imageblit emits color expansion setup and streams image data in chunks, reversing bit order on little-endian hosts. Sync waits for FIFO and PGRAPH idle.

## State and Persistence Behavior

The acceleration state is held in `struct nvidia_par`: DMA put/current/free/max counters, `dmaBase`, `currentRop`, `lockup`, and fbdev pixmap alignment. Hardware state persists in PRAMIN/PFIFO/PGRAPH objects initialized by `NVLoadStateExt()` and the command buffer region reserved at the end of framebuffer memory. If a timeout occurs, `lockup` is set, scan alignment is reduced, and later operations use `cfb_*` software paths.

## Dependencies and Integration Points

This file is called from `nvidiafb_set_par()` when acceleration is enabled and installed into `nvidia_fb_ops` for fbdev operations. It integrates with the NVIDIA register layout initialized by `nv_hw.c`, the framebuffer layout computed by `nvidia.c`, software fb helpers (`cfb_copyarea`, `cfb_fillrect`, `cfb_imageblit`), and the kernel softlockup watchdog.

## Risks and Edge Cases

The DMA wait/flush/sync loops use very large polling counts and only fall back after long busy waits. Correctness depends on reserving enough framebuffer tail memory for command buffers and cursor/scratch areas. DMA wraparound has a hardware race workaround using `SKIPS`; mistakes in put/get handling can wedge the engine. Mono imageblit assumes enough padded data and bit order conversion; non-1bpp imageblits fall back to software. Lockup fallback changes behavior dynamically and should be visible to tests.

## Test Signals

Useful tests compare accelerated and software output for copy, fill, invert ROP, and 1-bpp glyph/image paths at 8/16/24/32 bpp; force a simulated or hardware FIFO timeout and verify software fallback; run pan/mode-set followed by acceleration to validate pitch and clipping; and build with `CONFIG_FB_NVIDIA` across endian-sensitive architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_backlight.c

## Purpose

`nv_backlight.c` registers a raw backlight device for flat-panel NVIDIA displays and maps fbdev backlight levels to NVIDIA panel/backlight registers. The source was read as a complete 131-line file.

## Important APIs, Types, and Functions

The exported lifecycle functions are `nvidia_bl_init()` and `nvidia_bl_exit()`. The backlight operation is `nvidia_bl_update_status()` through `nvidia_bl_ops`. `nvidia_bl_get_level_brightness()` converts a fbdev brightness curve entry to a register value between `MIN_LEVEL` (`0x158`) and `MAX_LEVEL` (`0x534`) using `LEVEL_STEP`.

## Control Flow

Initialization returns immediately unless `par->FlatPanel` is true and, on PowerMac builds, the machine has the expected `"mnca"` backlight type. It registers a `backlight_device` named `nvidiabl<N>`, initializes `info->bl_curve`, sets brightness/power to maximum/on, and calls `backlight_update_status()`. Status updates read current PMC/PCRTC/PRAMDAC fields, either enable backlight and syncs with a scaled level or program a panel-off value, and write the updated registers. Exit unregisters `info->bl_dev`.

## State and Persistence Behavior

Runtime state is the fbdev `info->bl_dev`, `info->bl_curve`, and hardware register values in `PMC`, `PCRTC0`, and `PRAMDAC`. There is no file-backed persistence. The current brightness persists in hardware until changed, suspend/resume reprogramming, or driver removal.

## Dependencies and Integration Points

The file depends on the backlight subsystem, `struct nvidia_par` register mappings, `pci_get_drvdata()`, and optional PowerMac backlight detection. It is linked only with `CONFIG_FB_NVIDIA_BACKLIGHT` and called from `nvidiafb_probe()`/`nvidiafb_remove()` when the module parameter `backlight` allows it.

## Risks and Edge Cases

The register values are described as safe guesses, not fully documented limits. `nvidia_bl_exit()` unconditionally calls `backlight_device_unregister(bd)` with `info->bl_dev`; callers must avoid invoking it when no device was registered or rely on NULL-safe behavior. The update path ignores non-flat-panel devices and does not serialize with concurrent mode-setting beyond subsystem locking.

## Test Signals

Build-test with and without `CONFIG_FB_NVIDIA_BACKLIGHT`, probe a flat panel and verify `/sys/class/backlight/nvidiabl*` appears, exercise brightness 0/max/mid values, confirm CRT-only systems skip registration, and test suspend/resume or mode-set interactions that rewrite panel sync bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_dma.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_dma.h

## Purpose

`nv_dma.h` is a register/tag definition header for NVIDIA 2D DMA objects used by `nv_accel.c`. It names command offsets, depth encodings, bitfield positions, and data array limits for surface, ROP, pattern, clipping, line, blit, rectangle, color expansion, and stretch blit methods. The source was read as a complete 188-line file.

## Important APIs, Types, and Functions

There are no functions or types. Important macro groups include `SURFACE_*`, `ROP_SET`, `PATTERN_*`, `CLIP_*`, `LINE_*`, `BLIT_*`, `RECT_*`, `RECT_EXPAND_ONE_COLOR_*`, `RECT_EXPAND_TWO_COLOR_*`, and `STRETCH_BLIT_*`. Macros such as `SURFACE_PITCH_SRC 15:0` are intended for the bitfield helpers in `nv_type.h` (`SetBF`, `SetBitField`, etc.), while offset macros are sent through `NVDmaStart()`.

## Control Flow

No executable control flow exists. The header supplies symbolic constants consumed when acceleration code emits DMA method headers and payload words.

## State and Persistence Behavior

The file owns no state. Its constants describe hardware command-buffer layout; changing them changes how driver state is serialized into the GPU FIFO.

## Dependencies and Integration Points

It is included by `nv_accel.c` and `nvidia.c`, together with `nv_local.h` DMA macros. The constants must match the PRAMIN object setup performed in `NVLoadStateExt()` and the FIFO command stream expectations of supported NVIDIA architectures.

## Risks and Edge Cases

Macro values are hardware ABI. Incorrect offsets, duplicated/ambiguous definitions such as repeated `STRETCH_BLIT_CLIP_POINT`, or wrong data limits can corrupt FIFO commands or hang acceleration. Because the file has no type checking, callers must provide correct word counts to `NVDmaStart()`.

## Test Signals

Acceleration smoke tests are the real validation: fillrect, copyarea, mono imageblit, clipping, ROP, and pitch/offset behavior across bpp modes. Build coverage should also catch malformed macro use after edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_hw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_hw.c

## Purpose

`nv_hw.c` contains low-level NVIDIA hardware state calculation and register programming for `nvidiafb`. It handles VGA unlock/cursor visibility, clock discovery, FIFO arbitration heuristics, pixel-clock PLL calculation, extended CRTC/RAMDAC state generation, full graphics/FIFO object initialization, state save/restore, and CRTC start-address updates. The source was read as a complete 1688-line file.

## Important APIs, Types, and Functions

Exported functions are `NVLockUnlock()`, `NVShowHideCursor()`, `NVCalcStateExt()`, `NVLoadStateExt()`, `NVUnloadStateExt()`, and `NVSetStartAddress()`. Internal arbitration types include `nv4_fifo_info`, `nv4_sim_state`, `nv10_fifo_info`, and `nv10_sim_state`. Clock and FIFO helpers include `nvGetClocks()`, `nv4CalcArbitration()`, `nv4UpdateArbitrationSettings()`, `nv10CalcArbitration()`, `nv10UpdateArbitrationSettings()`, `nv30UpdateArbitrationSettings()`, `nForceUpdateArbitrationSettings()`, `CalcVClock()`, and `CalcVClock2Stage()`.

## Control Flow

Mode setup starts in `nvidia_calc_regs()` in `nvidia.c`, which calls `NVCalcStateExt()` to compute extended state from bpp, virtual width, visible dimensions, dot clock, and vmode flags. That routine chooses PLL calculation, architecture-specific FIFO arbitration, cursor register values, config/general bits, repaint and pixel-depth fields. `nvidia_write_regs()` later calls `NVLoadStateExt()`, which resets PMC/PTIMER/PFB/PGRAPH/PFIFO/PRAMIN objects, applies architecture- and chipset-specific graphics engine setup, then writes extended CRTC/RAMDAC fields from `RIVA_HW_STATE`. `NVUnloadStateExt()` reads the current extended state for saving. `NVSetStartAddress()` writes the display start register for panning.

## State and Persistence Behavior

State is represented by `RIVA_HW_STATE` instances in `struct nvidia_par`: `SavedReg`, `ModeReg`, `initial_state`, and `CurrentState`. Hardware-visible persistence includes programmed PLLs, CRTC registers, FIFO/object RAM entries, PGRAPH state, PRAMDAC flat-panel settings, cursor configuration, and framebuffer start address. The file also updates `CurrentState` so cursor show/hide can mutate the live state image.

## Dependencies and Integration Points

The file depends on register-bank pointers initialized by `NVCommonSetup()` in `nv_setup.c`, bitfield macros and architecture constants from `nv_type.h`, raw MMIO helpers from `nv_local.h`, and PCI config access for nForce arbitration. It is central to `nvidia.c` mode set, cursor, panning, suspend/resume, and acceleration setup; `nv_accel.c` assumes the graphics/FIFO objects initialized here are present.

## Risks and Edge Cases

Most register values are chipset-specific magic constants. Unsupported or misidentified architectures can program the wrong PRAMIN/PGRAPH/PFIFO layout. PLL calculation uses integer heuristics and must respect crystal frequency and two-stage PLL variants. Several PCI helper calls assume host bridge functions are present. Arbitration failures or overly optimistic FIFO watermarks can cause display snow or underruns. The broad register reset in `NVLoadStateExt()` can disrupt firmware/console state if save/restore ordering is wrong.

## Test Signals

Strong signals include successful mode-set on NV04/NV10/NV20/NV30/NV40 families, cursor visibility toggles, panning start address changes, suspend/resume save-load round trips, acceleration immediately after mode set, flat-panel and CRT paths, endian build coverage, and stress tests at high dot clocks where FIFO arbitration margins matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_i2c.c

## Purpose

`nv_i2c.c` provides bit-banged I2C/DDC buses for `nvidiafb`, allowing EDID reads from NVIDIA display connectors through CRTC GPIO registers. The source was read as a complete 171-line file.

## Important APIs, Types, and Functions

Exported functions are `nvidia_create_i2c_busses()`, `nvidia_delete_i2c_busses()`, and `nvidia_probe_i2c_connector()`. Internal GPIO callbacks are `nvidia_gpio_setscl()`, `nvidia_gpio_setsda()`, `nvidia_gpio_getscl()`, and `nvidia_gpio_getsda()`. `nvidia_setup_i2c_bus()` configures `struct i2c_adapter` and `struct i2c_algo_bit_data` inside `struct nvidia_i2c_chan`.

## Control Flow

During common setup, `nvidia_create_i2c_busses()` initializes three channels. Connector bus order uses CRTC DDC bases `0x3e` and `0x36`, optionally reversed by `reverse_i2c`, plus a third bus at `0x50`. Each channel raises SDA/SCL, waits briefly, and registers with `i2c_bit_add_bus()`. EDID probing uses `fb_ddc_read()` on `chan[conn - 1]`; for connector 1 it falls back to firmware EDID if bit-bang DDC fails. Delete removes registered adapters and clears `chan[i].par`.

## State and Persistence Behavior

State lives in `par->chan[3]`, including adapter objects, DDC base offsets, and back-pointers to `par`. The driver does not persist EDID data; `nvidia_probe_i2c_connector()` returns a newly allocated EDID buffer to the caller, which later frees it.

## Dependencies and Integration Points

The file depends on the I2C bit-banging framework, fbdev EDID helpers, NVIDIA CRTC register accessors from `nv_setup.c`, and `../edid.h`. It is compiled only under `CONFIG_FB_NVIDIA_I2C`; otherwise `nv_proto.h` supplies no-op/probe-failure stubs. `NVCommonSetup()` consumes these probes to populate monitor specs and choose flat panel/CRT routing.

## Risks and Edge Cases

DDC GPIO register bit meanings are hard-coded. Wrong `reverse_i2c` configuration can attach monitor detection to the wrong connector. `nvidia_setup_i2c_bus()` clears `chan->par` on registration failure, so later delete/probe must honor that guard. Timeouts are short (`msecs_to_jiffies(2)`) and can miss slow DDC devices. The `conn` argument is used as `conn - 1`; callers must pass valid 1-based connector numbers.

## Test Signals

Build-test with `CONFIG_FB_NVIDIA_I2C`, verify three adapters register or cleanly fail, read EDID on connector 1 and 2, exercise `reverse_i2c`, confirm firmware EDID fallback for connector 1, and run probe/remove repeatedly to catch adapter cleanup issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_local.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_local.h

## Purpose

`nv_local.h` centralizes environment-specific hardware access macros for the NVIDIA fbdev driver. It wraps raw MMIO reads/writes, VGA MMIO accesses, DMA command-buffer emission, FIFO put/get handling, memory barriers, and little-endian bit reversal for monochrome image data. The source was read as a complete 114-line file.

## Important APIs, Types, and Functions

The key macros are `NV_WR08`, `NV_RD08`, `NV_WR16`, `NV_RD16`, `NV_WR32`, `NV_RD32`, `VGA_WR08`, `VGA_RD08`, `NVDmaNext`, `NVDmaStart`, `_NV_FENCE`, `WRITE_PUT`, `READ_GET`, and `reverse_order`. These are macro APIs, not functions, and are used throughout `nv_hw.c`, `nv_setup.c`, `nv_accel.c`, and `nvidia.c`.

## Control Flow

There is no standalone flow. Callers use these macros inline to perform register I/O or emit DMA words. `NVDmaStart` checks DMA free space, calls `NVDmaWait()` when needed, emits a method header, and decrements free space. `WRITE_PUT` fences, reads framebuffer memory as a flush, writes the FIFO put pointer, and issues a memory barrier.

## State and Persistence Behavior

The macros mutate caller-owned `struct nvidia_par` fields such as `dmaCurrent`, `dmaFree`, and hardware FIFO registers. The header itself stores no state. `reverse_order` conditionally mutates a 32-bit word in-place on little-endian hosts.

## Dependencies and Integration Points

The header depends on Linux raw I/O helpers, barriers, optional x86 port I/O for `_NV_FENCE`, and `linux/bitrev.h` on little-endian builds. It intentionally keeps low-level access code separate from the more generic NVIDIA hardware logic.

## Risks and Edge Cases

Because most APIs are macros, argument side effects and type assumptions matter. Raw MMIO access bypasses endian conversion except where explicitly handled. `NVDmaStart` depends on an external `NVDmaWait()` symbol and must only be used in contexts where that helper exists. Incorrect barriers or FIFO put/get conversion can lead to lost commands or GPU lockups.

## Test Signals

Compiler coverage across endian and non-x86 architectures, accelerated rendering stress, FIFO wraparound tests, and sparse/build warnings around `__iomem` pointer arithmetic are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_of.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_of.c

## Purpose

`nv_of.c` retrieves EDID data for NVIDIA adapters from Open Firmware device-tree properties. It complements I2C DDC probing, especially on PowerPC/Open Firmware systems where firmware already exposes panel or display EDID. The source was read as a complete 78-line file.

## Important APIs, Types, and Functions

The single exported function is `nvidia_probe_of_connector(struct fb_info *info, int conn, u8 **out_edid)`. It searches property names `DFP,EDID`, `LCD,EDID`, `EDID`, `EDID1`, `EDID,B`, and `EDID,A`.

## Control Flow

The function maps the PCI device to its OF node. On dual-head hardware, it scans child nodes and matches connector 1 or 2 by child `"name"` suffix `A` or `B`, then searches the EDID property list. If no child EDID is found, it searches the parent. A found property is duplicated with `kmemdup(EDID_LENGTH, GFP_KERNEL)`, returned through `out_edid`, and logged; otherwise the function returns `-1`.

## State and Persistence Behavior

No persistent state is owned. It allocates an EDID copy for the caller, which is responsible for freeing it. Device-node references are temporarily acquired during child iteration and released with `of_node_put()` when a matching child is found.

## Dependencies and Integration Points

The file depends on PCI-to-OF mapping, device-tree property access, fbdev types, and `../edid.h`. It is called by `NVCommonSetup()` after or alongside I2C EDID probing.

## Risks and Edge Cases

Child-node matching assumes display node names end in `A` or `B`; firmware using other naming conventions may be missed. The code does not validate the EDID property length before copying `EDID_LENGTH`. It returns `-1` for both absence and allocation failure, so callers cannot distinguish missing firmware data from memory pressure.

## Test Signals

Test with OF nodes containing parent-only EDID, dual-head child EDID with `A`/`B` names, missing EDID, and malformed/short EDID properties. Probe should choose the correct head and free returned buffers in `NVCommonSetup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_proto.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_proto.h

## Purpose

`nv_proto.h` is the cross-file prototype contract for the NVIDIA fbdev driver. It declares setup/VGA register helpers, hardware state helpers, optional I2C and backlight entry points, Open Firmware EDID probing, and acceleration operations. The source was read as a complete 68-line file.

## Important APIs, Types, and Functions

Declared APIs include `NVCommonSetup`, `NVWriteCrtc`, `NVReadCrtc`, `NVWriteGr`, `NVReadGr`, `NVWriteSeq`, `NVReadSeq`, `NVWriteAttr`, `NVReadAttr`, DAC accessors, `NVCalcStateExt`, `NVLoadStateExt`, `NVUnloadStateExt`, `NVSetStartAddress`, `NVShowHideCursor`, `NVLockUnlock`, `nvidia_probe_of_connector`, `NVResetGraphics`, `nvidiafb_copyarea`, `nvidiafb_fillrect`, `nvidiafb_imageblit`, and `nvidiafb_sync`. Conditional stubs are provided for I2C and backlight when their config symbols are disabled.

## Control Flow

There is no runtime control flow. This header controls compile/link-time coupling among `nvidia.c`, `nv_setup.c`, `nv_hw.c`, `nv_accel.c`, `nv_i2c.c`, `nv_of.c`, and `nv_backlight.c`.

## State and Persistence Behavior

No state is stored. The prototypes describe functions that mutate `struct nvidia_par`, `struct fb_info`, hardware registers, and optional subsystem state elsewhere.

## Dependencies and Integration Points

It depends on `struct nvidia_par`, `struct fb_info`, and `struct _riva_hw_state` declarations from included or prior headers. It is the main integration point ensuring optional object files can be omitted while callers still compile through stub macros/functions.

## Risks and Edge Cases

Prototype drift can produce build failures or, worse, mismatched call assumptions if declarations and definitions diverge. Optional stubs must preserve return-value semantics expected by `NVCommonSetup()`; for example, disabled I2C probing returns failure so OF probing can still run.

## Test Signals

Build all NVIDIA fbdev config combinations: base only, I2C enabled, backlight enabled, both enabled, built-in and module. Warnings about missing prototypes or incompatible declarations are direct regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_setup.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_setup.c

## Purpose

`nv_setup.c` initializes shared NVIDIA register-bank pointers, provides VGA/DAC register accessors over MMIO, discovers framebuffer memory/clock limits, detects display heads/connectors, probes EDID through I2C or Open Firmware, and decides whether the active output is CRT, flat panel, or TV. The source was read as a complete 649-line file.

## Important APIs, Types, and Functions

Exported low-level accessors are `NVWriteCrtc`, `NVReadCrtc`, `NVWriteGr`, `NVReadGr`, `NVWriteSeq`, `NVReadSeq`, `NVWriteAttr`, `NVReadAttr`, `NVWriteMiscOut`, `NVReadMiscOut`, `NVWriteDacMask`, `NVWriteDacReadAddr`, `NVWriteDacWriteAddr`, `NVWriteDacData`, and `NVReadDacData`. The exported setup routine is `NVCommonSetup()`. Internal helpers include `NVIsConnected()` for analog detection, `NVSelectHeadRegisters()` for per-head pointer selection, `nv4GetConfig()` and `nv10GetConfig()` for memory/clock/cursor limits.

## Control Flow

`NVCommonSetup()` allocates temporary var and monitor-spec structures, maps register-bank pointers into `struct nvidia_par`, derives `twoHeads`, scaler, PLL, vsync, and blending capabilities, identifies mobile chip IDs, reads architecture-specific memory/clock configuration, selects head 0, unlocks VGA, creates I2C buses, and performs display detection. Single-head flow probes connector 1 for EDID or falls back to current hardware programming. Dual-head flow inspects output routing, analog presence, slaved flat-panel/TV bits, temporarily selects heads, probes EDID on both connectors, chooses a compatible monitor/head, applies forced flatpanel/CRTC parameters if provided, and selects final head registers. It then records panel width/height/syncs for flat panels, copies chosen monitor specs into `info->monspecs`, computes dithering/LVDS state, frees temporary EDID/monitor allocations, and returns.

## State and Persistence Behavior

The function fills nearly all hardware topology fields in `struct nvidia_par`: register pointers, `twoHeads`, `fpScaler`, `twoStagePLL`, `WaitVSyncPossible`, `BlendingPossible`, `RamAmountKBytes`, `CrystalFreqKHz`, `MinVClockFreqKHz`, `MaxVClockFreqKHz`, `CURSOR`, `IOBase`, `FlatPanel`, `Television`, `CRTCnumber`, `fpWidth`, `fpHeight`, `fpSyncs`, `FPDither`, and `LVDS`. It also stores parsed EDID monitor specs in `info->monspecs`; mode databases are later consumed and freed by `nvidia_set_fbinfo()`.

## Dependencies and Integration Points

The file depends on VGA constants, PCI config reads, NVIDIA raw MMIO helpers, `nv_i2c.c`, `nv_of.c`, fbdev EDID parsing, and the register layout used by `nv_hw.c` and `nvidia.c`. `nvidiafb_probe()` calls `NVCommonSetup()` before framebuffer mapping and initial mode selection.

## Risks and Edge Cases

Display detection mixes EDID, current register state, analog load detection, laptop chip heuristics, and user-forced options; ambiguous hardware can choose the wrong head or output. Some PCI config helper calls assume specific host bridge slots for nForce memory detection. OF/I2C EDID failures are tolerated but reduce mode validation quality. Temporary monitor specs are shallow-copied into `info->monspecs`, so ownership of mode databases must be handled carefully by later cleanup.

## Test Signals

Test single-head CRT, single-head DFP, dual-head CRT/DFP combinations, forced `flatpanel` and `forceCRTC`, `reverse_i2c`, OF EDID fallback, mobile chips with no detected output, LVDS/TMDS detection, and nForce memory-size paths. Monitor-spec mode databases should be valid through initial mode selection and freed once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_type.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_type.h

## Purpose

`nv_type.h` defines the shared data structures, architecture constants, and bitfield helpers for the NVIDIA fbdev driver. It is the state contract used by all `nvidiafb` implementation files. The source was read as a complete 176-line file.

## Important APIs, Types, and Functions

Important macros are `NV_ARCH_04`, `NV_ARCH_10`, `NV_ARCH_20`, `NV_ARCH_30`, `NV_ARCH_40`, `BITMASK`, `MASKEXPAND`, `SetBF`, `GetBF`, `SetBitField`, `SetBit`, `Set8Bits`, and `V_DBLSCAN`. Types include `NVFBLayout`, `struct nvidia_i2c_chan`, `RIVA_HW_STATE`, `struct riva_regs`, and `struct nvidia_par`. `RIVA_HW_STATE` contains VGA arrays plus NVIDIA extended mode registers. `struct nvidia_par` contains saved/current state, PCI device, framebuffer/MMIO addresses, architecture/chipset, panel/head flags, DMA state, cursor and acceleration fields, I2C channels, and register-bank pointers.

## Control Flow

There is no executable flow. The structs are allocated as `fb_info->par` in `nvidiafb_probe()` and are read/written by setup, mode-setting, acceleration, backlight, I2C, and remove paths.

## State and Persistence Behavior

This header defines the in-memory persistent state for a bound NVIDIA fbdev device. `SavedReg`, `ModeReg`, and `initial_state` preserve hardware state for suspend/open/release/mode-set transitions. Address fields and register pointers persist from probe until remove. DMA fields persist across accelerated operations and are reset on mode set. Nothing is persisted beyond driver lifetime.

## Dependencies and Integration Points

The header includes fbdev, Linux types, I2C bit-bang types, and VGA helpers. Every NVIDIA fbdev source includes it directly or indirectly, making it the central ABI between files.

## Risks and Edge Cases

Structure layout changes can affect assumptions across the driver but not user ABI. Bitfield helper macros use unusual `high:low` macro arguments and depend on integer widths; misuse can silently program wrong register bits. The large `struct nvidia_par` mixes ownership for many subsystems, so cleanup must match which fields were initialized on each error path.

## Test Signals

Build coverage is the primary direct signal. Runtime signals include correct cleanup after partial probe failures, suspend/resume preserving `SavedReg`, mode-set updating `ModeReg`/`CurrentState`, and accelerated operations mutating DMA fields without corrupting unrelated state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nvidia.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nvidia.c

## Purpose

`nvidia.c` is the main PCI/fbdev driver for legacy NVIDIA graphics adapters. It handles module parameters, PCI probe/remove, framebuffer/MMIO mapping, chipset/architecture selection, fbdev operation registration, initial mode selection, mode validation and programming, colormap and hardware cursor support, panning, blanking, suspend/resume, acceleration selection, and optional backlight initialization. The source was read as a complete 1599-line file.

## Important APIs, Types, and Functions

The driver registers `nvidiafb_driver` with a broad NVIDIA display-class PCI ID table. Key fbdev operations are `nvidiafb_open`, `nvidiafb_release`, `nvidiafb_check_var`, `nvidiafb_set_par`, `nvidiafb_setcolreg`, `nvidiafb_pan_display`, `nvidiafb_blank`, `nvidiafb_cursor`, `nvidiafb_sync`, and accelerated fill/copy/imageblit hooks. Important setup helpers are `nvidia_get_chipset()`, `nvidia_get_arch()`, `nvidia_set_fbinfo()`, `nvidia_init_vga()`, `nvidia_calc_regs()`, `nvidia_save_vga()`, `nvidia_write_regs()`, `nvidia_screen_off()`, `nvidia_panel_tweak()`, CLUT helpers, and cursor-image loading. Power management is implemented by `nvidiafb_suspend_late()` and `nvidiafb_resume()`.

## Control Flow

Initialization parses boot/module options, rejects global modesetting-disabled configurations, and registers the PCI driver. Probe enables PCI I/O/memory, maps BAR0 MMIO, determines chipset/architecture, removes conflicting apertures, allocates `fb_info` and pixmap memory, requests PCI regions, stores module option state into `struct nvidia_par`, calls `NVCommonSetup()`, computes framebuffer usable/scratch/cursor regions, maps framebuffer write-combined, enables write-combining unless `nomtrr`, initializes `fb_info`, validates the initial mode, saves VGA state, registers the framebuffer, optionally initializes backlight, and logs the device. Mode set (`nvidiafb_set_par`) locks/unlocks registers, initializes VGA defaults, computes register state, blanks the screen, writes registers, sets start address, installs acceleration or software fbops, resets cursor state, and unblanks. Remove tears down backlight, unregisters fbdev, removes write-combining, unmaps memory, frees EDID mode data, deletes I2C buses, releases PCI regions, frees pixmap memory, and releases `fb_info`.

## State and Persistence Behavior

Per-device state is `struct nvidia_par` plus fbdev `info` state. `SavedReg` is captured at probe/suspend, `initial_state` is captured on first open and restored on last release, and `ModeReg` is regenerated for each mode. `open_count` gates VGA save/restore. `pm_state` tracks suspend state. Framebuffer contents persist in VRAM while mapped; hardware registers persist until mode changes, suspend/resume, release restore, or remove. Module parameters persist globally for all probed devices.

## Dependencies and Integration Points

The file depends on PCI, aperture removal, fbdev helpers, console locking, backlight, write-combining, optional BootX text update, and all NVIDIA local modules (`nv_setup`, `nv_hw`, `nv_accel`, `nv_i2c`, `nv_of`, `nv_backlight`). It exposes a standard fbdev device to userspace and console layers and competes with DRM/native drivers for the same aperture.

## Risks and Edge Cases

Probe error paths must unwind partially initialized I2C, mode databases, MMIO mappings, PCI regions, and pixmap memory in the correct order. `nvidia_bl_exit()` is called unconditionally on remove even if backlight registration was skipped by parameter or hardware; this relies on safe handling of a NULL/no device. Mode validation mutates requested bpp/resolution and may cap flat-panel modes to panel size. Hardware cursor is disabled by default and limited to 32x32. Acceleration can be disabled by parameter or dynamically after lockup. The broad PCI ID table requires accurate architecture detection to avoid programming unsupported chips.

## Test Signals

Build and boot with representative NV04/NV10/NV20/NV30/NV40 IDs, test probe failure unwinds by injecting mapping/region/cmap failures, validate mode setting at 8/16/32 bpp and flat-panel bounds, exercise panning, colormap, blanking, open/release VGA restore, suspend/resume, backlight parameter on/off, `noaccel`, `hwcur`, `nomtrr`, and remove/reprobe cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nvidia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ocfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/ocfb.c

## Purpose

`ocfb.c` is a platform fbdev driver for the OpenCores VGA/LCD 2.0 controller. It allocates a coherent framebuffer, maps controller registers, programs timing and framebuffer base registers, supports 8/16/24/32-bpp packed-pixel modes, and exposes a simple fbdev device with color-register support. The source was read as a complete 428-line file.

## Important APIs, Types, and Functions

The key device state is `struct ocfb_dev`, embedding `struct fb_info`, register base, endianness flag, coherent framebuffer physical/virtual addresses, and a pseudo palette. Important functions are `ocfb_setup()` for boot option parsing, `ocfb_readreg()`/`ocfb_writereg()` for endian-aware register I/O, `ocfb_setupfb()` for hardware programming, `ocfb_setcolreg()` for palette/pseudo-palette updates, `ocfb_init_fix()`, `ocfb_init_var()`, `ocfb_probe()`, and `ocfb_remove()`. `ocfb_ops` uses `FB_DEFAULT_IOMEM_OPS` plus `.fb_setcolreg`.

## Control Flow

Init parses `ocfb` options in built-in mode and registers a platform driver matching `opencores,ocfb`. Probe allocates `ocfb_dev`, selects a video mode with `fb_find_mode()` and a 640x480@60 default, initializes `var`/`fix`, maps MMIO, allocates coherent framebuffer memory sized by line length and yres, clears it, calls `ocfb_setupfb()` to disable output, write framebuffer base, detect register endianness, program horizontal/vertical timing and total lengths, set color depth and burst length, and enable output. It then marks `FBINFO_FOREIGN_ENDIAN` if needed, allocates the cmap, and registers the framebuffer. Remove unregisters, frees cmap and DMA memory, disables display, and clears driver data.

## State and Persistence Behavior

State is per-platform-device and devm-managed except coherent framebuffer memory/cmap which are explicitly freed. Hardware state includes OCFB timing registers, framebuffer base address, control bits, palette entries, and enabled/disabled output. Framebuffer contents live in coherent DMA memory for the lifetime of the fbdev device; no storage persists across remove.

## Dependencies and Integration Points

The driver depends on platform devices, device tree matching, MMIO resource mapping, coherent DMA allocation, fbdev mode helpers, and framebuffer console/userspace through standard fbdev ops. It has a `mode_option` module parameter/boot option for initial mode selection.

## Risks and Edge Cases

`ocfb_setupfb()` assumes timing fields are nonzero before subtracting one; invalid or unusual mode timings could underflow register fields. Register endianness is detected by writing/reading `OCFB_VBARA`, which depends on a stable framebuffer physical address and readable register. `ocfb_setcolreg()` writes pseudo-palette entries for all regnos below cmap length even though truecolor pseudo palettes are conventionally 16 entries; callers normally limit truecolor regnos but the local guard is `info->cmap.len`. DMA allocation size is based on the chosen mode and can fail on high resolutions.

## Test Signals

Device-tree probe with big- and little-endian register mappings, initial mode parsing, successful coherent allocation and screen clear, 8-bpp palette writes to hardware, truecolor pseudo-palette writes, remove disabling display, and framebuffer console smoke at each supported bpp are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ocfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/offb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/offb.c

## Purpose

`offb.c` is the Open Firmware framebuffer driver. It exposes firmware-initialized display memory as a generic fbdev device when no native driver has claimed the hardware, with special palette handling for several older ATI, IBM, AVIVO, and QEMU VGA devices. The source was read as a complete 726-line file.

## Important APIs, Types, and Functions

Per-device state is `struct offb_par`, containing palette MMIO addresses, palette type, blanked flag, pseudo palette, and framebuffer resource base/size. The main fbdev callbacks are `offb_setcolreg()`, `offb_blank()`, `offb_set_par()`, and `offb_destroy()` in `offb_ops`. Hardware discovery and setup are handled by `offb_map_reg()`, `offb_init_palette_hacks()`, `offb_init_fb()`, `offb_init_nodriver()`, `offb_probe_bootx_noscreen()`, and `offb_probe_display()`.

## Control Flow

Init checks `fb_get_options("offb")`, then registers a BootX noscreen platform driver and an OF display platform driver. Probe calls `offb_init_nodriver()`, which reads firmware properties for depth, width, height, linebytes, endianness, and framebuffer address, then uses OF address ranges and PCI heuristics to choose a memory address. It optionally enables the PCI device, applies a Valkyrie address quirk, and calls `offb_init_fb()`. `offb_init_fb()` reserves the framebuffer memory, allocates `fb_info`, sets fix/var fields from firmware geometry/depth, initializes palette hacks for 8-bpp displays or truecolor layouts for higher depth, maps framebuffer memory, allocates cmap, acquires the aperture for platform use, and registers fbdev. Runtime color and blanking callbacks write pseudo palettes or device-specific DAC/LUT registers. Remove unregisters; fbdev destroy releases mappings, memory region, cmap, and `fb_info`.

## State and Persistence Behavior

The driver preserves firmware-programmed display mode and only maps/programs memory, palette, and blanking-related registers. It does not allocate video memory. `par->blanked` tracks blank state so unblank can restore the cmap. `par->base` and `par->size` own the reserved memory region until destroy. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on Open Firmware device-tree properties, OF address translation, PCI helpers, aperture conflict management, fbdev IOMEM helpers, and architecture endian handling. On PPC32 it can consume BootX `of_chosen` data. It is a fallback bridge between firmware boot graphics and Linux fbdev/console until native drivers take over.

## Risks and Edge Cases

Framebuffer address selection is explicitly heuristic because OF has no universal framebuffer address property. Palette hacks are device-name and compatibility-string based and can miss or mis-handle firmware variants. Some error paths in `offb_init_fb()` call `iounmap(par->cmap_adr)` only after `par` allocation; palette mappings must be valid or NULL. `fb_alloc_cmap()` return is not checked before registration. Depth support is limited to 8, 15, 16, and 32. The QEMU simple palette path depends on endian-specific OF I/O address representation.

## Test Signals

Test OF display nodes with `depth`, `width`, `height`, `linebytes`, `address`, `linux,bootx-*`, big/little-endian flags, and PCI ranges. Exercise 8-bpp palette writes for ATI/Rage128/Radeon/GXT2000/AVIVO/QEMU paths, truecolor pseudo palette at 15/16/32 bpp, blank/unblank cmap restoration, aperture conflicts with native drivers, and BootX noscreen fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/offb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Kconfig

## Purpose

`omap/Kconfig` defines configuration symbols for the OMAP1 fbdev driver and optional external LCD controller features. The source was read as a complete 49-line file.

## Important APIs, Types, and Functions

Configuration symbols are `FB_OMAP`, `FB_OMAP_LCDC_EXTERNAL`, `FB_OMAP_LCDC_HWA742`, `FB_OMAP_MANUAL_UPDATE`, `FB_OMAP_LCD_MIPID`, and `FB_OMAP_DMA_TUNE`. `FB_OMAP` is tristate, depends on `FB` and `ARCH_OMAP1 || (ARM && COMPILE_TEST)`, and selects `FB_IOMEM_HELPERS`.

## Control Flow

There is no runtime flow. Kconfig exposes menu choices and dependency constraints that control which source files the OMAP Makefile builds and which code paths are compiled.

## State and Persistence Behavior

The file owns build-time configuration state only. Selected symbols persist in the kernel `.config` and determine compiled driver capabilities.

## Dependencies and Integration Points

It integrates with the fbdev Kconfig tree, OMAP1 architecture support, ARM compile testing, SPI master support for MIPI DBI/DCS panels, and the OMAP Makefile object selections. `FB_OMAP_MANUAL_UPDATE` and `FB_OMAP_DMA_TUNE` influence behavior in the implementation files even though they are not built independently here.

## Risks and Edge Cases

Dependency mistakes can expose OMAP-only code to unsupported architectures or hide useful compile-test coverage. `FB_OMAP_LCDC_HWA742` depends on both base OMAP fbdev and external controller support; breaking that relationship would create missing symbols or invalid UI choices. Help text describes board and userspace expectations that should stay aligned with implementation behavior.

## Test Signals

Run Kconfig/build matrix checks for `FB_OMAP=m/y`, ARM compile-test, external LCD support, HWA742, MIPI DBI with and without `SPI_MASTER`, manual update, and DMA tuning. Verify the resulting object lists match Makefile expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Makefile

## Purpose

`omap/Makefile` defines the Kbuild object composition for the OMAP1 framebuffer driver, including base driver objects, external controller support, board LCD panel files, and MIPI DBI panel support. The source was read as a complete 26-line file.

## Important APIs, Types, and Functions

The key variables are `obj-$(CONFIG_FB_OMAP)`, `obj-y`, `objs-yy`, `objs-y$(CONFIG_FB_OMAP_LCDC_EXTERNAL)`, `objs-y$(CONFIG_FB_OMAP_LCDC_HWA742)`, `lcds-y$(CONFIG_MACH_AMS_DELTA)`, `lcds-y$(CONFIG_MACH_OMAP_PALMTE)`, `lcds-y$(CONFIG_FB_OMAP_LCD_MIPID)`, and `omapfb-objs`. Base `omapfb` objects are `omapfb_main.o` and `lcdc.o`; optional objects include `sossi.o`, `hwa742.o`, `lcd_ams_delta.o`, `lcd_palmte.o`, and `lcd_mipid.o`. `lcd_dma.o` is forced built-in when `CONFIG_FB_OMAP` is set.

## Control Flow

There is no runtime flow. Kbuild evaluates configuration symbols, links selected base objects into `omapfb.o`, builds `lcd_dma.o` built-in for base support, and includes board/panel LCD objects according to machine and panel configuration.

## State and Persistence Behavior

The file owns build-time object-selection state only. Runtime state is in the compiled driver objects.

## Dependencies and Integration Points

It integrates with `omap/Kconfig` symbols and machine symbols such as `CONFIG_MACH_AMS_DELTA` and `CONFIG_MACH_OMAP_PALMTE`. The explicit `obj-y += lcd_dma.o` comment notes that DMA support must be built-in when OMAP fbdev is enabled, which may matter for initialization ordering or exported helper availability.

## Risks and Edge Cases

The `objs-y$(CONFIG_...)` pattern relies on Kbuild variable expansion producing `objs-yy` for enabled booleans; typos would silently omit objects. If `FB_OMAP=m`, the forced `lcd_dma.o` built-in object can create built-in/module coupling that must be intentional and link-safe. Board LCD objects are added as standalone objects, not part of `omapfb-objs`, so initialization ordering and symbol visibility should be checked when moving code.

## Test Signals

Build with `CONFIG_FB_OMAP=y` and `m`, with external LCD/HWA742 enabled, with AMS Delta and PalmTE machine configs, and with MIPI DBI support. Confirm `omapfb.o` includes expected base/optional controller objects and that board LCD objects link without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Makefile -->
