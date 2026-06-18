# Research: subset-b-000093

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/references/registry_reference.go -->
# sources/cloud-native/cri-o/internal/storage/references/registry_reference.go

Purpose: defines `RegistryImageReference`, a strongly typed registry-qualified image reference that must include a tag or digest. The package exists to keep CRI-O storage code from passing arbitrary strings for images crossing CRI or registry boundaries.

Important APIs/types/functions: `RegistryImageReference` wraps a private `reference.Named`; `RegistryImageReferenceFromRaw` is an internal constructor for already-parsed references; `ParseRegistryImageReferenceFromOutOfProcessData` parses external strings with docker normalization and `:latest` defaulting; `StringForOutOfProcessConsumptionOnly`, `Format`, `Registry`, and `Raw` expose controlled views. `ensureInitialized` panics on zero values.

Control flow: external input is parsed with `reference.ParseNormalizedNamed`, normalized with `reference.TagNameOnly`, then sent through `RegistryImageReferenceFromRaw`. The raw constructor strips tags from tag+digest references so digest identity wins, rejects name-only references by panic, and stores the validated reference. Accessors all call `ensureInitialized`.

State and persistence: the type itself is immutable value state around containers/image reference data. It serializes only when callers deliberately use `StringForOutOfProcessConsumptionOnly`, mainly for CRI/status metadata or on-disk runtime metadata.

Dependencies/integration: depends on `go.podman.io/image/v5/docker/reference`. `pkg/config.ImageConfig.ParsePauseImage` validates configured pause images through this type, and `internal/storage/runtime.go` uses `Raw` to build storage transport references and uses the out-of-process string in container metadata.

Risks: invalid raw construction panics instead of returning an error, so only trusted internal code should call it. Zero values also panic, which enforces constructors but can surprise tests or structs with omitted fields. Tag stripping for tag+digest input is intentional but can hide user-supplied tag text after parsing.

Test signals: paired tests cover default docker.io/library/latest normalization, invalid parse errors, raw constructor panics, zero-value panics, `fmt.Formatter` behavior without `fmt.Stringer`, raw reference recovery, and registry extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/references/registry_reference.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/references/registry_reference_test.go -->
# sources/cloud-native/cri-o/internal/storage/references/registry_reference_test.go

Purpose: Ginkgo/Gomega tests for the registry-reference value type and its public parsing/accessor behavior.

Important APIs/types/functions: exercises `ParseRegistryImageReferenceFromOutOfProcessData`, `RegistryImageReferenceFromRaw`, `StringForOutOfProcessConsumptionOnly`, `Raw`, `Registry`, and `fmt.Formatter` conformance.

Control flow: tests parse valid short and fully qualified names, loop invalid inputs, assert panic paths for nil/name-only raw references and uninitialized values, then check formatting and registry-domain results.

State and persistence: no persistent state; the tests only construct in-memory references. They verify canonical strings that downstream metadata/status paths rely on.

Dependencies/integration: imports containers/image `reference` for raw-construction checks and the CRI-O `references` package under test. Uses the shared CRI-O test framework suite from `suite_test.go`.

Risks: tests cover tag-only and registry extraction but not tag+digest stripping; adding a regression test for digest precedence would protect the constructor's ambiguity handling. Panic-based API contracts are tested but still fragile for callers.

Test signals: strong signal that the type intentionally implements `fmt.Formatter` but not `fmt.Stringer`, preserving logging support while discouraging casual string conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/references/registry_reference_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/references/suite_test.go -->
# sources/cloud-native/cri-o/internal/storage/references/suite_test.go

Purpose: test-suite bootstrap for `internal/storage/references`.

Important APIs/types/functions: `TestReferences` registers Gomega's fail handler and runs framework specs named `Storage/references`; `BeforeSuite` creates and sets up a `TestFramework`; `AfterSuite` tears it down.

Control flow: Go test invokes `TestReferences`, Ginkgo runs specs, and suite hooks manage the shared framework lifecycle around all tests in the package.

State and persistence: holds package-level `t *TestFramework`. Any temporary resources are delegated to the framework setup/teardown.

Dependencies/integration: imports `github.com/cri-o/cri-o/test/framework` and Ginkgo/Gomega. This is standard CRI-O test wiring and not production code.

Risks: the package-level variable name `t` shadows common test naming but is a local suite convention. If framework setup grows heavier, even simple reference tests inherit that cost.

Test signals: confirms tests are framework-integrated, so build tags and suite setup must be available for the reference package tests to run.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/references/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/registry_reference.go -->
# sources/cloud-native/cri-o/internal/storage/registry_reference.go

Purpose: re-exports `references.RegistryImageReference` from the parent `internal/storage` package so storage callers can use the concept without importing the dependency-breaking subpackage directly.

Important APIs/types/functions: defines `type RegistryImageReference = references.RegistryImageReference`, an alias rather than a new type.

Control flow: none beyond compile-time aliasing.

State and persistence: no state; all value semantics and persistence behavior are owned by `internal/storage/references`.

