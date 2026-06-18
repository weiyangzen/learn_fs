# sources/distributed-fs/lustre-release/lnet/lnet/lib-md.c

## Purpose

`lib-md.c` manages LNet memory descriptors. An MD describes user/kernel memory used for PUT, GET, REPLY, ACK, and portal receive operations. This file builds internal `struct lnet_libmd` objects from user-facing `struct lnet_md`, attaches MDs to match entries or binds free-floating RDMA MDs, maps buffers to `bio_vec` fragments, links MDs into per-CPT resource containers, detaches response trackers, and unlinks/free MDs safely when operations complete.

## Important APIs, Types, and Functions

- `lnet_md_build()` validates and converts `struct lnet_md` into `struct lnet_libmd`, including contiguous-buffer splitting into page fragments, KIOV copy/validation, GPU flag propagation, threshold/options/user pointer/handler setup, and optional small-MD slab allocation.
- `lnet_md_unlink()` marks an MD zombie, detaches it from its ME/portal, invalidates its handle, and frees it immediately only when `md_refcount == 0`.
- `lnet_get_first_page()` and `lnet_cpt_of_md()` resolve the first backing page and CPT for locality decisions. Bulk-handle MDs redirect to the bulk MD.
- `lnet_md_link()` initializes a resource handle and inserts the MD into `the_lnet.ln_md_containers[cpt]->rec_active`.
- `lnet_assert_handler_unused()` verifies no active MD still uses a handler.
- `lnet_md_deconstruct()` copies event-visible MD fields into `struct lnet_event`.
- Exported public API: `LNetMDAttach()`, `LNetMDBind()`, and `LNetMDUnlink()`.

## Control Flow

`LNetMDAttach()` requires an empty ME and at least one GET or PUT operation flag. It builds the MD, locks the ME CPT resource container, unlinks the ME on build error, links the MD, attaches it to the portal through `lnet_ptl_attach_md()`, creates the handle, unlocks, then drops bad delayed messages and resumes matching delayed PUTs. The ME is either linked to the MD or freed on failure.

`LNetMDBind()` creates a free-floating MD for active operations. It rejects MDs that have GET/PUT operation flags, builds the MD, rejects buffers larger than `LNET_MTU`, locks the current resource CPT, links the MD, and returns a handle. These MDs are later used by `LNetPut()` and `LNetGet()`.

`LNetMDUnlink()` maps the handle cookie to a CPT, locks resources, retries if a zero-refcount MD is concurrently in handler execution, marks the MD aborted, builds a standalone unlink event if a handler exists and no operations are active, detaches any response tracker, calls `lnet_md_unlink()`, unlocks, and invokes the handler outside the resource lock.

## State and Persistence Behavior

MDs persist in per-CPT active resource containers until explicitly unlinked, automatically unlinked, or freed after the last active operation. A handle lookup remains valid only until `lnet_res_lh_invalidate()` in `lnet_md_unlink()`. `md_refcount`, `LNET_MD_FLAG_ZOMBIE`, `LNET_MD_FLAG_ABORTED`, `LNET_MD_FLAG_HANDLING`, `LNET_MD_FLAG_AUTO_UNLINK`, and optional `md_rspt_ptr` govern lifetime.

Memory backing is not owned by LNet. The MD stores page vectors pointing to caller memory. For contiguous input, the file computes page fragments from `virt_to_page()` or `vmalloc_to_page()`. For `LNET_MD_KIOV`, it trusts caller page pointers but validates fragment offsets/lengths. Event persistence is through callbacks/queues using data copied by `lnet_md_deconstruct()` and events built by the message path.

## Dependencies and Integration Points

The MD layer integrates with ME/portal logic (`lnet_ptl_attach_md()`, `lnet_ptl_detach_md()`, delayed message lists), resource-handle containers, message attach/finalize code, response tracking in `lib-move.c`, small-MD slab caches, and public LNet APIs consumed by upper protocols. CPT selection integrates with `lib-cpt.c` through `lnet_cpt_of_md()` and later message pathway selection.

## Risks and Edge Cases

- `lnet_get_first_page()` follows bulk handles without taking an explicit visible lock in this function; callers need to ensure handle lifetime/locking is appropriate.
- Contiguous MD building uses kernel virtual address translation and assumes caller memory remains pinned/valid for the operation lifetime.
- KIOV page pointers are explicitly taken on trust. Invalid pages cannot be detected here.
- `LNetMDBind()` rejects lengths over `LNET_MTU`, while attached MDs can represent larger portal buffers. Callers must choose the correct API.
- Unlink races with handler execution require `lnet_md_wait_handling()`. Missing this pattern in future code could lead to use-after-free or duplicate events.
- Response tracker cleanup crosses MD/resource and monitor-thread state; detach ordering is important to avoid stale tracker pointers.

## Test Signals

Tests should cover MD validation failures, contiguous and KIOV fragment construction, max-size constraints, GPU and bulk-handle flags, small versus large allocation paths, attach failure unlinking the ME, delayed PUT match/drop behavior after attach, free-floating bind constraints, unlink with and without active refs, handler callback delivery for immediate unlink, response tracker detachment, and race tests around `LNET_MD_FLAG_HANDLING`.
