# File Research: sources/block-storage/thin-provisioning-tools/src/devtools/mod.rs

This module conditionally exports development-only tooling.

It exposes:
- `damage_generator` when the `devtools` feature is enabled.

Integration points:
- Reached from `lib.rs` under `#[cfg(feature = "devtools")]`.

Risks and notes:
- Keeps damaging/corruption helper code out of default builds.
