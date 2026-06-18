# File Research: sources/block-storage/thin-provisioning-tools/src/era/mod.rs

This is the era module declaration file.

It exports:
- `check`
- `dump`
- `invalidate`
- `ir`
- `repair`
- `restore`
- `superblock`
- `writeset`
- `xml`

It conditionally exports:
- `metadata_generator` under the `devtools` feature.

Integration points:
- Used by `lib.rs` to expose era functionality to the crate.
