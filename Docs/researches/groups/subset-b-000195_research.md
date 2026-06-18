# subset-b-000195 research

This grouped report covers Moby daemon resource-update translation and the daemon volume stack: driver/plugin adapters, the local driver, mount parsers and mountpoint setup, safepath subpath containment, the volume API service/store, and supporting tests. Each source file has a source-tree-preserving section for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/update_linux.go -->
# sources/cloud-native/moby/daemon/update_linux.go

## Purpose
Linux implementation of `toContainerdResources`, translating Docker API `container.Resources` into the daemon's containerd resource struct backed by OCI runtime-spec Linux resource types.

## Important APIs, Types, And Functions
The single exported-in-package function is `toContainerdResources(resources container.Resources) (*libcontainerdtypes.Resources, error)`. It populates `specs.LinuxBlockIO`, `specs.LinuxCPU`, `specs.LinuxMemory`, and pids via helpers such as `getBlkioWeightDevices`, `getBlkioThrottleDevices`, and `getPidsLimit`.

## Control Flow
The function lazily allocates `BlockIO` only when a blkio field is explicitly present. It converts weight, read/write BPS, and read/write IOPS devices, returning early on conversion errors. CPU cpuset fields are always copied into a temporary `LinuxCPU`; shares, period, and quota are pointer-populated only when non-zero. `NanoCPUs` derives quota from a 100ms period unless explicit quota/period values fill missing values. Memory limit, reservation, and positive swap values are similarly pointer-populated. Empty CPU or memory structs are omitted.

## State And Persistence
No persistent state is modified. The result is an update payload consumed by containerd/runc integration, with nil substructures intentionally representing "unset" resources.

## Dependencies And Integration Points
Depends on Docker API container resources, internal libcontainerd types, OCI runtime-spec structs, and blkio/pids helper functions in the daemon package. It is used by container update flows that need Linux cgroup resource mutation through containerd.

## Risks
Pointer-versus-zero semantics are critical: accidentally allocating a subresource or setting a zero pointer can change containerd update behavior. `NanoCPUs` precedence over explicit quota/period must remain compatible with Docker API behavior. Blkio helpers can fail on invalid device specs, so callers must preserve errors.

## Test Signals
`update_linux_test.go` validates that an empty `container.Resources{}` produces a resource object whose nested fields are unset, guarding against default updates that would mutate existing container limits.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/update_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/update_linux_test.go -->
# sources/cloud-native/moby/daemon/update_linux_test.go

## Purpose
Linux unit coverage for default resource update conversion.

## Important APIs, Types, And Functions
`TestToContainerdResources_Defaults` calls `toContainerdResources(container.Resources{})` and validates the result with `checkResourcesAreUnset`.

## Control Flow
The test creates an empty Docker API resource config, invokes the Linux converter, fails on unexpected conversion errors, then asserts that no cgroup resource values are set in the returned containerd resources.

## State And Persistence
No state is persisted; this is pure conversion validation.

## Dependencies And Integration Points
Depends on the daemon resource conversion function, Docker API resource type, and a test helper that checks unset resource semantics.

## Risks
The test covers only the empty/default case. It does not exercise blkio conversions, `NanoCPUs` quota math, CPU shares/cpuset, memory, swap, or pids behavior.

## Test Signals
The important signal is regression protection for nil/zero semantics: default Docker update input must not produce populated containerd resource fields that could reset runtime settings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/update_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/update_windows.go -->
# sources/cloud-native/moby/daemon/update_windows.go

## Purpose
Windows implementation stub for resource updates.

## Important APIs, Types, And Functions
`toContainerdResources(resources container.Resources) (*libcontainerdtypes.Resources, error)` exists for platform parity but returns `nil, nil`.

## Control Flow
The function ignores input and exits immediately because Windows container update resource conversion is not supported here.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Provides the same package-level function name as the Linux implementation so higher-level daemon update code can compile on Windows. It imports Docker container resources and internal libcontainerd resource types only for signature compatibility.

## Risks
Callers must treat a nil resource payload as "unsupported/no-op" rather than a successful concrete update. Adding Windows support later must clarify API behavior for existing callers that currently expect no mutation.

## Test Signals
No direct Windows test is in this subset. Platform compilation and higher-level update tests would be the practical signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/update_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/adapter.go -->
# sources/cloud-native/moby/daemon/volume/drivers/adapter.go

## Purpose
Adapts legacy/HTTP volume plugin RPC clients to the daemon's `volume.Driver` and `volume.Volume` interfaces.

## Important APIs, Types, And Functions
`volumeDriverAdapter` implements driver operations by delegating to a generated `volumeDriver` proxy. `volumeAdapter` implements `volume.Volume` for plugin-returned volumes. `proxyVolume` mirrors plugin JSON fields. `getCapabilities` caches and normalizes driver capability scope.

## Control Flow
`Create` calls plugin `Create` and returns a `volumeAdapter`. `List` wraps each plugin `proxyVolume` and scopes mountpoints through plugin `ScopedPath`. `Get` handles the plugin edge case of nil volume plus nil error as `errNoSuchVolume`. `Path` lazily calls the plugin and caches an ephemeral mount path; `Mount` refreshes the cache, and successful `Unmount` clears it. Capability lookup defaults to local scope on endpoint error, lowercases scope, and falls back to local for invalid values.

## State And Persistence
State is in-memory only: cached capabilities, cached mount path, created time, and plugin status map. Persistent volume data belongs to the plugin.

## Dependencies And Integration Points
Integrates generated proxy RPC calls, plugin scoped paths, containerd logging, and the daemon volume interfaces consumed by `VolumeStore` and API service conversion.

## Risks
Path cache staleness is possible if plugin state changes out of band. Ignoring errors in `Path` can hide plugin failures. Capability fallback to local is conservative but can change cluster scheduling semantics for broken plugins. Status defensively copies maps; callers should preserve that protection.

## Test Signals
Proxy tests validate plugin error strings; store tests exercise adapter creation indirectly through fake plugin references and create-error dereferencing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/adapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/extpoint.go -->
# sources/cloud-native/moby/daemon/volume/drivers/extpoint.go

## Purpose
Manages registered volume drivers and dynamically discovered `VolumeDriver` plugins.

## Important APIs, Types, And Functions
`Store` holds an extension map, a global mutex, per-driver `locker.Locker`, and optional `plugingetter.PluginGetter`. Public methods include `Register`, `GetDriver`, `CreateDriver`, `ReleaseDriver`, `GetDriverList`, and `GetAllDrivers`. `makePluginAdapter` builds adapters for v1-client and address-based plugins.

## Control Flow
`lookup` validates the name, serializes lookup by driver name, checks registered extensions, then queries the plugin getter with lookup/acquire/release mode. It adapts the plugin, validates its scope, and releases an acquired reference if validation fails. v1 plugins are cached in `extensions`; newer plugins can be returned without caching. `GetAllDrivers` combines registered drivers with discoverable plugins, skipping duplicates.

## State And Persistence
The store is entirely in-memory. Plugin reference counts are maintained outside the store through `PluginGetter.Get` modes.

## Dependencies And Integration Points
The volume service creates this store, registers the local driver, and uses it for create/get/list/remove flows. It integrates Moby plugin discovery, generated volume proxy adapters, and typed errdefs.

## Risks
Reference count balance is subtle: acquire failures during create must release plugin refs. Holding `s.mu` while adapting plugins in `GetAllDrivers` can make slow plugin calls visible to driver listing. Invalid plugin scopes are rejected or coerced depending on path, so capability validation behavior must remain consistent.

## Test Signals
`extpoint_test.go` checks missing driver errors and successful registered-driver retrieval. Store tests with fake plugins cover create failure dereference behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/extpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/extpoint_test.go -->
# sources/cloud-native/moby/daemon/volume/drivers/extpoint_test.go

## Purpose
Basic unit coverage for driver store lookup and registration.

## Important APIs, Types, And Functions
`TestGetDriver` exercises `NewStore`, `GetDriver`, and `Register` with a fake volume driver.

## Control Flow
The test verifies that a missing driver returns an error, registers a fake driver under the name `fake`, retrieves it, and checks that the returned driver reports the expected name.

## State And Persistence
Only in-memory store state is mutated.

## Dependencies And Integration Points
Uses `daemon/volume/testutils.NewFakeDriver` to satisfy `volume.Driver` without a real plugin.

## Risks
The test does not exercise plugin discovery, acquire/release modes, duplicate registration, invalid scopes, or `GetAllDrivers`.

## Test Signals
Confirms the core extension map behavior and missing-driver path remain stable.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/extpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/proxy.go -->
# sources/cloud-native/moby/daemon/volume/drivers/proxy.go

## Purpose
Generated RPC client for the volume plugin API.

