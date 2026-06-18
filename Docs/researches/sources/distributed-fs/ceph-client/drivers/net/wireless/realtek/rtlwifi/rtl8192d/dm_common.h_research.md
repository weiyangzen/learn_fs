# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/dm_common.h

Purpose: Declares the shared RTL8192D dynamic-management constants, state enums, and exported function prototypes consumed by bus-specific drivers.

Important APIs/types: Defines DM disable bits (`HAL_DM_DIG_DISABLE`, `HAL_DM_HIPWR_DISABLE`), OFDM/CCK swing table sizes, DIG false-alarm thresholds, TX high-power levels, DM ownership modes, near-field thresholds, and enums for 1R CCA, RF save state, and software antenna switching. Exposes tx power tracking, false alarm, RSSI, DIG, EDCA turbo, and rate-adaptive-mask functions.

Control flow: The header has no runtime flow but describes the callable lifecycle: initialize DM, periodically collect false alarms and RSSI, run DIG/EDCA, and trigger thermal power tracking.

State and persistence: No storage by itself. Constants govern how `rtl_priv->dm`, `rtl_priv->dm_digtable`, and `rtl_priv->ra` are interpreted in `dm_common.c` and rtl8192de-specific DM.

Dependencies and integration: Included by rtl8192d common implementation and rtl8192de DM/hardware paths. Requires kernel bit macros and rtlwifi type declarations from prior includes.

Risks: Threshold values are hardware-tuned magic numbers. Header guard name and API naming are RTL92D-specific; changing constants affects power, sensitivity, and rate-control behavior across all users.

Test signals: Compile coverage across rtl8192d common and rtl8192de modules, plus runtime checks for DIG, EDCA, and power-tracking behavior.
