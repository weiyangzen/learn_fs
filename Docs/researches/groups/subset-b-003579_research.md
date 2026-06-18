# Research: subset-b-003579

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.c

## Purpose

`i9xx_wm.c` implements FIFO watermark and memory self-refresh control for pre-SKL Intel display hardware: i845/i830/i9xx/i965/Pineview, G4x, Valleyview/Cherryview, and Ironlake through Broadwell PCH-split platforms. It computes safe plane, cursor, sprite, FBC, self-refresh, HPLL, PM5, and DDR DVFS watermark settings from display mode, pixel format, plane visibility, FIFO partitioning, memory latency, and platform quirks, then programs the relevant MMIO/Punit registers during atomic commit phases and hardware state sanitization.

## Important APIs, Types, And Functions

The exported entry points are `intel_set_memory_cxsr()`, `ilk_disable_cxsr()`, `ilk_wm_sanitize()`, and `i9xx_wm_init()`. `i9xx_wm_init()` selects a `struct intel_wm_funcs` implementation for the platform. The main helper data types are `struct intel_watermark_params`, `struct intel_wm_config`, `struct cxsr_latency`, `struct g4x_wm_state`, `struct vlv_wm_state`, `struct intel_pipe_wm`, `struct ilk_wm_values`, `struct g4x_wm_values`, and `struct vlv_wm_values` as carried inside `intel_display` and `intel_crtc_state`.

The legacy path uses `i9xx_compute_watermarks()` to mark pre/post watermark updates and `i845_update_wm()`, `i9xx_update_wm()`, `i965_update_wm()`, or `pnv_update_wm()` to program registers. The G4x path centers on `g4x_raw_plane_wm_compute()`, `_g4x_compute_pipe_wm()`, `g4x_compute_intermediate_wm()`, `g4x_program_watermarks()`, `g4x_wm_get_hw_state()`, and `g4x_wm_sanitize()`. The VLV/CHV path uses `vlv_compute_fifo()`, `vlv_raw_plane_wm_compute()`, `_vlv_compute_pipe_wm()`, `vlv_atomic_update_fifo()`, `vlv_program_watermarks()`, `vlv_wm_get_hw_state()`, and `vlv_wm_sanitize()`. The ILK/SNB/IVB/HSW/BDW path uses `ilk_setup_wm_latency()`, `ilk_compute_pipe_wm()`, `ilk_compute_intermediate_wm()`, `ilk_wm_merge()`, `ilk_compute_wm_results()`, `ilk_write_wm_values()`, and `ilk_wm_get_hw_state()`.

## Control Flow

Initialization chooses the platform function table and reads or seeds memory latency values. PCH-split platforms read MCH/SSKPD/MLTR latency registers and apply SNB underrun and LP3 interrupt quirks. G4x and VLV seed fixed latency levels. Pineview validates its FSB/memory latency table before enabling the Pineview update path.

Atomic check computes per-CRTC watermark state. For G4x, VLV, and ILK-style atomic paths, plane states are converted into raw watermark levels, invalid levels are marked with `USHRT_MAX`, and an optimal pipe state is derived. An intermediate state is then created by combining old and new values so the hardware can be programmed before vblank without risking underrun; if the intermediate differs from the optimal state, `wm.need_postvbl_update` triggers a second programming pass. For non-atomic legacy GMCH paths, plane changes only set `update_wm_pre` and `update_wm_post`, and the old global update functions recompute directly from current CRTC and primary-plane state.

Programming merges per-pipe active watermark state into global register values. G4x enables CxSR/HPLL only for one active pipe with compatible state and temporarily disables CxSR before unsafe transitions. VLV/CHV additionally handles PM5 and DDR DVFS transitions through Punit sideband registers and updates DSPARB FIFO partitions under `uncore->lock`. ILK-style code merges LP1+ watermarks across active pipes, evaluates 1/2 versus 5/6 DDB partitioning when possible, disables affected LP watermarks before touching LP0, FBC, partitioning, or LP registers, and avoids unnecessary writes because the hardware reevaluates watermarks on each write.

## State And Persistence Behavior

Persistent software state lives in `display->wm`, per-CRTC `crtc->wm.active`, and per-commit `intel_crtc_state->wm`. Hardware state persists in DSPARB/DSPFW/FW_BLC, WM0/WM_LP/WM_MISC/DISP_ARB registers, VLV DDL registers, and Cherryview Punit PM/DVFS registers. CxSR is both hardware policy and tracked state for VLV and G4x. FIFO partition state is explicit in VLV `fifo_state` and can be reset by display power wells, so modesets force recomputation. Hardware readout reconstructs only what is trustworthy; sanitize paths recompute from current DRM state and rewrite hardware to match driver expectations.

## Dependencies And Integration Points

This file integrates DRM atomic state, i915 display register access (`intel_de_*`), platform descriptors, CRTC/plane state, framebuffer format/modifier state, FBC watermark support, Punit sideband access on VLV/CHV, memory/DRAM information for Pineview, tracepoints, and the common watermark hooks in `intel_wm.h`. It is selected by display init and then called by the generic Intel atomic modeset pipeline for check, initial programming, post-vblank optimization, atomic FIFO updates, hardware readout, and sanitize.

