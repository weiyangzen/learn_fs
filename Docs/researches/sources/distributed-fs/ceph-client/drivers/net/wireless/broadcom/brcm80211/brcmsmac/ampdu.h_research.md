# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ampdu.h

Purpose: declares the brcmsmac A-MPDU session interface and module lifecycle functions.

Important APIs and types: `struct brcms_ampdu_session` carries the current aggregate builder state: `wlc`, skb queue, maximum aggregate length/frame count, current aggregate byte count, and DMA byte count. Exported functions reset a session, add frames, finalize an aggregate, attach/detach the AMPDU module, process TX status, update BA template MAC address, and update SHM.

Control flow: callers create/reset a session, repeatedly call `brcms_c_ampdu_add_frame()` until it returns `-ENOSPC` or input is exhausted, then call `brcms_c_ampdu_finalize()` before transmission.

State and persistence: session state is per aggregate and transient. Module state is hidden in `struct ampdu_info` from `ampdu.c`.

Dependencies and integration: depends on `struct brcms_c_info`, `struct scb`, `struct sk_buff`, and `struct tx_status` declarations from brcmsmac internals.

Risks and test signals: callers must not reuse a session without reset and must handle `-ENOSPC` by transmitting/finalizing the existing aggregate. Tests should validate single-frame and multi-frame aggregates, empty finalize, and TX status calls for both station-present and station-null cases.
