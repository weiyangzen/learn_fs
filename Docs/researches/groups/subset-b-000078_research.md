# subset-b-000078 Research

This grouped report covers the subset-b-000078 source files. Each section is keyed by the original source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.2.0.toml -->
# sources/cloud-native/containerd/releases/v2.2.0.toml

- Purpose: Release metadata for containerd `v2.2.0`, consumed by release tooling to tag `HEAD`, find containerd-owned dependency changes, and generate GitHub release notes.
- Important fields: `project_name`, `github_repo`, `match_deps`, `ignore_deps`, `previous = "v2.1.0"`, `pre_release = false`, plus Markdown `preface` and `postface`.
- Control flow and state: The file is declarative TOML. State is the chosen previous release and prose embedded into generated release artifacts.
- Dependencies and integration: Integrates with the containerd release note generator and GitHub release publishing workflow. Dependency matching is limited to `github.com/containerd/...` modules while excluding the root containerd module.
- Risks: Incorrect `previous` skews changelog ranges; stale download guidance can mislead users about dynamic versus static tarballs; `commit = "HEAD"` relies on the release runner being checked out at the intended commit.
- Test signals: Validation is mainly release dry-runs and generated note review, not runtime tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.2.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.3.0.toml -->
# sources/cloud-native/containerd/releases/v2.3.0.toml

- Purpose: Release metadata for containerd `v2.3.0`, including the release narrative for the first annual LTS release under the Kubernetes-aligned cadence.
- Important fields: `previous = "v2.2.0"`, `pre_release = false`, `match_deps`, `ignore_deps`, and the release-note `preface` describing roughly four-month minor cadence and at least two years of LTS support.
- Control flow and state: Declarative input for release automation. The stateful boundary is the previous tag used to compute changes.
- Dependencies and integration: Coupled to GitHub release automation and docs links in the generated notes. Download guidance points users to containerd tarballs plus external runc and CNI plugin releases.
- Risks: The LTS/support statement is user-facing release policy; mistakes here have compatibility and support implications. `HEAD` must be the intended tag target.
- Test signals: Release-note generation, dependency diff output, and human review are the meaningful checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/releases/v2.3.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/critest.sh -->
# sources/cloud-native/containerd/script/critest.sh

- Purpose: Starts an isolated containerd daemon and runs Kubernetes CRI conformance tests through `critest`, writing logs and reports to a caller-supplied report directory.
- Important functions and variables: `traverse_path` relaxes execute permissions up the temporary build directory path for user-namespace runc startup; `cleanup` kills containerd, prints logs, and removes the temp directory. Inputs include `TEST_RUNTIME`, `CGROUP_DRIVER`, `SKIP_TEST`, `FOCUS_TEST`, and `EXTRA_CRITEST_OPTIONS`.
- Control flow: Create `BDIR`, write `config.toml` with CRI runtime and overlayfs `slow_chown`, optionally enable `SystemdCgroup`, assemble Ginkgo skip/focus flags, start `/usr/local/bin/containerd`, poll `crictl info`, then run `critest --parallel=8`.
- State and persistence: Mutates a temporary root/state tree under `BDIR`, writes `containerd.log`, and deletes temporary state on exit. It also uses `pkill containerd`, which can affect unrelated daemons in the same environment.
- Dependencies and integration: Requires containerd, `crictl`, `critest`, CNI config under `/etc/cni/net.d`, and a runtime shim matching `TEST_RUNTIME`.
- Risks: Unquoted `mkdir -p $report_dir`, broad `pkill containerd`, and root permission changes make it best suited for disposable CI hosts. The systemd cgroup OOMKilled test is skipped due to scope GC races.
- Test signals: The `critest` report directory and printed containerd logs are the primary failure diagnostics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/critest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/go-test-fuzz.sh -->
# sources/cloud-native/containerd/script/go-test-fuzz.sh

- Purpose: Thin wrapper for running Go fuzz tests with repository defaults.
- Important behavior: Uses strict shell options and `set -x`, sets `fuzztime=30s`, discovers fuzz functions with `git grep 'func Fuzz.*testing\.F'`, and runs each fuzz target separately because `go test -fuzz` accepts one fuzz function at a time.
- Control flow: Build a newline-delimited list of matching source locations excluding vendor, derive package path and `Fuzz...` function name with grep, then run `go test -fuzz=$fuzz_name ./$pkg_path -fuzztime=$fuzztime`.
- State and persistence: Persists Go fuzz cache/corpus data through the Go toolchain, typically under package `testdata/fuzz` or Go build cache depending on invocation.
- Dependencies and integration: Requires a Go version with native fuzzing support and package-level `Fuzz...` functions.
- Risks: Fuzzing is resource-intensive and can be nondeterministic by design; unbounded or long durations can stress CI.
- Test signals: Go test exit status, minimized failing corpus entries, and standard `go test` output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/go-test-fuzz.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/resize-vagrant-root.sh -->
# sources/cloud-native/containerd/script/resize-vagrant-root.sh

- Purpose: Expands the root partition and filesystem for Vagrant-based Linux development/test machines.
- Important logic: Installs `cloud-utils-growpart` with `dnf` if `growpart` is absent, parses `df -T /`, calls `growpart`, then resizes either btrfs or xfs root filesystems.
- Control flow: Parse `/dev/<disk><partition>` roots, tolerate `NOCHANGE`, branch on filesystem type, and fail for unknown filesystems or device-mapper roots.
- State and persistence: Mutates the host partition table and root filesystem size.
- Dependencies and integration: Requires root privileges, `growpart`, `btrfs filesystem resize` or `xfs_growfs`, and Rocky/Fedora-like package management for the fallback install.
- Risks: Regex parsing only supports simple block devices; device-mapper/LVM is explicitly unsupported; running on an unexpected host can alter storage irreversibly.
- Test signals: Successful `growpart`/filesystem tool exits and post-run `df` size changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/resize-vagrant-root.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-containerd -->
# sources/cloud-native/containerd/script/setup/config-containerd

- Purpose: Writes `/etc/containerd/config.toml` for integration/e2e environments.
- Important behavior: Detects SELinux availability with `getenforce`; writes config version 2, overlayfs `slow_chown = true`, and CRI `enable_selinux` matching host mode.
- Control flow: Set `enable_selinux=false`, enable it when SELinux exists and is not disabled, create `/etc/containerd`, then tee the generated TOML with sudo.
- State and persistence: Persists host-level containerd configuration under `/etc/containerd/config.toml`.
- Dependencies and integration: Used by setup pipelines before starting containerd; interacts with CRI plugin and overlayfs snapshotter.
- Risks: Overwrites existing config wholesale; assumes sudo is available for the `tee` path; config schema is containerd v2 style, not the newer `ConfigVersion = 4` Go constant.
- Test signals: Starting containerd and `crictl info` validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-containerd -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-selinux -->
# sources/cloud-native/containerd/script/setup/config-selinux

