# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pm.c

Purpose: implements AIE2-specific power-mode policy on top of generic AMD XDNA runtime PM. It sets DPM levels through device-private SMU operations, toggles firmware runtime clock-gating configuration, initializes default power state, and handles user-requested power modes.

Important APIs/functions: `aie2_pm_init()` discovers the highest DPM level from the device clock table, sets the initial DPM, enables clock gating, and records default mode. On resume it restores previous `dpm_level` and `clk_gating`. `aie2_pm_set_dpm()` resumes the device with `amdxdna_pm_resume_get_locked()`, calls `ndev->priv->hw_ops.set_dpm()`, updates `ndev->dpm_level`, and drops runtime PM. `aie2_pm_set_mode()` validates and applies `POWER_MODE_TURBO`, `POWER_MODE_HIGH`, or `POWER_MODE_DEFAULT`, including a no-active-context guard for turbo mode.

Control flow: user `DRM_AMDXDNA_SET_POWER_MODE` reaches this file through `aie2_set_state()`. XRS can also adjust the default DPM level when resource requirements change. DPM changes call SMU helper implementations selected by device-generation register files.

State and persistence: updates `pw_mode`, `dpm_level`, `dft_dpm_level`, `max_dpm_level`, and `clk_gating` in `amdxdna_dev_hdl`. State persists only while the driver/device handle is alive and is restored on resume.

Dependencies: relies on `aie2_runtime_cfg()` for firmware clock-gating controls, `amdxdna_pm` runtime PM helpers, and `aie2_smu.c` through `hw_ops.set_dpm`.

Risks: `aie2_pm_set_mode()` assumes caller holds `dev_lock`; failing to hold it risks racing context creation and turbo-mode checks. Runtime PM lock dropping in `amdxdna_pm_resume_get_locked()` must not be used from contexts that cannot release `dev_lock`.

Test signals: power-mode ioctl coverage, turbo rejection with active contexts, resume restore of DPM/clock gating, SMU command failure injection, and concurrent context creation while changing modes.
