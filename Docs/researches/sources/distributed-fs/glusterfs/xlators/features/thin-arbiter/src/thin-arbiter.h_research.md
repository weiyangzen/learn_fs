# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.h

## Purpose
Declares thin-arbiter constants, stack helper macros, and the per-fop state used by `thin-arbiter.c`.

## Important APIs, Types, and Functions
- `THIN_ARBITER_SOURCE_XATTR` names `trusted.ta.source`; `THIN_ARBITER_SOURCE_SIZE` is `2`.
- `TA_FAILED_FOP()` centralizes unsupported-fop failure callbacks.
- `TA_STACK_UNWIND()` releases `ta_fop_t` from `frame->local` before strict unwind.
- `struct _ta_fop` stores xattrop flags, `loc`, `fd`, incoming dict, generated brick-xattr dict, two on-disk indicators, and an index.

## Control Flow
The header is passive, but `TA_STACK_UNWIND()` shapes callback control flow by guaranteeing local cleanup before returning to the caller.

## State and Persistence
Defines only per-call state. No global state. The `loc`, `fd`, and dict members are refcounted or wiped by `ta_release_fop()`.

## Dependencies and Integration Points
Includes GlusterFS locking, xlator, and list headers. Its macros depend on GlusterFS default callback names and `STACK_UNWIND_STRICT`.

## Risks
The fixed `on_disk[2]` model mirrors thin-arbiter's two-source assumption; future replication layouts or dict sizes need bounds-aware changes. Macro side effects require valid `frame` and `frame->local` conventions.

## Test Signals
Compile-time inclusion plus runtime xattrop/fxattrop tests confirm macro cleanup, refcounts, and state copying.