## Risks And Edge Cases

The primary risk is underrun or lost vblank interrupt from too-aggressive watermarks, incorrect latency readout, or unsafe transition ordering. Legacy code assumes reconstructed primary framebuffer and adjusted mode state are valid before using `intel_crtc_active()`. VLV FIFO repartitioning has pipe-specific high-bit registers and a sprite0 workaround when sprite1 is active alone. CHV DDR DVFS may not acknowledge requests if BIOS disabled DVFS, and readout adapts by reducing available levels. ILK/SNB/IVB restrictions around sprites, scaling, multiple pipes, and FBC watermarks can silently reduce usable LP levels. Sanitization intentionally leaves BIOS watermarks untouched if the recomputed state is invalid.

## Test Signals

Useful validation includes boot fastboot/readout on every supported platform family, modesets with one and multiple active pipes, plane enable/disable/resize/rotation/tiling changes, cursor and sprite-only transitions, FBC enabled and disabled, VLV/CHV sprite FIFO repartition and power-well reset recovery, CxSR disable around plane updates, SNB high-resolution modes, LP3 interrupt quirk systems, suspend/resume, and underrun/vblank interrupt monitoring under IGT KMS plane, cursor, flip, FBC, PSR-disabled, and modeset stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.h

## Purpose

`i9xx_wm.h` is the internal interface for the legacy Intel display watermark implementation. It exposes the small set of cross-file entry points needed by display initialization, atomic commit, and CxSR management while hiding the platform-specific computation and register programming details in `i9xx_wm.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display`, `struct intel_crtc_state`, and `struct intel_plane_state`. Under `I915`, it declares `ilk_disable_cxsr()`, `ilk_wm_sanitize()`, `intel_set_memory_cxsr()`, and `i9xx_wm_init()`. Without `I915`, it provides no-op inline stubs returning safe defaults, so non-i915 builds can include shared display headers without linking the legacy watermark implementation.

## Control Flow

The header has no runtime control flow of its own. Callers use `i9xx_wm_init()` during display setup to install platform watermark callbacks. Commit and plane update paths can call `intel_set_memory_cxsr()` or `ilk_disable_cxsr()` before register updates that must not occur while the hardware is in self-refresh or low-power watermark modes. Hardware readout paths can call `ilk_wm_sanitize()` after initial state reconstruction.

## State And Persistence Behavior

No state is stored in the header. The functions it declares manipulate `display->wm`, per-CRTC watermark state, and display hardware registers through the implementation file. The no-op stubs preserve build-time behavior by avoiding state changes when the i915 implementation is not compiled.

## Dependencies And Integration Points

The header depends only on `<linux/types.h>` and forward declarations. It integrates the legacy watermark code with broader Intel display code while avoiding exposure of register macros or private watermark structures. The compile-time `I915` guard is the main integration boundary.

## Risks And Edge Cases

Because the non-I915 stubs silently return false or do nothing, call sites must not assume CxSR was actually disabled unless they are in a real i915 build. Any signature drift between this header and `i9xx_wm.c` would break platform initialization or suspend/resume sanitize paths. The declarations include `intel_crtc_state` and `intel_plane_state` forward declarations even though this header currently exports only display-level functions, so cleanup should verify whether those declarations remain necessary.

## Test Signals

Build coverage with and without `I915`, link coverage for all exported symbols, and boot tests on pre-SKL display platforms are the relevant signals. Static analysis should verify that callers handle the boolean return from CxSR helpers appropriately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm_regs.h

## Purpose

`i9xx_wm_regs.h` defines MMIO register addresses, field masks, shifts, register encoders, FIFO sizes, and maximum watermark constants used by the pre-SKL Intel display watermark code. It is a hardware-description header for legacy GMCH, Pineview, G4x, VLV/CHV, and Ironlake-style watermark programming.

## Important APIs, Types, And Macros

The header defines FIFO partition registers `DSPARB`, `DSPARB2`, `DSPARB3`, watermark registers `DSPFW1` through `DSPFW9_CHV`, high-order watermark registers `DSPHOWM`/`DSPHOWM1`, VLV drain latency registers `VLV_DDL(pipe)`, FIFO size constants such as `VALLEYVIEW_FIFO_SIZE`, `G4X_FIFO_SIZE`, `I965_FIFO_SIZE`, `I915_FIFO_SIZE`, and Pineview-specific limits. For Ironlake-style low-power watermarks it defines `WM0_PIPE_ILK(pipe)`, `WM1_LP_ILK`, `WM2_LP_ILK`, `WM3_LP_ILK`, `WM1S_LP_ILK`, `WM2S_LP_IVB`, `WM3S_LP_IVB`, `WM_MISC`, `WM_DBG`, and field macros such as `WM_LP_ENABLE`, `WM_LP_LATENCY()`, `WM_LP_PRIMARY()`, `WM_LP_CURSOR()`, and `WM_LP_SPRITE()`.

