# subset-b-003577 Research

Grouped source research for the subset-b-003577 files. Each section preserves the original source path for deterministic reconciliation into mirrored per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.c

Purpose: implements the low-level HIBMC DisplayPort hardware programming layer. It owns DP transmitter initialization, interrupt masking, HPD setup, stream timing programming, link enable/disable, link-status reset, color-bar test generation, and simple accessors for negotiated link rate and lane count.

Important APIs and functions: `hibmc_dp_hw_init()` allocates and wires `struct hibmc_dp_dev`, initializes AUX, SERDES, default 2-lane HBR3-like caps, resets DPTX, programs HDCP and clock enable registers. `hibmc_dp_mode_set()` triggers link training if channel equalization is not already true, disables the stream, then calls `hibmc_dp_link_cfg()`. `hibmc_dp_display_en()` toggles video and GCTL stream bits with timing sync strobes. `hibmc_dp_set_cbar()` programs color bar or solid RGB test output from `g_rgb_raw`. `hibmc_dp_check_hpd_status()` polls HPD state for up to 100 ms.

Control flow: mode setup flows from DRM encoder enable in `hibmc_drm_dp.c` into `hibmc_dp_prepare()`, then `hibmc_dp_mode_set()`. Link training is delegated to `dp_link.c`; if successful, this file writes timing generator, MSA, TU, SST, polarity, video mapping, and sync delay fields to MMIO. Stream enable is separate and occurs after timing is programmed.

State and persistence: persistent runtime state is in `dp->dp_dev`: `link.cap`, `link.status`, `hpd_status`, MMIO bases, AUX pointer, and mutex. Hardware state persists in DPTX registers until reset or driver teardown. No disk persistence exists.

Dependencies and integration points: depends on `dp_comm.h` register helpers, `dp_config.h` constants, `dp_reg.h` offsets, DRM display mode fields, Linux `readl_poll_timeout()`, and SERDES/link-training functions. It is integrated by `hibmc_dp_init()`, the HPD ISR, debugfs colorbar control, and connector mode validation.

Risks: TU/SST math assumes nonzero lane count and supported bpp/rate constants. `hibmc_dp_set_cbar()` indexes `g_rgb_raw` by pattern after validation in debugfs, but direct callers must keep pattern in range. Mode programming trusts prior mode validation for bandwidth. HPD polling is timing sensitive and may suppress connector events if hardware state changes slowly.

Test signals: useful checks include DP hotplug, DPCD read, successful link training at all supported rates and lane downgrades, visible mode set at supported resolutions, interrupt enable/disable, debugfs colorbar patterns, and suspend/resume retaining a trainable link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.h

Purpose: public HIBMC DP hardware interface used by the DRM connector/encoder layer and debugfs. It defines DP connector wrapper state, HPD status values, colorbar pattern/config structs, and exported hardware-control functions.

Important APIs/types: `struct hibmc_dp` embeds `struct drm_encoder`, `struct drm_connector`, `struct drm_dp_aux`, MMIO base, private DP device pointer, debug colorbar config, and last IRQ status. `struct hibmc_dp_cbar_cfg` carries enable, self timing, dynamic rate, and pattern. API prototypes include hardware init, mode set, display enable, colorbar setup, link reset, HPD config, interrupt control, HPD polling, and link capability accessors.

Control flow: this header is included by `hibmc_drm_drv.h` and exposes the DP block to HIBMC KMS code. The connector/encoder code calls into these functions during init, register/unregister, HPD, atomic enable/disable, and mode validation.

State and persistence: the header centralizes in-memory DP state ownership in `struct hibmc_dp`; nested `struct hibmc_dp_dev` remains opaque so low-level DP implementation files own detailed link and DPCD state.

Dependencies and integration points: includes DRM core headers and `drm_dp_helper.h` for AUX/DPCD integration. It is part of the HIBMC PCI DRM driver's private structure and provides the bridge between DRM objects and HIBMC DPTX hardware.

Risks: because `struct hibmc_dp` embeds DRM objects, lifetime must follow DRM device lifetime. The public colorbar config does not encode bounds in the type, so callers must validate the enum-like values.

Test signals: compile coverage of all HIBMC DP users, connector registration, AUX registration, HPD IRQ, colorbar debugfs writes, and mode validation exercise this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_link.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_link.c

Purpose: implements DisplayPort link training for HIBMC, including DPCD capability discovery, local transmitter/SERDES setup, clock recovery, channel equalization, and fallback to lower link rates or fewer lanes.

Important APIs/functions: `hibmc_dp_link_training()` is the exported entry point. Internal helpers map DP link rates to SERDES codes, program lane count and enhanced framing, set training patterns, initialize voltage/pre-emphasis, read and interpret lane status, apply sink adjust requests, downgrade rate/lane count, and update caps from DPCD.

Control flow: training starts by reading DPCD caps, clamping link rate to at most `DP_LINK_BW_8_1` and lanes to `HIBMC_DP_LANE_NUM_MAX`, programming SERDES rate, then looping. Each loop performs CR preparation, clock recovery with up to 80 tries and five same-voltage retries, then channel equalization with five retries. Failed CR reduces rate first, then lane count; failed EQ prefers lane reduction after CR succeeded, then rate reduction. On hard error, the training pattern is disabled before returning.

State and persistence: updates `dp->link.cap.link_rate`, `dp->link.cap.lanes`, `dp->link.train_set`, and `dp->link.status.clock_recovered/channel_equalized`. These are in-memory link state and feed later mode validation and TU calculation. The sink state is mutated through AUX writes to `DP_LINK_BW_SET`, `DP_DOWNSPREAD_CTRL`, `DP_TRAINING_PATTERN_SET`, and lane training set registers.

Dependencies and integration points: depends on DRM DP helper routines for DPCD IO, training delays, lane status parsing, and adjust requests. It calls HIBMC SERDES programming functions and DP register-field helpers. It is invoked from `hibmc_dp_mode_set()` when a stream needs an equalized link.

Risks: `drm_dp_read_dpcd_caps()` errors are logged but not returned before caps update, so stale or zero DPCD contents can influence fallback behavior. Training can spin through multiple fallback attempts and is sensitive to AUX reliability. Training pattern disable errors are ignored in some paths. Lane/rate downgrade reaches `-EIO` at the minimum capability.

Test signals: verify DPCD capability parsing, CR and EQ success/failure paths, sink adjust-request propagation to SERDES, fallback from HBR3 to lower rates and from 2 lanes to 1 lane, and cleanup of training pattern on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_reg.h

