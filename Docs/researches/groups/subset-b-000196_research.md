# Research Group subset-b-000196

This grouped report covers Moby daemon volume setup, wait/workdir helpers, version/user-agent helpers, error classification helpers, build/test/validation scripts, and legacy integration-cli API tests. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes.go -->
# sources/cloud-native/moby/daemon/volumes.go

## Purpose
Core daemon logic for translating a container's persisted and requested volume, bind, tmpfs, image, cluster, and named-pipe mounts into `container.MountPoints`.

## Important APIs and Types
Defines `mountSort`, `sortMounts`, `(*Daemon).registerMountPoints`, `(*Daemon).lazyInitializeVolume`, `(*Daemon).VolumesService`, `volumeMounter`, and `volumeWrapper`. `volumeWrapper` adapts `api/types/volume.Volume` plus `service.VolumesService` methods to the daemon volume interface used by mountpoints.

## Control Flow, State, and Persistence
`registerMountPoints` copies existing mountpoints, overlays `VolumesFrom`, legacy `HostConfig.Binds`, then structured `HostConfig.Mounts`. Duplicate destinations release prior volume references. Volume mounts call the volume service with container references, bind mounts may be marked skip-create, and image mounts resolve an image, create a hashed RW layer, mount it read-only, and store layer metadata on the mountpoint. On error, newly referenced volumes are released. Finally it locks the container only to swap `ctr.MountPoints` and release replaced backward-compatible volumes.

## Dependencies, Integration Points, Risks, and Test Signals
Integrates with `volume/service`, mount parsers, image/layer services, `errdefs`, and platform-specific `validateBindDaemonRoot`/`setBindModeIfNull`. Risks include leaked volume refs on partial failure, destination shadowing, daemon-root bind propagation, image-layer cleanup, and duplicate bind/tmpfs targets. Tests in this group and integration mount tests validate parser behavior, mount creation, volume deletion semantics, and platform propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_linux.go -->
# sources/cloud-native/moby/daemon/volumes_linux.go

## Purpose
Linux implementation of daemon-root bind validation used while registering bind mounts.

## Important APIs and Types
Defines `(*Daemon).validateBindDaemonRoot(mount.Mount) (bool, error)`.

## Control Flow, State, and Persistence
Non-bind mounts are ignored. For bind mounts, the function checks whether the mount source is inside the daemon root or the daemon root is inside the source. If unrelated, no special handling is required. If related and no propagation is specified, it returns `needsProp=true`, allowing callers to force `rslave`. Explicit `rslave` and `rshared` are accepted; private, shared, slave, and recursive-private modes are rejected as invalid parameters.

## Dependencies, Integration Points, Risks, and Test Signals
Used by `registerMountPoints` for both legacy binds and structured mounts. It depends on string prefix checks, `api/types/mount`, and `errdefs.InvalidParameter`. The risk is filesystem-prefix ambiguity if paths are not normalized upstream, because this file uses raw prefixes. `volumes_linux_test.go` exercises root, parent, child, and `/` sources with valid and invalid propagation modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_linux_test.go -->
# sources/cloud-native/moby/daemon/volumes_linux_test.go

## Purpose
Unit coverage for Linux daemon-root bind propagation validation.

## Important APIs and Types
Contains `TestBindDaemonRoot`, with table cases for nil, empty, private, rprivate, slave, rslave, shared, and an intended rshared case.

## Control Flow, State, and Persistence
The test builds a daemon rooted at `/a/b/c/daemon` and runs each propagation option against sources equal to the root, below it, above it, and `/`. It asserts whether an error is returned and whether the caller must apply propagation automatically.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `filepath` and `api/types/mount`. It directly guards the behavior consumed by `registerMountPoints`. A subtle test risk is that the "rshared propagation" row currently uses `PropagationRSlave`, so it does not independently verify explicit `rshared`. The suite still signals that unsafe propagation modes for daemon-root-related binds are rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_unit_test.go -->
# sources/cloud-native/moby/daemon/volumes_unit_test.go

## Purpose
Unit coverage for legacy `--volumes-from` parsing through the daemon mount parser.

## Important APIs and Types
Contains `TestParseVolumesFrom`, using `volumemounts.NewParser().ParseVolumesFrom`.

## Control Flow, State, and Persistence
The test parses empty input, plain container IDs, read-write and read-only suffixes, and an invalid mode. It verifies container ID extraction, default `rw`, explicit `ro`/`rw`, and error handling.

## Dependencies, Integration Points, Risks, and Test Signals
This guards the first overlay path in `registerMountPoints`, where volumes inherited from another container can replace earlier mountpoints. It does not create daemon state or volumes; the signal is parser contract stability. Risks outside this test include actual source container lookup, reference acquisition for anonymous volumes, and destination conflict cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_unit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_unix.go -->
# sources/cloud-native/moby/daemon/volumes_unix.go

## Purpose
Unix, non-Windows mount setup for starting containers.

## Important APIs and Types
Defines `(*Daemon).setupMounts` and Unix `setBindModeIfNull`.

## Control Flow, State, and Persistence
`setupMounts` collects tmpfs destinations, skips mountpoints covered by tmpfs, lazily restores volume handles, rejects daemon-host socket mounts during shutdown, and calls each mountpoint's `Setup` with mount label and remapped root identity. Cleanup callbacks are accumulated and released only on success. Non-network mounts are converted to `container.Mount` entries with bind recursion/read-only flags and volume mount events; network mounts are recorded on the container and appended after sorting. Network files under the daemon repository are chowned for user namespace remapping.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `cleanups.Composite`, id mapping, `volumemounts.MountPoint.Setup`, container network mount detection, and daemon volume events. Risks include cleanup leaks, incorrect read-only recursive option combinations, userns ownership failures, and ordering that could shadow nested mounts. Integration mount tests and daemon start tests exercise this path indirectly. `setBindModeIfNull` defaults local named volumes to SELinux shared label `z`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_windows.go -->
# sources/cloud-native/moby/daemon/volumes_windows.go

## Purpose
Windows implementation of mount setup and no-op platform hooks for bind mode and daemon-root propagation.

## Important APIs and Types
Defines Windows `(*Daemon).setupMounts`, `setBindModeIfNull`, and `validateBindDaemonRoot`.

## Control Flow, State, and Persistence
`setupMounts` walks container mountpoints, lazily initializes volume handles, calls `MountPoint.Setup` with empty identity and no validation callback, records temporary cleanups, and returns sorted `container.Mount` entries. Cleanup callbacks are invoked on setup failure and released on success. Unlike Unix, there is no network mount special handling, no SELinux mode default, and daemon-root bind propagation is always not needed.

## Dependencies, Integration Points, Risks, and Test Signals
Integrates with Windows runtime spec generation through daemon start. The file relies on `volumemounts` to implement Windows-specific validation and path handling. Risks include missing cleanup after setup errors, named-pipe or volume path normalization, and unsupported mount options. Windows integration tests in this group cover named-pipe bind validation and Windows-specific build/container behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volumes_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/wait.go -->
# sources/cloud-native/moby/daemon/wait.go

## Purpose
Thin daemon API for waiting on a container state condition.

## Important APIs and Types
Defines `(*Daemon).ContainerWait(ctx, name, condition)`.

## Control Flow, State, and Persistence
The method resolves the container by name or ID with `GetContainer`. If lookup fails, it returns nil channel plus the error immediately. Otherwise it delegates to `cntr.State.Wait(ctx, condition)`, returning a receive-only channel of `container.StateStatus`.

## Dependencies, Integration Points, Risks, and Test Signals
Used by API handlers and clients that implement `/containers/{id}/wait`. It depends on container state machinery for synchronization, exit code delivery, and context cancellation. Risks are mostly delegated: waiters must not leak on cancellation, and lookup errors must preserve not-found classification. Integration tests in `docker_api_containers_test.go` exercise wait behavior through the client.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/wait.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/workdir.go -->
# sources/cloud-native/moby/daemon/workdir.go

## Purpose
Backend helper for creating a container working directory on demand, mainly for builder flows.

