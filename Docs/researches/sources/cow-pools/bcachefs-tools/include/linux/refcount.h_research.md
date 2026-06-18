# File Research: sources/cow-pools/bcachefs-tools/include/linux/refcount.h

This header provides `refcount_t`, a reference-count wrapper around `atomic_t`. It defines `REFCOUNT_INIT`, `REFCOUNT_MAX`, `REFCOUNT_SATURATED`, saturation reason enums, and inline operations for set/read/add/inc/sub/dec variants.

The long header comment describes Linux refcount saturation and memory-ordering semantics. In this user-space version, many inline operations delegate to atomic operations without explicit saturation-warning machinery in the shown code, while preserving API names and ordering intent. Lock-coupled decrement helpers are declared externally.
