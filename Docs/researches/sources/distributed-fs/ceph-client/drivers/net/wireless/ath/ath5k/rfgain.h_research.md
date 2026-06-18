# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/rfgain.h

Purpose: Provides static RF gain initialization tables and gain-optimization ladders used by ath5k PHY/RF code to program analog gain behavior.

Important APIs and types: `struct ath5k_ini_rfgain` maps an RF gain register address to 5 GHz and 2 GHz values. Static tables `rfgain_5111`, `rfgain_5112`, `rfgain_2413`, `rfgain_2316`, `rfgain_5413`, and `rfgain_2425` provide mode-specific 64-entry gain defaults. `struct ath5k_gain_opt_step` stores adjustment parameters and resulting gain delta. `struct ath5k_gain_opt` stores a default step, count, and optimization ladder. `rfgain_opt_5111` and `rfgain_opt_5112` define dynamic gain adjustment steps for older RF chips. Macros define adjustment thresholds and `AR5K_GAIN_CHECK_ADJUST()`.

Control flow: The header itself is static data. Runtime code selects an initial gain table by RF chip and frequency band, writes gain registers, then uses the optimization ladder to move between gain steps when measured gain crosses low/high thresholds. The ladder parameters correspond to RF buffer fields such as PWD and mixgain controls plus PHY clip settings.

State and persistence: Owns immutable constants. Consumers maintain current gain measurements, low/high thresholds, selected step, and any pending RF bank edits. No durable persistence exists; values are re-applied during reset/PHY initialization.

Dependencies and integration points: Depends on RF gain register macros such as `AR5K_RF_GAIN()`, RF buffer field editing from `rfbuffer.h`, PHY calibration paths, channel band selection, and reset-time gain calibration in `reset.c`. It is most important for RF5111/RF5112 dynamic gain behavior and newer chips' initialization defaults.

Risks: Gain values are analog calibration constants; wrong table selection causes poor sensitivity, transmit quality, or unstable calibration. Optimization thresholds and step parameters are tuned for specific chip families and can regress fringe RF performance. Because tables are static and opaque, tests need hardware signal metrics rather than simple compile checks.

Test signals: Validate RX sensitivity, noise floor, transmit EVM/power, gain calibration convergence, 2 GHz versus 5 GHz table selection, reset-time reprogramming, dynamic gain step transitions under changing RSSI/noise, and no regressions on RF5111/RF5112 devices that use optimization ladders.
