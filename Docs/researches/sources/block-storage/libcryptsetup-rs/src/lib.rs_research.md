# File Research: sources/block-storage/libcryptsetup-rs/src/lib.rs

Crate root for `libcryptsetup-rs`.

Responsibilities:
- Documents the crate as a safer Rust wrapper over libcryptsetup FFI.
- Declares all internal modules.
- Re-exports public API types and functions.
- Re-exports `libc::{c_int, c_uint, size_t}`.
- Defines `Result<T> = std::result::Result<T, LibcryptErr>`.
- Defines global synchronization state for the `mutex` feature.

Important behavior:
- With `feature = "mutex"`, uses `LazyLock<PerThreadMutex>`.
- Without `feature = "mutex"`, records the initial thread ID and panics on libcryptsetup calls from other threads.
- Contains ignored integration tests that dispatch to `tests::*`.

Research notes:
- Public API surface is intentionally centralized here.
- Comments explain a keyfile-reading workaround where bindings include copied libcryptsetup logic because corresponding free functions are not public.
