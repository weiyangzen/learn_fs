# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.h

Purpose: Declares the memory-management API used by verbs, TX, RX, and QP flush code, plus inline helpers for releasing memory references and resolving pinned user pages.

Important APIs/types/functions: Exposes `siw_umem_get/release()`, `siw_pbl_alloc()`, `siw_pbl_get_buffer()`, `siw_mem_id2obj()`, `siw_invalidate_stag()`, `siw_check_mem()`, `siw_check_sge()`, `siw_wqe_put_mem()`, `siw_mr_add_mem()`, `siw_mr_drop_mem()`, and `siw_free_mem()`. `siw_mem_put()` wraps kref release. `siw_unref_mem_sgl()` drops a sequence of memory references in WQEs. Chunk macros define 512-page chunks and derived page-list sizing. `siw_get_upage()` maps a virtual address into the two-level `siw_umem` page array.

Control flow: TX/RX paths call check helpers to resolve SGEs into referenced `siw_mem` objects, use page/PBL helpers to locate memory, and then release via WQE put helpers. Verbs uses allocation and MR attach/drop helpers during registration/deregistration.

State and persistence behavior: The API manipulates in-memory, kref-counted memory registrations and pinned page arrays. It assumes callers hold references before dereferencing memory and release them once WQE processing completes.

Dependencies/integration: Depends on `siw.h` structure definitions and RDMA kernel types included by compile units. It is used heavily by `siw_mem.c`, `siw_qp_tx.c`, `siw_qp_rx.c`, `siw_qp.c`, and `siw_verbs.c`.

Risks: `siw_get_upage()` trusts `umem->fp_addr` and `num_pages`; wrong chunk arithmetic can return invalid pages. `siw_unref_mem_sgl()` stops at the first NULL, so callers must keep contiguous resolved-memory slots. Reference leaks or double puts surface under error and flush paths.

Test signals: Page lookup at first/last page, non-page-aligned buffers, multi-chunk MRs, partial SGE resolution failure, WQE flush after partial memory resolution, and KASAN/KCSAN on deregister plus in-flight TX/RX.
