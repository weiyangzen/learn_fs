# subset-b-003789 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/tegra114-mipi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/tegra114-mipi.c

## Purpose
Implements the Tegra MIPI calibration provider used by Tegra DSI/CSI clients to power the MIPI calibration block, program SoC-specific pad calibration values, start calibration, and wait for completion. It is a platform driver named `tegra-mipi` and registers a `tegra_mipi_ops` provider through `devm_tegra_mipi_add_provider()`.

## Important APIs, Types, and Functions
Key local types are `struct tegra_mipi_pad`, which maps data and optional clock-lane calibration registers for each pad group; `struct tegra_mipi_soc`, which captures SoC-specific pad tables and tuning constants; and `struct tegra_mipi`, which stores device state, MMIO base, prepared clock, mutex, and `usage_count`. Exported behavior is indirect through `tegra114_mipi_ops`: `enable`, `disable`, `start_calibration`, and `finish_calibration`. `tegra114_mipi_power_up()` and `tegra114_mipi_power_down()` toggle bias-pad clamp/regulator bits. `tegra114_mipi_start_calibration()` writes drive, clamp, lane, noise-filter, prescale, and start bits. `tegra114_mipi_finish_calibration()` polls `MIPI_CAL_STATUS` until calibration is inactive and done.

## Control Flow
Probe selects a compatible entry (`nvidia,tegra114-mipi`, `tegra124-mipi`, `tegra132-mipi`, or `tegra210-mipi`), maps the register resource, initializes the mutex, obtains a prepared clock, stores driver data, and publishes the provider. Clients call `enable()` before using lanes; the first user powers up shared bias resources. Calibration is a two-step transaction: `start_calibration()` enables the clock, locks the register mutex, programs selected lane registers according to `mipidev->pads`, starts the block, delays at least 72 microseconds, and returns with the mutex and clock still held. The paired `finish_calibration()` polls hardware status, then unlocks and disables the clock. `disable()` decrements `usage_count` and powers down on the last user.

## State and Persistence
Runtime state is held only in memory and hardware registers: `usage_count`, the mutex, SoC data pointer, MMIO state, and clock state. There is no filesystem persistence. Register values survive until hardware reset or later writes. The split start/finish API intentionally preserves lock and clock ownership across the calibration interval.

## Dependencies and Integration Points
Depends on Linux platform, OF matching, clk, MMIO, polling helpers, and the Tegra MIPI calibration framework in `<linux/tegra-mipi-cal.h>`. It is integrated with display/camera clients through the provider API and with host1x display plumbing by the externally visible `tegra_mipi_driver` symbol.

## Risks
The split calibration contract is fragile: every successful `start_calibration()` must be followed by `finish_calibration()` or the mutex remains locked and the clock remains enabled. `tegra114_mipi_disable()` decrements without guarding underflow, so mismatched client enable/disable calls can corrupt shared power state. SoC pad tables encode register aliases, including shared clock registers, and bad compatible data can program wrong lanes. Poll timeout failures propagate but still clean up lock/clock in `finish_calibration()`.

## Test Signals
Useful signals include successful probe for each compatible, balanced enable/disable tests with multiple clients, calibration timeout/error-path coverage, and DSI/CSI link bring-up with selected pads on Tegra114/124/132/210. Dynamic debug around register programming plus clock enable counts would expose mismatched start/finish or usage-count bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/tegra114-mipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Kconfig

## Purpose
Defines the build-time configuration symbol for the i.MX IPUv3 core driver. `CONFIG_IMX_IPUV3_CORE` is the switch that enables the base Image Processing Unit support used by i.MX5/i.MX6 display, capture, and image-processing clients.

## Important APIs, Types, and Functions
This file has no C APIs. Its important interface is the `tristate "IPUv3 core support"` Kconfig symbol. It constrains availability to `SOC_IMX5 || SOC_IMX6Q || COMPILE_TEST`, adds a DRM consistency dependency (`DRM || !DRM`) so the core is not built-in while DRM is modular, and selects `BITREVERSE`, `GENERIC_IRQ_CHIP`, and `GENERIC_ALLOCATOR if DRM`.

## Control Flow
Kconfig evaluation decides whether `IMX_IPUV3_CORE` can be disabled, built in, or built as a module. The selected helper symbols then make APIs used by the C implementation available, especially bit reversal for CPMEM/IC bitfield packing, generic IRQ chips for IPU interrupt domains, and genalloc for PRE IRAM allocation when DRM is enabled.

## State and Persistence
The only persistent state is the generated kernel configuration. It determines object inclusion and whether dependent symbols are forced on.

## Dependencies and Integration Points
Integrated directly with `drivers/gpu/ipu-v3/Makefile`, which builds `imx-ipu-v3.o` when this symbol is enabled. It also coordinates with DRM build mode because the IPU core has client devices used by DRM display components.

