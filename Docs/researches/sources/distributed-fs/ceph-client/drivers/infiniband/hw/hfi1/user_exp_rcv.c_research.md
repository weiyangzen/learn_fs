# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.c

## Purpose
`user_exp_rcv.c` manages user expected-receive TID mappings. It pins user receive pages, groups physically contiguous pages into hardware-supported TID page sets, programs hfi1 RcvArray entries, tracks each programmed entry in file-private state, reacts to MMU invalidations, returns invalidated TIDs to userspace, and clears mappings on user request or file teardown.

## Important APIs and Functions
Exported APIs are `hfi1_user_exp_rcv_init()`, `hfi1_user_exp_rcv_free()`, `hfi1_user_exp_rcv_setup()`, `hfi1_user_exp_rcv_clear()`, and `hfi1_user_exp_rcv_invalid()`. Internal helpers include `pin_rcv_pages()`, `unpin_rcv_pages()`, `find_phys_blocks()`, `program_rcvarray()`, `set_rcvarray_entry()`, `unprogram_rcvarray()`, `__clear_tid_node()`, `clear_tid_node()`, `unlock_exp_tids()`, `tid_rb_invalidate()`, `tid_cover_invalidate()`, and `cacheless_tid_rb_remove()`.

## Control Flow
Initialization allocates `entry_to_rb` for RcvArray entry-to-node lookup and, when the TID unmap capability is absent, allocates an invalid-TID ring and enables MMU notifier mode. Setup validates page alignment and nonzero length, creates a `tid_user_buf`, optionally installs a cover interval notifier, pins pages subject to memlock/cache limits, finds physically contiguous page sets, reserves the per-file TID share, and under the context expected-receive mutex programs full and partial TID groups. Each programmed entry allocates a `tid_rb_node`, DMA maps the pages, optionally installs an interval notifier for the exact pages, records the node in `entry_to_rb`, writes the hardware TID via `hfi1_put_tid()`, and adds encoded TID info to the returned list. Failures unprogram and unpin partial work.

Clear copies the user TID list, unprograms each entry under `exp_mutex`, removes interval notifiers, clears hardware, unmaps DMA, releases pages, updates group allocation state, and decrements `tid_used`. MMU invalidation immediately clears the hardware entry and queues the encoded TID into `fd->invalid_tids`, setting the per-subcontext user event bit. `hfi1_user_exp_rcv_invalid()` copies and clears that invalidation list without holding the lock during `copy_to_user()`.

## State, Persistence, and Dependencies
Persistent state is per open file/context: `fd->entry_to_rb`, `fd->invalid_tids`, `fd->invalid_tid_idx`, `fd->tid_used`, `fd->tid_limit`, `fd->tid_n_pinned`, locks, and event bits. Context state includes free/used/full `tid_group` lists, `expected_count`, `expected_base`, `exp_mutex`, and receive-entry group size. Nodes retain DMA address, page array, notifier, RcvArray entry, group pointer, and a `freed` guard. Dependencies include `mmu_interval_notifier`, DMA mapping, `user_pages.c` pin helpers, `exp_rcv.h`, `mmu_rb.h`, and TID tracepoints.

## Integration Points
The user ioctl/file layer calls setup, clear, invalid, init, and free. User SDMA expected sends consume TID values produced here and validate TID offset/length in `user_sdma.c`. Hardware receive programming uses `hfi1_put_tid()` and RcvArray group helpers. The event mechanism exposes MMU invalidations to PSM/user libraries.

## Risks and Test Signals
Risks include notifier races during setup, incorrect accounting when partially programming groups, clearing a node twice during user clear versus MMU invalidation, stale user TID values after invalidation, DMA unmap/unpin ordering, and memlock/cache-limit bypass. Test signals include partial setup under limited RcvArray resources, page unmap while TIDs are active, invalid list delivery and event-bit clearing, setup failure cleanup with no pinned-page leaks, repeated clear/free, subcontext TID-limit enforcement, and trace events for register/unregister/invalidate.
