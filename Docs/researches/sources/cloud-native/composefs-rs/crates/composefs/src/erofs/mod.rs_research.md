# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/mod.rs

Purpose: Module root for composefs EROFS support.

Important APIs and types: Re-exports submodules by declaring `composefs`, `debug`, `format`, `reader`, and `writer`.

Control flow: There is no runtime control flow. Rust module resolution uses this file to make the EROFS submodules available as `composefs::erofs::*`.

State and persistence: No state. It defines namespace structure only.

Dependencies and integration: Integrates the composefs-specific overlay metadata, debug utilities, on-disk format definitions, reader, and writer into one public module tree.

Risks: Public module declarations expose these submodules to crate users; renaming or hiding them would be an API change. Keeping reader/writer available here enables fuzz targets and callers to use stable paths.

Test signals: No direct tests are needed beyond compile coverage from imports throughout the crate and fuzz targets.