## Risks
The `DRM || !DRM` dependency is easy to misunderstand but prevents invalid link combinations. Broad `COMPILE_TEST` exposure increases build coverage but may expose architecture assumptions in code paths that normally run only on i.MX SoCs.

## Test Signals
Build matrix signals matter most: i.MX5/i.MX6 built-in, modular, DRM modular, DRM disabled, and COMPILE_TEST builds. Kconfig warnings or unresolved symbols around `bitrev`, generic IRQ chips, or genalloc indicate dependency drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Makefile

## Purpose
Assembles the i.MX IPUv3 core object from its submodule implementation files. It controls which source files participate in `imx-ipu-v3.o`.

## Important APIs, Types, and Functions
There are no runtime APIs. The central build artifact is `imx-ipu-v3.o`, enabled by `obj-$(CONFIG_IMX_IPUV3_CORE)`. The base object list includes common IPU core, CPMEM, CSI, DC, DI, DP, DMFC, IC, CSC, image-convert, SMFC, and VDI implementation files. Under `CONFIG_DRM`, it adds `ipu-pre.o` and `ipu-prg.o`.

## Control Flow
Kbuild compiles the listed objects into one module or built-in object depending on `CONFIG_IMX_IPUV3_CORE`. The conditional DRM block keeps PRE/PRG support tied to DRM builds because those modules are used for tiled framebuffer/display paths.

## State and Persistence
Build state is encoded in generated objects. There is no runtime state in this file.

## Dependencies and Integration Points
Couples with `Kconfig` and with `ipu-common.c`, whose module init registers not only the main IPU platform driver but also `ipu_pre_drv` and `ipu_prg_drv` when DRM is enabled. It also implies that symbols exported across these files are intra-module as well as available to other GPL modules.

## Risks
Adding a new submodule API without listing its source here will produce link failures or missing runtime functionality. PRE/PRG references in common code must remain guarded consistently with `CONFIG_DRM`, because these files disappear from non-DRM builds.

## Test Signals
The primary tests are compile/link coverage for `CONFIG_IMX_IPUV3_CORE=y/m`, `CONFIG_DRM=y/m/n`, and COMPILE_TEST. Undefined references to `ipu_pre_drv`, `ipu_prg_drv`, or submodule init/exit functions are direct Makefile/Kconfig mismatch signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-common.c

## Purpose
Provides the IPUv3 platform core: SoC matching, MMIO setup, clock/reset/memory initialization, IRQ-domain creation, IDMAC channel allocation/control, module clock gating, FSU/IDMAC linking, submodule initialization, and child platform-device registration for IPU clients.

## Important APIs, Types, and Functions
Major exported APIs include `ipu_get_num()`, color-space mapping helpers, `ipu_degrees_to_rot_mode()`, `ipu_idmac_get()/put()`, buffer readiness/select/clear helpers, IDMAC enable/disable/wait/watermark functions, `ipu_module_enable()/disable()`, CSI/IC source mux setters, `ipu_fsu_link()/unlink()`, `ipu_map_irq()`, `ipu_idmac_channel_irq()`, and `ipu_dump()`. `struct ipu_devtype` defines SoC offset maps and channel capabilities for i.MX51/i.MX53/i.MX6Q. `client_reg[]` describes child devices such as imx-ipuv3-crtc, csi, and other clients.

## Control Flow
`ipu_probe()` obtains OF match data, IRQs, memory resource, alias ID, optional PRG phandle for i.MX6QP DRM, maps common and IDMAC registers, gets/enables the bus clock, resets the device, resets internal memory, initializes the IRQ domain, programs display access timing, initializes submodules, then registers child platform devices. Removal unregisters children, exits submodules, removes IRQ mappings, and disables the bus clock. IDMAC users acquire channels through `ipu_idmac_get()`, configure CPMEM in other files, mark buffers ready, enable channels, and later disable and release them.

## State and Persistence
`struct ipu_soc` owns persistent runtime state for a probed IPU: device identity, devtype, MMIO bases, clock, IRQ domain, locks, channel list, submodule private pointers, and optional PRG private data. `channel_lock` protects IDMAC channel allocation; `ipu->lock` protects common register updates. Hardware state includes module enable bits, FSU links, IDMAC current/ready bits, IRQ masks/status, muxes, and reset state. There is no disk persistence.

## Dependencies and Integration Points
Uses platform/OF APIs, reset control via `device_reset()`, clk, generic IRQ chip/domain APIs, and submodule init/exit functions from CPMEM, CSI, IC, VDI, DP, DMFC, DI, DC, SMFC, and image-convert. It registers `ipu_pre_drv` and `ipu_prg_drv` before the main driver when DRM is enabled. Client devices use resources derived from the same IPU physical base and obtain exported GPL APIs to drive display/capture pipelines.

