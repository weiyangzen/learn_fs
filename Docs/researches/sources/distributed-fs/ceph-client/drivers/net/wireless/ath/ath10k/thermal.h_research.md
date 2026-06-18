# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.h

Purpose: Defines ath10k thermal throttling constants, runtime thermal state, and feature-gated thermal APIs.

Important APIs and types: Defines quiet period defaults/minimum/start offset, hwmon name length, WMI sync timeout, max throttle percentage, `struct ath10k_thermal`, and declarations or no-op stubs for thermal register/unregister/event/throttling functions.

Control flow, state, and persistence: The header owns no flow. `struct ath10k_thermal` state is split between `conf_mutex`-protected throttle/quiet settings and `data_lock`-protected temperature.

Dependencies and integration points: Depends on Linux thermal reachability and ath10k core state. It is embedded in `struct ath10k` and used by WMI event handlers and device registration paths.

Risks: Stubbed disabled builds silently skip thermal support. Locking comments are part of the API contract; violating them can race sysfs, WMI events, and cooling callbacks.

Test signals: Compile with thermal enabled and disabled, validate structure initialization, WMI temperature event dispatch, and no-op behavior in disabled builds.
