# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/cnqf.c

Purpose: `cnqf.c` implements PMF CnQF dynamic slider behavior. It transitions among quiet, balanced, performance, and turbo modes using AC/DC-specific firmware tables, platform-profile state, power-source state, and averaged socket power over transition windows.

Important APIs, types, and functions: static `struct cnqf_config config_store` stores per-source transition parameters and mode settings. `amd_pmf_load_defaults_cnqf()` reads AC/DC dynamic slider definitions through `apmf_get_dyn_slider_def_ac/dc()`. `amd_pmf_update_mode_set()`, `amd_pmf_update_trans_data()`, and `amd_pmf_update_power_threshold()` populate the runtime table. `amd_pmf_trans_cnqf()` is the metrics-driven transition engine. `cnqf_enable` sysfs attribute toggles runtime CnQF enablement through `cnqf_feature_attribute_group`.

Control flow: init loads defaults for supported AC/DC functions, starts metrics-table work, marks CnQF supported, initializes enablement from firmware flags, and applies balanced-mode limits if enabled and the platform profile is balanced. Each metrics tick chooses the active power source, refuses to enforce CnQF if the user-selected profile is not balanced, accumulates socket power over each transition time constant, sets priority booleans when averages cross thresholds, and applies the first/highest-priority target mode.

State and persistence: CnQF runtime state includes static global config, `dev->cnqf_supported`, `dev->cnqf_enabled`, metrics work, and firmware-applied SMU/fan settings. The sysfs toggle affects runtime only.

Dependencies and integration points: depends on ACPI dynamic slider functions, platform profile support through `is_pprof_balanced()`, PMF metrics work, power-supply source detection, SMU command transport, and optional fan-index ACPI method. Sysfs visibility is controlled by `cnqf_feature_is_visible()`.

Risks: global `config_store` prevents safe multi-device use. `amd_pmf_check_flags()` does not check ACPI getter return status before using `out.flags`. Time/power accumulators are 32-bit and can overflow under long intervals or large power values. Power-source mapping assumes `APMF_FUNC_DYN_SLIDER_AC + i` matches AC then DC function IDs. Send-command failures are ignored during mode application, allowing partial policy updates.

Test signals: `cnqf_enable` visibility only after supported init, AC/DC table loading, default enablement from flags, profile-balanced gating, transitions through all six priority directions, power-source switching, fallback to static slider when disabled, and work cancellation on deinit.