## Important APIs and Types
Defines `(*Daemon).ContainerCreateWorkdir(cID string) error`.

## Control Flow, State, and Persistence
The method resolves a container, mounts its root filesystem, defers unmount, then calls `container.SetupWorkingDirectory` with the daemon's remapped root identity. It mutates container filesystem state by creating the configured workdir if needed.

## Dependencies, Integration Points, Risks, and Test Signals
Integrates with builder code that wants the daemon to handle workdir creation instead of paying the cost during general container setup. It depends on daemon mount/unmount paths and id mapping. Risks include leaving the rootfs mounted on error if defers do not run, userns ownership errors, and Windows performance regressions that motivated the helper. Build and container create integration tests are indirect signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/workdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/dockerversion/useragent.go -->
# sources/cloud-native/moby/dockerversion/useragent.go

## Purpose
Builds Docker daemon User-Agent strings, including daemon version metadata and optional upstream client context.

## Important APIs and Types
Defines `WithUpstreamUserAgent`, `DockerUserAgent`, `getDaemonUserAgent`, `getUpstreamUserAgent`, and `escapeStr`. Uses a private context key and `sync.Once` cache for daemon metadata.

## Control Flow, State, and Persistence
`DockerUserAgent` appends optional extra `useragent.VersionInfo` entries to the cached daemon UA, then appends `UpstreamClient(...)` if present in context. `getDaemonUserAgent` includes Docker version, Go runtime, git commit, kernel version when available, OS, and architecture. `escapeStr` escapes comment delimiters and backslashes, preserves tabs, and drops other control bytes.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on build-time variables in `version_lib.go`, `pkg/parsers/kernel`, and `pkg/useragent`. It is used for daemon-originated HTTP requests and preserving upstream caller attribution. Risks include header injection if sanitization regresses, stale cached version data in tests, and dropped kernel version on probe failure. `useragent_test.go` covers metadata, upstream comments, escaping, and control-character removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/dockerversion/useragent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/dockerversion/useragent_test.go -->
# sources/cloud-native/moby/dockerversion/useragent_test.go

## Purpose
Tests Docker daemon User-Agent formatting and upstream client sanitization.

## Important APIs and Types
Contains `TestDockerUserAgent`, table-testing `DockerUserAgent` and `WithUpstreamUserAgent`.

## Control Flow, State, and Persistence
Each case builds a context and optional metadata slice, then checks the exact generated string against `getDaemonUserAgent()` plus appended metadata or `UpstreamClient(...)`.

## Dependencies, Integration Points, Risks, and Test Signals
Uses `pkg/useragent.VersionInfo` and `gotest.tools` assertions. It verifies parentheses, semicolon, and backslash escaping, and confirms CR/LF injection bytes are stripped. The test relies on the cached daemon UA from the same process, so it avoids fixed kernel/OS expectations while preserving exact formatting for the dynamic prefix.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/dockerversion/useragent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/dockerversion/version_lib.go -->
# sources/cloud-native/moby/dockerversion/version_lib.go

## Purpose
Provides default build-time version variables for library imports.

## Important APIs and Types
Exports package variables `GitCommit`, `Version`, `BuildTime`, `PlatformName`, `ProductName`, and `DefaultProductLicense`.

## Control Flow, State, and Persistence
There is no runtime control flow. Values default to `"library-import"` or empty strings and are expected to be overwritten by linker flags in release builds.

## Dependencies, Integration Points, Risks, and Test Signals
Consumed by user-agent generation, version endpoints, binaries, and packaging metadata. Risk is build pipelines failing to override these variables, producing misleading version output. Tests usually assert formatting rather than fixed values; release/build scripts using ldflags are the main validation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/dockerversion/version_lib.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/errdefs/defs.go -->
# sources/cloud-native/moby/errdefs/defs.go

## Purpose
Defines Moby's package-boundary error classification interfaces.

## Important APIs and Types
Exports marker interfaces for not found, invalid parameter, conflict, unauthorized, unavailable, forbidden, system, not modified, not implemented, unknown, cancelled, deadline exceeded, and data loss errors.

## Control Flow, State, and Persistence
There is no executable flow or stored state. The file establishes type contracts: classified errors implement exactly one marker method such as `NotFound()` or `InvalidParameter()`.

## Dependencies, Integration Points, Risks, and Test Signals
The helper wrappers in `helpers.go` implement these interfaces and containerd errdefs recognizes them. API layers use classifications to choose HTTP/gRPC status codes. Risks are semantic overlap, packages asserting marker interfaces directly without unwrapping, and errors implementing multiple markers. `helpers_test.go` validates that wrapped errors are recognized through containerd predicates and Go unwrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/errdefs/defs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/errdefs/doc.go -->
# sources/cloud-native/moby/errdefs/doc.go

## Purpose
Package documentation for Moby error definitions.

## Important APIs and Types
Declares package `errdefs` and documents that packages should communicate error classes by implementing one marker interface, preferably checked through helper functions.

## Control Flow, State, and Persistence
No runtime behavior or state.

## Dependencies, Integration Points, Risks, and Test Signals
The documentation frames how `defs.go` and `helpers.go` should be used across daemon, API, and client boundaries. The key risk is misuse: direct type assertions without following unwrap chains or errors that implement more than one class. Compile and documentation generation are sufficient direct signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/errdefs/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/errdefs/helpers.go -->
# sources/cloud-native/moby/errdefs/helpers.go

## Purpose
Factory helpers that wrap arbitrary errors with Moby/containerd-compatible error classes.

## Important APIs and Types
Defines wrapper structs and constructors: `NotFound`, `InvalidParameter`, `Conflict`, `Unauthorized`, `Unavailable`, `Forbidden`, `System`, `NotModified`, `NotImplemented`, `Unknown`, `Cancelled`, `Deadline`, `DataLoss`, plus `FromContext`.

## Control Flow, State, and Persistence
Each wrapper embeds an error, implements the marker method, and exposes both `Cause` and `Unwrap`. Constructors return nil unchanged and return already-classified containerd errors unchanged; otherwise they wrap. `FromContext` maps `context.Canceled` to `Cancelled`, `context.DeadlineExceeded` to `Deadline`, and other context errors to `Unknown`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `github.com/containerd/errdefs` predicates for compatibility. API handlers and storage/daemon subsystems use these helpers to preserve status semantics across wrapping. Risks include mapping a class to the wrong containerd predicate, double-wrapping custom classes, and exposing unclassified errors that become generic 500s. `helpers_test.go` checks each class, unwrap identity, `errors.Is`, and recognition through additional wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/errdefs/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/errdefs/helpers_test.go -->
# sources/cloud-native/moby/errdefs/helpers_test.go

## Purpose
Unit tests for all errdefs wrapper constructors.

## Important APIs and Types
Defines `errTest`, a local `wrapped` interface, and tests for each class constructor.

## Control Flow, State, and Persistence
Each test starts with a plain error that should not satisfy the containerd predicate, wraps it with the Moby helper, verifies the corresponding containerd `Is...` predicate, checks `Unwrap` returns the original error, checks `errors.Is`, then wraps again with `fmt.Errorf("%w")` to verify causal-chain classification.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on standard `errors`, `fmt`, `testing`, and containerd errdefs. It is strong compatibility coverage for cross-package error classification. It does not directly test nil passthrough, already-classified passthrough, or `FromContext`; those remain residual test gaps.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/errdefs/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/buildkit-ref -->
# sources/cloud-native/moby/hack/buildkit-ref

## Purpose
Outputs the BuildKit repository and ref used by the current Moby checkout, intended for GitHub Actions environment export.

## Important APIs and Types
Shell function `resolve_github_commit_sha(repo, ref)` uses `gh api` or `curl` plus `jq`. Main variables are `buildkit_pkg`, `buildkit_ref`, and `buildkit_repo`.

## Control Flow, State, and Persistence
The script queries `go list -m` for `github.com/moby/buildkit`, respects module replacement path/version, strips `github.com/`, resolves pseudo-version commit suffixes to full GitHub SHAs, and prints `BUILDKIT_REPO=` and `BUILDKIT_REF=` lines. It writes no files itself.