- Purpose: Sets the host SELinux mode for containerd test hosts according to the `SELINUX` environment variable.
- Important behavior: No-ops if `getenforce` and `setenforce` are unavailable; supports `Disabled`, `Enforcing`, and `Permissive`.
- Control flow: For disabled mode, set permissive and unmount `/sys/fs/selinux` if mounted. For enforcing/permissive, mount selinuxfs if needed and call `setenforce`.
- State and persistence: Mutates kernel SELinux runtime state and the selinuxfs mount, but does not edit persistent distribution config files.
- Dependencies and integration: Requires SELinux utilities, mount privileges, and callers that set `SELINUX`.
- Risks: Missing `SELINUX` under `set -u` fails; unmounting selinuxfs can surprise other processes; unsupported values exit hard.
- Test signals: Final `getenforce` output and subsequent containerd CRI SELinux tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-selinux -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni -->
# sources/cloud-native/containerd/script/setup/install-cni

- Purpose: Builds and installs Linux CNI plugins plus a basic containerd CNI conflist.
- Important variables: `CNI_COMMIT` defaults to the module version from `go.mod`; `CNI_REPO`, `DESTDIR`, `CNI_DIR`, and `CNI_CONFIG_DIR` control source and installation paths.
- Control flow: Clone CNI plugins, checkout the selected commit, run `build_linux.sh`, copy `bin` under `/opt/cni`, and write `10-containerd-net.conflist`.
- State and persistence: Installs binaries and writes `/etc/cni/net.d/10-containerd-net.conflist` with bridge, host-local IPv4/IPv6 ranges, default routes, and portmap.
- Dependencies and integration: Requires git, Go build tools, shell, and sudo when not root. Integrates with CRI tests and `crictl` pod networking.
- Risks: Copies the entire `bin` directory into `$CNI_DIR`, which can create nested layout surprises; network CIDRs are fixed; external clone without checksum relies on git commit selection.
- Test signals: `ls /etc/cni/net.d`, pod sandbox creation, and CRI networking tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni-windows -->
# sources/cloud-native/containerd/script/setup/install-cni-windows

- Purpose: Builds Microsoft Windows CNI binaries and generates a NAT CNI config for Windows containerd testing.
- Important functions: `split_ip` decomposes IPv4 addresses; `calculate_subnet` builds a subnet from gateway and prefix length.
- Control flow: Clone `windows-container-networking`, checkout a pinned commit, run `make all`, install `nat.exe`, `sdnbridge.exe`, and `sdnoverlay.exe`, query PowerShell for the NAT adapter gateway/prefix, then write `0-containerd-nat.conf`.
- State and persistence: Writes binaries under `DESTDIR/cni/bin` and CNI config under `DESTDIR/cni/conf`.
- Dependencies and integration: Requires Go/GOPATH style source layout, Windows PowerShell, Microsoft HCN-compatible networking, and make.
- Risks: Uses `eval` in `split_ip`, assumes `vEthernet (nat)` exists, and has a likely prefix-length inversion in the emitted CIDR suffix (`32 - prefix_len`).
- Test signals: Windows CRI integration pod networking and presence of installed `.exe` plugins.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni-windows -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-critools -->
# sources/cloud-native/containerd/script/setup/install-critools

- Purpose: Builds and installs CRI tools, including `critest` and `crictl`, for containerd CRI validation.
- Important variables: `CRITEST_COMMIT` from `critools-version`, `CRI_TOOLS_REPO`, `DESTDIR`, and sudo wrapper preserving `PATH`.
- Control flow: Install Ginkgo v2.9.2, clone cri-tools, checkout the pinned version, run `make`, run `make install` into `/usr/local/bin`, and write `crictl.yaml`.
- State and persistence: Installs host binaries and writes `/etc/crictl.yaml` pointing at `unix:///run/containerd/containerd.sock`.
- Dependencies and integration: Requires Go, git, make, and the cri-tools repository. Consumed by `critest.sh` and CRI integration scripts.
- Risks: Host global install may conflict with existing versions; default endpoint only matches standard Linux socket paths.
- Test signals: `crictl info`, `critest --version`, and CRI test execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-critools -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-dev-tools -->
# sources/cloud-native/containerd/script/setup/install-dev-tools

- Purpose: Installs pinned developer tooling used by containerd generation, docs, lint, and protocol workflows.
- Important commands: `go install` for `go-fix-acronym`, `go-md2man`, `golangci-lint/v2`, `protoc-gen-go-ttrpc`, and `buf`.
- Control flow and state: Sequential Go installs place binaries into `$GOBIN` or `$GOPATH/bin`.
- Dependencies and integration: Requires module-aware Go and network access to module proxies/source. Integrates with make targets for lint, docs, protobuf, and validation.
- Risks: Global tool installation can shadow user versions; no checksum pinning beyond module versions; failures leave partial tool sets.
- Test signals: Make validation/lint/doc targets finding the expected binaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-dev-tools -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-failpoint-binaries -->
# sources/cloud-native/containerd/script/setup/install-failpoint-binaries

- Purpose: Builds and installs failpoint-enabled binaries used by fault-injection tests.
- Important behavior: Runs make targets for `cni-bridge-fp`, `containerd-shim-runc-fp-v1`, `runc-fp`, and `loopback-v2`, then installs them into CNI or `/usr/local/bin` locations.
- Control flow: Resolve repository root from script path, build each failpoint binary, and `sudo install` it to configurable destination directories.
- State and persistence: Mutates host binary directories such as `/opt/cni/bin` and `/usr/local/bin`.
- Dependencies and integration: Requires make, Go, sudo, and corresponding make targets in the containerd tree. Used by integration tests that activate failpoints.
- Risks: Overwrites binaries in global paths; assumes failpoint make targets are supported on the host OS/arch.
- Test signals: Fault-injection integration tests and executable presence checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-failpoint-binaries -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-gotestsum -->
# sources/cloud-native/containerd/script/setup/install-gotestsum

- Purpose: Installs `gotestsum` for formatted Go test output in CI.
- Important behavior: `GO111MODULE=on go install gotest.tools/gotestsum@v1.8.2`.
- Control flow and state: Single module install into Go binary path.
- Dependencies and integration: Requires Go and network/module cache. Used by make or CI test targets that prefer gotestsum output.
- Risks: Global install and pinned old version can conflict with local expectations.
- Test signals: `gotestsum --version` and CI jobs that invoke it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-gotestsum -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-imgcrypt -->
# sources/cloud-native/containerd/script/setup/install-imgcrypt

- Purpose: Builds and installs imgcrypt/containerd encryption support artifacts for test environments.
- Important variables: `IMGCRYPT_REPO`, `IMGCRYPT_VERSION`, `DESTDIR`, and temporary clone root.
- Control flow: Clone imgcrypt, checkout pinned version, run `make containerd-release -e DESTDIR=...`, and clean the temporary clone.
- State and persistence: Installs generated release artifacts under `DESTDIR/usr/local`.
- Dependencies and integration: Requires git, make, Go tooling, and imgcrypt release targets. Integrates with encrypted image tests.
- Risks: External repository build can be slow/flaky; host install location is global; cleanup only runs after successful command flow unless trap exists.
- Test signals: Tests that exercise encrypted image pull/unpack and presence of installed imgcrypt tooling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-imgcrypt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runc -->
# sources/cloud-native/containerd/script/setup/install-runc