Dependencies/integration: imports the references subpackage. Comments explain this split breaks a dependency loop while keeping the type conceptually part of storage, especially alongside `StorageImageID`.

Risks: because this is an alias, method sets and zero-value panic behavior are exactly the subpackage behavior. Any future encapsulation change must preserve mockgen and package-cycle constraints.

Test signals: indirect tests come from storage runtime and references tests; this alias itself has no dedicated test need beyond compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/registry_reference.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/runtime.go -->
# sources/cloud-native/cri-o/internal/storage/runtime.go

Purpose: implements CRI-O's storage-backed runtime service for creating, starting, stopping, deleting, and inspecting pod sandbox/container filesystem records in containers/storage.

Important APIs/types/functions: defines error sentinels for invalid pod/container IDs and names; `ContainerInfo`; `RuntimeServer`; `RuntimeContainerMetadata`; `SetMountLabel`; internal `runtimeContainerMetadataTemplate`; `createContainerOrPodSandbox`; public methods `CreatePodSandbox`, `CreateContainer`, `DeleteContainer`, `SetContainerMetadata`, `GetContainerMetadata`, `StartContainer`, `StopContainer`, `GetWorkDir`, `GetRunDir`, and `GetRuntimeService`.

Control flow: creation validates pod/container names, resolves the image config through containers/image storage transport, builds JSON metadata, calls `CreateContainer`, then adds a layer name and resolves persistent/run directories. A defer deletes partially created containers if later steps fail. `CreatePodSandbox` first resolves the pause image locally and pulls it with optional auth if missing. Start loads metadata and mounts with the stored mount label. Stop unmounts, treating missing containers/layers as already gone in selected paths. Delete removes the storage container and best-effort deletes mapped parent layers.

State and persistence: writes `RuntimeContainerMetadata` JSON into containers/storage container metadata, stores container names and layer names, mutates ID mapping options with mappings assigned by storage, and returns work/run directory paths. `CreatedAt`, `Pod`, `Privileged`, image identity, labels, namespace, UID, and attempt become durable metadata.

Dependencies/integration: depends on containers/image storage transport/types, containers/storage, OCI image-spec `v1.Image`, CRI-O internal logging, `ImageServer`, `StorageTransport`, `StorageImageID`, and `RegistryImageReference`. Upper layers use the `RuntimeServer` interface to manage CRI pod sandboxes and workload containers.

Risks: metadata JSON is a compatibility surface; field/tag changes affect stored containers. Creation cleanup is best effort and may leave partial artifacts if deletion fails. `CreatePodSandbox` uses `context.Background()` for pulls instead of the service context. Error normalization is inconsistent by method: some unknown containers are nil, some become `ErrInvalidContainerID`. `SetContainerMetadata` marshals `&metadata`, a pointer to pointer, which currently works through JSON dereferencing but is easy to misread.

Test signals: `runtime_test.go` covers directory lookup, start/stop/delete errors, metadata read/write, create success/failure cleanup, and pause image pulling with default or provided auth file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/runtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/runtime_test.go -->
# sources/cloud-native/cri-o/internal/storage/runtime_test.go

Purpose: mock-based behavioral tests for `RuntimeServer` methods in `internal/storage/runtime.go`.

Important APIs/types/functions: constructs mocks for containers/storage `Store`, CRI-O `ImageServer`, and `StorageTransport`; tests `GetRunDir`, `GetWorkDir`, `StopContainer`, `StartContainer`, `GetContainerMetadata`, `SetContainerMetadata`, `DeleteContainer`, `CreateContainer`, and `CreatePodSandbox`.

Control flow: each spec establishes expected store/transport call order with gomock and `mockutils.InOrder`, invokes the service, and asserts error/value outcomes. Helper sequences model local-image resolution and pause-image resolution/pull paths.

State and persistence: no real storage is used. Tests assert metadata-dependent behavior through mock JSON strings, `Container` structs, directory return values, and ID mapping/image IDs.

Dependencies/integration: uses Ginkgo/Gomega, gomock, generated mocks under `test/mocks`, CRI-O storage reference and image ID types, containers/storage types, and a shared `testManifest` from suite setup.

Risks: strict ordered mocks can make harmless implementation refactors noisy. The suite has broad error coverage but does not inspect the exact metadata JSON written by creation, mapped-layer cleanup, or all unknown-container idempotency branches.

Test signals: verifies invalid pod/container inputs, cleanup after late creation failures, pause-image pull copy options including `AuthFilePath`, and translation of unknown storage errors to CRI-O sentinel errors in selected methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/runtime_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/suite_test.go -->
# sources/cloud-native/cri-o/internal/storage/suite_test.go

Purpose: test-suite bootstrap and shared fixture setup for `internal/storage` tests.

Important APIs/types/functions: `TestStorage` runs Ginkgo specs named `Storage`; `BeforeSuite` initializes `TestFramework` and a Docker schema v1-ish `testManifest`; `AfterSuite` tears the framework down.

