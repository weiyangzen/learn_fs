# sources/distributed-fs/ceph-client/drivers/regulator/db8500-prcmu.c

Purpose: Provides DB8500 PRCMU-backed regulators and power-domain switches for the UX500 platform. It represents always-on/platform-controlled rails and EPOD power domains as regulator framework devices.

Important APIs, types, and functions: The normal regulator ops are `db8500_regulator_enable()`, `db8500_regulator_disable()`, and `db8500_regulator_is_enabled()`, which update `dbx500_regulator_info` state and the global power-state active count. EPOD switch helpers `enable_epod()` and `disable_epod()` coordinate on/off and RAM-retention states. Switch regulator ops call these helpers through `db8500_regulator_switch_enable()`, `db8500_regulator_switch_disable()`, and `db8500_regulator_switch_is_enabled()`. `dbx500_regulator_info[]` is the static descriptor table for rails and EPOD switches.

Control flow: Probe obtains optional platform init data, iterates all DB8500 regulator descriptors, fills `regulator_config` with per-descriptor driver data and optional init constraints, and registers each regulator. It then initializes optional debugfs support through `ux500_regulator_debug_init()`. Remove only tears down debugfs. The driver registers at `arch_initcall`, reflecting early platform power dependency.

State and persistence: Per-regulator `is_enabled` flags are stored in the static descriptor array. Global EPOD state is tracked by `epod_on[]` and `epod_ramret[]` arrays so on and RAM-retention views of the same EPOD are coordinated. Non-switch regulators update a shared active power-state reference count unless flagged `exclude_from_power_state`. The actual EPOD state persists in PRCMU firmware/hardware through `prcmu_set_epod()`.

Dependencies and integration points: It depends on DB8500 regulator IDs, PRCMU MFD APIs, EPOD constants, regulator core, OF match names embedded in descriptors, and shared DBX500 debug/power-state helpers from `dbx500-prcmu.c`.

Risks and test signals: Test balanced enable/disable calls, `exclude_from_power_state` behavior for VSMPS2, EPOD on versus RAM-retention interactions, default enabled ESRAM switches, PRCMU call failure propagation, debugfs init/remove, and platform init-data indexing. Static global state means repeated bind/unbind or multiple platform instances would be unsafe; this matches the SoC-global design but should be considered in tests.
