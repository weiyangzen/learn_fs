# File Research: sources/cow-pools/bcachefs-tools/include/linux/idr.h

This header declares kernel-style IDR and IDA interfaces. The `struct idr_layer`/`struct idr` definitions mirror an ID-to-pointer radix tree with a hint, top layer, lock, and free layer cache. `idr_find()` has an inline hint fast path and falls back to `idr_find_slowpath()`.

Several IDR operations are external, but `idr_alloc()` and `idr_remove()` are stubbed inline in this header. The comments preserve RCU lookup synchronization requirements.

The IDA portion is a bcachefs-tools-specific integer allocator implemented as a flat d-ary bitmap tree in Eytzinger layout. `struct ida` contains a mutex, depth, and node array; allocation/free/batch/find APIs are declared, with convenience wrappers for min/max/range allocation.