## Important APIs, Types, And Functions
`volumeDriverProxy` wraps a plugin client with `CallWithOptions`. Methods cover `Create`, `Remove`, `Path`, `Mount`, `Unmount`, `List`, `Get`, and `Capabilities`. Each method has request/response structs with plugin `Err` fields. Timeouts are `longTimeout` for create/mount and `shortTimeout` for other calls.

## Control Flow
Each method populates a request, calls a `VolumeDriver.*` service endpoint with the configured timeout, copies response data into return values, and converts a non-empty response `Err` string into a Go error.

## State And Persistence
The proxy has no state beyond the embedded client. Persistent effects occur in plugin implementations.

## Dependencies And Integration Points
Generated from `extpoint.go` annotations and consumed by `volumeDriverAdapter`. It depends on plugin client transport and Moby plugin request timeout options.

## Risks
Generated code must match plugin endpoint names and JSON response schemas exactly. Error strings are untyped, limiting caller classification. Timeout choices affect daemon responsiveness and plugin compatibility.

## Test Signals
`proxy_test.go` validates that plugin endpoint `Err` fields and HTTP errors surface as method errors for all RPC operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/proxy_test.go -->
# sources/cloud-native/moby/daemon/volume/drivers/proxy_test.go

## Purpose
Unit coverage for generated volume plugin proxy error propagation.

## Important APIs, Types, And Functions
`TestVolumeRequestError` creates an `httptest.Server`, registers all volume plugin endpoints, builds a plugin client, and invokes `volumeDriverProxy` methods.

## Control Flow
Handlers return JSON `Err` strings for create/remove/mount/unmount/path/list/get, while capabilities returns HTTP 500. The test asserts each proxy method returns an error containing the plugin-provided string, or a capabilities transport error.

## State And Persistence
Only temporary HTTP server state is used.

## Dependencies And Integration Points
Uses Moby plugin client transport, plugin version MIME type, and TLS config options for the test client.

## Risks
The test validates error paths but not successful response decoding, timeout selection, request payload contents, or typed error conversion.

## Test Signals
Strong regression signal that plugin-reported `Err` fields do not get swallowed by generated proxy methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/drivers/proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local.go -->
# sources/cloud-native/moby/daemon/volume/local/local.go

## Purpose
Core implementation of Docker's built-in local volume driver, managing volume directories, metadata files, active mount counts, and live-restore reference state.

## Important APIs, Types, And Functions
`New` initializes a `Root`. `Root` implements `volume.Driver` through `List`, `Name`, `Create`, `Remove`, `Get`, and `Scope`. `localVolume` implements `volume.Volume` and `volume.LiveRestorer` through `Path`, `Mount`, `Unmount`, `Status`, `CreatedAt` in platform files, and `LiveRestoreVolume`. Helpers include `loadOpts`, `saveOpts`, `getAddress`, and `getPassword`.

## Control Flow
Startup creates `<scope>/volumes`, initializes quota control when available, scans child directories, identifies volumes by `_data` or `opts.json`, loads persisted options, restores already-mounted status, and caches volumes. `Create` validates name/options, creates root and `_data` directories with appropriate ownership, applies options, persists them if needed, and caches the volume. `Remove` rejects unknown volume types and active mounts, unmounts, resolves the data path, prevents deletion outside the local volume root, removes data/root paths, and drops cache state. `Mount` mounts once when options require it, increments active count, applies post-mount quota, and returns `_data`; `Unmount` decrements and unmounts only when the count reaches zero.

## State And Persistence
Persistent state is the volume root, `_data`, and `opts.json` written atomically. In-memory state includes the root volume map, quota controller, per-volume options, and `activeMount` count/mounted flags.

## Dependencies And Integration Points
Used as the default driver by `service/default_driver.go`. It depends on idmapped ownership helpers, quota, atomicwriter, mount platform files, errdefs, and Moby name validation.

## Risks
Deletion containment relies on symlink evaluation and prefix checks; path validation must remain strict. Mount count bugs can leave volumes mounted or removable while active. Option persistence compatibility with older nil/empty files matters during daemon upgrades. Password redaction is handled in platform mount errors.

## Test Signals
Local tests cover address/password parsing, create/remove/reload, name validation, option persistence, mount count behavior, tmpfs mounting, quota enforcement, and option validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_linux_test.go -->
# sources/cloud-native/moby/daemon/volume/local/local_linux_test.go

## Purpose
Linux-specific tests for local volume quota support and mount option processing.

## Important APIs, Types, And Functions
Tests include `TestQuota`, `testVolWithQuota`, `testVolQuotaUnsupported`, `TestVolCreateValidation`, and `TestVolMountOpts`.

## Control Flow
Quota tests prepare a sparse XFS image, run with quota enabled/disabled, create size-limited volumes, mount them, and assert writes within and beyond quota behavior. Validation tests exercise invalid names, unknown options, invalid sizes, no quota controller, missing mandatory type/device/o combinations, and CIFS URL port restrictions. Mount option tests inject a resolver to verify CIFS/NFS `addr=` and device host resolution.

## State And Persistence
Tests create temporary local volume roots and may mount quota test filesystems. Persisted options are written through the production local driver.

## Dependencies And Integration Points
Depends on daemon quota test helpers, idtools, local driver, and `gotest.tools` assertions.

## Risks
Quota tests are environment-sensitive and skip when quota support is unavailable. Validation mutates package-level `mandatoryOpts`, so ordering/parallelization would be risky if expanded.

## Test Signals
Good signal for Linux-only behavior: quota admission/failure, mount option DNS rewriting, CIFS password/URL validation, and correct invalid-argument classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_test.go -->
# sources/cloud-native/moby/daemon/volume/local/local_test.go

## Purpose
Cross-platform local-driver unit tests with Windows skips for mount-dependent behavior.

## Important APIs, Types, And Functions
Covers `getAddress`, `getPassword`, `Root.Remove`, `New` reload behavior, `Root.Create`, `validateName`, option-backed tmpfs create/mount, and no-option reload compatibility.

## Control Flow
Tests parse option strings, create temporary roots, create/remove volumes including missing `_data` fallback, restart `Root` over existing directories, validate accepted/rejected names, and on privileged non-Windows systems mount tmpfs with options, verify mountinfo, increment/decrement active count, and reload persisted options.

## State And Persistence
Uses temporary volume directories and persisted `opts.json`. Mount tests create real tmpfs mounts and must unmount through production code.

## Dependencies And Integration Points
Depends on local driver, idtools, mountinfo, runtime OS checks, and test skip helpers.

## Risks
Some reload edge cases in `TestReloadNoOpts` write files at paths that appear intended to simulate malformed opts; changes to directory layout could reduce test effectiveness. Privileged mount tests skip in many CI contexts.

## Test Signals
Protects name/path containment, local driver restart discovery, mount refcount semantics, option persistence, and compatibility with empty/null option data.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_unix.go -->
# sources/cloud-native/moby/daemon/volume/local/local_unix.go

## Purpose
Unix implementation of local driver option validation, mount/unmount behavior, quota application, mount restoration, and creation time.

## Important APIs, Types, And Functions
Defines `optsConfig` with mount type/options/device and quota. Implements `Root.validateOpts`, `localVolume.setOpts`, `needsMount`, `getMountOptions`, `mount`, `postMount`, `unmount`, `restoreIfMounted`, and `CreatedAt`.

## Control Flow
Validation rejects unknown options, invalid size values, size without quota support, CIFS device URLs with embedded ports, and missing mandatory companion options. `setOpts` stores mount and quota settings to `opts.json`. `getMountOptions` rewrites NFS/CIFS `addr=` hostnames and CIFS device hostnames to resolved IPs. `mount` calls `mount.Mount`, redacting CIFS passwords from errors. `postMount` applies quota. `unmount` tolerates already-unmounted paths if mountinfo confirms absence. Startup `restoreIfMounted` marks an option-backed `_data` path as mounted without increasing count.

## State And Persistence
Persists option configuration via common `saveOpts`. Mount and quota state live in the host kernel/filesystem, while active flags are in-memory.

## Dependencies And Integration Points
Depends on go-units, daemon quota, Moby mount and mountinfo packages, net/url/IP resolution, errdefs, and syscall stat ctime.

## Risks
DNS rewriting can surprise users and must preserve escaped CIFS paths. Password redaction only covers `password=<value>` in mount options. Mount restoration without refcount relies on live restore later incrementing usage. Quota support varies by filesystem.

## Test Signals
Linux tests cover quota, mandatory options, CIFS URL restrictions, tmpfs mounting, mountinfo checks, and host resolution behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_windows.go -->
# sources/cloud-native/moby/daemon/volume/local/local_windows.go

## Purpose
Windows implementation of local driver platform hooks, where local volume mount options are unsupported.

## Important APIs, Types, And Functions
Defines empty `optsConfig`. Implements no-op or rejecting variants of `validateOpts`, `setOpts`, `needsMount`, `mount`, `unmount`, `postMount`, `restoreIfMounted`, and `CreatedAt` using Windows creation time.

