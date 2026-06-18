<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Makefile -->
## sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Makefile

Purpose: build automation for the Rust optimizer-server across target OS/architecture combinations, with format and clippy gates.

Important targets/variables: `OS`, `ARCH`, architecture/linker maps, `RUST_TARGET`, `RUST_LINKER`, `RUST_TYPE`, `all`, `.release_version`, `.format`, `build`, `release`, `static-release`, and `clean`. `build` runs rustup target add, cargo fmt check, cargo build, cargo clippy with `-Dwarnings`, and installs the binary into `bin/optimizer-server`.

Control flow and state: `release` adds `--release`, static CRT features, and stripping flags before building. `static-release` separately invokes clippy and a static release cargo build. `clean` removes cargo outputs and local bin artifacts.

Dependencies/integration: requires Rust toolchain, rustup, cargo, architecture-specific GNU cross linker, and install utility. It integrates the Rust tool into the repository’s binary output layout.

Risks and test signals: `static-release` repeats `-C target-feature=+crt-static` twice. Cross-linker names assume `<arch>-linux-gnu-gcc` naming and may not exist on hosts. Clippy is run after build in `build`, so format/build failures appear before lint failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Makefile -->
