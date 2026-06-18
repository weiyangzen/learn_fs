# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwsignal.h

Purpose: declares the firmware-signaling interface used by the rest of `brcmfmac` and defines the firmware FIFO/access-category numbering shared with `fwsignal.c`.

Important APIs/types: `enum brcmf_fws_fifo` maps firmware FIFOs to background, best-effort, video, voice, BCMC, and ATIM queues. Function declarations cover attach/detach, debugfs creation, queueing/flow-control queries, header pull/push path entry through `brcmf_fws_process_skb` and `brcmf_fws_hdrpull`, interface lifetime hooks, bus TX completion/blocking, and RX reorder.

Control flow and state: callers do not own state directly; they hold or pass `struct brcmf_fws_info *` returned by attach and use interface callbacks as netdevs are added or removed. Header users can branch on `brcmf_fws_queue_skbs()` and `brcmf_fws_fc_active()` to decide whether the firmware-signaling queues are active.

Dependencies and integration: integrates with `core.h` types (`brcmf_pub`, `brcmf_if`), Linux `sk_buff`, bus/proto TX completion, and cfg80211 interface lifecycle. The header intentionally hides queue and descriptor internals from other compilation units.

Risks: callers must pair attach/detach and invoke interface add/delete hooks consistently; otherwise queued packets can be tied to stale descriptors. FIFO enum order is semantically significant because `fwsignal.c` maps priorities and credit arrays by index.

Test signals: compile/link coverage for all protocol modes, interface add/delete under traffic, and flow-control-active transitions when firmware does or does not supply credit maps.
