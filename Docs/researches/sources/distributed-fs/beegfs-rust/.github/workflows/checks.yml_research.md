<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/workflows/checks.yml -->
## sources/distributed-fs/beegfs-rust/.github/workflows/checks.yml

**Purpose:** Pull-request and reusable workflow for Rust formatting, linting, tests, and dependency/license checks.

**Important APIs/types/functions:** Triggers on pull requests except Markdown-only changes and on `workflow_call`. Sets `CARGO_NET_GIT_FETCH_WITH_CLI=true` and `CARGO_LOCKED=1`. Steps checkout, install Rust/clippy/cargo-deny, install nightly rustfmt, then run `make check`, `make test`, and `make deny`.

**Control flow:** A single `checks` job runs on `ubuntu-latest` with read-only contents permission. The Makefile enforces formatting with nightly rustfmt, clippy `-D warnings`, cargo tests, and cargo-deny.

**State and persistence behavior:** No repository state is modified. Cargo lock enforcement makes dependency drift fail CI.

**Dependencies and integration points:** Uses `.github/actions/package/action.yml` indirectly by sharing the same Makefile targets and toolchain assumptions. Depends on `deny.toml`, `about.toml` only through downstream Makefile packaging/compliance targets, and the workspace `Cargo.lock`.

**Risks:** Paths-ignore skips docs-only changes, so CI will not catch broken examples in Markdown. Tool installation is from GitHub Action and rustup network calls. The comment on `CARGO_NET_GIT_FETCH_WITH_CLI` is truncated but the env var is meaningful for git dependencies such as the ThinkParQ protobuf fork.

**Test signals:** A PR touching Rust code should execute this workflow and pass all three Makefile targets with locked dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/workflows/checks.yml -->
