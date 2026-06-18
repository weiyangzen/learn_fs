<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h` defines the extended MLME engine: management-frame construction/parsing helpers, channel plans, command handlers, action frame handling, site-survey state, link timers, operation mode, and C2H event headers. The source was reviewed as a complete 717-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `struct mlme_ext_priv`, `struct mlme_ext_info`, `struct ss_res`, `struct rt_channel_plan`, `struct action_handler`, `struct xmit_frame`, management helpers such as `issue_beacon`, `issue_probereq`, `issue_auth`, `issue_assocreq`, `issue_deauth`, `issue_nulldata`, `send_beacon`, IE helpers such as `rtw_set_fixed_ie`, `rtw_set_ie`, `rtw_get_wpa2_cipher_suite`, handlers such as `join_cmd_hdl`, `disconnect_hdl`, `sitesurvey_cmd_hdl`, `setkey_hdl`, `mlme_evt_hdl`, and C2H event callback declarations.

## Control Flow

The command thread invokes extended MLME handlers to scan channels, join/create BSS, set keys, issue management frames, process received management frames, maintain beacon timing, and handle action/ADDBA/TDLS-style control.

## State and Persistence Behavior

Extended MLME state persists channel plan, current channel/bandwidth/offset, survey result counters, sequence numbers, authentication/association status, beacon timing, link timers, and management-frame retry/timeout state.

## Dependencies and Integration Points

Deeply connected to `wifi.h`, `ieee80211.h`, `rtw_cmd.h`, `rtw_mlme.h`, `rtw_xmit.h`, `rtw_recv.h`, `sta_info.h`, `rtw_security.h`, `rtw_rf.h`, and HAL channel/power APIs. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Large management-frame surface with many length-sensitive IEs. Channel plan and timer mistakes can break regulatory behavior, association, or scanning. Handler table sizes must match command payloads.

## Test Signals

Management-frame encode/decode, scan across channel plans, auth/assoc timeout/retry, AP beaconing, ADDBA/action handling, malformed management frames, and channel switch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_mlme_ext.h -->
