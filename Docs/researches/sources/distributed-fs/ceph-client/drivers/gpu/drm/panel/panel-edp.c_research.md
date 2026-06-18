<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-edp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-edp.c

### Purpose

`panel-edp.c` is the generic DRM driver for simple embedded DisplayPort panels. It covers both statically described eDP panels and generic `edp-panel` devices discovered through EDID over AUX/DDC. The file owns eDP power sequencing delays, HPD waiting, runtime PM based prepare/unprepare, EDID mode enumeration, fixed-mode/timing fallbacks, DP AUX backlight registration, debugfs reporting of detected panel identity, and a large table of known EDID panel IDs mapped to safe delay profiles.

### Important APIs, types, and functions

`struct panel_delay` describes eDP timing requirements such as HPD reliability, HPD absent fallback, powered-on-to-enable, prepare-to-enable, enable, disable, and unprepare delays. `struct panel_desc` stores hard-coded modes or timings, bpc, size, and delays. `struct edp_panel_entry` maps `drm_edid_ident` values to delay profiles and optional EDID mode overrides. `struct panel_edp` stores DRM panel state, HPD/no-HPD flags, timestamps, descriptor, regulator, DDC or AUX handles, GPIOs, detected panel entry, cached EDID, override mode, and orientation.

Core functions include `panel_edp_get_modes()`, `panel_edp_get_non_edid_modes()`, `panel_edp_prepare_once()`, `panel_edp_resume()`, `panel_edp_suspend()`, `panel_edp_prepare()`, `panel_edp_enable()`, `panel_edp_disable()`, `panel_edp_unprepare()`, `panel_edp_parse_panel_timing_node()`, `generic_edp_panel_probe()`, `find_edp_panel()`, `panel_edp_probe()`, `panel_edp_remove()`, and `panel_edp_shutdown()`. Registration uses both a `platform_driver` and a `dp_aux_ep_driver`.

### Control flow

Probe allocates a panel, records the descriptor and optional AUX endpoint, reads `no-hpd`, HPD GPIO, power regulator, enable GPIO, orientation, and DDC source, parses a `panel-timing` override when applicable, initializes backlight handling, enables runtime PM/autosuspend, and either uses fixed descriptor data or powers the generic panel briefly to read EDID and infer delay data. Generic EDID probing reads `hpd-reliable-delay-ms` and `hpd-absent-delay-ms`, powers the panel via runtime resume, reads the EDID base block, finds a known entry, or falls back to conservative timings.

`prepare()` is runtime-PM get; resume calls `panel_edp_prepare_once()` up to five times on HPD timeout. That function enforces the previous unprepare delay, enables the supply, asserts enable GPIO, powers DPCD, waits for HPD reliability/absence timing, optionally polls HPD through GPIO or AUX, and records prepare and power-on timestamps. `enable()` enforces fixed enable, prepare-to-enable, and powered-on-to-enable delays before backlight use. `get_modes()` reads EDID if DDC is available, adds EDID or override EDID modes unless hard-coded modes exist, then adds fixed timings/modes when present.

### State and persistence behavior

The driver persists timestamp state across lifecycle calls to enforce minimum power-cycle intervals. Runtime PM keeps slow power operations off the direct panel callback path and autosuspends after transient EDID reads. `drm_edid` is cached after the first read. `detected_panel` records known, hardcoded, or unknown/conservative detection state and is exposed through debugfs. `override_mode` is populated only if a device-tree timing fits descriptor bounds. No user data is persisted; all state is per-device kernel memory.

### Dependencies

Dependencies include DRM panel/mode/EDID helpers, DP AUX helpers, `drm_dp_dpcd_set_powered()`, DP AUX bus endpoint registration, Linux runtime PM, debugfs, regulators, GPIOs, I2C adapters, OF display timing parsing, `readx_poll_timeout()`, and videomode conversion. The driver is tightly coupled to DT bindings for simple eDP panels and to EDID identity helpers.

### Integration points

Static compatibles in `platform_of_match` select hard-coded panel descriptors. The generic `edp-panel` compatible is only supported through the DP AUX bus path, while static panels can be platform devices. DDC can come from `ddc-i2c-bus` or AUX. DP AUX backlight registration is attempted when no backlight was provided and AUX exists. Debugfs exposes `detected_panel`, and connector setup receives EDID modes, fallback modes, bpc, size, and orientation.

### Risks

Power sequencing is the main risk: inaccurate delay table entries can cause intermittent panel bring-up, backlight-before-video artifacts, or HPD timeouts. Generic unknown panels fall back to conservative delays, which is safe but slow and intentionally noisy. EDID reads require temporarily powering the panel, so runtime PM and DDC/AUX lifetime ordering must be correct. The known-panel table must be sorted by vendor and product ID for maintainability, and duplicate panel IDs are resolved with identity matching first. `panel_edp_prepare()` must balance runtime PM get/put paths on errors. Hard-coded modes and EDID modes are deliberately not both exposed as preferred modes.

### Test signals

Test static-panel probe, generic `edp-panel` AUX probe, EDID detection for known and unknown IDs, HPD GPIO and AUX HPD paths, `no-hpd` behavior, retry-on-timeout, runtime autosuspend after mode reads, DP AUX backlight registration, debugfs `detected_panel`, device-tree timing override validation, suspend/resume through runtime and system PM, and connector mode lists with EDID-only, fixed-only, and override-EDID cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-edp.c -->