- Purpose: Installs the OCI runtime used by containerd tests, selecting either upstream runc or crun pretending to be runc.
- Important functions: `install_runc` clones `opencontainers/runc`, checks out `runc-version`, builds with seccomp, and installs; `install_crun` downloads a crun release binary to `/usr/local/sbin/runc`.
- Control flow: Determine sudo, switch on `RUNC_FLAVOR`, and run the selected installer.
- State and persistence: Installs a runtime binary into system paths.
- Dependencies and integration: Requires git/make/Go for runc or curl for crun; used by CRI and integration tests.
- Risks: Downloaded crun binary is not checksum-verified; global `/usr/local/sbin/runc` replacement can affect other workloads; runc build assumes seccomp headers.
- Test signals: Runtime version checks and container creation tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runc -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runhcs-shim -->
# sources/cloud-native/containerd/script/setup/install-runhcs-shim

- Purpose: Builds the Windows `containerd-shim-runhcs-v1.exe` from Microsoft hcsshim for Windows containerd tests.
- Important variables: `RUNHCS_VERSION`, `RUNHCS_REPO`, `HCSSHIM_SRC`, `DESTDIR`, and `GOOS=windows`.
- Control flow: If no local hcsshim source is supplied, shallow-fetch the selected version; otherwise checkout the version in the supplied source; build with `-mod=vendor`.
- State and persistence: Writes `containerd-shim-runhcs-v1.exe` under `DESTDIR`.
- Dependencies and integration: Requires Go cross-compilation, git, hcsshim vendored dependencies, and Windows runtime tests.
- Risks: Local `HCSSHIM_SRC` checkout is mutated; shallow fetch by arbitrary version depends on tag/branch existence.
- Test signals: Windows CRI integration and shim executable invocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runhcs-shim -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-seccomp -->
# sources/cloud-native/containerd/script/setup/install-seccomp

- Purpose: Builds and installs libseccomp `2.5.5` into `/usr/local`.
- Important behavior: Downloads release tarball, configures, makes, installs with sudo, runs `ldconfig`, and removes the temp directory.
- Control flow and state: Temporary source extraction followed by system library install.
- Dependencies and integration: Requires curl, tar, compiler toolchain, make, sudo, and dynamic linker cache updates. Supports runc/containerd seccomp build tags and tests.
- Risks: No checksum verification; global library install can override distro packages; build prerequisites are implicit.
- Test signals: Successful seccomp-enabled runtime build and seccomp integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-seccomp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-teststat -->
# sources/cloud-native/containerd/script/setup/install-teststat

- Purpose: Installs `teststat` for summarizing Go test results.
- Important behavior: `GO111MODULE=on go install github.com/vearutop/teststat@v0.1.3`.
- Control flow and state: Single Go module binary install.
- Dependencies and integration: Requires Go and network/module cache; integrates with test reporting pipelines.
- Risks: Very old pinned version and global install path.
- Test signals: CI test-stat reporting jobs finding the binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-teststat -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/test/cri-integration.sh -->
# sources/cloud-native/containerd/script/test/cri-integration.sh

- Purpose: Runs the built `cri-integration.test` binary against a freshly started test containerd daemon.
- Important variables: `FOCUS`, `REPORT_DIR`, `RUNTIME`, `RUNC_FLAVOR`, `TEST_IMAGE_LIST`, and paths initialized by sourced `utils.sh`.
- Control flow: Source test utilities, register teardown trap, choose report directory by OS, call `test_setup`, build a command with sudo/env, run the Go test binary with CRI endpoint/runtime/containerd/build-dir/image-list flags, and print logs on failure.
- State and persistence: Creates report directory, starts containerd with test root/state paths, and may move `containerd.log` into `$GITHUB_WORKSPACE/report`.
- Dependencies and integration: Requires built `bin/cri-integration.test`, `bin/containerd`, `crictl`, CNI/runc setup, and `utils.sh`.
- Risks: Command assembly via string variables can mishandle unusual paths; failure handling moves logs only in GitHub workspace mode.
- Test signals: Go test exit code and emitted containerd logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/test/cri-integration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/test/test2annotation.sh -->
# sources/cloud-native/containerd/script/test/test2annotation.sh

- Purpose: Converts Go test JSON-style output to GitHub Actions annotations using a jq program.
- Important behavior: Locates `test2annotation.jq` beside the script and pipes input through jq.
- Control flow and state: Stateless filter; input is stdin and output is annotated text.
- Dependencies and integration: Requires `jq` and the adjacent jq script. Used in CI to surface test failures inline.
- Risks: Fails if jq or the jq program is missing; only handles formats supported by that jq filter.
- Test signals: Annotation output in GitHub Actions logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/test/test2annotation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/test/utils.sh -->
# sources/cloud-native/containerd/script/test/utils.sh

- Purpose: Shared test harness for starting, supervising, and stopping containerd across Linux and Windows CRI integration runs.
- Important functions: `run_containerd`, `test_setup`, `test_teardown`, `run_ctr`, `run_crictl`, `keepalive`, and `readiness_check`.
- Control flow: Detect Windows via `$OS`, create a temporary/default config if needed, add Windows Hyper-V runtime config or Linux systemd cgroup options, compute root/state/socket paths, choose sudo wrapper, start containerd via keepalive on Linux or a Windows service, verify readiness with `ctr version` and `crictl info`, then teardown by process group or service deletion.
- State and persistence: Writes containerd config, root/state directories, logs, Windows service registration, and optional ACL changes under ProgramData on Windows.
- Dependencies and integration: Requires built `bin/containerd` and `bin/ctr`, `crictl`, sudo or Windows service tools, CNI config, and caller-provided report dir.
- Risks: Uses global test paths by default, can kill a process group, and readiness diagnostics reference variables that are local in some call paths. Windows paths and service registration are sensitive to quoting and permissions.
- Test signals: Readiness checks, `containerd.log`, config dump, and CRI integration results.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/test/utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/verify-go-modules.sh -->
# sources/cloud-native/containerd/script/verify-go-modules.sh

- Purpose: Verifies Go module files and generated vendor/module state remain clean.
- Important behavior: Accepts exactly one argument naming a second module directory, requires `jq`, and compares `require` plus `replace` directives from root `go.mod` against the second `go.mod`.
- Control flow: Load root requires/replaces into bash associative arrays using `go mod edit -json | jq`, load the second module's arrays, compare shared require versions, compare shared replace values, and ensure root replace directives also exist in the second module except for `github.com/containerd/containerd*`.
- State and persistence: Read-only against repository files; it may populate Go module cache while evaluating module metadata.
- Dependencies and integration: Requires Bash associative arrays, Go, and jq. Used when submodules must stay aligned with root module dependency overrides.
- Risks: String splitting around `#` and `:` assumes module paths/versions do not contain those separators; only overlapping requires are checked, while missing root requires are not considered errors.
- Test signals: Zero exit when no mismatch messages are emitted; nonzero exit with a count of module sync errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/verify-go-modules.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/build-test-images.sh -->
# sources/cloud-native/containerd/test/build-test-images.sh

