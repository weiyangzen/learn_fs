# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.c

Purpose: Implements SoftiWARP memory registration backing, STag lookup/validation/invalidation, user-memory pinning representation, physical buffer list allocation, PBL address lookup, and memory reference release.

Important APIs/types/functions: `siw_mem_id2obj()` resolves an STag index from the device memory xarray under RCU and returns a referenced `siw_mem`. `siw_mr_add_mem()` allocates a memory object, selects a cyclic 24-bit STag index, stores PD/VA/length/permissions, and sets MR lkey/rkey. `siw_mr_drop_mem()` invalidates and removes the memory object from the xarray. `siw_check_mem()` and `siw_check_sge()` enforce STag validity, PD match, permissions, key match, and address bounds. `siw_invalidate_stag()` implements local/remote invalidation. `siw_umem_get()` pins userspace memory through `ib_umem_get()` and stores pages in chunked arrays. `siw_pbl_get_buffer()` walks PBL entries by byte offset.

Control flow: Verbs registration calls into `siw_umem_get()` or `siw_pbl_alloc()`, then `siw_mr_add_mem()`. TX/RX paths resolve and hold memory references while moving data, then release with `siw_wqe_put_mem()` or specific put paths. Deregistration invalidates first, erases from lookup, and drops the final reference after active users finish.

State and persistence behavior: Memory registrations are transient kernel objects keyed by STag. `stag_valid` is the fast invalidation bit, made visible before xarray erase with a barrier. User pages remain pinned through `ib_umem` until release.

Dependencies/integration: Uses RDMA umem, scatter-gather iteration, DMA virtual helpers, xarray, RCU, krefs, and SIW QP WQE formats. It is a security boundary for all remote RDMA access.

Risks: Bounds checks use `addr + len` arithmetic and must avoid overflow assumptions. STag key/index mismatches, stale references after deregistration, and invalidation ordering are high-risk. Chunk calculation in `siw_umem_get()` must match pinned pages.

Test signals: Register/deregister user MRs, DMA MRs, fast-reg PBL MRs, zero-length rejection, stale STag access, wrong PD, wrong key, remote write/read permission failures, local invalidation, remote invalidation via SEND_INV, and deregister while TX/RX holds references.