## Control Flow

This header has no runtime control flow. Consumers compose register values with the masks and `REG_FIELD_PREP` helpers before writing through `intel_de_write()` or read fields back through matching masks. The macros encode platform-specific register aliasing, such as Cherryview using `DSPFW7_CHV`, `DSPFW8_CHV`, and `DSPFW9_CHV` where some offsets overlap or differ from Valleyview.

## State And Persistence Behavior

No software state is stored here. The macros name hardware registers whose values persist until rewritten, reset, or lost through display power transitions. DSPARB fields persist FIFO boundaries; DSPFW and WM_LP fields persist plane, cursor, sprite, self-refresh, HPLL, and FBC watermark thresholds; VLV DDL fields persist drain latency settings.

## Dependencies And Integration Points

The header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PORT`, `_MMIO_BASE_PIPE3`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. It is consumed primarily by `i9xx_wm.c`, but its register names also document the hardware contract that readout and sanitize code must respect.

## Risks And Edge Cases

The main risk is mismatched masks and shifts, because many registers pack multiple planes and some VLV/CHV watermarks need high bits in separate registers. Comments noting unusual CHV offsets highlight hardware quirks that should not be normalized without checking the specification. Cursor masks differ from plane and sprite masks. The constants are in cachelines or register units, not bytes, so consumers must convert consistently.

## Test Signals

Signals include register read/write tracing during watermark programming, comparing generated bitfields against hardware documentation, VLV/CHV pipe A/B/C FIFO partition tests, G4x FBC/HPLL self-refresh tests, Ironlake LP watermark enable/disable sequences, and compile coverage after any register macro refactor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.c

## Purpose

`icl_dsi.c` implements Gen11+ Intel MIPI DSI encoder, connector, host-transfer, PHY, transcoder, panel power, backlight, DSC, and mode-configuration support. It translates VBT DSI panel data and DRM atomic state into DSI packet transfers, Combo PHY setup, DSI PLL/escape clock setup, transcoder timing registers, panel command sequences, and connector properties.

## Important APIs, Types, And Functions

The exported functions are `icl_dsi_init()` and `icl_dsi_frame_update()`. Initialization allocates `struct intel_dsi` and `struct intel_connector`, registers a DRM DSI encoder and connector, creates per-port `struct intel_dsi_host` objects with `gen11_dsi_host_ops`, initializes VBT panel data, computes D-PHY timing registers in `icl_dphy_param_init()`, and adds scaling/orientation properties. Packet transmission uses `gen11_dsi_host_transfer()`, `dsi_send_pkt_payld()`, `dsi_send_pkt_hdr()`, and credit wait helpers. Power and enable sequencing is split across encoder hooks: `gen11_dsi_pre_pll_enable()`, `gen11_dsi_pre_enable()`, `gen11_dsi_enable()`, `gen11_dsi_disable()`, and `gen11_dsi_post_disable()`.

Key programming helpers include `gen11_dsi_program_esc_clk_div()`, `gen11_dsi_map_pll()`, `gen11_dsi_enable_io_power()`, `gen11_dsi_power_up_lanes()`, `gen11_dsi_config_phy_lanes_sequence()`, `gen11_dsi_voltage_swing_program_seq()`, `gen11_dsi_setup_dphy_timings()`, `gen11_dsi_setup_timings()`, `gen11_dsi_setup_timeouts()`, `gen11_dsi_configure_transcoder()`, `gen11_dsi_set_transcoder_timings()`, and `configure_dual_link_mode()`. Atomic state support comes through `gen11_dsi_compute_config()`, `gen11_dsi_get_config()`, `gen11_dsi_get_hw_state()`, and `gen11_dsi_initial_fastset_check()`.

## Control Flow

Probe-time initialization starts from a VBT encoder entry, determines the port, allocates objects, wires DRM callbacks, loads fixed panel modes and backlight data, determines single or dual-link ports, creates MIPI DSI hosts, runs VBT DSI initialization, and computes D-PHY register values from panel timing parameters. A host transfer builds a `mipi_dsi_packet`, writes long-packet payload DWORDs when needed, then writes the header with low-power or high-speed flags after checking hardware credits.

During enable, the pre-PLL hook waits panel power-cycle timing, runs VBT power/reset sequences, switches IO mode to DSI, takes IO power references, and programs escape clock divisors. The pre-enable hook maps the PLL, powers lanes, programs PHY sequencing, voltage swing, D-PHY timing, DDI buffer, clocks, utility TE pin, timeouts, protocol mode, dual-link splitter, and panel initialization commands, then writes DSC PPS and transcoder timings. The enable hook applies workarounds, enables the DSI transcoder, sends display/backlight-on sequences, prepares the panel, and enables vblank. Disable reverses this order: panel unprepare and backlight off first, then vblank off, transcoder disable, panel display off, ULPS entry, DDI function disable, DSC/scaler cleanup, port and IO power disable, reset assert, power off, and panel power-off timestamp update.

## State And Persistence Behavior

Persistent driver state lives in `struct intel_dsi`: selected ports/phys, lane count, pixel format, dual-link mode, VBT sequence data, panel timings, D-PHY register values, DSI hosts, IO wakerefs, panel power-off time, and attached connector. Hardware state persists in DSI command, timing, timeout, transcoder, DDI, PLL clock, Combo PHY, DSS splitter, utility pin, DSC, and backlight registers until the disable path or modeset rewrites them. Atomic state records output format, bpp, compressed DSC parameters, selected DSI transcoder, port clock, TE flags, and periodic command mode readout.

## Dependencies And Integration Points

The file integrates DRM MIPI DSI helpers, DRM atomic connector helpers, Intel VBT DSI parser, panel/backlight helpers, Combo PHY and DDI code, DPLL state, DSC helpers, scaler helpers, CRTC vblank control, power domains, and DSI register definitions from `icl_dsi_regs.h`. It plugs into the generic Intel encoder lifecycle through function pointers installed in `icl_dsi_init()`.

## Risks And Edge Cases

Enable/disable ordering is hardware-sensitive: IO power refs, PLL mapping, DDI buffer state, ULPS, command credit waits, panel command dispatch, DSC PPS, vblank, and backlight must remain ordered. Dual-link front/back mode depends on buffer-depth and overlap calculations. Command mode TE uses GPIO/UTIL pin assumptions and port-specific frame update flags. DSC intentionally forces full modesets in the fastset check. Several sanity failures log errors rather than aborting, so invalid timing inputs may still be programmed. Error cleanup in `icl_dsi_init()` must balance partially initialized connectors, encoders, hosts, and allocated objects.

## Test Signals

Useful tests include single-link and dual-link DSI panels, command and video modes, TE0/TE1 frame updates, long and short MIPI packet transfers, low-power transfer mode, DSC-enabled modes, backlight and VBT sequence ordering, suspend/resume, fastboot readout, hot-unplug or missing fixed-mode error paths, ADL escape-clock programming, JSL/EHL/TGL PHY branches, DDI buffer idle waits, ULPS entry, and IGT panel/backlight/modeset tests on real DSI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.h

## Purpose

`icl_dsi.h` is the public internal header for Gen11+ Intel DSI support. It exposes initialization and command-mode frame-update entry points to the rest of the i915 display driver while keeping the encoder implementation private to `icl_dsi.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display`, `struct intel_bios_encoder_data`, and `struct intel_crtc_state`. It declares `icl_dsi_init(struct intel_display *display, const struct intel_bios_encoder_data *devdata)` for VBT-driven encoder/connector creation and `icl_dsi_frame_update(struct intel_crtc_state *crtc_state)` for requesting a TE-gated command-mode frame update on the relevant DSI port.

## Control Flow

The header has no direct control flow. Display initialization calls `icl_dsi_init()` when firmware/VBT enumerates a DSI child device. Command-mode update paths call `icl_dsi_frame_update()` after inspecting CRTC mode flags that indicate TE0 or TE1 use.

## State And Persistence Behavior

No state is stored in this header. `icl_dsi_init()` creates and persists encoder, connector, DSI host, panel, and backlight state in heap objects and DRM lists. `icl_dsi_frame_update()` affects hardware frame-update request bits through the implementation.

## Dependencies And Integration Points

The header is intentionally light and depends only on forward declarations. It integrates DSI implementation with BIOS encoder enumeration and CRTC update code, and it avoids exposing MIPI DSI, PHY, or register details to unrelated display files.

## Risks And Edge Cases

Callers must pass a valid VBT encoder data object to initialization; a missing or invalid port causes the implementation to return without creating a connector. Frame-update calls rely on `crtc_state->mode_flags` being populated by the DSI command-mode configuration/readout path. If additional DSI entry points are added, this header should remain a narrow boundary rather than exposing register-level helpers.

## Test Signals

Compile coverage, DSI child-device probe, command-mode frame-update behavior for TE0, TE1, and dual-link configurations, and symbol checks for users of the two declared functions are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi_regs.h

## Purpose

`icl_dsi_regs.h` defines Gen11+ Intel DSI, D-PHY, command, interrupt, timing, transcoder, low-power message, and timeout register addresses and bitfields. It is the register contract used by `icl_dsi.c` when programming MIPI DSI ports and transcoders.

## Important APIs, Types, And Macros

Important address helpers include `_MMIO_DSI()`, `ICL_DSI_ESC_CLK_DIV(port)`, `ICL_DPHY_ESC_CLK_DIV(port)`, `ADL_MIPIO_DW(port, dw)`, `DSI_CMD_FRMCTL(port)`, `DSI_INTR_MASK_REG(port)`, `DSI_INTR_IDENT_REG(port)`, `ICL_DSI_IO_MODECTL(port)`, `TGL_DSI_CHKN_REG(port)`, `ICL_DSI_T_INIT_MASTER(port)`, `DPHY_*_TIMING_PARAM(port)`, `DSI_*_TIMING_PARAM(port)`, `DSI_TRANS_FUNC_CONF(tc)`, `DSI_CMD_RXCTL(tc)`, `DSI_CMD_TXCTL(tc)`, `DSI_CMD_TXHDR(tc)`, `DSI_CMD_TXPYLD(tc)`, `DSI_LP_MSG(tc)`, and timeout registers `DSI_HSTX_TO()`, `DSI_LPRX_HOST_TO()`, `DSI_PWAIT_TO()`, and `DSI_TA_TO()`.

Key fields include escape clock divisors, frame update request/periodic/null-packet bits, DSI interrupt status bits, Combo PHY DSI mode, LP-to-HS guardband, D-PHY clock/data/turnaround timing overrides, transcoder operation mode, TE source, link ready, pixel format, BGR transmission, virtual channel, continuous clock, low-power clock during LPM, calibration, blanking packet enable, command TX/RX credit fields, packet header flags, ULPS/LPTX bits, and timeout values.

## Control Flow

The header has no runtime control flow. It supplies packed field encoders and masks for the DSI implementation to program based on VBT data, atomic CRTC state, panel mode, command/video mode, DSC use, and platform generation.

## State And Persistence Behavior

No software state is stored here. The named hardware registers persist DSI clocking, protocol mode, packet queues, link state, ULPS state, timing, timeout, and interrupt status. Some registers are port-indexed and others are DSI-transcoder-indexed, so correct conversion between port and transcoder is required by consumers.

## Dependencies And Integration Points

The header depends on `intel_display_reg_defs.h` for MMIO and bitfield helpers. It is paired with `icl_dsi.c` and also aligns with Combo PHY/DDI/DSS register programming in other headers. Platform-specific fields such as ADL MIPIO and TGL chicken registers support generation-specific workarounds in the DSI implementation.

## Risks And Edge Cases

Field misuse can wedge DSI links: packet credit shifts, payload/header masks, ULPS bits, TE mode, and timeout fields have side effects. Some pixel-format constants exceed the documented two-bit `PIX_FMT_MASK` shape, so consumer assumptions must follow the actual hardware definition. Address helpers mix port and transcoder domains, and accidental use of `PORT_B` where `TRANSCODER_DSI_1` is required would target the wrong register.

## Test Signals

Register trace comparison during DSI enable, command transfer credit tests, command-mode frame update, video-mode timing programming, DSC compressed-pixel format, ULPS entry, ADL/TGL platform branches, interrupt status decoding, and static checks against the hardware specification are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.c

## Purpose

`intel_acpi.c` provides ACPI integration for the Intel display driver. It probes Intel display `_DSM` methods, logs platform mux information, evaluates a BIOS-data support DSM, assigns ACPI display device IDs to DRM connectors, associates connector firmware nodes, and registers ACPI video/backlight support when appropriate.

## Important APIs, Types, And Functions

Public functions are `intel_register_dsm_handler()`, `intel_unregister_dsm_handler()`, `intel_dsm_get_bios_data_funcs_supported()`, `intel_acpi_device_id_update()`, `intel_acpi_assign_connector_fwnodes()`, and `intel_acpi_video_register()`. Internal helpers include `intel_dsm_port_name()`, `intel_dsm_mux_type()`, `intel_dsm_platform_mux_info()`, `intel_dsm_pci_probe()`, `intel_dsm_detect()`, and `acpi_display_type()`. The file defines two Intel DSM GUIDs and ACPI `_DOD` display-device ID bitfields.

## Control Flow

DSM registration scans VGA-class PCI devices, checks for the Intel mux-info DSM, logs any mux package contents, and reports detection only when two VGA devices and an Intel DSM handle are present. The BIOS-data DSM helper obtains the i915 PCI ACPI handle and evaluates the second DSM function. Connector ACPI ID update iterates DRM connectors, maps connector type to ACPI display type, and assigns a per-type display index. Firmware-node assignment walks child fwnodes in connector order and prefers ACPI child address `0x1f` for integrated panels when available. ACPI video registration calls `acpi_video_register()` and registers ACPI video backlight only if an internal panel has native backlight functions but no backlight device.

## State And Persistence Behavior

Persistent state changes are connector-local: `connector->acpi_device_id` and `connector->fwnode` references. DSM probing itself is diagnostic and does not install a switcheroo handler in this implementation. ACPI video/backlight registration affects global ACPI video state managed outside this file. Fwnode references are acquired with `fwnode_handle_get()` and must be released by connector cleanup paths.

## Dependencies And Integration Points

The file integrates Linux ACPI, PCI device enumeration, ACPI video, DRM connector iteration, Intel connector/panel state, and display utility macros. It is called from display bring-up after connectors exist and connector order is final. The ACPI IDs follow ACPI spec `_DOD` encoding and feed firmware/user-space display identification.

## Risks And Edge Cases

DSM package parsing is defensive but only logs malformed objects. Connector fwnode assignment assumes firmware child-node order matches final connector order; calling it too early would attach wrong fwnodes. Integrated panel special handling assumes ACPI child address `0x1f` on most platforms but falls back when absent. ACPI video backlight registration must avoid racing native backlight registration on other GPUs. `intel_unregister_dsm_handler()` is intentionally empty.

## Test Signals

Useful validation includes hybrid-graphics systems with Intel mux DSM, malformed or absent DSM packages, connector ACPI ID stability across boot, internal panel fwnode assignment, external connector fwnode ordering, ACPI video backlight fallback when native device is missing, and builds with `CONFIG_ACPI` enabled and disabled via the header stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.h

## Purpose

`intel_acpi.h` declares the i915 display ACPI integration hooks and supplies no-op stubs when ACPI support is disabled. It is the boundary between generic display bring-up code and ACPI-specific connector, DSM, and backlight behavior.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display`. With `CONFIG_ACPI`, it declares `intel_register_dsm_handler()`, `intel_unregister_dsm_handler()`, `intel_dsm_get_bios_data_funcs_supported()`, `intel_acpi_device_id_update()`, `intel_acpi_assign_connector_fwnodes()`, and `intel_acpi_video_register()`. Without `CONFIG_ACPI`, inline stubs return immediately.

