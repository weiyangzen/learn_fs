# subset-b-000094 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_test.go -->
# sources/cloud-native/cri-o/pkg/config/config_test.go

This Ginkgo/Gomega test file is the broad behavioral safety net for CRI-O's `pkg/config` package. It validates the default config, runtime-dependent validation paths, TOML update behavior, runtime handler validation, image/network/root config checks, TLS settings, stats metric selection, and serialization helpers. The file is test-only but it documents the contract expected from `Config.Validate`, the embedded `APIConfig`, `RuntimeConfig`, `ImageConfig`, `NetworkConfig`, `RootConfig`, `UpdateFromFile`, `UpdateFromPath`, `ParsePauseImage`, runtime feature loading, and runtime handler timeout validation.

Important helpers include `runtimeValidConfig`, which mutates the shared `sut` into a runtime-valid fixture by adding a runtime handler, CNI dirs, conmon, socket, log, and namespace paths, and `isRootless`, which skips runtime tests that require root privileges. The control flow is organized as nested `t.Describe` sections around config subsystems. Most tests mutate one field, call the subsystem validator or update function, and assert either success or the precise high-level failure class. State is held in package-level `sut` from `suite_test.go`; each test resets through `BeforeEach(beforeEach)`. Temporary files and directories are used to model config files, sockets, storage inheritance, and runtime binaries.

Dependencies include CRI-O's config package, annotation constants, cgroup manager helpers, storage defaults from `go.podman.io/storage`, `cmdrunner` global taskset state, `crypto/tls`, and the framework's temp helpers. Integration signals are strong: tests cover the compatibility boundary with storage.conf defaults, conmon lookup, taskset injection for infra CPU sets, runtime type policy (`oci`, `vm`, `pod`), allowed annotation generation, websocket streaming support based on conmon-rs behavior, VM runtime config path validation, OCI runtime features JSON parsing, and Kubernetes-facing TLS/cipher options. Risks include environment sensitivity (`conmon`, `taskset`, root privileges, storage backends), mutation of shared global command runner state, and broad string replacement assumptions in fixtures. The test coverage is extensive for validation and parsing, but less focused on concurrent config mutation or full daemon startup integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_test_inject.go -->
# sources/cloud-native/cri-o/pkg/config/config_test_inject.go

This file is guarded by `//go:build test` and exposes internal config mutation hooks for tests. Its purpose is to let tests inject mocked networking, namespace, checkpoint/restore, and cgroup-manager state without exporting those knobs in production builds.

The public test APIs are `(*Config).SetCNIPlugin`, `(*Config).SetNamespaceManager`, `(*RuntimeConfig).SetCheckpointRestore`, and `(*RuntimeConfig).SetCgroupManager`. `SetCNIPlugin` lazily initializes `c.cniManager` with `cnimgr.CNIManager` before delegating to `SetCNIPlugin`, which means it preserves the manager's shutdown semantics. `SetNamespaceManager` directly replaces the unexported `namespaceManager`. `SetCheckpointRestore` toggles `EnableCriuSupport`, and `SetCgroupManager` injects a `cgmgr.CgroupManager`.

There is no persistence beyond in-memory config fields. Dependencies are CRI-O internal managers plus `ocicni.CNIPlugin`. Integration points are test suites that need to emulate server config state and runtime dependency injection, especially checkpoint tests. The main risk is that test-only access can drift from production initialization behavior, but the build tag prevents accidental production exposure. Test signal is indirect: files such as server checkpoint tests rely on `SetCheckpointRestore` to exercise enabled and disabled paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_unix.go -->
# sources/cloud-native/cri-o/pkg/config/config_unix.go

This platform-specific source provides default CRI-O paths for non-Windows, non-FreeBSD builds. It is configuration data, not executable control flow. The constants define CNI config and binary directories, conmon exit and attach socket directories, the primary config file and drop-in directory, the CRI-O socket path, the temporary version file, and the clean shutdown marker.

These constants feed `DefaultConfig` and related default config initialization in the broader package. State/persistence implications are significant because the paths point at daemon state on disk: `/var/run/crio` for sockets, exit files, and temporary version state, `/var/lib/crio/clean.shutdown` for durable shutdown state, and `/etc/crio` for operator-managed config. Dependencies are limited to build tags and the package namespace.

Risks are path compatibility and distro packaging assumptions. Any change here affects default daemon startup, config discovery, wipe behavior, and kubelet socket integration on Linux-like systems. Tests in this subset validate behavior built on these defaults through `DefaultConfig`, validation, template generation, and reload tests rather than this file directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_unsupported.go -->
# sources/cloud-native/cri-o/pkg/config/config_unsupported.go

This build-tagged file supports platforms that are not Linux, FreeBSD, or Windows. It provides placeholder constants and minimal stubs so the package can compile on unsupported targets, while intentionally making runtime defaults invalid.

Important symbols are invalid-valued defaults for runtime name/type/root, monitor cgroup, and `ImageVolumesBind`, plus `DefaultPauseImage`. It also defines `selinuxEnabled` as false, `checkKernelRROMountSupport` as `errdefs.ErrNotImplemented`, and `(*RuntimeConfig).ValidatePinnsPath` as a no-op. There is no state persistence; the behavior is compile-time platform selection.

Dependencies are only `utils/errdefs`. Integration is with generic config code that expects these functions and constants to exist on every platform. The risk is deliberate: tests and real runtime behavior are not expected to pass because defaults are placeholders. This file should be treated as portability scaffolding, not as a supported runtime implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_windows.go -->
# sources/cloud-native/cri-o/pkg/config/config_windows.go

