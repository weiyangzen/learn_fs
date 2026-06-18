<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/Makefile -->
## sources/distributed-fs/beegfs-rust/Makefile

**Purpose:** Developer, CI, and packaging command surface for the BeeGFS Rust workspace.

**Important APIs/types/functions:** Targets include `check`, `deny`, `test`, `build`, `clean`, `package`, `clean-package`, `coverage`, and `install-tools`. Variables include `CARGO_TARGET`, `TARGET_FLAG`, `VERSION`, `VERSION_TRIMMED`, `LOCKED_FLAG`, `PACKAGE_DIR`, `TARGET_DIR`, `RELEASE_BUILD_CMD`, `GLIBC_VERSION`, and `BIN_UTIL_PREFIX`.

**Control flow:** Check runs nightly rustfmt and clippy with warnings denied. Package optionally patches `mgmtd/Cargo.toml` for a minimum glibc dependency, generates third-party license HTML, cleans/rebuilds `mgmtd` release with full debug info, splits debug symbols, strips the binary, creates normal/debug DEB and RPM packages, normalizes DEB epoch filenames, and replaces tildes in package filenames. Coverage installs llvm-tools, runs instrumented tests, merges profiles, and reports source coverage.

**State and persistence behavior:** Package builds write to `target/package` and temporarily create `mgmtd/Cargo.toml.orig`; a shell trap restores the manifest. Coverage writes `target/coverage`. Version is derived from git tags and transformed for semver/package metadata.

**Dependencies and integration points:** Used by CI, release workflows, and the composite package action. Depends on cargo tools (`cargo-deny`, `cargo-about`, `cargo-deb`, `cargo-generate-rpm`, `cargo-zigbuild`), binutils, optional Zig, Git tags, and packaging metadata in `mgmtd/Cargo.toml`.

**Risks:** Temporary manifest patching must always restore correctly; failed or interrupted packaging could leave `mgmtd/Cargo.toml.orig` or modified dependency metadata. `.SHELLFLAGS=-cex` exposes command traces in logs. Cross packaging assumes matching `TARGET_DIR` layout and binutils prefix. The release build always uses `--locked`, while non-package build may not unless `CARGO_LOCKED` is set.

**Test signals:** Run `make check`, `make test`, `make deny`, native `make package`, and cross `CARGO_TARGET=aarch64-unknown-linux-gnu BIN_UTIL_PREFIX=aarch64-linux-gnu- GLIBC_VERSION=2.27 make package`; inspect package contents and manifest restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/Makefile -->