## Risks
Probe error unwinding is order-sensitive because clock, IRQ domain, submodules, and child devices have dependencies. IDMAC disable waits for busy status and manipulates double-buffer state; errors or races can leave channels active. FSU link tables only allow known source/sink pairs, and invalid links return `-EINVAL`. The IRQ cleanup comments indicate generic-chip removal is incomplete, so stale mappings are a maintenance risk. Channel allocation and module enable calls must be balanced by clients.

## Test Signals
Test probe/remove on supported compatibles, including reset failures and missing IRQ/resource cases. Exercise IDMAC allocation contention, double-buffer channel enable/disable, buffer-ready transitions, FSU link/unlink pairs, mapped EOF/NFACK IRQ delivery, and child-device creation. `ipu_dump()` register snapshots and dynamic debug around busy waits are strong diagnostics for stuck DMA or interrupt masking issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-cpmem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-cpmem.c

## Purpose
Implements Channel Parameter Memory programming for IPUv3 IDMAC channels. CPMEM entries describe image dimensions, strides, DMA buffer addresses, pixel format layout, rotation/block mode, burst size, interlacing, UV offsets, priority, and alpha/separate-plane behavior.

## Important APIs, Types, and Functions
`struct ipu_cpmem_word`, `struct ipu_ch_param`, and `struct ipu_cpmem` model packed parameter memory and its spinlock. Low-level `ipu_ch_param_write_field()` and `ipu_ch_param_read_field()` write bitfields that may cross 32-bit words using `bitrev8()`. Exported setters include `ipu_cpmem_zero()`, resolution/stride/buffer/UV/interlaced/burst/block/rotation/AXI/high-priority functions, RGB/passthrough/YUV format functions, `ipu_cpmem_set_fmt()`, `ipu_cpmem_set_image()`, and `ipu_cpmem_dump()`. RGB format descriptors define bit widths and offsets for many DRM fourcc formats.

## Control Flow
Users typically obtain an IDMAC channel, call `ipu_cpmem_zero()`, set image geometry and format either explicitly or via `ipu_cpmem_set_image()`, set buffers, burst/rotation/block flags, then enable the channel through `ipu-common.c`. `ipu_cpmem_set_image()` validates crop/size assumptions, selects planar/packed address offsets, handles V4L2-to-DRM conversion for legacy formats, programs resolution/stride/format, and stores plane addresses. Initialization maps the 128 KiB CPMEM aperture and stores it in `ipu->cpmem_priv`.

## State and Persistence
State is hardware CPMEM content plus the mapped base and spinlock in `struct ipu_cpmem`. CPMEM content persists until overwritten or reset. The spinlock serializes field writes so read-modify-write sequences do not corrupt adjacent packed fields.

## Dependencies and Integration Points
Depends on DRM fourcc definitions, V4L2 pixel format compatibility mapping, bit reversal helpers selected by Kconfig, and `struct ipuv3_channel` from the private IPU headers. It is used by image conversion, display, capture, and any IDMAC client before channel enable.

## Risks
Packed bitfield writes are sensitive to field definitions and cross-word handling. DMA base fields shift addresses, so unsupported alignment or high physical addresses could be misprogrammed if callers violate assumptions. Planar offset calculations depend on bytesperline, crop, subsampling, and chroma order; wrong format metadata causes corrupted images. Separate alpha uses a limited channel mapping table and returns errors for unsupported channels.

## Test Signals
Useful tests are format-by-format CPMEM dumps for RGB, packed YUV, NV12/NV16, planar YUV, interlaced scan, rotation, and separate alpha. Hardware frame checks should verify stride, crop, chroma offsets, and double-buffer addresses. KUnit-style tests for field packing would catch bitfield regressions without hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-cpmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-csi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-csi.c

## Purpose
Configures IPUv3 Camera Sensor Interface blocks. It translates V4L2 media-bus formats and signal configuration into CSI register programming, sets active capture windows, downsizing, MIPI datatypes, frame skipping, and data destinations, and exposes get/put lifetime APIs for CSI instances.

## Important APIs, Types, and Functions
`struct ipu_csi` stores ID, module bit, IPU pointer, clock, MMIO base, lock, and use count. `struct ipu_csi_bus_config` captures data width, clock mode, polarity, protocol, data format, and MIPI datatype details. Exported APIs include `ipu_csi_init_interface()`, `ipu_csi_set_window()`, `ipu_csi_set_downsize()`, `ipu_csi_set_mipi_datatype()`, `ipu_csi_set_skip_smfc()`, `ipu_csi_set_dest()`, enable/disable, get/put, init/exit, and dump. Helpers convert media-bus codes and fill config from `v4l2_mbus_config` plus `v4l2_mbus_framefmt`.