This Windows-specific file defines CRI-O default paths for CNI, runtime exits, attach sockets, config files, and sockets using Windows path syntax, and stubs recursive read-only mount support as not implemented.

The important exported/default constants include `ContainerAttachSocketDir`, `CrioConfigPath`, `CrioConfigDropInPath`, and `CrioSocketPath`. The control flow is minimal: `checkKernelRROMountSupport` returns `errdefs.ErrNotImplemented`. Persistence behavior is path-based, mapping CRI-O config and runtime files under `C:\crio\...`.

Dependencies are limited to `utils/errdefs`. Integration is with `DefaultConfig` and validation on Windows builds. A notable risk is that this file declares `CrioConfigPath` twice in the same const block, once for `C:\crio\etc\crio.conf` and once where the comment describes a version file. That would be a compile-time redeclaration problem if this Windows file is built, and it likely intended a distinct version-path constant. Tests in this subset do not exercise Windows builds, so this risk is not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/reload.go -->
# sources/cloud-native/cri-o/pkg/config/reload.go

This file implements CRI-O's partial live configuration reload. `(*Config).Reload` reconstructs a new default config, overlays the single config file and drop-in directory when present, then selectively applies hot-reloadable settings to the running config. It intentionally avoids wholesale replacement of daemon config.

Important APIs are `Reload`, `ReloadLogLevel`, `ReloadLogFilter`, `ReloadPauseImage`, `ReloadPinnedImages`, `ReloadRegistries`, `ReloadDecryptionKeyConfig`, `ReloadSeccompProfile`, `ReloadAppArmorProfile`, `ReloadBlockIOConfig`, `ReloadRdtConfig`, and `ReloadRuntimes`. `Reload` applies them in a fixed order and finally reconfigures CDI spec dirs. State mutations occur on the live `Config`: logrus level and hooks, pause image/auth/command, pinned images, decryption key path, seccomp/AppArmor/blockio/RDT loaded profiles, runtime map/default runtime, and CDI configuration. Persistent reads are from `singleConfigPath`, `dropInConfigDir`, auth files, seccomp paths, blockio/RDT config files, registries config, and runtime paths.

Dependencies include `logrus`, CRI-O internal log filtering, `containers/image` registry cache updates, CDI, `go-cmp` for sorted pinned image comparison, and config validation helpers. Integration points are SIGHUP-driven daemon reload, image pull behavior, OCI runtime selection, security profile loading, registry configuration, and device plugin discovery. Risks include partial mutation before a later reload step fails, reliance on external filesystem validity, and deliberately permissive seccomp fallback when a configured profile path does not exist. Tests in `reload_test.go` cover invalid log/filter/pause auth failures, seccomp fallback, registry errors, runtime replacement/inheritance/default validation, and pinned image replacement.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/reload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/reload_test.go -->
# sources/cloud-native/cri-o/pkg/config/reload_test.go

This file verifies the live reload contract defined in `reload.go`. It uses Ginkgo/Gomega and the shared config fixture to mutate serialized config files and individual `Config` objects, then checks whether hot-reload APIs update state or reject invalid input.

The main helper, `modifyDefaultConfig`, writes `sut` to a temp file, loads it back so `singleConfigPath` is set, replaces a config string, and then lets `sut.Reload` read the modified file. Test sections cover full `Reload`, log level, log filter, pause image/auth/command, registries, seccomp, AppArmor, runtimes, and pinned images. State changes are in-memory on `sut`, with persistent temp files used for config and seccomp profile simulation. AppArmor tests skip when AppArmor is disabled, and runtime tests use `EnsureRuntimeDeps`.

Dependencies include `go.podman.io/common/pkg/apparmor`, CRI-O config package, temporary filesystem helpers, and registry parsing. Integration signals include a no-change reload path, validation of invalid dynamic settings, fallback to the internal seccomp profile when configured path is missing, runtime inheritance during reload, and registry cache failure propagation. Risks are test fragility from string replacement in generated config output and environment-sensitive AppArmor/runtime availability. The file provides focused coverage for reloadable fields but does not prove atomicity if a late reload operation fails after earlier fields were already changed.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/reload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/suite_test.go -->
# sources/cloud-native/cri-o/pkg/config/suite_test.go

This is the Ginkgo suite bootstrap for `pkg/config` tests. `TestLibConfig` registers the fail handler and starts framework-backed specs under the `LibConfig` suite name. Package-level fixtures include the framework handle `t`, the shared system under test `sut`, and a reusable valid directory path.

The suite establishes constants `validFilePath` and `invalidPath`, provides `validConmonPath` for environment-dependent conmon lookup, initializes the test framework in `BeforeSuite`, tears it down in `AfterSuite`, and resets `sut` before individual tests through `beforeEach`. `defaultConfig` wraps `config.DefaultConfig`, asserts it succeeded, and calls `t.EnsureRuntimeDeps`.

State is test-global and intentionally reset between specs. Dependencies are Ginkgo/Gomega, CRI-O's test framework, and `os/exec` for `conmon` discovery. Integration risk is environment dependence: missing conmon causes selected tests to skip, while runtime dependency setup may mutate PATH or temp fixtures. The suite itself is not business logic, but it is the foundation for all test signals in this config subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/sysctl.go -->
# sources/cloud-native/cri-o/pkg/config/sysctl.go