## Control Flow
Any non-empty options map is rejected as invalid parameter. Mount-related methods do nothing and report no mount requirement. `CreatedAt` reads `Win32FileAttributeData.CreationTime` from the volume root.

## State And Persistence
No option state is persisted on Windows. Volume directory state is managed by common local code.

## Dependencies And Integration Points
Completes the local driver interface for Windows builds and integrates with common create/remove/list logic.

## Risks
Callers must not assume option support or mount refcount behavior on Windows. The empty `unmount` function is retained for platform compatibility and should not be mistaken for production unmounting.

## Test Signals
Common local tests run with Windows skips where needed; Windows-specific creation time is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/local/local_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/fuzz_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/fuzz_test.go

## Purpose
Fuzz target for Linux raw mount specification parsing.

## Important APIs, Types, And Functions
`FuzzParseLinux` constructs `NewLinuxParser`, injects `mockFiProvider`, and calls `ParseMountRaw` with arbitrary byte input converted to string.

## Control Flow
The fuzzer ignores parser outputs and errors; its only assertion is that parsing arbitrary input must not panic or hang.

## State And Persistence
No persistent state is used.

## Dependencies And Integration Points
Shares `mockFiProvider` from parser tests to avoid host filesystem dependence.

## Risks
It exercises only Linux raw syntax and does not assert semantic correctness. Fuzz coverage depends on Go fuzzing being enabled in the test environment.

## Test Signals
Good crash-resistance signal for colon splitting, mode parsing, path normalization, and validation error construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/lcow_parser.go -->
# sources/cloud-native/moby/daemon/volume/mounts/lcow_parser.go

## Purpose
Parser variant for Linux Containers on Windows, combining Windows host-source parsing with Linux-style container destinations.

## Important APIs, Types, And Functions
`NewLCOWParser` embeds a `windowsParser`; `lcowValidators` rejects root destinations, named pipes, and non-Linux absolute container paths. `lcowParser` overrides `ValidateMountConfig`, `ParseMountRaw`, and `ParseMountSpec`.

## Control Flow
Raw specs are split using Windows source rules plus LCOW destination regex. Parsing delegates to the Windows parser's `parseMount` but disables backslash conversion for targets and uses LCOW validators. Mount specs similarly reuse Windows source validation while preserving slash-style container targets.

## State And Persistence
No state is persisted. Parser state is limited to the embedded file-info provider.

## Dependencies And Integration Points
Used when daemon code needs LCOW semantics. Depends on shared Windows regex fragments, lazy regex compilation, Docker API mount types, and common mount validation helpers.

## Risks
Because it embeds Windows parser behavior, changes to Windows source regex or volume-name validation affect LCOW. Named pipe rejection and root normalization are security/compatibility-sensitive.

## Test Signals
`lcow_parser_test.go` covers valid/invalid raw specs, reserved names, file-vs-directory source checks, root target rejection, no named-pipe support, and parsed `MountPoint` fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/lcow_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/lcow_parser_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/lcow_parser_test.go

## Purpose
Unit coverage for LCOW raw mount parsing and split-to-`MountPoint` conversion.

## Important APIs, Types, And Functions
`TestLCOWParseMountRaw` validates accepted/rejected strings. `TestLCOWParseMountRawSplit` compares parsed mountpoints against expected structs.

## Control Flow
The tests inject `mockFiProvider`, then exercise Windows host paths, named volumes, mixed-case modes, Linux slash destinations, reserved Windows volume names, missing sources, file sources, root destinations, and named pipe rejection. Split tests assert source, destination, mode, driver, type, read-write, and propagation fields.

## State And Persistence
No persistent state; all source existence checks come from the mock provider.

## Dependencies And Integration Points
Depends on LCOW parser, shared Windows mock file info, Docker API mount structs, and cmp options ignoring unexported `MountPoint` fields.

## Risks
The tests are table-driven but cover only known regex cases. They do not cover `ParseMountSpec` directly beyond shared validator behavior.

## Test Signals
Strong signal for LCOW's hybrid path semantics: Windows source grammar with Linux container destination grammar and no named-pipe mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/lcow_parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/linux_parser.go -->
# sources/cloud-native/moby/daemon/volume/mounts/linux_parser.go

## Purpose
Linux mount parser and validator for raw `-v`-style specs and structured API `mount.Mount` configs.

## Important APIs, Types, And Functions
`NewLinuxParser` creates `linuxParser`. Important functions include `ValidateMountConfig`, `validateMountConfigImpl`, `ParseMountRaw`, `ParseMountSpec`, `ParseVolumesFrom`, `ConvertTmpfsOptions`, `ReadWrite`, `DefaultPropagationMode`, `DefaultCopyMode`, `IsBackwardCompatible`, and `ValidateTmpfsMountDestination`.

## Control Flow
Validation enforces exclusive option structs, non-empty absolute non-root targets, bind source presence/absolute path/existence unless raw parsing skips existence, volume subpath locality, tmpfs source absence and option validity, and image source/subpath rules. Raw parsing splits on up to three colon fields, distinguishes bind from volume by absolute source path, applies read-only, driver, copy, and propagation modes, then delegates to structured parsing. Structured parsing normalizes targets/sources, initializes `MountPoint`, and fills volume name/driver/copy, bind propagation, tmpfs, or image source fields. Tmpfs conversion serializes read-only, mode, size suffix, and a small option allowlist.

## State And Persistence
Parser has no persistence. It may query filesystem existence through `fileInfoProvider`.

## Dependencies And Integration Points
Used by daemon container create/update validation, volume service name validation, and mount setup. Depends on API mount types, shared copy mode helpers, and `MountPoint`.

## Risks
Colon grammar, path normalization, and raw-vs-structured bind source existence differences are compatibility-sensitive. Subpath validation is lexical; runtime symlink safety is handled later by `safepath`. Tmpfs option allowlist is intentionally narrow.

## Test Signals
Linux parser tests cover raw syntax, invalid modes, propagation, bind/volume parsing, file-info errors, structured validation, tmpfs option conversion, and fuzz crash resistance.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/linux_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/linux_parser_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/linux_parser_test.go

## Purpose
Linux parser tests for raw mount specs, structured mount validation, file-info error propagation, and tmpfs option serialization.

## Important APIs, Types, And Functions
Tests include `TestLinuxParseMountRaw`, `TestLinuxParseMountRawSplit`, `TestLinuxValidateMounts`, `TestLinuxParseMountSpecBindWithFileinfoError`, and `TestConvertTmpfsOptions`.

## Control Flow
Raw tests run valid and invalid string tables across destinations, bind paths, named volumes, rw/ro, SELinux labels, propagation modes, duplicate mode rejection, and invalid colon forms. Split tests compare complete `MountPoint` values. Structured validation checks bind, volume, invalid source, invalid type, and image behavior outside Windows. File-info tests ensure provider errors are returned instead of collapsed to missing-source errors. Tmpfs tests assert mode, size suffix, read-only, allowed options, and invalid option errors.

## State And Persistence
Uses temp dirs and mock file providers; no persistent daemon state.

## Dependencies And Integration Points
Depends on Linux parser, shared mocks, Docker API mount types, and cmp helpers.

## Risks
The tests document compatibility quirks such as empty mode versus explicit `rw`. Host mount setup is not exercised.

## Test Signals
Strong semantic signal for Linux mount spec compatibility, especially propagation/copy mode validation and file-info error fidelity.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/linux_parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/mounts.go -->
# sources/cloud-native/moby/daemon/volume/mounts/mounts.go

## Purpose
Defines the persistent `MountPoint` model and runtime setup/cleanup behavior connecting container mount declarations to volume, bind, image, and layer resources.

## Important APIs, Types, And Functions
`RWLayer` abstracts writable layer mount/unmount. `MountPoint` stores persisted mount metadata plus runtime fields (`Volume`, `active`, `safePaths`, `Layer`). Methods include `Cleanup`, `Setup`, `LiveRestore`, and `Path`.

## Control Flow
`Setup` returns source directly when mountpoint creation is skipped. For volumes it generates/reuses an ID, calls `Volume.Mount`, optionally wraps `VolumeOptions.Subpath` with `safepath.Join`, increments `active`, and returns a cleanup callback for the safe path. For image mounts with subpaths it uses `safepath.Join` over the image source. For bind mounts it optionally runs `checkFun`, then best-effort creates missing host directories with remapped root ownership. A deferred relabel block evaluates symlinks and applies SELinux labels when requested, cleaning up on relabel errors. `Cleanup` closes any valid safe paths, calls `Volume.Unmount`, decrements active count, and clears ID at zero. `LiveRestore` calls optional `volume.LiveRestorer` and increments active.

## State And Persistence
`MountPoint` is embedded in container state and persisted, but `Volume`, `safePaths`, and `Layer` are runtime-only. Setup mutates mount IDs, active counters, and may create host bind directories or temporary safe mounts.