## Control Flow
A client acquires a CSI with `ipu_csi_get()`, initializes the interface from media-bus config/frame format, programs optional window/downsize/MIPI datatype/skip settings, selects destination (`IC`, `IDMAC`, etc.), and enables the module. `ipu_csi_init_interface()` validates width/height and input format, calculates divider/protocol/data format fields, writes sensor config and frame size registers, and configures CCIR code registers for BT.656/BT.1120-like modes.

## State and Persistence
Per-CSI runtime state includes MMIO registers, use count protected by a spinlock, and the parent IPU module bit. Register state persists across client operations until reconfigured or reset. There is no filesystem persistence.

## Dependencies and Integration Points
Depends on V4L2 media-bus constants, videodev2 field/color definitions, clk APIs, and `ipu_module_enable()/disable()` in `ipu-common.c`. It integrates with SMFC, IC, IDMAC, and MIPI CSI2 routing via destination and datatype fields plus source muxing in common code.

## Risks
Media-bus conversion is dense and rejects unsupported combinations with `-EINVAL`; adding formats requires careful data-width/protocol mapping. Incorrect signal polarity or CCIR code generation can produce silent capture failures. Use-count balancing is required to avoid sharing conflicts. Register updates are not all globally serialized beyond local spinlock-protected lifetime state, so clients must avoid concurrent reconfiguration of an active CSI.

## Test Signals
Exercise supported media-bus codes, parallel and MIPI CSI2 modes, interlaced and progressive field handling, destination switching, skip/downsize controls, and invalid configuration rejection. Hardware signals include frame IRQs, correct active window size, and `ipu_csi_dump()` register values matching sensor timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dc.c

## Purpose
Implements the IPUv3 Display Controller programming layer. It maps IPU display channels to DI outputs, writes DC template microcode, configures bus pixel maps, and enables/disables DC channels and the global DC block.

## Important APIs, Types, and Functions
`struct ipu_dc` represents a display channel with channel number, DI selection, base pointer, and in-use flag. `struct ipu_dc_priv` owns global DC registers, template memory, array of ten channels, mutex, and completion. Exported APIs include `ipu_dc_init_sync()`, `ipu_dc_enable()/disable()`, `ipu_dc_enable_channel()/disable_channel()`, `ipu_dc_get()/put()`, `ipu_dc_init()/exit()`. Helpers `dc_link_event()` and `dc_write_tmpl()` program event routing and template words; `ipu_bus_format_to_map()` maps media bus formats.

## Control Flow
Initialization maps DC and template register windows, initializes channel bases, writes default channel config for DI0/DI1, and sets sync priorities. A display client gets a channel, calls `ipu_dc_init_sync()` with DI, interlace, pixel width, and bus format, which programs template words, event links, word sizes, display ID, field mode, and display width. Global and per-channel enable functions set DC_GEN and channel enable bits; disable reverses those bits and clears foreground/window state through caller-specific sequences.

## State and Persistence
Runtime state is channel allocation flags, selected DI in each `struct ipu_dc`, and hardware DC/template registers. The mutex serializes global register and allocation operations. No persistent disk state exists.

## Dependencies and Integration Points
Depends on media bus format constants, `struct ipu_di` for sync timing, and common IPU module enable/disable routines. It sits in the display pipeline between IDMAC/DMFC/DP and the DI output timing block.

## Risks
Template opcodes and event-link addresses are hardware-specific and hard to validate by inspection. Unsupported bus formats return errors; wrong mapping corrupts color ordering. Channel get/put balancing is required, and misprogramming DI/channel association can route pixels to the wrong display. Enable/disable races with active scanout can cause visible artifacts if callers do not sequence with vblank or DP/DC dependencies.

## Test Signals
Display bring-up for RGB565/RGB666/RGB888 and interlaced modes, channel allocation contention tests, register dumps for template words, and visual color-channel tests are important. Enabling/disabling during modesets should be checked for underflows or stuck DC_STAT bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-di.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-di.c

## Purpose
Implements Display Interface timing generation for IPUv3. It programs pixel clocks, sync waveforms, data pins, polarities, and panel timing registers for DI0/DI1.

## Important APIs, Types, and Functions
`struct ipu_di` stores ID, use count, clocks, IPU pointer, module bit, and MMIO base. `struct di_sync_config`, `enum di_pins`, and sync wave enums describe waveform generation. Exported APIs include `ipu_di_adjust_videomode()`, `ipu_di_init_sync_panel()`, `ipu_di_enable()/disable()`, `ipu_di_get_num()`, `ipu_di_get()/put()`, `ipu_di_init()/exit()`. Core helpers are `ipu_di_sync_config()`, interlaced/noninterlaced sync builders, `ipu_di_config_clock()`, and pin/data-wave configuration routines.

