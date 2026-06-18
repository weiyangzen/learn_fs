# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ps.h

## Purpose
`ps.h` declares the rtw89 power-save API implemented by `ps.c`. It exposes LPS, IPS, P2P power-save, NoA IE construction, one-shot NoA tracking, and small hwflags-based IPS helpers to the rest of the driver. The header owns no persistent state; it defines the callable boundary for modules that react to mac80211 configuration changes, VIF lifecycle events, coexistence control, and idle transitions.

## Important APIs and definitions
- `rtw89_enter_lps()` and `rtw89_leave_lps()` are the main leisure power-save entry/exit functions.
- `__rtw89_enter_ps_mode()` and `__rtw89_leave_ps_mode()` are lower-level low-power-mode helpers used by LPS and internal flows.
- `rtw89_leave_ps_mode()` is the public wiphy-lock-asserting leave helper.
- `rtw89_enter_ips()` and `rtw89_leave_ips()` control idle power save around core stop/start.
- `rtw89_set_coex_ctrl_lps()` lets coexistence policy force LPS exit when BTC takes control.
- `rtw89_process_p2p_ps()` and `rtw89_p2p_disable_all_noa()` synchronize P2P NoA firmware state with link BSS configuration.
- `rtw89_p2p_noa_renew()`, `rtw89_p2p_noa_append()`, and `rtw89_p2p_noa_fetch()` manage the local P2P NoA IE buffer attached to a VIF link.
- `rtw89_p2p_noa_once_init()`, `_deinit()`, and `_recalc()` manage delayed-work tracking for finite NoA intervals.
- Inline `rtw89_leave_ips_by_hwflags()` and `rtw89_enter_ips_by_hwflags()` gate IPS transitions on `IEEE80211_CONF_IDLE`; enter additionally refuses to power down while `rtwdev->scanning` is true.

## Control flow and state behavior
The header presents two power-save levels. LPS functions operate while the device is associated and firmware can manage station sleep behavior. IPS functions operate when mac80211 marks the hardware idle and the core can be stopped. The hwflags helpers are convenience wrappers for configuration-change code: leave IPS if the idle flag is set and work needs the device awake; enter IPS when the idle flag remains set, except during scans after remain-on-channel handling.

P2P declarations split recurring NoA firmware programming from local IE construction and one-shot duration tracking. Callers are expected to pass `struct rtw89_vif_link` objects that own the NoA buffers and delayed-work handlers initialized by the implementation.

## Dependencies and integration points
The prototypes depend on rtw89 core forward declarations supplied by including translation units, plus mac80211 types such as `struct ieee80211_bss_conf`, `struct ieee80211_p2p_noa_desc`, and `struct ieee80211_hw`. `ps.h` is included by rtw89 modules that need to enter or leave LPS/IPS in response to mac80211 PS, idle flags, scan state, coexistence control, P2P NoA updates, or device lifecycle events.

## Risks and edge cases
- The double-underscore helpers bypass the public lock assertions; callers must already be in the correct serialized context.
- The inline IPS helpers key entirely on `IEEE80211_CONF_IDLE` plus `rtwdev->scanning`, so callers must update those states before invoking them.
- Since this header does not include the full type definitions itself, include order must provide required struct visibility in C files that dereference fields in the inline helpers.
- P2P NoA callers must pair init/deinit with VIF-link lifetime to avoid delayed work running against stale link state.

## Test signals
Build coverage should catch missing type visibility and prototype drift with `ps.c`. Runtime signals include configuration-change paths entering/leaving IPS from hwflags, scans not entering IPS mid-scan, LPS APIs callable from station PS policy changes, coexistence-triggered LPS exit, and P2P NoA init/deinit running cleanly across VIF link creation and teardown.
