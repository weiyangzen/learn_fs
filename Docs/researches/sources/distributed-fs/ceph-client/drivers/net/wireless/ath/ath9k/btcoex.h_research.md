# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.h

Purpose: Declares ath9k Bluetooth coexistence constants, scheme/stomp enums, MCI/AIC/coex hardware state structures, and hardware coexistence APIs.

Important APIs/types: GPIO constants describe AR9280 and AR9300 WLAN-active, BT-active, and BT-priority pins. Timing/duty-cycle thresholds cover default BT period, duty cycle, scan duty cycle, BMISS threshold, priority counters, RX wait, FTP stomp threshold, and max TX power limits. `enum ath_stomp_type` selects WLAN aggressiveness toward BT traffic. `enum ath_btcoex_scheme` selects none, 2-wire, 3-wire, or MCI. `struct ath9k_hw_mci` tracks MCI interrupts, GPM/scheduler buffers, WLAN channel bitmaps, calibration sequence, BT version/state, FTP stomp, concurrent TX, and recovery timestamp. `struct ath9k_hw_aic` stores antenna interference cancellation state and SRAM image. `struct ath_btcoex_hw` aggregates scheme, MCI/AIC, GPIO pins, cached coex register settings, weight arrays, and per-stomp TX priority.

Control flow: This header supplies the state layout consumed by `btcoex.c` and other ath9k MCI/AIC policy files. Callers initialize scheme and hardware state, choose 2-wire/3-wire/MCI init, update weights or stomp, then enable/disable coexistence around runtime policy decisions.

State/persistence: All persistent coexistence policy and hardware shadow registers are in `struct ath_btcoex_hw` under `struct ath_hw`. The header does not allocate or own memory, but its `gpm_buf` pointer and channel arrays are long-lived MCI state.

Dependencies/integration: Includes `hw.h`, uses AR9300 weight dimensions, ATH AIC channel count, and exported functions implemented in `btcoex.c`.

Risks: Enum ordering is ABI-like within the driver because weight arrays are indexed by `enum ath_stomp_type`. Structure fields are hardware-policy coupled; accidental reinitialization can lose MCI calibration or BT version state. No bounds helpers are declared for stomp indexes.

Test signals: Compile all BT coexistence configurations, validate MCI initialization state defaults, confirm stomp arrays have `ATH_BTCOEX_STOMP_MAX` entries, and verify feature-guarded call sites use declared APIs consistently.
