# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.c

### Purpose
`intel_gt_pm_debugfs.c` registers per-GT debugfs files for forcewake, RC/DRPC state, frequency information, LLC/eDRAM data, RPS boost state, and performance limit reasons.

### Important APIs, Types, And Functions
Public functions are `intel_gt_pm_debugfs_register()`, `intel_gt_pm_frequency_dump()`, `intel_gt_pm_debugfs_forcewake_user_open()`, and `intel_gt_pm_debugfs_forcewake_user_release()`. Debugfs show paths include `fw_domains_show()`, `drpc_show()` with ILK/VLV/Gen6/MTL variants, `frequency_show()`, `llc_show()`, `rps_boost_show()`, and perf-limit get/clear callbacks.

### Control Flow
Opening `forcewake_user` increments `user_wakeref`, gets a GT PM ref, and takes user forcewake on Gen6+. Release reverses the operation. DRPC show obtains runtime PM and chooses platform-specific register dumps. Frequency and LLC dumps read RPS, pcode, IOSF, or legacy frequency registers. RPS boost prints software and hardware autotuning state. Perf limit reasons read or clear the log bits of the GT perf-limit register.

### State, Persistence, And Dependencies
State read includes uncore forcewake counters, RC6 residency, RPS frequencies/thresholds, power-gate status, pcode frequency tables, `gt->awake`, perf-limit log/status bits, and `gt->user_wakeref`. Dependencies include debugfs, seq_file, runtime PM, uncore, pcode, IOSF sideband, RPS/RC6/LLC helpers, and GT register definitions.

### Integration Points
Registered under each GT debugfs root by core GT debugfs. Upper-level non-GT debugfs code can call the forcewake helpers. The files are support and CI diagnostics for PM and frequency behavior.

### Risks
Debugfs reads touch live power-management registers and must hold runtime PM/forcewake where needed. `forcewake_user` can intentionally pin the GT awake. Some frequency data is platform-specific and may be unavailable or hidden when GuC SLPC replaces legacy RPS.

### Test Signals
Reading all PM debugfs files across ILK, VLV/CHV, Gen6+, Gen11+, MTL, SLPC and non-SLPC systems; holding/releasing forcewake_user across suspend; clearing perf limit log bits; and checking conditional file visibility are useful signals.
