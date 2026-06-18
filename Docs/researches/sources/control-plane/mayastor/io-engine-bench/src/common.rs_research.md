<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/common.rs -->
# sources/control-plane/mayastor/io-engine-bench/src/common.rs

Purpose: Re-exports the entire `io_engine_tests` crate into the benchmark crate under a local `common` module.

Important APIs/types/functions: `pub use io_engine_tests::*` makes test helpers, compose support, MayastorTest, bdev/nexus builders, and macros visible through `common::...`.

Dependencies: the file depends wholly on the `io-engine-tests` crate declared as a dev dependency. There is no local logic or state.

Integration points: `src/nexus.rs` imports `common::compose` and calls `common::composer_init()`, using this file as a compatibility shim rather than importing `io_engine_tests` directly everywhere.

State and persistence: no state; all state comes from re-exported modules.

Risks and test signals: broad wildcard re-export can hide where APIs come from and may expose unrelated test helpers to benchmarks. Compile failures in this file generally indicate `io-engine-tests` dependency or module export changes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/common.rs -->
