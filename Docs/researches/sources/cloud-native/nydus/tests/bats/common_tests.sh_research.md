# sources/cloud-native/nydus/tests/bats/common_tests.sh

Purpose: common shell helpers for the BATS integration suites, primarily deriving toolchain versions, generating a Rust+Go Dockerfile, starting nydus snapshotter, and configuring containerd for Nydus.

Important APIs/types/functions: `parse_toml` extracts a quoted key from TOML text with sed. `get_rust_toolcahin` reads `rust-toolchain.toml` or legacy `rust-toolchain` (function name contains a typo). `get_go_work_version` reads the `go` directive from `go.work`. Global variables set `repo_base_dir`, `rust_toolchain`, `go_work_version`, `compile_image`, and `nydus_snapshotter_repo`. `generate_rust_golang_dockerfile` writes a Dockerfile installing Rust, build packages, rustfmt/clippy, and Go. `run_nydus_snapshotter` writes a temporary nydus-erofs config, clears containerd/nydus cache directories, and launches `containerd-nydus-grpc`. `config_containerd_for_nydus` writes `/etc/containerd/config.toml`, restarts containerd, and sleeps.

Control flow: BATS files source this script, then call helpers to build an environment and configure runtime services. Dockerfile generation is a heredoc. Snapshotter startup runs in background with stdout/stderr redirected to a per-test log. Containerd configuration overwrites or creates the daemon config and restarts the service.

State and persistence: writes Dockerfiles, `/tmp/nydus-erofs-config.json`, `/etc/containerd/config.toml`, snapshotter logs, and deletes `/var/lib/containerd/io.containerd.snapshotter.v1.nydus` plus `/var/lib/nydus/cache`. It changes system containerd state.

Dependencies and integration points: depends on sed, grep, awk, wget, Docker build context, Go downloads, rustup, containerd, systemctl, `containerd-nydus-grpc`, and `/usr/local/bin/nydusd`. Ties Rust and Go workspace versions into the test image.

Risks: TOML parsing is ad hoc and only handles simple quoted `key = "value"` lines. Heredoc paths are unquoted, so spaces in paths would break. It overwrites containerd config and restarts the service, making it unsuitable outside isolated CI. Network download of Go and apt packages affects reproducibility. `git`/network assumptions appear in other BATS helpers.

Test signals: not a test by itself, but it is central to BATS integration repeatability. It exposes environmental assumptions that can explain CI-only failures.