This file parses and validates default sysctl settings from `RuntimeConfig`. It wraps sysctls in a small `Sysctl` type and enforces that user-configured default sysctls are both syntactically strict and known to be namespaced by the kernel.

Important APIs are `NewSysctl`, `(*Sysctl).Key`, `(*Sysctl).Value`, `(*RuntimeConfig).Sysctls`, and `(*Sysctl).Validate`. `Sysctls` iterates `DefaultSysctls`, skips empty entries for backward compatibility, requires exact `key=value` format with no trimming changes, and returns parsed values. `Validate` maps exact keys and prefixes to `IpcNamespace` or `NetNamespace`, rejects IPC sysctls for host IPC pods, rejects net sysctls for host network pods, and rejects anything outside the allowlist.

State is derived only from config strings; there is no persistence. Dependencies are Go `fmt` and `strings`. Integration points include runtime config validation and pod setup logic that needs safe default sysctls. Risks include allowlist maintenance as kernel namespacing evolves and the strict no-space parser rejecting values an operator may expect to be tolerated. Tests in `sysctl_test.go` cover parse success/failure, empty compatibility entries, whitelist failures, and host namespace restrictions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/sysctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/sysctl_test.go -->
# sources/cloud-native/cri-o/pkg/config/sysctl_test.go

This test file verifies sysctl parsing and namespace-aware validation. It uses the shared config fixture and mutates `sut.DefaultSysctls` for each scenario.

The tests cover default empty parsing, multiple valid `key=value` entries with empty entries skipped, wrong-format failure, extra-space failure, rejection of unwhitelisted sysctls, rejection of network sysctls with host network enabled, rejection of IPC sysctls with host IPC enabled, and success for allowed net or kernel sysctls when the corresponding host namespace is not shared. State is purely in-memory on `sut`; no external files are used.

