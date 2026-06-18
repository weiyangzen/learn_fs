# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lkowner.h

Purpose: `lkowner.h` provides inline helpers for `gf_lkowner_t`, the lock-owner token carried on call stacks and syncop contexts for POSIX/Gluster lock identity. It converts owners to printable hex, initializes owners from pointer/`uint64_t` values, compares owners, detects null owners, and copies owner bytes.

Important APIs and types: `lkowner_unparse()` formats `lkowner->data`; `set_lk_owner_from_ptr()` and `set_lk_owner_from_uint64()` encode little-endian bytes; `is_same_lkowner()` compares length and data with `memcmp`; `is_lk_owner_null()` treats NULL, zero length, or all-zero bytes as no owner; `lk_owner_copy()` copies length and payload. The actual `gf_lkowner_t` type is defined by broader Gluster headers.

Control flow and state: all behavior is inline and caller-owned. No global state or persistence exists. Data is written directly into the caller-provided `gf_lkowner_t` or output buffer.

Dependencies and integration: used by `stack.h` and `syncop.h` to preserve lock ownership across copied call stacks and synthetic sync frames. It relies on standard memory/string routines and on the lock-owner length not exceeding the backing array.

Risks: `lkowner_unparse()` has manual buffer accounting and uses `sprintf` for the non-fast path, so boundary behavior should be tested with small buffers and long owners. Copy/init helpers do not validate destination capacity. Pointer encoding is architecture-size dependent.

Test signals: unit tests should cover same/different owners, null/all-zero owners, 32-bit versus 64-bit length assumptions where applicable, formatting with exactly 16, 17, and truncated buffer sizes, and preservation of owners through `copy_frame()`/syncop-created frames.
