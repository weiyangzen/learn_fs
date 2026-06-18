# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.h

Purpose: declares power-related helper interfaces for ABM firmware configuration, PSR/Replay calculations, eDP-only checks, DSC/PSR-SU validation, and custom backlight capability reporting.

Important APIs/types: `enum abm_defines` defines four ABM levels and four config sets. `struct dmcu_iram_parameters` carries caller backlight LUT, ramping override, min backlight, and ABM set. Public functions mirror the implementation in `power_helpers.c`, including `dmcu_load_iram`, `dmub_init_abm_config`, Replay coasting/frame-skip helpers, PSR config helpers, `fill_custom_backlight_caps`, and mode-conversion declarations `change_replay_to_psr` / `change_psr_to_replay`.

Control flow role: this header is the contract used by DC/link management code to invoke firmware-table generation and PSR/Replay helper logic.

State and persistence: callers pass mutable `dc_link`, `psr_config`, `replay_config`, and backlight caps structures that the implementation updates in place.

Dependencies and integration: includes DMCU, ABM, and core DC type headers. It forward-declares `struct resource_pool` to avoid broader inclusion in consumers.

Risks: `dmcu_iram_parameters` has raw pointer plus size with no static enforcement; callers must guarantee the LUT remains valid and non-empty. Function declarations for `change_replay_to_psr` and `change_psr_to_replay` require matching definitions elsewhere.

Test signals: compile consumers against this header, validate null/resource-pool behavior in implementation, LUT parameter validation, Replay table updates, PSR config updates, and link mode conversion symbol resolution.
