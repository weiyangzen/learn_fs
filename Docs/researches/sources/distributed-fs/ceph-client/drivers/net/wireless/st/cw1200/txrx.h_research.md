# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/txrx.h

Purpose: Declares the CW1200 datapath interface shared by mac80211 glue, WSM transport, security setup, and AP link-id maintenance.

Important APIs, types, and functions: `struct tx_policy` encodes firmware retry counts in three little-endian words plus local metadata. `struct tx_policy_cache` provides eight cache entries, used/free lists, and a spinlock. Public entry points cover policy lifecycle (`tx_policy_init`, `tx_policy_upload_work`, `tx_policy_clean`), TX/RX callbacks (`cw1200_tx`, `cw1200_tx_confirm_cb`, `cw1200_rx_cb`), key lifecycle (`cw1200_alloc_key`, `cw1200_upload_keys`), timeout work, and link-id work/GC.

Control flow: The header does not implement flow, but it defines the contract that WSM uses for callbacks and the mac80211 side uses for TX submission. The retry policy cache exists because the firmware accepts a retry-policy id rather than a per-frame retry chain.

State and persistence: Declares in-memory policy cache and AP link-id GC timeout (`CW1200_LINK_ID_GC_TIMEOUT`). No persistent storage.

Dependencies and integration points: Depends on Linux lists/spinlocks, `struct ieee80211_hw`, `struct sk_buff`, WSM TX/RX structs, and CW1200 private state.

Risks: The small fixed retry-policy cache makes correct usage counting and release critical. Callers must preserve skb private offsets for `cw1200_skb_dtor()`.

Test signals: Compile coverage for all declared callbacks, TX policy cache saturation, and key/link-id lifecycle paths.