## Dependencies, Integration Points, Risks, and Test Signals
Requires Go module metadata and GitHub API access for pseudo-version expansion; optionally uses `GH_TOKEN`. Risks include non-GitHub BuildKit replacements, API rate limits, missing `jq`, or pseudo-version parsing assumptions. CI jobs that consume `$GITHUB_ENV` are the integration signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/buildkit-ref -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/dev.sh -->
# sources/cloud-native/moby/hack/dev.sh

## Purpose
Developer loop that repeatedly builds, installs, and runs `dockerd` in debug mode.

## Important APIs and Types
No functions. It invokes `./hack/make.sh binary`, `KEEPBUNDLE=1 ./hack/make.sh install-binary`, and `dockerd --debug`.

## Control Flow, State, and Persistence
An infinite loop rebuilds the daemon binary. Build failures sleep for five seconds and retry. Install failures skip to the next loop. `dockerd` exits are ignored, followed by a short sleep.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on the repository build container/tooling and a runnable daemon environment. It persists installed binaries through `hack/make.sh install-binary`. Risks include accidental long-running daemon loops, stale bundles with `KEEPBUNDLE`, and masking daemon crash exits. Validation is manual developer use rather than automated tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/dev.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/dind -->
# sources/cloud-native/moby/hack/dind

## Purpose
Docker-in-Docker wrapper for privileged containers that need to run Docker/Moby tests or daemons.

## Important APIs and Types
Shell entrypoint using environment variable `container=docker`, mounts, cgroup v2 setup, and final `exec "$@"`.

## Control Flow, State, and Persistence
The script mounts securityfs for AppArmor detection when available, mounts `/tmp` as tmpfs if needed, enables cgroup v2 nesting by moving processes to `/init` and writing subtree controllers in a retry loop, makes `/` recursively shared, and executes the requested command. If no command is supplied it prints an error.

## Dependencies, Integration Points, Risks, and Test Signals
Requires privileged container permissions, `mountpoint`, cgroup files, and kernel support. Used by CI/development containers. Risks are broad privileged mount changes, securityfs exposure, infinite cgroup retry if controllers cannot be enabled, and host-dependent behavior. Test signals are integration jobs that run daemon and archive/network tests inside DinD.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/dind -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/dind-systemd -->
# sources/cloud-native/moby/hack/dind-systemd

## Purpose
Systemd-based Docker-in-Docker entrypoint for privileged test containers.

## Important APIs and Types
Writes systemd unit files for `docker-entrypoint.target`, `docker-entrypoint.service`, and optional firewalld log collection. Uses `container=docker`, `FIREWALLD`, and quoted command storage.

## Control Flow, State, and Persistence
The script requires a command and TTY, mounts `/tmp`, makes root propagation shared, mounts securityfs when possible, optionally configures firewalld trusted zone and log collection, persists environment and command under `/etc`, creates a systemd service that runs the command and exits systemd with the command's status, masks/unmasks selected services, then execs systemd.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on privileged container capabilities, systemd binaries, writable `/etc/systemd`, and optional firewalld. Risks include command quoting bugs, service exit-status translation, mutable system configuration, and privileged securityfs/mount propagation. CI jobs needing systemd semantics and firewall behavior are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/dind-systemd -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/dockerfile/cli.sh -->
# sources/cloud-native/moby/hack/dockerfile/cli.sh

## Purpose
Builds or downloads the Docker CLI binary for Dockerfile-based builds.

## Important APIs and Types
Takes `version`, `repository`, and `outdir` arguments. Uses `xx-info`, `curl`, `tar`, `git`, `xx-go`, and `xx-verify`.

## Control Flow, State, and Persistence
The script constructs a static download URL from architecture and version. If the archive exists, it downloads and extracts `docker/docker`. Otherwise it initializes a git repo, fetches the requested version/tags, checks out the version, builds either `./cmd/docker` from `components/cli` layout or runs the CLI build script, and verifies the output binary.

## Dependencies, Integration Points, Risks, and Test Signals
Used in multi-platform Dockerfile build pipelines. It writes only under `outdir` plus temporary git working state. Risks include network failures, unavailable static binary URLs, repository layout drift, shallow fetch/tag resolution issues, and cross-build wrapper correctness. `xx-verify` and CI image builds are the direct validation signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/dockerfile/cli.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/dockerfile/etc/docker/daemon.json -->
# sources/cloud-native/moby/hack/dockerfile/etc/docker/daemon.json

## Purpose
Daemon configuration fragment for Dockerfile build/test images.

## Important APIs and Types
JSON config defines a `crun` runtime with path `/usr/local/bin/crun`.

## Control Flow, State, and Persistence
No executable flow. When installed as Docker daemon config, it persists runtime registration so containers can request `--runtime=crun`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on the `crun` binary being present at the configured path. Integrates with daemon startup and runtime selection in CI images. Risks include daemon startup failure if JSON is malformed or runtime path assumptions drift. Test signal is daemon boot and runtime-specific integration tests inside the image.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/dockerfile/etc/docker/daemon.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/dockerfile/install/install.sh -->
# sources/cloud-native/moby/hack/dockerfile/install/install.sh

## Purpose
Generic installer dispatcher used by Dockerfile build stages.

## Important APIs and Types
Uses `PREFIX`, optional `TMP_GOPATH`, computed `GO_BUILDMODE`, and sourced `<bin>.installer` files that define `install_<bin>`.

## Control Flow, State, and Persistence
The script creates a temporary GOPATH unless provided, chooses PIE build mode except on mips and ppc64, resolves the installer directory, shifts the binary name argument, sources the matching installer, and calls its install function with remaining arguments.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go, installer files in the same directory, and shell sourcing. It writes installed binaries under `PREFIX` by convention and may create temporary GOPATH state. Risks include missing installer files, function-name injection from `bin`, unremoved temp GOPATH in this snippet, and architecture buildmode mismatches. Dockerfile build jobs validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/dockerfile/install/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/generate-authors.sh -->
# sources/cloud-native/moby/hack/generate-authors.sh

## Purpose
Regenerates the repository `AUTHORS` file from git history.

## Important APIs and Types
Computes `SCRIPTDIR` and `ROOTDIR`, then uses `git log --format='%aN <%aE>'` and `sort -uf`.

## Control Flow, State, and Persistence
The script overwrites `AUTHORS` with a generated header and unique sorted author identities, relying on `.mailmap` for normalization.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on a full enough git history and locale `C.UTF-8`. Risks include shallow clones omitting contributors, mailmap changes altering output, and generated-file churn. Validation is by rerunning the script and checking a clean diff.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/generate-authors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/generate-test-certs.sh -->
# sources/cloud-native/moby/hack/generate-test-certs.sh

## Purpose
Generates trusted CA, server, and client TLS certificates for integration tests.

## Important APIs and Types
Uses `openssl genrsa`, `openssl req`, `openssl x509`, and temporary extension config files under `integration/testdata/https`.

## Control Flow, State, and Persistence
The script creates a CA key/cert, server key/CSR/options/cert, client key/CSR/options/cert, then removes CA serial, CA key, configs, and CSRs. SANs include wildcard, localhost, IPv4 loopback, and IPv6 loopback; server and client certs get appropriate extended key usages.

## Dependencies, Integration Points, Risks, and Test Signals
Supports HTTPS daemon/client integration data and symlinked integration-cli fixtures. Risks include non-deterministic key/cert output, OpenSSL behavior drift, certificate expiry, and leaving private CA key only transiently. Tests that use TLS fixtures validate the generated artifacts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/generate-test-certs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/generate-test-rogue-certs.sh -->
# sources/cloud-native/moby/hack/generate-test-rogue-certs.sh

## Purpose
Generates rogue CA, server, and client TLS certificates for negative HTTPS integration tests.

## Important APIs and Types
Uses the same OpenSSL primitives as trusted cert generation but writes `*-rogue-*` files under `integration-cli/fixtures/https`.