## Control Flow

There is no standalone control flow. Display initialization and cleanup can call these functions unconditionally; the preprocessor selects real ACPI behavior or no-op stubs.

## State And Persistence Behavior

The header stores no state. Real implementations update connector ACPI IDs, connector fwnode references, and ACPI video/backlight registration. Stub builds intentionally leave those states untouched.

## Dependencies And Integration Points

The header avoids including ACPI headers directly and depends only on the forward declaration of `intel_display`. It integrates ACPI support with the rest of i915 while keeping non-ACPI builds simple.

## Risks And Edge Cases

Callers must tolerate no-op behavior in non-ACPI builds. Any future function that needs a return value should define a meaningful stub result rather than silently hiding an error. Since connector fwnodes and ACPI IDs are absent in stub builds, user-space or tests expecting firmware-node metadata must account for `CONFIG_ACPI`.

## Test Signals

Build tests with `CONFIG_ACPI=y` and `CONFIG_ACPI=n`, boot tests verifying connector metadata on ACPI systems, and static checks for unconditional call sites are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.c

## Purpose

`intel_alpm.c` implements DisplayPort/eDP Adaptive Link Power Management support, including AUX wake, AUX-less wake, Lunar Lake ALPM timing calculations, Panel Replay ALPM programming, Link Off Between Frames (LOBF) policy, sink DPCD enablement, debugfs controls, hardware disable, and ALPM error handling.