## Dependencies And Integration Points
Integrates parsers, volume drivers, safepath, idtools, user chown helpers, SELinux labeling, string IDs, and container layer code.

## Risks
Mount/unmount reference counting and safe path cleanup are security-sensitive. Subpath handling must avoid TOCTOU and use-after-close. Bind auto-creation can create directories where files were intended. Relabel failure handling must clean up temporary resources correctly.

## Test Signals
Parser and safepath tests cover inputs feeding `Setup`; direct setup behavior is primarily covered by higher-level daemon/container integration tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/mounts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/parser.go -->
# sources/cloud-native/moby/daemon/volume/mounts/parser.go

## Purpose
Defines common mount parser interfaces, shared errors, mode maps, and host-OS parser selection.

## Important APIs, Types, And Functions
Exports `ErrVolumeTargetIsRoot`, shared subpath errors, `rwModes`, `Parser`, and `NewParser`.

## Control Flow
`NewParser` returns `NewWindowsParser` when `runtime.GOOS == "windows"` and `NewLinuxParser` otherwise. The `Parser` interface defines raw/spec parsing, volumes-from parsing, tmpfs conversion, default copy/propagation, volume-name validation, resource ownership checks, and mount config validation.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
All daemon mount parsing and volume service volume-name validation depend on this common interface. The platform-specific parser implementations satisfy it.

## Risks
Adding fields to `Parser` affects all platform parsers. Shared error values are used by tests and possibly API error matching, so changing messages can break compatibility.

## Test Signals
`parser_test.go`, platform parser tests, and validation tests exercise `NewParser` and interface behavior across OS-specific constants.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/parser_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/parser_test.go

## Purpose
Shared parser tests and mock file-info providers for platform parser suites.

## Important APIs, Types, And Functions
`mockFiProvider` and `mockFiProviderWithError` provide deterministic file existence. `TestParseMountSpec` verifies `NewParser().ParseMountSpec` normalization and fields for bind, volume, and image mounts.

## Control Flow
The test creates a temp source directory, obtains the platform parser, and runs structured mount cases for read-only/read-write binds, trailing separator cleanup, anonymous volumes, and non-Windows image mounts. It asserts type, destination, source, RW, propagation, driver, and copy data.

## State And Persistence
Only temporary directories are used.

## Dependencies And Integration Points
Supports Linux, Windows, and LCOW tests by sharing mock file-info behavior.

## Risks
Because it adapts to `runtime.GOOS`, expected paths come from platform constants in separate files. It does not deeply compare all `MountPoint.Spec` fields.

## Test Signals
Provides cross-platform smoke coverage for parser selection and normalized structured mountpoint output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate.go -->
# sources/cloud-native/moby/daemon/volume/mounts/validate.go

## Purpose
Shared mount validation error helpers and option exclusivity checks.

## Important APIs, Types, And Functions
`errMountConfig` wraps a `mount.Mount` and underlying validation error. Helpers include `errBindSourceDoesNotExist`, `errExtraField`, `errMissingField`, and `validateExclusiveOptions`.

## Control Flow
Platform parsers call `validateExclusiveOptions` before type-specific checks. It rejects bind, volume, image, tmpfs, and cluster option structs when the mount type does not match.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used by Linux, Windows, and LCOW validators to produce consistent API error messages for invalid mount configs.

## Risks
Error text is user-facing and tested. New mount types/options must update exclusivity checks or invalid cross-type fields may pass silently.

## Test Signals
`validate_test.go` exercises missing fields, extra option structs, unknown type, missing bind source, and image-specific option exclusivity.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/validate_test.go

## Purpose
Shared validation tests for mount configs on the current platform plus LCOW-specific validation on Windows.

## Important APIs, Types, And Functions
`TestValidateMount` calls `NewParser().ValidateMountConfig`; `TestValidateLCOWMount` calls `NewLCOWParser` on Windows.

## Control Flow
Tests cover missing target/source, valid volume and bind configs, volume subpaths, extra option structs for wrong mount types, unknown mount types, missing bind source, and non-Windows image mount validation. LCOW tests verify similar rules with Linux-style targets and Windows host sources.

## State And Persistence
Uses temporary directories only.

## Dependencies And Integration Points
Depends on parser selection and platform constants from `validate_unix_test.go` or `validate_windows_test.go`.

## Risks
Because platform-specific parser behavior differs, the same table can assert slightly different full errors only through substring matching.

## Test Signals
Good regression signal for common API validation rules and cross-type option rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate_unix_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/validate_unix_test.go

## Purpose
Unix test constants for shared mount validation tests.

## Important APIs, Types, And Functions
Defines `testDestinationPath = "/foo"` and `testSourcePath = "/foo"` for non-Windows builds.

## Control Flow
No runtime logic; constants are compiled into `validate_test.go` and `parser_test.go`.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected by `//go:build !windows` and used by shared tests to express Unix absolute paths.

## Risks
Constants must stay valid for Linux parser absolute-path rules.

## Test Signals
Successful non-Windows test compilation validates build-tag wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate_windows_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/validate_windows_test.go

## Purpose
Windows test constants for shared mount validation tests.

## Important APIs, Types, And Functions
Defines `testDestinationPath = c:\foo` and `testSourcePath = c:\foo`.

## Control Flow
No runtime logic; constants are used by shared parser/validation tests on Windows builds.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected on Windows and keeps shared tests aligned with Windows absolute path grammar.

## Risks
Constants must remain accepted by Windows parser destination/source regexes.

## Test Signals
Successful Windows test compilation validates build-tag wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/validate_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/volume_copy.go -->
# sources/cloud-native/moby/daemon/volume/mounts/volume_copy.go

## Purpose
Shared helpers for volume copy mode parsing.

## Important APIs, Types, And Functions
`copyModes` currently maps `nocopy` to false. `copyModeExists` checks mode membership. `getCopyMode(mode string, def bool) (bool, bool)` returns selected copy behavior and whether it was explicitly set.

## Control Flow
`getCopyMode` splits comma-separated mount mode strings, returns the first recognized copy option, or the caller-provided default with `isSet=false`.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Linux and Windows/LCOW raw parsers use this to set `mount.VolumeOptions.NoCopy` and `MountPoint.CopyData`.

## Risks
Adding more copy modes must preserve duplicate-mode validation in platform parsers. Because only the first copy option is returned, parser-side counting remains responsible for rejecting duplicates.

## Test Signals
Linux/Windows parser tests cover `nocopy` rejection in volumes-from and copy default behavior through parsed `MountPoint.CopyData`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/volume_copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/volume_unix.go -->
# sources/cloud-native/moby/daemon/volume/mounts/volume_unix.go

## Purpose
Unix implementation of mount resource ownership checks.

## Important APIs, Types, And Functions
`(p *linuxParser) HasResource(m *MountPoint, absolutePath string) bool` tests whether an absolute path is inside a mountpoint destination.

## Control Flow
The function computes `filepath.Rel(m.Destination, absolutePath)` and returns true when the relative path is not `..` and does not start with `../`.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used by daemon logic that needs to determine whether a path is covered by a mountpoint, such as conflict/resource checks.

## Risks
This is lexical and destination-relative; callers must pass normalized absolute paths. Platform separator handling matters for correctness.

## Test Signals
No direct test in this subset; parser and mount tests indirectly depend on destination normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/volume_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/volume_windows.go -->
# sources/cloud-native/moby/daemon/volume/mounts/volume_windows.go

## Purpose
Windows implementation stub for Linux parser resource ownership checks.

## Important APIs, Types, And Functions
`(p *linuxParser) HasResource(m *MountPoint, absolutePath string) bool` returns false on Windows builds.

## Control Flow
No conditional logic; all inputs produce false.

## State And Persistence
No state.

## Dependencies And Integration Points
Satisfies the `Parser` interface for build combinations where `linuxParser` still needs a Windows method implementation.

## Risks
Callers must not expect Linux-style resource coverage checks on Windows. Any Windows-specific resource logic belongs in `windowsParser.HasResource`.

## Test Signals
No direct tests; interface compilation is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/volume_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/windows_parser.go -->
# sources/cloud-native/moby/daemon/volume/mounts/windows_parser.go

## Purpose
Windows mount parser and validator for raw and structured mount specs, including bind mounts, named volumes, and named pipes.

## Important APIs, Types, And Functions
Defines regex fragments for host dirs, names, reserved names, named pipes, sources, destinations, and modes. `windowsParser` implements `Parser` methods: `ParseMountRaw`, `ParseMountSpec`, `ValidateMountConfig`, `ParseVolumesFrom`, `ReadWrite`, `ValidateVolumeName`, tmpfs/default methods, and `HasResource`.