## Control Flow
Clients acquire a DI, optionally adjust a videomode to hardware constraints, call `ipu_di_init_sync_panel()` with signal config, then enable the DI pixel clock. Sync-panel setup locks a global mutex, configures clock source/divider, generates waveforms for H/V sync, data enable, and interlaced fields, sets polarity and data-ready behavior, and writes DI_GENERAL. Enable prepares/enables the chosen pixel clock; disable unprepares it.

## State and Persistence
Per-DI state includes selected `clk_di_pixel`, use count, and MMIO timing registers. `di_mutex` serializes global timing programming, while `ipu_di_lock` protects get/put use counts. Clock rates may be changed via `clk_set_rate()`, affecting shared clock tree state beyond this driver.

## Dependencies and Integration Points
Depends on Linux clk, videomode structures, IPU module enable/disable, and display clients that provide `struct ipu_di_signal_cfg`. It integrates directly with DC through DI IDs and with panel/bridge drivers through mode timing and polarity.

## Risks
Clock divisor selection is sensitive to pixel-clock limits and parent rates; rounding can produce modes outside display tolerance. Interlaced waveform generation has many derived offsets and counters. Global locking prevents concurrent programming but not bad sequencing by callers. `WARN_ON(IS_ERR(di->clk_di_pixel))` indicates enable/disable assumes successful prior initialization.

## Test Signals
Mode validation should cover low/high pixel clocks, external clock flags, interlaced and progressive modes, polarity variants, and DI0/DI1 concurrency. Scope or display-controller measurements of HSync/VSync/data-enable timing are the strongest hardware validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-di.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dmfc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dmfc.c

## Purpose
Configures the Display Multi FIFO Controller, which allocates FIFO behavior for IPU display/DP channels and controls wait-for-end-of-transfer behavior.

## Important APIs, Types, and Functions
`struct dmfc_channel_data` maps IPU channel numbers to DMFC register offsets and shift positions. `struct dmfc_channel` stores per-channel mapping and in-use state; `struct ipu_dmfc_priv` stores base MMIO, mutex, IPU pointer, and channel array. Exported APIs are `ipu_dmfc_enable_channel()`, `ipu_dmfc_disable_channel()`, `ipu_dmfc_config_wait4eot()`, `ipu_dmfc_get()/put()`, `ipu_dmfc_init()/exit()`.

## Control Flow
Initialization maps the DMFC register page, initializes the known channel mappings, and writes default FIFO allocation/control values. Display clients get the DMFC channel matching their IPU channel, enable or disable it by setting per-channel bits under the mutex, and may configure wait-for-EOT based on frame width.

## State and Persistence
State is the in-use bit per channel plus DMFC hardware registers. The mutex protects all register read-modify-write operations and allocation state. No disk persistence exists.

## Dependencies and Integration Points
Depends on IPU channel constants from `<video/imx-ipu-v3.h>` and common module lifetime managed by `ipu-common.c`. It integrates with DC/DP/DI display scanout paths by ensuring display channels have appropriate FIFO behavior.

## Risks
Only a fixed set of channel mappings is supported; invalid channel requests fail. Incorrect FIFO defaults or wait4eot thresholds can cause display underflow, tearing, or latency. Because it is shared by display flows, unbalanced get/put or enable/disable affects other clients.

## Test Signals
Display underflow counters, stable scanout under high memory load, channel get failure tests, and register checks after init/enable/disable are relevant. Mode changes across narrow and wide frame widths should exercise wait4eot programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dmfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dp.c

## Purpose
Implements the IPUv3 Display Processor layer for foreground/background composition, global alpha, color-space conversion, foreground positioning, and flow/channel enablement.

## Important APIs, Types, and Functions
`struct ipu_dp`, `struct ipu_flow`, and `struct ipu_dp_priv` model DP channels, sync/async flows, and global state protected by a mutex. Exported APIs include `ipu_dp_set_global_alpha()`, `ipu_dp_set_window_pos()`, `ipu_dp_setup_channel()`, `ipu_dp_enable()/disable()`, `ipu_dp_enable_channel()/disable_channel()`, `ipu_dp_get()/put()`, and init/exit. `ipu_dp_csc_init()` writes hard-coded CSC matrices for RGB/YUV conversion combinations.

## Control Flow
Initialization maps the DP register page and creates three flows: sync, async0, and async1. Clients acquire a DP channel by flow, configure input/output color spaces and foreground/background behavior, optionally set alpha/window position, then enable the global DP module and the specific channel. Disable clears channel enable, foreground enable, and foreground position; sync disable can request SRM DP update through common code.