## Important APIs, Types, And Functions

Public entry points include `intel_alpm_init()`, `intel_alpm_aux_wake_supported()`, `intel_alpm_aux_less_wake_supported()`, `intel_alpm_is_alpm_aux_less()`, `intel_alpm_compute_params()`, `intel_alpm_lobf_compute_config()`, `intel_alpm_lobf_compute_config_late()`, `intel_alpm_lobf_min_guardband()`, `intel_alpm_configure()`, `intel_alpm_port_configure()`, `intel_alpm_enable_sink()`, `intel_alpm_lobf_enable()`, `intel_alpm_lobf_disable()`, `intel_alpm_lobf_debugfs_add()`, `intel_alpm_disable()`, and `intel_alpm_get_error()`. Internal timing helpers calculate silence period symbols, LFPS cycles, AUX-less wake time, fast wake lines, IO wake lines, and LOBF feasibility.

## Control Flow

Initialization creates `intel_dp->alpm.lock`. During atomic configuration, `intel_alpm_lobf_compute_config()` filters for eDP, Display version 20+, adaptive-sync SDP support, no PSR, fixed VRR timing, supported ALPM DPCD capabilities, and successful timing computation before setting `crtc_state->has_lobf`. A late LOBF check then verifies Window 1 and guardband/wake timing after other state fields such as VRR guardband and context latency are known. `intel_alpm_compute_params()` converts eDP spec timing, AUX precharge/preamble, PHY wake, fast wake, and LNL AUX-less timing into scanline counts stored in `crtc_state->alpm_state`.

