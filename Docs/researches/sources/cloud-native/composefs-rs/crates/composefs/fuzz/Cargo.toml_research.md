# sources/cloud-native/composefs-rs/crates/composefs/fuzz/Cargo.toml

Purpose: Configures the cargo-fuzz harness crate for `composefs`.

Important APIs and types: Declares package `composefs-fuzz`, `publish = false`, `cargo-fuzz = true`, its own workspace boundary, dependency on `libfuzzer-sys`, and path dependency on the parent `composefs` crate.

Control flow: Cargo exposes three binaries: `read_image`, `debug_image`, and `generate-corpus`. The first two are libFuzzer targets with tests/docs/bench disabled; the third is a normal corpus generator binary.

State and persistence: The manifest persists fuzz target registration and isolates the fuzz crate from the parent workspace, as required by cargo-fuzz.

Dependencies and integration: Integrates with `cargo fuzz`, LLVM libFuzzer through `libfuzzer-sys`, and the local `composefs` crate. Corpus generation writes under the fuzz crate's `corpus` directories.

Risks: The fuzz crate is intentionally not published and should remain outside normal workspace release semantics. Target names and paths must stay synchronized with files under `fuzz_targets/`.

Test signals: The existence of registered targets is itself a coverage signal for EROFS reader/debug panic resistance. `generate-corpus` seeds both fuzz targets with structured images.
