## sources/control-plane/mayastor/io-engine/src/bdev/util/mod.rs

### Purpose
`bdev/util/mod.rs` declares utility submodules shared by bdev URI adapters and io_uring support.

### Important APIs, Types, And Functions
It exposes `pub(super) mod uri` for URI parsing helpers and `pub mod uring` for kernel io_uring support checks.

### Control Flow
There is no runtime logic in this file; it only controls module visibility.

### State, Persistence, And Dependencies
No state or persistence. Dependencies are the sibling `uri.rs` and `uring.rs` modules.

### Integration Points
Bdev adapters import `crate::bdev::util::uri` for path/query parsing. Other code can import `bdev::util::uring::kernel_support()`.

### Risks
`uri` is `pub(super)`, so helpers are intentionally limited to the bdev module tree. Adding new utility modules here changes public or internal API surface.

### Test Signals
Build tests are sufficient for module visibility; behavior is covered in the submodule reports.
