# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.c

Purpose: builds the DMUB-backed ABM object and adapts the generic `abm_funcs` interface to LCD/eDP-specific DMUB ABM operations.

Important functions: `dmub_abm_create()` allocates a `struct dce_abm` only when `ctx->dc->caps.dmcub_support` is true. `dmub_abm_construct()` attaches the function table and DCE ABM register descriptors. Wrapper callbacks include init, level, current/target backlight, config, pause, save/restore, pipe selection, and PWM backlight level. `abm_feature_support()` gates operations to detected eDP panels.

Control flow: most callbacks first map the requested panel instance through `dc_get_edp_links()`. Supported LCD panels call into `dmub_abm_lcd.c`; unsupported panels return false or no-op success depending on the legacy ABM API expectation. `set_level` builds a panel mask across all supported eDP instances and applies one DMUB level command to that mask.

State and persistence: software state is `struct dce_abm` with base `abm`, register tables, and `dmcu_is_running=false`. Runtime ABM state is maintained by hardware registers and DMUB firmware. The wrapper disables DC idle optimizations before reading current/target backlight, preventing low-power state from hiding register access.

Dependencies and integration: depends on `abm.h`, `dce_abm.h`, `core_types`, `dc_get_edp_links`, DMUB command support, and the LCD command helpers. It integrates with DC resource construction as the ABM provider when DMCUB is available.

Risks: panel instance is treated as eDP enumeration order, so multi-eDP mapping correctness matters. Unsupported panel calls may return true for config, which can mask missing support. Destroy assumes a non-null pointer to a DMUB-created object. Test signals include DMCUB-cap gating, multi-eDP panel masks, backlight reads with idle optimizations disabled, unsupported panel behavior, and create/destroy lifecycle.
