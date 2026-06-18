# sources/distributed-fs/ceph-client/net/ceph/buffer.c

## Purpose
Provides refcounted variable-size buffers for libceph payloads such as decoded ticket blobs and authorizers.

## Important APIs, Types, and Functions
APIs are `ceph_buffer_new()`, `ceph_buffer_release()`, and `ceph_decode_buffer()`. The implementation uses `struct ceph_buffer`, `struct kref`, `kvmalloc()`/`kvfree()`, and Ceph decode helpers.

## Control Flow
`ceph_buffer_new()` allocates the metadata with `kmalloc`, allocates a data vector with `kvmalloc`, initializes the kref and lengths, and returns the buffer. `ceph_buffer_release()` frees the vector and metadata when the kref reaches zero. `ceph_decode_buffer()` decodes a u32 length, bounds-checks the source, allocates a new buffer with `GFP_NOFS`, copies decoded bytes into it, and advances the decode pointer.

## State and Persistence
Buffers are heap objects with kref-managed lifetime. There is no global state or persistence.

## Dependencies and Integration Points
Used by Ceph auth, OSD maps, and other libceph decoders that need refcounted byte vectors. Depends on `linux/ceph/buffer.h`, decode helpers, and libceph `kvmalloc` context.

## Risks
Large decoded lengths can allocate significant memory after only a bounds check against the incoming message. `ceph_decode_buffer()` leaves cleanup to the caller after success and returns `-ENOMEM` or `-EINVAL` on failure. Callers must use `ceph_buffer_put()` or equivalent to release refs.

## Test Signals
Decode zero-length, small, page-sized, and vmalloc-sized buffers; simulate allocation failures; verify kref release under KMEMLEAK; and fuzz truncated length/data combinations.
