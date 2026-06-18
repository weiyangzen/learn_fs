# sources/distributed-fs/ceph-client/drivers/misc/ocxl/pasid.c

Purpose: implements simple ordered range allocation/free for per-function PASID and ACTAG subranges assigned to AFUs.

Important APIs and types: internal `struct id_range` records `[start,end]` allocations in a list. `range_alloc()` and `range_free()` implement common allocation logic. Public-internal APIs are `ocxl_pasid_afu_alloc()`, `ocxl_pasid_afu_free()`, `ocxl_actag_afu_alloc()`, and `ocxl_actag_afu_free()`.

Control flow: allocation scans the sorted list looking for the first gap larger than the requested size, inserts a new range after the prior entry, and returns the start ID or `-ENOSPC`. PASID maximum is derived from `fn->config.max_pasid_log`; ACTAG maximum is `fn->actag_enabled`. Free scans for an exact start/size match and warns if none is found.

State and persistence: state is maintained in `fn->pasid_list` and `fn->actag_list`, both in kernel memory and tied to the OCXL function lifetime.

Dependencies and integration points: depends on `struct ocxl_fn` from `ocxl_internal.h`. Callers must serialize access if these lists can be touched concurrently; this file itself contains no lock.

Risks and test signals: check for off-by-one behavior: `max_pasid = 1 << max_pasid_log` is passed as max ID, so callers should confirm whether the maximum is intended inclusive. Allocation uses `cur->start - last_end > size`, which is gap-size sensitive. Tests should allocate/free adjacent ranges, maximal ranges, impossible ranges, and invalid frees under debug/WARN observation.
