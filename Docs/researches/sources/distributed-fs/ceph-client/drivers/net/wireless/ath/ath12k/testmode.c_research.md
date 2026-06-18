## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.c

Purpose: implements the ath12k nl80211 testmode command/event bridge. It lets userspace query the testmode ABI version, start factory test mode, send raw WMI commands, and send segmented UTF/FTM WMI payloads to firmware.

Important APIs/functions: `ath12k_tm_cmd()` is the exported cfg80211 testmode entry point; `ath12k_tm_cmd_get_version()`, `ath12k_tm_cmd_testmode_start()`, `ath12k_tm_cmd_wmi()`, and `ath12k_tm_cmd_process_ftm()` handle individual commands. `ath12k_tm_wmi_event_unsegmented()` and `ath12k_tm_process_event()` convert firmware WMI/test events back into cfg80211 testmode events. The file uses `ath12k_tm_policy` to validate netlink attributes from `../testmode_i.h`.

Control flow: `ath12k_tm_cmd()` asserts the wiphy mutex, parses nlattrs, selects the current radio from `hw->priv`, and dispatches by `ATH_TM_ATTR_CMD`. FTM commands require `ATH12K_HW_STATE_TM`, segment data into `MAX_WMI_UTF_LEN` chunks, fill `ath12k_wmi_ftm_cmd` segment headers, and submit each chunk with `ath12k_wmi_cmd_send()`. Segmented events use `ab->ftm_event_obj` to accumulate chunks until all expected segments arrive, then allocate a cfg80211 event skb and publish the assembled payload.

State and persistence: all state is runtime-only. Starting testmode allocates `ab->ftm_event_obj.eventdata`, sets `ar->ah->state = ATH12K_HW_STATE_TM`, and resets `ar->ftm_msgref`. Event reassembly tracks `expected_seq` and `data_pos` under `ab->ftm_event_obj`; temperature-like persistence or disk state is absent.

Dependencies/integration: depends on cfg80211 testmode skb helpers, netlink nla helpers, ath12k WMI allocation/submission, `debug.h` tracing, and core/hif radio state. It integrates with firmware UTF/FTM events from the WMI receive path and with mac80211's testmode callback.

Risks: event reassembly trusts segment order via `expected_seq` but does not compare `current_seq` against it before copying; malformed firmware data can desynchronize reassembly until sequence zero resets it. `ath12k_tm_cmd_testmode_start()` allocates `eventdata` but this file has no matching free path. Raw WMI testmode accepts userspace-provided binary TLVs, so validation is intentionally minimal but risky if exposed outside controlled test environments. MLO handling is marked TODO and currently chooses `ah->radio`.

Test signals: useful coverage includes netlink attribute validation failures, version reply, start-only-from-OFF behavior, WMI pdev-id rewrite for `WMI_TAG_PDEV_SET_PARAM_CMD`, FTM payload segmentation boundaries, oversized event rejection at `ATH_FTM_EVENT_MAX_BUF_LENGTH`, and cfg80211 event emission for segmented and unsegmented firmware events.