Dependencies are Ginkgo/Gomega and the config suite. Integration signal is strong for the strict parser and allowlist rules that protect host namespace safety. Risks not covered include future kernel sysctl namespace additions and full pod admission paths, but the unit tests are precise for the current table-driven behavior in `sysctl.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/sysctl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/template.go -->
# sources/cloud-native/cri-o/pkg/config/template.go

This file generates the TOML configuration template emitted by CRI-O. `(*Config).WriteTemplate` builds a Go `text/template` from a dynamically assembled string and executes it against the current `Config`. The template is organized by CRI-O config tables and comments out default-valued options unless `displayAllConfig` is true.

Important APIs and types are `WriteTemplate`, `assembleTemplateString`, `crioTemplateString`, `templateGroup`, `templateConfigValue`, `initCrioTemplateConfig`, `RuntimesEqual`, and `WorkloadsEqual`. `initCrioTemplateConfig` creates a large registry mapping each config field to a template snippet, group, and default comparison result. It uses scalar equality, `slices.Equal`, custom map equality for runtimes/workloads, and special NRI default-validator detection. `crioTemplateString` strips the `{{ $.Comment }}` marker for non-default values or when showing all config; otherwise the generated entry remains commented through the `Comment` field in `Config`.

State is not persisted directly except through the writer provided by callers. Dependencies include `text/template`, `strings`, `reflect`, and `slices`. Integration points are config file generation, `Config.ToFile`, config docs, reload discoverability comments, and tests that round-trip generated config into `UpdateFromFile`. Risks include silent empty output if `DefaultConfig` fails during assembly, brittle hand-maintained coverage of every config field, equality subtleties for maps containing pointers, and template syntax failures surfacing at write time. Tests cover successful rendering and runtime map equality; broader coverage is indirect through config serialization and reload tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/template_test.go -->
# sources/cloud-native/cri-o/pkg/config/template_test.go

This file provides focused tests for config template rendering and runtime map equality. `WriteTemplate` is exercised with `displayAllConfig=true` against a buffer and is expected to succeed. The `RuntimesEqual` tests check map length mismatch, key mismatch, scalar field mismatch, slice field mismatch, and equal values.

State is limited to local runtime maps and the shared `sut` fixture for template rendering. Dependencies are Ginkgo/Gomega, bytes.Buffer, and the config package. Integration signal is narrow but useful: it verifies the generated template parses and executes for default config, and that `RuntimesEqual` detects the differences `template.go` relies on to decide whether runtime config should be commented as default.

Risks not covered include full textual output correctness, every template field's presence, `WorkloadsEqual`, and non-default comment stripping behavior. Those are mostly covered indirectly by tests that serialize config to temp files.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/template_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/workloads.go -->
# sources/cloud-native/cri-o/pkg/config/workloads.go

This file implements CRI-O's experimental workload configuration, where pod annotations can activate per-container resource defaults and overrides outside normal CRI resource fields. It provides a map of named workloads, validation, allowed-annotation filtering, and OCI spec mutation.

Important types are `Workloads`, `WorkloadConfig`, and `Resources`. Important APIs are `Workloads.Validate`, `(*WorkloadConfig).Validate`, `ValidateWorkloadAllowedAnnotations`, `AllowedAnnotations`, `FilterDisallowedAnnotations`, `MutateSpecGivenAnnotations`, `resourcesFromAnnotation`, `milliCPUToQuota`, `(*Resources).ValidateDefaults`, and `(*Resources).MutateSpec`. Control flow starts by matching the pod's annotations against each workload's exact `ActivationAnnotation`. If active, `resourcesFromAnnotation` reads an annotation key of `prefix/containerName`, unmarshals JSON into `Resources`, fills zero fields from defaults, converts `CPULimit` in millicores to CFS quota, and applies non-zero values to the OCI generator.

State is stored in config as workload maps and `DisallowedAnnotations` generated during validation. There is no filesystem persistence. Dependencies include JSON, logrus, OCI runtime-tools generator, Kubernetes cpuset parsing, and the package's annotation allowlist validator. Integration points are sandbox annotation processing, runtime handler annotation security policy, and OCI Linux resources. Risks include nil default resources causing a dereference in `resourcesFromAnnotation` if an override omits a field, first-match map iteration order when multiple workloads are activated, JSON annotation type sensitivity, and possible confusion between the documented per-resource annotation shape and the implementation's single JSON annotation per container. Tests cover invalid defaults, mutation, `cpulimit` precedence, and quota conversion behavior through spec assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/workloads.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/workloads_test.go -->
# sources/cloud-native/cri-o/pkg/config/workloads_test.go

This file tests workload validation and OCI spec mutation from workload annotations. It verifies invalid cpusets, `cpuquota < cpushares`, and `cpuperiod < 1000` are rejected, while individual valid resource defaults pass. It also confirms that `Resources.MutateSpec` writes CPU cpuset, shares, quota, and period to `specs.LinuxResources`.

The annotation mutation tests construct a workload with an activation annotation and a per-container JSON resource annotation. They check `cpulimit` conversion to quota, `cpulimit` precedence over `cpuquota`, direct quota, cpuperiod, and cpushares. State is local test data plus generated OCI specs; there is no filesystem persistence.

Dependencies include Ginkgo/Gomega, OCI runtime spec and generator packages, and CRI-O config. Integration signal is useful for the exact JSON annotation contract and CFS quota conversion. Gaps include no tests for `AllowedAnnotations`, `FilterDisallowedAnnotations`, nil resources/defaults, invalid JSON, multiple simultaneously active workloads, or map iteration ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/config/workloads_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/types/types.go -->
# sources/cloud-native/cri-o/pkg/types/types.go

This file defines small JSON-serializable data transfer structs for CRI-O introspection. `ContainerInfo` captures container metadata such as name, pid, image identifiers, timestamps, labels, annotations, CRI-O annotations, log/root paths, sandbox ID, IPs, and host-network state. `IDMappings` wraps UID/GID maps from container storage idtools. `CrioInfo` reports daemon-level storage and cgroup information plus default ID mappings.

There are no functions or control flow. State is represented as values that can be marshaled to JSON for APIs or diagnostics. Dependencies are limited to `go.podman.io/storage/pkg/idtools`. Integration points are likely status/info endpoints and tooling that consume CRI-O's daemon/container metadata. Risks are schema stability and the comment that `Image` may not correspond to the user's requested image name, while `ImageRef` has a storage-specific string format. There are no direct tests in this subset; compatibility is usually covered by consumers that marshal or inspect these structs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/pkg/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.0.9.toml -->
# sources/cloud-native/cri-o/releases/v1.0.9.toml

This TOML file is release metadata for CRI-O `v1.0.9`. It identifies `commit = "v1.0.9"`, `project_name = "CRI-O"`, `github_repo = "kubernetes-sigs/cri-o"`, `previous = "v1.0.8"`, and `pre_release = false`, with empty `preface`, `[notes]`, and `[breaking]` sections.

There are no APIs or control flow; the file is declarative input for release tooling. Its persistence role is historical release state used to generate release notes or changelogs. Integration is with release-note generators that compare `previous` to `commit` and render project/repo metadata. Risks are stale repository naming (`kubernetes-sigs/cri-o` differs from modern `cri-o/cri-o`) and empty notes/breaking sections providing no human detail. Test signal is indirect through release tooling parsing TOML files.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.0.9.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.8.5.toml -->
# sources/cloud-native/cri-o/releases/v1.8.5.toml

This release metadata file describes CRI-O `v1.8.5`. It sets the release tag as both commit and identity, points at project `CRI-O` and repository `kubernetes-sigs/cri-o`, records `previous = "v1.8.4"`, and marks the release as non-prerelease. The preface, notes, and breaking sections are empty.

It has no executable APIs. State is persistent historical metadata consumed by release tooling. Integration points are changelog/release-note generators that need a previous tag boundary and project repository data. Risks are the same as the adjacent legacy release files: empty notes reduce generated content, and the legacy GitHub org may matter if tooling assumes current repository paths. No direct tests target this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.8.5.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.1.toml -->
# sources/cloud-native/cri-o/releases/v1.9.1.toml

This TOML file records metadata for CRI-O `v1.9.1`, comparing against `v1.9.0` and marking the release as stable (`pre_release = false`). It includes empty narrative sections for preface, notes, and breaking changes.

The file is declarative release state. It has no functions, but release tooling can use `commit`, `previous`, `project_name`, and `github_repo` as inputs for comparison links and generated notes. Risks are missing human notes and legacy repository naming. Test coverage is indirect through release tooling that loads release descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.2.toml -->
# sources/cloud-native/cri-o/releases/v1.9.2.toml

This file is a release descriptor for CRI-O `v1.9.2`. It declares the current tag, previous tag `v1.9.1`, project and GitHub repository, and stable-release status. Notes and breaking-change tables are present but empty.

There is no control flow or runtime state. The persisted state is the release boundary used by release/changelog tooling. Integration is with scripts or external generators that read TOML descriptors. Risks are low but include silent generation of thin release notes and possible historical repository path mismatch. No direct tests appear in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.3.toml -->
# sources/cloud-native/cri-o/releases/v1.9.3.toml

This CRI-O release metadata file defines `v1.9.3` with `previous = "v1.9.2"` and `pre_release = false`. It carries the project name and legacy GitHub repository path, with empty preface, notes, and breaking sections.

The file is static input for release-note or changelog generation. It persists a release graph edge from `v1.9.2` to `v1.9.3`. Integration risk is mostly data quality: empty notes produce little release-specific content, and repository metadata may require normalization in modern tooling. There is no direct test coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.3.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.5.toml -->
# sources/cloud-native/cri-o/releases/v1.9.5.toml

This TOML descriptor records CRI-O `v1.9.5`, using `v1.9.3` as the previous release. That means the metadata intentionally or historically skips `v1.9.4`. It marks the release as stable and leaves preface, notes, and breaking sections empty.

There are no APIs or control paths. The persisted release edge is important for changelog range selection. Integration points are release tooling that compares tags and emits notes. Risks include accidental omission of an intermediate tag if `v1.9.4` existed and was expected in the release sequence, plus empty human-facing notes. No direct tests validate the descriptor.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.5.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.6.toml -->
# sources/cloud-native/cri-o/releases/v1.9.6.toml

This file describes CRI-O `v1.9.6`, comparing against `v1.9.5` and marking the release as non-prerelease. It includes standard project/repository metadata and empty preface, notes, and breaking tables.

It is declarative release state for generators and has no executable behavior. Integration is with tooling that expects the release descriptor shape used by older CRI-O releases. Risks are minimal but include weak generated notes due to empty sections and legacy repo path assumptions. Test signal is indirect only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/releases/v1.9.6.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/dependencies/dependencies.go -->
# sources/cloud-native/cri-o/scripts/dependencies/dependencies.go

This Go script generates and optionally publishes a CRI-O dependency report. It writes `dependencies.md` under a requested output path and, when `GITHUB_TOKEN` is present, commits and pushes the report to the `gh-pages` branch.

Important APIs are `main` and `run`. `run` creates the output directory, disables `GOSUMDB`, executes `go list --mod=mod -u -m --json all`, stores the module JSON in a temp file, pipes it through `./build/bin/go-mod-outdated` twice for direct outdated and all dependencies, obtains the current Git HEAD, writes a Markdown report with links, then optionally checks out `gh-pages`, writes the report at repo root, commits, rebases, and retries push up to ten times. State/persistence includes temp module JSON, output report file, branch checkout, git commit, and remote push.

Dependencies include logrus, release-sdk git helpers, release-utils command piping, the Go toolchain, `go-mod-outdated`, and GitHub credentials. Integration points are CI, `gh-pages`, and dependency visibility. Risks include leaving branch state changed if deferred checkout errors are hidden, use of `os.Exit(0)` inside `run` when token is absent, unremoved temp files, network/toolchain dependence, and mutating module resolution because `--mod=mod` can update module files. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/dependencies/dependencies.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/github-actions-packages -->
# sources/cloud-native/cri-o/scripts/github-actions-packages

This Bash script installs Ubuntu packages required by CRI-O GitHub Actions jobs. It sources `/etc/os-release`, constructs an OpenSUSE CRIU repository URL for the Ubuntu version, adds its key and apt source, updates package indexes, and installs build/runtime dependencies such as conmon, criu, development headers, rust/cargo, lld, make, socat, and wget.

There are no functions; execution is linear with `set -euo pipefail`. State changes are system-wide: apt keys/sources, package cache, and installed packages. Dependencies include sudo, curl, apt-key, apt, tee, and network access to the CRIU repository. Integration is CI setup for tests that need CRIU, conmon, storage libraries, seccomp, AppArmor, and build tools.

Risks include deprecated `apt-key`, repository availability, unquoted variable expansion for the repository URL, broad system mutation on the runner, and package drift over time. Test signal is operational rather than unit-tested; failures surface in CI setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/github-actions-packages -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/github-actions-setup -->
# sources/cloud-native/cri-o/scripts/github-actions-setup

This Bash script performs full dependency setup for CRI-O GitHub Actions jobs. It sources a `versions` file, detects `GOARCH`, prepares the system, and installs bats, conmon, conmon-rs, cri-tools, crun, libpathrs, runc, ginkgo, CNI plugins, policy/config files, and buildah.

Control flow is through `main` and helper functions. `prepare_system` stops Docker, disables ufw, loads bridge netfilter, sets sysctls, adds subordinate ID ranges, and disables journald rate limits. Install helpers clone GitHub repositories or download release artifacts, build components, copy binaries into system paths, and verify versions. `install_libpathrs` verifies downloaded helper scripts by SHA256 before building. `install_files` copies CRI-O test registry policy/configuration into `/etc/containers`.

State/persistence is extensive and system-wide: kernel modules/sysctls, iptables NAT rule, `/etc/subuid`, `/etc/subgid`, journald config, binaries under `/usr/bin` and `/usr/sbin`, `/opt/cni/bin`, `/etc/containers`, and cloned temp trees. Dependencies include sudo, git, make, Go, curl/wget, network, and many upstream repos. Integration is CI and e2e-style tests. Risks include high privilege requirements, network drift, building from `master` for cri-tools, checksum maintenance for libpathrs helpers, and cleanup omissions if a command fails mid-function.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/github-actions-setup -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release-branch-forward/release_branch_forward.go -->
# sources/cloud-native/cri-o/scripts/release-branch-forward/release_branch_forward.go

This automation finds the latest CRI-O release branch and merges `main` into it when no tag exists for that release branch. It is intended to keep unreleased release branches forward with main until the release tag lands.

Important APIs are `main` and `run`. `run` checks for `git`, `grep`, and `tail`, determines dry-run mode from the `DRY_RUN` environment variable and `-dry-run` flag, uses `git ls-remote --sort=v:refname --heads` piped through grep/tail to pick the latest `release-*` branch, checks for matching remote tags, and exits if any exist. Otherwise it opens the local repo, optionally sets dry mode, records the current branch, checks out the release branch, merges `origin/main`, pushes the release branch, and triggers the GitHub `test` workflow via `gh workflow run`.

State changes are git checkout, merge commit or dry-run equivalent, remote push, and workflow dispatch. Dependencies include release-sdk git, release-utils command/env helpers, logrus, shell commands, network, and GitHub CLI. Risks include selecting the wrong branch if remote naming changes, treating any matching tag output as completion, hidden checkout errors in deferred restore, and the broad impact of automatically merging main into a release branch. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release-branch-forward/release_branch_forward.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release-notes/release_notes.go -->
# sources/cloud-native/cri-o/scripts/release-notes/release_notes.go

This script generates CRI-O release notes and publishes them to `gh-pages`. It requires `GITHUB_TOKEN`, accepts `-output-path`, detects whether the current checkout is exactly on a tag, builds a large release-notes Go template with bundle, SBOM, OpenVEX, SLSA, cosign verification, and changelog sections, runs `./build/bin/release-notes`, then updates the `gh-pages` branch with the generated Markdown and README link.

Important functions are `run`, `readLines`, `indexOfPrefix`, `decVersion`, and `startVersionFromCurrent`. `run` opens the repo, gets HEAD, chooses `CURRENT_BRANCH` or `main`, computes `startTag` and `endRev` from `internal/version.Version` or the exact Git tag, writes a temp template file, invokes the release-notes binary with org/repo/range arguments, reads the generated output, checks out `gh-pages`, writes the release file, inserts or updates its README list entry, commits, rebases, and retries push up to ten times. `decVersion` decrements a tag for exact-tag releases after clearing prerelease data; `startVersionFromCurrent` decrements patch or minor for current development versions.

State/persistence includes temp templates, generated notes, branch checkout, README mutation, commit, and remote push. Dependencies include semver, logrus, release-sdk git, release-utils command/helpers, the release-notes binary, GitHub token, and network. Risks include `os.Exit(0)` from inside `run` when token is absent, panics in `decVersion` for invalid tags, hidden deferred checkout errors, generated template brittleness, and a deliberate non-fatal return if pull/rebase fails. Tests are absent here; helper behavior is not directly validated in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release-notes/release_notes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release/release.go -->
# sources/cloud-native/cri-o/scripts/release/release.go

This Go script automates patch version bump pull requests for active CRI-O release branches. It requires `GITHUB_TOKEN`, uses optional `REMOTE` and `ORG`, loops through `version.ReleaseMinorVersions`, reads each release branch's current version, increments the patch, updates release files, pushes a branch, and opens a GitHub PR.

Important functions are `run`, `updateVersionAndCreatePR`, `modifyVersionFile`, `updateSpecFile`, and `updateDependenciesYAML`. The main control flow configures git identity, opens the repo, checks out each `release-x.y` branch through `utils.GetCurrentVersionFromReleaseBranch`, increments semver patch, and delegates to PR creation. If the bump branch already exists remotely, it checks it out, rebases on the base branch, and force-pushes. Otherwise it creates the branch, replaces old version strings in `internal/version/version.go`, `dependencies.yaml`, and `contrib/test/ci/cri-o.spec`, commits, pushes, and calls GitHub's create pull request API.

State/persistence includes branch checkout, file rewrites, commits, remote pushes, and PR creation. Dependencies include release-sdk git/GitHub clients, release-utils command/env, logrus, semver through utils, and CRI-O version metadata. Risks include global string replacement in `modifyVersionFile`, exact YAML text dependency in `updateDependenciesYAML`, regex-only spec update, branch-state side effects across loop iterations, and destructive force-push for existing bump branches. Tests cover reading and modifying version file content only, leaving PR, git, YAML, and spec update behavior mostly untested.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release/release.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release/release_test.go -->
# sources/cloud-native/cri-o/scripts/release/release_test.go

This test file validates a small part of the release automation: extracting a version from a version file and replacing it with `modifyVersionFile`. It creates temporary files containing mock Go source returned by `getMockVersionFileContent`, asserts `utils.GetCurrentVersionFromVersionFile` reads `1.30.0`, runs `modifyVersionFile` to update `1.30.0` to `1.30.1`, then compares the full file content to the expected mock source.

State is limited to temp files. Dependencies are Ginkgo/Gomega, `os`, `fmt`, and `scripts/utils`. Integration signal is narrow but important because the release script relies on global byte replacement. Risks not covered include actual git branch behavior, GitHub PR creation, dependencies YAML updates, spec regex updates, multiple version occurrences beyond the mocked file, and failure handling for missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release/release_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release/suite_test.go -->
# sources/cloud-native/cri-o/scripts/release/suite_test.go

This file bootstraps the Ginkgo suite for the release script tests. `TestVersion` registers the Gomega fail handler and runs framework specs under the `Version` suite name. `BeforeSuite` creates and sets up the CRI-O test framework; `AfterSuite` tears it down.

There is no production logic. State is the package-level framework pointer `t`. Dependencies are testing, Ginkgo/Gomega, and the CRI-O test framework. Integration signal is only that release script tests share the same test harness conventions as other CRI-O tests. Risks are minimal, though using the full framework for simple file tests may add setup cost or environment dependence.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/release/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/tag-reconciler/tag-reconciler.go -->
# sources/cloud-native/cri-o/scripts/tag-reconciler/tag-reconciler.go

This automation reconciles expected release tags for each active CRI-O release branch. It reads the current version from each release branch, checks whether that version tag already exists on the branch, and if missing creates and pushes the tag and triggers the GitHub `test` workflow.

Important functions are `run`, `pushTagToRemote`, and `hasCurrentReleaseVersionTag`. `run` requires `GITHUB_TOKEN`, reads `REMOTE` and `ORG` defaults, configures git identity, opens the repo, loops over `version.ReleaseMinorVersions`, builds `release-x.y`, reads the current semver using `scripts/utils`, prefixes it with `v`, queries tags for the branch, and pushes missing tags. `pushTagToRemote` creates an annotated/lightweight tag via release-sdk `repo.Tag`, pushes `git push <remote> tag <tag>`, and triggers `gh workflow run test --ref <tag>`.

State changes include branch checkouts in the utils call, tag creation, remote push, and workflow dispatch. Dependencies are release-sdk git, release-utils command/env, logrus, slices, GitHub CLI, and CRI-O version metadata. Risks include trusting the version file on each branch, no rollback if workflow dispatch fails after tag push, branch checkout side effects, and no direct validation that `ORG` is used beyond logging. There are no direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/tag-reconciler/tag-reconciler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/upload-artifacts -->
# sources/cloud-native/cri-o/scripts/upload-artifacts

This Bash script uploads a branch or tag marker file to the `gs://cri-o` Google Cloud bucket when `GCS_CRIO_SA` is provided. If the environment variable is empty, it prints a skip message and exits successfully.

