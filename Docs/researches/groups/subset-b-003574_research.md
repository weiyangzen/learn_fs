# Research: subset-b-003574

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.c

## Purpose

This is the platform and DRM core entry point for the Freescale/NXP DCU DRM driver. It binds `fsl,ls1021a-dcu` and `fsl,vf610-dcu` platform devices, maps the DCU register block through regmap, enables clocks, registers a derived pixel-clock divider, initializes optional TCON bypass support, allocates/registers the DRM device, installs IRQ/vblank handling, and wires system suspend/resume.

## Important APIs, Types, And Functions

Key functions are `fsl_dcu_drm_probe()`, `fsl_dcu_drm_remove()`, `fsl_dcu_drm_shutdown()`, `fsl_dcu_load()`, `fsl_dcu_unload()`, `fsl_dcu_drm_irq()`, `fsl_dcu_irq_install()`, `fsl_dcu_drm_pm_suspend()`, and `fsl_dcu_drm_pm_resume()`. The file defines the `fsl_dcu_drm_driver`, `fsl_dcu_drm_platform_driver`, SoC data for LS1021A and VF610, an OF match table, `legacyfb_depth`, and a regmap configuration with `DCU_INT_STATUS` and `DCU_UPDATE_MODE` marked volatile.

## Control Flow

Probe allocates `struct fsl_dcu_drm_device`, selects SoC data from OF, maps MMIO, fetches IRQ and clocks, enables the DCU clock, chooses the pixel-clock parent (`pix` clock or legacy `dcu` fallback), registers a divider on `DCU_DIV_RATIO`, initializes optional TCON, allocates the DRM device, stores private pointers, registers the DRM device, and starts fbdev/client setup. Driver load initializes KMS objects, enables LS1021A SCFG PIXCLK if available, initializes vblank, installs IRQ, and validates legacy fb depth. IRQ reads `DCU_INT_STATUS`, forwards vblank bit 3 to DRM, then writes the status back to acknowledge. Suspend disables IRQ, suspends mode config, and disables the DCU clock; resume re-enables clock, restores TCON bypass and layer registers, re-enables IRQ, and resumes mode config.

## State And Persistence

Persistent driver state lives in `fsl_dcu_drm_device`: regmap, IRQ number, core and pixel clocks, TCON pointer, DRM object, CRTC/encoder/connector storage, and SoC capabilities. Hardware state includes interrupt masks/status, mode-setting registers, DCU layer descriptors, the divider register, and the LS1021A SCFG pixel-clock gate. Suspend drops the clock and relies on resume reinitialization and DRM mode restoration. `legacyfb_depth` is a module parameter and is normalized to 16/24/32 bpp during load.

## Dependencies And Integration Points

The file integrates Linux platform/OF, clk, regmap, syscon, PM sleep, DRM GEM DMA helpers, DRM fbdev DMA helpers, KMS helpers, vblank, `fsl_dcu_drm_modeset_init()`, plane reinitialization, and `fsl_tcon`. It also depends on SoC-specific register layout differences from `fsl_dcu_drm_drv.h`.

## Risks And Test Signals

Risks include IRQ-not-connected handling, regmap volatility mistakes for W1C/status registers, unbalanced clock or pixel-divider cleanup on probe failure, permanently enabled LS1021A PIXCLK power cost, and suspend/resume ordering around IRQ and mode restoration. Test signals are platform probe/remove, invalid `legacyfb_depth`, vblank interrupts, fbdev creation, suspend/resume with active modes, TCON-present and TCON-absent device trees, big-endian divider shift handling, and both LS1021A/VF610 layer-count variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.h

## Purpose

This header is the central register and private-state contract for the FSL DCU DRM driver. It defines DCU global register offsets, interrupt bits, timing/background/threshold fields, layer descriptor address calculations and bit encodings, supported DCU pixel format IDs, LS1021A SCFG pixel-clock control bits, SoC layer layout constants, and the private device structures consumed by the driver, KMS, output, and plane files.

## Important APIs, Types, And Macros

Important register macros cover `DCU_DCU_MODE`, `DCU_BGND`, `DCU_DISP_SIZE`, `DCU_HSYN_PARA`, `DCU_VSYN_PARA`, `DCU_SYN_POL`, `DCU_THRESHOLD`, `DCU_INT_STATUS`, `DCU_INT_MASK`, `DCU_DIV_RATIO`, `DCU_UPDATE_MODE`, and `DCU_CTRLDESCLN(layer, reg)`. Layer macros encode height/width, position, enable, tiling, alpha blending, BPP, chroma-key bounds, colors, and pre/post skip. `struct fsl_dcu_soc_data` describes per-SoC layer counts and descriptor register count. `struct fsl_dcu_drm_device` stores device, node, regmap, IRQ, clocks, optional TCON, DRM objects, connector, and SoC data. It declares `fsl_dcu_drm_modeset_init()`.

## Control Flow

The header has no executable control flow. It shapes runtime control by giving other files the register contract. The platform driver selects a `fsl_dcu_soc_data`, KMS uses mode/timing macros to program the CRTC, planes compute descriptor offsets through `DCU_CTRLDESCLN()`, and IRQ code uses `DCU_INT_STATUS_VBLANK` and masks to reset/ack interrupts.

## State And Persistence

The structures define driver-owned persistent state across probe, modeset, and PM. The register macros describe persistent hardware state in the DCU and SCFG blocks. Layer descriptor registers remain programmed until explicitly reset, overwritten by atomic updates, or lost through clock/power reset.

## Dependencies And Integration Points

It includes DRM encoder and local CRTC/output/plane headers, and forward-declares kernel/DRM types. Integration points are the platform driver, CRTC programming, plane programming, output connector storage, optional TCON handling, regmap register access, syscon PIXCLK enable, and DRM private data.

## Risks And Test Signals

Risks are incorrect descriptor stride math between LS1021A and VF610, format-code mismatches with DRM fourcc selection, bitfield overflow from unchecked mode geometry, and stale register definitions if SoC variants diverge. Test by building all FSL DCU objects, probing both compatibles, exercising every advertised pixel format, validating 16-layer and 64-layer reset loops, and checking that horizontal display widths obey the DCU 16-pixel granularity used by the output code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_kms.c

## Purpose

This file initializes the DRM mode-setting topology for the FSL DCU driver. It sets mode configuration bounds and callbacks, creates the CRTC, encoder, and output connector/bridge/panel objects, resets mode state, and starts KMS polling.

## Important APIs, Types, And Functions

The exported entry point is `fsl_dcu_drm_modeset_init()`. It uses `drm_mode_config_init()`, `drm_mode_config_reset()`, `drm_kms_helper_poll_init()`, `drm_mode_config_cleanup()`, `fsl_dcu_drm_crtc_create()`, `fsl_dcu_drm_encoder_create()`, and `fsl_dcu_create_outputs()`. The local `fsl_dcu_drm_mode_config_funcs` supplies atomic helper check/commit and GEM framebuffer creation.

## Control Flow

Initialization sets the mode bounds to minimum zero and maximum 2031x2047, assigns `fsl_dcu_drm_mode_config_funcs`, creates the CRTC first, then the encoder, then external outputs. On success it resets mode state and enables helper polling. Any failure jumps to cleanup and returns the failing error code.

## State And Persistence

The file mutates `drm->mode_config` and causes CRTC/encoder/connector objects to be registered inside DRM mode lists. No independent state is stored in this file. Polling state persists until `drm_kms_helper_poll_fini()` in the driver unload/remove path.

## Dependencies And Integration Points

It integrates DRM atomic helpers, GEM framebuffer helper, probe/poll helpers, the local CRTC creation API, and output creation API. It is called by `fsl_dcu_load()` and is therefore on the critical DRM registration path.

## Risks And Test Signals

Risks include cleanup after partially-created objects, too-low max width/height for future DCU variants, and missing polling teardown on later load failure paths. Test signals are probe success/failure injection in CRTC/encoder/output creation, `modetest` connector enumeration, fb creation, atomic commits, and hotplug/panel detection polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_output.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_output.h

## Purpose

This header defines the FSL DCU connector wrapper and output creation entry points. It is the interface between core driver storage and the RGB/panel/bridge output implementation.

