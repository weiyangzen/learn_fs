# sources/cloud-native/nydus/build.rs

Purpose: Cargo build script that records compiler, profile, build time, and git revision data into compile-time environment variables.

Important APIs/types/functions: `get_version_from_cmd` runs `<executable> -V` and trims the trailing newline. `get_git_commit_hash` runs `git rev-parse --verify HEAD`. `get_git_commit_version` runs `git describe --tags`. `main` emits `cargo:rustc-env` lines for `RUSTC_VERSION`, `PROFILE`, `BUILT_TIME_UTC`, `GIT_COMMIT_HASH`, and `GIT_COMMIT_VERSION`.

Control flow: `main` reads `RUSTC` and `PROFILE`, formats the current UTC time in ISO-8601 via `time`, tries git commands, then prints Cargo directives. Git failures degrade to `"unknown"` while `RUSTC` command failures panic when `RUSTC` is set but not executable.

State and persistence: no files are written directly. Persistence is through Cargo build metadata and environment variables embedded into compiled crates. `cargo:rerun-if-changed=../git/HEAD` attempts to make rebuilds sensitive to repository head changes.

Dependencies and integration points: uses standard `Command`, `OsString`, and the `time` crate. It feeds version structs such as `BuildTimeInfo` in the API crate or binaries that read these env vars.

Risks: the rerun path is unusual for a normal `.git/HEAD` path and may not always trigger on git changes. `String::from_utf8(output.stdout).unwrap()` assumes valid UTF-8 from compiler output. Git command success status is not checked; empty stdout would become an empty string rather than `"unknown"`.

Test signals: no direct tests. Behavior is normally validated by build outputs and runtime version reporting.
