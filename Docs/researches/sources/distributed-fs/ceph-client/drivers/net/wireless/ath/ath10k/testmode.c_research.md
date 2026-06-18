# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.c

Purpose: Implements nl80211 testmode support for ath10k UTF/FTM firmware, including firmware loading, UTF start/stop, raw WMI command injection, segmented TLV command transmission, and routing UTF WMI events back to userspace.

Important APIs and functions: Public entry points are `ath10k_tm_cmd()`, `ath10k_tm_event_wmi()`, and `ath10k_testmode_destroy()`. Major helpers handle unsegmented and segmented event emission, version replies, UTF firmware fetch (`ath10k_tm_fetch_firmware()`), UTF lifecycle (`ath10k_tm_cmd_utf_start()`, `__ath10k_tm_cmd_utf_stop()`), raw WMI sends, and TLV segmentation.

Control flow: `ath10k_tm_cmd()` parses netlink attributes, resets expected sequence state, and dispatches by command. UTF start requires the device to be OFF, fetches API 2 or legacy API 1 UTF firmware, reuses normal board/OTP data when needed, optionally initializes code-swap, enables `utf_monitor`, powers HIF in UTF mode, allocates an FTM event buffer, starts the core, and moves state to UTF. UTF stop reverses core/HIF/monitor/firmware/event-buffer state. WMI commands send user payloads directly with a provided WMI command ID. TLV commands segment up to `MAX_WMI_UTF_LEN` chunks into `wmi_ftm_cmd` frames and increment `ftm_msgref`. Incoming WMI events are consumed only while `utf_monitor` is set and are emitted through cfg80211 testmode, reassembling segmented FTM events into a bounded buffer.

State and persistence: Mutates `ar->state`, `ar->testmode.utf_monitor`, `expected_seq`, `data_pos`, `eventdata`, `ftm_msgref`, and `utf_mode_fw`. No durable persistence exists; firmware images are released on stop/destroy. `conf_mutex` protects lifecycle and command sends; `data_lock` protects event monitor state and segmented event buffer use.

Dependencies and integration points: Depends on cfg80211 testmode, netlink policies, ath10k firmware/core/HIF/WMI/TLV/swap layers, and normal firmware components for board/OTP reuse. It intercepts WMI events before normal mac80211 paths when UTF firmware is running.

Risks: Testmode exposes powerful firmware command injection and is only safe under `CONFIG_NL80211_TESTMODE`. Segmented event handling trusts sequence progression enough to append by current data position; out-of-order segments can produce bad user data though length is bounded. In `ath10k_tm_cmd_wmi()`, send failure path does not free the allocated skb locally, relying on WMI send ownership assumptions. UTF start failure unwinds several resources and must keep `utf_monitor`/firmware/code-swap/event buffer consistent.

Test signals: Get-version reply, UTF API 2 load and API 1 fallback, start while ON/UTF/OFF, stop while not UTF, raw WMI send with missing attrs, TLV segmentation across one and multiple chunks, segmented event reassembly boundaries, oversized event rejection, code-swap UTF firmware, destroy while UTF active, and builds with/without nl80211 testmode.