Control flow: Go test enters the suite, framework setup runs once, tests share `testManifest`, and teardown runs after all specs.

State and persistence: package-level `t` and `testManifest` are in-memory test state only.

Dependencies/integration: depends on CRI-O test framework and Ginkgo/Gomega. The manifest fixture is consumed by runtime image-resolution mocks.

Risks: shared fixture shape must remain compatible with containers/image mock helpers. Framework-level setup can hide dependencies from otherwise unit-style tests.

Test signals: confirms the storage tests are suite-based rather than plain `testing` tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/utils.go -->
# sources/cloud-native/cri-o/internal/storage/utils.go

Purpose: provides a small helper to identify containers created by CRI-O based on stored runtime metadata.

Important APIs/types/functions: `IsCrioContainer(md *RuntimeContainerMetadata) bool` returns true when both `PodName` and `PodID` are non-empty.

Control flow: single boolean expression; no nil guard.

State and persistence: reads `RuntimeContainerMetadata` fields produced by `runtime.go`; does not mutate or persist anything.

Dependencies/integration: belongs with the storage metadata model and likely filters containers/storage records to distinguish CRI-O-managed containers from Podman or other users.

Risks: passing nil panics. The heuristic assumes both pod fields are mandatory for all CRI-O-created sandboxes and containers; any migration with missing legacy fields would be classified as non-CRI-O.

Test signals: no direct tests in this subset; storage metadata creation tests indirectly preserve the invariant that CRI-O containers have pod name and ID.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/tools/tools.go -->
# sources/cloud-native/cri-o/internal/tools/tools.go

Purpose: Go tools tracking file for module dependency retention under the `tools` build tag.

Important APIs/types/functions: blank-imports `go.uber.org/mock/mockgen/model` so mockgen-related packages remain in `go.mod`.

Control flow: no runtime control flow; excluded from normal builds by `//go:build tools`.

State and persistence: affects module dependency graph, not runtime state.

Dependencies/integration: supports generated mock workflows used by packages like storage and watchdog tests.

Risks: removing or building without the tag is harmless for production but can cause tooling dependency pruning. Adding runtime imports here would be inappropriate because it is tools-only.

Test signals: compilation with `-tags tools` or dependency maintenance commands are sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/tools/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/linkmode_dynamic.go -->
# sources/cloud-native/cri-o/internal/version/linkmode_dynamic.go

Purpose: supplies the default link mode value for non-static builds.

Important APIs/types/functions: declares `const linkmode = "dynamic"` under build constraint `!static`.

Control flow: compile-time file selection only.

State and persistence: contributes to `version.Info.Linkmode` returned by `Get`; no persistent state.

Dependencies/integration: paired with `linkmode_static.go`; selected by Go build tags and consumed by `version.go`.

Risks: build tags must stay mutually exclusive or `linkmode` will be undefined/duplicated. Incorrect tag use affects version reporting only.

Test signals: version formatting tests use an explicit `Info` value, so build-tag coverage is mostly compile-time.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/linkmode_dynamic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/linkmode_static.go -->
# sources/cloud-native/cri-o/internal/version/linkmode_static.go

Purpose: supplies the link mode value for static builds.

Important APIs/types/functions: declares `const linkmode = "static"` under build constraint `static`.

Control flow: compile-time selection when the `static` build tag is present.

State and persistence: contributes to version info output only.

Dependencies/integration: paired with `linkmode_dynamic.go` and read by `Get` in `version.go`.

Risks: mismatched build tags would make static builds report incorrectly or fail compilation.

Test signals: best verified by compiling with `-tags static` and checking `Get(false).Linkmode`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/linkmode_static.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/suite_test.go -->
# sources/cloud-native/cri-o/internal/version/suite_test.go

Purpose: test-suite bootstrap for the `internal/version` package.

Important APIs/types/functions: `TestVersion`, package-level framework `t`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers Gomega fail handler, runs `Version` framework specs, and brackets them with framework setup/teardown.

State and persistence: only in-memory framework state; version tests themselves create temporary files.

Dependencies/integration: uses CRI-O test framework and Ginkgo/Gomega.

Risks: same suite-level dependency risk as other CRI-O internal tests.

Test signals: required for `version_test.go` specs to execute.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/version.go -->
# sources/cloud-native/cri-o/internal/version/version.go

Purpose: centralizes CRI-O version constants, build metadata reporting, version-file upgrade/wipe decisions, and string/JSON rendering of version information.

Important APIs/types/functions: `Version`, `ReleaseMinorVersions`, build-time vars `buildDate` and `buildCommit`, `Info`, `ShouldCrioWipe`, `WriteVersionFile`, `LogVersion`, `Get`, `Info.String`, and `Info.JSONString`. Internal helpers include `shouldCrioWipe`, `writeVersionFile`, and `parseVersionConstant`.

