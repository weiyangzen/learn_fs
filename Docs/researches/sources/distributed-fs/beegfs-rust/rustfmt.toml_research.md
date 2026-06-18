<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rustfmt.toml -->
# sources/distributed-fs/beegfs-rust/rustfmt.toml

Purpose: configures formatting style for the BeeGFS Rust workspace.

Important APIs/types/functions: sets `style_edition = "2024"`, groups imports as one block, uses module-level import granularity, wraps comments, and sets comment width to 100.

Control flow: rustfmt reads this file during formatting and applies these choices across crates.

State and persistence: no runtime state; it affects source formatting and review diffs.

Dependencies and integration points: used by developer/CI formatting workflows and must be supported by the pinned Rust/rustfmt version.

Risks: `style_edition = "2024"` and import grouping options require sufficiently new rustfmt support. If contributors use older toolchains, formatting can fail or produce inconsistent output.

Test signals: `cargo fmt --check` or equivalent is the relevant validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rustfmt.toml -->