Purpose: defines the HIBMC DP transmitter and SERDES MMIO register map, bit fields, and SERDES tuning constants used by the DP hardware, AUX, training, colorbar, interrupt, and timing paths.

Important APIs/types: register offsets include AUX command/data/status, HPD status, PHYIF control, video timing/MSA/packet/control, colorbar, timing generator, HDCP config, reset/clock/gctl, interrupt status/clear/enable, timing sync, and SERDES lane/rate/status registers. Field macros use `BIT()` and `GENMASK()` so callers can use `FIELD_PREP/FIELD_GET` helpers.

Control flow: the header has no executable control flow, but its constants drive sequencing in `dp_hw.c`, `dp_link.c`, `dp_serdes.c`, and the HIBMC PCI IRQ handler. The SERDES constants form the TX de-emphasis table selected from DP training voltage swing and pre-emphasis requests.

State and persistence: hardware register writes based on these definitions persist in device MMIO until reset or power transition. No in-memory state is defined here.

Dependencies and integration points: used by HIBMC DP source files and by `hibmc_drm_drv.c` to probe DP block presence and read/clear DP interrupt status. It assumes Linux bitfield macro availability through including C files.

Risks: register maps are hardware-contract sensitive. A wrong offset or field mask can silently break AUX, HPD, link training, or timing. The SERDES tuning table is hardcoded to hardware-specific values and requires hardware validation for new silicon.

Test signals: low-level MMIO trace comparison against hardware documentation, successful AUX transactions, HPD interrupts, link training status, colorbar output, and mode timing correctness exercise these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_serdes.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_serdes.c

Purpose: programs the DP SERDES physical layer for HIBMC link training and link-rate changes.

Important APIs/functions: `hibmc_dp_serdes_init()` sets the SERDES base, initializes both lane TX de-emphasis registers to level 0/pre-emphasis 0, and switches to the highest SERDES rate. `hibmc_dp_serdes_rate_switch()` writes the same rate to both lane rate registers and waits for lane status. `hibmc_dp_serdes_set_tx_cfg()` translates DP training-set voltage/pre-emphasis bits into per-lane de-emphasis values and writes PMA lane registers.

Control flow: link training calls rate switch before training loops and TX config whenever the sink requests new training settings. Each programming sequence waits 300 to 500 us, then requires `HIBMC_DP_LANE_STATUS_OFFSET` to equal `DP_SERDES_DONE`.

State and persistence: `dp->serdes_base` is derived from the DP base. Hardware lane PMA and rate registers retain their programmed values until subsequent writes or reset. There is no software cache other than the caller's `train_set`.

Dependencies and integration points: depends on DP register macros, DP training bit masks, `FIELD_GET/PREP`, and DRM debug logging. It is tightly coupled to `dp_link.c`.

Risks: the static `serdes_tx_cfg[4][4]` table is sparse and invalid voltage/pre-emphasis combinations return `-EINVAL`, which can stop training. The function loops over `HIBMC_DP_LANE_NUM_MAX` instead of active lane count, so both lanes are programmed even when training falls back to one lane. SERDES status equality check is strict.

Test signals: training at each voltage/pre-emphasis combination, one-lane fallback, rate changes across 1.62/2.7/5.4/8.1 classes, and injected lane status failures validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_de.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_de.c

Purpose: implements the HIBMC display engine CRTC and primary plane. It validates atomic plane state, programs VRAM scanout registers, manages display power and vblank, configures CRT timing/PLL registers, and initializes plane/CRTC DRM objects.

Important APIs/functions: `hibmc_de_init()` creates the primary plane and CRTC. Plane helpers check no scaling, nonnegative position, visible bounds, and 128-byte stride alignment, then program framebuffer address, width, pitch, and pixel format. CRTC helpers manage DPMS, atomic enable/disable, begin/flush, mode validation, timing programming, vblank IRQ enable, and gamma LUT upload.

Control flow: during KMS init, this file registers the universal primary plane and CRTC. Atomic commits call plane check/update and CRTC helper callbacks. Enabling powers mode 0 and display/localmem gates, turns vblank on, and sets DPMS on. Mode set writes PLL values from a fixed resolution table and programs horizontal/vertical timing, sync, auto-centering, clock select, and plane enable bits.

State and persistence: hardware state is MMIO registers in `priv->mmio`; persistent software state is the DRM CRTC/plane state and gamma store. Supported PLL values are fixed in `hibmc_pll_table`.

Dependencies and integration points: depends on DRM atomic helpers, GEM VRAM helpers, vblank core, `hibmc_set_power_mode()`, `hibmc_set_current_gate()`, and `hibmc_drm_regs.h`. Outputs feed both VGA and optional DP encoders through the same CRTC.

Risks: mode validation only accepts 59-61 Hz and tabled resolutions. Unsupported scaling and stride alignment failures are user-visible. PLL programming relies on magic values. Plane address assumes VRAM object was pinned by helper prepare paths. Gamma setter ignores supplied arrays and reloads `crtc->gamma_store`.

Test signals: atomic modesets for every tabled resolution, stride-alignment failures, vblank IRQ delivery, DPMS transitions, framebuffer format coverage, gamma update, suspend/resume, and clone behavior with VGA/DP encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_de.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_debugfs.c

Purpose: exposes a connector debugfs control for HIBMC DP colorbar configuration.

Important APIs/functions: `hibmc_debugfs_init()` creates `colorbar-cfg`. `hibmc_control_write()` parses four fields into `priv->dp.cfg` and applies `hibmc_dp_set_cbar()`. `hibmc_dp_dbgfs_show()` returns the current config. `hibmc_open()` wires the seq-file show path.

Control flow: connector debugfs registration calls `hibmc_debugfs_init()`. Users write a short string with enable, self timing, dynamic rate, and pattern. The write path copies user data, validates parse count and basic ranges, enters the DRM device critical section, programs colorbar registers, and returns byte count.

State and persistence: colorbar config is stored in `priv->dp.cfg` and reflected in hardware by `hibmc_dp_set_cbar()`. It is runtime-only and reset when the driver/device resets.

Dependencies and integration points: depends on debugfs, seq_file, DRM device enter/exit, and DP colorbar hardware API. It is registered by the DP connector funcs in `hibmc_drm_dp.c`.

Risks: comments describe enable values inconsistently with code (`cfg->enable` is passed directly). `debugfs_create_file()` mode is write-only `0200` even though read handlers exist, so read access may be unavailable to users. Pattern validation permits 0-9 and prevents direct table overflow from this path.

Test signals: debugfs file creation under DP connector, valid and invalid writes, colorbar visible output, read permission behavior, device unplug during write, and race behavior with mode set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_dp.c

