# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.h

Purpose: this header declares the i40e AF_XDP zero-copy entry points used by the main Tx/Rx, XDP, and netdev code. It also defines the Tx batch size used by `i40e_xsk.c`.

Important APIs/types: it forward-declares `struct i40e_ring`, `struct i40e_vsi`, `struct net_device`, and `struct xsk_buff_pool`; defines `PKTS_PER_BATCH` as 4 for unrolled AF_XDP Tx descriptor filling; and declares queue-pair enable/disable, pool setup, zero-copy Rx buffer allocation/cleaning, XDP Tx cleanup, wakeup, Rx BI reallocation, and zero-copy Rx BI clearing.

Control flow and state: callers use `i40e_xsk_pool_setup` from XSK pool bind/unbind paths, `i40e_clean_rx_irq_zc` and `i40e_clean_xdp_tx_irq` from NAPI paths, and cleanup helpers from queue teardown. The header does not store state itself, but its API assumes ring/VSI fields such as XSK pool pointers, zero-copy queue bitmaps, and descriptor indexes are maintained by the implementation.

Dependencies and integration: it depends only on Linux integer types and i40e/XSK forward declarations, keeping inclusion light for other driver modules. It bridges generic AF_XDP netdev callbacks with i40e-specific queue and descriptor handling.

Risks and test signals: API mismatch can break build integration across XDP, queue setup, and Rx/Tx files. `PKTS_PER_BATCH` is performance-sensitive and tied to an unroll pragma in the implementation. Test signals are compile coverage with XDP/XSK enabled, queue bind/unbind smoke tests, and NAPI cleanup paths invoking the declared helpers.
