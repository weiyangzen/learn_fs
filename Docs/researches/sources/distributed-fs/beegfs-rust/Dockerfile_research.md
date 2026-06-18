<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/Dockerfile -->
## sources/distributed-fs/beegfs-rust/Dockerfile

**Purpose:** Simple container build for the BeeGFS Rust management binary.

**Important APIs/types/functions:** Uses `rustlang/rust:nightly`, copies the repository, runs `cargo update`, installs `sqlite3`, builds `cargo build --release --bin mgmtd`, creates `/auth_file`, creates `/var/lib/beegfs`, and switches working directory to `/project/target/release`.

**Control flow:** The image builds everything inside a Rust nightly container and leaves the release binary directory as the final working directory.

**State and persistence behavior:** The image bakes in a generated auth file containing `shared_secret` and creates a BeeGFS data directory. `cargo update` mutates dependency resolution during image build rather than respecting the checked-in lockfile.

**Dependencies and integration points:** Depends on the workspace build, Rust nightly image, apt repository availability, and SQLite runtime tooling. It is separate from the package/release pipeline, which uses Makefile package targets.

**Risks:** `cargo update` harms reproducibility and can diverge from CI/release builds using `--locked`. The image retains the full source tree and build artifacts rather than producing a slim runtime image. A hard-coded shared secret is unsafe for production.

**Test signals:** Build the Docker image, run `/project/target/release/beegfs-mgmtd --help`, and verify runtime config/auth handling is overridden for real deployments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/Dockerfile -->
