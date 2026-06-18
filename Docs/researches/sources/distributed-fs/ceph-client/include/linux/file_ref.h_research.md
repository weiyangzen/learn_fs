# sources/distributed-fs/ceph-client/include/linux/file_ref.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/file_ref.h` implements a file-specific reference counter designed for `SLAB_TYPESAFE_BY_RCU` file objects. The source was read as a complete 218-line file for this report.

## Important APIs, Types, and Functions

Key exports are `FILE_REF_ONEREF`, `FILE_REF_MAXREF`, `FILE_REF_SATURATED`, `FILE_REF_RELEASED`, `FILE_REF_DEAD`, `FILE_REF_NOREF`, `file_ref_t`, `file_ref_init`, `__file_ref_put`, `file_ref_get`, `file_ref_inc`, `file_ref_put`, `file_ref_put_close`, `file_ref_read`, and `__file_ref_read_raw`.

## Control Flow

`file_ref_init()` stores count minus one. `file_ref_get()` unconditionally increments with full ordering and succeeds only if the resulting value is not in a negative/dead zone. `file_ref_inc()` is for callers already holding a ref and warns on released refs. `file_ref_put()` disables preemption, decrements, and falls into `__file_ref_put()` when the result enters saturation/dead handling. `file_ref_put_close()` optimizes the common last-reference close by CASing one-ref directly to dead.

## State and Persistence Behavior

The counter stores valid, saturation, released/dead, and no-ref zones in an atomic long-sized field. It is in-memory lifetime state for `struct file`, not persistent storage.

## Dependencies and Integration Points

It depends on atomics, preemption guards, and integer types. It integrates with the VFS file cache and RCU-safe file object reuse.

## Risks and Edge Cases

The design intentionally avoids trying to repair negative/dead counts after failed gets because the file may already have been recycled. Preemption disabling in `file_ref_put()` protects against slab-page freeing races. Incorrect callers can resurrect, leak, or prematurely free files.

## Test Signals

Refcount stress tests with concurrent get/put/close, KCSAN and KASAN under file-table churn, SLAB_TYPESAFE_BY_RCU reuse tests, saturation tests, and warnings from `file_ref_inc()` misuse.