## Control Flow
Raw parsing lowercases and splits via named regex groups, rejects malformed specs, detects attempts to map files as anonymous local volumes, and validates reserved names. Structured validation enforces exclusive options, non-root/non-empty targets, destination regex, bind source absolute/existing/directory rules, volume subpath locality and name validation, and named pipe source/target rules. Parsed mountpoints normalize slashes to backslashes, trim trailing backslashes except drive roots, set drivers/copy data for volumes, and mark read-only based on mode.

## State And Persistence
Parser state is limited to `fileInfoProvider`; no persistence.

## Dependencies And Integration Points
Used by Windows daemon mount validation and by LCOW through embedding. Depends on lazy regexes, API mount types, shared validation/copy helpers, and filesystem stat provider.

## Risks
Regex grammar is dense and highly compatibility-sensitive. Lowercasing raw specs may affect case-preserving expectations. Reserved device names and named pipe handling are security-sensitive. Windows tmpfs/image/resource methods intentionally return unsupported defaults.

## Test Signals
Windows parser tests cover many raw forms, reserved names, file-vs-directory checks, named pipes, mode parsing, structured validation, and file-info error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/windows_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/windows_parser_test.go -->
# sources/cloud-native/moby/daemon/volume/mounts/windows_parser_test.go

## Purpose
Unit tests for Windows raw mount parsing and structured validation.

## Important APIs, Types, And Functions
Tests include `TestWindowsParseMountRaw`, `TestWindowsParseMountRawSplit`, `TestWindowsValidateMounts`, and `TestWindowsParseMountSpecBindWithFileinfoError`.

## Control Flow
Raw tests cover drive roots, long paths, paths with spaces, named volumes, mixed-case modes, forward slash normalization, named pipes, invalid punctuation, reserved names, root C drive destination rejection, missing sources, file sources, and invalid pipe targets. Split tests compare complete `MountPoint` structs for bind, volume, read-only, driver, and pipe cases. Structured tests validate bind, anonymous volume, invalid sources/types, and provider error propagation.

## State And Persistence
No persistent state; mock file provider supplies deterministic Windows paths.

## Dependencies And Integration Points
Depends on Windows parser, shared mocks, Docker API mount types, cmp options, and assertion helpers.

## Risks
Most paths are syntactic mocks rather than real Windows filesystem state. The tests intentionally document compatibility quirks such as destination/mode ambiguity.

## Test Signals
Strong signal for Windows mount-spec grammar, reserved-name handling, named pipe validation, and stat error fidelity.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/mounts/windows_parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/common.go -->
# sources/cloud-native/moby/daemon/volume/safepath/common.go

## Purpose
Shared path-resolution helpers for safe volume/image subpath mounting.

## Important APIs, Types, And Functions
`evaluatePath(path, subpath)` resolves symlinks in the base and combined path, returns resolved base and a relative resolved subpath, and errors if the result escapes. `isLocalTo(path, basepath)` lexically checks subtree membership via `filepath.Rel` and `filepath.IsLocal`.

## Control Flow
`evaluatePath` resolves the base, maps missing/inaccessible paths to `ErrNotAccessible`, resolves the combined path, computes the relative path from base to combined target, and rejects non-local relative paths as `ErrEscapesBase`.

## State And Persistence
No state is persisted. It reads filesystem metadata through `EvalSymlinks`.

## Dependencies And Integration Points
Called by Linux and Windows `Join` implementations before platform-specific fd/handle locking. Errors integrate with Moby errdefs through marker methods.

## Risks
The initial symlink resolution is not sufficient alone for TOCTOU safety; callers must continue with platform-specific safe open/locking. `filepath.IsLocal` behavior differs by OS and is central to containment.

## Test Signals
`common_test.go` covers lexical locality cases including backtracking, absolute escapes, relative paths, and dot-containing filenames.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/common_test.go -->
# sources/cloud-native/moby/daemon/volume/safepath/common_test.go

## Purpose
Unit tests for lexical subtree checks used by safepath.

## Important APIs, Types, And Functions
`TestIsLocalTo` exercises `isLocalTo`.

## Control Flow
The table checks paths equal to base, nested paths, absolute escapes, `..` backtracking outside base, backtracking that remains inside base, relative paths, and filenames containing dots.

## State And Persistence
No filesystem state is required; checks are lexical.

## Dependencies And Integration Points
Validates the helper used by both Linux fallback safe open and Windows handle-lock traversal.

## Risks
Does not test symlink resolution; those behaviors are covered by `join_test.go`.

## Test Signals
Good signal that containment is not implemented by naive string prefix checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/errors.go -->
# sources/cloud-native/moby/daemon/volume/safepath/errors.go

## Purpose
Typed errors for safe subpath resolution failures.

## Important APIs, Types, And Functions
`ErrNotAccessible` records path and cause, implements `NotFound`, `Unwrap`, and `Error`. `ErrEscapesBase` records base/subpath and implements `InvalidParameter` plus `Error`.

## Control Flow
Platform join/open code returns these errors for missing/inaccessible paths, symlink replacement, and base escape attempts. Marker methods allow error classification by Moby errdefs.

## State And Persistence
No state beyond error values.

## Dependencies And Integration Points
Used by `safepath.Join` and mount setup for volume/image subpaths. Higher layers can map them to API not-found or invalid-parameter responses.

## Risks
Error classification is part of API behavior. Avoid leaking sensitive full paths if future call sites expose messages directly.

## Test Signals
Join tests assert `ErrEscapesBase` for escaping symlinks and indirectly exercise `ErrNotAccessible` in failure paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/join_linux.go -->
# sources/cloud-native/moby/daemon/volume/safepath/join_linux.go

## Purpose
Linux implementation of secure subpath joining that returns a temporary bind mount pinned to the validated target.

## Important APIs, Types, And Functions
`Join(ctx, path, subpath)` is the public API. Helpers include `safeOpenFd`, `tempMountPoint`, and `cleanupSafePath`.

## Control Flow
`Join` resolves base/subpath, locks the OS thread, opens the resolved subpath with `safeOpenFd`, creates a temp file or directory mountpoint based on fd type, bind mounts `/proc/self/fd/<fd>` to that temp path, and returns a `SafePath` with cleanup. `safeOpenFd` opens the base with `O_PATH|O_DIRECTORY|O_NOFOLLOW`, tries `openat2` with `RESOLVE_BENEATH|NO_MAGICLINKS|NO_SYMLINKS`, falls back to Kubernetes safe-open on `ENOSYS`, maps `EXDEV` to escape and `ENOENT/ELOOP` to inaccessible. Cleanup unmounts with `MNT_DETACH` and removes the temp path.

## State And Persistence
Creates temporary filesystem entries and kernel bind mounts; `SafePath.Close` must remove them. No daemon metadata is persisted.

## Dependencies And Integration Points
Used by `MountPoint.Setup` for volume/image subpaths. Depends on unix syscalls, `/proc/self/fd`, no-EINTR wrappers, and Kubernetes-derived fallback logic.

## Risks
Requires mount permissions and Linux kernel support. Cleanup leaks can leave temp mounts. Correct fd lifetime and thread locking are important to avoid racing mount source resolution.

## Test Signals
Join tests cover escaping symlinks, safe symlinks inside base, symlink replacement after join, and close invalidation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/join_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/join_test.go -->
# sources/cloud-native/moby/daemon/volume/safepath/join_test.go

## Purpose
Cross-platform tests for safepath subpath containment and lifetime guarantees.

## Important APIs, Types, And Functions
Tests include `TestJoinEscapingSymlink`, `TestJoinGoodSymlink`, `TestJoinWithSymlinkReplace`, and `TestJoinCloseInvalidates`.

## Control Flow
Escaping tests create symlinks to root, absolute files, and relative `../../` targets and expect `ErrEscapesBase`. Good symlink tests create files/directories and symlinks inside the base and verify returned safe paths can read expected data. Replacement tests obtain a safe path, replace the original target with an escaping symlink on Unix, and assert the safe path still points to old content. Close tests ensure `IsValid` flips after `Close`.

## State And Persistence
Uses temporary directories, symlinks, and platform join cleanup; Linux tests may create temporary bind mounts through production code.

## Dependencies And Integration Points
Validates `Join`, `SafePath`, and typed errors used by mount setup for volume/image subpaths.

## Risks
Some Windows behavior differs because handles prevent deletion/replacement. Tests do not explicitly assert `Path` panics after close.

## Test Signals
Strong security signal for symlink escape rejection and TOCTOU resistance after successful join.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/join_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/join_windows.go -->
# sources/cloud-native/moby/daemon/volume/safepath/join_windows.go

## Purpose
Windows implementation of safe subpath joining through component handle locking.

## Important APIs, Types, And Functions
`Join(ctx, path, subpath)` resolves and locks a path. `lockFile` opens each component with backup semantics and reparse-point flags.

