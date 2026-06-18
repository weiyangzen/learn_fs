# subset-b-000089 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_test.go

## Purpose
Exercises the factory-level container object that builds OCI specs from CRI container and pod sandbox input. The tests document expected behavior for mounts, annotations, image command resolution, privilege/capability setup, Linux resources, SELinux label generation, read-only and restore flags, and systemd detection.

## Important APIs, Types, And Functions
- Uses the package-level `sut container.Container` from `suite_test.go`, especially `SetConfig`, `Spec`, `SpecAddMount`, `SpecAddAnnotations`, `DisableFips`, `UserRequestedImage`, `ReadOnly`, `SetRestore`, `SelinuxLabel`, `AddUnifiedResourcesFromAnnotations`, `SpecSetProcessArgs`, `WillRunSystemd`, `SpecSetupCapabilities`, `SpecSetPrivileges`, and `SpecSetLinuxContainerResources`.
- Builds CRI `types.ContainerConfig` and `types.PodSandboxConfig`, OCI `rspec` mounts/resources, image-spec `v1.Image`, CRI-O `sandbox.Builder`, and storage image reference objects.
- Uses CRI-O annotation constants as the contract for `SpecAddAnnotations`.

## Control Flow
Each Ginkgo `Describe` block sets up minimal CRI input, calls a single container factory method, and asserts the resulting OCI generator state. Annotation tests construct a realistic sandbox, image result, log path, metadata JSON, and volume JSON before validating every generated annotation. Process argument tests cover command, args, image entrypoint/cmd inheritance, and empty-command failure. Capability tests cover add/drop semantics including `ALL`, invalid capability names, inheritable propagation, and privileged all-capability setup.

## State And Persistence
The tests do not persist data to disk, but they verify state mutations inside the in-memory OCI spec generator: mounts are de-duplicated, annotations are populated, process args/capabilities/resources are written, unified cgroup entries are stored under `Linux.Resources.Unified`, and restore/read-only/FIPS decisions are derived from config state. The annotation test also validates that serialized CRI metadata/labels/volumes/annotations survive as JSON strings in the OCI spec.

## Dependencies And Integration Points
Integrates factory code with CRI API types, OCI runtime spec generation, image metadata, CRI-O storage reference parsing, sandbox builder output, kubelet labels, CRI-O annotation packages, hostport port mapping types, and Linux capability discovery from `moby/sys/capability`.

## Risks And Edge Cases
The suite highlights risks around missing image specs, invalid/empty process command resolution, invalid capability names, capability ordering/count assumptions, cgroup v2 unified resource decoding, minimum memory enforcement, swap less than memory, and annotation correctness for downstream OCI/runtime consumers. Some expectations depend on host capability discovery and runtime-spec defaults.

## Test Signals
This file is itself the primary signal for the factory container behavior. It asserts broad positive and negative paths and should catch regressions in OCI spec annotations, command resolution, resource validation, privilege handling, and default behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_freebsd.go -->
# sources/cloud-native/cri-o/internal/factory/container/device_freebsd.go

## Purpose
Provides FreeBSD-specific stubs for container device setup. Device addition is a no-op on FreeBSD, while CDI injection is unsupported unless no CDI devices were requested.

## Important APIs, Types, And Functions
- `(*container).SpecAddDevices(configuredDevices, annotationDevices []devicecfg.Device, privilegedWithoutHostDevices, enableDeviceOwnershipFromSecurityContext bool) error` returns nil without mutating the spec.
- `(*container).SpecInjectCDIDevices() error` returns an unsupported-platform error only when `c.Config().CDIDevices` is non-empty.

## Control Flow
FreeBSD callers can invoke the same factory API as Linux code, but no Linux device nodes or cgroup device resources are added. CDI is treated as a conditional feature: empty CDI input succeeds, requested CDI input fails with a message including `runtime.GOOS`.

## State And Persistence
No state is persisted and no OCI device state is changed. The only observable behavior is error/no-error selection based on requested CDI devices.

## Dependencies And Integration Points
Keeps the common container factory interface buildable on FreeBSD while importing only `devicecfg`, `runtime`, and `fmt`. It avoids Linux-only runc device and CDI injection behavior.

## Risks And Edge Cases
FreeBSD callers expecting CRI device mappings to be enforced will get a silent no-op. CDI requests are rejected, but ordinary configured device lists are accepted without effect.

## Test Signals
No dedicated FreeBSD test is in this subset; coverage is primarily compile-time platform selection plus common factory interface expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_linux.go -->
# sources/cloud-native/cri-o/internal/factory/container/device_linux.go

## Purpose
Implements Linux OCI device setup for containers, including configured CRI-O devices, annotation devices, privileged host-device exposure, CRI container device requests, directory-of-devices expansion, device ownership from security context, and CDI injection.

## Important APIs, Types, And Functions
- `SpecAddDevices` clears existing Linux devices, adds configured and annotation devices plus resource cgroup permissions, optionally adds all host devices for privileged containers, then applies CRI container `Devices`.
- `specAddHostDevicesIfPrivileged` imports `devices.HostDevices()` and grants blanket `rwm` cgroup access for privileged containers unless `privilegedWithoutHostDevices` is set.
- `specAddContainerConfigDevices` resolves host paths securely, calls `devices.DeviceFromPath`, maps to container paths, appends matching `LinuxDeviceCgroup` entries, and recursively walks directories containing device nodes.
- `SpecInjectCDIDevices` merges CRI `CDIDevices` and CDI annotation requests, skips duplicates from annotations, refreshes the CDI registry, and calls `cdi.InjectDevices`.
- `getDeviceUserGroupID` optionally replaces host UID/GID with non-root `RunAsUser`/`RunAsGroup`.

## Control Flow
Device addition starts by resetting `Spec().Config.Linux.Devices`, so each call reconstructs the device list. Static configured and annotation devices are added first. Privileged containers then receive host devices and a broad resources device allow rule. Finally CRI devices are validated: privileged containers using a different container path must not collide with an existing host path, host paths are secure-joined under `/`, device nodes are added directly, and non-device directories are walked for child device nodes. CDI injection separately gathers device names from the structured CRI field and legacy annotations, refreshes registry state best-effort, then injects CDI-provided spec edits.

## State And Persistence
Mutates the in-memory OCI spec generator: `Linux.Devices`, `Linux.Resources.Devices`, environment, mounts, hooks, and other CDI edits may be changed. No durable state is written here. CDI registry state is refreshed through the external CDI library, and later factory call ordering must preserve the edits made by CDI.

## Dependencies And Integration Points
Depends on runc/libcontainer device discovery, OCI runtime-spec types, CRI API security context, CRI-O device config, `securejoin`, CRI-O `utils.IsDirectory`, CRI-O logging, and the CNCF CDI library. It integrates with kubelet CRI device requests and runtime-spec cgroup device controls.

## Risks And Edge Cases
Resetting `Linux.Devices` discards previous device edits. Privileged host-device import can expose broad host device access. Directory walking ignores errors and silently skips non-device children. `strings.Replace` assumes child paths are under the source directory. Device ownership override applies only for non-root IDs and only when enabled. CDI refresh errors are only logged, so invalid spec files may surface later during injection. CDI edits may be lost if callers reset OCI spec fields after injection.

## Test Signals
`device_test.go` covers privileged host devices, `privilegedWithoutHostDevices`, security-context device ownership, invalid CDI references, missing CDI devices, valid CDI injection through CRI fields and annotations, and expected injected env/device nodes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/device_test.go

## Purpose
Tests Linux device handling in the container factory, including host-device exposure policy, device node ownership, and CDI device injection from both structured CRI fields and legacy annotations.

## Important APIs, Types, And Functions
- Exercises `sut.SpecAddDevices` and `sut.SpecInjectCDIDevices`.
- Uses `devices.HostDevices()` to choose real host device fixtures and `types.ContainerConfig.Devices` for CRI device requests.
- Defines `writeCDISpecFiles` to create temporary CDI YAML specs and configure the CDI registry for each test.

## Control Flow
The first table toggles privileged state and `privilegedWithoutHostDevices` to assert whether host devices are copied into the spec. The second table builds a single CRI device request from an actual host device and checks UID/GID selection with or without `deviceOwnershipFromSecurityContext`. The CDI table writes optional CDI spec files, configures container annotations or `CDIDevices`, calls injection, and verifies either errors or expected env/device edits.

