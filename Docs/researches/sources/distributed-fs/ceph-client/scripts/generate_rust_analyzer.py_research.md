# sources/distributed-fs/ceph-client/scripts/generate_rust_analyzer.py

## Purpose
Builds `rust-project.json` for `rust-analyzer` so kernel Rust crates, generated bindings, sysroot crates, proc macros, scripts, samples, drivers, and optional external modules can be indexed without Cargo metadata.

## APIs, Control Flow, and State
The main API is `generate_crates(srctree, objtree, sysroot_src, external_src, cfgs, core_edition)`, returning a list of typed crate dictionaries. It reads `include/generated/rustc_cfg`, parses `--cfgs crate=values` with `args_crates_cfgs()`, shells out through `invoke_rustc()` using `$RUSTC` for crate names and proc-macro dylib names, then registers crates in dependency order. Helpers create sysroot crates (`core`, `alloc`, `std`, `proc_macro`), vendored support crates (`compiler_builtins`, `proc_macro2`, `quote`, `syn`), proc macros, generated crates (`bindings`, `uapi`, `kernel` with `OBJTREE` and include/exclude source metadata), Rust scripts referenced from `scripts/Makefile`, and root crates under `samples`/`drivers` or `exttree` when matching Makefile/Kbuild targets exist.

## Dependencies and Integration
It depends on Python 3, `RUSTC`, kernel Rust source layout, generated object-tree files, sysroot source layout, and `rust-analyzer`'s JSON schema. State is transient in the `crates` list and emitted JSON only.

## Risks and Test Signals
Risks include stale generated cfgs, missing proc-macro dylibs, mismatched sysroot editions, false positives/negatives in root-crate detection, and JSON paths that are valid only for the current tree. Test signals are valid JSON, rust-analyzer loading without unresolved core/kernel crates, `--verbose` logs for discovered external crates, and build-system tests that regenerate project metadata after Rust layout changes.