Purpose: provides the DRM connector and encoder integration for the HIBMC DP block, including EDID/DPCD discovery, connector status, mode bandwidth validation, AUX registration, HPD ISR handling, and atomic encoder enable/disable.

Important APIs/functions: `hibmc_dp_init()` initializes hardware, encoder, connector, helpers, and HPD polling. `hibmc_dp_detect()` reads DPCD, descriptor, downstream info, branch sink count, and HPD status. `hibmc_dp_mode_valid()` compares mode clock times bpp to current link bandwidth. `hibmc_dp_hpd_isr()` handles threaded HPD plug/unplug events and calls connector hotplug notification.

Control flow: HIBMC KMS init calls `hibmc_dp_init()` when the SERDES control register suggests DP hardware exists. Late connector registration enables DP interrupts and registers AUX; early unregister disables them. Atomic encoder enable disables the stream, mode-sets/trains the DP link, then enables the stream.

State and persistence: uses `struct hibmc_dp` embedded in driver private data. `irq_status` is latched by the primary IRQ handler and interpreted by the threaded handler. DPCD, branch flag, downstream ports, descriptor, and HPD status live under `dp_dev`.

Dependencies and integration points: depends on DRM EDID, DP AUX helpers, atomic helpers, `dp_hw.h`, `dp_comm.h`, and `dp_config.h`. It is connected to MSI vector 1 by `hibmc_drm_drv.c`.

Risks: `irq_status` is used as a latch without explicit locking, so IRQ/thread ordering matters. A nonzero IRQ status with HPD status not in can short-circuit detection. Mode validation uses current software link caps, which may not yet reflect post-training downgrade. Branch-device sink count handling depends on downstream HPD bit.

Test signals: AUX registration, EDID mode enumeration, branch and non-branch sink detect, HPD plug/unplug interrupt flow, link reset on unplug, mode rejection above bandwidth, and atomic enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.c

Purpose: top-level PCI DRM driver for HIBMC. It owns PCI probe/remove/shutdown, DRM driver registration, VRAM helper setup, KMS initialization, MMIO mapping, hardware reset/power setup, MSI interrupt registration, and suspend/resume entry points.

Important APIs/functions: `hibmc_pci_probe()` allocates the DRM device, enables PCI, loads hardware/KMS, registers DRM, and starts client setup. `hibmc_load()` maps hardware, initializes VRAM, KMS, vblank, MSI, and mode config state. `hibmc_kms_init()` configures mode limits, initializes DE, optional DP, and VGA VDAC. `hibmc_msi_init()` requests vblank IRQ and optional threaded DP HPD IRQ. `hibmc_set_power_mode()` and `hibmc_set_current_gate()` are shared power helpers.

Control flow: module PCI registration dispatches probe. Probe removes conflicting apertures, enables PCI master, calls `hibmc_load()`, then `drm_dev_register()`. Error paths call `hibmc_unload()`. Interrupt vector 0 handles vblank directly; vector 1, when allocated, reads DP interrupt status, clears it, and wakes the threaded HPD handler.

State and persistence: `struct hibmc_drm_private` embeds DRM device, plane, CRTC, VGA, DP, and MMIO pointer. Hardware power/gate/MMIO state persists until shutdown or reset. Driver state is runtime-only.

Dependencies and integration points: depends on PCI, aperture, DRM atomic/GEM/VRAM/fbdev helpers, vblank core, HIBMC DE/VDAC/DP modules, and DP register definitions for probing and interrupt status.

Risks: DP is initialized conditionally by reading `HIBMC_DP_HOST_SERDES_CTRL`; false positives/negatives affect connector exposure. If only one MSI vector is allocated, DP HPD interrupt is not requested. `dev->mode_config.funcs` is assigned through a cast. Power-gate sequences are hardware-sensitive.

Test signals: PCI bind/unbind, aperture takeover, VRAM mapping, KMS object creation, vblank IRQ, optional DP IRQ, suspend/resume, fbdev client setup, and failure injection in each init stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.h

Purpose: shared private header for the HIBMC DRM driver. It defines the driver-private object graph, VGA DDC state, conversion helpers, init hooks, and power/IRQ/debugfs declarations.

Important APIs/types: `struct hibmc_vdac` embeds the VGA encoder, connector, I2C adapter, and bit-bang data. `struct hibmc_drm_private` embeds MMIO pointer, DRM device, primary plane, CRTC, VDAC, and DP. Container helpers convert connectors/devices to private structs. Function declarations connect DE, VDAC, DDC, DP, debugfs, power mode/gate, and HPD ISR modules.

Control flow: included by all HIBMC C files to share private layout and cross-module APIs. Probe allocates `struct hibmc_drm_private` around `struct drm_device`; downstream modules fill the embedded subobjects during KMS init.

State and persistence: defines the in-memory runtime state for the whole HIBMC driver. It does not store persistent configuration beyond what each embedded object holds.

Dependencies and integration points: depends on Linux GPIO/I2C bit-bang headers, DRM framebuffer types, and DP public hardware header. Integrates PCI driver, display engine, VDAC, I2C, DP, and debugfs files.

Risks: embedded DRM objects require stable lifetime and cleanup order. Adding connectors or CRTCs requires updating clone masks and mode config assumptions. Container helpers assume the passed objects are exactly the embedded HIBMC instances.

Test signals: compile coverage, KMS init/cleanup, connector-to-private conversions in EDID/HPD paths, and module unload validate this shared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_i2c.c

Purpose: implements a GPIO-backed bit-banged I2C adapter for HIBMC VGA DDC/EDID.

Important APIs/functions: `hibmc_ddc_create()` initializes `struct i2c_adapter` and `struct i2c_algo_bit_data`, sets 20 us delay and 2000 us timeout, and registers the bus. `hibmc_ddc_del()` removes it. Internal `setsda/setscl/getsda/getscl` callbacks manipulate MMIO GPIO data and direction bits.

Control flow: VDAC init creates the DDC adapter before registering the VGA connector. EDID reads in `hibmc_drm_vdac.c` use the adapter. Destroy paths call `hibmc_ddc_del()`.

State and persistence: the I2C adapter state is embedded in `struct hibmc_vdac`. SDA/SCL electrical state is represented by GPIO data and direction registers. There is no persistent state.

Dependencies and integration points: depends on I2C bit-bang core, PCI/DRM device parent pointers, and HIBMC MMIO from `struct hibmc_drm_private`.

Risks: GPIO open-drain semantics are encoded through direction changes: high means input/released, low means drive low. Incorrect direction handling can break EDID or hold the bus. No explicit locking is done around GPIO register updates beyond the I2C algorithm's sequencing.