Execution is linear with `set -euo pipefail`. When enabled, it writes the service account JSON to `/tmp/key.json`, authenticates with `gcloud`, determines the marker from `git rev-parse --abbrev-ref HEAD`, uses the current commit as the version, and if in detached HEAD assumes an exact tag, replaces the marker with the tag's major.minor substring and the version with the tag. It writes `latest-$MARKER.txt` and copies it to the bucket with `gsutil`.

State/persistence includes `/tmp/key.json`, a local marker file, and GCS object updates. Dependencies are git, gcloud, gsutil, and credentials. Risks include leaving credentials on disk, fragile `cut -c 2-5` major.minor extraction for multi-digit versions, assuming detached HEAD means exact tag, and no cleanup of marker files. No tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/upload-artifacts -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/utils/utils.go -->
# sources/cloud-native/cri-o/scripts/utils/utils.go

This utility package centralizes constants and helper functions used by CRI-O release automation. Constants define environment variable names, important file paths, branch/tag prefixes, and the canonical CRI-O org/repo string.

Important APIs are `GetCurrentVersionFromReleaseBranch`, `ConvertStringToSemver`, and `GetCurrentVersionFromVersionFile`. The first checks out a release branch with release-sdk git, reads the version file, logs it, and converts it to semver. `ConvertStringToSemver` accepts tag-like strings through release-utils helpers and clears prerelease data. `GetCurrentVersionFromVersionFile` reads a Go file and extracts `const Version = "..."` using a regular expression.

