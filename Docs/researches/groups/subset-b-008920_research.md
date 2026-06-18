# subset-b-008920 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/tikv_trouble_shooting.json -->
# sources/storage-engines/tikv/metrics/grafana/tikv_trouble_shooting.json

## Purpose
This file is a generated Grafana dashboard named `Test-Cluster-TiKV-Trouble-Shooting` with UID `Lg4wiEkZz`, schema version 18, and version 4. It gives TiKV operators a symptom-oriented troubleshooting view across hot read, hot write, leader drops, channel saturation, server busy errors, slow reads, slow writes, RocksDB write stalls, OOM, and huge region conditions.

## Important Structures
The top-level JSON uses standard Grafana dashboard fields: `__inputs`, `__requires`, `annotations`, `panels`, `templating`, `time`, `timepicker`, `refresh`, `timezone`, `title`, `uid`, and `version`. It contains 80 panel objects in total: 10 `row` panels that group symptom areas and 70 `graph` panels that visualize Prometheus expressions. The dashboard depends on the `${DS_TEST-CLUSTER}` Prometheus datasource and includes the default `Annotations & Alerts` annotation entry.

## Variables and Queries
Templating variables scope every panel to a TiDB/TiKV deployment. `k8s_cluster` is derived from `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`, `tidb_cluster` is filtered by `k8s_cluster`, `db` is a multi/all database selector derived from block cache metrics, `command` is a multi/all command selector from `tikv_storage_command_total`, and `instance` is a multi/all TiKV instance selector from `tikv_engine_size_bytes`. Most graph expressions use `$k8s_cluster`, `$tidb_cluster`, and `instance=~"$instance"` to keep a consistent drill-down path.

## Control Flow and Operational Story
Grafana evaluates this file declaratively: variables are resolved first, rows organize panels, and panel targets execute PromQL on refresh. The panel sequence follows common TiKV incident triage: resource pressure first for hot read/write, then raft leadership movement, channel fullness, busy signals, read and write latency breakdowns, RocksDB write-stall causes, memory pressure, and region-size skew. The graph targets primarily use `rate`, `irate`, `histogram_quantile`, `sum`, and `avg` over one-minute or five-minute windows.

## State and Persistence
There is no runtime application state in this JSON, but it is persistent dashboard state for Grafana. It stores layout coordinates, panel configuration, variable definitions, refresh behavior, schema metadata, and the stable UID. The file is expected to be regenerated from dashboard Python sources and guarded by `scripts/check-dashboards` through a `.sha256` checksum.

## Dependencies and Integration Points
The dashboard integrates with Prometheus metrics emitted by TiKV, RocksDB, raftstore, coprocessor, scheduler, gRPC, process exporters, and node disk exporters. Important metric families include `tikv_thread_cpu_seconds_total`, `tikv_grpc_msg_duration_seconds_*`, `tikv_raftstore_*`, `tikv_engine_*`, `tikv_scheduler_*`, `tikv_channel_full_total`, `tikv_coprocessor_*`, `process_cpu_seconds_total`, `process_resident_memory_bytes`, and `node_disk_*`. It is integrated into the repository maintenance flow through `scripts/gen-tikv-details-dashboard`, which runs grafanalib generation in Docker, and `scripts/check-dashboards`, which rejects manual JSON drift.

## Risks
The largest risk is silent metric drift: renamed labels or metric families will leave panels empty even though the JSON remains syntactically valid. The dashboard also assumes Kubernetes/TiDB cluster labels are present on TiKV and node-exporter metrics. Some very high quantiles such as `0.999999` can be noisy on sparse histograms. Disk panels do not always constrain `instance` directly, so label alignment between TiKV and node metrics must be validated in the deployment. Manual edits are risky because the checksum gate expects generated output.

## Test Signals
Useful validation signals are successful JSON parsing, Grafana import/load, PromQL execution against a representative Prometheus dataset, and `./scripts/check-dashboards` passing against the matching `.sha256` file. Empty variable dropdowns or blank row sections indicate integration breakage even if the file passes checksum validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/tikv_trouble_shooting.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/patches/tempdir/Cargo.toml -->
# sources/storage-engines/tikv/patches/tempdir/Cargo.toml

## Purpose
This manifest defines a local, unpublished crate named `tempdir` at version `0.3.7`. It is a compatibility patch for code that expects the historical `tempdir` API while delegating the implementation to the maintained `tempfile` crate.

## Important Fields
The package uses Rust edition 2021, `publish = false`, and dual `MIT OR Apache-2.0` licensing. Its only dependency is `tempfile = "3"`, which provides secure temporary directory creation and ownership transfer.