## State and Persistence
State is DP flow/channel in-use flags and hardware registers for composition, CSC, alpha, and positions. The mutex serializes register updates and allocation. No filesystem persistence exists.

## Dependencies and Integration Points
Depends on DRM color management definitions for color-space concepts, IPU color-space helpers, and common module enable/SRM update functions. It integrates with DMFC/DC/DI display output and display clients that compose overlay/primary planes.

## Risks
CSC coefficients are fixed tables; unsupported or mismatched color spaces can produce wrong colors. Foreground/background configuration depends on caller channel roles. `ipu_dp_disable_channel()` optionally syncs through SRM, so callers must choose the correct sync behavior for active display updates. Shared flow state requires balanced get/put.

## Test Signals
Plane composition tests with global alpha on/off, foreground position changes, RGB-to-YUV and YUV-to-RGB output validation, async/sync flow coverage, and modeset enable/disable stress are key. Visual color bars and CRCs can detect CSC regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic-csc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic-csc.c

## Purpose
Provides color-space conversion coefficient selection and calculation for the IPUv3 Image Converter. It maps input/output encoding, quantization, and color space to hardware CSC coefficients.

## Important APIs, Types, and Functions
The file is mostly static coefficient tables for identity, RGB full/limited, YUV full/limited, BT.601, and BT.709 conversions. `calc_csc_coeffs()` selects a parameter table and stores coefficients into `struct ipu_ic_csc`. Exported APIs are `__ipu_ic_calc_csc()` for prefilled CSC descriptors and `ipu_ic_calc_csc()` for callers providing V4L2 encodings, quantization, and IPU color spaces.

## Control Flow
Callers set or pass source/destination encoding and quantization. `ipu_ic_calc_csc()` fills the CSC descriptor and delegates to `__ipu_ic_calc_csc()`, which validates the combination and calls `calc_csc_coeffs()`. The resulting descriptor is consumed by `ipu-ic.c` when programming task parameter memory.

## State and Persistence
There is no mutable global state. Coefficient tables are static read-only data; calculated coefficients live in caller-owned `struct ipu_ic_csc`.

## Dependencies and Integration Points
Depends on IPU private color-space definitions, V4L2 ycbcr/quantization enums passed from image conversion and other IC users, and `ipu-ic.c` CSC programming. Kconfig-selected `BITREVERSE` is used elsewhere when these coefficients are packed into hardware.

## Risks
Colorimetry combinations outside the table return errors. Limited/full-range mapping is subtle and can cause washed-out or crushed output if caller metadata is wrong. Future color spaces or encodings require explicit table additions rather than automatic derivation.

## Test Signals
Unit-style tests should cover every RGB/YUV, full/limited, BT.601/BT.709 matrix path and invalid combinations. Hardware validation can compare converted color bars or image CRCs against software conversion references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic-csc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic.c

## Purpose
Implements IPUv3 Image Converter task control for preprocessing, viewfinder, and post-processing tasks. It configures resizing, CSC, combiner, rotation, IDMAC task dimensions, and IC/IRT module enablement.

## Important APIs, Types, and Functions
`struct ic_task_regoffs` and `struct ic_task_bitfields` map task-specific register offsets and bit positions. `struct ipu_ic` represents an individual task, while `struct ipu_ic_priv` owns the MMIO base, task parameter memory, spinlock, task array, and use count. Exported APIs include `ipu_ic_task_enable()/disable()`, `ipu_ic_task_init_rsc()`, `ipu_ic_task_init()`, `ipu_ic_task_idma_init()`, `ipu_ic_enable()/disable()`, `ipu_ic_get()/put()`, `ipu_ic_init()/exit()`, and `ipu_ic_dump()`.

## Control Flow
Clients acquire an IC task, initialize resizing/CSC with `ipu_ic_task_init_rsc()` or `ipu_ic_task_init()`, initialize associated IDMAC channel parameters with `ipu_ic_task_idma_init()`, enable the IC module, then enable the task. The task init path validates resize limits, computes downsizing and resize coefficients, writes CSC coefficients into task parameter memory, and sets task bits. Disable clears task bits, rotation/IRT state, and module enable as appropriate.

## State and Persistence
Mutable state includes task `inuse` flags, IC module use count, and hardware registers/task parameter memory. A spinlock serializes most register and allocation operations. Hardware state persists until disabled, reset, or overwritten.

## Dependencies and Integration Points
Depends on `ipu-ic-csc.c` for CSC descriptors, CPMEM/IDMAC channel setup, common module enable/disable, and image-convert clients. The IRT rotation path uses common module bits for rotation-specific hardware.

