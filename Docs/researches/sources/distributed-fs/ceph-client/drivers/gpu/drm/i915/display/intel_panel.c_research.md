# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_panel.c

Purpose: centralizes embedded panel fixed-mode management, panel mode validation/configuration, DRRS/VRR fixed-mode selection, EDID/VBT/current-mode fixed-mode ingestion, panel/backlight lifetime, connector detection, and DRM panel follower preparation.

Important functions: `intel_panel_use_ssc()`, `intel_panel_preferred_fixed_mode()`, `intel_panel_fixed_mode()`, `intel_panel_downclock_mode()`, `intel_panel_highest_mode()`, `intel_panel_get_modes()`, `intel_panel_compute_config()`, `intel_panel_add_edid_fixed_modes()`, VBT/current fixed-mode adders, `intel_panel_detect()`, `intel_panel_mode_valid()`, `intel_panel_init_alloc()`, `intel_panel_init()`, `intel_panel_fini()`, `intel_panel_register()/unregister()`, and `intel_panel_prepare()/unprepare()`.

Control flow: initialization seeds VBT defaults and fixed mode list, then later stores fixed EDID, initializes backlight functions, and disables DRRS if no matching alternate fixed modes exist. EDID modes are reduced to preferred and optional alternate fixed modes; VBT/current modes are duplicated and added as preferred driver modes. Compute config chooses the best fixed mode for requested refresh, rejects non-VRR refresh mismatches beyond 1 Hz, copies fixed timings, and for VRR adjusts `vtotal` to match requested refresh. Registration creates a backlight device and, for eDP/DSI, allocates/registers a DRM panel once the connector kdev exists, then syncs already-enabled panel state.

State and persistence: `connector->panel` owns fixed EDID, fixed mode list, VBT-derived panel fields, backlight state, and optional `drm_panel *base`. Probed EDID modes are moved/destroyed after fixed-mode extraction.

Dependencies/integration: integrates with DRM mode lists, EDID helpers, backlight, VBT/BIOS parsing, quirks, DRRS, VRR, connector sysfs/kdev lifecycle, ACPI fwnodes, and DRM panel follower notifications.

Risks/test signals: important risks are mode list ownership, fixed EDID lifetime, VRR vtotal math, 1 Hz tolerance behavior, DRRS detection, panel registration after kdev creation, and prepare sync for BIOS-enabled panels. Test eDP/DSI/LVDS connectors with EDID preferred/alternate modes, VBT fallback, current BIOS mode fallback, VRR refresh requests, DRRS downclock modes, backlight registration failure, late_register panel sync, and unregister/fini cleanup.
