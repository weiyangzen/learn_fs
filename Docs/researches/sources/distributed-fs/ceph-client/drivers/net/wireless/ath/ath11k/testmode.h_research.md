# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/testmode.h

Purpose: Provides the compile-time interface for ath11k nl80211 testmode support and no-op stubs when testmode is disabled.

Important APIs and functions: When `CONFIG_NL80211_TESTMODE` is enabled, the header declares `ath11k_tm_wmi_event()` for WMI event forwarding and `ath11k_tm_cmd()` for cfg80211 testmode command dispatch. When disabled, it defines inline stubs: events are ignored and commands return success.

Control flow: `wmi.c` can call `ath11k_tm_wmi_event()` unconditionally after including this header, and `mac.c` can register `ath11k_tm_cmd` in cfg80211 operations only when the testmode macro path is active. The stubbed event path drops test events at compile time when nl80211 testmode is not available.

State and persistence behavior: The header owns no state. It references `struct ath11k_base`, `struct ieee80211_hw`, `struct ieee80211_vif`, and `struct sk_buff` via included core definitions and caller-visible kernel headers. Any state allocation, such as FTM event buffers, is in the C implementation.

Dependencies and integration points: It includes `core.h` for ath11k types and depends on the kernel `CONFIG_NL80211_TESTMODE` feature. The header is the integration boundary between the always-built WMI/MAC code and optional testmode object inclusion from the ath11k Makefile.

Risks and edge cases: Returning `0` from the disabled `ath11k_tm_cmd()` stub can be misleading if a caller accidentally exposes a command hook without the implementation, though normal cfg80211 registration is also configuration-gated. Event drops in disabled builds are silent. New testmode entry points must preserve the same conditional-compilation behavior to avoid unresolved symbols.

Test signals: Compile-test both enabled and disabled configurations. In disabled builds, verify no testmode object is linked, WMI event references resolve to the stub, and no userspace testmode command is advertised. In enabled builds, confirm `testmode.c` symbols are linked and cfg80211/WMI integration paths reach the real functions.