## Control Flow and Build Behavior
Cargo treats this as a normal local package when the workspace or patch configuration points `tempdir` dependencies at `patches/tempdir`. There are no features, build scripts, binaries, or examples in this manifest.

## State and Persistence
No persistent state is declared by the manifest. Runtime filesystem state is created by `src/lib.rs` through `tempfile` and removed by the compatibility wrapper's `Drop` or `close` behavior.

## Dependencies and Integration Points
The crate integrates into TiKV as a dependency override or local patch target. It narrows the dependency surface to `tempfile` and avoids publishing patched compatibility code to crates.io.

## Risks
The version number intentionally mirrors the old crate version, so consumers may assume exact upstream behavior. API or semantic mismatches must be checked in `src/lib.rs`, especially around ownership transfer and cleanup errors.

## Test Signals
Relevant checks are `cargo check` for crates that depend on `tempdir`, tests that create, persist, and close temporary directories, and dependency graph inspection to ensure the intended local crate is selected.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/patches/tempdir/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/patches/tempdir/src/lib.rs -->
# sources/storage-engines/tikv/patches/tempdir/src/lib.rs

## Purpose
This source implements the local `tempdir` compatibility API on top of `tempfile::Builder`. It exposes a `TempDir` type with the familiar creation, path access, persistence, explicit close, `AsRef<Path>`, `Debug`, and automatic cleanup behavior.

## Important APIs and Types
`TempDir` stores `path: Option<PathBuf>` so ownership can be consumed exactly once. `TempDir::new(prefix)` creates a temporary directory under `env::temp_dir()`. `TempDir::new_in(tmpdir, prefix)` accepts any `AsRef<Path>`, normalizes relative bases against `env::current_dir()`, creates the directory with `tempfile::Builder::prefix(prefix).tempdir_in(base)`, and stores the path from `TempDir::into_path()`. `path(&self)` returns `&Path`, `into_path(self)` prevents cleanup by taking the path, and `close(self)` removes the directory with `fs::remove_dir_all`.

## Control Flow
Creation flows through `new` to `new_in`. `new_in` resolves the base directory, creates a `tempfile::TempDir`, converts it into a persisted path with `into_path`, and wraps it in `Some`. `close` removes the current path, sets the option to `None`, and returns the removal result. `Drop` checks whether the option still contains a path and best-effort removes it, ignoring errors.

## State and Persistence
The only state is the optional path. A live `Some(path)` means the wrapper owns cleanup. `into_path` transfers persistence to the caller and leaves `None`, so `Drop` no longer deletes it. `close` consumes the wrapper, attempts deletion, and clears the path before returning. The code uses `unwrap()` in `path` and `into_path`, relying on the public consuming API to avoid post-consumption access.

## Dependencies and Integration Points
The implementation depends on `std::env`, `std::fmt`, `std::fs`, `std::io`, `std::path`, and `tempfile`. It integrates with code expecting `tempdir::TempDir` while inheriting actual directory creation behavior from `tempfile`.

## Risks
`tempfile::TempDir::into_path()` is used to disable `tempfile`'s own drop cleanup and reimplement cleanup locally; that keeps API compatibility but means cleanup errors are ignored in `Drop`. `path().unwrap()` will panic if called after `into_path` or internal clearing, though normal ownership makes that hard from safe external calls. Relative path normalization can fail if `current_dir` is unavailable. Symlink and permission behavior follows `remove_dir_all`.

## Test Signals
Useful tests should assert directory existence after `new`/`new_in`, deletion after drop and `close`, survival after `into_path`, relative base handling, and `Debug`/`AsRef<Path>` output. Cargo tests in downstream crates are also important because this is a compatibility shim.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/patches/tempdir/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/rust-toolchain.toml -->
# sources/storage-engines/tikv/rust-toolchain.toml

## Purpose
This file pins the Rust toolchain used by rustup-aware commands in the TiKV source tree. It makes local development and CI use `nightly-2026-01-30` with a minimal profile.

## Important Settings
The `[toolchain]` table sets `channel = "nightly-2026-01-30"`, `profile = "minimal"`, and installs `rustfmt`, `clippy`, `rust-src`, and `rust-analyzer`. The selected nightly supports unstable rustfmt options and any nightly-only build flags used by scripts such as frame-pointer builds.

## Control Flow and State
There is no executable control flow. rustup reads this file when a command runs under the repository and selects or installs the pinned toolchain and listed components. Toolchain state is persisted in the user's rustup installation, not in the repo.