- Purpose: Builds and pushes integration test images needed by containerd test jobs.
- Important behavior: Sources build utilities and buildx initialization, then runs image make targets for `volume-copy-up` and `volume-ownership` with `PROJ=gcr.io/${PROJECT}`.
- Control flow and state: Prepare Docker buildx for multiarch, resolve repo root, and push selected images; errors are tolerated for the individual image pushes.
- Dependencies and integration: Requires Docker/buildx, Google credentials/project from `build-utils.sh`, and image makefiles under `integration/images`.
- Risks: `|| true` can mask failed image publication; pushes to shared registry names.
- Test signals: Registry image availability and downstream integration tests pulling the images.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/build-test-images.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/build-utils.sh -->
# sources/cloud-native/containerd/test/build-utils.sh

- Purpose: Shared CI build setup for containerd release/test scripts.
- Important behavior: Authenticates to Google Cloud when `GOOGLE_APPLICATION_CREDENTIALS` exists, installs seccomp packages, and adjusts git refs for pull request builds.
- Control flow and state: Run package install commands and optional cloud/git setup before build/push scripts.
- Dependencies and integration: Requires apt-based environment, gcloud/gsutil credentials, and git. Sourced by build and image scripts.
- Risks: Assumes Debian/Ubuntu package manager; mutates package state; credential-dependent behavior can differ between CI and local runs.
- Test signals: Later build and push scripts succeeding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/build-utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/build.sh -->
# sources/cloud-native/containerd/test/build.sh

- Purpose: Builds a CRI+CNI containerd release tarball for Kubernetes test infrastructure and uploads it to GCS.
- Important behavior: Runs `make clean`, `make BUILDTAGS="seccomp no_btrfs no_devmapper no_zfs" cri-cni-release`, rewrites tarball naming, computes version with `git describe`, then delegates upload to `test/push.sh`.
- Control flow and state: Use a temp build directory, copy release tarball/checksum, set deployment directory, and clean temp files on exit.
- Dependencies and integration: Requires make, git, release make targets, GCS tooling from `push.sh`, and build utilities.
- Risks: Assumes `releases/cri-cni-containerd.tar.gz` symlink exists; uploads are externally visible and versioned.
- Test signals: Release tarball/checksum existence and GCS upload success.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/gci-init.sh -->
# sources/cloud-native/containerd/test/e2e_node/gci-init.sh

- Purpose: Initializes Google Container-Optimized OS/GCI nodes for containerd e2e-node testing.
- Important functions: `configure_cgroup_mode` adjusts kubelet/containerd cgroup settings based on metadata-provided environment.
- Control flow: Load `/home/containerd/containerd-env` if present, configure cgroup mode, prepare kubelet and containerized mounter directories, and bind/mount required paths.
- State and persistence: Mutates host filesystem directories and kubelet/containerd runtime configuration on boot.
- Dependencies and integration: Used with the cloud-init `init.yaml` service chain and Kubernetes e2e node infrastructure.
- Risks: Depends on metadata/env file shape; host-level mount and kubelet changes must match image expectations.
- Test signals: Node joins with containerd and kubelet e2e tests pass.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/gci-init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/init.yaml -->
# sources/cloud-native/containerd/test/e2e_node/init.yaml

- Purpose: Cloud-init config that installs and starts containerd on e2e nodes through systemd units.
- Important resources: `containerd-installation.service`, `containerd.service`, and `containerd.target`.
- Control flow: Fetch `containerd-configure-sh` from GCE metadata, chmod it, execute it, then start containerd with overlay module pre-load. `runcmd` stops existing containerd, reloads units, enables services, starts the target, and starts Docker if needed.
- State and persistence: Writes systemd unit files and enables services on the node.
- Dependencies and integration: Requires GCE metadata service, curl, systemd, overlay kernel module, and binaries installed under `/home/containerd/usr/local/bin`.
- Risks: Metadata script controls installation; bind-remounting `/home/containerd` as exec is security-sensitive; service ordering with Docker must be correct.
- Test signals: Active `containerd.target`, running containerd service, and Kubernetes e2e node success.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/init.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/init-buildx.sh -->
# sources/cloud-native/containerd/test/init-buildx.sh

- Purpose: Ensures Docker Buildx is configured for multi-architecture image builds.
- Important behavior: Checks current builder output for non-docker driver and required platforms; on Linux installs QEMU binfmt with a pinned `multiarch/qemu-user-static` digest.
- Control flow: Exit early when a suitable builder exists, otherwise reset binfmt, remove existing `containerd-buildkit-multiarch`, create it, and bootstrap.
- State and persistence: Mutates Docker buildx builder selection and binfmt_misc registrations.
- Dependencies and integration: Requires Docker, Buildx, privileged Docker run on Linux, and network access to the pinned image.
- Risks: Removing/recreating a named builder can affect concurrent builds; pinned image digest is old and must be reviewed when platforms change.
- Test signals: `docker buildx inspect --bootstrap` reporting required platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/init-buildx.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/push.sh -->
# sources/cloud-native/containerd/test/push.sh

- Purpose: Uploads containerd test release tarballs and checksums to a Google Cloud Storage bucket.
- Important variables: `DEPLOY_BUCKET`, `DEPLOY_DIR`, `BUILD_DIR`, `TARBALL`, `LATEST`, `PUSH_VERSION`, and `VERSION`.
- Control flow: Verify tarball and checksum exist, create bucket with TTL if missing, derive deploy path, upload files, optionally copy versioned artifacts and latest markers.
- State and persistence: Writes objects into `gs://$DEPLOY_BUCKET/$DEPLOY_DIR` and possibly updates latest/version aliases.
- Dependencies and integration: Requires `gsutil`, sourced `test/utils.sh` for bucket helper/checksum, and GCS credentials.
- Risks: Uploading latest aliases is mutable global state; missing deploy dir defaults can overwrite shared paths.
- Test signals: `gsutil cp` success and public GCS URLs resolving.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/push.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/utils.sh -->
# sources/cloud-native/containerd/test/utils.sh

- Purpose: General test utility helpers for GCS log upload and checksums.
- Important functions: `upload_logs_to_gcs`, `create_ttl_bucket`, and `sha256`.
- Control flow: Create bucket if missing, set a 30-day lifecycle rule and public ACL/default ACL, copy logs, and print a gcsweb URL. `sha256` chooses `sha256sum` or `shasum -a256`.
- State and persistence: Creates/updates GCS buckets and lifecycle rules; writes temporary lifecycle JSON locally.
- Dependencies and integration: Requires `gsutil`, GCS credentials, and checksum tools. Used by build/push/report scripts.
- Risks: Public-read ACLs and new buckets are security-sensitive; lifecycle rule is hardcoded to 30 days.
- Test signals: GCS listing/copy success and correct checksum output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/version/version.go -->
# sources/cloud-native/containerd/version/version.go

