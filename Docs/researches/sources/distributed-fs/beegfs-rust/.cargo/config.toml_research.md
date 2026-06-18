<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.cargo/config.toml -->
## sources/distributed-fs/beegfs-rust/.cargo/config.toml

**Purpose:** Cargo target configuration for cross-compiling the workspace to `aarch64-unknown-linux-gnu`.

**Important APIs/types/functions:** Defines `[target.aarch64-unknown-linux-gnu] linker = "aarch64-linux-gnu-gcc"`.

**Control flow:** Cargo reads this file automatically and uses the configured linker when `CARGO_BUILD_TARGET`, `--target`, or package scripts request the aarch64 GNU target.

**State and persistence behavior:** No runtime state. It persists build-tool selection in source control and affects reproducible packaging.

**Dependencies and integration points:** Integrates with `.github/actions/package/action.yml`, which installs `gcc-aarch64-linux-gnu`, and with Makefile packaging variables `CARGO_TARGET=aarch64-unknown-linux-gnu` and `BIN_UTIL_PREFIX=aarch64-linux-gnu-`.

**Risks:** Builds fail if the cross linker is missing or named differently on the runner. This config only handles the linker; binutils and libc compatibility are still managed by CI and the Makefile.

**Test signals:** Run `cargo build --target aarch64-unknown-linux-gnu` or the package action's aarch64 path on a machine with the cross compiler installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.cargo/config.toml -->