Control flow: wipe checks read a JSON semver file, parse old and current versions, and request wipe on read/parse errors or major/minor mismatch. Writing parses the current version plus optional git build metadata, marshals semver JSON, creates parent directories, and atomically writes with `renameio`. `Get` reads Go build info, extracts VCS settings/tags/ldflags, falls back to injected commit, optionally lists dependencies, and fills runtime/platform/security fields. `String` reflects over `Info` fields and tab-aligns non-empty values; `JSONString` marshals indented JSON.

State and persistence: version files are durable semver JSON used to detect reboot/upgrade wipe behavior. Build metadata comes from Go build info or ldflags. `Get` observes runtime security capability state through seccomp/AppArmor probes.

Dependencies/integration: uses `blang/semver`, `runtime/debug`, `renameio`, `logrus`, goccy JSON, and common seccomp/apparmor helpers. Startup and CLI version paths consume `Info`.

Risks: malformed or unreadable version files intentionally trigger wipe. Only major/minor differences matter; patch upgrades do not. Build info may be unavailable, causing `Get` errors. Reflection-based formatting depends on field order and supported kinds. The fallback `buildCommit` dirty suffix parsing assumes a `-dirty` convention.

Test signals: tests cover semver parsing, git build metadata trimming, version-file writing, wipe decisions for empty/bad/same/patch/minor/major versions, and exact string/JSON output.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/version_test.go -->
# sources/cloud-native/cri-o/internal/version/version_test.go

Purpose: validates version parsing, version-file persistence, wipe decision semantics, and `Info` rendering.

Important APIs/types/functions: tests internal helpers `parseVersionConstant`, `writeVersionFile`, `shouldCrioWipe`, plus `Info.String` and `Info.JSONString`.

Control flow: specs create temp files, write semver JSON or malformed data, call helpers with controlled old/new versions, and compare exact expected strings/JSON.

State and persistence: writes temporary version files and removes them in selected specs. Ensures persisted semver JSON matches `semver.MarshalJSON`.

Dependencies/integration: Ginkgo/Gomega, `os`, `strings`, and package internals in the same package.

Risks: exact string comparison is sensitive to field order and tabwriter spacing. Some specs shadow `tempFileName` and use relative temp filenames, so framework cwd assumptions matter.

Test signals: strong coverage for wipe policy: missing/malformed files request wipe with error, patch-only changes do not, major/minor changes do, and bad current constants are treated as wipe-worthy errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/version/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/suite_test.go -->
# sources/cloud-native/cri-o/internal/watchdog/suite_test.go

Purpose: Ginkgo suite bootstrap for systemd watchdog tests.

Important APIs/types/functions: `TestWatchdog`, package-level framework `t`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs specs named `Watchdog`, and manages shared framework setup/teardown.

State and persistence: no durable state; framework state only.

Dependencies/integration: CRI-O test framework plus Ginkgo/Gomega.

Risks: tests rely on build tag support for the injection file to set mock systemd.

Test signals: enables the mock-based watchdog test file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/systemd.go -->
# sources/cloud-native/cri-o/internal/watchdog/systemd.go

Purpose: wraps go-systemd daemon notification functions behind a small interface for production use and tests.

Important APIs/types/functions: `Systemd` interface with `WatchdogEnabled` and `Notify`; `defaultSystemd`; `DefaultSystemd`; methods delegating to `daemon.SdWatchdogEnabled(false)` and `daemon.SdNotify(false, state)`.

Control flow: direct delegation to systemd helper calls; no retries here.

State and persistence: stateless wrapper. Systemd notification state is external through environment and the notify socket.

Dependencies/integration: consumed by `Watchdog` in `watchdog.go`; test injection swaps it for a gomock implementation.

Risks: passing `false` means the helper checks the current process rather than unset-env behavior. If `NOTIFY_SOCKET` is absent, `Notify` returns unsupported and `Watchdog.Start` handles it.

Test signals: watchdog tests mock this interface rather than invoking real systemd.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/systemd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/watchdog.go -->
# sources/cloud-native/cri-o/internal/watchdog/watchdog.go

Purpose: implements CRI-O's systemd watchdog notification loop with pluggable health checks.

Important APIs/types/functions: `Watchdog` struct, `HealthCheckFn`, `New`, `Start`, `Notifications`, and `runHealthCheckers`. `minInterval` requires a watchdog timeout greater than one second.

Control flow: `Start` asks systemd for the watchdog timeout, returns nil when disabled, rejects too-small intervals, halves the interval, and starts a goroutine with `wait.Until`. Each tick runs health checkers sequentially; on success it uses two-step exponential backoff to call `Notify(SdNotifyWatchdog)`. Notify errors are retried; unsupported notification returns a terminal backoff error for that tick. Notifications are counted for every notify attempt.

State and persistence: stores health checkers, backoff config, injected `Systemd`, and an atomic notification-attempt counter. No durable state.

Dependencies/integration: uses `github.com/coreos/go-systemd/v22/daemon`, Kubernetes `wait`, CRI-O internal logging, and `Systemd` abstraction. Higher-level server startup can instantiate this with health probes.