## Control Flow
After shared symlink evaluation, `Join` splits the relative subpath and walks each component. For each path it opens a handle, registers cleanup, re-evaluates symlinks, rejects escapes, checks file information by handle, and rejects reparse points. On success it returns a `SafePath` pointing to the real full path with cleanup handles released to the `SafePath`.

## State And Persistence
No files are created. The `SafePath` owns open Windows handles that keep components stable until closed.

## Dependencies And Integration Points
Used by mount setup for subpaths on Windows. Depends on Windows syscall handles, `cleanups.Composite`, and shared safepath errors.

## Risks
Handle lifetime is the core safety boundary; cleanup bugs can leak handles. Reparse-point rejection is important for symlink/junction safety. Capturing `fullPath` in cleanup closures must remain correct if modified.

## Test Signals
Cross-platform safepath tests cover escape rejection, valid internal symlinks, replacement behavior, and close invalidation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/join_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/k8s_safeopen_linux.go -->
# sources/cloud-native/moby/daemon/volume/safepath/k8s_safeopen_linux.go

## Purpose
Fallback Linux safe-open implementation derived from Kubernetes subpath handling for kernels lacking `openat2`.

## Important APIs, Types, And Functions
`kubernetesSafeOpen(base, subpath string) (int, error)` opens a path component-by-component without following symlinks and returns an fd for the final target.

## Control Flow
The function opens the base with nofollow flags, splits the subpath, checks each current path remains local to base, triggers automounts with `fstatat` on a trailing slash, opens each child via `openat` with `O_NOFOLLOW|O_PATH`, stats it to reject symlinks, closes the previous parent fd, and returns the final fd without closing it.

## State And Persistence
No persistent state. It opens and closes fds; caller owns the returned fd.

## Dependencies And Integration Points
Used by `safeOpenFd` when `openat2` is unavailable. Depends on Unix no-EINTR wrappers and shared `isLocalTo`/typed errors.

## Risks
Correct fd cleanup on all error paths is subtle. It assumes resolved input from `evaluatePath` and disallows symlinks during traversal. Automount behavior may have host-specific effects.

## Test Signals
Covered indirectly by safepath join tests on systems where `openat2` is unavailable or by forcing fallback in lower-level tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/k8s_safeopen_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/safepath.go -->
# sources/cloud-native/moby/daemon/volume/safepath/safepath.go

## Purpose
Defines the `SafePath` handle returned by platform-specific safe join implementations.

## Important APIs, Types, And Functions
`SafePath` stores the usable path, cleanup callback, mutex, and immutable source base/subpath. Methods are `Close`, `IsValid`, `Path`, and `SourcePath`.

## Control Flow
`Close` serializes with the mutex, logs and no-ops if already closed, clears the path before calling cleanup, and returns cleanup errors. `IsValid` reports whether the path is still usable. `Path` panics on use after close. `SourcePath` returns immutable origin data without locking.

## State And Persistence
State is in-memory path validity plus cleanup-owned platform resources such as bind mounts or Windows handles.

## Dependencies And Integration Points
`MountPoint.Setup` stores safe paths and calls cleanup callbacks; `MountPoint.Cleanup` closes any leftover safe paths.

## Risks
Clearing `path` before cleanup means cleanup failures still invalidate the object, which avoids reuse but can hide leaked resources. `Path` panic is intentional but must not be reached from user-controlled cleanup paths.

## Test Signals
`join_test.go` verifies `Close` invalidates `SafePath`; mount cleanup logs unclosed safe paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/safepath/safepath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/by.go -->
# sources/cloud-native/moby/daemon/volume/service/by.go

## Purpose
Defines composable in-memory volume filters for `VolumeStore.Find`.

## Important APIs, Types, And Functions
`By` is the marker interface. Constructors/types include `ByDriver`, `ByReferenced`, `And`, `Or`, `CustomFilter`, `FromList`, and `byLabelFilter`.

## Control Flow
Filters are marker values interpreted by `VolumeStore.filter`. `byLabelFilter` returns a `CustomFilter` that requires `volume.DetailedVolume`, matches positive `label` filters, and rejects volumes matching `label!`.

## State And Persistence
No state is persisted; filters operate on volume lists and store reference state.

## Dependencies And Integration Points
Used by service list/prune/local-size flows and store tests. Integrates daemon filter args and detailed volume labels.

## Risks
Label filtering excludes volumes that do not implement `DetailedVolume`. `Or`/`And` behavior is implemented elsewhere, so new filter types require updates in `VolumeStore.filter`.

## Test Signals
Service list/prune and store filter tests cover driver, dangling/reference, label, and custom filtering behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/by.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/convert.go -->
# sources/cloud-native/moby/daemon/volume/service/convert.go

## Purpose
Converts internal volume objects and API filter args to public API volume representations and store filters.

## Important APIs, Types, And Functions
Defines conversion options `useCachedPath` and `calcSize`, `pathCacher`, `volumesToAPI`, `volumeToAPIType`, `filtersToBy`, and `withPrune`.

## Control Flow
`volumesToAPI` loops with context cancellation checks, converts each volume, optionally uses cached mountpoint, and optionally calculates directory size plus reference count. `volumeToAPIType` fills name, driver, RFC3339 created time, labels/options/scope for `DetailedVolume`, and cached mountpoint when supported. `filtersToBy` validates accepted filters and builds `By` combinators for driver, name, label, and dangling. `withPrune` adds the anonymous-volume label filter unless `all=true`.

## State And Persistence
No persistent writes. Size calculation reads filesystem data, and reference counts are read from the store.

## Dependencies And Integration Points
Used by `VolumesService.Get`, `List`, `Prune`, and `LocalVolumesSize`. Depends on directory size helper, filter args, API volume types, and store reference counting.

## Risks
`CreatedAt` errors are ignored. Size calculation may be expensive or fail; failures return `-1` size. `withPrune` mutates the provided filter args.

## Test Signals
`convert_test.go`, service tests, and Linux local-size tests cover prune filter mutation, API status/size behavior, and filter conversion effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/convert_test.go -->
# sources/cloud-native/moby/daemon/volume/service/convert_test.go

## Purpose
Unit tests for prune filter normalization.

## Important APIs, Types, And Functions
`TestFilterWithPrune` exercises `withPrune`.

## Control Flow
The test checks that empty filters gain the anonymous-volume label, existing labels are preserved and augmented, `all=1`/`all=true` disables anonymous-only injection, `all=0`/`false` keeps anonymous-only behavior, and invalid or repeated `all` values return invalid filter errors.

## State And Persistence
Only in-memory filter args are mutated.

## Dependencies And Integration Points
Uses daemon filter args and `AnonymousLabel`, feeding behavior used by `VolumesService.Prune`.

## Risks
Does not test `filtersToBy` directly or actual volume deletion; service tests cover those paths.

## Test Signals
Protects Docker prune compatibility: default prune targets anonymous volumes unless the user requests all volumes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/convert_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/db.go -->
# sources/cloud-native/moby/daemon/volume/service/db.go

## Purpose
BoltDB metadata persistence for volume name, driver, labels, and options.

## Important APIs, Types, And Functions
Defines `volumeBucketName`, `volumeMetadata`, and helpers `setMeta`, `getMeta`, `removeMeta`, and `listMeta` with store receiver wrappers.

## Control Flow
`setMeta` JSON-marshals metadata, creates the bucket if needed, and writes by volume name. `getMeta` reads the bucket and unmarshals when a value exists, returning zero metadata for missing keys. `removeMeta` deletes by key. `listMeta` iterates all bucket values during restore, skips empty values, logs malformed JSON, and returns valid metadata entries.

## State And Persistence
Persists metadata in `<root>/volumes/metadata.db` under the `volumes` bucket.

## Dependencies And Integration Points
Used by `VolumeStore.create`, `getVolume`, `purge`, `Remove`, and `restore`. Depends on bbolt and JSON.

## Risks
Store receiver methods assume `s.db` is non-nil; an in-memory store with empty root would panic if metadata methods are used. `removeMeta` assumes bucket exists. Corrupt metadata is logged and skipped during restore.

## Test Signals
`db_test.go` covers missing bucket behavior, zero metadata for missing key, and round-trip labels/options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/db_test.go -->
# sources/cloud-native/moby/daemon/volume/service/db_test.go

## Purpose
Unit tests for BoltDB volume metadata helpers.

## Important APIs, Types, And Functions
`TestSetGetMeta` opens a temporary Bolt database, constructs a `VolumeStore`, and exercises `getMeta`/`setMeta`.

## Control Flow
The test verifies `getMeta` errors when the bucket is absent, creates the bucket, verifies a missing key returns zero `volumeMetadata`, writes metadata with driver, labels, and options, and reads it back exactly.

## State And Persistence
Creates a temporary bbolt database file and closes it through `store.Shutdown`.

## Dependencies And Integration Points
Validates metadata persistence used by store create/restore paths.

## Risks
Does not test `removeMeta`, `listMeta`, corrupt JSON, or concurrent transactions.