Enable/configure flow writes sink DPCD `DP_RECEIVER_ALPM_CONFIG`, then writes transcoder `ALPM_CTL` and optional `PR_ALPM_CTL`, and writes port-level ALPM/LFPS registers for AUX-less mode. LOBF enable iterates encoders in the CRTC state and applies the eDP DP path. Disable clears ALPM/LOBF bits in the stored transcoder. Error handling reads `DP_RECEIVER_ALPM_STATUS`, logs lock timeout, clears the sink error bit by writing it back, and returns whether an error was observed.

## State And Persistence Behavior

Persistent software state lives in `intel_dp->alpm`: lock, selected transcoder, debug disable flag, and sink error state from surrounding code. Per-commit ALPM state lives in `crtc_state->alpm_state` and `crtc_state->has_lobf`. Hardware state persists in transcoder `ALPM_CTL`, `PR_ALPM_CTL`, port `PORT_ALPM_CTL`, `PORT_ALPM_LFPS_CTL`, and sink DPCD ALPM configuration/status registers until disabled or reprogrammed.

## Dependencies And Integration Points

The file integrates DP/eDP state, PSR and Panel Replay decisions, DP AUX helpers, VRR fixed-rate policy, CRTC timing conversion, display register access, DP DPCD constants, and connector debugfs. It is used by DP modeset and panel power flows rather than by standalone connector code.