Risks: health checkers run serially and one failure suppresses later checks and notification. The goroutine is asynchronous; `Start` returning nil does not mean a notification succeeded. `Notifications` counts failed attempts too. Too-small systemd intervals fail startup for watchdog setup.

Test signals: tests cover success, retry, unsupported notify, unhealthy checker suppression, disabled watchdog, `WatchdogEnabled` error, and too-low interval.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/watchdog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/watchdog_test.go -->
# sources/cloud-native/cri-o/internal/watchdog/watchdog_test.go

Purpose: validates watchdog control flow with a mocked systemd backend and in-memory health checkers.

Important APIs/types/functions: uses `watchdog.New`, test-only `SetSystemd`, `Start`, and `Notifications`; defines `waitForNotifications` polling helper.

Control flow: each spec sets gomock expectations for `WatchdogEnabled`/`Notify`, starts the watchdog, waits until notification attempts or health-check flags indicate the goroutine ran, and asserts errors/side effects.

State and persistence: only in-memory booleans and atomic notification counts. No real systemd socket or durable state is used.

Dependencies/integration: requires the `test` build-tag injection file and generated `systemd` mock.

Risks: asynchronous polling can hang if expected notifications never arrive; gomock expectations and Ginkgo timeouts bound this indirectly. The "does not acknowledge" test proves no startup error, but the actual failure is logged asynchronously.

Test signals: confirms health-check short-circuiting, retry count behavior, disabled watchdog no-op, and invalid interval rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/watchdog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/watchdog_test_inject.go -->
# sources/cloud-native/cri-o/internal/watchdog/watchdog_test_inject.go

Purpose: test-only injection hook for replacing the watchdog's systemd implementation.

Important APIs/types/functions: `SetSystemd(systemd Systemd)` mutates `w.systemd`.

Control flow: no branching; direct field assignment.

State and persistence: mutates in-memory `Watchdog` state for tests only.

Dependencies/integration: guarded by `//go:build test`, used by `watchdog_test.go` to inject gomock `Systemd`.

Risks: must only be available in test builds; exposing it in production would allow uncontrolled replacement of the notification backend.

Test signals: package tests depend on this method to avoid real systemd calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/watchdog/watchdog_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/Makefile -->
# sources/cloud-native/cri-o/pinns/Makefile

Purpose: builds the `pinns` helper binary from C sources and installs it under `../bin/pinns`.

Important APIs/types/functions: derives `src` and `obj` from `src/*.c`, sets `STRIP`, `LIBS`, and default `CFLAGS`, defines `all`, binary link, object compile, `../bin` creation, and `clean` targets.

Control flow: object files compile from C sources, the binary target links them with configured flags, strips symbols, and creates `../bin` as needed.

State and persistence: produces `.o` files beside sources and `../bin/pinns`; `clean` removes those artifacts.

Dependencies/integration: requires a C compiler and `strip`. CRI-O runtime config validates `pinns` on Linux and namespace management uses the resulting executable.

Risks: default `CFLAGS` include `-static`, `-Werror`, and `-O3`, so portability depends on static libc/toolchain support and warning cleanliness. `HEADERS` is referenced but not defined, so header dependencies may not trigger rebuilds unless supplied by the caller.

Test signals: build success of `../bin/pinns` is the primary signal; there are no unit tests in this subset for the C helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/pinns.c -->
# sources/cloud-native/cri-o/pinns/src/pinns.c

Purpose: command-line helper that creates/unshares selected Linux namespaces, optionally configures user mappings and sysctls, and bind-mounts namespace handles into a pin directory for CRI-O namespace lifecycle management.

Important APIs/types/functions: `main`; option parsing for `--uts`, `--ipc`, `--net`, `--user`, `--cgroup`, `--mnt`, `--dir`, `--filename`, `--uid-mapping`, `--gid-mapping`, and `--sysctl`; helpers `is_host_ns`, `setup_unbindable_bindpath`, `create_bind_root`, `bind_ns`, `directory_exists_or_create`, and `write_mapping_file`.

Control flow: parses requested namespaces and paths, validates mappings, creates the pin directory, then either unshares in-process or forks when user/mount namespaces require a child. User namespace creation synchronizes parent/child over a `SOCK_SEQPACKET` socketpair so parent can write uid/gid maps before the child unshares remaining namespaces and pauses. The parent then bind-mounts `/proc/<pid>/ns/<name>` or `/proc/self/ns/<name>` into `$dir/${ns}ns/$filename`, makes mount namespace bind roots unbindable, kills/waits child when done, and exits.

State and persistence: creates namespace pin directories/files, bind mounts namespace descriptors, writes `/proc/<pid>/uid_map` and `gid_map`, applies sysctls inside newly created namespaces, and may create a temporary child process. Pinned namespace mounts persist after the helper exits until unmounted by CRI-O cleanup.

Dependencies/integration: uses Linux namespace syscalls, mount APIs, procfs namespace files, `sysctl.c`, and `utils.h`. `pkg/config/config_linux.go` validates the executable path; CRI-O namespace manager invokes it.