Test signals: VGA EDID read, DDC detect, connector hotplug polling, adapter registration/removal, and bus recovery after NACK/timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_regs.h

Purpose: defines the HIBMC non-DP MMIO register map for power, gates, PLLs, CRT scanout/timing, panel/VGA controls, vblank interrupts, palette, and field packing.

Important APIs/types: macros cover power mode and current-gate registers, PLL field builders and fixed PLL magic values, display control/DPMS/format/timing bits, framebuffer address/width/pitch, horizontal and vertical timing registers, auto-centering registers, panel control, vblank raw interrupt/enable, and `HIBMC_FIELD()`.

Control flow: no executable flow, but the definitions are used throughout `hibmc_drm_drv.c`, `hibmc_drm_de.c`, and `hibmc_drm_vdac.c` to program device state.

State and persistence: values written through these definitions persist in device registers until changed, reset, or power-gated. No software storage is declared.

Dependencies and integration points: used by the HIBMC display engine and top-level driver. It assumes register values and masks match HIBMC hardware documentation.

Risks: magic PLL constants and field masks are high-risk hardware contract points. `HIBMC_FIELD()` assumes field macros have matching `_MASK` macros and can silently mask bad values. Resolution support is constrained by tabled PLL values in `hibmc_drm_de.c`.

Test signals: mode timing correctness, supported resolution PLL programming, vblank IRQ enable/ack, framebuffer pitch/address display, power-gate transitions, and palette/gamma output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_vdac.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_vdac.c

Purpose: implements the HIBMC VGA-style DAC encoder and connector, including DDC-backed EDID mode enumeration and panel output enabling.

Important APIs/functions: `hibmc_vdac_init()` creates the DDC adapter, DAC encoder, VGA connector, helper functions, and encoder attachment. `hibmc_connector_get_modes()` reads EDID through DDC, falls back to no-EDID modes, and prefers 1024x768. `hibmc_encoder_mode_set()` sets panel/display control enable bits. `hibmc_connector_destroy()` unregisters the DDC adapter and cleans up the connector.

Control flow: called by HIBMC KMS init after DE and optional DP setup. Connector probing uses DDC detect helper and mode enumeration. Encoder mode set programs display control on modeset.

State and persistence: VDAC state is embedded in `priv->vdac`, with I2C adapter, connector, and encoder. Hardware output enable bits persist in `HIBMC_DISPLAY_CONTROL_HISILE`.

Dependencies and integration points: depends on DRM connector/encoder helpers, EDID helpers, HIBMC DDC implementation, and HIBMC register definitions. It shares the single HIBMC CRTC with optional DP output.

Risks: fallback mode list relies on global mode-config max dimensions. Error cleanup calls `hibmc_ddc_del()` for encoder or connector init failures. `hibmc_encoder_mode_set()` turns on panel-related bits but has no corresponding disable callback in this file.

Test signals: VGA connector detection via DDC, EDID and no-EDID fallback modes, encoder attach, mode set enabling output bits, connector destroy cleanup, and clone behavior with DP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_vdac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Kconfig

Purpose: declares the `DRM_HISI_KIRIN` build option for Hisilicon Kirin/Hi6220 DRM support.

Important APIs/types: the config is a tristate requiring DRM, OF, and ARM64 or compile-test. It selects DRM client selection, KMS helper, GEM DMA helper, and MIPI DSI support.

Control flow: Kconfig selection controls whether `kirin-drm` and `dw_drm_dsi` are built by the directory Makefile.

State and persistence: no runtime state. It influences kernel build configuration.

Dependencies and integration points: integrates Kirin DRM with the DRM core, OF graph/component model, DMA GEM backing, and MIPI DSI host support.

Risks: missing selected dependencies would break link or runtime probe. The help text targets Hi6220 and may not cover broader Kirin variants.

Test signals: allmodconfig/allyesconfig build, module build as `M`, and OF-enabled platform probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Makefile

Purpose: builds the Kirin DRM objects for the selected Kconfig option.

Important APIs/types: `kirin-drm-y` contains `kirin_drm_drv.o` and `kirin_drm_ade.o`; `obj-$(CONFIG_DRM_HISI_KIRIN)` links `kirin-drm.o` plus `dw_drm_dsi.o`.

Control flow: when `DRM_HISI_KIRIN` is enabled, the master DRM/ADE code and DSI host/encoder code are compiled into the module/built-in target.

State and persistence: no runtime state; build graph only.

Dependencies and integration points: tied to the Kconfig symbol and Linux kbuild conventions. It keeps the DSI driver as a separate object alongside the aggregate Kirin DRM object.

Risks: adding ADE or DSI dependencies requires updating this list. Incorrect object order or missing object would break component binding at runtime.

Test signals: kernel build with `CONFIG_DRM_HISI_KIRIN=y/m`, module contents inspection, and symbol presence for `kirin_drm_platform_driver` and `dsi_driver`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_drm_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_drm_dsi.c

Purpose: implements a DesignWare MIPI DSI host/encoder for HiSilicon Kirin/Hi6220 platforms, including D-PHY PLL/timing calculation, DSI video-mode programming, MIPI DSI host attach/detach, component binding, and bridge attachment.

Important APIs/functions: `dsi_probe()` allocates driver data, maps registers, gets `pclk`, and registers a MIPI DSI host. `dsi_host_attach()` records lanes, format, and mode flags and adds the component. `dsi_bind()` initializes the DRM DSI encoder and attaches the downstream bridge. Encoder helpers validate mode/PHY rate, store adjusted mode, and enable/disable DSI core and PHY. `dsi_calc_phy_rate()` and `dsi_get_phy_params()` compute PLL and timing parameters.

Control flow: platform probe registers the host. When a DSI peripheral attaches, the driver becomes a DRM component. Master bind calls `dsi_bind()`, which creates an encoder and attaches bridge endpoint port 1. Atomic modeset calls mode validation through possible CRTC mode fixup, then mode set stores adjusted mode. Enable prepares the pixel clock and calls `dsi_mipi_init()` to reset core, program PHY, timing, video mode, and power up.

State and persistence: `struct dw_dsi` stores encoder, host, current mode, DSI format/lanes/flags, PHY parameters, and enable flag. Hardware state is DSI/D-PHY registers. No disk persistence.

Dependencies and integration points: depends on Linux component framework, DRM encoder/bridge/OF helpers, MIPI DSI host APIs, platform resources, clocks, and `dw_dsi_reg.h`. It expects a downstream panel/bridge in OF graph.

