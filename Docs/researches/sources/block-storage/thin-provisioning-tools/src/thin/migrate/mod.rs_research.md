# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/mod.rs

This file declares and re-exports migration submodules:

- `pub mod base;`
- `pub mod devices;`
- `pub mod metadata;`
- `pub mod stream;`
- `pub use base::*;`

It makes the high-level migration API from `base.rs` available through the `thin::migrate` module.
