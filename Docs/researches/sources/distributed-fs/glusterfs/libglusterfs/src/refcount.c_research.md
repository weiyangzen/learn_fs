# sources/distributed-fs/glusterfs/libglusterfs/src/refcount.c

## Purpose

`refcount.c` implements the small `gf_ref_t` intrusive reference-count helper used by libglusterfs objects that need atomic lifetime management and an optional release callback. It centralizes get, put, and initialization semantics around Gluster's atomic and assertion macros.

## Important APIs, Types, and Functions

The exported internal functions are `_gf_ref_init()`, `_gf_ref_get()`, and `_gf_ref_put()`. `gf_ref_t` carries an atomic `cnt`, a `release` callback of type `gf_ref_release_t`, and a `data` pointer. `_gf_ref_init()` initializes the count to one and stores callback/data. `_gf_ref_get()` atomically increments and returns the referenced data. `_gf_ref_put()` atomically decrements, invokes `release(data)` on the final put, and returns whether the object still has references.

## Control Flow and Data Flow

Initialization sets the initial ownership reference. Readers call `_gf_ref_get()` before using the associated object; the function uses fetch-add and asserts the previous count was nonzero, because acquiring a reference after final release is a fatal protocol error. Releasers call `_gf_ref_put()`; fetch-sub returns the previous count, the final owner is detected by `cnt == 1`, and the release callback runs synchronously in the caller's context.

## State and Persistence Behavior

All state is in-memory only. The only persistent effect is any side effect performed by the caller-provided release callback. The atomic counter is the sole concurrency state, but object-level locking is still required to prevent racing a get against teardown after count reaches zero.

## Dependencies and Integration Points

This file depends on `glusterfs/common-utils.h` for `GF_ASSERT` and atomic helpers and on `glusterfs/refcount.h` for the public type contract. It integrates with any libglusterfs structure embedding `gf_ref_t`; callers own storage allocation and release-callback behavior.

## Risks and Edge Cases

The helper asserts rather than gracefully handling over-put or get-after-free situations. A race where two threads try to get after count reaches zero can allow only one to observe zero, but any zero observation is treated as a fatal bug. The release callback runs inline and must not assume external locks unless the caller's ownership rules guarantee them. Returning `NULL` from `_gf_ref_get()` after count zero is defensive but should never be relied on as normal flow.

## Test Signals

Useful tests cover initial count behavior, multiple get/put sequences, final release callback exactly once, no release before the final put, and assertion coverage for over-put or get-after-zero in debug builds. Threaded stress should verify no double release when many holders drop references concurrently.
