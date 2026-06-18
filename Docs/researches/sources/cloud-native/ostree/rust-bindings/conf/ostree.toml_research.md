# sources/cloud-native/ostree/rust-bindings/conf/ostree.toml

Purpose: This GIR configuration generates the safe/high-level Rust `ostree` crate bindings for OSTree 1.0. It defines generated, manual, and ignored APIs and applies per-object fixes for nullability, concurrency, string typing, and broken GIR shapes.

Important settings: `work_mode = "normal"`, `target_path = ".."`, `doc_target_path = "../target/vendor.md"`, `deprecate_by_min_version = true`, `trust_return_value_nullability = true`, and `generate_display_trait = true`. The `generate` list includes core objects, enums, flags, repo/sysroot helpers, signing, static delta options, and finder types. The `manual` list includes GLib/Gio types plus hand-written OSTree wrappers such as `KernelArgs`, checkout options, transaction stats, and sysroot deploy options.

Control flow and state: The Makefile feeds this config into `gir`, producing generated modules under `src/auto`. Per-object rules ignore functions that are unsafe, deprecated, private, impossible to represent cleanly, or better handled manually. Feature gates are derived from GIR versions.

Dependencies and integration points: Integrates with gtk-rs/gir, GIR metadata, manual wrapper modules, `ostree-sys`, GLib/Gio crates, docs generation, and CI feature testing. It is the authority for which libostree APIs Rust callers see.

Risks: `trust_return_value_nullability` makes GIR accuracy critical. Ignored APIs can hide functionality, while incorrectly generated APIs can expose unsound lifetimes, invalid arrays, or raw pointer misuse. The config explicitly disables several async finder APIs and checksum APIs due to lifetime/custom checksum concerns, which should be revisited when GIR or manual wrappers improve.

Test signals: `gir-report` for not-bound APIs, compile tests across feature gates, manual wrapper tests for ignored APIs, and diff review after GIR updates. Any change here should be validated against generated `src/auto/mod.rs` exports.