## Dependencies and Integration Points
The file is consumed by rustup, Cargo, rustfmt, clippy, rust-analyzer, and scripts that call cargo or rustup. It pairs with `rustfmt.toml`, `scripts/clippy`, `scripts/test`, and `scripts/run-cargo.sh`.

## Risks
Using a nightly pin means the repository depends on rustup availability and the continued availability of the exact nightly. CI images or offline developer environments missing this toolchain will fail before code compilation. Updating the pin can change lint, formatting, or compiler behavior across the whole tree.

## Test Signals
Signals include `rustup show active-toolchain`, `cargo check`, `cargo clippy`, `cargo fmt --check`, and rust-analyzer startup using the expected channel and components.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/rust-toolchain.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/rustfmt.toml -->
# sources/storage-engines/tikv/rustfmt.toml

## Purpose
This file defines repository-wide Rust formatting policy. It opts into Rust 2024 style formatting and unstable rustfmt features, so it must be used with the pinned nightly toolchain.

## Important Settings
The config enables `style_edition = "2024"` and `unstable_features = true`. It wraps and normalizes comments, formats code in doc comments, formats macro bodies and matchers, normalizes doc attributes, condenses wildcard suffixes, forces Unix newlines, uses field-init and `?` shorthand, groups imports by crate, and uses crate-level import granularity.

## Control Flow and State
Rustfmt reads this file when formatting Rust sources. It does not maintain state, but it deterministically rewrites source formatting and can affect generated diffs across the repository.

## Dependencies and Integration Points
The file depends on a rustfmt version that supports the configured unstable options. It integrates with developer formatting, CI format checks, editor integrations, and the `rust-toolchain.toml` component list.

## Risks
Because unstable rustfmt options are enabled, updating the nightly can change formatting output. Formatting macro bodies and doc-comment code can touch areas that older rustfmt versions ignore. Import grouping and granularity can create large mechanical diffs if run after toolchain changes.

## Test Signals
The primary signal is `cargo fmt --check` or `rustfmt --check` under `nightly-2026-01-30`. Unexpected large diffs after a toolchain bump indicate policy drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/rustfmt.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-bins.py -->
# sources/storage-engines/tikv/scripts/check-bins.py

## Purpose
This Python CI helper verifies binary-linkage and CPU-instruction expectations. It checks that test binaries link jemalloc when enabled, release binaries use SSE4.2 when requested, selected system libraries are statically linked, and OpenSSL linkage matches the enabled feature set.

## Important APIs and Functions
`ensure_link(args, require_static, libs)` uses `ldd` on Linux to require or forbid dynamic libraries. `check_jemalloc(executable)` scans `readelf -s` output for jemalloc symbols. `check_sse(executable)` uses `nm` and `objdump` to confirm `crc32c_3way` contains the SSE4.2 `crc32` opcode. `check_openssl(executable, is_static_link)` validates `libcrypto`/`libssl` linkage and rejects embedded OpenSSL text symbols when dynamic linking is expected. `check_tests(features)` consumes Cargo JSON messages on stdin and checks each test executable except a whitelist. `check_release(features, args)` checks explicitly supplied release binaries. `main()` parses optional `--features`, then dispatches to `--check-tests` or `--check-release`.

## Control Flow
The script splits enabled features, branches between test and release modes, and exits with status 1 at the first hard failure. Test mode reads all stdin lines, ignores non-JSON and non-executable entries, derives binary names from paths, skips known whitelist prefixes, and validates jemalloc plus static OpenSSL. Release mode first forbids dynamic `libstdc++`, then conditionally validates jemalloc, SSE4.2, and OpenSSL based on feature names.

## State and Persistence
The script has no persistent state. It reads binary files and command output from the current system and reports progress to stdout, using carriage-return updates on TTYs.

## Dependencies and Integration Points
It depends on Linux tooling (`ldd`, `readelf`, `nm`, `objdump`, `uname`), Python standard libraries, Cargo JSON output, and TiKV feature names such as `jemalloc`, `sse`, and `openssl-vendored`. `scripts/test-all` pipes `cargo test --message-format=json-render-diagnostics -q --no-run` into it for test-binary validation.

## Risks
The script constructs shell commands with filenames and `os.popen`, so unusual paths can break parsing. Linux-only inspection is skipped on non-Linux systems. Symbol names and opcode assumptions are tightly coupled to current allocator, RocksDB CRC, and OpenSSL builds. `is_sse_enabled` checks for substring `sse`, which is simple but broad.

## Test Signals
A passing run prints checked binaries and exits 0. Useful negative tests include binaries without jemalloc symbols, release binaries missing `crc32`, and dynamic OpenSSL/static OpenSSL mismatches. CI coverage comes indirectly from `scripts/test-all`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-bins.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-build-opts.py -->
# sources/storage-engines/tikv/scripts/check-build-opts.py