## Control Flow, State, and Persistence
The script creates an "Evil Inc" CA, rogue server cert, rogue client cert, matching extension config files, then removes serial, CA private key, configs, and CSRs. Persisted outputs are rogue public CA/certs and private keys used by tests.

## Dependencies, Integration Points, Risks, and Test Signals
Used by tests that assert daemon/client TLS rejection of untrusted identities. Risks mirror the trusted generator: nondeterminism, OpenSSL compatibility, expiry, and fixture path assumptions. HTTPS negative integration tests are the validation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/generate-test-rogue-certs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make.sh -->
# sources/cloud-native/moby/hack/make.sh

## Purpose
Main bundle dispatcher for building Moby binaries and test artifacts inside the project build environment.

## Important APIs and Types
Exports `DOCKER_PKG`, `SCRIPTDIR`, `MAKEDIR`, `PKG_CONFIG`, computes `VERSION`, `GITCOMMIT`, build tags, static ldflags, and defines `bundle()` plus `main()`.

## Control Flow, State, and Persistence
The script normalizes CI ref names into versions, computes build time from `SOURCE_DATE_EPOCH`, resolves git commit and dirty suffix, optionally enters auto-GOPATH mode, adds journald tags when libsystemd is available, sets debug flags, and dispatches requested bundle scripts from `hack/make`. With no args it runs default bundles: daemon binary, dynamic binary, integration tests, and docker-py tests.

## Dependencies, Integration Points, Risks, and Test Signals
All `hack/make/*` scripts depend on its exported environment. It writes bundle artifacts under `bundles/` through child scripts. Risks include environment-sensitive reproducibility, shell word splitting in bundle args, dirty tree version suffixes, and platform-specific linker tags. CI build/test jobs and install scripts are the validation surface.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.binary -->
# sources/cloud-native/moby/hack/make/.binary

## Purpose
Shared shell helper for building Go binary artifacts.

## Important APIs and Types
Defines `binary_extension()` and uses `BINARY_NAME`, `BINARY_EXTENSION`, `BINARY_FULLNAME`, `DEST`, and Go build environment/ldflags from `make.sh`.

## Control Flow, State, and Persistence
The helper determines a Windows `.exe` extension when needed, prepares binary output names, and performs the common Go build steps used by daemon/proxy/client bundle wrappers. It places outputs in the active bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Sourced by `binary-*` and `dynbinary-*` scripts. Depends on Go, cross-compilation environment, and ldflags set upstream. Risks include extension mismatch, stale bundle destinations, and incorrect static/dynamic flags. Successful binary bundle builds validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.binary -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.go-autogen -->
# sources/cloud-native/moby/hack/make/.go-autogen

## Purpose
Shared build helper for generating Go package metadata before compiling.

## Important APIs and Types
Uses package/version variables exported by `make.sh` to generate source consumed by Docker binaries.

## Control Flow, State, and Persistence
The script writes generated Go version data into the build tree or bundle workspace so compiled binaries embed version, git commit, platform, product, license, and build-time information.

## Dependencies, Integration Points, Risks, and Test Signals
Sourced by binary bundle scripts. Risks include generated file drift, incorrect linker/build metadata, and dirty workspace effects. Compile success plus `docker version`/CLI version checks are the practical signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.go-autogen -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.install -->
# sources/cloud-native/moby/hack/make/.install

## Purpose
Shared install helper for copying bundle outputs into an install destination.

## Important APIs and Types
Uses bundle destination variables, `DESTDIR`/`PREFIX` style environment, and file-install commands.

## Control Flow, State, and Persistence
The helper checks that bundle outputs exist, creates target directories, and copies or installs binaries into the configured prefix.

## Dependencies, Integration Points, Risks, and Test Signals
Sourced by `install-binary` and `install-proxy`. It mutates the host/container filesystem. Risks include installing stale artifacts, permissions errors, and overwriting unrelated binaries when prefixes are misconfigured. `hack/dev.sh`, CI image builds, and post-install command availability validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.install -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.integration-daemon-start -->
# sources/cloud-native/moby/hack/make/.integration-daemon-start

## Purpose
Starts a daemon configured for integration tests.

## Important APIs and Types
Uses `TEST_CLIENT_BINARY`, `DOCKER_CLI_PATH`, `DOCKER_TEST_HOST`, `DOCKER_GRAPHDRIVER`, `DOCKER_USERLANDPROXY`, `DOCKER_STORAGE_OPTS`, `DOCKER_REMAP_ROOT`, `DOCKER_EXPERIMENTAL`, `DOCKER_FIREWALL_BACKEND`, and `DOCKER_ROOTLESS`.

## Control Flow, State, and Persistence
The script prepends built daemon paths, resolves the test Docker CLI, handles Windows pipe defaults, requires `dockerd`, constructs daemon flags for graphdriver, userland proxy, API version, storage opts, remap, experimental, firewall, and rootless modes, then starts the daemon unless a remote host is configured.

## Dependencies, Integration Points, Risks, and Test Signals
Sourced by integration test scripts. It creates daemon root/pid/log/socket state through `dockerd`. Risks include wrong host/socket selection, rootless prerequisites, firewall backend divergence, and stale daemon state. Integration suites using `hack/make/test-integration*` validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.integration-daemon-start -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.integration-daemon-stop -->
# sources/cloud-native/moby/hack/make/.integration-daemon-stop

## Purpose
Stops the integration-test daemon started by the make helpers.

## Important APIs and Types
Uses daemon pid/log/socket environment established by `.integration-daemon-start`.

## Control Flow, State, and Persistence
The script checks whether a local daemon was started, sends termination, waits for exit, and performs cleanup around daemon process state. Remote daemon configurations are left alone.

## Dependencies, Integration Points, Risks, and Test Signals
Used by integration test wrappers to avoid leaking dockerd processes. Risks include killing the wrong process if pid files are stale, failing to stop a wedged daemon, or skipping cleanup when environment variables are inconsistent. Suite teardown and clean process tables validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.integration-daemon-stop -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.integration-test-helpers -->
# sources/cloud-native/moby/hack/make/.integration-test-helpers

## Purpose
Shared shell library for integration test selection, environment isolation, suite binary builds, repeats, and timeouts.

## Important APIs and Types
Defines `setup_integration_test_filter`, `run_test_integration`, `run_test_integration_suites`, `build_test_suite_binaries`, `build_test_suite_binary`, `cleanup_test_suite_binaries`, `repeat`, `test_env`, and `set_repeat_timeout`.

## Control Flow, State, and Persistence
It derives test filters from `TESTFLAGS`, builds suite binaries with selected tags, creates isolated fake HOME/TEMP and daemon destinations, disables Go/Delve telemetry, runs suites under a scrubbed `env -i`, supports repeat loops, and manages cleanup of suite binaries.

## Dependencies, Integration Points, Risks, and Test Signals
Sourced by integration test bundle scripts. Depends on Go, `gotestsum`/test binaries, daemon start helpers, and many `DOCKER_*` variables. Risks include losing required environment through isolation, insufficient timeout scaling, stale binaries, and repeat logic masking flakiness. CI integration bundles directly validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.integration-test-helpers -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.mkwinres -->
# sources/cloud-native/moby/hack/make/.mkwinres

## Purpose
Windows resource generation helper for embedding version metadata into Windows binaries.

## Important APIs and Types
Uses version/product/license variables from `make.sh` and `mkwinres`-style tooling to produce `.syso` resources.

## Control Flow, State, and Persistence
The helper prepares resource metadata and emits generated files consumed by Windows Go builds. It is used only when building Windows artifacts.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Windows resource tooling and correct version variables. Risks include malformed resource metadata, stale generated `.syso` files, and mismatches between CLI version output and Windows file properties. Windows binary builds are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/.mkwinres -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/binary -->
# sources/cloud-native/moby/hack/make/binary

## Purpose
Bundle target for building the primary Docker CLI/static binary set through shared helpers.

## Important APIs and Types
Thin wrapper around `.binary` with `BINARY_NAME`/package settings.