- Purpose: Defines build-time version identity for containerd.
- Important variables/constants: `Name`, `Package`, `Version = "2.3.0+unknown"`, `Revision`, `GoVersion = runtime.Version()`, and `ConfigVersion = 4`.
- Control flow and state: Values are package globals overridden by linker flags in release builds; `GoVersion` is computed at initialization.
- Dependencies and integration: Imported by CLI/server version reporting and configuration handling. `ConfigVersion` is the maximum supported config version for main and plugin config migration.
- Risks: Default version is only a fallback; missing linker flags produce `+unknown`. Config version changes need matching migration support.
- Test signals: Version command output and config migration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/.cirrus.yml -->
# sources/cloud-native/containers-storage/.cirrus.yml

- Purpose: Cirrus CI configuration for containers/storage validation across lint, Linux driver matrices, metadata updates, vendoring, cross-builds, gofix, codespell, and aggregate success.
- Important jobs: Fedora and Debian matrix jobs run setup plus build/test; lint runs validation and golangci; vendor checks generated vendor state; cross builds with Go 1.23; success depends on all required tasks.
- Control flow and state: Global env defines VM image names, GCE project, timestamp command, log commands, and cache locations. Test tasks use GCE instances and post-run diagnostics.
- Dependencies and integration: Integrates with Cirrus, GCE images, encrypted credentials, containers automation images, and `contrib/cirrus` scripts.
- Risks: Encrypted credentials and exact success task name are operationally sensitive; VM image pinning can stale; driver matrix can fail due to kernel/filesystem support.
- Test signals: Cirrus task statuses, archived logs, and success aggregate.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/.cirrus.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-issues.yml -->
# sources/cloud-native/containers-storage/.github/workflows/auto-close-issues.yml

- Purpose: GitHub Actions workflow that closes newly opened issues because the repository has migrated to `containers/container-libs`.
- Important behavior: Triggers on `issues` opened events, grants `issues: write`, sets `GH_TOKEN`, `REPO`, and `ISSUE`, and runs `gh issue close --repo "$REPO" --comment "...migrated..." "$ISSUE"`.
- Control flow and state: Event-triggered job on `ubuntu-latest` mutates GitHub issue state and posts the migration comment.
- Dependencies and integration: Uses GitHub CLI and `secrets.GITHUB_TOKEN`; integrates with repository migration policy.
- Risks: All newly opened issues are closed unconditionally, so any exception must be handled by changing the workflow.
- Test signals: Workflow logs and the issue timeline showing the migration close comment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-issues.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-prs.yml -->
# sources/cloud-native/containers-storage/.github/workflows/auto-close-prs.yml

- Purpose: GitHub Actions workflow that closes newly opened pull requests against `main` because development moved to `containers/container-libs`.
- Important behavior: Triggers on `pull_request_target` opened events for `main` and uses `superbrothers/close-pull-request` pinned to commit `9c18513d...` with a migration comment.
- Control flow and state: Event-triggered job on `ubuntu-latest` mutates PR state and comments through the third-party action.
- Dependencies and integration: Relies on `pull_request_target` permissions and the pinned close-pull-request action.
- Risks: `pull_request_target` is privileged; although this workflow does not check out PR code, any future expansion must avoid executing untrusted content. All matching PRs are closed unconditionally.
- Test signals: Workflow run logs and PR timeline migration comment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-prs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/.golangci.yml -->
# sources/cloud-native/containers-storage/.golangci.yml

- Purpose: golangci-lint configuration for containers/storage.
- Important behavior: Uses config version 2, enables `gofumpt` formatting, enables `nolintlint` and `unconvert`, applies exclusion presets for comments and standard error handling, and configures staticcheck to run all checks except `ST1003` and `QF1008`.
- Control flow and state: Declarative input consumed by `golangci-lint` during `make lint` and Cirrus lint.
- Dependencies and integration: Coupled to the golangci-lint version installed by tooling and to repository code style.
- Risks: Linter-version drift can make rules change; broad excludes can hide real defects.
- Test signals: `make lint` and Cirrus lint task.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/Makefile -->
# sources/cloud-native/containers-storage/Makefile

- Purpose: Central build/test/lint/docs automation for containers/storage.
- Important targets: Local binary and cross builds, unit and integration tests, validation, lint, docs/manpage generation, vendor maintenance, and tool installation.
- Control flow and state: Make variables control storage driver, transient mode, build tags, install paths, and test environment. Targets invoke Go commands, helper scripts, and docs tools.
- Dependencies and integration: Integrates with Cirrus scripts, docs Makefile, Go module tooling, and integration test suite.
- Risks: Environment-sensitive variables such as storage driver and rootless setup can change behavior; make target dependencies need to keep generated tools current.
- Test signals: CI executes `local-binary`, `local-cross`, `local-test-integration`, `local-test-unit`, `local-validate`, and `lint`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/check.go -->
# sources/cloud-native/containers-storage/check.go

- Purpose: Implements storage integrity checking and repair across layers, images, containers, and low-level graph-driver layers.
- Important APIs/types: Exported error aliases, `CheckOptions`, `CheckMost`, `CheckEverything`, `CheckReport`, `RepairOptions`, `RepairEverything`, `(*store).Check`, and `(*store).Repair`. Internal comparison types include `checkIgnore`, `checkFileInfo`, and `checkDirectory`.
- Control flow: `Check` derives ignore rules from graph/pull options, walks layer stores to validate big data, diff digests/sizes, mountability, and optional mounted contents, then walks image stores to validate big data and layer references, walks containers to validate data/image/layer references, flags old unreferenced layers, and compares graph-driver layer listing for unaccounted layers.
- State and persistence: Mostly read-only, but it mounts layers for inspection and uses graph-driver get/put. `Repair` mutates storage by deleting damaged containers/images/layers, unmounting layers, and removing unaccounted driver layers.
- Dependencies and integration: Relies on storage driver APIs, archive/tar diff generation, id mappings, lock-protected store readers, logrus, and shared error types.
- Risks: Expensive full-store operation; content comparison must correctly handle whiteouts, hard links, idmapped ownership, and configured ignore modes. Repair deletes data and must preserve order so child layers are removed before parents.
- Test signals: Unit tests cover directory comparison; integration tests should exercise damaged data, missing layers, and repair behavior across drivers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/check_test.go -->
# sources/cloud-native/containers-storage/check_test.go

- Purpose: Unit tests for `checkDirectory` and writable/read-only store detection helpers.
- Important tests: `TestCheckDirectory` builds expected directory trees from tar headers and validates whiteout/remove/replace semantics; `TestCheckDetectWriteable` checks read-write detection behavior.
- Control flow and state: In-memory test construction with temporary directories or store fixtures as needed; no persistent production state.
- Dependencies and integration: Uses Go `testing`, tar header helpers, and check.go internals because it is in package `storage`.
- Risks: Coverage is focused on comparison primitives, not full `Check`/`Repair` destructive workflows.
- Test signals: `go test` for the storage package.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/check_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/check.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/check.go