Risks: privileged syscall-heavy code with many host side effects. `sysctls` allocation is based on `argc/2`, which matches expected option/value pairs but is not independently bounds-checked. `open(..., O_CREAT|O_EXCL, 0)` creates mode-000 pin files before bind mounting. `write_mapping_file` writes a NUL byte because it uses `it - content + 1`; proc mapping files may reject unexpected bytes depending on kernel behavior. Path concatenation relies on `PATH_MAX` truncation discipline rather than rejecting overlong inputs.

Test signals: no direct tests in this subset; validation is mainly compile/build plus integration tests that create and clean pinned namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/pinns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/sysctl.c -->
# sources/cloud-native/cri-o/pinns/src/sysctl.c

Purpose: applies sysctl key/value settings inside the current namespace context for `pinns`.

Important APIs/types/functions: `configure_sysctls`, internal `separate_sysctl_key_value`, and `write_sysctl_to_file`.

Control flow: `configure_sysctls` iterates configured strings, splits each `key=value` in place, validates non-empty key/value, rewrites dots in keys to slashes, opens `/proc/sys` with `O_DIRECTORY|O_PATH`, opens the specific sysctl with `openat`, and writes the value with EINTR retry.

State and persistence: mutates kernel sysctl state in `/proc/sys` for the namespace where `pinns` runs after unshare. It also mutates the input argument strings by replacing `=` and `.` with NUL and `/`.

Dependencies/integration: called from `pinns.c` after namespace creation; uses cleanup macros and logging helpers from `utils.h`.

Risks: in-place mutation means the original sysctl string cannot be reused after configuration. There is no allowlist; caller must ensure only intended sysctls are passed. Write success does not verify full byte count beyond negative return, so short positive writes are not detected. Path traversal through sysctl keys is mitigated only by opening under `/proc/sys`; slash-containing input can still address nested sysctls.

Test signals: no direct tests; integration should cover malformed key/value, namespace-specific sysctls, permission errors, and absent procfs entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/sysctl.h -->
# sources/cloud-native/cri-o/pinns/src/sysctl.h

Purpose: declares the sysctl configuration entry point for the `pinns` C helper.

Important APIs/types/functions: `int configure_sysctls(char ** const sysctls, int size);`

Control flow: none; header guard only.

State and persistence: none directly; implementation writes `/proc/sys`.

Dependencies/integration: included by `pinns.c` and implemented in `sysctl.c`.

Risks: API documents no ownership/mutation semantics, although implementation mutates strings in place.

Test signals: compile-time linkage between `pinns.c` and `sysctl.c`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/utils.h -->
# sources/cloud-native/cri-o/pinns/src/utils.h

Purpose: shared C utility macros for `pinns`, covering EINTR retry, cleanup attributes, branch prediction, fd/file cleanup, and standardized warning/error output.

Important APIs/types/functions: `TEMP_FAILURE_RETRY`, `pexit`, `_pexit`, `pexitf`, `pwarn`, `pwarnf`, `nexit`, `nexitf`, `nwarn`, `nwarnf`, `_cleanup_`, `freep`, `closep`, `fclosep`, `_cleanup_free_`, `_cleanup_close_`, `_cleanup_fclose_`, `LIKELY`, and `UNLIKELY`.

Control flow: error macros print to stderr and either `exit` or `_exit`; cleanup functions are invoked by GCC/Clang cleanup attributes when variables go out of scope.

State and persistence: affects process exit behavior and closes/frees resources; no durable state.

Dependencies/integration: included by `pinns.c` and `sysctl.c`. Requires GNU-compatible compiler support for statement expressions and cleanup attributes.

Risks: macros with trailing semicolons on `nwarn`/`nwarnf` can be awkward in `if/else` contexts. Error macros exit immediately, so callers cannot recover. GNU extensions reduce portability outside the intended Linux toolchain.

Test signals: warning-free compile under the `pinns` Makefile's `-Werror -Wextra` settings is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pinns/src/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/annotations/annotations.go -->
# sources/cloud-native/cri-o/pkg/annotations/annotations.go

Purpose: backwards-compatible annotation facade that re-exports deprecated v1 constants and the v2 lookup helper from `pkg/annotations/v2`.

Important APIs/types/functions: `GetAnnotationValue`; deprecated constants such as `UsernsModeAnnotation`, `UnifiedCgroupAnnotation`, `SeccompProfileAnnotation`, `DisableFIPSAnnotation`, and many CPU/runtime annotations; `AllAllowedAnnotations`.

Control flow: `GetAnnotationValue` delegates directly to `v2.GetAnnotationValue`. Constants are compile-time aliases to v2 package constants.

State and persistence: no runtime state. The constants define allowed pod/container/image annotation keys that can appear in Kubernetes metadata and runtime config allowlists.

Dependencies/integration: imports `pkg/annotations/v2`. Existing callers can keep importing `pkg/annotations` while new code moves to v2 names.