## State And Persistence
Uses temporary CDI spec directories and mutates the package-global CDI registry configuration during tests. The OCI spec generator records injected devices and process environment entries. No CRI-O persistent container state is written.

## Dependencies And Integration Points
Integrates runc device discovery, CRI API security contexts and CDI fields, runtime-spec Linux devices, and the CNCF CDI registry/parser. It relies on the shared test framework and the factory `sut` initialized in `suite_test.go`.

## Risks And Edge Cases
Tests depend on host device availability and on at least one host device for ownership assertions. CDI registry global state can leak if not reset by framework/process isolation. Root-owned devices and equal UID/GID devices are handled by fallback selection logic.

## Test Signals
Strong signal for host-device policy and CDI behavior. It covers nil/empty CDI input, malformed CDI names, unresolved devices, successful multi-vendor injection, annotation-based injection, and expected device/env edits.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_unsupported.go -->
# sources/cloud-native/cri-o/internal/factory/container/device_unsupported.go

## Purpose
Provides device API implementations for platforms that are neither Linux nor FreeBSD. It rejects general device setup and conditionally rejects CDI injection when devices are requested.

## Important APIs, Types, And Functions
- `SpecAddDevices` always returns an unsupported-platform error containing `runtime.GOOS`.
- `SpecInjectCDIDevices` succeeds for empty CDI input and errors for non-empty `c.Config().CDIDevices`.

## Control Flow
The file is gated by `//go:build !linux && !freebsd`. Common factory callers can compile on unsupported platforms but cannot successfully add CRI-O/CRI devices. CDI is only tolerated when there is nothing to inject.

## State And Persistence
No state is changed. It does not mutate the OCI spec or persist anything.

## Dependencies And Integration Points
Maintains API parity for cross-platform builds while avoiding Linux and FreeBSD-specific imports. It imports only the CRI-O device config type plus `fmt` and `runtime`.

## Risks And Edge Cases
Configured devices fail fast on unsupported platforms, unlike FreeBSD where they are a no-op. Only structured CDI device requests are checked; legacy annotation CDI behavior is not parsed here.

## Test Signals
No direct tests in this subset. Build tags and compile coverage are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/device_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces.go -->
# sources/cloud-native/cri-o/internal/factory/container/namespaces.go

## Purpose
Exposes the managed PID namespace associated with a container factory object after target-PID namespace setup.

## Important APIs, Types, And Functions
- `(*container).PidNamespace() nsmgr.Namespace` returns the `c.pidns` field.

## Control Flow
There is no branching. Linux `SpecAddNamespaces` may set `c.pidns` when `NamespaceMode_TARGET` is requested, and this accessor exposes it to callers/tests for cleanup or inspection.

## State And Persistence
No persistence occurs. It reads in-memory container factory state. The returned namespace may represent a managed namespace requiring removal by the caller.

## Dependencies And Integration Points
Depends on `internal/config/nsmgr.Namespace`. Used by namespace tests to verify and clean up target PID namespaces.

## Risks And Edge Cases
May return nil when no target PID namespace was configured. Callers must guard nil and must not assume ownership unless the namespace was created by the namespace manager.

## Test Signals
`namespaces_test.go` checks that `PidNamespace()` becomes non-nil for target PID namespace mode and uses it for cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces_freebsd.go -->
# sources/cloud-native/cri-o/internal/factory/container/namespaces_freebsd.go

## Purpose
Implements FreeBSD namespace handling by translating the sandbox network namespace path into a FreeBSD jail annotation.

## Important APIs, Types, And Functions
- `(*container).SpecAddNamespaces(sb SandboxIFace, targetCtr *oci.Container, serverConfig *config.Config) error` iterates sandbox managed namespaces and adds `org.freebsd.parentJail` for the network namespace.

## Control Flow
The method retrieves `sb.NamespacePaths()`, scans for `nsmgr.NETNS`, and writes the namespace path into the OCI spec annotations. Target PID containers and server config are unused on FreeBSD.

## State And Persistence
Mutates only the in-memory OCI spec annotations. The annotation names the parent jail used by downstream FreeBSD runtime handling.

## Dependencies And Integration Points
Integrates sandbox namespace metadata with the OCI spec generator through FreeBSD jail conventions. It depends on CRI-O namespace manager types and common `SandboxIFace`.

## Risks And Edge Cases
Only the network namespace is represented. Multiple network namespace entries would result in repeated annotation writes with the last value winning. Empty paths are not filtered here.

## Test Signals
No FreeBSD-specific test appears in this subset; behavior is compile-time platform-specific.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces_linux.go -->
# sources/cloud-native/cri-o/internal/factory/container/namespaces_linux.go

## Purpose
Configures Linux OCI namespaces for a container based on pod sandbox namespace paths and CRI namespace options, including host network/PID, pod PID namespace, and target-container PID namespace.

## Important APIs, Types, And Functions
- `SpecAddNamespaces(sb SandboxIFace, targetCtr *oci.Container, serverConfig *config.Config) error` is the main Linux namespace mutator.
- `ConfigureGeneratorGivenNamespacePaths(managedNamespaces []*namespace.ManagedNamespace, g *generate.Generator) error` maps CRI-O namespace manager types to OCI namespace types and adds/replaces generator namespaces.

## Control Flow
The method first joins all non-empty sandbox-managed namespace paths into the OCI generator. It then inspects container security context namespace options. Host network removes the OCI network namespace. Host PID removes the PID namespace. Pod PID requires a valid sandbox PID namespace path and replaces the OCI PID namespace with it. Target PID requires a target container, resolves its PID, asks the namespace manager for a PID namespace from `/proc`, sets that path in the spec, and stores the managed namespace in `c.pidns`.

## State And Persistence
Mutates `generate.Generator.Config.Linux.Namespaces` and may store a managed PID namespace in the container object. The managed namespace can imply filesystem state in the namespace manager, but this file itself does not write persistent files.

## Dependencies And Integration Points
Depends on CRI API namespace modes, OCI runtime-spec namespace types, runtime-tools generator APIs, CRI-O namespace manager, sandbox namespace metadata, target OCI containers, and server config namespace manager. It is part of container creation before runtime handoff.

## Risks And Edge Cases
`ConfigureGeneratorGivenNamespacePaths` indexes a map of supported namespace types and errors on unknown types. Empty namespace paths are skipped. Pod PID mode errors if the sandbox was not similarly configured or has no valid infra PID namespace path. Target PID mode errors on nil target, PID lookup failure, namespace-manager failure, or generator update failure. The caller must later remove `c.pidns`.

## Test Signals
`namespaces_test.go` covers inherited sandbox namespaces, host-network removal, host-PID removal, pod PID namespace replacement, target PID namespace creation, and empty path skipping.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/namespaces_test.go

## Purpose
Tests Linux namespace configuration for the factory container, documenting how pod sandbox namespaces and CRI namespace options alter the OCI spec.

## Important APIs, Types, And Functions
- Exercises `sut.SpecAddNamespaces` and `sut.PidNamespace`.
- Uses `sandbox.Sandbox`, `nsmgrtest.AllSpoofedNamespaces`, `nsmgrtest.ContainerWithPid`, and `config.Config.NamespaceManager`.
- Uses CRI `types.NamespaceOption` modes and OCI `rspec` namespace constants.

## Control Flow
Tests create container configs with namespace options, attach spoofed namespace paths to a sandbox, clear default generator namespaces, call `SpecAddNamespaces`, and inspect resulting `spec.Config.Linux.Namespaces`. Target PID mode initializes a real namespace manager, resolves the current process as the target container, and verifies the stored managed PID namespace path.

## State And Persistence
Most tests mutate only the OCI generator. The target PID test creates namespace-manager state under a temp directory and defers removal of the managed namespace returned by `sut.PidNamespace()`.

## Dependencies And Integration Points
Integrates CRI namespace modes with CRI-O sandbox and namespace manager test helpers. The target PID path depends on Linux `/proc` and is skipped when running rootless because namespace operations require privileges.

## Risks And Edge Cases
Test coverage highlights host namespace removal, empty managed namespace path skipping, sandbox PID misconfiguration risk, and target PID cleanup requirements. The host-PID expectation is sensitive to default namespace entries and spoofed namespace fixture contents.

## Test Signals
Strong signal for Linux namespace behavior. It covers success and important mode-dependent transformations, including the privileged target PID path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/namespaces_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/sandbox.go -->
# sources/cloud-native/cri-o/internal/factory/container/sandbox.go