## Control Flow, State, and Persistence
Delegates common build setup to `.binary`, producing a bundle under `bundles/binary` or the active destination.

## Dependencies, Integration Points, Risks, and Test Signals
Called by `hack/make.sh binary` and developer loops. Risks are inherited from `.binary`: wrong package path, missing version generation, and stale output. Successful CLI binary execution and install bundle tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/binary -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/binary-daemon -->
# sources/cloud-native/moby/hack/make/binary-daemon

## Purpose
Bundle target for building the `dockerd` daemon binary.

## Important APIs and Types
Sets daemon-specific binary name/package variables and sources shared binary generation helpers.

## Control Flow, State, and Persistence
Builds `dockerd` with static build tags/ldflags from `make.sh`, writing to the daemon binary bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Required by integration daemon startup, install-binary, and release artifacts. Risks include missing daemon build tags such as journald/static settings, incorrect embedded version data, and cross-platform incompatibility. Integration suites that start `dockerd` validate the output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/binary-daemon -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/binary-proxy -->
# sources/cloud-native/moby/hack/make/binary-proxy

## Purpose
Bundle target for building `docker-proxy`.

## Important APIs and Types
Thin wrapper setting proxy binary/package variables and sourcing `.binary`.

## Control Flow, State, and Persistence
Compiles the userland proxy binary into the active bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Used when integration or libnetwork tests require `docker-proxy`. Risks include missing binary in PATH for bridge/network tests and build tag mismatches. `hack/test/unit` triggers proxy build/install for libnetwork bridge packages when needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/binary-proxy -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/dynbinary -->
# sources/cloud-native/moby/hack/make/dynbinary

## Purpose
Bundle target for dynamically linked Docker binary artifacts.

## Important APIs and Types
Wrapper around shared binary logic with dynamic-build flags rather than static ldflags.

## Control Flow, State, and Persistence
Builds into the `dynbinary` bundle destination, relying on upstream environment to select dynamic linking behavior.

## Dependencies, Integration Points, Risks, and Test Signals
Used by default `hack/make.sh` bundles. Risks include runtime library availability and divergence from static binary behavior. CI build and integration runs using `dynbinary` validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/dynbinary -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/dynbinary-daemon -->
# sources/cloud-native/moby/hack/make/dynbinary-daemon

## Purpose
Builds a dynamically linked `dockerd` daemon binary.

## Important APIs and Types
Daemon-specific wrapper for `.binary`/dynamic build settings.

## Control Flow, State, and Persistence
Compiles `dockerd` into a dynamic daemon bundle, preserving version metadata from `make.sh`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on system libraries such as libsystemd when journald tags are enabled. Risks include missing runtime libraries in target images and mismatch with static daemon behavior. Daemon startup in test bundles is the validation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/dynbinary-daemon -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/dynbinary-proxy -->
# sources/cloud-native/moby/hack/make/dynbinary-proxy

## Purpose
Builds a dynamically linked `docker-proxy` binary.

## Important APIs and Types
Proxy-specific dynamic wrapper around shared binary helpers.

## Control Flow, State, and Persistence
Compiles proxy output into the dynamic proxy bundle destination.

## Dependencies, Integration Points, Risks, and Test Signals
Used by networking tests when dynamic artifacts are preferred. Risks include missing runtime libraries and proxy not found by daemon/test PATH. Libnetwork and integration networking tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/dynbinary-proxy -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/install-binary -->
# sources/cloud-native/moby/hack/make/install-binary

## Purpose
Installs built Docker binaries from bundle output into the configured destination.

## Important APIs and Types
Sources `.install` and uses binary bundle paths plus install prefix variables.

## Control Flow, State, and Persistence
Ensures the binary bundle is present or built, creates install directories, and installs binaries. It mutates the local/container filesystem.

## Dependencies, Integration Points, Risks, and Test Signals
Used by `hack/dev.sh` and CI images. Risks include stale binary installation, permission errors, and PATH confusion when multiple bundles exist. Post-install `dockerd`/`docker` invocation validates it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/install-binary -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/install-proxy -->
# sources/cloud-native/moby/hack/make/install-proxy

## Purpose
Installs `docker-proxy` from bundle output.

## Important APIs and Types
Thin wrapper around `.install` for the proxy artifact.

## Control Flow, State, and Persistence
Copies the built proxy binary into the configured install prefix.

## Dependencies, Integration Points, Risks, and Test Signals
Used by unit/integration tests that require userland proxy availability. Risks are missing or stale proxy binaries and insufficient install permissions. Network and libnetwork tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/install-proxy -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/run -->
# sources/cloud-native/moby/hack/make/run

## Purpose
Convenience bundle for running a development daemon with selected flags.

## Important APIs and Types
Uses `DOCKER_GRAPHDRIVER`, `DOCKER_USERLANDPROXY`, `DOCKER_STORAGE_OPTS`, `DOCKER_PORT`, `DELVE_PORT`, `DOCKER_REMAP_ROOT`, `DOCKER_EXPERIMENTAL`, and `DOCKER_ROOTLESS`.

## Control Flow, State, and Persistence
The script resolves `dockerd`, builds a flag list for graphdriver, userland proxy, storage opts, TCP port, Delve debug port, remap, experimental, and rootless mode. It may wrap the daemon with Delve, choose rootless helpers, and finally exec/run the daemon.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on a built `dockerd`, optional Delve, and rootless prerequisites. It creates daemon runtime state and listens on configured sockets/ports. Risks include exposing TCP daemon ports, debug server exposure, and rootless setup drift. Manual developer use is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/run -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-docker-py -->
# sources/cloud-native/moby/hack/make/test-docker-py

## Purpose
Runs Docker SDK for Python integration tests against the test daemon.

## Important APIs and Types
Uses Python test options, graphdriver settings, selected deselected tests, and integration daemon helpers.

## Control Flow, State, and Persistence
The script configures daemon graphdriver expectations, excludes known unsupported or incompatible SDK tests, starts the integration daemon through shared helpers, and runs the Python test suite with the configured environment.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Python test dependencies, a compatible daemon, and test certificates/environment. Risks include skipped tests hiding regressions, SDK test drift, and graphdriver-specific failures. CI docker-py bundle results are the direct signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-docker-py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-integration -->
# sources/cloud-native/moby/hack/make/test-integration

## Purpose
Runs the main Go integration test suite.

## Important APIs and Types
Sources `.integration-test-helpers` and calls the standard integration runner.

## Control Flow, State, and Persistence
The script delegates daemon setup, filter setup, suite binary building, environment isolation, execution, and cleanup to shared helpers.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `hack/make/.integration-*`, Go test tooling, and a runnable daemon. Risks are inherited from shared helpers: stale daemon state, incorrect filters, and environment loss. The suite's pass/fail result is the validation signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-integration -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-integration-flaky -->
# sources/cloud-native/moby/hack/make/test-integration-flaky

## Purpose
Runs integration tests marked or selected as flaky, usually with repeat/retry behavior.

## Important APIs and Types
Uses `.integration-test-helpers`, `TESTFLAGS`, repeat controls, and flaky test filters.

## Control Flow, State, and Persistence
The script configures filters for flaky tests and executes them through the same daemon and environment isolation used by the main integration bundle.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on the integration helper library and test naming conventions. Risks include stale flaky classification, repeat loops masking deterministic failures, and long runtime. CI flaky lane behavior and failure reproduction are the signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-integration-flaky -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-integration-shell -->
# sources/cloud-native/moby/hack/make/test-integration-shell

## Purpose
Runs shell-based integration tests through the shared integration environment.

## Important APIs and Types
Thin shell wrapper around integration helper functions and shell test entrypoints.

## Control Flow, State, and Persistence
Delegates daemon startup, environment setup, and execution to `.integration-test-helpers`, then runs the shell integration suite.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on shell test files, daemon helpers, and built binaries. Risks include shell portability, environment leakage, and daemon cleanup. CI shell integration results validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/make/test-integration-shell -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/test/e2e-run.sh -->
# sources/cloud-native/moby/hack/test/e2e-run.sh

