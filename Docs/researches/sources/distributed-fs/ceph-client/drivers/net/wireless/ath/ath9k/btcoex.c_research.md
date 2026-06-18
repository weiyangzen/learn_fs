# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.c

Purpose: Programs hardware Bluetooth coexistence for 2-wire, 3-wire, and MCI-capable ath9k chips, including GPIO routing, coexistence mode registers, WLAN/BT weight tables, enable/disable sequencing, and stomp policies.

Important APIs/functions: Exported entry points are `ath9k_hw_init_btcoex_hw()`, `ath9k_hw_btcoex_init_scheme()`, `ath9k_hw_btcoex_init_2wire()`, `ath9k_hw_btcoex_init_3wire()`, `ath9k_hw_btcoex_deinit()`, `ath9k_hw_btcoex_init_mci()`, `ath9k_hw_btcoex_set_weight()`, `ath9k_hw_btcoex_enable()`, `ath9k_hw_btcoex_disable()`, `ath9k_hw_btcoex_bt_stomp()`, and `ath9k_hw_btcoex_set_concur_txprio()`. Static weight tables encode AR9003 and MCI WLAN priorities for `ATH_BTCOEX_STOMP_*`.

Control flow: Scheme selection honors global `common->btcoex_enabled`, then picks MCI if available, otherwise 3-wire for AR9300+ or AR9285, and 2-wire for other AR9280+ parts. Init configures GPIO muxes and input requests. Hardware defaults build `bt_coex_mode`, `bt_coex_mode2`, and SoC mode3 fields. Enabling dispatches by scheme: 2-wire requests WLAN active output, 3-wire writes coex mode/weight registers and RX-clear GPIO output, and MCI writes MCI coex weights. Disabling clears `enabled`, resets MCI or legacy registers, and returns WLAN-active GPIO to output-low/simple output.

State/persistence: Persistent state lives in `ah->btcoex_hw`: scheme, GPIO numbers, cached register values, BT/WLAN weights, MCI state, AIC state, concurrency TX priority table, and `enabled`. Hardware state persists in GPIO mux/request ownership, AR_BT_COEX registers, AR_MCI weight registers, quiet/PCU fields, and pull-down/pull-up programming.

Dependencies/integration: Depends on silicon revision predicates, register macros, GPIO request/free helpers, MCI capability bits, debug logging, and higher-level BT coexistence policy code that chooses stomp type, duty cycle, scans, and antenna diversity.

Risks: Revision-specific GPIO and polarity choices are fragile. `ath9k_hw_btcoex_set_weight()` indexes by stomp type and assumes callers pass values below `ATH_BTCOEX_STOMP_MAX`. Concurrent TX priority bit insertion must match weight register layout. Deinit frees GPIOs unconditionally, so scheme initialization must have assigned valid pins. MCI and non-MCI disable paths intentionally differ.

Test signals: Exercise AR9280 2-wire, AR9285/AR9300 3-wire, AR9462/AR9565 MCI, global disable, enable/disable cycles, stomp all/low/none/audio/FTP policies, concurrent TX priority override, GPIO ownership cleanup, and Bluetooth/WLAN throughput or scan coexistence behavior.