## Purpose
Defines the narrow sandbox interface needed by the container factory so factory code can consume sandbox information without importing the full sandbox implementation package.

## Important APIs, Types, And Functions
- `SandboxIFace` exposes log directory, annotations, ID/name, resolv path, IPs, managed namespace paths, PID namespace path, and CRI namespace options.

## Control Flow
This file declares an interface only. Runtime behavior is supplied by concrete sandbox objects implementing these methods.

## State And Persistence
No state is held or persisted. Interface methods expose state from sandbox implementations.

## Dependencies And Integration Points
Uses CRI namespace option types and CRI-O `internal/lib/namespace.ManagedNamespace`. The interface is consumed by annotation setup, namespace setup, and other factory operations that need pod sandbox metadata.

## Risks And Edge Cases
Because it is intentionally narrow, future factory methods needing more sandbox data must extend this interface. Implementations must preserve semantics such as empty PID namespace path meaning no infra namespace is available.

## Test Signals
Indirectly tested wherever sandbox builder or sandbox instances are passed to factory methods in `container_test.go` and `namespaces_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/suite_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/suite_test.go

## Purpose
Bootstraps the Ginkgo/Gomega test suite for `internal/factory/container` and provides shared test framework state plus a fresh container factory subject for each test.

## Important APIs, Types, And Functions
- `TestContainer(t *testing.T)` registers Gomega fail handling and runs framework specs.
- Package globals `t *TestFramework` and `sut container.Container` are used by tests.
- `BeforeSuite`, `AfterSuite`, and `BeforeEach` manage framework setup/teardown and recreate `sut` via `container.New()`.

## Control Flow
Before the suite, a CRI-O test framework is created with no-op setup/teardown callbacks and initialized. After the suite it is torn down. Before every spec, the shared `sut` is replaced with a newly constructed container.

## State And Persistence
Maintains package-global test state. Temporary files or directories are managed by `TestFramework` helpers in individual tests; this file itself does not persist state.

## Dependencies And Integration Points
Integrates ONSI Ginkgo/Gomega with CRI-O's `test/framework` and the factory container constructor.

## Risks And Edge Cases
All tests rely on `sut` being fresh per test; if a test mutates package-level external state such as CDI configuration, this suite setup alone may not reset it.

## Test Signals
Failure here would prevent the whole factory container test suite from running. It provides no product assertions itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/fake_iptables.go -->
# sources/cloud-native/cri-o/internal/hostport/fake_iptables.go

## Purpose
Implements an in-memory `internal/iptables.Interface` used by hostport tests to simulate iptables chain/rule operations, save/restore output, protocol selection, and builtin-chain behavior.

## Important APIs, Types, And Functions
- `fakeIPTables`, `fakeTable`, and `fakeChain` model tables, chains, and rule lists.
- `newFakeIPTables`, `EnsureChain`, `FlushChain`, `DeleteChain`, `ChainExists`, `EnsureRule`, `DeleteRule`, `SaveInto`, `Restore`, `RestoreAll`, `Protocol`, `IsIPv6`, `Present`, and `HasRandomFully` satisfy the iptables interface.
- Helpers `normalizeRule`, `findRule`, `saveChain`, `restore`, and `isBuiltinChain` implement test semantics close to real iptables.

## Control Flow
Chain and rule operations lazily create missing chains as needed. Rules are normalized before insertion to mimic iptables behavior for `--to-destination`, quoted comments, and IP CIDR suffixes. `SaveInto` writes iptables-save style table, chain, and `-A` rule lines. `restore` parses iptables-restore data table-by-table, creates chain lines, appends or prepends rules, deletes chains, flushes non-builtin user chains unless they are being deleted, and honors table filtering.

## State And Persistence
All state lives in maps and slices inside `fakeIPTables`. There is no disk persistence. Restore operations mutate the in-memory tables in a way tests can later inspect through `SaveInto` or direct map access.

## Dependencies And Integration Points
Implements CRI-O's vendored Kubernetes iptables abstraction for hostport unit tests. Uses Kubernetes set utilities and IP family helpers for normalization.

## Risks And Edge Cases
The fake is not a complete iptables parser. It splits restore lines simplistically, supports only the operations needed by tests, and normalizes comments/IP addresses in ways tailored to assertions. Divergence from real iptables can hide production bugs or create false failures when command formatting changes.

## Test Signals
`fake_iptables_test.go`, `hostport_iptables_test.go`, and `meta_hostport_manager_test.go` exercise save/restore, chain cleanup, IPv4/IPv6 rule generation, and legacy cleanup behavior through this fake.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/fake_iptables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/fake_iptables_test.go -->
# sources/cloud-native/cri-o/internal/hostport/fake_iptables_test.go

## Purpose
Validates fake iptables restore behavior needed by hostport tests, especially no-flush restore semantics for user-defined versus builtin chains.

## Important APIs, Types, And Functions
- Exercises `newFakeIPTables`, `EnsureChain`, internal `ensureRule`, `writeLine`, `MakeChainLine`, and `Restore`.

## Control Flow
The test creates a fake NAT table with a hostport user chain and a builtin `POSTROUTING` rule, builds a restore payload containing only chain declarations and `COMMIT`, then calls `Restore` with `NoFlushTables`. It asserts the user-defined `KUBE-HOSTPORTS` chain is flushed while builtin `POSTROUTING` keeps its rule.

## State And Persistence
Mutates only fake in-memory table state. No durable persistence.

## Dependencies And Integration Points
Confirms the fake's behavior matches the assumptions of `hostport_iptables.go` tests that rebuild hostport user chains while preserving unrelated builtin chain rules.

## Risks And Edge Cases
The test covers one restore scenario; other parser branches such as `-I`, `-X`, malformed rules, and table filtering are covered indirectly by hostport tests.

## Test Signals
Good targeted signal that fake restore cleanup semantics are sufficient for hostport manager tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/fake_iptables_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_iptables.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_iptables.go

## Purpose
Implements the iptables backend for CRI-O hostport mappings. It creates per-pod/per-port NAT chains for DNAT and hairpin masquerade, preserves unrelated hostport state, and removes matching chains atomically through iptables-restore.

## Important APIs, Types, And Functions
- Constants define `KUBE-HOSTPORTS`, `KUBE-HP-*`, `CRIO-HOSTPORTS-MASQ`, and `CRIO-MASQ-*` chain names.
- `hostportManagerIPTables` wraps `utiliptables.Interface` plus a mutex.
- `newHostportManagerIPTables`, `Add`, `Remove`, `syncIPTables`, `ensureKubeHostportChains`, `getHostportChain`, `getExistingHostportIPTablesRules`, `getChainLines`, `readLine`, `filterRules`, `filterChains`, and `writeLine` implement backend behavior.

## Control Flow
`Add` ensures base hostport and masquerade chains, locks, reads current NAT hostport chains/rules, builds new chain declarations and insertion rules for every mapping, adds DNAT rules optionally constrained by `HostIP`, adds hairpin MASQUERADE rules, filters out old copies of the same chains, appends remaining existing hostport state, and restores the composed NAT table. `Remove` locks, computes target chain names from mappings, filters out rules mentioning those chains, emits existing chain declarations, emits `-X` deletes for existing target chains, and restores. Chain names are stable SHA-256/base32 hashes of sandbox ID, host port, protocol, and host IP.

## State And Persistence
Persists hostport behavior in kernel iptables NAT tables. It reads current state through `iptables-save` and writes through `iptables-restore --noflush --counters`. The manager mutex serializes operations within the process; iptables package handles command-level locking.

## Dependencies And Integration Points
Uses CRI-O internal iptables abstraction, Kubernetes-derived rule formatting, `net.JoinHostPort` for IPv6-safe destinations, and CRI hostport `PortMapping`. It is selected by `meta_hostport_manager.go` when nftables is unavailable or for legacy cleanup.

## Risks And Edge Cases
Changing `getHostportChain` breaks cleanup of existing rules. Rule filtering uses substring matching on chain names, so chain-name uniqueness matters. `getChainLines` can panic on malformed chain lines without spaces. Broad hostport jump rules must remain ordered behind kube-services assumptions. HostIP wildcard handling only recognizes empty, `0.0.0.0`, and `::`. Atomicity is limited to composed restore plus process mutex.

## Test Signals
`hostport_iptables_test.go` validates base chain setup, hash uniqueness, IPv4/IPv6 DNAT/SNAT rule generation, hostIP-specific rules, same host port on different IPs/protocols, and removal back to an empty hostport rule set.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_iptables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_iptables_test.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_iptables_test.go

## Purpose
Tests iptables hostport rule construction and cleanup using the in-memory fake iptables backend.

## Important APIs, Types, And Functions
- Defines expected IPv4 and IPv6 hostport rule sets.
- `checkIPTablesRules` compares hostport-related `iptables-save` output against expected sets.
- Exercises `ensureKubeHostportChains`, `getHostportChain`, `hostportManagerIPTables.Add`, and `hostportManagerIPTables.Remove`.

## Control Flow
Tests first verify base chains and jump rules, then validate hash-derived chain names are distinct for different ports/prefixes. IPv4 and IPv6 tests instantiate fake managers, add all shared test cases, compare generated `KUBE-HOSTPORTS`, `CRIO-HOSTPORTS-MASQ`, `KUBE-HP-*`, and `CRIO-MASQ-*` rules, remove all mappings, and assert no hostport rules remain.

## State And Persistence
Mutates fake in-memory NAT tables. Expected rule arrays document the persistent kernel state that real iptables would receive.

## Dependencies And Integration Points
Depends on shared `testCasesV4`/`testCasesV6`, fake iptables normalization, Kubernetes sets for comparison, and CRI-O iptables constants/types.

## Risks And Edge Cases
Expected rules are intentionally exact and may fail on harmless ordering/formatting changes unless the comparison remains set-based. Hash outputs are pinned, which protects cleanup compatibility but makes intended hash changes disruptive.

## Test Signals
Strong regression signal for iptables rule generation, IPv6 bracket formatting, HostIP filtering, SCTP support, duplicate host ports across IPs/protocols, and removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_iptables_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_manager.go

## Purpose
Defines the CRI-O hostport management interface and the `PortMapping` data model shared by iptables, nftables, meta, and noop hostport managers.

## Important APIs, Types, And Functions
- `HostPortManager` interface declares `Add(id, name, podIP string, hostportMappings []*PortMapping) error` and `Remove(id string, hostportMappings []*PortMapping) error`.
- `PortMapping` contains `HostPort`, `ContainerPort`, Kubernetes `Protocol`, and optional `HostIP`.

## Control Flow
This file has declarations only. Implementations decide backend behavior and cleanup strategy.

## State And Persistence
No state is stored here. Implementations persist hostport mappings in kernel packet filtering state or do nothing.

## Dependencies And Integration Points
Uses Kubernetes core `v1.Protocol`. The interface is consumed by sandbox/container networking code and implemented by iptables, nftables, meta, and noop managers.

## Risks And Edge Cases
`Remove` is explicitly required to work without pod IP, which shapes backend state keys and cleanup algorithms. `HostPort <= 0` filtering is implemented in the meta layer, not the type itself.

## Test Signals
Shared test cases in `hostport_manager_test.go` instantiate `PortMapping` scenarios used by backend tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager_linux.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_manager_linux.go

## Purpose
Provides Linux-specific deletion of UDP conntrack entries for hostport destination ports after new NAT rules are installed.

## Important APIs, Types, And Functions
- `deleteConntrackEntriesForDstPort(port uint16, protocol uint8, family netlink.InetFamily) error` builds a `netlink.ConntrackFilter` and calls `netlink.ConntrackDeleteFilters`.

## Control Flow
The function adds protocol and original destination port filters, then deletes matching entries from the conntrack table for the specified address family. Each setup/delete error is wrapped with protocol and port context.

## State And Persistence
Mutates kernel conntrack state by deleting entries. It does not alter iptables/nftables rules or CRI-O state.

## Dependencies And Integration Points
Used by `metaHostportManager.Add` for UDP hostports after backend Add succeeds. Depends on `vishvananda/netlink` and Linux netfilter conntrack support.

## Risks And Edge Cases
Deletion requires suitable privileges and kernel support. Errors are logged but ignored by the meta manager, so stale conntrack entries may remain and temporarily blackhole UDP traffic.

## Test Signals
No direct unit test in this subset because it touches kernel conntrack. Behavior is indirectly represented by meta-manager code paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager_test.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_manager_test.go

## Purpose
Defines shared IPv4 and IPv6 hostport test fixtures used by iptables, nftables, and meta hostport manager tests.

## Important APIs, Types, And Functions
- `testCase` groups sandbox ID, pod name, pod IP, and mappings.
- `testCasesV4` covers TCP, UDP, SCTP, specific HostIP, duplicate host port on different HostIPs, and duplicate host port across protocols.
- `testCasesV6` mirrors core IPv6 scenarios including `::1` HostIP.

## Control Flow
No executable test specs are defined. Other tests iterate over these fixtures to add/remove hostports and compare backend-specific expected state.

## State And Persistence
No mutable state. The fixed IDs intentionally produce stable hash outputs used in expected iptables chain names and nftables comments.

## Dependencies And Integration Points
Uses Kubernetes `v1.Protocol` and the local `PortMapping` type. Tightly coupled to expected rule/element arrays in backend tests.

## Risks And Edge Cases
Changing fixture IDs, ports, HostIPs, or ordering invalidates many expected outputs. The fixtures cover common cases but do not include invalid protocols, negative ports, or mixed-family HostIP/podIP beyond meta filtering.

## Test Signals
Provides cross-backend consistency for hostport behavior. Its presence makes backend tests comparable across iptables and nftables.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager_unsupported.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_manager_unsupported.go

## Purpose
Provides a non-Linux stub for UDP conntrack cleanup used by hostport management.

## Important APIs, Types, And Functions
- `deleteConntrackEntriesForDstPort(port uint16, protocol uint8, family netlink.InetFamily) error` always returns an unsupported-platform error with `runtime.GOOS`.

## Control Flow
Build-tagged with `//go:build !linux`. It does not inspect arguments beyond formatting the error.