## Important APIs, Types, And Functions

`struct fsl_dcu_drm_connector` embeds `struct drm_connector` and stores its `drm_encoder` and attached `drm_panel`. `to_fsl_dcu_connector()` converts a DRM connector pointer to the wrapper. The file declares `fsl_dcu_drm_encoder_create()` and `fsl_dcu_create_outputs()`.

## Control Flow

There is no runtime logic beyond the inline container conversion. The declared functions are called during KMS initialization: encoder creation precedes output discovery, and output discovery may create a panel-backed connector or attach a bridge.

## State And Persistence

The connector wrapper persists as part of `struct fsl_dcu_drm_device`; it is not dynamically allocated per connector in this header. The `panel` pointer is set by output discovery and used for mode enumeration.

## Dependencies And Integration Points

It depends on DRM connector/encoder/panel types through including translation units. It integrates `fsl_dcu_drm_drv.h`, the RGB output file, KMS initialization, panel helpers, and bridge attachment.

## Risks And Test Signals

Risks are lifetime mismatches around the embedded connector and panel pointer, and null conversion use if a connector is absent. Test signals are build coverage, panel-backed device trees via legacy `fsl,panel`, modern graph panel/bridge endpoints, connector cleanup, and mode enumeration through `drm_panel_get_modes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.c

## Purpose

This file implements FSL DCU primary-plane allocation, atomic plane validation, layer descriptor programming, and layer reset. It maps DRM framebuffer formats and plane state to DCU hardware layer descriptors.

## Important APIs, Types, And Functions

Important functions are `fsl_dcu_drm_plane_index()`, `fsl_dcu_drm_plane_atomic_check()`, `fsl_dcu_drm_plane_atomic_disable()`, `fsl_dcu_drm_plane_atomic_update()`, `fsl_dcu_drm_init_planes()`, and `fsl_dcu_drm_primary_create_plane()`. It defines DRM plane helper/functions and `fsl_dcu_drm_plane_formats` for RGB565, RGB888, XRGB/ARGB8888, XRGB/ARGB4444, XRGB/ARGB1555, and YUV422.

## Control Flow

Plane creation allocates a `struct drm_plane`, initializes it as a primary universal plane with possible CRTCs filled later, and adds helper callbacks. Atomic check accepts only the supported formats. Atomic update exits if no framebuffer, maps the DRM plane index to a DCU layer by reversing `total_layer - index - 1`, gets the DMA GEM object, converts the fourcc to a DCU BPP code and alpha mode, then writes descriptor registers for size, position, base DMA address, enable/BPP/alpha, chroma key min/max, tile, foreground/background, and LS1021A-specific skip values. Disable clears `DCU_LAYER_EN` in descriptor register 4. Plane initialization zeros every descriptor register for every hardware layer.

## State And Persistence

Layer descriptor registers are persistent hardware state. Atomic updates overwrite all descriptor fields used by this driver; disable only clears the enable bit, leaving most layer state intact. GEM DMA addresses are consumed directly by hardware. The layer index mapping means DRM plane ordering is inverted relative to DCU layer numbering.

## Dependencies And Integration Points

The file uses DRM atomic and plane helpers, DRM fourcc/framebuffer metadata, GEM DMA helpers, regmap, SoC layer counts from `fsl_dcu_drm_drv.h`, and `fsl_dcu_drm_crtc_create()` indirectly through primary plane creation.

## Risks And Test Signals

Risks include unchecked clipping/scaling constraints beyond format validation, using `plane->state->fb` while fetching `new_state`, DMA address width assumptions, format/alpha mismatches for XRGB versus ARGB variants, and layer register count differences. Test signals are atomic commits for all formats, plane disable/reenable, suspend/resume layer reset, out-of-range plane index logging, LS1021A register-10 programming, and framebuffer panning/position changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.h

## Purpose

This header exposes the FSL DCU plane initialization and primary-plane creation API to the rest of the driver.

## Important APIs, Types, And Functions

It declares `fsl_dcu_drm_init_planes(struct drm_device *dev)` and `fsl_dcu_drm_primary_create_plane(struct drm_device *dev)`. The first resets hardware layer descriptor registers; the second allocates/registers the DRM primary plane.

## Control Flow

The header contains no executable control flow. The CRTC creation path uses `fsl_dcu_drm_primary_create_plane()`, while resume and initialization paths use `fsl_dcu_drm_init_planes()` to clear descriptors before restoring display state.

## State And Persistence

No state is stored here. The declared functions act on persistent DRM plane objects and DCU hardware layer registers.

## Dependencies And Integration Points

It relies on `struct drm_device` from DRM headers in consumers and integrates the plane implementation with CRTC and PM paths.

## Risks And Test Signals

Risk is mostly API drift: callers depend on these functions existing with non-managed allocation semantics. Test signals are compile coverage, CRTC creation, resume register clearing, and successful primary-plane atomic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_rgb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_rgb.c

## Purpose

This file implements the simple RGB/LVDS output side of the FSL DCU DRM driver. It creates a simple LVDS encoder, optionally enables TCON bypass, discovers a panel or bridge from device tree, and creates/registers a panel-backed connector when needed.

## Important APIs, Types, And Functions

Main entry points are `fsl_dcu_drm_encoder_create()` and `fsl_dcu_create_outputs()`. Internal helpers include `fsl_dcu_drm_connector_destroy()`, `fsl_dcu_drm_connector_get_modes()`, `fsl_dcu_drm_connector_mode_valid()`, and `fsl_dcu_attach_panel()`. Connector callbacks use atomic state helpers, single-connector probing, panel mode enumeration, and LVDS connector type.

## Control Flow

Encoder creation sets `possible_crtcs = 1`, enables TCON bypass if available, and initializes a simple LVDS encoder. Output creation first checks the legacy `fsl,panel` phandle and attaches that panel through a locally initialized connector. If absent, it calls `drm_of_find_panel_or_bridge()` for graph-based discovery. A panel is attached through the same connector path; otherwise the bridge is attached directly to the encoder. Mode validation rejects horizontal display values not divisible by 16, matching the DCU display-size register encoding.

## State And Persistence

Output state is stored in the embedded encoder and connector inside `fsl_dcu_drm_device`. The connector stores the panel pointer and encoder pointer. TCON bypass is a hardware bit in the optional TCON block. Connector registration creates sysfs/user-visible state until cleanup.

## Dependencies And Integration Points

The file integrates OF graph helpers, DRM panel/bridge APIs, simple encoder helpers, atomic connector helpers, `drm_panel_get_modes()`, `drm_bridge_attach()`, and `fsl_tcon_bypass_enable()`. It is called by KMS initialization after CRTC creation.

## Risks And Test Signals

Risks include legacy and graph bindings disagreeing, unhandled deferred probe from panel/bridge lookup, connector registration cleanup on attach failure, no EDID/HPD path for bridges in this file, and the strict 16-pixel width rule surprising userspace. Test signals are legacy panel DT, graph panel DT, graph bridge DT, deferred-probe behavior, connector sysfs cleanup, and `modetest` mode validation for widths with and without low four bits set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_rgb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.c

## Purpose

This file implements optional Freescale TCON support used by the DCU driver. Its only runtime display operation is enabling or disabling TCON bypass mode so the DCU can drive a parallel RGB/LVDS encoder path.

## Important APIs, Types, And Functions

Exported functions are `fsl_tcon_init()`, `fsl_tcon_free()`, `fsl_tcon_bypass_enable()`, and `fsl_tcon_bypass_disable()`. Internal helper `fsl_tcon_init_regmap()` maps the phandle resource and creates a named MMIO regmap. The file defines a 32-bit regmap config named `"tcon"`.

## Control Flow

`fsl_tcon_init()` parses the optional `fsl,tcon` phandle from the DCU node. If missing, it returns `NULL` and the main driver continues without TCON. If present, it allocates `struct fsl_tcon`, maps the resource, creates a regmap, obtains the `ipg` clock, enables it, drops the node reference, logs bypass usage, and returns the object. Bypass helpers update `FSL_TCON_CTRL1_TCON_BYPASS` in `FSL_TCON_CTRL1`. `fsl_tcon_free()` disables and releases the clock.

## State And Persistence

The `struct fsl_tcon` stores regmap and IPG clock. TCON bypass is persistent hardware state while the TCON clock/register block is powered. The allocation and regmap mapping are devm-managed; the explicit free helper only handles the non-devm clock reference path.

## Dependencies And Integration Points

It depends on OF address/resource parsing, clk, regmap MMIO, and local `fsl_tcon.h`. The FSL DCU probe calls `fsl_tcon_init()`, encoder creation and resume call bypass enable, and output operation depends on bypass being set for simple RGB/LVDS routing.

## Risks And Test Signals

Risks include returning `NULL` for both absent and failed TCON init, which lets the main driver continue after mapping/clock errors; no explicit call to `fsl_tcon_free()` in the shown DCU remove path; and clock lifetime asymmetry because `of_clk_get_by_name()` is not devm-managed. Test signals are DT with no TCON, DT with valid TCON, invalid TCON resource, missing `ipg` clock, bypass bit readback, and suspend/resume with TCON present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.h

## Purpose

This header defines the minimal Freescale TCON register contract and public API used by the DCU DRM driver.

## Important APIs, Types, And Macros

It defines `FSL_TCON_CTRL1` and `FSL_TCON_CTRL1_TCON_BYPASS` bit 29. `struct fsl_tcon` stores the TCON regmap and IPG clock. The public functions are `fsl_tcon_init()`, `fsl_tcon_free()`, `fsl_tcon_bypass_disable()`, and `fsl_tcon_bypass_enable()`.

## Control Flow

No runtime control flow exists in the header. Consumers call `fsl_tcon_init()` during DCU probe, then use bypass helpers during encoder setup/resume.

## State And Persistence

The struct stores the driver handle to the TCON register block and clock. The bypass bit is persistent hardware state until changed, reset, or power-cycled.

## Dependencies And Integration Points

It includes Linux bitops for `BIT()` and forward-relies on consumers providing `struct device`, `struct regmap`, and `struct clk` definitions. Integration is limited to FSL DCU RGB/LVDS output routing.

## Risks And Test Signals

Risks are small but hardware-facing: a wrong bypass bit prevents panel output, and missing forward declarations could break isolated include use. Test by compiling the FSL DCU driver, enabling/disabling bypass on TCON-capable hardware, and verifying display output after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_tcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Kconfig

## Purpose

This Kconfig entry exposes the Intel GMA500/GMA600/GMA3600/GMA3650 KMS framebuffer DRM driver as `DRM_GMA500`.

## Important APIs, Types, And Symbols

`config DRM_GMA500` is a tristate labeled "Intel GMA500/600/3600/3650 KMS Framebuffer". It depends on `DRM`, `PCI`, `X86`, and `HAS_IOPORT`. It selects DRM client selection, KMS helper, optional fbdev I/O-memory helpers, I2C/bit-banged I2C, and ACPI-related video/backlight/input/platform/WMI support when ACPI is enabled.

## Control Flow

There is no runtime control flow. Build-time selection enables compilation and module availability for the gma500 driver. Dependency selection ensures the old display stack has PCI, x86 I/O port access, I2C/DDC, KMS helpers, and ACPI video/backlight glue available.

## State And Persistence

The file stores no runtime state. Its persistent effect is the kernel configuration value that determines whether `gma500_gfx` is built in, modular, or omitted.

## Dependencies And Integration Points

It integrates with the DRM subsystem menu, PCI/X86 platform support, fbdev emulation, ACPI video/backlight routing, and the Makefile object list for `gma500_gfx.o`.

## Risks And Test Signals

Risks include overly broad `select`s pulling ACPI/WMI support, missing `HAS_IOPORT` for inb/outb users, and stale "experimental" help text. Test signals are `allyesconfig`/`allmodconfig`, X86 builds with and without ACPI/fbdev emulation, module autoload on matching PCI IDs, and absence from non-X86 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Makefile

## Purpose

This Makefile defines the `gma500_gfx` DRM module composition. It aggregates shared GMA500 code, Poulsbo/MRST/Oaktrail/Cedarview display paths, memory management, power, BIOS parsing, I2C, IRQ, and optional ACPI/fbdev components.

## Important APIs, Types, And Symbols

The main build variable is `gma500_gfx-y`, which includes the subset files `backlight.o`, `cdv_device.o`, `cdv_intel_crt.o`, `cdv_intel_display.o`, `cdv_intel_dp.o`, `cdv_intel_hdmi.o`, `cdv_intel_lvds.o`, `framebuffer.o`, `gem.o`, `gma_device.o`, `gma_display.o`, `gtt.o`, and `intel_bios.o`, plus other driver files. Conditional objects are `opregion.o` for `CONFIG_ACPI` and `fbdev.o` for `CONFIG_DRM_FBDEV_EMULATION`. `obj-$(CONFIG_DRM_GMA500)` builds `gma500_gfx.o`.

## Control Flow

No runtime control flow exists. At build time, Kbuild links all listed objects into one module/built-in object, allowing cross-file callbacks through `psb_ops`, DRM helpers, and shared private structures.

## State And Persistence

The Makefile stores build composition only. Its persistent effect is which driver features are present in the compiled kernel/module.

## Dependencies And Integration Points

It integrates the Kconfig symbol with Linux Kbuild and ties Cedarview, Poulsbo, Oaktrail, GEM/GTT/MMU, power, IRQ, I2C, VBT, and fbdev subsystems into a single driver.

## Risks And Test Signals

Risks include object ordering surprises if initcall/static symbol assumptions appear, missing conditional guards for ACPI/fbdev users, and monolithic linkage hiding unused platform code. Test signals are modular and built-in builds, ACPI on/off, fbdev emulation on/off, and link checks for exported cross-file symbols such as `cdv_chip_ops`, `psb_gem_dumb_create`, and `psb_fbdev_driver_fbdev_probe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/backlight.c

