## sources/distributed-fs/beegfs-rust/sqlite/src/lib.rs

### Purpose
Crate root for the SQLite helper crate.

### Important APIs, Types, and Functions
- Private modules: `connection`, `migration`, and `transaction`.
- Publicly re-exports all items from those modules with `pub use`.

### Control Flow and State
No runtime behavior. It defines the public API surface.

### Dependencies and Integration Points
Consumers import connection pooling, migration, and transaction extension helpers from this crate root.

### Risks and Edge Cases
Glob re-exports make all helper names part of the public API and can create name collisions as modules grow.

### Test Signals
Compile checks validate exports; behavior tests live in child modules.