- Purpose: CLI command for running store integrity checks and optional repair.
- Important behavior: Builds `storage.CheckOptions`, invokes `m.Check`, prints layer/image/container problems, and optionally invokes repair options.
- Control flow: Parse flags for scope/repair behavior, call store check, format grouped errors, and set nonzero exit when problems or repair failures are present.
- State and persistence: Read-only unless repair is requested, in which case store contents may be deleted through library repair.
- Dependencies and integration: Calls the exported storage `Check`/`Repair` APIs and uses the common command registry in `main.go`.
- Risks: Repair is destructive; output format is intended for humans and may not be stable for scripts.
- Test signals: CLI integration tests and library check tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/config.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/config.go

- Purpose: CLI command that prints effective storage configuration.
- Important behavior: Reads store/options information and emits human or JSON output.
- Control flow and state: No mutation beyond normal store initialization.
- Dependencies and integration: Uses common CLI flag parsing and storage options/defaults.
- Risks: Output can expose host paths and graph driver options.
- Test signals: CLI smoke tests comparing effective config.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/container.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/container.go

- Purpose: Implements per-container inspection and big-data operations.
- Important functions: `container`, `listContainerBigData`, `getContainerBigData`, `getContainerBigDataSize`, `getContainerBigDataDigest`, `setContainerBigData`, `getContainerDir`, `getContainerRunDir`, and `containerParentOwners`.
- Control flow: Resolve container by ID/name, call storage APIs for metadata, big data, directory paths, or parent ownership chain, and write human or raw output.
- State and persistence: `setContainerBigData` writes big-data files and updates container JSON metadata through the store; read commands are non-mutating.
- Dependencies and integration: Relies on `storage.Store` container APIs and command flags for data file path/output selection.
- Risks: Raw big-data output can be binary; setting data from files mutates persistent store state.
- Test signals: CLI tests over create-container, data set/get, and path commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/containers.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/containers.go

- Purpose: Lists known containers.
- Important behavior: Calls `m.Containers()`, emits JSON when requested, otherwise prints container IDs with names and big-data item names.
- Control flow and state: Read-only command registered as `containers`.
- Dependencies and integration: Uses the common `jsonOutput` flag and storage store enumeration.
- Risks: Human output omits some fields; scripts should use JSON.
- Test signals: CLI list output after container creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/copy.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/copy.go

- Purpose: Copies file content between host paths and mounted storage objects.
- Important behavior: Parses chown options and calls storage copy helpers to place or retrieve files/directories.
- Control flow: Validate arguments, parse ownership override, open source/destination, and delegate to storage/archive copy logic.
- State and persistence: Mutates layer/container mounted content or host filesystem destinations depending on direction.
- Dependencies and integration: Uses storage mount/copy APIs and CLI flags.
- Risks: Ownership and path handling are security-sensitive; copying into mounted layers can alter container state.
- Test signals: Integration tests validating copied content and ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/create.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/create.go

- Purpose: Implements creation/import commands for storage-driver layers, logical layers, images, and containers.
- Important functions: `paramIDMapping`, `createStorageLayer`, `createLayer`, `importLayer`, `createImage`, and `createContainer`.
- Control flow: Parse ID/name/read-only/mount label/idmap/subuid/subgid flags, optionally read metadata from file, create or import layers, create images from top layers, and create containers from images.
- State and persistence: Mutates storage by adding driver layers, layer metadata, image records, container records, id mappings, metadata, and volatile flags.
- Dependencies and integration: Uses storage `Create*`, `ApplyDiff`, ID mapping options, and common command registration.
- Risks: ID/name collisions and overlapping ID maps must be rejected; importing diffs from stdin/files can ingest untrusted archives.
- Test signals: CLI integration tests and storage library create/import tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/dedup.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/dedup.go

- Purpose: CLI command for deduplicating storage content where the driver supports it.
- Important behavior: Accepts hash method selection, invokes store deduplication, and reports reclaimed/processed results.
- Control flow and state: Mutates storage driver backing files through dedup operations.
- Dependencies and integration: Depends on graph-driver support and the selected hash method, defaulting to CRC.
- Risks: Deduplication is filesystem/driver-sensitive and can be expensive.
- Test signals: Driver integration tests and reported dedup statistics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/dedup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/delete.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/delete.go

- Purpose: Implements deletion commands for layers, images, containers, and a generic delete dispatcher.
- Important functions/types: `deleteThing`, `deleteLayer`, `deletedImage`, `deleteImage`, and `deleteContainer`.
- Control flow: Resolve the requested object, call the matching store delete API, optionally force image deletion/testing behavior, and report deleted IDs/layers.
- State and persistence: Removes metadata records, big data directories, layers, images, and containers from storage.
- Dependencies and integration: Uses storage deletion APIs and command aliases.
- Risks: Destructive command; image deletion can cascade layer deletion; generic dispatch can surprise users if an ID matches multiple namespaces.
- Test signals: CLI delete tests and subsequent `exists`/list commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/diff.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/diff.go

- Purpose: Implements diff generation, change listing, applying diffs, and diff-size commands.
- Important functions/types: `changes`, `diff`, `fileFetcher`, `sendFileParts`, `GetBlobAt`, `applyDiffUsingStagingDirectory`, `applyDiff`, and `diffSize`.
- Control flow: Generate archive diffs between layers, list filesystem changes, optionally stream file chunks through a staging directory, apply tar streams to layers, and compute diff sizes.
- State and persistence: `applyDiff*` mutates layers; diff/read operations may mount or stream layer content.
- Dependencies and integration: Uses containers/image chunked interfaces, storage Diff/ApplyDiff APIs, and file streaming channels.
- Risks: Tar stream handling is sensitive to untrusted input; staging directory cleanup and chunk errors must be handled to avoid leaks/corruption.
- Test signals: Diff/apply round-trip integration tests and change-list expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/exists.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/exists.go

- Purpose: Tests whether a layer, image, container, or generic object exists.
- Important behavior: Dispatches by requested object type and uses store `Exists`/lookup APIs.
- Control flow and state: Read-only, returning success/failure via exit status and optional output.
- Dependencies and integration: Used by scripts to gate create/delete flows.
- Risks: Ambiguous names across object namespaces require explicit type to avoid confusion.
- Test signals: CLI exit status after object creation/deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/exists.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/gc.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/gc.go

- Purpose: Exposes garbage collection for unreferenced storage data.
- Important behavior: Calls `m.GarbageCollect()` and reports errors.
- Control flow and state: Mutates storage by removing unreferenced data directories or driver state that the library considers garbage.
- Dependencies and integration: Relies on store GC implementations, especially container/layer/image stores.
- Risks: GC is destructive and correctness depends on metadata references being current.
- Test signals: Integration tests that leave orphan data and verify cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/image.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/image.go

- Purpose: Implements per-image inspection, big-data, and directory path commands.
- Important functions: `image`, `listImageBigData`, `getImageBigData`, `wrongManifestDigest`, `getImageBigDataSize`, `getImageBigDataDigest`, `getImageDir`, `getImageRunDir`, and `setImageBigData`.
- Control flow: Resolve image, print metadata or JSON, list/get/set big data, calculate size/digest, and expose storage paths.
- State and persistence: `setImageBigData` writes persistent big-data items and updates size/digest metadata.
- Dependencies and integration: Uses digest handling and storage image APIs. The `wrongManifestDigest` helper supports legacy manifest digest behavior.
- Risks: Raw data output may be binary; setting manifest-like data affects later pulls/lookups.
- Test signals: Image create/data CLI tests and digest/size validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/images.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/images.go