Risks: deprecated names remain a compatibility surface. Because this package re-exports v1 constants from v2, any v2 mapping error propagates to legacy users. New v2 annotations not re-exported here may be invisible to old importers.

Test signals: annotations tests check fallback lookup and allowed-list inclusion for v1 and v2 keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/annotations/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/annotations/annotations_test.go -->
# sources/cloud-native/cri-o/pkg/annotations/annotations_test.go

Purpose: plain Go tests for annotation migration lookup and allowed annotation inventory.

Important APIs/types/functions: tests `v2.GetAnnotationValue`, deprecated v1 constants, v2 constants, and package-level `AllAllowedAnnotations`.

Control flow: table-driven tests verify v2 precedence, v1 fallback, missing keys, slash and dot container-specific suffix fallback, and specific annotations like DisableFIPS and LinkLogs. Additional tests iterate expected v2-to-v1 mappings and ensure allowed-list presence.

State and persistence: in-memory annotation maps only.

Dependencies/integration: imports `testing` and `pkg/annotations/v2`. The tests live in package `annotations`, so they also validate the legacy facade's `AllAllowedAnnotations` variable.

Risks: expected reverse mapping list is duplicated in tests and can drift when new migrated annotations are added. Tests call `v2.GetAnnotationValue` directly in the main table rather than the wrapper, so wrapper delegation has only indirect coverage.

Test signals: good migration coverage for base and container-specific keys, plus allowed-list regression detection for migrated annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/annotations/annotations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/annotations/v2/annotations.go -->
# sources/cloud-native/cri-o/pkg/annotations/v2/annotations.go

Purpose: authoritative v2 annotation key registry and migration lookup logic for CRI-O annotations.

Important APIs/types/functions: v2 constants for cgroups, devices, FIPS, logs, platform runtime, seccomp, shm, spoofing, SELinux relabel skip, umask, userns, CPU tuning, IRQ, OCI seccomp hook, and stop signal; deprecated v1 constants; `SeccompNotifierActionStop`; `reverseAnnotationMigrationMap`; `GetAnnotationValue`; `GetAnnotationValueWithKey`; `findV1KeyForContainerSpecific`; `AllAnnotations`; `AllV1Annotations`; `AllAllowedAnnotations`.

Control flow: lookup first checks the requested v2 key, then exact v2-to-v1 fallback, then detects container-specific slash or dot suffixes by matching known v2 bases and appending the suffix to the v1 base. Allowed annotations are built by appending external/runtime prefixes, all v2 annotations, and all v1 annotations.

State and persistence: constants are metadata contract keys used in pod annotations, image annotations, and runtime-handler `allowed_annotations`. No mutable runtime state except package-level slices/maps.

Dependencies/integration: imported by config runtime validation to validate allowed annotations and by callers extracting annotation values. Runtime config comments document these v2 names as recommended while supporting v1 fallback.

Risks: `reverseAnnotationMigrationMap` omits v2 annotations without v1 equivalents; fallback is intentionally unavailable for those. Container-specific matching iterates over a map, but because it returns only after exact prefix+separator matches, ambiguous bases would be risky if introduced. `AllAllowedAnnotations` includes prefix-like strings such as `org.systemd.property.`; consumers must know whether they treat entries as exact keys or prefixes.

Test signals: package-level tests verify v2 precedence, exact fallback, slash/dot container suffix fallback, and inclusion of migrated v1/v2 annotations in the allowed list.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/annotations/v2/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config.go -->
# sources/cloud-native/cri-o/pkg/config/config.go

Purpose: defines CRI-O's full TOML-backed configuration model, default construction, config-file/drop-in loading, serialization, validation, runtime-handler feature setup, and accessors for derived subsystem configs.

Important APIs/types/functions: major structs include `Config`, `RootConfig`, `RuntimeConfig`, `RuntimeHandler`, `ImageConfig`, `NetworkConfig`, `APIConfig`, `MetricsConfig`, `TracingConfig`, `StatsConfig`, and `tomlConfig`. Key functions/methods include `DefaultConfig`, `DefaultRuntimeConfig`, `UpdateFromFile`, `UpdateFromDropInFile`, `UpdateFromPath`, `ToBytes/ToString/ToFile`, `Validate` on each config section, `RemoveUnusedSocket`, `ValidateDefaultRuntime`, `ValidateRuntimes`, `initializeRuntimeFeatures`, monitor-field translation, runtime-handler validation helpers, `ParsePauseImage`, CNI accessors, stats metrics validation, and TLS parsed-value accessors.

Control flow: defaults combine containers/storage defaults, platform constants, user agent, cgroup manager detection, and subsystem default constructors. Config loading decodes TOML through `tomlConfig`, merging drop-ins over existing values and preserving storage defaults when files omit them; duplicate storage options keep the last occurrence. Top-level validation checks image volume type, optional node execution validation, then root/runtime/image/network/API/NRI/stats validation. Runtime execution validation configures cgroup manager, validates runtimes, probes registries, normalizes hooks dirs, configures CDI, validates `pinns`, initializes namespace manager, checks CRIU, loads seccomp/AppArmor/blockio/RDT configs, and translates deprecated conmon fields into runtime handlers. Runtime feature initialization calls runtime `--version` and `features`, parses OCI feature JSON, and gates recursive read-only support through kernel checks.