## State And Persistence
No state is changed. No conntrack entries are deleted.

## Dependencies And Integration Points
Keeps hostport meta manager buildable off Linux while preserving the same function signature. Imports `netlink.InetFamily` for signature compatibility.

## Risks And Edge Cases
If hostport Add calls UDP conntrack cleanup on non-Linux, errors are logged by the meta manager but not returned. This is acceptable for best-effort cleanup but means UDP stale state is not cleared off Linux.

## Test Signals
No direct tests in this subset; compile-time build tag coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_manager_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_nftables.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_nftables.go

## Purpose
Implements the nftables backend for CRI-O hostport mappings using nft maps and sets rather than per-port chains.

## Important APIs, Types, And Functions
- Constants define the `crio-hostports` table, `hostports` map, `hostipports` map, and `hairpins` set.
- `hostportManagerNFTables` wraps a `knftables.Interface`, family, and mutex.
- `newHostportManagerNFTables`, `Add`, `Remove`, `hashSandboxID`, and `ensureHostPortsTable` implement backend behavior.

## Control Flow
`Add` locks, creates a transaction, ensures the table/chains/maps/set and static rules exist, hashes the sandbox ID into a comment, then adds map elements for wildcard hostports or HostIP-specific hostports and a hairpin set element. `Remove` lists existing elements from both maps and the hairpin set, deletes elements whose comment matches the sandbox hash, and runs the transaction only if there is work. `ensureHostPortsTable` creates IPv4 or IPv6-specific nftables objects and flushes/repopulates static chains while preserving dynamic map/set elements.

## State And Persistence
Persists hostport mappings in kernel nftables table elements. The sandbox hash comment is the persistent key for IP-independent removal. Static chains are idempotently recreated on Add.

## Dependencies And Integration Points
Uses `sigs.k8s.io/knftables` for typed nftables transactions. Selected preferentially by `meta_hostport_manager.go` when available. Supports IPv4 and IPv6 families with family-specific address types and rule syntax.

## Risks And Edge Cases
Comment hash collisions are possible but unlikely; a collision would over-delete mappings. `Remove` ignores the supplied mapping details and deletes all elements for the sandbox comment. Ensuring static chains flushes chains but not dynamic elements. Errors listing maps/sets other than not-found abort removal.