## Test Signals
Good signal for JSON round-trip and missing metadata semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/default_driver.go -->
# sources/cloud-native/moby/daemon/volume/service/default_driver.go

## Purpose
Registers the built-in local volume driver during volume service startup on supported platforms.

## Important APIs, Types, And Functions
`setupDefaultDriver(store *drivers.Store, root string, rootIDs idtools.Identity) error` creates a local driver and registers it under `volume.DefaultDriverName`.

## Control Flow
The function calls `local.New(root, rootIDs)`, returns creation errors, and registers the resulting driver in the driver store.

## State And Persistence
Initializes the local driver's on-disk volume root and loads any existing local volumes through `local.New`.

## Dependencies And Integration Points
Called by `NewVolumeService`. Depends on the local driver, driver store, default driver name, and root identity.

## Risks
If registration fails due to an existing driver name, this implementation does not surface that boolean; local initialization errors are the main startup failure path.

## Test Signals
Service tests often construct stores manually; local driver behavior is covered by local package tests and Linux service size tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/default_driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/default_driver_stubs.go -->
# sources/cloud-native/moby/daemon/volume/service/default_driver_stubs.go

## Purpose
Platform stub for default driver setup where the local driver is not registered by this build.

## Important APIs, Types, And Functions
`setupDefaultDriver(_ *drivers.Store, _ string, _ idtools.Identity) error { return nil }`.

## Control Flow
No-op success.

## State And Persistence
No state is created or loaded.

## Dependencies And Integration Points
Maintains `NewVolumeService` compilation on platforms/build tags without the local driver setup implementation.

## Risks
Services on stub platforms will not have a default local driver unless registered elsewhere.

## Test Signals
Build success on covered platforms is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/default_driver_stubs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/errors.go -->
# sources/cloud-native/moby/daemon/volume/service/errors.go

## Purpose
Typed error definitions and operation wrapper for volume service/store failures.

## Important APIs, Types, And Functions
Defines `errVolumeInUse`, `errNoSuchVolume`, and `errNameConflict`; marker types `conflictError` and `notFoundError`; `OpErr` with `Error`, `Cause`, and `Unwrap`; classifiers `IsInUse`, `IsNotExist`, and `IsNameConflict`.

## Control Flow
Store methods wrap driver/store failures in `OpErr` with operation/name/ref context. Classifiers use `errors.Is` and legacy `Cause()` recursion to match typed sentinel errors through wrappers.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by API service methods to map internal errors to errdefs conflict/not-found responses and by tests to assert correct behavior.

## Risks
Error message formatting includes refs and is user-visible. Maintaining both `Unwrap` and legacy `Cause` support matters for existing error utilities.

## Test Signals
Store and service tests assert `IsInUse`, `IsNotExist`, `IsNameConflict`, conflict errdefs, and formatted operation errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/opts/opts.go -->
# sources/cloud-native/moby/daemon/volume/service/opts/opts.go

## Purpose
Functional option types for volume create, get, and remove operations.

## Important APIs, Types, And Functions
`CreateConfig` with `WithCreateLabel`, `WithCreateLabels`, `WithCreateOptions`, and `WithCreateReference`; `GetConfig` with `WithGetDriver`, `WithGetReference`, and `WithGetResolveStatus`; `RemoveConfig` with `WithPurgeOnError`.

## Control Flow
Each option mutates a config struct later consumed by `VolumesService` or `VolumeStore`. Label options initialize maps when needed, bulk setters assign map references directly, and reference options protect volumes from cleanup races.

## State And Persistence
No direct persistence. Options flow into store metadata labels/options and in-memory references.

## Dependencies And Integration Points
Used throughout service and store APIs and tests to attach labels/options/references, select drivers, request status, and purge stale metadata.

## Risks
Bulk label/options setters do not deep-copy maps at option application time; callers mutating maps later can affect stored values until copied/wrapped. `WithGetResolveStatus` has an unusual direct function signature matching `GetOption`.

## Test Signals
Store/service tests cover create labels/options/references, get driver/reference/status, and remove purge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/opts/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/restore.go -->
# sources/cloud-native/moby/daemon/volume/service/restore.go

## Purpose
Restores volume store in-memory state and plugin driver references from persisted metadata at daemon startup.

## Important APIs, Types, And Functions
`(s *VolumeStore) restore()` reads all `volumeMetadata` and repopulates names, labels, options, refs, and driver refcounts.

## Control Flow
The method reads metadata in a Bolt view, then launches one goroutine per metadata entry. Entries with a known driver call `lookupVolume`; missing volumes are queued for metadata removal, communication errors are logged. Entries without driver probe via `getVolume` and update metadata with the discovered driver. Existing volumes increment driver refcount through `CreateDriver` and are cached under global lock with empty refs. After workers complete, stale metadata is removed in one update transaction.

## State And Persistence
Reads and may update/remove entries in `metadata.db`. Rebuilds in-memory caches and plugin references, but does not restore per-container refs.

## Dependencies And Integration Points
Called by `NewStore`. Depends on Bolt metadata helpers, driver store, lookupVolume, and logging.

## Risks
Concurrent goroutines call store methods and metadata updates; lock ordering must avoid deadlocks. Errors from `CreateDriver` are ignored. Restored refs are empty by design, so live restore must reattach runtime references separately.

## Test Signals
`restore_test.go` verifies labels/options survive shutdown and new store initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/restore_test.go -->
# sources/cloud-native/moby/daemon/volume/service/restore_test.go

## Purpose
Unit test for volume metadata restoration after store restart.

## Important APIs, Types, And Functions
`TestRestore` creates a store, writes volumes with and without labels/options, shuts it down, creates a new store over the same root, and reads volumes back.

## Control Flow
The test registers a fake driver, creates `test1` with nil metadata and `test2` with labels/options, closes the store, reopens it, retrieves both volumes, and asserts `DetailedVolume` options/labels are nil for the first and equal to original maps for the second.

## State And Persistence
Persists data in temporary `metadata.db` and fake driver memory across store restarts.

## Dependencies And Integration Points
Validates `NewStore`, `restore`, metadata helpers, fake driver, and detailed volume wrapping.

## Risks
Does not cover stale metadata removal, missing drivers, plugin refcounts, or metadata entries without driver names.

## Test Signals
Strong signal that labels/options are not lost across daemon store restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/restore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/service.go -->
# sources/cloud-native/moby/daemon/volume/service/service.go

## Purpose
High-level volume API service used by daemon handlers, wrapping `VolumeStore`, driver listing, event logging, API conversion, prune, and live restore.

## Important APIs, Types, And Functions
`VolumesService` contains `VolumeStore`, driver lister, prune-running flag, and event logger. Methods include `NewVolumeService`, `GetDriverList`, `Create`, `Get`, `Mount`, `Unmount`, `Release`, `Remove`, `LocalVolumesSize`, `Prune`, `List`, `Shutdown`, and `LiveRestoreVolume`. `AnonymousLabel` marks generated anonymous volumes.

## Control Flow
Startup creates a driver store, registers default local driver, and creates a metadata-backed store. `Create` generates anonymous IDs and labels when name is empty, delegates to store, and converts to API type. `Get` optionally resolves driver status. `Mount`/`Unmount` look up by API volume name/driver and call underlying volume. `Remove` maps not-found/in-use to API-friendly behavior. `Prune` serializes concurrent prunes with an atomic flag, normalizes filters, finds unreferenced local volumes without options, computes reclaim size, removes each, and emits a prune event. `List` converts filtered volumes using cached paths.

## State And Persistence
Service mutates store metadata and driver volume state through delegated calls. `pruneRunning` is in-memory concurrency state.

## Dependencies And Integration Points
Integrates API volume types/events, filters, directory sizing, driver store/plugin getter, local driver setup, idtools, and error mapping.

## Risks
Prune intentionally skips non-local and option-backed local volumes. Size calculation before remove can race with filesystem changes. Event logger is assumed non-nil in prune paths. API conversion may use cached mountpoints for list.

## Test Signals
Service tests cover create conflicts, list filters, remove purge, get status/driver conflicts, prune filters, and local volume size.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/service_linux_test.go -->
# sources/cloud-native/moby/daemon/volume/service/service_linux_test.go

## Purpose
Linux-specific API service test for local volume size reporting.

## Important APIs, Types, And Functions
`TestLocalVolumeSize` exercises `VolumesService.LocalVolumesSize`.

## Control Flow
The test creates a real local driver, registers it as the default driver plus a fake driver, creates two local volumes and one fake volume, writes different data sizes into local mountpoints, requests local sizes, and asserts only the two local volumes are returned with expected sizes and reference counts.

## State And Persistence
Uses temporary local volume directories and writes test data files.

## Dependencies And Integration Points
Validates service conversion, local driver, store references, directory size calculation, and filtering of non-local drivers.

