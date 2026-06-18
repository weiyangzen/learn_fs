# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/thermal.h

Purpose: Declares ath11k thermal constants, per-radio thermal state, and the public thermal registration/control/event API with stubs when the kernel thermal framework is unavailable.

Important APIs, types, and constants: Constants define thermal mitigation low/high marks (`-100` and `150` Celsius), maximum throttle state (`100`), default duty cycle (`100`), hwmon name length, and WMI temperature synchronization timeout (`5 * HZ`). `struct ath11k_thermal` stores a cooling device pointer, completion, cached throttle state, and cached temperature. The enabled declarations are `ath11k_thermal_register()`, `ath11k_thermal_unregister()`, `ath11k_thermal_set_throttling()`, and `ath11k_thermal_event_temperature()`.

Control flow: Core code calls register/unregister during device lifecycle, calls `ath11k_thermal_set_throttling()` when radio state changes or thermal policy updates, and WMI event handling calls `ath11k_thermal_event_temperature()` when firmware returns a temperature. If `CONFIG_THERMAL` is not reachable, all functions compile to no-ops or success-returning stubs.

State and persistence behavior: The structure is embedded in the per-radio `struct ath11k`, so its lifetime follows the radio object. Comments specify `throttle_state` is protected by `conf_mutex` and `temperature` by `data_lock`. The completion is used only for synchronous firmware temperature reads and must be initialized by core setup before use.

Dependencies and integration points: The header depends on Linux thermal device and completion types, ath11k core types, and the `IS_REACHABLE(CONFIG_THERMAL)` build condition. It forms the boundary between the main driver, WMI thermal events, Linux thermal cooling framework, and optional hwmon exposure implemented in `thermal.c`.

Risks and edge cases: Disabled-thermal stubs return success for throttling, so callers must not assume firmware mitigation was installed unless thermal support is built and the radio is ON. Constants are firmware policy inputs; changing low/high marks or duty-cycle defaults can alter mitigation behavior for all radios. Locking comments must stay synchronized with implementation if new thermal fields are added.

Test signals: Compile-test with thermal enabled, modular, and disabled. Runtime tests should verify `struct ath11k_thermal` initialization before register, completion behavior for temperature reads, lockdep expectations around throttle state, and that disabled-thermal builds do not expose cooling/hwmon devices while allowing the rest of ath11k to load.