## Test Signals
`hostport_nftables_test.go` verifies table/rule layout, IPv4/IPv6 element generation, HostIP-specific map use, hairpin entries, and cleanup to no elements.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_nftables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_nftables_test.go -->
# sources/cloud-native/cri-o/internal/hostport/hostport_nftables_test.go

## Purpose
Tests nftables hostport table creation, element generation, and removal for IPv4 and IPv6.

## Important APIs, Types, And Functions
- Expected element arrays pin map/set entries for IPv4 and IPv6.
- `checkNFTablesElements` compares fake nftables dump elements against expectations.
- Exercises `ensureHostPortsTable`, `hostportManagerNFTables.Add`, and `hostportManagerNFTables.Remove`.

## Control Flow
The table test creates a fake nftables transaction, runs `ensureHostPortsTable`, and compares the static table/chains/maps/set/rules dump. IPv4 and IPv6 tests add all shared fixture mappings to a fake manager, compare only dynamic `add element` lines, remove all mappings, and assert no elements remain.

## State And Persistence
Mutates `knftables.Fake` in-memory state. Expected dump strings document intended persistent nftables kernel objects.

## Dependencies And Integration Points
Uses `knftables.Fake`, Kubernetes set comparison, and shared hostport test fixtures. Confirms backend behavior used by the meta manager.

## Risks And Edge Cases
Exact static dump expectations are sensitive to knftables formatting. The tests validate normal add/remove paths but do not inject list/run failures or comment hash collision cases.

## Test Signals
Strong signal for nftables syntax, table idempotence assumptions, IPv6 family handling, HostIP map ordering, and sandbox-comment cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/hostport_nftables_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager.go -->
# sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager.go

## Purpose
Coordinates hostport management across IPv4/IPv6 and iptables/nftables backends. It prefers nftables for new rules, falls back to iptables, cleans both on removal for migration safety, filters mappings by IP family, and clears UDP conntrack entries after Add.

## Important APIs, Types, And Functions
- `metaHostportManager` maps `utilnet.IPFamily` to `hostportManagers`.
- `hostportManagers` holds optional iptables and nftables managers.
- `NewMetaHostportManager`, `newMetaHostportManagerInternal`, `Add`, `Remove`, and `filterHostportMappings` implement orchestration.
- `netlinkFamily` maps Kubernetes IP families to netlink families.

## Control Flow
Construction tries IPv4 iptables and nftables and fails only if both are unavailable. IPv6 backends are attempted but may be absent, with informational logging. `Add` determines pod IP family, filters invalid or mismatched mappings, errors if no manager exists for the family, selects nftables if present otherwise iptables, and then best-effort deletes UDP conntrack entries for host ports. `Remove` does not know pod IP, so it iterates all configured families, filters mappings by HostIP family, removes nftables entries when available, removes iptables entries too, and ignores iptables errors when nftables is primary.

## State And Persistence
Persists no state directly; delegates to backend kernel state. UDP conntrack deletion mutates kernel conntrack state. Manager availability is kept in memory.

## Dependencies And Integration Points
Integrates CRI-O iptables wrapper, knftables, Kubernetes IP family utilities, netlink conntrack, Linux `unix` protocol constants, and backend hostport managers. This is the main `HostPortManager` implementation callers should use when hostports are enabled.

## Risks And Edge Cases
IPv6 support is optional; IPv6 Add fails if no IPv6 backend is present. HostIP-family filtering can drop mappings silently. `HostPort <= 0` mappings are ignored. UDP conntrack cleanup failures are logged but not returned. Remove aggregates backend errors into a newline-joined error string but ignores iptables errors when nftables exists.

## Test Signals
`meta_hostport_manager_test.go` covers iptables-only, nftables-only, both-backend preference, legacy iptables cleanup while using nftables, and IPv4-only manager behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager_test.go -->
# sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager_test.go

## Purpose
Tests the meta hostport manager's backend selection, dual-stack routing, nftables preference, migration cleanup, and IPv4-only behavior.

## Important APIs, Types, And Functions
- Exercises `newMetaHostportManagerInternal`, `HostPortManager.Add`, and `HostPortManager.Remove`.
- Uses fake iptables backends and `knftables.Fake` backends.
- Reuses `checkIPTablesRules`, `checkNFTablesElements`, and shared IPv4/IPv6 test cases.

## Control Flow
The file builds an interleaved list of IPv4 and IPv6 cases. Separate tests construct managers with only iptables, only nftables, both backends, and only IPv4 support. The migration test first creates legacy iptables rules, rebuilds a manager with nftables also available, verifies new Add operations use nftables without disturbing legacy iptables rules, then verifies Remove clears both backends.

## State And Persistence
Mutates fake iptables and fake nftables state to model persistent kernel rules across manager restarts. The migration test intentionally carries fake iptables state across manager instances.

## Dependencies And Integration Points
Validates the integration contract between meta manager and both backends. Uses Kubernetes IP family utilities to decide expected IPv6 failure in IPv4-only mode.

## Risks And Edge Cases
The tests do not verify UDP conntrack cleanup because the real netlink function is not faked here. They rely on backend expected outputs and stable sandbox hash/chain derivation.

## Test Signals
Very strong signal for upgrade/downgrade safety: CRI-O can switch to nftables for new hostports while still removing old iptables hostports.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/meta_hostport_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/noop_hostport_manager.go -->
# sources/cloud-native/cri-o/internal/hostport/noop_hostport_manager.go

## Purpose
Implements a disabled hostport manager that satisfies `HostPortManager` while performing no network rule changes.

## Important APIs, Types, And Functions
- `noopHostportManager` is an empty implementation.
- `NewNoopHostportManager` logs that hostport mapping is disabled and returns the manager.
- `Add` and `Remove` log debug messages and return nil.

## Control Flow
Construction and method calls have no branches beyond logging. All inputs are ignored.

## State And Persistence
No state is held and no kernel packet filtering state is changed.

## Dependencies And Integration Points
Used when CRI-O hostport mapping is disabled. It depends only on logrus and the shared interface/type definitions.

## Risks And Edge Cases
Callers receive successful nil errors even though requested hostport mappings are not installed. This is intentional for disabled configurations but can hide misconfiguration if selected accidentally.

## Test Signals
`noop_hostport_manager_test.go` verifies construction and nil-error Add/Remove behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/noop_hostport_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/noop_hostport_manager_test.go -->
# sources/cloud-native/cri-o/internal/hostport/noop_hostport_manager_test.go

## Purpose
Confirms the disabled hostport manager satisfies the interface and treats Add/Remove as successful no-ops.

## Important APIs, Types, And Functions
- Exercises `NewNoopHostportManager`, `Add`, and `Remove`.

## Control Flow
The single test constructs the manager, calls Add with sample pod identity/IP and nil mappings, then calls Remove with nil mappings. Both operations must return nil.

## State And Persistence
No state is changed. No kernel rules are written.

## Dependencies And Integration Points
Uses the hostport test suite framework and the no-op manager implementation.

## Risks And Edge Cases
Only nil mappings are tested; non-empty mappings should be equally ignored by implementation but are not explicitly asserted.

## Test Signals
Basic smoke test for disabled hostport mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/noop_hostport_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/suite_test.go -->
# sources/cloud-native/cri-o/internal/hostport/suite_test.go

## Purpose
Bootstraps the Ginkgo/Gomega hostport test suite.

## Important APIs, Types, And Functions
- `TestHostPort(t *testing.T)` registers fail handling and runs framework specs.
- Package global `t *TestFramework` is initialized by `BeforeSuite` and torn down by `AfterSuite`.

## Control Flow
Before the suite, a CRI-O test framework is created with no-op callbacks and setup is run. After the suite, teardown is run.

## State And Persistence
Holds package-global test framework state. Individual tests create fake in-memory iptables/nftables state; this file does not persist data.

## Dependencies And Integration Points
Integrates ONSI Ginkgo/Gomega with CRI-O's shared test framework for hostport tests.

## Risks And Edge Cases
Suite setup does not reset external kernel state because tests use fakes. Any future test using real netfilter state must handle its own isolation.

## Test Signals
Provides test runner plumbing only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/hostport/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/iptables.go -->
# sources/cloud-native/cri-o/internal/iptables/iptables.go

## Purpose
Provides CRI-O's vendored Kubernetes iptables abstraction for goroutine-safe command execution, rule/chain management, save/restore, feature detection, canary monitoring, error parsing, and restore context extraction.

