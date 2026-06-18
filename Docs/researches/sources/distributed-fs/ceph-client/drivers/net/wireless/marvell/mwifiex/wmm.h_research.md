# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.h

Purpose: declares the mwifiex WMM API surface and small inline helpers used by the mwifiex data path. It defines bit masks for WMM AC/AIFSN and ECW fields, exposes priority-conversion tables, and makes queue management functions available to association, command, 11n, TDLS, and bus-specific code.

Important APIs/types/functions: defines `enum ieee_types_wmm_aciaifsn_bitmasks` with `MWIFIEX_AIFSN`, `MWIFIEX_ACM`, and `MWIFIEX_ACI`; defines `enum ieee_types_wmm_ecw_bitmasks` with `MWIFIEX_ECW_MIN` and `MWIFIEX_ECW_MAX`; declares external `mwifiex_1d_to_wmm_queue[]` and `tos_to_tid_inv[]`; provides inline `mwifiex_get_tid` and `mwifiex_wmm_is_ra_list_empty`; declares enqueue, bypass, RA-list, TX processing, delay, association, status, downgrade, pause, and init functions implemented mainly in `wmm.c`.

Control flow: callers include this header to retrieve the TID at the head of a RA-list queue, test whether a TID RA-list is empty, enqueue frames into normal or bypass queues, process queued frames, update queue state from firmware or association IEs, and clean up per-peer RA-list state. The inline helpers are deliberately simple and require the caller to use the same locking discipline as the owning WMM code.

State and persistence: this header owns no storage except declarations for shared constant mapping arrays. The helpers read `struct mwifiex_ra_list_tbl` skb queues and return transient queue state. Persistent runtime state remains in `struct mwifiex_private` and `struct mwifiex_wmm_desc`.

Dependencies and integration: depends on mwifiex private structs declared elsewhere, Linux `list_head` and `sk_buff_head`, and WMM bit layout defined by 802.11/WMM firmware contracts. It is the interface between `wmm.c` and other mwifiex modules that need TX scheduling or RA-list visibility.

Risks: inline helpers do not acquire locks; using them without holding `ra_list_spinlock` or an otherwise stable queue context can race with enqueue/dequeue/delete. `mwifiex_get_tid` returns 0 for an empty RA list, so callers must not treat that as an actual queued TID unless they already know a frame exists. Extern table declarations require exactly one definition with matching semantics.

Test signals: compile coverage should catch signature drift between the header and implementation. Runtime coverage should include callers using `mwifiex_get_tid` only after non-empty checks and RA-list emptiness tests under concurrent queue update scenarios.
