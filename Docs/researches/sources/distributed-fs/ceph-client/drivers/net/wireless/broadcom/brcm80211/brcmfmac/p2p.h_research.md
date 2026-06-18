# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/p2p.h

Purpose: declares the P2P subsystem's public interface and state structures shared between cfg80211, event handlers, and `p2p.c`.

Important APIs/types: `enum p2p_bss_type` maps primary, discovery device, and up to two P2P connection BSS configs. `struct p2p_bss` stores per-BSS vif pointers. `enum brcmf_p2p_status` defines bit positions for enablement, interface add/delete/change, action-frame progress, GO negotiation, listen, response wait, and common-channel search. `struct afx_hdl` stores action-frame channel-search work/completion state. `struct brcmf_p2p_info` is the main state object embedded in cfg80211 info. Function declarations expose attach/detach, vif add/delete, role change, start/stop, scan prep, remain/cancel ROC, event notifications, action-frame send, common-channel scan hook, and probe-request notification.

Control flow and state: the header makes `brcmf_p2p_info` visible so other driver components can embed and inspect P2P state. Status bits are used as a compact state machine across cfg80211 ops and firmware event callbacks. Completions synchronize action-frame send and channel-search flows.

Dependencies and integration: includes cfg80211 and references `brcmf_cfg80211_info`, `brcmf_cfg80211_vif`, `brcmf_if`, `brcmf_fil_af_params_le`, `brcmf_bss_info_le`, and firmware event messages. It is the contract between generic cfg80211 glue and the P2P implementation.

Risks: status enum ordering is ABI-like within the driver because bits are stored in `unsigned long status`; reordering changes behavior. Shared mutable fields such as `remain_on_channel_cookie`, `next_af_subtype`, `block_gon_req_tx`, and AFX channel fields require disciplined locking or single-thread assumptions from callers/events. Public structure exposure increases coupling.

Test signals: build coverage of cfg80211/P2P users, lifecycle tests for all bss index slots, concurrent action-frame and remain-on-channel operations, and event callbacks after interface removal.