## Purpose

This file provides the common GMA500 backlight class-device glue. It tracks logical backlight enable/level state and delegates hardware-specific get/set/init behavior through the chip `psb_ops` table.

## Important APIs, Types, And Functions

Exported functions are `gma_backlight_enable()`, `gma_backlight_disable()`, `gma_backlight_set()`, `gma_backlight_init()`, and `gma_backlight_exit()`. Local backlight ops are `gma_backlight_get_brightness()` and `gma_backlight_update_status()`. It uses `dev_priv->ops->backlight_init`, `backlight_get`, `backlight_set`, and `backlight_name`.

## Control Flow

Initialization defaults the driver state to enabled at level 100, calls the chip-specific backlight init, then skips native registration if ACPI video policy says not to use native backlight. With `CONFIG_BACKLIGHT_CLASS_DEVICE`, it registers a raw backlight device with max `PSB_MAX_BRIGHTNESS`. Updates clamp visible brightness to at least 1, store `dev_priv->backlight_level`, and call the hardware setter only if `backlight_enabled` is true. Enable restores the saved level; disable writes hardware level zero.

## State And Persistence

Persistent state is in `drm_psb_private`: `backlight_enabled`, `backlight_level`, and optional `backlight_device`. Hardware PWM or platform backlight registers are owned by chip-specific callbacks such as Cedarview's `cdv_set_brightness()`.

## Dependencies And Integration Points

It depends on Linux backlight and ACPI video policy, DRM logging, `psb_drv.h`, register headers, BIOS definitions, and power helpers. LVDS/eDP paths call the enable/disable/set helpers during panel sequencing.

## Risks And Test Signals

Risks include forcing minimum userspace brightness to 1, divergence between stored level and hardware if chip callbacks fail silently, and no class device when ACPI chooses firmware/vendor backlight. Test signals are ACPI native/non-native policy, class device registration/removal, brightness reads through chip getter, DPMS panel off/on, and suspend/resume backlight restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.c

## Purpose

This file provides Cedarview-specific chip operations for the GMA500 DRM driver. It initializes Cedarview outputs, disables legacy VGA, implements Cedarview backlight control, PM/power gating, hotplug handling, HDMI/DP connector properties, display-register save/restore, watermarks integration, errata, and the `cdv_chip_ops` dispatch table.