- Purpose: Lists images and supports digest-based image lookup.
- Important functions: `images` and `imagesByDigest`; `imagesQuiet` controls terse output.
- Control flow: Enumerate images, output JSON or human list, optionally filter/lookup by digest.
- State and persistence: Read-only.
- Dependencies and integration: Uses storage image enumeration and digest metadata.
- Risks: Quiet output may omit information needed for disambiguation.
- Test signals: CLI output after image creation and digest assignment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/images.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layer.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/layer.go

- Purpose: Implements per-layer inspection, big-data operations, and parent-owner reporting.
- Important functions: `listLayerBigData`, `getLayerBigData`, `setLayerBigData`, `layer`, and `layerParentOwners`.
- Control flow: Resolve layer ID/name, display metadata, list/read/write big-data items, or traverse parent owners.
- State and persistence: `setLayerBigData` writes persistent layer big-data files; other commands are read-only.
- Dependencies and integration: Uses storage layer APIs and command flags.
- Risks: Big-data mutation can change layer metadata assumptions; parent ownership output depends on consistent layer graph.
- Test signals: CLI layer creation/data tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layers.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/layers.go

- Purpose: Lists logical layers and low-level storage-driver layers.
- Important functions: `storageLayers` and `layers`; flags include tree/quiet variants.
- Control flow: Enumerate store layers or driver-only layers, print IDs and metadata, optionally tree-format relationships.
- State and persistence: Read-only.
- Dependencies and integration: Uses storage layer enumeration, graph-driver layer listing, and `tree.go` formatting.
- Risks: Driver layer listing can reveal unaccounted internal layers that logical metadata does not know about.
- Test signals: CLI list after layer creation and tree formatting tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/layers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/main.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/main.go

- Purpose: Main CLI entry point and command registry dispatcher for the `containers-storage` diagnostic/admin tool.
- Important types/functions: `command`, global `commands`, `jsonOutput`, `force`, `main`, and `outputJSON`.
- Control flow: Initialize reexec, parse global flags into `types.StoreOptions`, load default options when none are supplied, resolve subcommand, parse command-specific flags, optionally reexec in a user namespace, set log level, open store with `storage.GetStore`, run command action, and exit with returned status.
- State and persistence: Store initialization may create/use lock files and storage roots. `store.Free()` is called before action, which is unusual but likely releases process-global store reference while leaving the handle usable.
- Dependencies and integration: Uses `mflag`, `unshare`, `reexec`, storage options, and command files that append in `init`.
- Risks: Commands rely on package init ordering only for registry population; `store.Free()` placement needs care if store lifetime expectations change.
- Test signals: CLI smoke tests for parsing, namespace behavior, JSON output, and command dispatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/metadata.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/metadata.go

- Purpose: Gets or sets metadata strings for layers, images, or containers.
- Important functions: `metadata` and `setMetadata`; `metadataQuiet` controls output.
- Control flow: Resolve object type/name, call corresponding metadata getter/setter, and print value or JSON/human response.
- State and persistence: `setMetadata` mutates metadata in the relevant store JSON.
- Dependencies and integration: Uses storage metadata APIs shared across object types.
- Risks: Metadata is opaque caller data; replacing it can break higher-level tools.
- Test signals: Round-trip get/set CLI tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/mount.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/mount.go

- Purpose: Mounts, unmounts, and checks mounted state for layers/containers.
- Important types/functions: `mountPointOrError`, `mountPointError`, `mount`, `unmount`, and `mounted`.
- Control flow: Resolve one or more IDs, call mount/unmount APIs, collect mount points or errors, and optionally emit JSON.
- State and persistence: Mutates mount state and reference counts in the storage driver/runtime.
- Dependencies and integration: Requires graph-driver mount support and appropriate privileges.
- Risks: Leaked mounts can block deletion; forced unmounts can disrupt users; JSON error aggregation must preserve per-ID failures.
- Test signals: Mount path existence, mounted command status, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/name.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/name.go

- Purpose: Gets, adds, removes, or replaces names for storage objects.
- Important functions: `getNames`, `addNames`, `removeNames`, and `setNames`.
- Control flow: Resolve object, apply name operation, persist through storage API, and print resulting names.
- State and persistence: Mutates object name indexes in store metadata.
- Dependencies and integration: Uses storage name update semantics and duplicate-name checks.
- Risks: Name collisions can remove or reassign references; scripts should prefer IDs for stable addressing.
- Test signals: Lookup by new/removed names and duplicate-name rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/shutdown.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/shutdown.go

- Purpose: Exposes store shutdown behavior from the CLI.
- Important behavior: `forceShutdown` flag controls whether shutdown should be forced.
- Control flow and state: Calls store shutdown API, which may release resources, unmount, or close driver state depending on backend.
- Dependencies and integration: Uses storage store lifecycle API.
- Risks: Forced shutdown can interrupt active users of the same store.
- Test signals: Store can be reopened cleanly after shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/shutdown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/status.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/status.go

- Purpose: Prints storage driver/store status.
- Important behavior: Calls status APIs and emits key/value or JSON output.
- Control flow and state: Read-only command registered as `status`.
- Dependencies and integration: Relies on graph-driver status support.
- Risks: Output shape is driver-specific; scripts need defensive parsing.
- Test signals: CLI status returns successfully for configured drivers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/tree.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/tree.go

- Purpose: Utility for printing layer/image parent relationships as a tree.
- Important types/functions: `treeNode`, `selectRoot`, `printSubTree`, and `printTree`.
- Control flow: Select roots from nodes, recursively print children with branch/continuation prefixes, and remove printed nodes until complete.
- State and persistence: Pure formatting helper; no storage mutation.
- Dependencies and integration: Used by layer/image list commands for tree output.
- Risks: Cycles or inconsistent parent data can cause missing or repeated output if not prefiltered.
- Test signals: `tree_test.go` exercises basic tree printing without assertions beyond no panic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/tree_test.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/tree_test.go

- Purpose: Minimal test coverage for tree formatting.
- Important test: `TestTree` invokes tree printing with sample nodes.
- Control flow and state: Pure in-memory test, no store interaction.
- Dependencies and integration: Uses Go `testing` in package main.
- Risks: The test is weak because it does not appear to assert exact output.
- Test signals: No panic/regression during `go test`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/unshare.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/unshare.go

- Purpose: Runs a command inside a user namespace through the containers/storage unshare helper.
- Important behavior: `unshareFn` delegates to namespace reexecution/command execution.
- Control flow and state: May reexec process with user namespace mappings and then run requested arguments.
- Dependencies and integration: Uses `pkg/unshare` and common CLI dispatch.
- Risks: Namespace behavior differs by kernel/subuid/subgid setup; nested unshare can confuse scripts.
- Test signals: Rootless CLI workflows and namespace-sensitive integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/unshare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/version.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/version.go

