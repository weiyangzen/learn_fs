<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/deny.toml -->
## sources/distributed-fs/beegfs-rust/deny.toml

**Purpose:** `cargo-deny` policy for advisories, licenses, duplicate/dependency bans, and allowed sources.

**Important APIs/types/functions:** Graph targets are `x86_64-unknown-linux-gnu` and `x86_64-unknown-linux-musl`; output feature depth is 1; advisory `RUSTSEC-2025-0069` for `daemonize` is ignored with a reason; licenses allow MIT, Apache-2.0, ISC, BSD-3-Clause, Unicode-3.0, and Zlib; private crates are ignored; duplicate versions and wildcard dependencies are allowed; unknown registries/git sources warn; crates.io is allowed; GitHub org `thinkparq` is allowed.

**Control flow:** `make deny` runs `cargo deny $(LOCKED_FLAG) --all-features check`, applying these policies to dependency metadata.

**State and persistence behavior:** No runtime state. It defines CI/release compliance gate behavior.

**Dependencies and integration points:** Used in PR checks and package action. The allowed ThinkParQ GitHub org accommodates the workspace protobuf git dependency.

**Risks:** `unknown-git = "warn"` and empty `allow-git` with org allowance may permit warnings rather than hard failures for unexpected git sources. `multiple-versions = "allow"` avoids dependency churn failures but can hide bloat or vulnerability duplication. Advisory ignore for `daemonize` should be revisited if usage expands.

**Test signals:** `make deny` should pass on locked dependencies; introduce a disallowed license/source in a branch to verify policy severity matches expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/deny.toml -->
