# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/auto-mode.c

Purpose: `auto-mode.c` implements PMF Auto Mode, a firmware-configured dynamic thermal/power policy that transitions among quiet, balanced, performance, and performance-on-lap modes based on averaged socket power and CQL notifications.

Important APIs, types, and functions: static `struct auto_mode_mode_config config_store` holds transition thresholds/timers and per-mode power/fan settings. `amd_pmf_load_defaults_auto_mode()` reads `struct apmf_auto_mode` through ACPI and populates config. `amd_pmf_trans_automode()` applies the transition algorithm on each metrics sample. `amd_pmf_set_automode()` sends SPL/FPPT/SPPT/SPPT_APU_ONLY/STT limits to SMU and optionally updates fan index through ACPI. Public functions include `amd_pmf_update_2_cql()`, `amd_pmf_reset_amt()`, `amd_pmf_handle_amt()`, `amd_pmf_init_auto_mode()`, and `amd_pmf_deinit_auto_mode()`.

Control flow: initialization loads ACPI defaults, sets initial mode to balanced, initializes moving-average history, and starts the PMF metrics delayed work. Each metrics tick computes a 3-sample moving average, updates per-transition timers depending on threshold direction, marks transitions applied/unapplied, then selects the first applied transition as highest priority and sends the target mode limits if the mode changed. CQL notifications can redirect the performance target between normal performance and on-lap performance.

State and persistence: Auto Mode state is global to the module through `config_store`; per-device history index and socket power samples live in `amd_pmf_dev`. SMU power limits and fan index are runtime firmware/device state. No persistent storage exists.

Dependencies and integration points: depends on ACPI `APMF_FUNC_AUTO_MODE`, PMF core metrics scheduling, SMU command transport, optional `APMF_FUNC_SET_FAN_IDX`, and static-slider fallback for reset. It integrates with `acpi.c` notify handling for AMT/CQL and with `core.c` metrics collection.

Risks: `config_store` is static global, so multiple PMF devices would conflict. `amd_pmf_load_defaults_auto_mode()` does not check the return from `apmf_get_auto_mode_def()`, risking zeroed or stale defaults. Several `amd_pmf_send_cmd()` calls ignore failures, so partial mode application is possible. Threshold calculations subtract deltas from power floors with unsigned arithmetic and can underflow if firmware provides inconsistent values.

Test signals: ACPI defaults load, initial balanced mode application on AMT enable, moving-average transitions at configured thresholds/time constants, CQL toggling performance-on-lap limits, fan index automatic/manual behavior, metrics work cancellation on deinit, and static-slider restoration on AMT reset.