## Purpose
End-to-end test runner wrapper for newer and legacy integration suites.

## Important APIs and Types
Defines `run_test_integration`, `run_test_integration_suites`, `run_test_integration_legacy_suites`, and `test_env`.

## Control Flow, State, and Persistence
The script constructs a test environment, runs selected suite binaries or legacy suites, and propagates results. It centralizes environment variables needed by e2e tests rather than relying on the caller's shell.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on built test binaries, daemon/client binaries, and e2e environment variables. Risks include inconsistent behavior with `hack/make` helpers, missing cleanup between suites, and stale legacy suite assumptions. E2E CI lanes validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/test/e2e-run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/test/unit -->
# sources/cloud-native/moby/hack/test/unit

## Purpose
Runs Go unit tests across Moby modules and writes coverage/JUnit/report artifacts.

## Important APIs and Types
Uses `TESTFLAGS`, `TESTDIRS`, build tags `netgo journald`, `gotestsum`, module package lists, and bundle outputs under `bundles/`.

## Control Flow, State, and Persistence
The script detects whether requested packages fall under `api`, `client`, root, or `libnetwork`, runs separate module tests with `-mod=readonly`, excludes vendor/integration packages for root tests, builds/installs `docker-proxy` if bridge tests need it, runs libnetwork tests serially, and optionally reruns `TestFlaky.*` with retries. It writes JSON, JUnit, and coverage files under `bundles`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go, `gotestsum`, module layout, and optionally docker-proxy. Risks include shell word splitting in test flags/package lists, module selection misses, and flaky reruns hiding nondeterminism. The produced reports and exit status are the direct test signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/test/unit -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/.validate -->
# sources/cloud-native/moby/hack/validate/.validate

## Purpose
Shared validation bootstrap for comparing a PR branch against upstream.

## Important APIs and Types
Exports `VALIDATE_REPO`, `VALIDATE_BRANCH`, `VALIDATE_HEAD`, `VALIDATE_ORIGIN_BRANCH`, `VALIDATE_UPSTREAM`, `VALIDATE_COMMIT_LOG`, `VALIDATE_COMMIT_DIFF`, and helper functions `validate_diff` and `validate_log`.

## Control Flow, State, and Persistence
If `VALIDATE_UPSTREAM` is unset, it computes HEAD, fetches the upstream branch when needed, resolves the upstream commit, and defines helper functions that return diffs/logs only when HEAD differs from upstream.

## Dependencies, Integration Points, Risks, and Test Signals
Sourced by validation scripts. Depends on git remotes/network unless `VALIDATE_ORIGIN_BRANCH` is supplied. Risks include fetch cost, wrong upstream branch, and empty diffs for merge-base edge cases. Validation scripts consuming consistent diffs/logs are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/.validate -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/all -->
# sources/cloud-native/moby/hack/validate/all

## Purpose
Runs the full validation set.

## Important APIs and Types
Sources `default` and `vendor` from the validation directory.

## Control Flow, State, and Persistence
The script computes `SCRIPTDIR`, then sequentially executes default validation and vendoring validation in the current shell.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on every sourced validation script and shared `.validate`. Risks include sourced scripts mutating shell state and early exit preventing later checks. CI validation pass/fail is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/all -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/dco -->
# sources/cloud-native/moby/hack/validate/dco

## Purpose
Validates Developer Certificate of Origin signoffs on changed commits.

## Important APIs and Types
Uses `validate_diff`, `validate_log`, `dcoRegex`, `githubUsernameRegex`, and `check_dco`.

## Control Flow, State, and Persistence
The script sums added/deleted lines. If there are changes, it iterates changed commits, skips contentless commits, checks commit bodies for a valid `Signed-off-by:` marker, and fails with a list of bad commits.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on git history and `.validate`. Risks include regex rejecting unusual but valid identities, shell array behavior with many commits, and bypass when diff has no additions/deletions. CI DCO validation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/dco -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/default -->
# sources/cloud-native/moby/hack/validate/default

## Purpose
Runs the default, non-vendor validation set.

## Important APIs and Types
Sources `pkg-imports`, `deprecate-integration-cli`, `golangci-lint`, and `shfmt`; DCO is intentionally skipped here.

## Control Flow, State, and Persistence
The script computes `SCRIPTDIR` and sources each validation script in order, failing on the first script that exits nonzero.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on shell sourcing and the individual validators. Risks include later checks not running after an early failure and sourced scripts leaking variables. CI default validation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/default -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/deprecate-integration-cli -->
# sources/cloud-native/moby/hack/validate/deprecate-integration-cli

## Purpose
Prevents adding new tests to deprecated `integration-cli` API/CLI test files.

## Important APIs and Types
Uses `.validate`, `validate_diff`, grep for added `func ... Test` lines, and GitHub Actions `::error::` output.

## Control Flow, State, and Persistence
The script diffs changed `integration-cli/*_api_*.go` and `integration-cli/*_cli_*.go` files, looking only at added lines. If new test functions are found, it prints an error instructing authors to add tests under `integration/COMPONENT/`; otherwise it prints success.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on diff context and naming conventions. Risks include missing tests with nonstandard names or blocking helper functions that match the regex. CI validation protects migration away from integration-cli.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/deprecate-integration-cli -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/golangci-lint -->
# sources/cloud-native/moby/hack/validate/golangci-lint

## Purpose
Runs golangci-lint across all Go modules except `man`.

## Important APIs and Types
Uses `GOLANGCI_LINT_OPTS`, `DOCKER_BUILDTAGS`, `pkg-config libsystemd`, module discovery by `find go.mod`, and `.golangci.yml`.

## Control Flow, State, and Persistence
The script sets a default timeout, adds `journald` build tag when libsystemd is available, discovers module directories, then runs `golangci-lint run` in each module with shared config and build tags.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on golangci-lint, Go module layout, pkg-config, and shell arrays. Risks include platform-dependent tags, long runtime, lint config drift, and missing modules filtered by path. CI lint results validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/golangci-lint -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/module-replace -->
# sources/cloud-native/moby/hack/validate/module-replace

## Purpose
Ensures local replace rules are present when `api` or `client` module source changes require them.

## Important APIs and Types
Uses `.validate`, `filter_diff`, `only_changes_module`, `go list -m -json`, `jq`, and `TEST_FORCE_VALIDATE`.

## Control Flow, State, and Persistence
The script gathers non-test/documentation diffs under `api` and `client`, prints current `go.mod`, and checks whether changed modules have appropriate `replace` entries. Client diffs that only update the API module revision are allowed. It exits nonzero if required replace rules are missing.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on git diff, Go module metadata, and jq. Risks include path filter omissions, noisy go.mod output, and false positives for generated/version-only changes. CI module validation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/module-replace -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/pkg-imports -->
# sources/cloud-native/moby/hack/validate/pkg-imports

## Purpose
Validates that packages under `pkg/` do not import non-public Moby internals.

## Important APIs and Types
Uses `.validate`, `validate_diff`, `go list -e -f '{{ join .Deps "\n" }}'`, and grep filters.

## Control Flow, State, and Persistence
The script lists changed `pkg/*.go` files, computes dependencies for each, filters out allowed `pkg`, `vendor`, and `internal` paths, and fails if remaining dependencies begin with `github.com/moby/moby`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go package loading and changed-file detection. Risks include only checking direct `pkg/*.go` paths rather than recursive package paths if the diff glob is too narrow, and go list behavior with broken packages. CI validation protects package layering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/pkg-imports -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/pr-gh-references -->
# sources/cloud-native/moby/hack/validate/pr-gh-references

## Purpose
Rejects GitHub issue or PR references in commit messages, encouraging commit-hash references instead.

## Important APIs and Types
Uses regexes for shorthand `#123`, repo refs, owner/repo refs, GitHub URLs, and `check_references`.

