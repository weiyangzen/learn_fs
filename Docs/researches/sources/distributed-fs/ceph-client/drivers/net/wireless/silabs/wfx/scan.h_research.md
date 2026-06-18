# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.h

Purpose: Declares WFx scan and remain-on-channel mac80211 callbacks plus scan-completion helper.

Important APIs and types: Exports `wfx_hw_scan()`, `wfx_cancel_hw_scan()`, `wfx_scan_complete()`, `wfx_remain_on_channel()`, `wfx_cancel_remain_on_channel()`, and their work functions.

Control flow and integration: `main.c` wires these into `ieee80211_ops`; `hif_rx.c` calls `wfx_scan_complete()` on firmware scan-complete indications.

State and persistence: State is stored in `struct wfx_vif` fields declared in `wfx.h`.

Dependencies: Depends on mac80211 scan/ROC types and WFx vif private data.

Risks and test signals: Build tests should keep callback signatures current with mac80211; runtime tests should ensure completion is delivered for normal scan, abort, and ROC.

Test signals: Source read size: 28 lines, 886 bytes.