Risks: only RGB888 color coding is effectively supported. PHY mode validation uses a strict denominator relationship between adjusted pixel clock and lane byte clock. PLL calculation increments requested rate until valid and must stay within supported ranges. DSI host component add/del is tied to peripheral attach/detach, so missing peripheral prevents component bind.

Test signals: OF probe, DSI peripheral attach/detach, bridge discovery, mode validation at supported clocks, scope-visible D-PHY clock/data lanes, panel enable/disable, and suspend/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_drm_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_dsi_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_dsi_reg.h

Purpose: defines DesignWare DSI host and D-PHY register offsets, bit values, mode enums, and a register update helper for Kirin DSI.

Important APIs/types: register macros include core power, clock manager, PHY reset/test/status, PHY timing test codes, DPI color/polarity, video horizontal/vertical timing, packet size, video mode, BTA/LP timers, LP clock control, and mode config. Enums define DPI color coding, video mode type, and command/video work mode. `dw_update_bits()` performs read-modify-write bitfield updates.

Control flow: no independent flow. `dw_drm_dsi.c` consumes these definitions while programming PHY, timing, video mode, and core power state.

State and persistence: DSI hardware state is the register values written via these offsets. The header carries no software storage.

Dependencies and integration points: includes Linux IO and assumes bit macros. It is specific to the DesignWare DSI version used by the Kirin driver.

Risks: `MASK(x)` uses `BIT(x) - 1`, so inputs must remain in valid bit-width ranges. Wrong register codes or offsets can break PHY bring-up. The helper shifts `mask` by `bit_start`, so callers must pass an unshifted mask.