State changes are mainly branch checkout side effects in `GetCurrentVersionFromReleaseBranch`; other functions are read-only. Dependencies include semver, logrus, release-sdk git, release-utils helpers, regex, strings, and filesystem reads. Integration points are release PR creation and tag reconciliation. Risks include regex fragility if the version constant changes shape, branch checkout without restoring the prior branch, and prerelease suffixes being silently cleared. Tests in `release_test.go` cover version extraction from a mock file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/utils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/version_bump.go -->
# sources/cloud-native/cri-o/scripts/version_bump.go

This standalone script bumps CRI-O's version in a version Go file and RPM spec file. It accepts `-bump` (`major`, `minor`, `patch`, default patch), `-f` for the version file, and `-spec` for the spec file.

Important functions are `getCurrentVersion`, `bumpVersion`, `incrementVersionPart`, `updateSpecVersion`, and `updateVersion`. Control flow reads the current version by regex, increments the selected semantic version segment using string splitting, rewrites the version file by replacing `const Version = "..."`, rewrites the first matching `Version: oldVersion` in the spec, and prints the result. State/persistence is direct in-place file mutation.

Dependencies are only standard library packages. Integration is developer or CI version bump workflow, separate from the more elaborate `scripts/release` automation. Risks include no validation that the version has exactly three numeric parts, invalid numeric parts becoming `0` after increment failure, defaulting unknown bump types to patch, regex replacement across any matching const, and spec update requiring exact old version text. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/scripts/version_bump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/artifacts_test.go -->
# sources/cloud-native/cri-o/server/artifacts_test.go

