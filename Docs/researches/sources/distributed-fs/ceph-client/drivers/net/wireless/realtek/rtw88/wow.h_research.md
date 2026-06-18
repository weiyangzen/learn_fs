## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.h

Purpose: public WoWLAN definitions for rtw88 suspend/resume support.

Important APIs/types: `PNO_CHECK_BYTE`, `enum rtw_wow_pattern_type`, `enum rtw_wake_reason`, `struct rtw_fw_media_status_iter_data`, and `struct rtw_fw_key_type_iter_data`. Inline helpers `rtw_wow_mgd_linked()` and `rtw_wow_no_link()` inspect the selected WoW VIF's rtw private net type. Prototypes expose `rtw_wow_suspend()` and `rtw_wow_resume()`.

Control flow and state: the inline helpers assume `rtwdev->wow.wow_vif` is valid and return whether WoW is handling a linked managed station or a no-link station used for PNO. The enums define firmware/hardware wake reason and pattern classifications used in `wow.c`.

Dependencies and integration: depends on `main.h`, mac80211 VIF private state, firmware AOAC command data, and cfg80211 WoWLAN.

Risks and test signals: invalid `wow_vif` use would dereference NULL; callers must set wakeups before invoking linked/no-link helpers. Test suspend rejection with no suitable station VIF, linked WoW, and PNO no-link WoW.