## Important APIs, Types, And Functions

Important functions include `cdv_disable_vga()`, `cdv_output_init()`, `cdv_get_max_backlight()`, `cdv_get_brightness()`, `cdv_set_brightness()`, `cdv_backlight_init()`, `CDV_MSG_READ32()`, `CDV_MSG_WRITE32()`, `cdv_init_pm()`, `cdv_errata()`, `cdv_save_display_registers()`, `cdv_restore_display_registers()`, `cdv_power_down()`, `cdv_power_up()`, `cdv_hotplug_event()`, `cdv_hotplug_enable()`, property attach helpers, `cdv_chip_setup()`, and global `cdv_chip_ops`.

## Control Flow

Chip setup initializes hotplug work, enables MSI use, installs the Cedarview register map, reads core frequency, initializes opregion/VBT, and clears hotplug enables. Output init creates scaling property, disables VGA, initializes CRT and LVDS, then detects SDVOB/SDVOC as HDMI and optionally DisplayPort. PM init discovers APM/OSPM bases through PUNIT sideband config cycles and powers the GPU on. Save/restore capture display, panel, backlight, VGA, and interrupt registers, DPMS connectors off/on, reinitialize DPIO/DPLL sync lock, reapply errata, reset mode config, and force mode restoration. Hotplug IRQ schedules work that emits a DRM HPD event.

## State And Persistence

State persists in `drm_psb_private`: APM/OSPM bases, core frequency, register save area, `hotplug_work`, properties, VBT-derived fields, and `regmap`. Hardware state includes VGA sequencer bits, APM command/status ports, PUNIT message registers, display/clock/watermark registers, backlight PWM, panel power registers, hotplug enable/status, and interrupt mask/enable.

## Dependencies And Integration Points

The file integrates PCI config access, x86 I/O ports, DRM connector iteration, helper DPMS, opregion/VBT parsing, Cedarview CRT/LVDS/HDMI/DP init files, shared CRTC save/restore, watermarks in `cdv_intel_display.c`, and the core `psb_ops` abstraction.

## Risks And Test Signals

Risks include unguarded root PCI device assumptions in sideband helpers, short power-transition retry loops that return success even on timeout in power up/down, fragile save/restore ordering, hotplug status clearing races, and output probing based on register-detected bits. Test signals are Cedarview boot, VGA-disabled display handoff, CRT/LVDS/HDMI/DP enumeration, hotplug IRQs, backlight percentage conversion including legacy combination mode, suspend/resume register restoration, and dual-pipe watermark behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.h

## Purpose

This header declares Cedarview-specific display callbacks and clock helpers shared across the GMA500 Cedarview files.

## Important APIs, Types, And Functions

It declares `cdv_intel_helper_funcs`, `cdv_clock_funcs`, `cdv_intel_crt_init()`, `cdv_intel_lvds_init()`, `cdv_hdmi_init()`, `cdv_intel_crtc_mode_get()`, `cdv_update_wm()`, and `cdv_disable_sr()`. Forward declarations cover DRM CRTC/device and `psb_intel_mode_device`.

## Control Flow

There is no executable flow. The chip ops table consumes the helper/clock structs, output init calls the connector init functions, LVDS/eDP fallback mode discovery calls `cdv_intel_crtc_mode_get()`, and generic CRTC DPMS calls watermark/self-refresh helpers through `psb_ops`.

## State And Persistence

No state is stored here. The declared functions operate on persistent DRM objects, Cedarview hardware registers, and `drm_psb_private` state.

## Dependencies And Integration Points

It links `cdv_device.c` with `cdv_intel_display.c`, `cdv_intel_crt.c`, `cdv_intel_lvds.c`, `cdv_intel_hdmi.c`, and the DP file through declarations.

## Risks And Test Signals

Risks are API drift between declarations and definitions, especially around legacy DRM helper signatures. Test signals are compile/link coverage and Cedarview mode-set, connector init, watermark, and mode-query paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_crt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_crt.c

## Purpose

This file implements Cedarview analog VGA/CRT connector and encoder support for GMA500. It controls the ADPA DAC register, performs CRT hotplug detection, validates CRT modes, creates the DDC bus, and registers DRM connector/encoder callbacks.

## Important APIs, Types, And Functions

The exported function is `cdv_intel_crt_init()`. Internal callbacks include `cdv_intel_crt_dpms()`, `cdv_intel_crt_mode_valid()`, `cdv_intel_crt_mode_set()`, `cdv_intel_crt_detect_hotplug()`, `cdv_intel_crt_detect()`, `cdv_intel_crt_destroy()`, `cdv_intel_crt_get_modes()`, and a no-op property setter. Helper structs are `cdv_intel_crt_helper_funcs`, connector funcs, and connector helper funcs.

## Control Flow

Initialization allocates `gma_encoder` and `gma_connector`, creates a GPIOA DDC bus, initializes a VGA connector with DDC, creates a DAC encoder, attaches them, marks output type `INTEL_OUTPUT_ANALOG`, and installs helper callbacks. DPMS clears or sets DAC/hsync/vsync disable bits according to DRM DPMS mode. Mode set clears a DPLL multiplier used for SDVO clone paths, applies hsync/vsync polarity, and selects pipe A or B in ADPA. Detection forces CRT hotplug twice, waits up to one second for each forced detect, reads monitor status, clears generated interrupt status, and restores hotplug enable bits.

## State And Persistence

Connector/encoder objects persist in DRM mode lists until destroyed. Hardware state persists in ADPA, DPLL MD, hotplug enable/status registers, and DDC GPIO state. The DDC bus is owned by the connector and destroyed on connector cleanup.

## Dependencies And Integration Points

The file depends on DRM simple encoder and helper callbacks, GMA I2C helpers, DDC mode retrieval, Cedarview register macros, shared GMA encoder prepare/commit/destroy, and `gma_best_encoder()`.

## Risks And Test Signals

Risks include long hotplug waits in detect paths, restoring hotplug register bits after concurrent HPD changes, no EDID fallback modes when DDC fails, and mode limits hardcoded to 20-355 MHz. Test signals are VGA monitor plug/unplug, DDC EDID reads, DPMS standby/suspend/off, mode polarity correctness, pipe A/B routing, and cleanup after init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_crt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_display.c

## Purpose

This file implements Cedarview CRTC mode-setting, DPLL programming through the sideband/DPIO bus, clock limit selection, DisplayPort M/N handoff integration, watermark/self-refresh handling, and current-mode reconstruction for GMA500.

## Important APIs, Types, And Functions

Exported symbols are `cdv_sb_read()`, `cdv_sb_write()`, `cdv_sb_reset()`, `cdv_disable_sr()`, `cdv_update_wm()`, `cdv_intel_crtc_mode_get()`, `cdv_intel_helper_funcs`, and `cdv_clock_funcs`. Important internals include the `cdv_intel_limits[]` table, `cdv_dpll_set_clock_cdv()`, `cdv_intel_limit()`, `cdv_intel_clock()`, `cdv_intel_find_dp_pll()`, `cdv_intel_pipe_enabled()`, `cdv_intel_panel_fitter_pipe()`, `cdv_intel_crtc_mode_set()`, `i8xx_clock()`, and `cdv_intel_crtc_clock_get()`.

## Control Flow

Mode set identifies the active connector type for the CRTC, chooses the reference clock from SKU flags, output type, and LVDS SSC settings, selects a clock limit table, computes PLL divisors, programs DP M/N registers for DP/eDP or clears them for non-DP, configures BPC and plane control, writes the DPLL control register in sync-lock mode, programs DPIO sideband PLL M/N/P/reference/lane registers, handles LVDS pair power before DPLL enable, disables panel fitter if already assigned to this pipe, waits for DPLL lock, writes timing registers, enables pipe/plane, and delegates framebuffer base programming to `gma_pipe_set_base()`. Watermark updates choose single-pipe self-refresh values or dual-pipe suggested values and disable self-refresh as needed.

## State And Persistence