This server test file verifies `server.FilterMountPathsBySubPath`, which filters OCI artifact blob mount paths by a requested subpath. The tests construct a fixed list of `libartifact` blob mount paths and assert behavior for empty subpath, a directory subpath, `"."`, `"./"`-prefixed subpath, and a non-existing subpath.

State is local test data only. The expected control flow is that empty or dot subpaths return the original path list, directory filtering strips the requested directory prefix from returned names, and missing subpaths produce an error with nil result. Dependencies are Ginkgo/Gomega, context, `go.podman.io/common/pkg/libartifact/types`, and the server package.

Integration signal is important for OCI artifact mount support because CRI-O must mount only the requested subpath while preserving relative paths inside the container. Risks not shown include path traversal, Windows path separators, duplicate names, and behavior with files that share prefixes but are not children. This file tests behavior, not the implementation location.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/artifacts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_attach.go -->
# sources/cloud-native/cri-o/server/container_attach.go

This file implements CRI attach endpoint preparation and stream-service attach execution. `(*Server).Attach` handles the CRI request and returns a streaming URL, while `(*StreamService).Attach` executes the attach operation once the streaming server receives a connection.

`Server.Attach` resolves the container by short ID, finds the sandbox runtime handler, and checks whether the runtime handler uses monitor-provided websocket streaming. If websockets are enabled, it asks the runtime to `ServeAttachContainer` and returns that URL. Otherwise it falls back to `s.getAttach(req)` and returns a generic streaming endpoint, mapping preparation failure to a generic error. `StreamService.Attach` starts a trace span, resolves the container, updates container status, requires state `running` or `created`, and delegates to `Runtime().AttachContainer` with input/output/error streams, TTY, and resize channel.

