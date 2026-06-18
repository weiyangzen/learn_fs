# File Research: sources/block-storage/thin-provisioning-tools/src/lib.rs

This is the crate root module declaration file.

It enables test-only quickcheck crates and exposes major modules:
- cache, checksum, commands, copier, dump_utils, era, file_utils, grid_layout, io_engine, ioctl, math, pack, pdata, report, run_iter, shrink, thin, units, utils, version, write_batcher, xml.

Conditional exports:
- `random` under test or `devtools`.
- `devtools` under the `devtools` feature.

It also re-exports:
- `utils::hashvec`

Integration points:
- Defines the public module surface for the thin-provisioning-tools Rust crate.
