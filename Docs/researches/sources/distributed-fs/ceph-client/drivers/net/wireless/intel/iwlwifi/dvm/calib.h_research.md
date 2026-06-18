# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/calib.h

Purpose: Small public header for DVM runtime calibration entry points. It exposes sensitivity and chain-noise calibration routines to the RX/statistics and device lifecycle code without exposing the implementation details in `calib.c`.

Important APIs and types: Declares `iwl_chain_noise_calibration()`, `iwl_sensitivity_calibration()`, `iwl_init_sensitivity()`, and `iwl_reset_run_time_calib()`. It includes `dev.h` for `struct iwl_priv` and calibration state, and `commands.h` for firmware calibration and sensitivity command definitions.

Control flow: Callers initialize sensitivity after firmware/device setup with `iwl_init_sensitivity()`, reset runtime calibration state with `iwl_reset_run_time_calib()` around association or firmware restart boundaries, and invoke `iwl_sensitivity_calibration()` plus `iwl_chain_noise_calibration()` when firmware statistics notifications provide the beacon/interference data needed by the algorithms.

State and persistence: The header owns no state directly. Its functions mutate `priv->sensitivity_data`, `priv->chain_noise_data`, cached sensitivity command tables, and firmware calibration state through the implementation in `calib.c`.

Dependencies and integration points: Used by DVM RX/statistics handling, association/RXON paths, and firmware initialization code. It binds DVM private state to firmware command structures such as `struct iwl_sensitivity_cmd`, `struct iwl_enhance_sensitivity_cmd`, and `struct iwl_calib_chain_noise_gain_cmd`.

Risks: Because this header hides no locking contract in the prototypes, callers must rely on the implementation to take `priv->statistics.lock` where needed and must call these routines only when firmware statistics and association state are meaningful. Prototype drift would break calibration invocation across DVM files.

Test signals: Compile coverage for every caller, runtime coverage for association setup, statistics-notification processing, firmware restart/runtime calibration reset, and builds with calibration-related firmware command structures changed.