Hardware state persists in DPLL control/MD registers, sideband DPIO registers, lane PLL selection registers, pipe timing/source registers, plane control, panel fitter, watermark registers, self-refresh control, and DP M/N registers. Software state uses `gma_crtc->clock_funcs`, `gma_crtc->pipe`, `gma_crtc->active`, `dev_priv->dplla_96mhz`, `lvds_use_ssc`, `lvds_ssc_freq`, and saved register snapshots when power is unavailable.

## Dependencies And Integration Points

The file integrates DRM CRTC helpers, shared GMA display helpers, Cedarview output types, DP M/N programming from `cdv_intel_dp.c`, power management via `gma_power_begin()`, and `psb_ops` watermark/self-refresh callbacks.

## Risks And Test Signals

Risks include fragile sideband timeouts, hardcoded BIOS-like magic values, incorrect reference clock selection for unusual boards, DPLL lock failures, panel fitter reassignment, self-refresh watermark regressions, and mixed legacy helper return semantics where some failures return zero. Test signals are mode-setting on CRT/HDMI/LVDS/DP/eDP, 27/96/100 MHz refclk platforms, DPLL lock readback, DP link clock modes, single- versus dual-pipe watermarks, suspend/resume mode reconstruction, and display underrun monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_dp.c

## Purpose

This file implements Cedarview DisplayPort and embedded DisplayPort support. It includes a legacy I2C-over-AUX adapter, native AUX helpers, DPCD and EDID probing, link bandwidth/lane selection, M/N ratio programming, eDP panel power and backlight sequencing, port mode programming, sink power management, and two-phase DP link training.

## Important APIs, Types, And Functions

The exported entry points are `cdv_intel_dp_init()` and `cdv_intel_dp_set_m_n()`. Important local types are `struct i2c_algo_dp_aux_data`, `struct cdv_intel_dp`, `struct ddi_regoff`, and `struct cdv_intel_dp_m_n`. Important functions include AUX/I2C helpers (`cdv_intel_dp_aux_ch()`, native read/write, I2C xfer), eDP helpers (`cdv_intel_edp_panel_vdd_on/off()`, `panel_on/off()`, `backlight_on/off()`), mode helpers (`cdv_intel_dp_mode_valid()`, `mode_fixup()`, `mode_set()`), training helpers (`cdv_intel_dp_start_link_train()`, `complete_link_train()`, `link_down()`), detect/get_modes/property callbacks, `cdv_intel_dpc_is_edp()`, and `cdv_disable_intel_clock_gating()`.

## Control Flow

Initialization allocates encoder/connector/private state, chooses DisplayPort versus eDP using VBT child-device data, initializes DRM objects, sets output type and DDI selection for DP_B or DP_C, disables display clock gating needed for DP/eDP bring-up, creates an AUX-backed I2C adapter, attaches force-audio and broadcast-RGB properties, and for eDP reads panel timing delays from panel-power registers and validates DPCD while VDD is forced on. Detection reads DPCD over native AUX, optionally reads EDID for audio, and toggles eDP VDD around AUX access. Mode fixup chooses link bandwidth and lane count sufficient for pixel clock and bpp, using a forced maximum fallback for eDP. Commit powers the panel, performs pattern 1 clock recovery and pattern 2 channel equalization with AUX status feedback, then enables backlight.

## State And Persistence

`struct cdv_intel_dp` stores the output register, pending DP register image, link configuration, DPCD, train set/status, audio/color properties, AUX adapter state, lane count/link bandwidth, and eDP power delays/fixed mode/panel-on state. Hardware state persists in DP_B/DP_C registers, AUX control/data registers, DPCD sink registers, PP_CONTROL/status/delay registers, BLC PWM routing, pipe M/N registers, and DPIO lane training registers.

## Dependencies And Integration Points

The file depends on DRM DP helper constants, DRM EDID helpers, I2C core, shared GMA display helpers, `cdv_sb_write()` sideband support, GMA backlight, VBT child device fields from `intel_bios.h`, and Cedarview CRTC mode-set which calls `cdv_intel_dp_set_m_n()`.

## Risks And Test Signals

Risks include the legacy AUX helper needing migration, busy-wait AUX loops without an explicit timeout inside the send-busy wait, complex eDP power sequencing, partial cleanup on DP init failures, disabled DPIO training code under `CDV_FAST_LINK_TRAIN`, property changes forcing full modesets, and link-training fallback behavior that may leave a marginal link active. Test signals are DP/eDP detection, DPCD reads, EDID-over-AUX, force-audio and broadcast-RGB property changes, 1/2/4 lane training at 1.62 and 2.7 Gbps, eDP VDD/panel/backlight timing, hotplug, suspend/resume, and AUX timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_hdmi.c

## Purpose

This file implements Cedarview HDMI/TMDS connector and encoder support for ports exposed through SDVOB/SDVOC register names. It handles DDC-based detection, HDMI audio capability tracking, port control programming, scaling property changes, and DRM object creation.

## Important APIs, Types, And Functions

The exported function is `cdv_hdmi_init()`. Important local pieces are `struct mid_intel_hdmi_priv`, `cdv_hdmi_mode_set()`, `cdv_hdmi_dpms()`, `cdv_hdmi_save()`, `cdv_hdmi_restore()`, `cdv_hdmi_detect()`, `cdv_hdmi_set_property()`, `cdv_hdmi_get_modes()`, `cdv_hdmi_mode_valid()`, and cleanup/helper callback tables.

## Control Flow

Initialization allocates encoder, connector, and private state; picks GPIOE/DDI0 for SDVOB or GPIOD/DDI1 for SDVOC; creates a DDC bus; initializes a DVID connector and TMDS encoder; attaches them; installs helpers; disables interlace/doublescan; and attaches the scaling property. Detection reads EDID, marks connected if the input is digital, and derives HDMI sink/audio flags. Mode set writes sync polarity, pipe select, audio enable, and null-packet bits before DPMS toggles `HDMIB_PORT_EN`. Scaling property changes update the connector property and either call full mode set or encoder mode-set depending on center/no-scale transition.

## State And Persistence

Private state stores the HDMI register offset, saved register value, sink/audio flags, and device pointer. Hardware state persists in the SDVOB/SDVOC HDMI control register and DDC GPIO/I2C state. Connector properties persist until changed by userspace.

## Dependencies And Integration Points

It integrates DRM EDID helpers, GMA I2C, simple encoder creation, shared GMA encoder helpers, Cedarview property helpers, and output detection in `cdv_output_init()`.

## Risks And Test Signals

Risks include connector type `DVID` despite HDMI semantics, no HPD status register use in detection beyond polling setup, mode clock cap hardcoded to 165 MHz, returning `MODE_CLOCK_HIGH` for clocks below 20 MHz, and scaling property paths using legacy helper mode setting. Test signals are EDID detection on both SDVOB/SDVOC, HDMI audio EDID, DPMS on/off, mode validation around 20 MHz and 165 MHz, scaling property changes, and cleanup after DDC or DRM init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_lvds.c

## Purpose

This file implements Cedarview LVDS panel support. It discovers panel presence and fixed mode from VBT, EDID, or currently-programmed registers, creates the LVDS connector/encoder, controls panel power and panel fitter, and exposes scaling/backlight/DPMS properties.

## Important APIs, Types, And Functions

The exported function is `cdv_intel_lvds_init()`. Important local items are `struct cdv_intel_lvds_priv`, `cdv_intel_lvds_get_max_backlight()`, `cdv_intel_lvds_set_backlight()`, `cdv_intel_lvds_set_power()`, `cdv_intel_lvds_encoder_dpms()`, `cdv_intel_lvds_mode_valid()`, `cdv_intel_lvds_mode_fixup()`, `cdv_intel_lvds_prepare()`, `cdv_intel_lvds_commit()`, `cdv_intel_lvds_mode_set()`, `cdv_intel_lvds_get_modes()`, `cdv_intel_lvds_set_property()`, and `lvds_is_present_in_vbt()`.

## Control Flow

Initialization exits if VBT disables LVDS or child-device data says no panel. It allocates connector/encoder/private state, creates LVDS DDC on GPIOC, creates a simple LVDS encoder, attaches scaling and backlight properties, creates an LVDS backlight I2C bus on GPIOB, then probes fixed panel mode: preferred EDID mode first, VBT LFP mode second, and current LVDS pipe mode third. It configures PWM pipe routing and enable. Mode fixup replaces requested timings with fixed panel timings and prevents sharing the CRTC with another encoder. Mode set programs panel fitter scaling/dither. Prepare saves current PWM duty and powers panel off; commit restores a nonzero backlight duty and powers panel on.