Test signals: DSI controller register trace during panel enable, PHY lock/status, video timing output, and compile coverage of all macros used by `dw_drm_dsi.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_dsi_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_ade_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_ade_reg.h

Purpose: defines the Kirin ADE display controller register map, bitfields, hardware enums, and update helper used by the ADE CRTC/plane implementation.

Important APIs/types: macros cover ADE control/reload/reset, RDMA channel registers, overlay routing/control/output size, color transform, clip, LDI timing/control/interrupts, DSI pixel clock gate, and media NoC QoS registers. Enums describe frame-effect timing, framebuffer formats, channels, scaler/ctran/overlay IDs, alpha modes, LDI output/work/input modes, DSI pixel clock gate values, and QoS modes.

Control flow: no runtime flow. `kirin_drm_ade.c` uses these definitions for power-up initialization, LDI mode programming, RDMA/clip/compositor setup, vblank IRQ handling, and QoS configuration.

State and persistence: hardware state is stored in ADE registers. Reload-disable bits govern when changes take effect in hardware.

Dependencies and integration points: relies on Linux `readl/writel`, `BIT_ULL`, and bit macros. It is tightly coupled to ADE channel count and the primary-plane-only setup.

Risks: `ADE_CH_NUM` is currently one, so many helper macros imply broader hardware but driver data exposes only primary plane. `MASK(32)` uses 64-bit math to avoid overflow, but callers must still use sensible widths. Offsets and reload bits are critical for frame-synchronized updates.

Test signals: ADE register dumps, vblank interrupt behavior, primary plane RDMA scanout, clipping, overlay routing, LDI timing, and QoS register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_ade_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_ade.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_ade.c

Purpose: implements the Kirin Hi6220 ADE CRTC and plane backend. It allocates ADE hardware context, controls clocks/reset/power, handles vblank, programs LDI timing, RDMA, clipping, compositor routing, and exposes ADE-specific `kirin_drm_data` to the master driver.

Important APIs/functions: `ade_hw_ctx_alloc()` maps registers, gets reset, NoC regmap, IRQ, and clocks, and requests the vblank IRQ. CRTC helpers include mode fixup, mode set, atomic begin/flush/enable/disable, and vblank enable/disable. Plane helpers validate no scaling and bounds, update RDMA/clip/compositor, and disable channels. `ade_driver_data` exports format lists, DRM funcs, config limits, and context callbacks.

Control flow: master private init calls `alloc_hw_ctx()`, creates planes and CRTC using data from `ade_driver_data`. Atomic mode setting powers up if needed, rounds and sets pixel clock, writes LDI timing, enables ADE/LDI and overlay, and arms vblank events. Plane updates write DMA address from GEM DMA object, source clipping, and overlay routing. Disable powers down core clock/reset/media NoC.

State and persistence: `struct ade_hw_ctx` stores MMIO base, clocks, reset, NoC regmap, power flag, IRQ, and CRTC pointer. `struct kirin_crtc` stores enable flag. Hardware registers persist while powered; context is devm-managed.

Dependencies and integration points: depends on DRM atomic/GEM DMA helpers, clk/reset/regmap/syscon/platform APIs, vblank core, and `kirin_ade_reg.h`. Integrates with Kirin master through `ade_driver_data` and with DSI through LDI/DSI pixel gate.

Risks: only one channel/primary plane is exposed despite broader ADE hardware. `ade_power_up()` does not unwind earlier clock/reset enables if a later step fails. `ade_crtc_enable_vblank()` ignores a failed power-up cast to void. No scaling is supported. Debug register dump path is compiled on by `ADE_DEBUG 1`.

Test signals: platform resource acquisition, IRQ delivery, pixel clock rounding, primary plane scanout, no-scaling rejection, vblank event delivery, enable/disable power transitions, DMA address correctness, and DSI panel output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_ade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.c

Purpose: master DRM platform driver for Kirin display. It coordinates OF graph/component binding, allocates the DRM device, initializes mode config, private CRTC/plane hardware data, vblank, polling, DRM registration, and cleanup.

Important APIs/functions: `kirin_drm_platform_probe()` finds the remote graph node and registers a component master. `kirin_drm_bind()` allocates and registers the DRM device. `kirin_drm_kms_init()` initializes mode config, private display controller objects, binds subdrivers, initializes vblank, resets state, and starts polling. `kirin_drm_private_init()` allocates `kirin_drm_private`, hardware context, planes, and CRTC.

Control flow: platform probe creates component match for the downstream device. Component bind gets `kirin_drm_data` from OF match, allocates DRM, initializes KMS, registers DRM, and starts clients. Unbind unregisters DRM, shuts down atomics, cleans private data, unbinds components, and drops the device.

State and persistence: `struct kirin_drm_private` contains one CRTC, up to two planes, and `hw_ctx`. DRM state lives in mode config and object state. No persistent storage.

Dependencies and integration points: depends on component framework, OF graph, DRM OF helpers, GEM DMA, vblank, and ADE driver data. DSI is expected as a component through graph matching.

Risks: `dev->mode_config.max_height` is assigned `driver_data->config_max_width` instead of `config_max_height` in this tree. `kirin_drm_crtc_init()` calls `of_node_put(port)` before assigning `crtc->port = port`, which is suspicious for node lifetime. Cleanup assumes `dev_private` is set and driver data cleanup is safe.

Test signals: OF graph probe, component bind/unbind order, DRM registration, mode config dimensions, vblank init, shutdown path, and DSI bridge attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.h

Purpose: shared Kirin DRM private interface between the master driver and ADE backend.

Important APIs/types: container macros convert DRM CRTC/plane to Kirin wrappers. `struct kirin_format` maps DRM fourcc to hardware formats. `struct kirin_crtc` and `struct kirin_plane` extend DRM objects with hardware context and channel/enable state. `struct kirin_drm_data` packages per-display-controller callbacks, formats, limits, DRM driver, function tables, plane counts, and context lifecycle. `ade_driver_data` is declared externally.

Control flow: the master driver consumes `kirin_drm_data` from OF match data to allocate objects and call ADE context setup, while ADE fills the exported data.

State and persistence: defines runtime object wrappers and immutable driver-data contracts. No persistent storage.

Dependencies and integration points: integrates Kirin master, ADE backend, DRM atomic helpers, and platform resource allocation through function pointers.

Risks: function pointer table correctness controls all object initialization. `KIRIN_MAX_PLANE` in the C file must remain compatible with `num_planes`. Container macros assume exact embedding.

Test signals: compile/link of ADE data, platform bind using OF match data, object initialization for all `num_planes`, and cleanup callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Kconfig

Purpose: declares `DRM_HYPERV`, the Hyper-V synthetic video DRM KMS driver option.

Important APIs/types: the tristate depends on DRM, PCI, and Hyper-V VMBus. It selects DRM client selection, KMS helper, and GEM shmem helper.

Control flow: when selected, the Hyper-V Makefile builds the driver objects into `hyperv_drm`.

State and persistence: build-time configuration only.

Dependencies and integration points: integrates with Hyper-V VMBus and a PCI stub for generation 1 VM support, plus DRM shmem/fbdev helpers.

Risks: help text notes `CONFIG_FB_HYPERV` should be unselected so the DRM driver is default. Dependency mismatch can leave the synthetic device without the intended KMS driver.

Test signals: build with `CONFIG_DRM_HYPERV=y/m`, boot in Hyper-V VM, and conflict behavior with Hyper-V framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Makefile

Purpose: defines the Hyper-V DRM module object composition.

Important APIs/types: `hyperv_drm-y` includes driver, modeset, and protocol objects. `obj-$(CONFIG_DRM_HYPERV)` emits `hyperv_drm.o`.

Control flow: kbuild links `hyperv_drm_drv.o`, `hyperv_drm_modeset.o`, and `hyperv_drm_proto.o` when the Kconfig symbol is enabled.

State and persistence: no runtime state; build graph only.

Dependencies and integration points: mirrors the three-file architecture: bus/DRM registration, KMS plane/CRTC/connector setup, and VMBus protocol.

Risks: missing any object breaks probe, scanout, or host protocol.

Test signals: module build, exported internal symbol resolution, and load in a Hyper-V guest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm.h

Purpose: shared Hyper-V DRM private header. It defines device-private state and prototypes for modeset and VMBus protocol operations.

Important APIs/types: `struct hyperv_drm_device` embeds DRM device, plane, CRTC, encoder, connector, mode limits, preferred mode, depth, VRAM resource/mapping/base/size, VMBus wait completion, negotiated protocol version, MMIO size, dirt flag, fixed init/receive buffers, and `hv_device`. `to_hv()` converts DRM device to private state. Protocol function prototypes cover VRAM location, situation update, pointer hide, dirty rect, and VSP connect.

Control flow: `hyperv_drm_drv.c` allocates this structure and initializes protocol/VRAM/modeset; modeset and protocol files share it through `hv_get_drvdata()` and `to_hv()`.

State and persistence: contains all runtime state for the synthetic video device. No disk persistence.

Dependencies and integration points: requires DRM object types through including C files and Hyper-V types for `struct hv_device`. Integrates VMBus protocol state with DRM KMS objects.

Risks: fixed 16 KiB buffers must cover all in-band messages. Completion and shared init buffer require single outstanding synchronous protocol transaction. `dirt_needed` gates dirty-rect notifications.

Test signals: VSP negotiation, resolution query, VRAM map, atomic updates, suspend/resume, dirty notification, and remove/unplug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_drv.c

Purpose: bus-facing top-level Hyper-V synthetic video DRM driver. It registers a PCI stub and VMBus driver, negotiates with the host, allocates/maps VRAM, initializes modeset, registers DRM, and handles remove, shutdown, suspend, and resume.

Important APIs/functions: `hyperv_vmbus_probe()` allocates `hyperv_drm_device`, connects VSP, removes conflicting apertures, sets up VRAM, sends VRAM location, initializes KMS, registers DRM, and starts clients. `hyperv_setup_vram()` allocates Hyper-V MMIO and maps it cacheable. Suspend/resume close/reopen VMBus and refresh VRAM location.

Control flow: module init refuses firmware-only DRM mode, registers the PCI stub, then the VMBus driver. Probe negotiates protocol before allocating VRAM because host-reported MMIO size is needed. Remove unplugs DRM, shuts down atomics, closes VMBus, clears drvdata, unmaps VRAM, and frees MMIO.

State and persistence: driver state is in `hyperv_drm_device`; VRAM is guest physical MMIO allocated from VMBus and mapped cacheable. Protocol state is runtime-only and renegotiated on resume.

Dependencies and integration points: depends on Hyper-V VMBus, PCI IDs for gen1 stub, aperture helpers, DRM shmem/fbdev helpers, and Hyper-V protocol/modeset files.

Risks: `hyperv_pci_probe()` is a no-op by design but still claims PCI ID as a stub. Failure to update VRAM location is nonfatal at probe but fatal on resume. Resource cleanup must match allocation state carefully. Cacheable VRAM mapping is required for ARM64 VM display behavior.

Test signals: boot in Hyper-V gen1/gen2 VMs, VMBus negotiation, DRM device registration, framebuffer console, suspend/resume, remove/unplug, and MMIO allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_modeset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_modeset.c

Purpose: implements KMS objects for Hyper-V synthetic video: virtual connector, primary shadow plane, CRTC, encoder, mode config, VRAM blitting, dirty rectangle notifications, and panic scanout support.

Important APIs/functions: `hyperv_mode_config_init()` initializes DRM mode config and one pipe. Plane update iterates damage clips, copies shadow framebuffer data into `hv->vram`, and calls `hyperv_update_dirt()`. CRTC enable hides the host pointer and sends a situation update. Connector mode enumeration creates no-EDID modes up to host-provided maximum and sets preferred mode.

Control flow: top-level probe calls mode config init after VRAM and host resolution setup. Atomic plane check validates no scaling and framebuffer size fits VRAM. Atomic update blits damaged rectangles. CRTC enable sends active mode details and enables vblank. Dirty notifications tell the host which rectangles changed.

State and persistence: KMS state lives in DRM atomic state. The scanout backing is Hyper-V VRAM at `hv->vram`; guest shadow buffers come from GEM shmem. Host display state is updated by VMBus messages.

Dependencies and integration points: depends on DRM shmem shadow plane helpers, format helpers, damage helpers, vblank timer functions, panic helpers, and Hyper-V protocol calls.

Risks: only `DRM_FORMAT_XRGB8888` and linear modifiers are exposed. Plane check uses full framebuffer height for size; mode validity uses pitch derived from width and depth if no fb. `hyperv_plane_atomic_update()` ignores return values from blit and dirty update. Dirty notifications are skipped if host feature flag says not needed.

Test signals: mode enumeration with host preferred resolution, framebuffer size rejection, damage-only updates, full-screen updates, host visible refresh, panic flush, vblank timer behavior, and suspend/resume modeset restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_modeset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_proto.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_proto.c

Purpose: implements the Hyper-V synthetic video VMBus protocol: version negotiation, VRAM location, display situation updates, host cursor hiding, dirty rectangle messages, supported resolution query, feature-change handling, receive callback, and VSP connection.

Important APIs/functions: `hyperv_connect_vsp()` opens the VMBus channel, negotiates protocol based on VMBus version, gets supported resolutions for Win10 protocol, sets screen depth and MMIO size. `hyperv_update_vram_location()`, `hyperv_update_situation()`, `hyperv_hide_hw_ptr()`, and `hyperv_update_dirt()` send host messages. `hyperv_receive()` drains incoming packets and `hyperv_receive_sub()` completes synchronous waits or handles feature changes.

Control flow: probe/resume call connect; connect opens channel and negotiates the best accepted version. Synchronous requests reuse `hv->init_buf`, send a packet, then wait up to 10 seconds for receive callback to copy the response and complete. Runtime display updates use stack messages without waiting for ACK, except VRAM location/version/resolution flows.

State and persistence: protocol version, screen max/preferred sizes, `dirt_needed`, MMIO megabytes, wait completion, and buffers are stored in `hyperv_drm_device`. Host-side state is updated via VMBus messages.

Dependencies and integration points: depends on Hyper-V channel APIs, DRM logging, and modeset calls. Dirty updates are triggered by plane damage; cursor hiding is triggered by CRTC enable and feature changes.

Risks: one shared completion/init buffer assumes no concurrent synchronous protocol calls. `hyperv_sendpacket()` return is ignored by some callers. Feature-change handling hides the pointer only when dirt is needed, matching this implementation's policy. Version fallback differs by host VMBus protocol. Resolution query failure falls back only partially; Win8 defaults set max but not preferred dimensions explicitly.

Test signals: negotiated version logs, timeout handling, host resolution list parsing, dirty feature toggling, cursor disappearance after VMConnect reopen, VRAM location ACK matching, and packet receive under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Kconfig

Purpose: declares i915 DRM driver configuration and related optional features for Intel integrated graphics.

Important APIs/types: `DRM_I915` is a tristate depending on DRM, X86, PCI, and not PREEMPT_RT, selecting many display, memory, ACPI, sync, TTM, and helper dependencies. Additional symbols include force-probe string, error capture/compression, userptr, GVT KVMGT, PXP, DP tunnel support, and hidden `DRM_I915_GVT`.

Control flow: selected symbols control build inclusion in `drivers/gpu/drm/i915/Makefile`, optional debug/profile submenus, and feature-specific source lists.

State and persistence: build-time configuration and default module parameter values only.

Dependencies and integration points: integrates i915 with DRM helpers, display helpers, KMS, ACPI video, Intel GTT, audio, CEC, TTM, auxiliary bus, selftests, virtualization, protected content, and DP tunnel support.

Risks: large dependency surface; force-probe can enable unsupported hardware and taint the kernel. `!PREEMPT_RT` excludes realtime kernels because tracepoints are disabled globally through Makefile flags. Optional features require matching firmware/subsystems.

Test signals: allmodconfig, i915 module build, selected feature builds, force_probe parameter behavior, and boot/probe on supported and blocked PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Makefile

Purpose: defines the i915 build graph, compiler flags, conditional object lists, display/GT/GEM/PXP/GVT/selftest components, and header/kernel-doc test hooks.

Important APIs/types: object aggregations include `i915-y`, `gt-y`, `gem-y`, conditional `i915-$(CONFIG_...)`, `obj-$(CONFIG_DRM_I915)`, and `obj-$(CONFIG_DRM_I915_GVT_KVMGT)`. Flags add format-truncation warnings, optional Werror, `-DI915`, optional `-DNOTRACE`, and include path.

Control flow: kbuild expands sorted object lists into the i915 module. Conditional sections add compat ioctls, debugfs, PMU, fbdev, ACPI, DP tunnel, GVT, PXP commands/debug, selftests, and header tests.

State and persistence: build-time only.

Dependencies and integration points: integrates nearly all i915 subsystems: core driver, GT, GEM/TTM, display, encoders, DP/HDMI/DSI/LVDS/DVO, GuC/HuC/GSC, PXP, error capture, selftests, GVT, and generated render state.

Risks: file list ordering and conditional objects are critical for link correctness. The DVO source files in this subset are always part of modesetting output/encoder code. Header tests intentionally exclude broken headers. PREEMPT_RT disables tracing wholesale through `NOTRACE`.

Test signals: full i915 build across config matrices, Werror/kernel-doc builds, module symbol/link checks, selftest builds, and display-only source reuse with `-DI915`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/bxt_dpio_phy_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/bxt_dpio_phy_regs.h

Purpose: defines Broxton DPIO PHY MMIO register addresses and bitfields for i915 display PHY and PLL programming.

Important APIs/types: macros map PHY base addresses, channel/lane addressing, port PLL enable/status, PLL divisor/fraction/gain/lock fields, common lane registers, reference calibration registers, PCS lane/group registers, and TX lane/group swing/de-emphasis/DCC/latency fields.

Control flow: no executable control flow. Display PHY/PLL code includes this header to calculate register addresses for specific PHY, channel, port, and lane operations.

State and persistence: hardware state lives in the BXT PHY registers addressed here. The header itself stores no state.

Dependencies and integration points: depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PORT`, `_PICK_EVEN_2RANGES`, `_PIPE`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Used by Broxton display PHY and DPLL management code.

