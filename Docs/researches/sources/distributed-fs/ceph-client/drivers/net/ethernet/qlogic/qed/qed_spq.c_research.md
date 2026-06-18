# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_spq.c

## Purpose

`qed_spq.c` implements the slow-path queue, event queue, and consolidation queue runtime for QED hardware functions. It allocates DMA chains, initializes firmware context and doorbells, posts slow-path elements, waits for blocking completions, dispatches async events, handles out-of-order completions, and recycles SPQ entries.

## Important APIs and Functions

- Blocking completion: `qed_spq_blocking_cb()`, `__qed_spq_block()`, and `qed_spq_block()` implement EBLOCK/BLOCK waiting. The wait path does a quick udelay poll, then msleep polling, then asks MCP to drain, retries, and finally reports `QED_HW_ERR_RAMROD_FAIL` if the ramrod remains stuck.
- Entry preparation and hardware posting: `qed_spq_fill_entry()` installs the blocking callback when needed; `qed_spq_hw_initialize()` programs the SPQ CID context; `qed_spq_hw_post()` writes the SPQE to the chain and rings the doorbell with memory barriers.
- Async events: `qed_async_event_completion()`, `qed_spq_register_async_cb()`, and `qed_spq_unregister_async_cb()` dispatch firmware async EQEs by protocol.
- EQ operations: `qed_eq_alloc()`, `qed_eq_setup()`, `qed_eq_free()`, `qed_eq_prod_update()`, and `qed_eq_completion()` manage event-ring memory and completion draining.
- CQE completion: `qed_eth_cqe_completion()` routes Ethernet slow-path CQEs to SPQ completion for PFs.
- SPQ lifecycle: `qed_spq_alloc()`, `qed_spq_setup()`, and `qed_spq_free()` allocate chains, DMA-backed entries, doorbell recovery records, and CID context.
- Entry and posting flow: `qed_spq_get_entry()`, `qed_spq_return_entry()`, `qed_spq_add_entry()`, `qed_spq_pend_post()`, `qed_spq_post()`, and `qed_spq_completion()` own list movement and completion callbacks.
- ConsQ lifecycle: `qed_consq_alloc()`, `qed_consq_setup()`, and `qed_consq_free()`.

## Control Flow

During setup, `qed_spq_alloc()` allocates the SPQ object, a single-mode chain of `slow_path_element` entries, and a coherent DMA array of `struct qed_spq_entry`. `qed_spq_setup()` initializes lists and lock, assigns each entry a DMA data pointer to its embedded `ramrod`, acquires a core CID, initializes the firmware context, resets the chain, builds doorbell data, and registers the doorbell for recovery.

Posting starts when a caller obtains an entry. If the free pool is empty, `qed_spq_get_entry()` allocates an entry dynamically and tags it for `unlimited_pending`. `qed_spq_post()` fills callbacks, adds the entry to pending, posts as many pending entries as the ring has capacity for, and, for EBLOCK, waits until completion before returning the entry. `qed_spq_post_list()` moves posted entries to `completion_pending`, writes each SPQE into the chain, and rings the hardware doorbell.

Completions arrive through `qed_eq_completion()` or the Ethernet CQE completion path. EQ completion snapshots the firmware consumer index, consumes each event-ring entry, dispatches async events or SPQ completions, recycles consumed EQ elements, updates the EQ producer, and attempts to post pending SPQ work. `qed_spq_completion()` finds the matching entry by `echo`, updates the out-of-order completion bitmap and chain consumer, invokes the callback outside the lock, and returns non-EBLOCK entries to the free pool.

## State and Persistence Behavior

The module owns transient but long-lived kernel/firmware state: SPQ lists, DMA entry memory, SPQ and EQ chains, completion bitmap, doorbell recovery metadata, and counters. It uses `spin_lock_bh()` to protect SPQ lists and counters. Memory ordering matters in two places: blocking completion uses release/acquire around `comp_done->done`, and hardware posting uses write memory barriers before and after the doorbell.

Recovery mode is treated specially. If `cdev->recov_in_prog` is set, `qed_spq_post()` skips hardware posting and returns success, optionally setting RDMA firmware return codes to success so upper layers can unwind without normal ramrod completion.

## Dependencies and Integration Points

`qed_spq.c` depends on QED chain, context, interrupt, hardware register, MCP, doorbell recovery, RDMA, iSCSI, OOO, and SR-IOV headers. It integrates with:

- Firmware context allocation through `qed_cxt_acquire_cid()` and `qed_cxt_get_cid_info()`.
- Interrupt registration through `qed_int_register_cb()`.
- Doorbell registers through `DOORBELL()`, `qed_db_addr()`, and doorbell recovery registration.
- MCP drain and hardware-error notification for stuck ramrods.
- SR-IOV async events by allowing `qed_sriov_eqe_event()` to register as the common protocol callback.
- Ethernet queue completion through `qed_eth_cqe_completion()`.

## Risks and Edge Cases

- EBLOCK entries from `unlimited_pending` have two objects: the original dynamically allocated entry and a posted pool entry. The `post_ent` ownership path is subtle and must remain consistent to avoid leaks or double returns.
- `qed_spq_comp_bmap_update()` handles out-of-order completions using `echo % SPQ_RING_SIZE`. Any change to echo generation or ring sizing risks returning produced elements too early.
- `qed_spq_post()` returns success immediately in recovery mode without freeing the entry through normal completion flow. Callers rely on recovery semantics and request ownership must be reviewed when adding new callers.
- The doorbell path depends on correct barriers. Removing or weakening `wmb()` can let firmware observe a producer update before the SPQE content is visible.
- `qed_eq_completion()` returns a single `rc` while continuing through events; one bad async or SPQ completion can make the whole drain report failure.
- `qed_spq_get_entry()` can allocate with `GFP_ATOMIC` under pressure. Heavy slow-path bursts can hit allocation failures if the ring is full and no free entries are available.
- Blocking waits can last several seconds before MCP drain and error notification. Tests that inject missing completions should account for that timeout.

## Test Signals

Relevant tests include SPQ allocation/setup/free under probe/remove, posting CB and EBLOCK ramrods, forcing ring exhaustion to exercise `unlimited_pending`, injecting out-of-order completions to verify bitmap advancement, validating doorbell recovery registration/removal, EQ async dispatch to SR-IOV, CQE-based Ethernet ramrod completion, and failure injection for stuck ramrods that should invoke MCP drain and hardware-error notification.