## State And Persistence

State persists in `mode_dev->panel_fixed_mode`, `mode_dev->backlight_duty_cycle`, connector properties, `dev_priv->lvds_i2c_bus`, VBT flags, and encoder private storage. Hardware state includes LVDS port/pair power bits, panel power registers, PWM control, PFIT_CONTROL, and BLC PWM duty.

## Dependencies And Integration Points

It depends on DMI/I2C, DRM helper callbacks, GMA I2C/DDC helpers, Cedarview mode query from `cdv_intel_display.c`, BIOS/VBT data from `intel_bios.c`, power helpers, and common backlight logic.

## Risks And Test Signals

Risks include unbounded polling loops waiting for `PP_STATUS`, trusting VBT heuristics for LVDS presence, FIXME around destroying the backlight I2C bus, panel mode fallback from existing hardware state, and property callbacks returning `-1` rather than standard errno values. Test signals are LVDS-enabled/disabled VBT, EDID preferred mode, VBT-only panel mode, no-mode fallback, scaling modes, backlight property changes, DPMS power cycles, and suspend/resume panel restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/fbdev.c

## Purpose

This file implements fbdev emulation support for GMA500 when DRM fbdev emulation is enabled. It allocates a stolen-memory-backed GEM framebuffer for the console, maps it into fbdev, and provides fb mmap/destroy callbacks.

## Important APIs, Types, And Functions

The exported probe is `psb_fbdev_driver_fbdev_probe()`. Local pieces are `psb_fbdev_vm_fault()`, `psb_fbdev_fb_mmap()`, `psb_fbdev_fb_destroy()`, `psb_fbdev_fb_ops`, and an empty `drm_fb_helper_funcs` table.

## Control Flow

Fbdev probe adjusts packed 24 bpp requests to 32 bpp, computes fourcc/pitch/size, allocates a stolen GEM object named `"fb"`, falls back from >16 bpp to 16 bpp on stolen-memory `-EBUSY`, creates a GEM handle and DRM client buffer, links fb helper state, maps `info->screen_base` directly to `dev_priv->vram_addr + offset`, fills fb info, sets physical smem and MMIO ranges, clears the framebuffer, then drops the temporary GEM handle and object reference. Mmap only accepts zero offset, sets VM flags, and faults physical stolen-memory PFNs through `vmf_insert_mixed()`.

## State And Persistence

Persistent fbdev state lives in `drm_fb_helper`, `drm_client_buffer`, `fb_info`, and the stolen GEM object referenced by the framebuffer. Hardware-visible state is the stolen memory contents and GTT allocation. The fbdev mapping is noncached and maps physical stolen memory directly.

## Dependencies And Integration Points

It depends on DRM fb helper/client APIs, GMA GEM allocation, PCI resource reporting, and stolen-memory mapping initialized by `psb_gem_mm_init()`. It is conditionally linked by the Makefile.

## Risks And Test Signals

Risks include vm fault mapping all VMA pages starting at adjusted address, direct stolen-memory access cache attributes, limited fallback only on `-EBUSY`, and correct teardown of helper/client/buffer references. Test signals are fbcon at 16/32 bpp, mmap from `/dev/fb*`, stolen-memory exhaustion, mode changes through fbdev, destroy/unload, and fbdev-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.c

## Purpose

This file initializes GMA500 DRM mode configuration and user framebuffer validation. It creates CRTCs, invokes chip-specific output initialization, assigns encoder CRTC/clone masks, and performs chip errata after output setup.

## Important APIs, Types, And Functions

Important functions are `psb_user_framebuffer_create()`, `psb_setup_outputs()`, `psb_modeset_init()`, and `psb_modeset_cleanup()`. `psb_mode_funcs` supplies the framebuffer creation callback.

## Control Flow

User framebuffer creation rejects unknown depth, YUV or unsupported formats, formats with more than four bytes per pixel, and pitches not aligned to 64 bytes, then delegates to `drm_gem_fb_create()`. Modeset init calls `drmm_mode_config_init()`, sets min bounds and callbacks, creates one CRTC per `dev_priv->num_pipe`, sets max bounds to 4096x4096, runs `psb_setup_outputs()`, applies chip errata, and marks `modeset` true. Output setup creates a scaling property, optionally creates a backlight property, invokes `dev_priv->ops->output_init()`, then iterates connectors to set encoder `possible_crtcs` and clone masks based on GMA output type.

## State And Persistence

Mode config state, CRTC objects, connector/encoder lists, properties, and `dev_priv->modeset` persist after initialization. User framebuffer objects persist through GEM/framebuffer references. Cleanup only finalizes KMS polling when modeset was initialized.

## Dependencies And Integration Points

It integrates DRM mode config, GEM framebuffer helper, connector iteration, chip ops output init/errata masks, CRTC init from other GMA500 files, and `gma_connector_clones()`.

## Risks And Test Signals

Risks include legacy helper mode config without full atomic funcs, pitch alignment rejection compatibility, possible null `backlight_property` attachment if property creation fails, and clone-mask assumptions by output type. Test signals are framebuffer creation with supported/unsupported formats and pitch alignments, CRTC count variants, connector masks for CRT/LVDS/HDMI/DP/eDP, errata invocation, and modeset cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.h

## Purpose

This header provides framebuffer/modeset integration declarations for GMA500.

## Important APIs, Types, And Functions

It includes `psb_drv.h` and declares `gma_connector_clones(struct drm_device *dev, int type_mask)`, used by output setup to compute encoder clone masks.

## Control Flow

No executable flow exists. `psb_setup_outputs()` calls the declared helper while iterating connectors.

## State And Persistence

The header stores no state. The declared function reads DRM connector/encoder state and output type masks to build persistent encoder clone capability fields.

## Dependencies And Integration Points

It ties `framebuffer.c` to shared PSB/GMA driver types and the connector clone helper implemented elsewhere in the driver.

## Risks And Test Signals

Risks are limited to declaration drift and broad inclusion of `psb_drv.h`. Test signals are compile/link success and clone-mask correctness for analog and HDMI connectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.c

## Purpose

This file implements GMA500 GEM object allocation, pinning into the GTT and video MMU, dumb-buffer creation, GEM mmap fault handling, stolen-memory setup, and GEM/GTT resource restoration on resume.

## Important APIs, Types, And Functions

Exported functions are `psb_gem_pin()`, `psb_gem_unpin()`, `psb_gem_create()`, `psb_gem_dumb_create()`, `psb_gem_mm_init()`, `psb_gem_mm_fini()`, and `psb_gem_mm_resume()`. Internal helpers include `psb_gem_free_object()`, `psb_gem_fault()`, `psb_gem_mm_populate_stolen()`, and `psb_gem_mm_populate_resources()`. Object callbacks are `psb_gem_object_funcs` and `psb_gem_vm_ops`.

## Control Flow

Creation rounds size to pages, allocates a `psb_gem_object`, reserves GTT address space from stolen or system range, initializes a private stolen GEM object or normal GEM shmem object, and restricts normal mappings to DMA32 pages. Pinning locks the DMA reservation, no-ops for already mapped/stolen objects, gets pages, marks them WC, inserts PTEs into the hardware GTT and driver MMU at `gatt_start + offset`, stores pages, and increments `in_gart`. Unpin decrements, removes MMU/GTT mappings when the last non-stolen pin drops, restores WB caching, and releases pages. Mmap faults pin once and map either stolen PFNs or backing pages directly. MM init maps stolen memory WC and prepopulates stolen pages in the GTT; resume validates stolen size and repopulates stolen and still-pinned resources.

## State And Persistence

`psb_gem_object` stores GEM base, resource, GTT offset, pin count, stolen flag, mmap pin flag, and backing pages. `drm_psb_private` stores stolen base/size, vram mapping, mmap mutex, and GTT tree. Hardware state includes GTT entries and MMU page-directory mappings. Mmap pins intentionally persist until object destruction.

## Dependencies And Integration Points