## Risks And Edge Cases

ALPM timing is highly generation-specific. The LNL AUX-less path has several unit conversions from link rate, symbols, microseconds, nanoseconds, and scanlines; overflow or rounding mistakes can either disable ALPM unnecessarily or cause wake timing violations. A FIXME notes that LOBF guardband currently uses the max of IO and AUX-less wake lines because the exact applicable wake mode is not readily available. Debugfs can force LOBF off. `intel_alpm_disable()` relies on the last stored transcoder. DPCD read failures are treated as errors, and sink lock-timeout status is cleared by writing the read value back.

## Test Signals

Validation should cover eDP panels with AUX wake and AUX-less wake capabilities, Display version 20+ hardware, Panel Replay with ALPM, LOBF with fixed VRR timing, debugfs disable and info files, PSR exclusion, sink error injection, suspend/resume and modeset disable clearing registers, safest-params behavior, and DPCD traces confirming sink configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.h

## Purpose

`intel_alpm.h` declares the DisplayPort/eDP ALPM interface used by DP, PSR, Panel Replay, VRR, modeset, and debugfs code. It exposes capability checks, parameter computation, hardware programming, LOBF lifecycle, and error handling while keeping timing formulas in `intel_alpm.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_dp`, `struct intel_crtc_state`, `struct drm_connector_state`, `struct intel_connector`, `struct intel_atomic_state`, and `struct intel_crtc`. It declares capability helpers `intel_alpm_aux_wake_supported()`, `intel_alpm_aux_less_wake_supported()`, and `intel_alpm_is_alpm_aux_less()`, setup and computation functions `intel_alpm_init()`, `intel_alpm_compute_params()`, `intel_alpm_lobf_compute_config()`, `intel_alpm_lobf_compute_config_late()`, and `intel_alpm_lobf_min_guardband()`, programming functions `intel_alpm_configure()`, `intel_alpm_port_configure()`, `intel_alpm_enable_sink()`, `intel_alpm_lobf_enable()`, `intel_alpm_lobf_disable()`, and lifecycle/debug helpers `intel_alpm_lobf_debugfs_add()`, `intel_alpm_disable()`, and `intel_alpm_get_error()`.

## Control Flow

The header has no direct control flow. It allows the DP modeset path to compute ALPM/LOBF eligibility during atomic check, program sink and source registers during enable, clear state during disable, and expose connector debugfs files at registration time.

## State And Persistence Behavior

No state is stored in the header. The implementation updates `intel_dp->alpm`, `intel_crtc_state->alpm_state`, source ALPM registers, and sink DPCD state. Call order is important because late LOBF computation depends on values established by earlier atomic computations.

## Dependencies And Integration Points

The header depends on `<linux/types.h>` for `bool` and forward declarations for Intel display types. It integrates ALPM with DP/eDP code while avoiding direct register or DPCD helper exposure.

## Risks And Edge Cases

The API mixes early compute, late compute, enable, disable, and debug responsibilities, so call sites must preserve ordering. `intel_alpm_is_alpm_aux_less()` depends on both PSR needs and LOBF state, making stale `crtc_state` data a risk. Future non-eDP or non-LNL support would need careful API expansion because current implementation filters heavily by output type and display version.

## Test Signals

Build coverage, DP modeset call-order tests, debugfs registration on eDP only, ALPM sink error handling, and LOBF enable/disable sequencing are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.c

## Purpose

`intel_atomic.c` implements shared i915 display atomic state helpers for digital connector properties, connector atomic checks, connector and CRTC state duplication/destruction, CRTC color blob lifetime, Intel atomic-state allocation/free/clear, and typed accessors for Intel connector and CRTC state.

## Important APIs, Types, And Functions

Connector property hooks are `intel_digital_connector_atomic_get_property()` and `intel_digital_connector_atomic_set_property()` for force-audio and broadcast-RGB properties. `intel_digital_connector_atomic_check()` runs HDCP atomic checks and requests a modeset when fastset-handled connector properties change. State helpers include `intel_digital_connector_duplicate_state()`, `intel_connector_needs_modeset()`, `intel_any_crtc_needs_modeset()`, `intel_atomic_get_digital_connector_state()`, `intel_crtc_duplicate_state()`, `intel_crtc_destroy_state()`, `intel_crtc_free_hw_state()`, `intel_atomic_state_alloc()`, `intel_atomic_state_free()`, `intel_atomic_state_clear()`, and `intel_atomic_get_crtc_state()`.

