<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/Cargo.toml -->
## sources/cloud-native/ostree/tests/inst/Cargo.toml

Purpose: defines the older installed-test Rust binary `ostree-test`, including non-destructive and destructive OSTree system tests.

Important APIs/types/functions: binary target is `src/insttestmain.rs`; dependencies cover CLI parsing (`structopt`, `clap`), test harness (`libtest-mimic`), OSTree/rpm-ostree bindings, async HTTP serving (`tokio`, `hyper`, `hyper-staticfile`), command shell helpers, random mutation, process/tempdir helpers, and serialization.

Control flow/state: manifest creates an isolated workspace and pulls some git dependencies (`rpmostree-client`, `with-procspawn-tempdir`), which means build reproducibility depends on pinned tags or repository availability.

Dependencies/integration: integrates with kola wrapper installation, destructive test listing, and installed VM tests.

Risks/test signals: old dependency versions may conflict with modern toolchains. Cargo build and `cargo run -- list-destructive` are primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/Cargo.toml -->
