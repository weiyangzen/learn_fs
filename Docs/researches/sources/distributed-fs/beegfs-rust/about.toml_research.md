<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/about.toml -->
## sources/distributed-fs/beegfs-rust/about.toml

**Purpose:** `cargo-about` configuration for third-party license report generation.

**Important APIs/types/functions:** Accepts `MIT`, `Apache-2.0`, `ISC`, `BSD-3-Clause`, `Unicode-3.0`, and `Zlib`; targets `x86_64-unknown-linux-gnu` and `x86_64-unknown-linux-musl`; ignores private workspace crates.

**Control flow:** The Makefile package target runs `cargo about generate about.hbs --all-features -o $(TARGET_DIR)/thirdparty-licenses.html`, using this policy to include approved dependency licenses.

**State and persistence behavior:** No runtime state. It determines generated package documentation content.

**Dependencies and integration points:** Used by `cargo-about` during packaging and the package metadata that installs `thirdparty-licenses.html`.

**Risks:** Target list omits aarch64 even though packages are built for aarch64, so license resolution may not perfectly reflect cross-target dependencies if any are target-specific. Any dependency with an unaccepted license needs policy update or replacement.

**Test signals:** Run `cargo about generate about.hbs --all-features` during package builds and verify the resulting HTML is packaged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/about.toml -->