It depends on DRM GEM, VMA manager, DMA reservations, Linux page cache/cache-attribute helpers, GTT helpers, PSB MMU helpers, PCI stolen-memory register `PSB_BSM`, and fbdev/CRTC paths that allocate or pin buffers.

## Risks And Test Signals

Risks include permanently pinned mmap objects, correct cache attribute restoration, GTT space exhaustion, 32-bit DMA constraints, stolen-size calculation from GTT physical start, and resume ordering with GTT re-enable/clear. Test signals are dumb-buffer create/mmap/page faults, framebuffer display pin/unpin, stolen fbdev allocation, object destruction with mmap pins, suspend/resume with pinned buffers, and GTT/MMU PTE validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.h

## Purpose

This header defines the GMA500 GEM object wrapper and public GEM/memory-management API.

## Important APIs, Types, And Functions

`struct psb_gem_object` embeds `struct drm_gem_object` and stores a GTT `resource`, `offset`, `in_gart` reference count, `stolen` flag, `mmapping` flag, and backing `pages`. `to_psb_gem_object()` converts from DRM GEM object. Declared functions are `psb_gem_create()`, `psb_gem_pin()`, `psb_gem_unpin()`, `psb_gem_mm_init()`, `psb_gem_mm_fini()`, and `psb_gem_mm_resume()`.

## Control Flow

The header has no executable flow. Display, cursor, fbdev, and dumb-buffer paths create and pin objects through these declarations.

## State And Persistence

The object fields encode persistent allocation and mapping state: GTT resource ownership, GPU-visible offset, pin lifetime, stolen backing, mmap lifetime, and system pages. These fields drive cleanup and resume reconstruction.

## Dependencies And Integration Points

It includes Linux kernel and DRM GEM definitions and is used by framebuffer, fbdev, display, GTT, and PSB driver core files.

## Risks And Test Signals

Risks include manual refcount semantics in `in_gart`, conflating mmap lifetime with pin lifetime, and GTT resource exposure to non-GTT code. Test signals are compile coverage, object create/free, pin/unpin nesting, stolen versus shmem objects, and resume restoration of objects with non-null `pages`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.c

## Purpose

This file provides a shared helper to determine and store the GMA core frequency from chipset/root PCI configuration.

## Important APIs, Types, And Functions

The exported function is `gma_get_core_freq(struct drm_device *dev)`. It writes a message/control value to root PCI config offset `0xD0`, reads offset `0xD4`, decodes the low three bits, and stores `dev_priv->core_freq` as 100, 133, 150, 178, 200, 266, or zero.

## Control Flow

The helper obtains the root PCI device for the domain/bus, performs the config write/read transaction, releases the root device, and switches on `clock & 0x07` to update the private frequency field. Cedarview chip setup calls it before display initialization uses timing/watermark data.

## State And Persistence

The only software state mutation is `drm_psb_private.core_freq`. The helper also briefly changes chipset PCI config message registers as part of the read protocol.

## Dependencies And Integration Points

It depends on PCI, `psb_drv.h`, and `gma_device.h`. It is integrated by `cdv_chip_setup()` and potentially other chip setup paths.

## Risks And Test Signals

Risks include assuming root PCI device lookup succeeds, hardcoded config offsets/protocol, and frequency table validity across chip variants. Test signals are Cedarview/Poulsbo probe, root PCI config access failure handling under fault injection, and comparing stored core frequency against platform documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.h

## Purpose

This header declares the shared GMA core-frequency helper.

## Important APIs, Types, And Functions

It forward-declares `struct drm_device` and declares `gma_get_core_freq(struct drm_device *dev)`.

## Control Flow

No executable flow exists. Chip setup files call the declared helper during device initialization.

## State And Persistence

No state is stored here. The helper mutates `drm_psb_private.core_freq`.

## Dependencies And Integration Points

It provides a small interface between chip-specific setup files and `gma_device.c`.

## Risks And Test Signals

Risks are declaration drift and missing include guards in consumers. Test signals are build/link success and chip setup storing a nonzero core frequency on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.c

## Purpose

This file implements shared legacy CRTC, plane-base, cursor, gamma, DPMS, page-flip, save/restore, encoder, connector, and PLL-search helpers for the GMA500 driver family.

## Important APIs, Types, And Functions

Exported functions include `gma_pipe_has_type()`, `gma_wait_for_vblank()`, `gma_pipe_set_base()`, `gma_crtc_load_lut()`, `gma_crtc_dpms()`, `gma_crtc_prepare()`, `gma_crtc_commit()`, `gma_crtc_disable()`, `gma_crtc_destroy()`, `gma_crtc_page_flip()`, `gma_crtc_save()`, `gma_crtc_restore()`, `gma_encoder_prepare()`, `gma_encoder_commit()`, `gma_encoder_destroy()`, `gma_best_encoder()`, `gma_connector_attach_encoder()`, `gma_pll_is_valid()`, and `gma_find_best_pll()`. It defines `gma_crtc_funcs`.

## Control Flow

Base setting powers the device, pins the new framebuffer GEM object, writes stride and pixel format, programs base/surface registers differently for PSB versus other chips, and unpins the old framebuffer. DPMS enables or disables DPLL, plane, pipe, vblank, palette, self-refresh/watermarks, and FIFO arbitration in the required order. Cursor set looks up and pins the cursor GEM, optionally copies into physical cursor memory, writes cursor control/base, and unpins the old cursor. Page flip assigns the new primary fb, optionally arms a vblank event, calls mode_set_base, and restores the previous fb on failure. Save/restore capture pipe, plane, timing, DPLL, and palette registers. PLL search brute-forces divisors within `gma_limit_t` ranges.

## State And Persistence

Persistent software state includes `gma_crtc->active`, cursor object/address, page-flip event, saved CRTC state, gamma store, and framebuffer GEM pin counts. Hardware state includes pipe/plane/DPLL/timing/palette/cursor registers and GTT/MMU mappings. Old framebuffers are unpinned only after the new base is programmed.

## Dependencies And Integration Points

It depends on DRM CRTC/fourcc/framebuffer/vblank helpers, PSB IRQ vblank helpers, GEM/GTT pinning, power gating (`gma_power_begin/end`), chip ops watermarks/self-refresh, and per-chip register maps.

## Risks And Test Signals

Risks include legacy mutable `crtc->primary->fb` semantics, missing full clipping/scaling validation, fixed 20 ms vblank wait, cursor size limited to 64x64, page-flip event cleanup races, palette fallback storing pipe 0 even for other pipes, and display power failures returning success in some paths. Test signals are mode set, pan/page flip with and without events, vblank events, cursor enable/move/disable, gamma updates, suspend/resume restore, PSB versus CDV base programming, and PLL validation edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.h

## Purpose

This header defines shared GMA display clock data structures and declares common CRTC/encoder/display helper functions.

## Important APIs, Types, And Functions

Types include `struct gma_clock_t` for PLL divisors and derived dot/vco values, `struct gma_range_t`, `struct gma_p2_t`, `struct gma_limit_t` with a `find_pll` callback, and `struct gma_clock_funcs` with clock/limit/validation callbacks. It declares shared pipe, base, LUT, DPMS, CRTC lifecycle, page flip, save/restore, encoder lifecycle, `gma_crtc_funcs`, `gma_limit()`, `gma_pll_is_valid()`, and `gma_find_best_pll()`.

## Control Flow

There is no executable flow. Per-chip display code installs `gma_clock_funcs` and CRTC helper callbacks using these declarations; shared display code calls chip clock callbacks through the structs.

## State And Persistence

The structs are transient calculation contracts for PLL selection. Function declarations operate on persistent DRM CRTC/encoder/framebuffer objects and hardware registers.

## Dependencies And Integration Points

It includes PM runtime and DRM vblank headers and connects Cedarview/Poulsbo/Oaktrail display code with shared GMA display helpers.

## Risks And Test Signals

Risks include legacy helper API drift, non-atomic display assumptions, and PLL range structs allowing invalid per-chip values if not carefully initialized. Test signals are compile coverage, per-chip mode setting, PLL search results, page flips, and CRTC save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.c

## Purpose