## Purpose
This Python 3 script verifies that individual TiKV crates build under important feature combinations. It protects against workspace-level feature coupling that lets the whole repository build while individual crates fail.

## Important APIs and Functions
It discovers component crates by listing `components/`, adds `cmd`, `tests`, and root `tikv`, and stores `(crate, path)` pairs in `crates`. `cargo_run_default` runs `cargo check -p` or `cargo test -p --no-run` with default features. `cargo_run_test_engines` runs crates that contain `test-engines-rocksdb` with `--no-default-features --features test-engines-{engines}`. `cargo_run_test_engines_ext` separately selects `test-engine-kv-{kv_engine}` and `test-engine-raft-{raft_engine}`. `run_and_collect_errors` records failing commands. `get_features` reads each crate's `Cargo.toml` and detects whether test-engine features are present by substring.

## Control Flow
The script builds the crate list at import time, then runs eight phases: default check, panic test engines check, RocksDB test engines check, split KV/Raft engine check, and the same combinations under `cargo test --no-run`. It accumulates failures instead of stopping at the first one, prints an error list, and exits 1 if any command failed.

## State and Persistence
No repository state is modified beyond Cargo's normal target/cache outputs. The global `errors` list is in-memory state used to summarize failures.

## Dependencies and Integration Points
It depends on Python 3.6+, Cargo, the TiKV workspace layout, component crates under `components/`, and feature naming conventions in `Cargo.toml`. It integrates with CI or developer validation for feature hygiene.

## Risks
Feature detection is string-based and can produce false positives from comments or miss renamed features. The script assumes it runs from the repository root. It can be expensive because it invokes many cargo checks/tests serially. Newly added non-component crates must be represented by the discovery logic or `other_crates`.

## Test Signals
Success is exit 0 with no recorded errors. Failure output lists each exact cargo command that failed, which is useful for reproducing feature configuration regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-build-opts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-dashboards -->
# sources/storage-engines/tikv/scripts/check-dashboards

## Purpose
This bash script verifies that generated Grafana dashboard JSON files have not been manually edited. It compares every `./metrics/grafana/*.sha256` checksum file against the corresponding dashboard output.

## Important Commands
The script enables `set -euo pipefail`, loops over checksum files, runs `sha256sum -c "$sha256"`, derives the dashboard name from the checksum filename on failure, and tells the user to run `./scripts/gen-tikv-details-dashboard`.

## Control Flow
Every checksum must validate. The first failed checksum prints remediation guidance and exits 1. If all checks pass, it prints `Dashboards check passed.`

## State and Persistence
The script does not write state. It reads checksum files and dashboard JSON files from `metrics/grafana`.

## Dependencies and Integration Points
It depends on GNU-compatible `sha256sum`, the generated dashboard files, and checksum files. It pairs directly with `scripts/gen-tikv-details-dashboard`, which regenerates JSON and `.sha256` files.

## Risks
It validates byte-level generation drift, not Grafana semantics. Missing checksum files mean a dashboard is not checked by this loop. The use of `sha256sum` may require adjustment on systems that only provide `shasum`.

## Test Signals
Passing output confirms generated dashboard bytes match recorded checksums. A failing checksum is a strong signal that the generator must be rerun or the generated artifact must be reconciled.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-dashboards -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-docker-build -->
# sources/storage-engines/tikv/scripts/check-docker-build

## Purpose
This bash CI guard checks every tracked `Cargo.toml` file, except fuzz manifests, for explicit paths on test, bench, bin, and example targets. It prevents Docker build failures caused by implicit Cargo target path inference.

## Important Commands
The script uses `git ls-files | grep 'Cargo.toml' | grep -v 'fuzz/'` to choose manifests. For each manifest and each target kind, it uses `sed` to extract from `[[target]]` to the next blank line, then compares the count of target headers with the count of `path =` lines.

## Control Flow
The script exits on shell errors. If any target section lacks a matching path line, it prints the manifest and target kind and exits 1. Otherwise it prints `Docker build check passed.`

## State and Persistence
No state is persisted. The script reads tracked files and exits according to the check result.

## Dependencies and Integration Points
It depends on Git, grep, sed, shell arithmetic/comparison, and the TiKV manifest style. It integrates with CI before or during Docker image validation.

## Risks
The TOML parsing is textual and can be confused by blank lines, comments, or unusual target-table formatting. It only checks tracked files and intentionally ignores fuzz manifests. The grep pattern for `[[target]]` is simple and assumes conventional formatting.

