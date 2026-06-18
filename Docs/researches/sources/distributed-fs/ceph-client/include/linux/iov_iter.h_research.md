# sources/distributed-fs/ceph-client/include/linux/iov_iter.h

Purpose: This header provides low-level iteration helpers that advance `struct iov_iter` across user buffers, iovecs, kvecs, bvecs, folio queues, xarrays, and discard iterators.

Important APIs, types, and functions: Callback types are `iov_step_f` for kernel addresses and `iov_ustep_f` for user addresses. Per-kind helpers are `iterate_ubuf`, `iterate_iovec`, `iterate_kvec`, `iterate_bvec`, `iterate_folioq`, `iterate_xarray`, and `iterate_discard`. Public dispatchers are `iterate_and_advance`, `iterate_and_advance2`, and `iterate_and_advance_kernel`.

Control flow: Dispatch clamps length to `iter->count`, skips zero-length work, selects the iterator kind, maps pages/folios locally where needed, calls a step function with segment base/progress/length, advances iterator offsets and segment pointers by consumed bytes, and stops early if the step reports remaining bytes.

State and persistence: The iterator is mutated in place: `count`, `iov_offset`, segment pointer, segment count, folio queue slot, or xarray offset are advanced. Temporary kmap mappings are created and released per page-sized chunk.

Dependencies and integration points: Depends on UIO, bvecs, folio queues, xarray/RCU, kmap-local APIs, and copy/checksum consumers that implement step callbacks.

Risks: User iterators pass faultable `__user` pointers without pinning. Step callbacks must return unprocessed bytes, not processed bytes. Xarray iteration runs under RCU and rejects value/hugetlb entries with warnings. Kernel-only dispatcher must not receive UBUF/IOVEC.

Test signals: Cover partial consumption, segment boundary advancement, zero-length segments, bvec page splitting, folio queue extension, xarray gaps/retries, discard iterators, user fault handling by callbacks, and count/offset consistency after early stop.