## Important APIs, Types, And Functions
- `Interface` defines chain/rule/save/restore/monitor/random-fully/presence operations.
- Types/constants include `RulePosition`, `Protocol`, `Table`, `Chain`, `RestoreCountersFlag`, `FlushFlag`, command names, version thresholds, wait flags, and lock paths.
- `runner` implements the interface around `utilexec.Interface`.
- Key methods: `New`, `newInternal`, `EnsureChain`, `FlushChain`, `DeleteChain`, `EnsureRule`, `DeleteRule`, `SaveInto`, `Restore`, `RestoreAll`, `Monitor`, `ChainExists`, `HasRandomFully`, and `Present`.
- Helpers include command selection, version parsing, wait flag selection, rule checking with or without `-C`, not-found/resource error classification, restore parse error parsing, and `ExtractLines`.

## Control Flow
Construction probes iptables version and configures support for `-C`, `--random-fully`, command wait flags, and restore wait flags. Mutating methods acquire `runner.mu`, build full arguments, use check-before-add/delete for rules, and wrap command output into contextual errors. Restore builds arguments, optionally appends `--noflush` and `--counters`, uses native restore wait flags or manual lock acquisition, runs restore with stdin data, and parses line-number errors. Monitor creates canary chains, waits for external flushes, waits for other table canaries to disappear, then invokes reload.

## State And Persistence
The runner holds feature flags and a mutex in memory. Operations persist state in kernel iptables tables via external commands. `SaveInto` copies kernel table state into a caller buffer. Monitor creates/deletes canary chains in kernel tables.

## Dependencies And Integration Points
Depends on Kubernetes/apimachinery sets/version/wait, Kubernetes exec interface, CRI-O logging, and platform-specific lock acquisition in `iptables_linux.go`. Hostport iptables backend depends on this package for NAT table persistence and restore.

## Risks And Edge Cases
String parsing for old rule checks and not-found detection is imperfect. `checkRuleWithoutCheck` can miss argument ordering differences. Restore parse error handling depends on iptables stderr format. Manual locks are used only when restore lacks wait support. Monitor uses deprecated polling APIs and assumes canary deletion indicates flush. `Present` only checks NAT POSTROUTING.

## Test Signals
No direct tests in this subset, but hostport fake implements this interface and hostport tests exercise save/restore assumptions. Production behavior is inherited from Kubernetes vendored utility patterns.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/iptables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/iptables_linux.go -->
# sources/cloud-native/cri-o/internal/iptables/iptables_linux.go

## Purpose
Implements Linux manual xtables locking for iptables-restore when native restore wait flags are unavailable.

## Important APIs, Types, And Functions
- `locker` holds a 1.6-style file lock and 1.4-style Unix listener lock.
- `(*locker).Close` releases both locks.
- `grabIptablesLocks(lockfilePath14x, lockfilePath16x string) (iptablesLocker, error)` acquires both lock styles with polling.
- `grabIptablesFileLock` uses `unix.Flock`.

## Control Flow
`grabIptablesLocks` opens/creates the 1.6 lock file, polls for a non-blocking exclusive flock, then polls for a Unix listener at the 1.4 lock path. A deferred cleanup closes partially acquired locks unless both acquisitions succeed.

## State And Persistence
Creates/opens a lock file under the configured xtables lock path and binds a Unix socket at the old lock path. These are process-level synchronization artifacts, not CRI-O state.

## Dependencies And Integration Points
Called by `runner.restoreInternal` in `iptables.go` when iptables-restore lacks wait support. Depends on Linux `flock`, `net.ListenUnix`, and Kubernetes wait polling.

## Risks And Edge Cases
Lock acquisition times out after two seconds per lock style. Failure to close locks is logged by caller. The old Unix socket lock can conflict with stale filesystem entries or permissions.

## Test Signals
No direct tests in this subset. Behavior is indirectly important for safe production restore serialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/iptables_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/iptables_unsupported.go -->
# sources/cloud-native/cri-o/internal/iptables/iptables_unsupported.go

## Purpose
Provides a non-Linux implementation of manual iptables lock acquisition that always reports unsupported platform.

## Important APIs, Types, And Functions
- `grabIptablesLocks(lockfilePath14x, lockfilePath16x string) (iptablesLocker, error)` returns nil plus a `runtime.GOOS` error.

## Control Flow
Build-tagged with `//go:build !linux`. No lock paths are used.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Keeps the shared iptables runner compileable off Linux. If restore wait flags are unavailable on non-Linux, restore will fail through this path.

## Risks And Edge Cases
The broader iptables runner can still be constructed off Linux, but actual restore locking is unsupported. This matches the platform reality for iptables management.

## Test Signals
No direct tests in this subset; build-tag compilation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/iptables_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/save_restore.go -->
# sources/cloud-native/cri-o/internal/iptables/save_restore.go

## Purpose
Provides a small helper for formatting iptables-save/restore chain declaration lines.

## Important APIs, Types, And Functions
- `MakeChainLine(chain Chain) string` returns `:<chain> - [0:0]`.

## Control Flow
No branching; formats the supplied chain into an iptables-save-compatible declaration.

## State And Persistence
No state is changed. The returned string is used in restore payload generation.

## Dependencies And Integration Points
Used by hostport iptables code and fake iptables tests to emit chain declarations in restore data. Depends only on `fmt` and local `Chain`.

## Risks And Edge Cases
Assumes zero counters and default policy marker `-`, which is appropriate for user-defined chains. Builtin chain policies may require different formatting in other contexts.

## Test Signals
Used by hostport tests and fake restore tests; no direct standalone test.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/iptables/save_restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/checkpoint.go -->
# sources/cloud-native/cri-o/internal/lib/checkpoint.go

## Purpose
Implements container checkpointing and optional checkpoint archive export for CRI-O containers, including runtime pause/checkpoint coordination, rootfs diff capture, metadata/spec dumps, bind mount type metadata, log capture, archive generation, and cleanup.

## Important APIs, Types, And Functions
- `ContainerCheckpointOptions` exposes `Keep`, `KeepRunning`, and `TargetFile`.
- `(*ContainerServer).ContainerCheckpoint` is the main checkpoint API.
- Helpers/constants: `containerMounts`, `bindMount`, `skipBindMount`, `getDiff`, `ExternalBindMount`, `prepareCheckpointExport`, and `exportCheckpoint`.

## Control Flow
`ContainerCheckpoint` looks up the container, loads `config.json`, requires running state, pauses the container, and defers status update/unpause/state persistence. If exporting, it writes spec/config dumps and bind mount metadata before invoking runtime checkpoint. On checkpoint failure it removes the checkpoint directory. If exporting, it captures rootfs diff/logs and writes a tar to `TargetFile`, then removes checkpoint directory. If `KeepRunning` is false it unmounts/stops storage. If `Keep` is false it deletes selected dump/stat files from the container directory.

## State And Persistence
Writes checkpoint artifacts under `ctr.CheckpointPath()`/`ctr.Dir()`, optional metadata JSON files (`spec.dump`, `config.dump`, `bind.mounts`), optional copied log file, rootfs diff tar components, and the final export file with mode `0600`. It updates in-memory/runtime status through runtime calls and persists container state to disk in the deferred path.

## Dependencies And Integration Points
Integrates `checkpointctl` metadata, CRIU stats filenames, OCI runtime-tools generator, CRI-O runtime/storage servers, Podman/common CRIU utilities, containers/storage archive diff/tar APIs, CRI-O annotations, and OCI container state.

## Risks And Edge Cases
Checkpointing pauses the container to reduce rootfs/log race windows, but exported files can still represent a point-in-time approximation. Export failure after runtime checkpoint can leave partial export files. `TargetFile` is opened with `O_RDWR|O_CREATE` but not `O_TRUNC`, so overwriting a larger existing file can risk trailing bytes. Cleanup of files and checkpoint dirs is best-effort in places. Bind mount source stat failures abort export prep.

## Test Signals
`checkpoint_test.go` covers invalid container ID, invalid config, not-running containers, successful checkpoint, runtime pause failure, export with bind mount metadata and rootfs diff, and storage unmount failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/checkpoint_test.go -->
# sources/cloud-native/cri-o/internal/lib/checkpoint_test.go

## Purpose
Tests `ContainerServer.ContainerCheckpoint` behavior for invalid input, container state validation, runtime failures, successful checkpointing, export paths, and storage unmount errors.

