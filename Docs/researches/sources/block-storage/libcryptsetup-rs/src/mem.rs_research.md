# File Research: sources/block-storage/libcryptsetup-rs/src/mem.rs

Implements safe-zeroing and safe-free memory handles.

Key types:
- `SafeMemzero` trait behind `cryptsetup23supported`
- `SafeOwnedMemZero` behind `cryptsetup23supported`
- `SafeBorrowedMemZero` behind `cryptsetup23supported`
- `SafeMemHandle`

Behavior:
- Uses macros to define pointer-plus-size memory handles.
- Drop for safe-zero handles calls `safe_memzero`, and owned variants can additionally call `libc::free`.
- `SafeMemHandle` drops with `crypt_safe_free`.
- `SafeMemHandle::alloc` uses `crypt_safe_alloc` behind `cryptsetup23supported`.
- Implements `AsRef<[u8]>` and `AsMut<[u8]>` for memory views.
- Marks `SafeMemHandle` as `Send`.

Research notes:
- Safety depends on pointer provenance and exact size correctness; docs warn about memory corruption if wrong.
- `SafeMemHandle` is used by keyfile contents to ensure key material is cleaned up.
- Tests cover explicit zeroing and borrowed-memory zeroing.
