<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/build.rs -->
# sources/control-plane/mayastor/io-engine-bench/build.rs

Purpose: Emits linker search and rpath directives so benchmark binaries can find native SPDK-related artifacts in the repository target directory.

Important flow: reads `PROFILE` and `SRCDIR`, builds `$SRCDIR/target/$PROFILE`, then prints `cargo:rustc-link-search=native=...` and `cargo:rustc-link-arg=-Wl,-rpath=...`.

Dependencies: relies on Cargo environment variable `PROFILE` and repository-specific `SRCDIR`. It has no fallback if either is absent.

Integration points: complements `.cargo/runner.sh`; the build script handles link/runtime lookup while the runner handles runtime privileges.

State and persistence: no persisted state. It affects Cargo build output by altering linker arguments for this crate.

Risks and test signals: hardwires native library lookup to a target profile under `SRCDIR`; cross-compilation or custom target directories can break. Test by building the benchmark and checking that generated binaries run without missing shared library errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/build.rs -->