## Control Flow, State, and Persistence
For each changed non-empty commit, the script scans the commit body for forbidden references. It emits GitHub Actions error lines and exits nonzero if any are found.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `.validate` and git logs. Risks include regex false positives in prose or code snippets, false negatives for unusual URL forms, and blocking historical references during backports. CI validation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/pr-gh-references -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/shfmt -->
# sources/cloud-native/moby/hack/validate/shfmt

## Purpose
Checks shell script formatting.

## Important APIs and Types
Uses `git grep --name-only '^#!'`, exclusion regexes, `xargs shfmt -d`, and flags `-bn -ci -sr`.

## Control Flow, State, and Persistence
The script finds shebang files excluding vendor, Go, Jenkinsfile, Python, and bats files. It runs `shfmt` in diff mode and prints success or a command to reformat.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on git, egrep, xargs, and shfmt. Risks include false positives from non-shell shebang files, missed shell files without shebangs, and xargs behavior with unusual paths. CI validation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/validate/shfmt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/hack/vendor.sh -->
# sources/cloud-native/moby/hack/vendor.sh

## Purpose
Wrapper for tidying, vendoring, and managing local replace rules across Moby modules.

## Important APIs and Types
Defines `tidy`, `vendor`, `replace`, `dropreplace`, and `help`. Module sets are `api`, `client`, root, and `man` for vendoring.

## Control Flow, State, and Persistence
`tidy` runs `go mod tidy` in all modules. `vendor` runs `go mod vendor` in selected modules. `replace` adds root and client replace rules for local `api` and `client`. `dropreplace` resolves a git ref, drops replace rules, requires api/client modules at that ref, tidies, and vendors. The case statement dispatches subcommands, defaulting to tidy plus vendor.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go modules, git remotes, and module layout. It mutates `go.mod`, `go.sum`, and `vendor/`. Risks include missing `$2` under `set -u`-like assumptions if changed, ref resolution surprises, and large vendored diffs. Validation scripts and clean module builds are the signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/hack/vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/benchmark_test.go -->
# sources/cloud-native/moby/integration-cli/benchmark_test.go

## Purpose
Legacy integration benchmarks for daemon/container concurrency and log rotation/follow behavior.

## Important APIs and Types
Defines `DockerBenchmarkSuite`, `BenchmarkConcurrentContainerActions`, and `BenchmarkLogsCLIRotateFollow`.

## Control Flow, State, and Persistence
The suite cleans containers after tests and dumps daemon info on timeout. The concurrent benchmark starts containers, performs parallel daemon actions, and measures end-to-end behavior. The log benchmark creates containers with log rotation settings and follows logs while rotation occurs.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on integration-cli helpers, daemon/client binaries, and a local daemon. It stresses container lifecycle state, log driver persistence, and concurrent API interactions. Risks include benchmark flakiness, timing sensitivity, and environmental daemon load. Benchmark pass and performance trends are the signals rather than unit assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/check_test.go -->
# sources/cloud-native/moby/integration-cli/check_test.go

## Purpose
Legacy integration-cli test harness that registers suites, prepares the test environment, and defines suite-level setup/teardown behavior.

## Important APIs and Types
Defines `TestMain`, `testRun`, suite entry tests for API/CLI/registry/daemon/swarm/plugin/network/hub suites, and suite structs including `DockerSuite`, registry auth suites, `DockerDaemonSuite`, `DockerSwarmSuite`, and `DockerPluginSuite`.

## Control Flow, State, and Persistence
`TestMain` initializes execution environment, prints versions, and runs all suite wrappers. Suite setup starts registries, daemons, swarm nodes, and plugin fixtures as needed. Teardown removes containers, networks, volumes, daemons, registries, and plugin state.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `internal/test/environment`, integration helpers, registry fixtures, daemon helpers, and Docker CLI/API binaries. It is the central integration point for legacy tests. Risks include global mutable `testEnv`, cleanup gaps causing cross-test pollution, and deprecated suite expansion. Its test wrappers provide broad behavioral signals across the daemon.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/check_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/checker/checker.go -->
# sources/cloud-native/moby/integration-cli/checker/checker.go

## Purpose
Compatibility comparison helpers for legacy integration-cli assertions.

## Important APIs and Types
Defines `Compare` and helpers `False`, `True`, `Equals`, `Contains`, `Not`, `DeepEquals`, `HasLen`, `IsNil`, and `GreaterThan`.

## Control Flow, State, and Persistence
Each helper returns a function that adapts a value into a `gotest.tools/assert` comparison. `Not` negates another comparison and preserves diagnostic strings.

## Dependencies, Integration Points, Risks, and Test Signals
Used by older tests that predate direct gotest-tools calls. It stores no state. Risks are weak typing with `any`, diagnostics that may be less precise than direct assertions, and divergence from upstream assertion semantics. Compile and legacy test execution validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/checker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/cli/cli.go -->
# sources/cloud-native/moby/integration-cli/cli/cli.go

## Purpose
Command helper layer for invoking Docker CLI commands in integration tests.

## Important APIs and Types
Defines global `testEnv`, `SetTestEnvironment`, `CmdOperator`, `DockerCmd`, `BuildCmd`, `InspectCmd`, `WaitRun`, `WaitExited`, `Docker`, `Args`, and command modifiers like `Daemon`, `WithTimeout`, `WithEnvironmentVariables`, `WithFlags`, `InDir`, `WithStdout`, and `WithStdin`.

## Control Flow, State, and Persistence
Helpers build `icmd.Cmd` values using the configured Docker binary and daemon host, apply modifiers with undo closures, run commands, and assert exit status where appropriate. Wait helpers poll `docker inspect` output until expected state appears.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `internal/test/environment`, `gotest.tools/icmd`, and daemon helper package. It shells out to Docker and therefore mutates daemon state according to commands. Risks include global environment races, argument validation gaps, command timeouts, and cleanup relying on callers. Nearly every integration-cli file validates this helper path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/cli/cli.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/daemon/daemon.go -->
# sources/cloud-native/moby/integration-cli/daemon/daemon.go

## Purpose
Legacy integration helper wrapper around `internal/test/daemon.Daemon`.

## Important APIs and Types
Defines `Daemon` embedding the newer daemon helper and methods `New`, `Cmd`, `RunCmd`, `Command`, `PrependHostArg`, `GetIDByName`, `InspectField`, `CheckActiveContainerCount`, `WaitRun`, and `WaitInspectWithArgs`.

## Control Flow, State, and Persistence
The wrapper constructs daemon-bound CLI commands, prepends `-H` host arguments, runs inspect filters, checks active container counts, and polls for running/exited states. It delegates daemon lifecycle to the embedded helper.

## Dependencies, Integration Points, Risks, and Test Signals
Used by daemon/swarm/plugin suites to target specific daemon instances. Depends on CLI binary paths, `icmd`, and inspect formatting. Risks include host-arg ordering, polling timeouts, and stale container counts across tests. Swarm and daemon integration tests provide signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/daemon/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/daemon/daemon_swarm.go -->
# sources/cloud-native/moby/integration-cli/daemon/daemon_swarm.go

## Purpose
Swarm-specific polling helpers for legacy integration tests.

## Important APIs and Types
Defines checks for service tasks in states/errors, running tasks, service update state, plugin running/image state, task networks/images, node ready count, local node state, control availability, leader detection, and `CmdRetryOutOfSequence`.

## Control Flow, State, and Persistence
Each method returns a polling closure that runs Docker CLI commands against the daemon, parses JSON/text output, and returns poll success/continue/error. `CmdRetryOutOfSequence` retries commands that fail due to Raft out-of-sequence errors.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on swarm API CLI output, poll helpers, and daemon command wrapper. Risks include fragile output parsing, races during convergence, and masking real errors as retryable. Swarm integration suite tests validate these helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/daemon/daemon_swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/daemon_swarm_hack_test.go -->
# sources/cloud-native/moby/integration-cli/daemon_swarm_hack_test.go

## Purpose
Small compatibility helper for mapping swarm node IDs to daemon helpers in legacy tests.

## Important APIs and Types
Defines `(*DockerSwarmSuite).getDaemon` and `nodeCmd`.

