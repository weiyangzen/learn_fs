# File Research: sources/cow-pools/bcachefs-tools/include/linux/percpu-refcount.h

This header simplifies Linux `percpu_ref` into an atomic-long reference counter. `struct percpu_ref` stores `count`, a `release` callback, and a `confirm_switch` callback pointer.

Initialization sets the starting count to one unless `PERCPU_REF_INIT_DEAD` is requested. Get/tryget/put operations directly manipulate the atomic count; `percpu_ref_put_many()` calls the release callback when the count reaches zero. Kill drops the initial reference, reinit increments again, and dying/zero checks read the count.

The per-CPU fast/atomic mode flags are defined for API compatibility, but this implementation does not maintain separate per-CPU counters.