## Control Flow

DRM atomic property get/set callbacks translate generic connector state into `struct intel_digital_connector_state` and handle only known display properties. Connector atomic check compares old and new connector state for audio, RGB range, colorspace, aspect ratio, content type, scaling mode, privacy-screen software state, and HDR metadata changes; if any differ, it marks the associated CRTC state `mode_changed`. CRTC duplication kmemdups the old Intel CRTC state, invokes DRM helper duplication, increments references on color blobs and DP tunnel references, then clears transient flags and commit-only pointers so the new state starts clean. Destruction releases DRM helper state, color blobs, DP tunnel refs, and memory.

Intel atomic state allocation wraps `drm_atomic_state_init()` around `struct intel_atomic_state`. Clear releases default DRM state, clears Intel global state, intentionally preserves `state->internal`, resets top-level booleans, and cleans inherited DP tunnel atomic state. Typed getters wrap DRM atomic getters and cast to Intel state types.

## State And Persistence Behavior

The file manages lifetime and copying of persistent state snapshots rather than hardware registers. It preserves refcounted blobs (`degamma_lut`, `gamma_lut`, `ctm`, pre/post CSC LUTs) and DP tunnel references across duplicated states. It explicitly resets transient fields such as watermark update flags, FIFO change flags, async flip flags, DSB pointers, LUT preload flags, plane update bitmasks, and DSB usage so stale commit actions do not leak into later atomic checks.

## Dependencies And Integration Points

Dependencies include DRM atomic core/helpers, HDR metadata comparison, DP tunnel references, Intel display properties, HDCP, PSR, global state, CDCLK-related state via included headers, and universal plane state. These helpers are used by connector function tables, CRTC function tables, atomic check/commit code, and internal sanitize transactions.

## Risks And Edge Cases

Forgetting to refcount a new blob or pointer field in `intel_crtc_duplicate_state()` can cause use-after-free; forgetting to clear a transient field can cause spurious hardware programming. Connector atomic check marks mode changes for properties handled by fastset, which is conservative but can increase modesets. `intel_atomic_state_clear()` intentionally preserves `internal`, so callers must set it deliberately and not expect a full reset. Unknown property access returns `-EINVAL` after debug logging.

## Test Signals

Relevant tests include atomic property get/set for force audio and broadcast RGB, HDR metadata changes, connector scaling/colorspace/content-type changes, HDCP state checks, CRTC state duplication/destruction leak tests, DP tunnel reference lifetime, repeated atomic clear/reuse, async flip state reset, DSB pointer WARN coverage, and KASAN/KMEMLEAK under IGT atomic modeset stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.h

## Purpose

`intel_atomic.h` declares shared i915 atomic display helper APIs for connector property handling, connector/CRTC state access, modeset detection, and Intel atomic-state lifetime management. It is the common header included by encoder, connector, CRTC, watermark, and modeset code needing typed Intel wrappers around DRM atomic state.

## Important APIs, Types, And Functions

The header forward declares DRM and Intel atomic, connector, CRTC, and property types. It declares digital connector hooks `intel_digital_connector_atomic_get_property()`, `intel_digital_connector_atomic_set_property()`, `intel_digital_connector_atomic_check()`, and `intel_digital_connector_duplicate_state()`. It declares modeset/state accessors `intel_connector_needs_modeset()`, `intel_any_crtc_needs_modeset()`, `intel_atomic_get_digital_connector_state()`, and `intel_atomic_get_crtc_state()`. It declares CRTC and atomic state lifetime helpers `intel_crtc_duplicate_state()`, `intel_crtc_destroy_state()`, `intel_crtc_free_hw_state()`, `intel_atomic_state_alloc()`, `intel_atomic_state_free()`, and `intel_atomic_state_clear()`.

## Control Flow

The header has no runtime control flow. DRM object function tables and Intel display code call the declared helpers during atomic property operations, state duplication/destruction, atomic check, internal sanitize transactions, and state cleanup.

## State And Persistence Behavior

No state is stored in the header. The implementation manages connector state fields, CRTC state snapshots, color blob references, DP tunnel references, and Intel atomic state global-object arrays. The declarations define the ownership boundary for those operations.

## Dependencies And Integration Points

The header depends on `<linux/types.h>` and forward declarations, keeping dependencies low for many display files. It integrates with DRM atomic core while exposing Intel-specific typed state (`struct intel_atomic_state`, `struct intel_crtc_state`, and `struct intel_digital_connector_state`).

## Risks And Edge Cases

The header returns raw DRM state pointers for duplicate/allocation functions and Intel typed pointers for accessors, so call sites must use the right conversion and error handling. Any new Intel state field requiring reference management must be handled in the C implementation without changing this API. Broad inclusion means signature changes have a large compile-time blast radius.

## Test Signals

Build coverage across display objects, connector property tests, atomic state allocation/clear/free tests, CRTC duplicate/destroy lifetime checks, and static analysis for `ERR_PTR` handling on typed getters are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_atomic.h -->