## Test Signals
A passing run indicates all relevant explicit target sections declare paths. To test the guard, add a temporary `[[test]]` without `path =` in a tracked manifest and verify it fails.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-docker-build -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-license -->
# sources/storage-engines/tikv/scripts/check-license

## Purpose
This bash script enforces license headers on newly added Rust files. It checks untracked, non-ignored `.rs` files and requires the first line to match the TiKV Apache-2.0 copyright header.

## Important Commands
It uses `git ls-files -o --exclude-standard | grep "\.rs"` to find untracked Rust files, then uses a first-line `sed` expression to match `Copyright [year] TiKV Project Authors. Licensed under Apache-2.0.`

## Control Flow
The script exits immediately on a missing header, printing the file path. If all untracked Rust files have the header, it prints `License check passed.`

## State and Persistence
It does not modify files or persist state. It only inspects the current working tree's untracked Rust files.

## Dependencies and Integration Points
It depends on Git and sed. It is likely used as a pre-commit or CI helper to catch new files before they are staged or committed.

## Risks
Tracked files are not checked, so it is not a full repository license audit. The check is first-line and exact-text oriented, so alternative valid license forms will fail and misplaced headers will fail. The `grep "\.rs"` pattern may match paths containing `.rs` in non-extension positions.

## Test Signals
Create an untracked Rust file with and without the exact first-line header to verify pass/fail behavior. CI should report the missing file path on failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-license -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-log-style -->
# sources/storage-engines/tikv/scripts/check-log-style

## Purpose
This bash script enforces snake_case keys in structured Rust log fields. It prevents log key names with spaces or hyphens from entering most of the codebase.

## Important Commands
The script defines `error_msg` to print `Prefer snake_case for log kv.` It recursively greps Rust files outside `target` with an extended regular expression that detects quoted log keys containing spaces or hyphens before `=>`, then filters out allowed paths such as `config.rs`, `tikv_util/src/logger`, and `file_system/src/rate_limiter.rs`.

## Control Flow
If the grep pipeline finds any unapproved match, the script prints the error and exits 1. If no matches remain after exclusions, it prints `Log style check passed.`

## State and Persistence
The script reads source files only and does not persist state.

## Dependencies and Integration Points
It depends on bash, grep with extended regex support, and TiKV's structured logging style. It integrates with CI lint checks and keeps log fields machine-friendly.

## Risks
Regex linting can produce false positives or false negatives for complex macros, raw strings, multiline arguments, or generated code. The exclusion list is path-based and must be maintained as logging infrastructure changes.

## Test Signals
Adding a Rust log field like `"bad key" => value` should fail unless it is in an excluded path. A snake_case key should pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-log-style -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-redact-log -->
# sources/storage-engines/tikv/scripts/check-redact-log

## Purpose
This bash script guards against logging user data through raw uppercase hex encoding. It requires code to use TiKV log wrappers that respect `security.redact-info-log`.

## Important Commands
The script defines a long explanatory `error_msg` recommending `log_wrappers::Value()` or `log_wrappers::hex_encode_upper`. On Darwin it uses portable grep for `encode_upper` and excludes matches containing `log_wrappers`. On other systems it uses `grep -P '(?<!hex_)encode_upper'` to detect non-wrapper uses while excluding `hex.rs`, `tikv-ctl`, and `target`.

## Control Flow
The script selects the grep implementation based on `uname`. Any match triggers the explanatory error and exit 1. No matches prints `Security check passed.`

## State and Persistence
It is read-only and does not persist state.

## Dependencies and Integration Points
It depends on bash, grep, platform-specific regex support, and TiKV's logging wrapper conventions. It integrates with CI security/lint checks around redaction compliance.

## Risks
The Darwin branch is less precise because it lacks the negative lookbehind used with GNU grep. Regex-based detection may miss aliased calls or flag harmless helper names. The policy is coupled to wrapper names and must evolve if logging APIs change.

## Test Signals
A direct Rust call to `hex::encode_upper` outside excluded paths should fail. Calls routed through `log_wrappers` or named `hex_encode_upper` should pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/check-redact-log -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/clippy -->
# sources/storage-engines/tikv/scripts/clippy

## Purpose
This bash script runs TiKV's curated Clippy policy for the workspace. It centralizes allowed, warned, and denied lints and ensures the command runs inside the Makefile-provided environment.