This file manages GMA500 GTT address-space allocation and hardware page-table programming. It enables/disables the chipset GTT, maps the GTT table, clears it to a scratch page, allocates ranges for stolen/system-backed GEM objects, inserts/removes PTEs, and reinitializes ranges after resume.

## Important APIs, Types, And Functions

Exported functions are `psb_gtt_allocate_resource()`, `psb_gtt_mask_pte()`, `psb_gtt_insert_pages()`, `psb_gtt_remove_pages()`, `psb_gtt_init()`, `psb_gtt_fini()`, and `psb_gtt_resume()`. Internal helpers are `psb_gtt_entry()`, `psb_gtt_enable()`, `psb_gtt_disable()`, `psb_gtt_clear()`, and `psb_gtt_init_ranges()`.

## Control Flow

Initialization creates the GTT mutex, enables GMCH/PGETBL, derives GTT/GATT physical and logical ranges from PCI BARs or Cedarview fallback values, ioremaps the GTT table, and fills all entries with the scratch page. Resource allocation reserves from the stolen prefix for stolen objects or the remaining range for system objects. Insertion locks the GTT mutex, writes one PTE per backing page, and reads back the last slot to flush. Removal replaces object PTEs with the scratch page. Resume re-enables the GTT, recomputes ranges, verifies page count did not change, clears entries, then disables the GTT on exit from the helper.

## State And Persistence

State lives in `drm_psb_private.gtt`, `gtt_mem`, `gtt_map`, saved `gmch_ctrl`, saved `pge_ctl`, `gtt_mutex`, and scratch page. Hardware state is the GMCH GTT-enable bit, PGETBL control register, and GTT PTE contents. Resource tree children persist as GEM allocations.

## Dependencies And Integration Points

It depends on PCI resources/config, PSB register access macros, `struct psb_gem_object` for resume resource walking elsewhere, and GEM pinning/removal paths.

## Risks And Test Signals

Risks include fallback fake GATT resources on CDV, 32-bit PFN BUG_ON for high memory, clearing GTT during resume before GEM repopulation, `psb_gtt_resume()` disabling GTT after clearing, and resource fragmentation/exhaustion. Test signals are GTT init/fini, stolen/system allocations, PTE readback, pin/unpin cycles, suspend/resume with pinned objects, CDV missing BAR fallback, and scratch-page mapping after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.h

## Purpose

This header defines the GMA500 GTT state structure and public GTT management API.

## Important APIs, Types, And Functions

`struct psb_gtt` stores `gatt_start`, `mmu_gatt_start`, `gtt_start`, `gtt_phys_start`, GTT/GATT page counts, and stolen-memory size fields. It declares init/fini/resume, resource allocation, PTE encoding, page insertion, and page removal functions.

## Control Flow

No executable flow exists. GEM and driver init/resume paths call into the declared functions to reserve GPU address space and program hardware PTEs.

## State And Persistence

The struct is embedded in `drm_psb_private` and persists for the device lifetime. Its values define address-space boundaries used by every GEM object.

## Dependencies And Integration Points

It includes DRM GEM for related types and forward-declares `drm_psb_private`. It is consumed by GEM, driver init/fini, and display pinning paths.

## Risks And Test Signals

Risks include 32-bit address fields limiting larger apertures, duplicated stolen-size fields between `psb_gtt` and `drm_psb_private`, and API coupling to Linux `struct resource`. Test signals are compile coverage, allocation boundary tests, stolen/system range separation, and resume consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.c

## Purpose

This file parses Intel VBT/BDB data for GMA500. It obtains VBT data from the ACPI OpRegion or PCI ROM, walks BIOS data blocks, and extracts panel modes, LVDS/backlight settings, child device mappings, SDVO mappings, driver feature flags, DPLL reference hints, and eDP link/power parameters.

## Important APIs, Types, And Functions

Exported functions are `psb_intel_init_bios()` and `psb_intel_destroy_bios()`. Important internal functions include `find_section()`, `parse_edp()`, `get_blocksize()`, `fill_detail_timing_data()`, `parse_backlight_data()`, `parse_lfp_panel_data()`, `parse_sdvo_panel_data()`, `parse_general_features()`, `parse_sdvo_device_mapping()`, `parse_driver_features()`, and `parse_device_mapping()`.

## Control Flow

Initialization sets `panel_type` invalid, validates and uses OpRegion VBT if present, otherwise maps PCI ROM and scans for `$VBT`. It derives the BDB pointer from the VBT offset and then parses general features, driver features, LFP panel data, SDVO panel data, SDVO mappings, generic child-device mappings, LVDS backlight data, and eDP data. Section lookup starts after the BDB header and walks ID/size-prefixed blocks. Panel timing conversion expands packed DVO timing fields into a DRM mode, fixes bogus totals shorter than sync end, and marks the mode preferred. Destroy frees allocated VBT-derived mode/backlight data.

## State And Persistence

Parsed state persists in `drm_psb_private`: `panel_type`, `lvds_dither`, `lvds_vbt`, `lfp_lvds_vbt_mode`, `sdvo_lvds_vbt_mode`, `lvds_bl`, `int_tv_support`, `int_crt_support`, `lvds_use_ssc`, `lvds_ssc_freq`, `sdvo_mappings`, `child_dev`, `child_dev_num`, `edp` fields, `lvds_enabled_in_vbt`, and `dplla_96mhz`. PCI ROM mapping is temporary and unmapped before return.

## Dependencies And Integration Points

It depends on DRM mode helpers, DP constants, PCI ROM access, opregion state from the core driver, packed layout declarations in `intel_bios.h`, and downstream LVDS/DP/HDMI output discovery.

## Risks And Test Signals

Risks include limited bounds validation while walking BDB sections, assuming child device struct size exactly matches, `parse_backlight_data()` using `bl_start + 1` without a null check after finding options, memory ownership for `child_dev` not freed in the shown destroy path, and trusting firmware timing/link data. Test signals are OpRegion VBT and ROM VBT systems, missing `$VBT`, malformed/short BDB sections, LVDS/eDP mode discovery, DPLL 96 MHz flag behavior, child-device DP/eDP detection, backlight data parsing, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.h

## Purpose

This header defines the packed Intel VBT/BDB layout structures, section IDs, child-device constants, eDP parameter encodings, scratch-register bit definitions, and parser API used by the GMA500 BIOS parser and output code.

## Important APIs, Types, And Macros

Important structures include `vbt_header`, `bdb_header`, `vbios_data`, `bdb_general_features`, `child_device_config`, `bdb_general_definitions`, `bdb_lvds_options`, `bdb_lvds_backlight`, LFP timing structures, `bdb_lvds_lfp_data`, AIM/VCH panel data, `bdb_sdvo_lvds_options`, `bdb_driver_features`, `edp_power_seq`, `edp_link_params`, and `bdb_edp`. Macros enumerate BDB section IDs, device types/config/wiring/ports, driver LVDS feature values, eDP color/rate/lane/preemphasis/vswing encodings, GR18 and SWF scratch bits, and Cedarview device classes such as HDMI, DP, and eDP. It declares `psb_intel_init_bios()` and `psb_intel_destroy_bios()`.

## Control Flow

The header has no executable flow. Its packed structures are cast directly over firmware bytes by `intel_bios.c`; output code also consults child-device constants to classify LVDS/eDP/DP ports.

## State And Persistence

No runtime state is stored in the header. It defines the ABI used to populate persistent fields in `drm_psb_private`, especially panel modes, child devices, and eDP settings. Scratch-register macros describe firmware/driver communication state in VGA/SWF registers.

## Dependencies And Integration Points

It is used by the BIOS parser, Cedarview LVDS detection, Cedarview DP eDP detection, backlight setup, SDVO code, and any code interpreting OpRegion or PCI ROM VBT data.

## Risks And Test Signals

Risks include packed layout drift across VBT versions, bitfield endian/compiler assumptions, unsafe direct casts over untrusted firmware data, duplicate old/new device-type constants, and scratch-bit semantics that depend on BIOS behavior. Test signals are compile coverage, parser tests with representative VBT versions, LVDS/eDP child-device matching, eDP bpp/lane/rate decoding, and malformed firmware fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.h -->