State is not persisted here, but runtime state is read and refreshed through container lookup and status update. Dependencies include CRI runtime API types, Kubernetes remotecommand stream types, gRPC status/codes, CRI-O logging/tracing, and internal OCI state. Integration points are kubelet `Attach`, CRI streaming server, runtime monitor websocket support, and container lifecycle state. Risks include `s.getSandbox(ctx, c.Sandbox())` assuming sandbox availability, generic error hiding fallback endpoint details, and differences between websocket and standard attach behavior. Tests cover success, invalid request, and stream attach missing-container failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_attach_test.go -->
# sources/cloud-native/cri-o/server/container_attach_test.go

This test file exercises the basic attach paths. The suite setup creates a server SUT and tears it down around each test. The CRI `ContainerAttach` test adds a container and sandbox, calls `sut.Attach` with the test container ID and stdout requested, and expects a non-nil response. A second CRI test sends an empty request and expects an error/nil response. The stream-server test calls `testStreamService.Attach` without registering the container and expects failure.

State is provided by the server test framework helpers such as `addContainerAndSandbox`, `setupSUT`, and `testContainer`. Dependencies include CRI runtime API types, Kubernetes remotecommand terminal size, Ginkgo/Gomega, and context. Integration signal confirms the high-level CRI endpoint wiring and missing-container error path. Gaps include no test for websocket runtime handlers, container state rejection, status update failure, stdin/stderr combinations, TTY resize behavior, or actual stream data transfer.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_checkpoint.go -->
# sources/cloud-native/cri-o/server/container_checkpoint.go

This file implements the CRI `CheckpointContainer` endpoint. It gates checkpointing on config support, validates the container exists, constructs checkpoint metadata and options, delegates to the server's lower-level checkpoint implementation, and returns an empty CRI response on success.

The key API is `(*Server).CheckpointContainer`. Control flow first checks `s.config.CheckpointRestore()` and returns `"checkpoint/restore support not available"` if disabled. It then resolves the container by short ID, returning gRPC NotFound status on failure. It logs the operation, creates `metadata.ContainerConfig{ID: req.GetContainerId()}`, creates `lib.ContainerCheckpointOptions{TargetFile: req.GetLocation(), KeepRunning: true}`, calls `s.ContainerCheckpoint`, logs success, and returns `CheckpointContainerResponse`.

State/persistence is delegated to checkpoint creation: the target file from the request may be written by lower layers, and `KeepRunning` preserves the running container for forensic use. Dependencies include checkpointctl metadata, CRI API types, gRPC status codes, CRI-O internal lib checkpoint options, and logging. Integration points are kubelet/CRI checkpoint API, CRIU/checkpointctl, and server config. Risks include keeping containers running by default, limited request validation in this wrapper, and lower-layer errors passing through without CRI status normalization. Tests cover enabled success, invalid container ID, and disabled checkpoint/restore behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_checkpoint_test.go -->
# sources/cloud-native/cri-o/server/container_checkpoint_test.go

This file tests the `CheckpointContainer` CRI endpoint in enabled and disabled configurations. The enabled suite sets up dummy config, mocks runtime config, skips if CRIU is unavailable, enables checkpoint/restore with the test injection hook, and creates the server SUT. The success test adds a container and sandbox, marks the container running, sets a minimal OCI spec, and expects checkpointing to succeed. The invalid-container test expects an error. Cleanup removes checkpoint-related files such as `config.dump`, `cp.tar`, `dump.log`, and `spec.dump`.

The disabled suite sets `CheckpointRestore` false and verifies the endpoint returns the exact `"checkpoint/restore support not available"` message. State includes test framework server/container fixtures and checkpoint artifacts on disk. Dependencies include CRIU availability checks, OCI specs, CRI runtime API, Ginkgo/Gomega, and CRI-O internal OCI state.

Integration signal is strong for the feature gate and minimal working CRIU path, but environment-sensitive because CRIU may be absent and skip the success path. Gaps include target location handling, lower-layer checkpoint failures, non-running container behavior, and validation of checkpoint archive contents.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_checkpoint_test.go -->
