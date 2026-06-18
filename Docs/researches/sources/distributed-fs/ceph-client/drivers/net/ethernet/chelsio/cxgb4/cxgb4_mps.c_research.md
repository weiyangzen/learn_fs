# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_mps.c

Purpose: wraps firmware MPS MAC filter allocation/free/update with an adapter-local reference list so shared MAC TCAM entries are not released while another user still references the same hardware index.

Important APIs/functions: `cxgb4_alloc_mac_filt`, `cxgb4_free_mac_filt`, `cxgb4_update_mac_filt`, `cxgb4_init_mps_ref_entries`, and `cxgb4_free_mps_ref_entries`; internal helpers `cxgb4_mps_ref_inc` and `cxgb4_mps_ref_dec_by_mac` manage `struct mps_entries_ref` records under `adap->mps_ref_lock`.

Control flow: allocation delegates to `t4_alloc_mac_filt`, then records every returned non-`0xffff` index; on local ref allocation failure it frees the just-allocated filters. Freeing decrements by MAC and only calls `t4_free_mac_filt` when the reference count reaches zero. Updating calls `cxgb4_change_mac` and then adds a reference for the returned TCAM index.

State and persistence: state is in the in-memory `adap->mps_ref` list with `refcount_t` counts, address, mask, and MPS index. It is initialized during adapter setup and torn down during driver cleanup; hardware state persists until explicit firmware filter frees.

Dependencies/integration: depends on `cxgb4.h`, Ethernet address helpers, Chelsio firmware helpers `t4_alloc_mac_filt`/`t4_free_mac_filt`/`cxgb4_change_mac`, and adapter lifecycle code in `cxgb4_main.c`.

Risks: `cxgb4_update_mac_filt` increments the reference list but does not roll back on later caller failure. The dec-by-MAC path ignores `-EBUSY` and only frees hardware on zero ref, so callers must interpret the returned freed-count contract carefully. Locking uses `GFP_ATOMIC` under a bottom-half spinlock.

Test signals: useful tests include duplicate allocation/free sequencing for the same MAC, update and teardown paths, ENOMEM injection after firmware allocation, and adapter remove with non-empty `mps_ref`.