## Risks
Resize coefficients have hardware limits; invalid dimensions return errors but borderline rounding can affect image quality. Multiple tasks share global IC registers and parameter memory, so locking and use count correctness are critical. Rotation paths require coordinated IDMAC links and IRT enablement; partial failures can leave modules enabled if caller unwinding is wrong.

## Test Signals
Coverage should include all IC tasks, resize up/down limits, CSC on/off, rotation and non-rotation IDMAC initialization, task allocation contention, and dump inspection. End-to-end image conversion CRCs are the best behavioral signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-image-convert.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-image-convert.c

## Purpose
Provides an asynchronous tiled image conversion service on top of IPUv3 IC, IDMAC, CPMEM, and optional IRT rotation. It adjusts/verifies image constraints, splits large images into hardware-sized tiles, computes resize coefficients and tile offsets, queues conversion runs, handles EOF interrupts, and invokes completion callbacks.

## Important APIs, Types, and Functions
Important types are `struct ipu_image_convert_ctx` for prepared conversion state, `struct ipu_image_convert_chan` for per-IC-task queues/resources/IRQs, `struct ipu_image_convert_priv` for global service state, and tile/format/DMA helper structures. Exported APIs are `ipu_image_convert_adjust()`, `ipu_image_convert_verify()`, `ipu_image_convert_prepare()`, `ipu_image_convert_queue()`, `ipu_image_convert_abort()`, `ipu_image_convert_unprepare()`, `ipu_image_convert()`, init, and exit. Internal pillars include resize coefficient calculation, tile seam selection, tile dimension/offset calculation, `convert_start()`, EOF IRQ handling, and resource acquisition/release.

## Control Flow
Clients either call the canned `ipu_image_convert()` or explicitly prepare a context, queue one or more runs, and unprepare after callbacks. Prepare validates formats and sizes, calculates downsize/resize coefficients, determines tile rows/columns, maps output tile order for rotation, allocates intermediate DMA buffers for IRT rotation, computes CSC, decides whether double-buffering is safe, adds the context to the channel list, and lazily acquires IC/IDMAC/IRQ resources for the first context. Queue adds a run to `pending_q` and starts it immediately if no run is active. EOF IRQs accumulate input/output/rotation completion bits; when a tile completes, the handler either reprograms buffers for the next tile or stops hardware, moves the run to `done_q`, and wakes the threaded bottom half. The bottom half drains done runs and calls client callbacks.

## State and Persistence
State is entirely runtime: context lists, pending/done queues, current run, spinlock-protected IRQ state, abort completion, tile metadata, intermediate coherent DMA buffers, and acquired IPU resources. Hardware state spans IC task registers, CPMEM channel descriptors, IDMAC buffer readiness, FSU links for rotation, and IRQ mappings. There is no filesystem persistence.

## Dependencies and Integration Points
Integrates deeply with `ipu-common.c` IDMAC/IRQ APIs, `ipu-cpmem.c`, `ipu-ic.c`, `ipu-ic-csc.c`, and V4L2 image metadata. It uses DMA coherent allocation for rotation intermediates and threaded IRQs for EOF completion. Public declarations are in `<video/imx-ipu-image-convert.h>`.

## Risks
This is the highest-risk file in the subset. Queue and IRQ state are protected by one spinlock, but callbacks run after dropping it, so lifecycle rules are important. Abort waits up to 10 seconds and then force-stops hardware; double-buffered conversions intentionally defer abort until safe. Tile calculations must obey alignment, subsampling, rotation, stride, and 4:1 resize limits; mistakes cause memory corruption or bad images. Resource acquisition is lazy and shared per IC task, so prepare/unprepare imbalance leaks IRQs/channels. Planar formats disable double buffering because CPMEM has shared UV offsets.

## Test Signals
End-to-end tests should cover packed and planar formats, min/max dimensions, multi-tile scaling, 90/270-degree IRT rotation, double-buffered and single-buffered paths, abort while pending and active, invalid format/size rejection, and concurrent contexts per IC task. Strong signals are completion callback status, image CRC comparison against software reference, absence of IRQ storms, and no leaked IDMAC/IRQ resources after unprepare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-image-convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-pre.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-pre.c

## Purpose
Implements the i.MX6QP IPU Prefetch Resolve Engine support used by DRM/display paths for tiled framebuffer prefetch and resolve into an intermediate IRAM buffer.

## Important APIs, Types, and Functions
`struct ipu_pre` stores list membership, device, IPU pointer, MMIO base, AXI clock, IRAM pool, allocated buffer virtual/physical addresses, and current shadow register state. Public functions include `ipu_pre_get_available_count()`, `ipu_pre_lookup_by_phandle()`, `ipu_pre_get()/put()`, `ipu_pre_configure()`, `ipu_pre_update()`, `ipu_pre_update_pending()`, `ipu_pre_get_baddr()`, and platform probe/remove. Helpers issue software reset and configure TPR tile format.