## Important APIs, Types, And Functions
- Exercises `sut.ContainerCheckpoint` with `metadata.ContainerConfig` and `lib.ContainerCheckpointOptions`.
- Uses mock storage store expectations, mock runtime configuration helpers, and CRIU availability checks.

## Control Flow
The main checkpoint tests set up dummy config/runtime state, skip when CRIU is unavailable, add a container/sandbox, configure container state/spec, and call checkpoint. Export test writes a custom OCI config with file and directory bind mounts, expects storage `Changes`, `Mount`, `Container`, and `Unmount` calls, and verifies success. Separate tests without full CRIU setup cover invalid ID and invalid `config.json` handling.

## State And Persistence
Creates temporary files/directories, writes test `config.json`, may create `cp.tar`, and removes test dump/export files. Mutates mocked container state to running where needed.

## Dependencies And Integration Points
Integrates CRIU utility version checking, checkpointctl metadata, runtime-spec state, containers/storage mocks, archive change fixtures, and CRI-O test setup helpers.

## Risks And Edge Cases
Tests are environment-sensitive because CRIU availability gates the main block. Some assertions depend on exact error strings. Export test uses `/tmp/` as a mocked mountpoint and verifies success rather than deeply inspecting tar contents.

## Test Signals
Good coverage for major checkpoint control-flow branches and error wrapping. It does not fully validate archive contents or cleanup on every failure path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/checkpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/constants/constants.go -->
# sources/cloud-native/cri-o/internal/lib/constants/constants.go

## Purpose
Defines the CRI-O container manager annotation value used to identify containers managed by CRI-O.

## Important APIs, Types, And Functions
- `ContainerManagerCRIO = "cri-o"`.

## Control Flow
Declaration only. Runtime behavior occurs in code that compares annotation values.

## State And Persistence
No state is held. The value is persisted elsewhere as an OCI annotation, typically under `io.container.manager`.

## Dependencies And Integration Points
Used by factory annotation code and `ContainerServer.LoadContainer` to distinguish CRI-O-managed containers from other managers such as libpod.

## Risks And Edge Cases
Changing the value would break compatibility with persisted container specs and load filtering.

## Test Signals
`container_test.go` validates generated annotations include this value, and `container_server_test.go` validates non-CRI-O manager annotations are rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/constants/constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container.go -->
# sources/cloud-native/cri-o/internal/lib/container.go

## Purpose
Provides lookup helpers on `ContainerServer` for resolving containers and sandboxes by name, full ID, or short ID, and for retrieving the storage container/top layer associated with an OCI container.

## Important APIs, Types, And Functions
- `GetStorageContainer`, `GetContainerTopLayerID`, `GetContainerFromShortID`, `LookupContainer`, `getSandboxFromRequest`, and `LookupSandbox`.

## Control Flow
Container lookup validates non-empty input, resolves names through registrars when possible, falls back to treating input as an ID, resolves short IDs through truncindex, retrieves objects from in-memory stores, and validates containers are created. Storage helpers first resolve the OCI container and then query the containers/storage store for container metadata/layer ID. Sandbox lookup mirrors the container path with pod name and ID indexes.

## State And Persistence
Reads in-memory registrars/truncindex/memorystore and the storage backend. It does not mutate state.

## Dependencies And Integration Points
Integrates `registrar` name reservations, `truncindex` ID prefix lookup, in-memory CRI-O container/sandbox stores, OCI container state, and containers/storage metadata.

## Risks And Edge Cases
Empty IDs/names fail fast. Registrar errors other than name-not-reserved abort lookup. A resolved ID missing from memory or a not-yet-created container returns an error. Short ID ambiguity is handled by truncindex.

## Test Signals
`container_test.go` covers successful lookup, empty input errors, invalid short IDs, and the not-created container guard.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server.go -->
# sources/cloud-native/cri-o/internal/lib/container_server.go

## Purpose
Implements CRI-O's core `ContainerServer`: runtime/storage service construction, sandbox/container restore from disk, name/ID indexes, in-memory state management, state persistence, resource updates, shutdown, storage repair/wipe helpers, and monitor probing.

## Important APIs, Types, And Functions
- `ContainerServer` holds runtime, storage, image/runtime services, registrars, truncindexes, hook manager, state stores, config, stats server, and monitor channel.
- Constructor/getters: `New`, `Runtime`, `Store`, `StorageImageServer`, `StorageRuntimeServer`, `CtrIDIndex`, `PodIDIndex`, and `Config`.
- Restore/load: `LoadSandbox`, `LoadContainer`, `restoreVolumes`, `ErrIsNonCrioContainer`.
- Persistence/indexing: `ContainerStateToDisk`, `ReserveContainerName`, `ReleaseContainerName`, `ContainerIDForName`, `ReservePodName`, `ReleasePodName`, `PodIDForName`.
- State operations: `AddContainer`, `AddInfraContainer`, `GetContainer`, `GetInfraContainer`, `HasContainer`, `RemoveContainer`, `RemoveInfraContainer`, `ListContainers`, `AddSandbox`, `GetSandbox`, `GetSandboxContainer`, `HasSandbox`, `RemoveSandbox`, `ListSandboxes`.
- Maintenance: `UpdateContainerLinuxResources`, `ShutdownWasUnclean`, `RemoveStorageDirectory`, `checkQuick`, `CheckReportHasErrors`, `probeMonitorProcesses`, and `Shutdown`.

## Control Flow
`New` validates config, gets storage, optionally repairs or wipes storage after unclean shutdown, creates image/runtime services, OCI runtime, hooks manager, state stores, stats server, and starts monitor probing. `LoadSandbox` reads OCI spec from disk, validates annotations and metadata, reserves pod/container names, reconstructs sandbox fields, creates/restores infra container, restores volumes and namespaces, reloads state from disk, writes state back, reserves labels/IDs, and uses defers to roll back partial state on error. `LoadContainer` reads persisted spec, rejects non-CRI-O containers, reconstructs metadata/image references/kube annotations, requires sandbox presence, creates OCI container, restores volumes/state/spec/runtime path, adds it to state, and indexes ID. State add/remove methods coordinate sandbox membership, stats cleanup, managed namespace cleanup, and platform-specific SELinux bookkeeping.

## State And Persistence
Persists container state JSON through atomic writes to `ctr.StatePath()`. Reads `config.json` and state from storage container directories. Maintains in-memory stores for containers, infra containers, sandboxes, process SELinux level reference counts, registrars, and truncindexes. Storage repair/wipe can mutate or delete the storage graph root. Shutdown closes monitor channel and storage. Monitor probing periodically inspects container monitor processes.

## Dependencies And Integration Points
Integrates CRI-O config, OCI runtime, containers/storage, image/runtime storage services, hooks, stats server, sandbox builder/model, annotations, v2 annotations, hostport mappings, SELinux, memorystore, registrar, truncindex, Kubernetes CRI types, and runtime-spec.

## Risks And Edge Cases
Restore correctness depends on trusted OCI annotations; many malformed annotation cases are guarded. Deferred rollback must release names, namespaces, and IDs on partial failure. `AddContainer` silently ignores containers whose sandbox is absent. `RemoveContainer` leaves a container in state if the sandbox is already gone. Storage wipe is destructive and guarded against running Podman/shared-storage layers unless forced. Monitor goroutine uses jitter but list access must remain safe through memorystore. `UpdateContainerLinuxResources` assumes non-nil `resources.CPU` and `resources.Memory` fields.

## Test Signals
`container_server_test.go` covers constructor failures, getters, sandbox/container load success and many malformed annotation/directory cases, non-CRI-O rejection, state write error, name reservation conflicts, shutdown behavior, add/remove/list state operations, and infra container store operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_freebsd.go -->
# sources/cloud-native/cri-o/internal/lib/container_server_freebsd.go

## Purpose
Provides FreeBSD-specific namespace path restoration logic for container server sandbox loading.

## Important APIs, Types, And Functions
- `configNsPath(spec *rspec.Spec, nsType rspec.LinuxNamespaceType) (string, error)` returns the sandbox ID for network namespaces when the sandbox is not host-networked.

## Control Flow
If the requested namespace type is `NetworkNamespace` and the spec annotation does not indicate host network, the function returns `annotations.SandboxID`. Otherwise it returns a missing namespace error.

## State And Persistence
No state is changed. The returned path-like value is interpreted by FreeBSD code as the jail name for the infra container owning pod vnet.