## Risks
Directory size calculations can vary with filesystem behavior, but the test uses simple file contents to keep expectations stable.

## Test Signals
Good signal for `LocalVolumesSize` filtering and usage data population.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/service_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/service_test.go -->
# sources/cloud-native/moby/daemon/volume/service/service_test.go

## Purpose
Unit tests for high-level `VolumesService` behavior.

## Important APIs, Types, And Functions
Tests cover `Create`, `List`, `Remove`, `Get`, `Prune`, and test service construction with `dummyEventLogger`.

## Control Flow
Create tests verify unknown driver not-found, idempotent same-driver create, cross-driver name conflict, and recreate after remove. List tests cover driver and dangling filters with references. Remove tests cover normal removal and purge-on-error not-found. Get tests cover missing volumes, status resolution, driver conflict, and correct driver matching. Prune tests cover label/all filters, default local-only behavior, non-local preservation, anonymous-label defaulting, label exclusion, and referenced volume preservation.

## State And Persistence
Uses temporary metadata stores and fake drivers; no real local driver except in Linux-specific test.

## Dependencies And Integration Points
Exercises service, store, filters, options, error classification, event logging interface, and fake drivers.

## Risks
Event logger output is not asserted. Prune size accounting is not deeply validated here; Linux size test covers usage data separately.

## Test Signals
Strong API-level signal for conflict semantics, filter conversion, reference-aware pruning, and status retrieval.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store.go -->
# sources/cloud-native/moby/daemon/volume/service/store.go

## Purpose
Core metadata-backed volume store handling driver lookup, creation, removal, listing, reference counting, filtering, restore, and cache consistency.

## Important APIs, Types, And Functions
`VolumeStore` owns per-name locks, global maps (`names`, `refs`, `labels`, `options`), driver store, Bolt DB, and event logger. `volumeWrapper` adds labels/options/scope/cached path/live restore. Important methods include `NewStore`, `Find`, `list`, `Create`, `checkConflict`, `create`, `Get`, `getVolume`, `Remove`, `Release`, `CountReferences`, `purge`, and `Shutdown`.

## Control Flow
`NewStore` initializes maps, opens metadata DB if root is set, creates the bucket, and restores metadata. `Find` interprets `By` filters, lists drivers in parallel, merges cached volumes from failed drivers, and removes cross-driver name conflicts. `Create` normalizes/locks the name, validates with the platform parser, checks cached conflict/staleness, probes existing volumes when driver unspecified, acquires driver ref, creates through the driver if needed, records labels/options/empty refs, and persists metadata. `Get` uses metadata/driver hints/cache/all-driver probing, updates missing driver metadata, and attaches optional references. `Remove` rejects referenced volumes, resolves the latest volume, removes via driver, purges metadata/cache on success or forced purge, and emits destroy events. `Release` removes refs under locks.

## State And Persistence
Persistent state is Bolt metadata; driver backends own actual volumes. In-memory state caches names, refs, labels, options, and plugin refs. `purge` deletes metadata and releases driver refs.

## Dependencies And Integration Points
Used by `VolumesService` and `MountPoint` consumers. Integrates driver store/plugin refs, mount parser volume-name validation, bbolt metadata, event logging, and error wrappers.

## Risks
Lock ordering between per-name locks and globalLock is critical. Plugin driver refcounts must balance create/remove/purge/error paths. Metadata can become stale relative to external plugins, so conflict checks and purge behavior are delicate. `Shutdown` assumes `db` is non-nil.

## Test Signals
Store tests cover create/remove/list/restore, driver filters, references, stale refs, plugin dereference on error, get with reference, and filter function behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store_test.go -->
# sources/cloud-native/moby/daemon/volume/service/store_test.go

## Purpose
Unit tests for `VolumeStore` creation, removal, listing, filtering, references, plugin reference cleanup, and get behavior.

## Important APIs, Types, And Functions
Tests include `TestCreate`, `TestRemove`, `TestList`, `TestFindByDriver`, `TestFindByReferenced`, `TestDerefMultipleOfSameRef`, `TestCreateKeepOptsLabelsWhenExistsRemotely`, `TestDefererencePluginOnCreateError`, `TestRefDerefRemove`, `TestGet`, `TestGetWithReference`, and `TestFilterFunc`.

## Control Flow
Tests register fake drivers, create volumes with labels/options/references, assert unknown driver and driver create errors, remove referenced/unreferenced volumes, verify persistence across store restart, filter by driver/dangling, release duplicate refs, preserve labels for remotely existing volumes, ensure plugin acquire refs are released after create error, and validate slice filtering cases.

## State And Persistence
Uses temporary Bolt metadata stores, fake in-memory drivers, and a fake HTTP plugin server for reference-count behavior.

## Dependencies And Integration Points
Exercises store, driver store, plugin adapter path, options, fake drivers/plugins, error wrappers, and cmp rules for wrapped volumes.

## Risks
Fake drivers are simpler than real plugins and do not cover slow/unavailable plugin list behavior. Some tests rely on string comparisons for driver-originated errors.

## Test Signals
Broad regression signal for store correctness, especially reference protection and plugin refcount cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store_unix.go -->
# sources/cloud-native/moby/daemon/volume/service/store_unix.go

## Purpose
Unix volume-name normalization hook.

## Important APIs, Types, And Functions
`normalizeVolumeName(name string) string` returns the input unchanged.

## Control Flow
No conditional logic.

## State And Persistence
No state.

## Dependencies And Integration Points
Called by `VolumeStore.Create`, `Get`, and `CountReferences` before locking/cache access.

## Risks
Unix volume names are case-sensitive. Any future normalization would affect persisted metadata keys and compatibility.

## Test Signals
Store tests on Unix implicitly validate unchanged names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store_windows.go -->
# sources/cloud-native/moby/daemon/volume/service/store_windows.go

## Purpose
Windows volume-name normalization hook.

## Important APIs, Types, And Functions
`normalizeVolumeName(name string) string` lowercases names.

## Control Flow
The function delegates to `strings.ToLower`.

## State And Persistence
No state, but normalized names become lock keys, cache keys, and metadata keys.

## Dependencies And Integration Points
Used by `VolumeStore` operations to make Windows volume names case-insensitive.

## Risks
Lowercasing can collapse distinct names if external drivers preserve case differently. Metadata compatibility depends on consistent normalization.

## Test Signals
Windows store behavior is indirectly covered by platform test runs; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/service/store_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/testutils/testutils.go -->
# sources/cloud-native/moby/daemon/volume/testutils/testutils.go

## Purpose
Test utilities for volume, driver, plugin, and plugin getter fakes.

## Important APIs, Types, And Functions
Provides `NoopVolume`, `FakeVolume`, `NewFakeVolume`, `FakeDriver`, `NewFakeDriver`, `MakeFakePlugin`, `NewFakePluginGetter`, and `FakeRefs`.

## Control Flow
Fake volumes return fixed paths/status and creation times. `FakeDriver` stores volumes in a map, supports create/remove/list/get, and can return a configured create error through the `opts["error"]` key. `MakeFakePlugin` creates a plugin client/server pair with a `VolumeDriver.Create` handler. `fakePluginGetter.Get` returns plugins by name and increments refs by the requested mode.

## State And Persistence
All state is in-memory maps, fake plugin refs, and an HTTP listener for plugin tests.

## Dependencies And Integration Points
Used by driver, store, and service tests to avoid real volume drivers/plugins. Implements Moby plugin compatibility interfaces.

## Risks
The fake plugin only implements create, so tests needing other plugin RPCs must extend it. `FakeRefs` panics for non-fake plugins by design. Fake driver errors are untyped strings.

## Test Signals
Enables tests for reference counting, create errors, filtering, labels/status conversion, and plugin adapter paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/testutils/testutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/volume.go -->
# sources/cloud-native/moby/daemon/volume/volume.go

## Purpose
Defines daemon volume interfaces and shared constants for driver/volume implementations.

## Important APIs, Types, And Functions
`DefaultDriverName` is `local`. Scopes are `LocalScope` and `GlobalScope`. Interfaces are `Driver`, `Volume`, optional `LiveRestorer`, and `DetailedVolume`. `Capability` carries driver scope.

## Control Flow
No runtime logic; this is an interface contract file.

## State And Persistence
No state. Implementations such as local driver and plugin adapters provide persistence and runtime behavior.

## Dependencies And Integration Points
Implemented by local volumes, plugin adapters, wrappers, and test fakes. Consumed by driver store, volume store/service, mount setup, and API conversion.

## Risks
Interface changes have a wide blast radius across daemon drivers, plugins, tests, and persisted mountpoint behavior. Scope values influence swarm/cluster handling and plugin validation.

## Test Signals
Compilation plus broad service/store/local/driver tests validate that implementations satisfy the contracts. `volumeWrapper` and `localVolume` explicitly assert optional live restore support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/volume/volume.go -->