Risks: address selection is highly platform-specific. PHY0/PHY1/PHY2 base mapping and channel/lane offset math must match silicon. Misprogramming PLL or TX fields can prevent display link lock or damage signal integrity.

Test signals: BXT PHY power good, PLL lock, GRC calibration, DP/HDMI link bring-up, lane swing/de-emphasis tuning, and register readback on Broxton hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/bxt_dpio_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7017.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7017.c

Purpose: i915 DVO driver for Chrontel CH7017/CH7018/CH7019 LVDS transmitters over I2C.

Important APIs/functions: exported `ch7017_ops` implements init, detect, mode_valid, mode_set, dpms, get_hw_state, dump_regs, and destroy for `intel_dvo_dev_ops`. Internal I2C helpers read/write 8-bit registers. `ch7017_mode_set()` programs LVDS PLL, output channels, active dimensions, and power-down registers. `ch7017_dpms()` powers LVDS on/off and keeps TV DACs powered down.

Control flow: i915 DVO core calls init to detect device ID and allocate private state. During modeset, the driver dumps registers, disables output, programs mode-dependent PLL/output fields based on 100 MHz threshold and assumed dual-channel support, then powers LVDS back. DPMS and get_hw_state manage/read LVDS power state.

State and persistence: only a dummy private allocation is stored in `dvo->dev_priv`. Hardware register state persists in the CH7017 over I2C. No EDID or panel state is stored.

