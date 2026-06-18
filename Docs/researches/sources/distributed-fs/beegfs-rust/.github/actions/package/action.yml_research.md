<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/actions/package/action.yml -->
## sources/distributed-fs/beegfs-rust/.github/actions/package/action.yml

**Purpose:** Composite GitHub Action that builds BeeGFS Rust RPM and DEB packages for x86_64, aarch64, or both.

**Important APIs/types/functions:** Inputs are `build-targets` (`x86_64`, `aarch64`, or `both`) and `skip-deny`. Steps install Rust tools through `moonrepo/setup-rust`, install `gcc-aarch64-linux-gnu`, `dpkg-sig`, `rpm`, `gnupg2`, nightly rustfmt, Zig 0.13, run `make check`, optional `make deny`, `make test`, set `VERSION` from tags, run `make package` per architecture, and generate `target/package/checksums.txt`.

**Control flow:** The action prepares all build dependencies, validates formatting/lint/tests/compliance, conditionally builds x86_64 unless only aarch64 was requested, conditionally builds aarch64 unless only x86_64 was requested, and finally hashes any produced `.rpm` or `.deb` files.

**State and persistence behavior:** It writes tools into the runner, exports `VERSION` through `GITHUB_ENV`, places Zig on `GITHUB_PATH`, and emits packages/checksums under `target/package`. It does not publish artifacts by itself; release workflow consumes the package directory.

**Dependencies and integration points:** Depends on the repository Makefile, Cargo packaging tools (`cargo-deny`, `cargo-about`, `cargo-generate-rpm`, `cargo-deb`, `cargo-zigbuild`), the cargo aarch64 linker config, and the release workflow.

**Risks:** Uses network installs and a direct Debian package URL, so runner availability and upstream package movement can break builds. `skip-deny` can bypass compliance checks. Zig is pinned because newer releases are noted as problematic; updating `cargo-zigbuild` or Zig requires packaging validation. The action assumes Ubuntu runners and apt.

**Test signals:** Invoke via workflow_call or release workflow for all three `build-targets` modes; verify `make check`, `make test`, `make deny`, generated packages, and `checksums.txt` for both architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/actions/package/action.yml -->
