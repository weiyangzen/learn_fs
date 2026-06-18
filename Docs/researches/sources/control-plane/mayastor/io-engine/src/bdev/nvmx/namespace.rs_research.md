## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/namespace.rs

### Purpose
`nvmx/namespace.rs` wraps an SPDK NVMe namespace pointer and exposes geometry, identity, alignment, metadata, and feature capability queries.

### Important APIs, Types, And Functions
`NvmeNamespace(NonNull<spdk_nvme_ns>)` exposes `size_in_bytes()`, `block_len()`, `num_blocks()`, `uuid()`, `supports_compare()`, `supports_deallocate()`, `supports_write_zeroes()`, `alignment()`, `md_size()`, `from_ptr()`, and `as_ptr()`.

### Control Flow
Methods are thin unsafe calls to SPDK namespace getters. `from_ptr()` converts a raw namespace pointer to `NonNull` and panics on null. Capability methods inspect SPDK flags for deallocate and write-zeroes support.

### State, Persistence, And Dependencies
The wrapper stores only the raw namespace pointer and is marked `Send`/`Sync`. It depends on the controller lifetime keeping the SPDK namespace valid and on `spdk_rs::Uuid` conversion.

### Integration Points
`controller.rs` populates namespaces after attach and AER changes. `device.rs` exposes namespace geometry and capabilities through `BlockDevice`. `handle.rs` uses `as_ptr()` for every namespace command.

### Risks
The file itself questions whether `NvmeNamespace` is truly `Send`/`Sync`; this is a real safety contract with SPDK. Any use after controller detach is undefined. `alignment()` returns optimal I/O boundary, which may not be a memory alignment in all contexts.

### Test Signals
Use SPDK-backed tests or mocks for geometry, UUID conversion, capability flags, metadata size, null pointer panic, and namespace lifetime across controller removal.