## Important Settings
The script re-enters through `make run` unless `MAKEFILE_RUN` is set. It optionally enables shell tracing with `SHELL_DEBUG`. `CLIPPY_LINTS` allows known noisy lints such as `module_inception`, `large_enum_variant`, `too_many_arguments`, and `type_complexity`, warns on `dbg_macro` and `todo`, denies policy lints such as `upper_case_acronyms`, `disallowed_methods`, `rust-2018-idioms`, and async-related lints including `unused_async`, `manual_async_fn`, and `large_futures`.

## Control Flow
After environment setup, the script builds the lint array in phases with comments documenting why certain lints are allowed or denied. It then invokes `cargo clippy --workspace`, excludes fuzz crates, disables default features, enables `${TIKV_ENABLE_FEATURES}`, forwards user arguments, and appends the lint policy after `--`.

## State and Persistence
No persistent state is written by the script. Cargo and Clippy may write normal target artifacts.

## Dependencies and Integration Points
It depends on bash, make, Cargo, Clippy, and `TIKV_ENABLE_FEATURES` from the Makefile environment. It is invoked directly by developers and by `scripts/clippy-all`.

## Risks
Lint availability changes with the Rust toolchain, which is why it depends on the pinned toolchain. The default `${TIKV_ENABLE_FEATURES}` expansion is required under `set -u`; the Makefile environment must define it. Allowing many lints makes this a policy compromise rather than exhaustive cleanup.

## Test Signals
Success is a clean `cargo clippy` exit for the workspace. Intentional `dbg!`, `todo!`, denied async patterns, or disallowed methods should make the script fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/clippy -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/clippy-all -->
# sources/storage-engines/tikv/scripts/clippy-all

## Purpose
This bash wrapper runs the common Clippy script with broader target coverage and TiKV test features. It is the "all targets" lint entry point for pre-submit or CI usage.

## Important Commands
Like `scripts/clippy`, it re-enters through `make run` unless `MAKEFILE_RUN` is set and honors `SHELL_DEBUG`. Its active command is `./scripts/clippy --all-targets --features "testexport failpoints"`.

## Control Flow
The script performs environment setup, then delegates to `scripts/clippy`. Commented blocks show older or possible per-package clippy invocations for `components/cdc`, `components/backup`, `cmd`, `tests`, and fuzz packages, but they are inactive.

## State and Persistence
The wrapper itself does not persist state. Cargo/Clippy target artifacts are the only expected side effects.

## Dependencies and Integration Points
It depends on `scripts/clippy`, make, Cargo, Clippy, and feature compatibility for `testexport` and `failpoints`. It is an integration point for linting tests and examples in addition to primary library targets.

## Risks
Because this wrapper forwards `--features "testexport failpoints"` while `scripts/clippy` also supplies `--no-default-features --features "${TIKV_ENABLE_FEATURES}"`, feature composition depends on Cargo argument behavior and the Makefile environment. The commented legacy commands may drift from current policy.

## Test Signals
A passing run means all targets covered by the workspace clippy command satisfy the curated policy under test/failpoint features. Failures should reproduce through the delegated `scripts/clippy` command.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/clippy-all -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/deny -->
# sources/storage-engines/tikv/scripts/deny

## Purpose
This bash script installs and runs `cargo-deny` using a standalone Rust toolchain, decoupling dependency-policy checks from the repository's primary build toolchain.

## Important Commands
It sets `RUST_VERSION="1.92.0"`, installs that toolchain with rustup minimal profile, installs `cargo-deny@0.18.9` with `cargo +${RUST_VERSION} install --locked`, prints the cargo-deny version, fetches advisory/license/source data with `deny fetch all`, and runs `deny check --show-stats`.

## Control Flow
`set -euo pipefail` stops on most failures. The install command redirects stderr to `/dev/null` and falls back to echoing `Install cargo-deny failed`, but subsequent `cargo deny` commands still determine success or failure.

## State and Persistence
The script writes to the user's rustup toolchain directory and Cargo install/cache locations. It does not modify repository files directly unless cargo-deny or Cargo caches are configured inside the repo.

## Dependencies and Integration Points
It depends on rustup, network access for toolchain and crate installation if absent, Cargo, `cargo-deny`, and the repository's deny configuration. It integrates with dependency license, advisory, bans, and source checks.

## Risks
The pinned standalone Rust version must exist and support installing the pinned cargo-deny. Suppressing install stderr can hide useful diagnostics. Network or registry outages can fail the script before policy checks run. The comment mentions an older cargo-deny update context while the actual version is `0.18.9`.

## Test Signals
Useful signals are successful `cargo +1.92.0 deny -V`, successful `deny fetch all`, and a zero exit from `deny check --show-stats` with expected statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/deny -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/env -->
# sources/storage-engines/tikv/scripts/env

