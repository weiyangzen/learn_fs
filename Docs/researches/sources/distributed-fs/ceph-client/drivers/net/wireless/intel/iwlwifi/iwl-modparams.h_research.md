# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-modparams.h

Purpose: Defines global iwlwifi module-parameter state and small policy helpers that gate advertised capabilities and RX buffer sizing.

Important APIs and types: `struct iwl_mod_params` stores flags for software crypto, HT/VHT/HE/EHT disablement, A-MSDU size, firmware restart, Bluetooth coexistence, LEDs, power save, NVM file override, U-APSD disablement, INI debug, and removal behavior. Enums define power levels, 11n disable bits, A-MSDU size values, and U-APSD disable bits. Inline helpers `iwl_enable_rx_ampdu()`, `iwl_enable_tx_ampdu()`, and `iwl_amsdu_size_to_rxb_size()` interpret the global parameters.

Control flow: Runtime code reads `iwlwifi_mod_params` to enable/disable aggregation, HT/VHT/HE/EHT capability advertising, firmware restart, and NVM loading. The A-MSDU helper validates supported receive-buffer sizes and falls back to 4K with an error log.

State and persistence: `iwlwifi_mod_params` is process-global module state configured at load/runtime via module parameters. It persists while the module is loaded and influences all devices.

Dependencies and integration points: Used by NVM parsing/capability construction, TX/RX aggregation setup, debug configuration, transport restart policy, and firmware/NVM file paths.

Risks: Global parameters affect every adapter. Invalid `amsdu_size` is tolerated with fallback, which can hide configuration mistakes. Disabling standards features changes cfg80211/mac80211 capability surfaces and can invalidate assumptions in tests.

Test signals: Module-load parameter parsing, HT aggregation enable/disable matrices, A-MSDU fallback logging, capability advertisement with `disable_11ac/11ax/11be`, and firmware restart disabled behavior.
