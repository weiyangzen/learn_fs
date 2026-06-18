<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bitmap.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/bitmap.rs

## Purpose
This file wraps Linux C bitmap APIs in Rust, providing borrowed `Bitmap` views and owned `BitmapVec` storage with inline or allocated representation.

## Important APIs, Types, and Functions
`Bitmap` is an unsized wrapper over a bit-length metadata slice and exposes unsafe `from_raw`, `from_raw_mut`, `as_ptr`, `as_mut_ptr`, and `len`. `BitmapVec` owns either a single inline `usize` bitmap or a `bitmap_zalloc` allocation via `BitmapRepr`, with constants `MAX_LEN` and `MAX_INLINE_LEN`. Bitmap operations include non-atomic `set_bit`/`clear_bit`, relaxed atomic `set_bit_atomic`/`clear_bit_atomic`, `copy_and_extend`, `last_bit`, `next_bit`, and `next_zero_bit`. `BitmapVec::new_inline`, `new`, and optional benchmark-only `fill_random` manage owned storage.

## Control Flow and State
`BitmapVec::new` selects inline zeroed storage for lengths up to one machine word, rejects sizes above `i32::MAX`, otherwise allocates zeroed C bitmap memory. Deref/DerefMut choose the correct pointer and build a borrowed `Bitmap` with bit-length metadata. Out-of-bounds mutating operations either panic under `CONFIG_RUST_BITMAP_HARDENED` or log and return under non-hardened builds. Search operations call C `_find_*` helpers and translate indexes at or beyond `len` into `None`.

## State and Persistence Behavior
Inline state lives directly in `BitmapVec::repr.bitmap`. Larger state persists in a C allocation freed by `Drop` through `bitmap_free`. Borrowed `Bitmap` references do not own memory and require the caller or owning `BitmapVec` to keep the backing storage alive.

## Dependencies and Integration Points
This module depends on `crate::bindings` for bitmap helpers, `AllocError`, allocation `Flags`, optional `pr_err!`, and kernel config gates. It is intended to interoperate with C APIs expecting `unsigned long *` bitmap storage.

## Risks
Atomic and non-atomic operations must not be mixed unsafely by callers. The unsized `Bitmap` cast relies on careful metadata interpretation: length is in bits while the backing memory is `usize` words. Non-hardened out-of-bounds behavior silently ignores writes after logging, which can hide caller bugs. Allocation length conversion to `u32` assumes prior `MAX_LEN` validation.

## Test Signals
KUnit tests cover borrowing raw arrays/words, allocation at several sizes, rejection of too-large lengths, set/clear/find semantics, non-hardened out-of-bounds behavior, and `copy_and_extend` clearing old destination bits. Hardened panic tests are noted but blocked by KUnit cfg/should-panic support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bitmap.rs -->
