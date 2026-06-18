# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-qcom-spm.c

Purpose: registers Qualcomm SPM-backed ARM cpuidle states for CPUs with `qcom,saw` power controllers, using SCM warm boot setup and SPM low-power mode programming.

Important APIs and functions: `qcom_pm_collapse()` calls `qcom_scm_cpu_power_down(QCOM_SCM_CPU_PWR_DOWN_L2_ON)` and returns failure if the CPU did not power down. `qcom_cpu_spc()` programs SPM `PM_SLEEP_MODE_SPC`, calls `cpu_suspend()`, then resets SPM mode to standby. `spm_enter_idle_state()` wraps that path in `CPU_PM_CPU_IDLE_ENTER_PARAM()`. `spm_cpuidle_register()` finds a CPU's `qcom,saw` phandle, obtains the SPM platform device and drvdata, copies a template driver with a per-CPU cpumask, parses DT idle states compatible with `qcom,idle-state-spc`, and registers cpuidle. Probe verifies SCM availability, sets warm boot address to `cpu_resume_arm`, and registers each present CPU that has SPM.

Control flow and state: each registered CPU gets a devm-allocated `cpuidle_qcom_spm_data` containing the copied driver and SPM pointer. The init function registers a platform driver and only creates the synthetic platform device if at least one available CPU SAW node exists.

Dependencies and integration points: depends on Qualcomm SCM, `soc/qcom/spm` driver data, CPU DT `qcom,saw` phandles, DT idle-state parsing, ARM suspend/resume, CPU PM notifiers, and cpuidle core.

Risks and test signals: risks include partial registration continuing after per-CPU failures, no unregister path for successfully registered per-CPU drivers, dependence on SCM warm boot address setup before any idle entry, SPM mode reset being required to avoid accidental powerdown from generic WFI, and probe deferral until SCM is available. Test signals include SCM warm boot setup success, SPM drvdata present for SAW nodes, per-CPU cpuidle drivers with parsed SPC states, SPM mode returning to standby after idle, and power collapse returning through CPU resume on wake.
