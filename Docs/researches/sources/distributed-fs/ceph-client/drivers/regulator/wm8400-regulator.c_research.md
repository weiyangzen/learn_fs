<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm8400-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/wm8400-regulator.c

Purpose: Registers WM8400 LDO1-4 and DCDC1-2 regulators and exposes an MFD helper for enabling software control of individual rails.

Important APIs and types: `regulators[]` defines four LDO descriptors with linear-range voltage maps and two DCDC descriptors with linear voltage selectors. LDO ops use standard regmap enable and voltage helpers. DCDC ops add `wm8400_dcdc_get_mode()`, `_set_mode()`, and `_get_optimum_mode()`. `wm8400_register_regulator()` prepares a platform device embedded in the parent `struct wm8400`.

Control flow: The MFD/platform init path calls `wm8400_register_regulator()` with init data for each rail. Platform probe recovers the parent `struct wm8400` with `container_of()`, registers the selected descriptor against the parent regmap, and stores the regulator device. Module init registers the platform driver at subsys init.

State and persistence: Software state is held by embedded platform devices in the parent MFD. Voltage, enable, active/sleep, and force-PWM state persist in WM8400 registers.

Dependencies and integration points: Depends on WM8400 private MFD structures, regmap, regulator init data, and platform-device registration from the MFD.

Risks: `wm8400_register_regulator()` does not range-check `reg` before indexing `wm8400->regulators`. DCDC standby/hibernate mode handling supports FAST/NORMAL/IDLE but not STANDBY in set mode. `get_mode()` returns zero on regmap read failure, which is not a regulator mode.

Test signals: Register each rail, duplicate registration returning `-EBUSY`, invalid index handling at callers, DCDC mode transitions, regmap bulk read failures, voltage selector boundaries, and module init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm8400-regulator.c -->