- Purpose: Prints containers-storage version/build information.
- Important behavior: `version` command emits version data in human or JSON form.
- Control flow and state: Read-only.
- Dependencies and integration: Uses module/version variables from the storage package/build.
- Risks: Missing linker/build metadata can produce incomplete version output.
- Test signals: CLI version smoke tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/wipe.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/wipe.go

- Purpose: Removes all storage content through the CLI.
- Important behavior: Calls store wipe API and returns any error.
- Control flow and state: Destructive full-store operation.
- Dependencies and integration: Uses storage wipe implementation across layers/images/containers.
- Risks: Irreversible data loss; should be protected by operator intent and isolated roots in tests.
- Test signals: Store lists are empty after wipe and can be reused.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/wipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/containers.go -->
# sources/cloud-native/containers-storage/containers.go

- Purpose: Implements the JSON-backed container metadata store for containers/storage.
- Important APIs/types: `Container`, `rwContainerStore`, `containerStore`, `copyContainer`, label/mount option accessors, lock methods, `newContainerStore`, lookup/name/metadata/big-data methods, create/delete/wipe, and garbage collection.
- Control flow: Store construction creates directories and lock file, loads stable and volatile JSON files, builds ID/layer/name/trunc indexes, resolves duplicate names by saving when holding a write lock, and serves reads/writes under a process RW lock plus cross-process lockfile.
- State and persistence: Stable containers live in `containers.json`; volatile containers live in `volatile-containers.json` in `runDir` when transient mode is enabled. Big data is stored as files under per-container data directories, with sizes and digests tracked in metadata. Saves use atomic file writes and lockfile write records.
- Dependencies and integration: Uses ID mapping validation, string ID generation, truncindex lookup, lockfile last-write detection, logrus, digest calculation, and store helper functions shared with images/layers.
- Risks: Concurrent readers must reload carefully when on-disk state changes; duplicate name cleanup requires write lock; volatile data is less durable by design; big-data keys map to filenames and must be validated.
- Test signals: Unit/integration tests for create/get/lookup/delete, transient store behavior, big-data size/digest backfill, lock/reload behavior, and GC of orphan datadirs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/build_and_test.sh -->
# sources/cloud-native/containers-storage/contrib/cirrus/build_and_test.sh

- Purpose: Cirrus script that builds containers/storage and runs driver-specific test suites.
- Important behavior: Installs tools, runs local binary and cross builds, then switches on `TEST_DRIVER` for overlay, overlay-transient, fuse-overlay, fuse-overlay-whiteout, vfs, aufs, btrfs, and zfs variants.
- Control flow and state: Source `lib.sh`, cd to `$GOSRC`, run make targets with driver-specific environment, and for some drivers set up backing loop devices or skip unsupported filesystems.
- Dependencies and integration: Requires Cirrus environment, make targets, kernel/filesystem support, fuse-overlayfs, and automation helper functions like `showrun`.
- Risks: Driver tests are host-kernel sensitive; unsupported filesystems or missing modules must fail clearly.
- Test signals: Cirrus build/test task status for each matrix entry.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/build_and_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/lib.sh -->
# sources/cloud-native/containers-storage/contrib/cirrus/lib.sh

- Purpose: Shared Cirrus shell library for environment normalization and dependency installation.
- Important functions: `bad_os_id_ver`, `lilto`, `bigto`, `install_fuse_overlayfs_from_git`, `install_bats_from_git`, and `check_filesystem_supported`.
- Control flow: Exports CI variables, sources containers automation common library when present, derives Go/source paths, computes `EPOCH_TEST_COMMIT`, defines package manager wrappers, and provides install/check helpers.
- State and persistence: Installs fuse-overlayfs and bats into system paths, clones temporary sources, and sets exported environment for child scripts.
- Dependencies and integration: Requires containers/automation helper functions, Go env, git, dnf/apt, sudo, and kernel module support checks.
- Risks: Heavy reliance on external automation library; global `set -a` export can leak variables; source installs from git are not version-pinned here.
- Test signals: Setup/build scripts successfully sourcing it and installing required tools.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/setup.sh -->
# sources/cloud-native/containers-storage/contrib/cirrus/setup.sh

- Purpose: Cirrus setup script that prepares Fedora/Debian test VMs.
- Important behavior: Sources `lib.sh`, shows environment, removes conflicting packages by distro, installs fuse-overlayfs from git, and installs bats.
- Control flow and state: Switches on `$OS_RELEASE_ID`; unsupported distributions call `bad_os_id_ver`.
- Dependencies and integration: Uses package wrappers and install helpers from `lib.sh`.
- Risks: Mutates host packages and installs from upstream git; unsupported distro detection must stay current with CI images.
- Test signals: Later build/test script finds fuse-overlayfs and bats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/timestamp.awk -->
# sources/cloud-native/containers-storage/contrib/cirrus/timestamp.awk

- Purpose: Prefixes CI log lines with elapsed time for easier diagnosis.
- Important behavior: Records `STARTTIME` in `BEGIN`, prints each input line with relative seconds, and prints total duration in `END`.
- Control flow and state: Stateless stream filter except for start timestamp.
- Dependencies and integration: Used by `.cirrus.yml` as `_TIMESTAMP` around setup/build/test scripts.
- Risks: Output buffering and awk implementation differences can affect live logs.
- Test signals: Cirrus logs show `[+NNNNs]` prefixes and END duration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/timestamp.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/deprecated.go -->
# sources/cloud-native/containers-storage/deprecated.go

- Purpose: Preserves deprecated interface names for compatibility with older consumers.
- Important types: `ROFileBasedStore`, `RWFileBasedStore`, `FileBasedStore`, `ROMetadataStore`, `RWMetadataStore`, `MetadataStore`, big-data store aliases, `FlaggableStore`, `ContainerStore`, `ROImageStore`, `ImageStore`, `ROLayerStore`, and `LayerStore`.
- Control flow and state: Pure type/interface declarations; no runtime behavior.
- Dependencies and integration: Re-exports or composes current internal interfaces so downstream packages can continue compiling.
- Risks: Deprecated interfaces can freeze old API shape and complicate refactoring; removal would be breaking.
- Test signals: Downstream compile compatibility and package API checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/deprecated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/docs/Makefile -->
# sources/cloud-native/containers-storage/docs/Makefile

- Purpose: Builds and installs man pages from Markdown documentation.
- Important targets: `docs` builds `.1` pages and `containers-storage.conf.5`; `install` installs `.5` pages under `${PREFIX}/share/man/man5`.
- Control flow and state: Uses `go-md2man` from `../tests/tools/build/go-md2man`, wildcard Markdown inputs, and `install`.
- Dependencies and integration: Called by top-level docs targets and packaging workflows.
- Risks: `MANPAGES_MD` references `docs/*.5.md` while the Makefile itself is already in docs, so path assumptions are sensitive to invocation directory.
- Test signals: Generated man pages exist and package install includes them.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/docs/Makefile -->