## Purpose
This small bash wrapper runs an arbitrary command inside the TiKV Makefile environment. It is a convenience entry point for commands that need the same variables and setup as `make run`.

## Important Commands
The script enables `set -euo pipefail` and executes `make -f "$(dirname "$0")/../Makefile" run` with `COMMAND="$*"`.

## Control Flow
All arguments are joined into a single command string and passed through the `COMMAND` environment variable. `exec` replaces the shell with make, so make's exit status becomes the script's exit status.

## State and Persistence
The wrapper itself writes no state. Side effects are entirely from the command run by the Makefile target.

## Dependencies and Integration Points
It depends on bash, make, the repository Makefile, and the `run` target's interpretation of `COMMAND`. It is a generic integration point for developer and CI commands that need TiKV build environment variables.

## Risks
Joining arguments through `$*` can lose original argument boundaries and quoting. The script assumes its path is inside `scripts/` under the repository root.

## Test Signals
Running `./scripts/env env` or a simple echo command should show execution under the Makefile `run` target and preserve the command exit status.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/env -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/gen-tikv-details-dashboard -->
# sources/storage-engines/tikv/scripts/gen-tikv-details-dashboard

## Purpose
This bash script regenerates Grafana dashboard JSON and checksum files from Python dashboard definitions in `metrics/grafana`. It provides a reproducible Dockerized generator environment.

## Important Commands
The script computes `root_dir` from its own location, builds a local Docker image `tikv-dashboard-gen` from `pyfound/black:23.11.0`, installs `isort==5.13.2` and `grafanalib==v0.7.0`, then runs a container with the repository `metrics` directory mounted at `/metrics`. Inside the container it sorts imports, formats dashboard Python files, runs `generate-dashboard` for each `*.dashboard.py`, and writes `sha256sum` files for generated JSON.

## Control Flow
Docker build must succeed before the generator runs. The container command is strict (`set -euo pipefail`), so formatting, generation, or checksum failure aborts the run. Each dashboard Python file produces a same-name `.json` and `.json.sha256`.

## State and Persistence
The script writes formatted dashboard Python files, generated dashboard JSON files, and `.sha256` checksum files under the mounted `metrics/grafana` directory. It also creates or updates a local Docker image.

## Dependencies and Integration Points
It depends on Docker, network access or cached layers for Python packages, `black`, `isort`, `grafanalib`, and the `generate-dashboard` CLI. It integrates directly with `scripts/check-dashboards`, which validates the generated checksums.

## Risks
Running the script mutates dashboard source formatting as well as generated artifacts. Docker availability and Python package resolution are required. The checksum command inside the container writes paths relative to `./metrics/grafana`, so path assumptions should be preserved.

## Test Signals
Signals include successful Docker build, no formatter/generator errors, updated `.json` and `.json.sha256` files, and a subsequent `./scripts/check-dashboards` pass.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/gen-tikv-details-dashboard -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/run-cargo.sh -->
# sources/storage-engines/tikv/scripts/run-cargo.sh

## Purpose
This bash script runs Cargo with experimental compile-time options driven by environment variables. It is used by Makefile `x-` targets and manages temporary Cargo config files, custom feature sets, release/debug toggles, Rust flags, package selection, and frame-pointer builds.

## Important Variables
Required `X_CARGO_CMD` selects the cargo subcommand. Optional variables include `X_CARGO_FEATURES`, `X_CARGO_RELEASE`, `X_CARGO_CONFIG_FILE`, `X_RUSTFLAGS`, `X_DEBUG`, `X_PACKAGE`, `X_CARGO_ARGS`, `TIKV_FRAME_POINTER`, `TIKV_BUILD_RUSTC_TARGET`, and `X_CARGO_TARGET_DIR`. It always adds `--no-default-features` and defaults features to `default`.

## Control Flow
The script removes any existing `.cargo/config`, builds an argument string, fails if `X_CARGO_CMD` is unset, optionally adds `--release`, copies a requested config file into `.cargo/config`, appends custom `RUSTFLAGS`, enables debug info profiles, constructs `--package` arguments from `X_PACKAGE`, and handles special `-Z build-std` arguments when frame pointers are requested. It then disables immediate exit, prints and runs the cargo command, captures the exit code, removes temporary `.cargo/config`, removes `.cargo` if empty, and exits with the original cargo status.

## State and Persistence
This script deliberately mutates `.cargo/config` during execution and attempts cleanup afterward. It can write normal Cargo target artifacts, install `rust-src` for frame-pointer builds, and export environment variables into the cargo process.

