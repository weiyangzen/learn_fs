# sources/cloud-native/nydus/storage/src/lib.rs

Purpose: crate root for `nydus-storage`. It documents the three-layer storage design (backend, cache, device), exports public modules, defines shared RAFS sizing constants, provides a helper macro for metadata getter implementations, and defines the storage-specific error/result type.

Important APIs and control flow: exported modules are `backend`, `cache`, `device`, `factory`, `meta`, and `utils`, with test helpers gated by `cfg(test)`. `impl_getter!` expands simple value-returning getters for upper RAFS metadata types. Constants include default/max chunk sizes, max chunks per blob, and batch merge size-to-gap shift. `StorageError` covers unsupported operations, backend wait timeout, volatile-slice errors, memory overflow, non-continuous ranges, cache-index IO errors, and proxy forbidden/rate-limited cases. Its `Display` implementation provides human-readable messages. `StorageResult<T>` aliases `Result<T, StorageError>`.

State and persistence behavior: no runtime state or persistence is owned here; it establishes shared constants and error contracts consumed throughout storage.

Dependencies and integration points: imports logging, bitflags, and nydus API macros crate-wide. `StorageError` is used by cache state waiting, cache IO helpers, proxy/backends, and device paths that need non-`io::Error` storage status.

Risks and test signals: `StorageError` does not implement `std::error::Error` or automatic conversion here, so callers manually map to `io::Error` when crossing IO APIs. Tests cover display text for proxy forbidden and proxy limited variants.
