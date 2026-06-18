# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/sysfs.c

Purpose: Exposes selected ath5k ANI tuning and limit values through a device sysfs attribute group named `ani`.

Important APIs and functions: Macros `SIMPLE_SHOW_STORE()` and `SIMPLE_SHOW()` generate sysfs show/store handlers. Writable attributes include `ani_mode`, `noise_immunity_level`, `spur_level`, `firstep_level`, `ofdm_weak_signal_detection`, and `cck_weak_signal_detection`; read-only attributes include maximum noise immunity, spur, and firstep levels. `ath5k_sysfs_register()` creates the group and `ath5k_sysfs_unregister()` removes it.

Control flow: A show handler obtains `struct ieee80211_hw` via `dev_get_drvdata()`, resolves `struct ath5k_hw`, and emits the current ANI value. A store handler parses decimal input with `kstrtoint()` and calls the corresponding ANI setter, returning the input byte count on success. Registration creates the `ani` group under the device kobject and logs failure through `ATH5K_ERR`.

State and persistence: Mutates in-memory ANI state and hardware ANI settings through `ath5k_ani_*` setters. Sysfs changes are runtime-only and do not persist across reloads or reset unless higher-level ANI initialization reuses the state.

Dependencies and integration points: Depends on Linux device/sysfs APIs, mac80211 device private data, ANI state in `ah->ani_state`, ANI setters from ath5k, and constants such as `ATH5K_ANI_MAX_NOISE_IMM_LVL`. It is integrated during device registration/teardown.

Risks: Store handlers do not validate ranges themselves, relying on ANI setters to clamp or reject values. Concurrent sysfs writes and driver reset/ANI recalibration can race at the semantic level. Exposing low-level tuning can degrade RF performance if users write unsuitable values.

Test signals: Register/unregister group on probe/remove, read each attribute, write valid and invalid integers, verify setters are invoked and hardware behavior changes, confirm parse errors return negative status, and ensure group removal prevents use-after-free during teardown.