## Dependencies and Integration Points
It depends on bash, Cargo, rustup for `rust-src`, nightly Cargo for `-Z build-std`/`-Z unstable-options`, and Makefile targets that set the `X_` variables. It integrates with TiKV build experimentation and custom release/debug profiles.

## Risks
The script removes pre-existing `.cargo/config` without preserving it, so it assumes repository-local config is disposable or managed elsewhere. Many variable reads occur under `set -e` but not `set -u`, allowing unset variables to expand empty. Argument assembly via strings can be sensitive to spaces. Frame-pointer builds require target and output-dir variables to be valid.

## Test Signals
Useful checks include running with minimal `X_CARGO_CMD=check`, with a temporary config file, with custom features, and with cargo failure to confirm cleanup still happens and the original cargo exit status is returned.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/run-cargo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/test -->
# sources/storage-engines/tikv/scripts/test

## Purpose
This bash script runs TiKV workspace tests under the common Makefile environment. It centralizes feature handling, Docker-specific feature injection, library path handling, logging verbosity, and standard workspace exclusions.

## Important Variables
It re-enters through `make run` unless `MAKEFILE_RUN` is set. It reads `SHELL_DEBUG`, `DYLD_LIBRARY_PATH`, `LOCAL_DIR`, `TIKV_ENABLE_FEATURES`, `CUSTOM_TEST_COMMAND`, and `EXTRA_CARGO_ARGS`. Defaults are `CUSTOM_TEST_COMMAND="test"` and empty feature/extra-argument values.

## Control Flow
After environment setup, it adds `docker_test` to `TIKV_ENABLE_FEATURES` when running inside Docker. It exports `DYLD_LIBRARY_PATH` with `${LOCAL_DIR}/lib`, sets `LOG_LEVEL=DEBUG` and `RUST_BACKTRACE=full`, prints enabled features, and invokes `cargo $CUSTOM_TEST_COMMAND --workspace` while excluding fuzz crates and enabling the selected feature string. User arguments are forwarded at the end.

## State and Persistence
The script does not persist custom state. Cargo writes normal build/test artifacts, and tests may create their own temporary data. Environment variables affect child cargo/test processes only.

## Dependencies and Integration Points
It depends on bash, make, Cargo, the Makefile `run` target, TiKV feature naming, and workspace package layout. It is used directly by developers and by `scripts/test-all`.

## Risks
Feature strings must be compatible with Cargo and may be empty. `EXTRA_CARGO_ARGS` is preserved for compatibility but the comment says direct arguments are preferred. macOS dynamic library path handling depends on `LOCAL_DIR`. Docker detection relies on `/.dockerenv`.

## Test Signals
A passing run is a zero exit from Cargo tests. Useful smoke checks are `./scripts/test --no-run`, Docker runs that include `docker_test`, and runs with `CUSTOM_TEST_COMMAND=check` or extra cargo arguments.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/test -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/scripts/test-all -->
# sources/storage-engines/tikv/scripts/test-all

## Purpose
This bash wrapper runs the common test command plus extra Linux-only validation paths. It is intended as a broad pre-submit test entry point.

## Important Commands
The script re-enters through `make run` unless `MAKEFILE_RUN` is set. It first runs `./scripts/test "$@"`. On Linux it reruns tests with `MALLOC_CONF=prof:true` and the `ifdef_malloc_conf` test filter. On Linux it also runs a no-run cargo test build with JSON diagnostics and pipes the output to `python3 scripts/check-bins.py --features "${TIKV_ENABLE_FEATURES}" --check-tests`.

## Control Flow
Each phase is chained with `&& echo`, and `set -euo pipefail` makes any failing phase abort the script. The binary-inspection phase is Linux-only and depends on JSON build output from `scripts/test`.

## State and Persistence
The script itself persists no state. Cargo build artifacts and test outputs are normal side effects. The `MALLOC_CONF` export applies to the second test run in the current shell.

## Dependencies and Integration Points
It depends on `scripts/test`, `scripts/check-bins.py`, Python 3, Linux binary inspection tools through `check-bins.py`, Cargo JSON message format, and the Makefile environment's `TIKV_ENABLE_FEATURES`.

## Risks
The `${TIKV_ENABLE_FEATURES}` expansion under `set -u` requires the Makefile environment to define the variable before the Linux binary-inspection phase. The Linux-only no-run build can be expensive. Binary checks are skipped on non-Linux platforms, so local macOS runs do not cover allocator/linkage policy.

## Test Signals
Passing output means normal tests, malloc-config-specific tests, and Linux binary checks completed. Failures from the last phase usually indicate missing jemalloc, OpenSSL linkage mismatch, or another binary policy violation detected by `check-bins.py`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/scripts/test-all -->
