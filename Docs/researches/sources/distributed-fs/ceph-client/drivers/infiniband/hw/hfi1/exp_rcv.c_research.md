# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.c

Purpose: expected receive TID group lifecycle for HFI1 contexts. It initializes free/used/full TID group lists, allocates group descriptors for a receive context, and frees them while clearing hardware TID state.

Important APIs/functions: `hfi1_exp_tid_group_init()` initializes `rcd->tid_group_list`, `rcd->tid_used_list`, and `rcd->tid_full_list`. `hfi1_alloc_ctxt_rcv_groups()` allocates `rcd->groups` on the context NUMA node and seeds free groups based on `expected_base`, `expected_count`, and `dd->rcv_entries.group_size`. `hfi1_free_ctxt_rcv_groups()` frees group storage, reinitializes lists, and calls `hfi1_clear_tids()`.

Control flow: allocation calculates `ngroups = expected_count / group_size`, allocates an array, then loops assigning each group a base TID, size, and list entry. Freeing drops the array, resets list heads/counts, and clears TIDs from hardware/software context state.

State and persistence: persistent context state includes `rcd->groups` and the three `exp_tid_set` lists. Hardware receive array/TID entries may persist until `hfi1_clear_tids()` clears them. Group fields track base, size, used count, and bitmap-like map state.

Dependencies and integration: depends on `exp_rcv.h`, `hfi.h`, list helpers, NUMA allocation, and chip receive-entry sizing. Higher-level TID RDMA/user memory registration code consumes these group lists to allocate expected receive entries.

Risks: allocation silently truncates if `expected_count` is not an exact multiple of `group_size`; the rest of the driver likely guarantees alignment, but that invariant matters. Freeing is documented for kernel and base user contexts; calling it on an active context would invalidate TID state. Group list counts must remain synchronized with list mutations in inline helpers.

Test signals: context allocation/free cycles, NUMA allocation failure, expected_count/group_size boundary cases, TID registration/unregistration stress, and verification that hardware TID entries are cleared during context teardown.