## Dependencies And Integration Points
Used by `LoadSandbox` when joining namespaces. Integrates runtime-spec namespace types with FreeBSD jail semantics and CRI-O annotations.

## Risks And Edge Cases
Only network namespace is supported. It ignores actual `spec.Linux.Namespaces` entries and relies on annotations. Host-networked sandboxes report missing namespace.

## Test Signals
No FreeBSD-specific tests in this subset; common `LoadSandbox` tests primarily exercise Linux behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_linux.go -->
# sources/cloud-native/cri-o/internal/lib/container_server_linux.go

## Purpose
Provides Linux-specific platform hooks for sandbox SELinux level reference counting and OCI namespace path extraction during sandbox restore.

## Important APIs, Types, And Functions
- `addSandboxPlatform` parses the sandbox process label and increments `state.processLevels[level]`.
- `removeSandboxPlatform` decrements the level count and releases the SELinux label when the count reaches zero.
- `configNsPath(spec *rspec.Spec, nsType rspec.LinuxNamespaceType) (string, error)` finds a non-empty namespace path in the OCI spec.

## Control Flow
Sandbox add/remove parse SELinux context maps and update reference counts under the caller's `stateLock`. Namespace extraction scans `spec.Linux.Namespaces`, returns the matching non-empty path, and errors on empty or missing paths.

## State And Persistence
Mutates in-memory SELinux process level counts and may release SELinux labels through the SELinux library. No files are written here.

## Dependencies And Integration Points
Called by `ContainerServer.AddSandbox`, `RemoveSandbox`, and `LoadSandbox`. Depends on opencontainers SELinux library and runtime-spec namespace types.

## Risks And Edge Cases
Malformed SELinux labels cause sandbox add/remove errors. Level reference counts must stay balanced or labels may leak or be released too early. `configNsPath` assumes `spec.Linux` and `Namespaces` are present when called.

## Test Signals
`container_server_test.go` covers invalid SELinux label failure and missing/empty network namespace behavior through `LoadSandbox`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_test.go -->
# sources/cloud-native/cri-o/internal/lib/container_server_test.go

## Purpose
Tests `ContainerServer` construction, getters, sandbox/container restore from persisted specs, state persistence errors, name reservation, shutdown, in-memory state stores, and list/filter behavior.

## Important APIs, Types, And Functions
- Exercises `lib.New`, getters, `LoadSandbox`, `LoadContainer`, `ContainerStateToDisk`, `ReserveContainerName`, `ReservePodName`, `Shutdown`, `AddContainer`, `AddSandbox`, `RemoveContainer`, `RemoveSandbox`, `ListContainers`, `ListSandboxes`, `AddInfraContainer`, and `RemoveInfraContainer`.
- Uses shared helpers such as `beforeEach`, `createDummyState`, `mockDirs`, `testManifest`, `mySandbox`, and `myContainer`.

## Control Flow
Constructor tests mock config/store access and clean shutdown markers. LoadSandbox tests mutate a serialized manifest to produce valid and invalid annotations, metadata, namespace options, port mappings, labels, SELinux labels, pod resources, names, and storage directory errors. LoadContainer tests cover valid restore, bad manifests, storage directory failures, invalid annotations, and non-CRI-O manager rejection. Later blocks validate name reservation conflicts, storage shutdown errors, add/remove semantics, and list filtering.

## State And Persistence
Uses mocks for storage directories and state, creates temporary files for clean shutdown/config, and mutates in-memory server stores/indexes. `ContainerStateToDisk` failure is tested with an invalid state path.

## Dependencies And Integration Points
Integrates gomock storage/config mocks, CRI-O annotations/constants, OCI container creation, CRI API metadata, and the test framework. It documents the on-disk annotation contract used to restore sandboxes and containers.

## Risks And Edge Cases
Many tests depend on exact JSON fragments in `testManifest`; unrelated formatting changes can require updates. Some behavior labeled "should fail" intentionally returns a partially built sandbox plus error, so callers must inspect both. RemoveContainer behavior when sandbox is already missing leaves the container present, which the test documents.

## Test Signals
Very strong signal for persistence/restore robustness and server state invariants. It catches malformed persisted metadata and name/index lifecycle regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_test_inject.go -->
# sources/cloud-native/cri-o/internal/lib/container_server_test_inject.go

## Purpose
Provides test-only setters for injecting mocked storage services into `ContainerServer`.

## Important APIs, Types, And Functions
- `SetStorageRuntimeServer(server storage.RuntimeServer)`.
- `SetStorageImageServer(server storage.ImageServer)`.

## Control Flow
Build-tagged with `//go:build test`. Each setter directly replaces the corresponding unexported field.

## State And Persistence
Mutates in-memory `ContainerServer` fields. No persistence.

## Dependencies And Integration Points
Used by tests that need to replace storage runtime/image service dependencies with mocks without exposing setters in production builds.

## Risks And Edge Cases
Only available with the `test` build tag. Tests can create inconsistent server state by injecting nil or incompatible mocks.

## Test Signals
Supports checkpoint/container server tests; no standalone assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_unsupported.go -->
# sources/cloud-native/cri-o/internal/lib/container_server_unsupported.go

## Purpose
Provides non-Linux no-op platform hooks for sandbox add/remove bookkeeping.

## Important APIs, Types, And Functions
- `addSandboxPlatform(sb *sandbox.Sandbox) error` returns nil.
- `removeSandboxPlatform(sb *sandbox.Sandbox) error` returns nil.

## Control Flow
Build-tagged with `//go:build !linux`. Both functions ignore input and succeed.

## State And Persistence
No state is changed. There is no SELinux process-level reference counting on these platforms.

## Dependencies And Integration Points
Keeps `ContainerServer.AddSandbox` and `RemoveSandbox` buildable off Linux. FreeBSD still has its own `configNsPath` but uses these no-op platform hooks.

## Risks And Edge Cases
Non-Linux platforms do not get SELinux label accounting through this path. This is intentional but differs from Linux cleanup semantics.

## Test Signals
No direct tests in this subset; build-tag compilation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_server_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_test.go -->
# sources/cloud-native/cri-o/internal/lib/container_test.go

## Purpose
Tests `ContainerServer` lookup helpers for containers by ID/name/short ID and validation of created container state.

## Important APIs, Types, And Functions
- Exercises `LookupContainer` and `GetContainerFromShortID`.
- Uses shared fixtures `addContainerAndSandbox`, `myContainer`, `mySandbox`, `containerID`, and `sandboxID`.

## Control Flow
Tests add a container/sandbox for successful lookup, call lookup helpers with empty or invalid IDs for failures, and construct a not-yet-created container in indexes/state to confirm `GetContainerFromShortID` rejects it.

## State And Persistence
Mutates in-memory server state, name/ID indexes, and sandbox/container stores. No disk state is written.

## Dependencies And Integration Points
Validates integration between registrar/truncindex lookup and in-memory OCI container state. Uses the shared lib test setup.

## Risks And Edge Cases
The not-created test documents that index presence alone is insufficient; `ctr.Created()` must be true. Empty input error strings come from lookup helpers.

## Test Signals
Focused signal for lookup correctness and guarding against operations on uncreated containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/namespace/namespace.go -->
# sources/cloud-native/cri-o/internal/lib/namespace/namespace.go

## Purpose
Defines a small value object representing a namespace path and namespace type exposed from sandbox state to code that should not depend on full namespace-manager internals.

## Important APIs, Types, And Functions
- `ManagedNamespace` stores `nsPath` and `nsType`.
- `Type() nsmgr.NSType`, `Path() string`, and `NewManagedNamespace(nsPath string, nsType nsmgr.NSType) *ManagedNamespace`.

## Control Flow
Construction records the provided values. Accessors return them without validation.

## State And Persistence
Instances hold in-memory namespace metadata only. They do not own or persist namespace files.

## Dependencies And Integration Points
Uses `internal/config/nsmgr.NSType`. Returned by sandbox namespace APIs and consumed by factory namespace setup to translate CRI-O namespace manager types into OCI namespace entries.

## Risks And Edge Cases
The struct can hold empty paths or unsupported namespace types; consumers such as `ConfigureGeneratorGivenNamespacePaths` must handle those cases.

## Test Signals
Indirectly covered by namespace tests that pass `ManagedNamespace` values through sandbox namespace paths into OCI spec generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/namespace/namespace.go -->
