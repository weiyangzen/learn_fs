# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Makefile

Purpose: maps DRM display helper Kconfig symbols to compiled objects for the display helper module/library.

Important entries: `obj-$(CONFIG_DRM_DISPLAY_DP_AUX_BUS) += drm_dp_aux_bus.o` builds the AUX endpoint bus separately. `drm_display_helper-y := drm_display_helper_mod.o` is the base helper object. Conditional additions include bridge connector, DP dual-mode/helper/MST, DP tunnel, DSC, HDCP, HDMI audio/CEC/notifier/helper/state helpers, SCDC, DP AUX chardev, and DP AUX CEC. `obj-$(CONFIG_DRM_DISPLAY_HELPER) += drm_display_helper.o` emits the final helper object/module.

Control flow: Kconfig determines composition; module init in `drm_display_helper_mod.c` initializes the DP AUX char device when compiled in.

State and persistence: build artifact composition only.

Dependencies and integration points: mirrors display `Kconfig` and internal headers such as `drm_dp_helper_internal.h`.

Risks: helper APIs are widely exported; missing objects under a selected config causes link errors. Keeping DP AUX bus outside the umbrella helper means users must select the bus explicitly.

Test signals: compile each config combination, verify exported symbols link for DRM drivers, and module load/unload with DP AUX char device enabled.