## Control Flow
Probe maps registers, gets the AXI clock, obtains the `fsl,iram` gen_pool, allocates a fixed intermediate buffer sized for `IPU_PRE_MAX_WIDTH * IPU_PRE_NUM_SCANLINES * 4`, enables the clock, and adds the instance to a global list. Users look up/get a PRE, configure dimensions, strides, modifier/tile settings, current/next buffer addresses, prefetch and store engines, then update the next buffer during scanout with `ipu_pre_update()`. Remove deletes from the list, disables the clock, and frees IRAM.

## State and Persistence
Global state is `ipu_pre_list` plus `available_pres` protected by `ipu_pre_list_mutex`. Per-engine state includes the allocated IRAM buffer, current control shadow (`pre->cur.ctrl`), and hardware registers. No disk persistence exists; IRAM allocation persists for device lifetime.

## Dependencies and Integration Points
Built only with DRM. Depends on DRM fourcc modifiers, genalloc IRAM pools, platform/OF, clk, and IPU private APIs. It integrates with `ipu-prg.c`, which obtains PRE instances for PRG channels, and with display scanout code that needs resolved/tiled buffer handling.

## Risks
IRAM availability is mandatory; probe fails if the pool or allocation is missing. Width is capped at 2048 and buffer sizing assumes four bytes per pixel over eight scanlines. Update waits/polls store-engine status and can be sensitive to scanout timing. Global list lookup by phandle must match IPU/PRG device tree relationships.

## Test Signals
Probe/remove with and without IRAM, PRE allocation exhaustion, tiled modifiers, buffer address updates during active scanout, update-pending polling, and suspend-like reconfiguration should be exercised. Display CRCs and underflow counters reveal resolve/prefetch errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-pre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prg.c

## Purpose
Implements the i.MX6QP IPU Prefetch Resolve Gasket, which connects IPU display channels to PRE engines and configures stride, height, base addresses, bypass, shadow updates, and runtime power for tiled framebuffer scanout.

## Important APIs, Types, and Functions
`struct ipu_prg_channel` tracks the PRE assigned to each PRG channel. `struct ipu_prg` stores list membership, device, IPU pointer, MMIO base, clocks, regmap to IOMUXC GPR, and channel state. Exported APIs include `ipu_prg_lookup_by_phandle()`, `ipu_prg_max_active_channels()`, `ipu_prg_present()`, `ipu_prg_format_supported()`, `ipu_prg_enable()/disable()`, `ipu_prg_channel_disable()`, `ipu_prg_channel_configure()`, and `ipu_prg_channel_configure_pending()`. Probe/remove and PM ops manage platform lifetime.

## Control Flow
Probe maps registers, gets IPG/AXI clocks, obtains a syscon regmap, enables clocks, deasserts bypass/shadow defaults, sets thresholds, enables runtime PM, and adds the PRG to a global list. The IPU core looks up PRG by phandle during probe. Display code enables runtime PM, configures a channel by mapping IPU channel to PRG channel, obtaining a PRE, programming stride/height/base/offset/control fields, triggering register update, and polling buffer-ready status. Disable clears channel control, triggers update, releases PRE, and drops runtime PM.

## State and Persistence
Global state is `ipu_prg_list` protected by `ipu_prg_list_mutex`. Per-PRG state includes clock/runtime-PM state, register values, PRE assignments, and IOMUXC GPR linkage. Hardware register state persists until runtime suspend/reset/reconfiguration.

## Dependencies and Integration Points
Built only with DRM and registered alongside the IPU core. Depends on DRM fourcc, runtime PM, clk, regmap/syscon for `fsl,imx6q-iomuxc-gpr`, platform/OF, PRE APIs, and IPU channel definitions. It integrates with `ipu-common.c` through `ipu->prg_priv` and with CPMEM setup, which avoids setting nonzero AXI IDs when PRG is present.

## Risks
Channel mapping only supports selected IPU display channels. PRE acquisition can fail when no compatible PRE is free. Runtime PM and direct clock suspend/resume must stay balanced, or register access can occur while clocks are disabled. Polling `IPU_PRG_STATUS` for buffer readiness can time out. Format support is intentionally narrow, mostly tiled RGB paths; unsupported modifiers/formats must be rejected by callers.

## Test Signals
Probe deferral via phandle, runtime PM cycles, channel configure/disable for every mapped display channel, PRE exhaustion, unsupported format rejection, suspend/resume register access, and display CRCs for tiled framebuffer scanout are important. Timeout logs from configure-pending or status polling indicate PRG/PRE handoff failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-prg.c -->