State and persistence: config can be loaded from a primary file plus drop-in directory and serialized back to TOML. Validation mutates derived state: parsed TLS values, storage roots/options, cgroup/conmon/namespace/CNI managers, seccomp/AppArmor/blockio/RDT/ulimit/device configs, runtime handler paths, disallowed annotation lists, defaulted timeouts, CNI plugin dirs, and enabled metrics. On execution it creates directories, removes stale sockets, and may initialize external managers.

Dependencies/integration: integrates with BurntSushi TOML, containers/storage, containers/image system context and registries config, CRI-O internal config subsystems, CNI, CDI, conmon-rs, Kubernetes TLS parsing/cpuset, runtime-spec features, annotations v2, user agent, and command runner. It is a central dependency for CRI-O server startup and reload.

Risks: validation has side effects, so callers must distinguish dry validation from execution validation. Drop-in walking uses filesystem order from `filepath.Walk`, which is lexical for most implementations but still worth treating as config-order sensitive. Runtime feature probing executes configured runtime binaries. Missing optional runtime handlers are dropped, but invalid default runtime is fatal. Annotation allowlists depend on exact `AllAllowedAnnotations` contents. TLS parsed state resets on validation; users of getters before validation see zero values. Some platform constants and methods are build-tag dependent.

Test signals: this subset does not include config tests, but the code has many validation branches that should be covered elsewhere: default generation, TOML round trips, drop-in merge precedence, TLS validation, socket removal, runtime handler inheritance/validation, allowed annotations, seccomp fallback, CNI init, stats metric validation, pause-image parsing, and platform-specific `pinns`/RRO behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_freebsd.go -->
# sources/cloud-native/cri-o/pkg/config/config_freebsd.go

Purpose: FreeBSD-specific CRI-O config defaults and platform stubs.

Important APIs/types/functions: constants for CNI paths, socket/config/version/clean-shutdown paths, default runtime `ocijail`, runtime root/type, monitor cgroup, `ImageVolumesBind = "nullfs"`, and FreeBSD pause image. Functions `selinuxEnabled`, `checkKernelRROMountSupport`, and `RuntimeConfig.ValidatePinnsPath`.

Control flow: SELinux always returns false; RRO support returns not implemented; `ValidatePinnsPath` is a no-op.

State and persistence: supplies path defaults used by `DefaultConfig` and runtime validation on FreeBSD. No mutable state.

Dependencies/integration: imports CRI-O `errdefs` for not-implemented RRO. Complements `config_linux.go` under build selection.

Risks: feature support intentionally differs from Linux: no SELinux, no pinns validation, no RRO support. FreeBSD-specific pause image and paths must be maintained separately from Linux defaults.

Test signals: compile/test on FreeBSD should confirm defaults and no-op validation; Linux-only RRO/pinns tests should not assume these functions behave the same.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_linux.go -->
# sources/cloud-native/cri-o/pkg/config/config_linux.go

Purpose: Linux-specific CRI-O config defaults and validation helpers for SELinux, `pinns`, and recursive read-only mount kernel support.

Important APIs/types/functions: constants for default runtime `crun`, runtime type/root, default monitor cgroup `system.slice`, bind image volume type, and pause image. Functions `selinuxEnabled`, `RuntimeConfig.ValidatePinnsPath`, `checkKernelRROMountSupport`, `validateKernelRROVersion`, and `validateKernelRROMount`; package vars cache RRO support through `sync.Once`.

Control flow: SELinux queries the host library. `ValidatePinnsPath` resolves or stats the executable via shared `validateExecutablePath`. RRO support first checks kernel version >= 5.12; if too old, it performs a live tmpfs mount and `unix.MountSetattr(... AT_RECURSIVE, MOUNT_ATTR_RDONLY)` probe to detect backported support, caching the result.

State and persistence: RRO validation creates a temporary directory, mounts tmpfs, unmounts it, and removes the directory; result is cached in package globals. `ValidatePinnsPath` mutates `RuntimeConfig.PinnsPath`.

Dependencies/integration: used by `config.go` runtime validation and runtime feature gating. Depends on opencontainers SELinux, containers/storage kernel parser, `x/sys/unix`, and logrus.

Risks: the live mount probe requires privileges/capabilities and can fail for environmental reasons unrelated to kernel capability. `sync.Once` means the first result persists for process lifetime, even if test environment or privileges change. Cleanup logs but cannot recover failed unmount/removal. `pinns` validation is execution-path dependent.

Test signals: best covered with unit tests for version comparison using fakes and integration tests for mount probing under privileged Linux; normal unprivileged tests may need to avoid the live probe.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_linux.go -->
