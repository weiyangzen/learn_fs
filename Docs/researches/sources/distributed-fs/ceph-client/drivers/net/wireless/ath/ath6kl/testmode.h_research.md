<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.h

## Purpose
`testmode.h` provides conditional declarations for ath6kl nl80211 testmode support. It lets the rest of the driver call testmode hooks regardless of whether `CONFIG_NL80211_TESTMODE` is enabled.

## Important APIs, Types, And Functions
When testmode is enabled, it declares `ath6kl_tm_rx_event()` and `ath6kl_tm_cmd()`. When disabled, it supplies static inline no-op replacements: RX events are dropped and commands return success.

## Control Flow
The header has compile-time control flow. Enabled builds route calls to `testmode.c`; disabled builds compile out behavior without adding preprocessor checks to callers.

## State And Persistence
No state is stored. The only behavioral persistence is build configuration: disabled testmode silently discards events and treats commands as no-ops.

## Dependencies And Integration Points
It includes `core.h` for `struct ath6kl` and relies on cfg80211 types from surrounding declarations. `cfg80211.c` or related registration code can point testmode callbacks at `ath6kl_tm_cmd()` only when enabled, while WMI event handling can call `ath6kl_tm_rx_event()` unconditionally.

## Risks
Returning zero from the disabled `ath6kl_tm_cmd()` stub can hide accidental command use in builds without testmode support if the callback is reachable. Call sites should ensure userspace cannot invoke a disabled testmode op, or return `-EOPNOTSUPP` at registration boundaries.

## Test Signals
Build tests should cover both `CONFIG_NL80211_TESTMODE=y` and disabled configurations. Runtime tests in disabled builds should verify no testmode callback is exposed to userspace or that no-op behavior is intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.h -->