Dependencies and integration points: depends on i915 DVO core, `intel_dvo_dev_ops`, Linux I2C transfer, and DRM debug logging.

Risks: `detect()` always returns connected. Dual-channel panel detection is hardcoded true in a dead conditional. Mode validity only caps clock at 160 MHz. I2C read/write failures during mode set are not propagated. Power sequencing waits a fixed 20 ms.

Test signals: I2C probe IDs for CH7017/18/19, LVDS output at low/high clock modes, DPMS on/off, register dump correctness, and behavior on missing or NACKing device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7017.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7xxx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7xxx.c

Purpose: i915 DVO driver for Chrontel CH7xxx DVI/TV-output chips, especially CH701x/CH7301 class devices.

Important APIs/functions: exported `ch7xxx_ops` implements init/detect/mode_valid/mode_set/dpms/get_hw_state/dump_regs/destroy. Helpers identify vendor/device IDs, read/write 8-bit I2C registers, detect DVI connection, program PLL/timing control registers, and set power management bits.

Control flow: init allocates private state, probes vendor and device IDs quietly, then enables logging after a match. Detect temporarily powers DVI logic, reads connection-detect, and restores original power state. Mode set chooses timing values based on <=65 MHz or higher clocks, programs clock and PLL controls, updates input sync polarity, and configures sync outputs. DPMS toggles DVI power bits.

State and persistence: `struct ch7xxx_priv` stores only quiet flag. Hardware state persists in chip registers.

Dependencies and integration points: i915 DVO core, Linux I2C, DRM debug logging, and DVO connector/encoder machinery.

Risks: ID tables are limited. Detection manipulates power management and assumes safe restoration. I2C failures are mostly logged but not returned through DVO ops. Mode programming is coarse and only supports fixed clock ranges with a 165 MHz cap.

Test signals: probe across supported Chrontel IDs, DVI connection detection, 65 MHz threshold modes, sync polarity, DPMS state readback, and register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ch7xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ivch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ivch.c

Purpose: i915 DVO driver for Intel i82807AA/IVCH LVDS panel controller over I2C.

Important APIs/functions: exported `ivch_ops` implements init, dpms, get_hw_state, mode_valid, mode_set, detect, dump_regs, and destroy. `ivch_read()` and `ivch_write()` access 16-bit registers through a special multi-message I2C sequence. `ivch_reset()` restores a saved register backup. Mode set configures dithering and panel fitting ratios.

Control flow: init allocates private state, verifies VR00 base address matches target I2C address, reads native panel width/height, backs up a fixed register list, and dumps registers. DPMS resets registers, writes backlight GPIO, toggles LCD/DVO enable bits, polls panel status, then waits extra. Mode set resets, determines 18 bpp dithering, enables fitting if requested mode differs from adjusted CRTC mode, and writes ratio registers.

State and persistence: `struct ivch_priv` stores quiet flag, panel width/height, and backups for resume/reset. Hardware register state persists in IVCH.

Dependencies and integration points: i915 DVO core, I2C, DRM display modes, and DRM debug logging.

Risks: `detect()` always reports connected. Register reset before most operations can mask external state changes. Panel fitting ratio math divides by adjusted dimensions minus one, relying on valid modes. I2C failure handling is best-effort. Backup restore depends on init-time BIOS state.

Test signals: I2C probe with matching base address, suspend/resume restore, DPMS transitions and panel status polling, scaling/fitting modes, dithering on 18 bpp panel configurations, and register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ivch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ns2501.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ns2501.c

Purpose: i915 DVO driver for National Semiconductor NS2501 panel controller, with reverse-engineered mode tables for 1024x768 laptop panels.

Important APIs/functions: exported `ns2501_ops` implements init, detect, mode_valid, mode_set, dpms, get_hw_state, and destroy. The file defines register constants, mode-specific configuration tables for 640x480, 800x600, and 1024x768, mode-agnostic register values, and I2C read/write helpers.

Control flow: init allocates private state and probes vendor/device low bytes. Mode validation accepts exactly three mode/clock combinations. Mode set writes init registers, mode-agnostic register table, then mode-specific PLL, scaler, sync, display-window, position, dither, and sync-control values, storing the selected config in private state. DPMS uses the stored config to sequence output/backlight enable or disable with fixed delays.

State and persistence: `struct ns2501_priv` stores quiet flag and pointer to the current configuration. Hardware state persists in NS2501 registers. DPMS assumes `mode_set()` has already populated `ns->conf`.

Dependencies and integration points: i915 DVO core, I2C, DRM debug logging, and DVO connector/encoder machinery.

Risks: the driver relies on reverse-engineered magic values and only supports three exact modes. `detect()` always returns connected due to unreliable hardware detection. Calling DPMS before mode_set could dereference a null config. I2C write failures are ignored during large table programming.

Test signals: vendor/device probe, exact supported mode validation, visible output for all three tabled modes, DPMS/backlight sequence, behavior after suspend/resume, and missing-device I2C failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ns2501.c -->