## Control Flow, State, and Persistence
`getDaemon` searches the suite's daemon slice for a daemon whose node ID matches the requested ID and fails the test if absent. `nodeCmd` runs a command against that daemon.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on swarm suite state populated in `check_test.go`. Risks include stale node IDs after daemon restart and test failure diagnostics when nodes are removed. Swarm tests that address nodes by ID validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/daemon_swarm_hack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_attach_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_attach_test.go

## Purpose
Integration tests for container attach over websocket, HTTP hijack, and client API.

## Important APIs and Types
Defines attach tests plus helpers `requestHijack`, `bodyIsWritable`, and `readTimeout`.

## Control Flow, State, and Persistence
Tests create interactive BusyBox containers, attach through `/containers/{id}/attach/ws` or hijacked HTTP POST, write stdin, and assert stdout/stderr multiplexing or TTY behavior. Not-found tests assert 404 responses. Client API tests validate media type, log replay, and stdcopy demultiplexing.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Docker daemon API, raw socket connections, websocket package, stdcopy, and test request helpers. It mutates daemon container state and open streams. Risks include timing-sensitive reads, goroutine/socket leaks, and platform TTY differences. It provides strong signals for attach protocol compatibility and error response behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_build_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_build_test.go

## Purpose
Integration tests for `/build` API behavior around remote contexts, Dockerfile selection, cache invalidation, ONBUILD, copy/add, chown, and scratch builds.

## Important APIs and Types
Contains tests such as `TestBuildAPIDockerFileRemote`, remote tarball/custom Dockerfile tests, git `-f` tests, unnormalized tar path cache tests, ONBUILD cache/copy tests, `TestBuildCopyFromForcePull`, and helper `getImageIDsFromBuild`.

## Control Flow, State, and Persistence
Tests create fake HTTP storage, fake git repositories, tar streams, and registry-backed images, then POST to `/build` with query parameters or tar bodies. They parse build output and inspect images/containers to verify selected Dockerfiles, cache boundaries, remote ADD behavior, ownership, and produced image IDs.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on fakecontext/fakegit/fakestorage, request helpers, registry suite, and Docker build backend. It persists built images and may pull/push through test registries. Risks include legacy builder versus BuildKit differences, network timing, and brittle output parsing. These tests signal build API compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_build_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_build_windows_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_build_windows_test.go

## Purpose
Windows-specific build API regression coverage.

## Important APIs and Types
Defines `TestBuildWithRecycleBin`.

## Control Flow, State, and Persistence
The test exercises a Windows build context scenario involving recycle-bin path handling to ensure build operations do not fail on Windows-specific filesystem artifacts.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Windows daemon/image availability and the build API. Risks are platform path semantics, hidden/system directories, and Windows base image differences. The test is a targeted signal for Windows build context filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_build_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_containers_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_containers_test.go

## Purpose
Large legacy API integration suite for container list, inspect, export, diff, stats, pause/top, commit, create/start/stop/wait/remove, archive copy, resource validation, and mount behavior.

## Important APIs and Types
Defines many `DockerAPISuite` tests, helper `ChannelBuffer`, `UtilCreateNetworkMode`, and `containerExit`.

## Control Flow, State, and Persistence
Tests create containers through client and raw HTTP requests, start/stop/remove them, stream stats, inspect JSON, export tar archives, validate headers and null JSON handling, check resource validation errors, and exercise mount validation and creation for bind, volume, tmpfs, local driver options, propagation, NoCopy, anonymous volume removal, named volume persistence, and custom stop-signal kill behavior.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Docker client API, CLI helpers, daemon platform predicates, filesystem temp dirs, volume service, network/resource validation, and poll helpers. It mutates containers, images, volumes, and host temp mounts. Risks include timing-sensitive stats streams, platform branches, leaked volumes, and brittle expected error text. It is the main signal for daemon container API compatibility, especially mount behavior tied to `daemon/volumes.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_containers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_containers_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_containers_unix_test.go

## Purpose
Unix helper for mount setup inside container API integration tests.

## Important APIs and Types
Defines `mountWrapper(t, device, target, mType, options) error`.

## Control Flow, State, and Persistence
The helper shells out to the platform mount command to create test bind/shared mount setups. It marks the test failed or returns errors through assertions depending on call sites.

## Dependencies, Integration Points, Risks, and Test Signals
Used by mount propagation test cases in `docker_api_containers_test.go`. Depends on Unix mount privileges and host filesystem capabilities. Risks include requiring privileged CI, leaving mounts behind if cleanup elsewhere fails, and platform-specific option support. Successful mount propagation tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_containers_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_containers_windows_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_containers_windows_test.go

## Purpose
Windows-specific container API mount tests and helper stub.

## Important APIs and Types
Defines `TestContainersAPICreateMountsBindNamedPipe` and Windows `mountWrapper`.

## Control Flow, State, and Persistence
The test creates a named pipe bind mount configuration and verifies daemon API handling for Windows named-pipe mounts. The Windows `mountWrapper` is a compatibility helper for shared test code and does not perform Unix mounts.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Windows daemon support for named pipes and client mount API types. Risks include Windows path escaping, named-pipe lifecycle, and divergent mount option validation from Linux. The test signals that Windows mount parsing remains compatible.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_containers_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_exec_resize_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_exec_resize_test.go

## Purpose
Integration tests for exec resize API validation and race handling.

## Important APIs and Types
Defines `TestExecResizeAPIHeightWidthNoInt` and `TestExecResizeImmediatelyAfterExecStart`.

## Control Flow, State, and Persistence
Tests call exec resize endpoints with invalid non-integer height/width and resize immediately after exec start to catch races between exec lifecycle and TTY resize handling.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on exec API, request helpers, and running containers with TTY/exec sessions. Risks include timing sensitivity and platform TTY differences. Signals cover HTTP validation and daemon exec resize concurrency.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_exec_resize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_exec_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_exec_test.go

## Purpose
Integration tests for exec create/start/inspect lifecycle and cleanup.

## Important APIs and Types
Defines tests for missing command, invalid content type, paused containers, start modes, headers, repeated start errors, detach, valid/invalid commands, and exec state cleanup. Helpers include `createExec`, `createExecCmd`, `startExec`, `inspectExec`, `waitForExec`, and `inspectContainer`.

## Control Flow, State, and Persistence
Tests create running containers, create exec instances, start them through raw API/client paths, inspect exec state, wait for completion, and verify cleanup after container removal. They assert response headers, error messages, and container/exec state transitions.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on container lifecycle, exec API, request helpers, and polling. It mutates container exec state in daemon memory/persistence. Risks include races around cleanup and output timing, plus platform command differences. The suite signals exec API compatibility and resource cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_images_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_images_test.go

## Purpose
Small image API integration coverage for search response content type.

## Important APIs and Types
Defines `TestAPIImagesSearchJSONContentType`.

## Control Flow, State, and Persistence
The test calls image search through the API and asserts JSON content type behavior.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on daemon image search endpoint and possibly network/registry availability depending on environment. Risks include external registry instability and content-type header regressions. It is a narrow HTTP contract signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_images_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_inspect_test.go -->
# sources/cloud-native/moby/integration-cli/docker_api_inspect_test.go

## Purpose
Integration tests for inspect API response shape for containers, volumes, images, and older bridge network settings.

## Important APIs and Types
Defines `TestInspectAPIContainerResponse`, `TestInspectAPIContainerVolumeDriver`, `TestInspectAPIImageResponse`, and `TestInspectAPIBridgeNetworkSettings121`.

## Control Flow, State, and Persistence
Tests create containers/images/volumes as needed, call inspect endpoints through the API, decode responses, and verify key fields such as container JSON content, mounted volume driver reporting, image inspect structure, and API-version-specific bridge network fields.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Docker API version negotiation, daemon inspect serializers, volume metadata, and test CLI helpers. Risks include response schema regressions, omitted fields for backward compatibility, and platform-specific inspect output. These tests signal inspect contract stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_api_inspect_test.go -->
