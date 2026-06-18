# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/txrx.h

Purpose: Declares shared ath10k TX completion and peer mapping APIs.

Important APIs and types: Exposes `ath10k_txrx_tx_unref()`, peer lookup helpers, peer create/delete wait helpers, and HTT peer map/unmap event handlers. It includes `htt.h` for HTT completion and peer event types.

Control flow, state, and persistence: No flow or state. The prototypes define how HTT event processing, MAC lifecycle, and data path code interact with TX completion and peer map state.

Dependencies and integration points: Consumed by HTT RX/TX event handlers and MAC peer lifecycle code. The APIs operate on `struct ath10k`, `struct ath10k_htt`, and firmware event payloads.

Risks: Callers of peer lookup helpers must hold `ar->data_lock`, as enforced in implementations. Misuse can race peer map/unmap events. TX unref ownership expectations must match HTT pending-ID allocation.

Test signals: Compile HTT event users, lockdep coverage around peer lookups, TX completion reporting, and peer wait helpers.
