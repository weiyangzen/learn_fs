# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.h

## Purpose

`wow.h` is the public ath12k Wake-on-WLAN interface inside the driver. It defines driver-local WoW state, retry/pattern constants, pattern conversion helper types, PM-enabled function prototypes, and PM-disabled no-op stubs.

## Important APIs, Types, And Constants

- `ATH12K_WOW_RETRY_NUM` and `ATH12K_WOW_RETRY_WAIT_MS` bound firmware WoW-enable retries.
- `ATH12K_WOW_PATTERNS` is the advertised pattern count used by `ar->wow.max_num_patterns`.
- `struct ath12k_wow` contains `max_num_patterns`, `wakeup_completed`, and persistent `wiphy_wowlan_support`.
- `struct ath12k_pkt_pattern` stores converted pattern bytes, bytemask, length, and packet offset.
- `struct rfc1042_hdr` provides the packed SNAP/RFC1042 layout used by Ethernet-to-802.11 pattern conversion.
- PM prototypes cover init, suspend, resume, device wakeup enable, firmware WoW enable, and firmware wakeup.
- PM-disabled stubs return success for init/enable/wakeup to keep non-PM builds linkable.

## Control Flow

`mac.c` calls `ath12k_wow_init()` during setup, while hardware ops use `ath12k_wow_op_suspend()`, `ath12k_wow_op_resume()`, and `ath12k_wow_op_set_wakeup()` when PM support is compiled. `wow.c` uses the constants and local structures for retry handling and pattern conversion. Without `CONFIG_PM`, the inline stubs prevent firmware programming while preserving call-site compilation.

## State And Persistence Behavior

`struct ath12k_wow` is embedded in the ath12k radio object and must outlive `wiphy->wowlan`, which points to its `wowlan_support` member. `wakeup_completed` is reused across wakeup handshakes. `ath12k_pkt_pattern` instances are transient stack buffers.

## Dependencies And Integration Points

The header depends on WMI pattern-size constants, cfg80211/mac80211 types, and ath12k core structures through including contexts. It integrates with ath12k MAC setup, PM callbacks, and the WoW implementation.

## Risks

Changing WMI pattern limits changes stack buffer size and conversion constraints. PM-disabled stubs can hide functional absence if callers treat success as real firmware programming. `wiphy->wowlan` lifetime depends on `ar->wow` remaining stable. Retry constants encode firmware timing assumptions.

## Test Signals

PM-enabled builds should expose and exercise real callbacks. PM-disabled builds should compile with stubs and not expose operational WoW. Static checks should ensure WMI pattern-limit changes are reflected in `ath12k_pkt_pattern` and native-WiFi offset calculations.
