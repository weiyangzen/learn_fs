# subset-b-000444 grouped research

This grouped report covers Rook Ceph client command/configuration, CRUSH, CephFS, mirroring, manager, monitor, and OSD command adapters. Each source section is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/command.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/command.go

Purpose: centralizes shelling out to Ceph-related CLIs from the operator and daemons. It builds standard `ceph`, `rbd`, `rados`, `crushtool`, `ganesha-rados-grace`, and toolbox `kubectl exec` invocations with cluster config, keyring, namespace, timeout, and output-format handling.

Important APIs: `CephConfFilePath()` builds the per-cluster config path. `FinalizeCephCommandArgs()` appends standard `--cluster`, `--conf`, `--name`, `--keyring`, and Ceph connect timeout flags, with exceptions for tools that do not support them. `CephToolCommand` stores command context, args, JSON/plain output choice, combined-output mode, timeout, and Multus remote execution mode. `NewCephCommand()`, `NewRBDCommand()`, `NewRadosCommand()`, and `NewGaneshaRadosGraceCommand()` construct configured command wrappers. `Run()`, `RunWithTimeout()`, and `ExecuteCephCommandWithRetry()` are the execution surface.

Control flow and state: `run()` first respects `clusterInfo.Context` cancellation, then either finalizes local args or leaves args minimal for remote command-proxy execution. It appends JSON/plain formatting flags except for tools that reject those flags. Local execution dispatches to the configured executor, optional timeout, or combined output; remote RBD/Rados/Ganesha commands run through `RemoteExecutor.ExecCommandInContainerWithFullOutputWithTimeout()` against the `rook-ceph-mgr` command-proxy init container. The global `RunAllCephCommandsInToolboxPod` redirects all command execution into a toolbox pod during e2e tests, which is mutable process state and must be reset by tests.

Dependencies and integration: used by nearly every file in this package. It depends on `clusterd.Context` executors, `ClusterInfo` credentials/network spec, `exec.CephCommandsTimeout`, Kubernetes remote pod execution for Multus, and package logger. Risks include global toolbox state leakage, command-specific flag incompatibility, remote stderr handling that assumes `err` is non-nil when stderr exists, and accidental JSON formatting on tools that output non-JSON. Test signals in `command_test.go` and `mon_test.go` cover arg finalization, toolbox wrapping, Multus remote path selection, cancellation, keyring override, and Ganesha flag exceptions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/command_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/command_test.go

Purpose: validates the shared Ceph command construction and execution adapter behavior that all other client files rely on.

Important test cases: `TestFinalizeCephCommandArgs` verifies standard `ceph` command flags, config path construction, timeout flag insertion, and `KeyringFileOverride`. `TestFinalizeRadosGWAdminCommandArgs` confirms `radosgw-admin` receives standard config/keyring flags but no connect-timeout exception. `TestFinalizeCephCommandArgsToolBox` sets `RunAllCephCommandsInToolboxPod` and verifies `kubectl exec -i <pod> -n <ns> -- timeout <seconds> ceph ...` wrapping. `TestNewRBDCommand` verifies normal RBD execution, Multus-triggered `RemoteExecution`, and early cancellation via `clusterInfo.Context`. `TestNewGaneshaRadosGraceCommand` ensures Ganesha uses `--cephconf`, rejects standard Ceph config/name/keyring/format flags, and honors `RunWithTimeout`.

Control flow and dependencies: tests use `exectest.MockExecutor`, fake Kubernetes clientsets for remote executor behavior, `AdminTestClusterInfo`, and mutable `exec.CephCommandsTimeout`. They inspect positional args after `FinalizeCephCommandArgs()` appends flags, so the tests are sensitive to command ordering.

Risks and coverage gaps: the tests protect the most brittle command-line surfaces, especially toolbox and Ganesha exceptions. They do not fully cover `ExecuteCephCommandWithRetry()`, remote stderr handling, `NewRadosCommand()`, or timeout branches for non-Ganesha local command execution. They also mutate globals (`RunAllCephCommandsInToolboxPod`, `exec.CephCommandsTimeout`) and manually reset only the toolbox pod, so parallel execution would require care.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/command_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/config.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/config.go

Purpose: generates Ceph configuration and keyring files for daemons and command-line clients, including default monitor host entries and optional user override merging from the Rook config override ConfigMap.

Important APIs/types: `GlobalConfig` and `CephConfig` model INI sections. `DefaultConfigFilePath()`, `getConfFilePath()`, `GenerateConnectionConfig()`, `GenerateConnectionConfigWithSettings()`, `generateConfigFile()`, `CreateDefaultCephConfig()`, `PopulateMonHostMembers()`, and `WriteCephConfig()` form the main API. Helpers include `mergeDefaultConfigWithRookConfigOverride()`, `getQualifiedUser()`, `createGlobalConfigFileSection()`, and `addClientConfigFileSection()`.

Control flow and persistence: `GenerateConnectionConfigWithSettings()` writes the user's keyring, builds a config directory under `context.ConfigDir/<namespace>`, creates a global INI section, merges ConfigMap overrides, adds a client section with keyring path and optional settings, then saves `<namespace>.config`. `WriteCephConfig()` regenerates a config and copies it to the process default `/etc/ceph/ceph.conf` path, using 0600 permissions for the destination. `CreateDefaultCephConfig()` may derive `clusterInfo.CephVersion` from `ROOK_CEPH_VERSION`, then populates `fsid`, `mon initial members`, and `mon host`. `PopulateMonHostMembers()` skips monitors marked out of quorum and emits v2-only or v2+v1 address vectors based on the existing endpoint port.

Dependencies and integration: depends on `go-ini`, Kubernetes ConfigMaps, `k8sutil.ConfigOverrideName`, Ceph version extraction, Ceph endpoint parsing, keyring helpers, and `ClusterInfo.AllMonitors()`. The output is consumed by `command.go` and Ceph daemons.

Risks: monitor order comes from maps and is nondeterministic; tests account for membership rather than exact order. Config override `Append()` can alter arbitrary INI sections; debug keys are explicitly removed from global to keep CLI JSON parseable. `WriteCephConfig()` writes a process-global default config, so permission and filesystem failures are operationally important. Test signals cover default monitor formatting and ConfigMap override merging.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/config_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/config_test.go

Purpose: validates default Ceph config rendering and config override merging.

Important test cases: `TestCreateDefaultCephConfig` constructs a `ClusterInfo` with FSID, monitor secret, namespace, and two internal monitors, then verifies `CreateDefaultCephConfig()` fills `MonMembers` and `MonHost`. `TestGenerateConfigFile` creates a temporary config directory and fake Kubernetes ConfigMap named `rook-config-override`, then calls `generateConfigFile()` and reloads the result with `ini.Load()` to confirm both default `fsid` and override `bluestore_min_alloc_size_hdd` exist. Helpers `verifyConfig()` and `verifyConfigValue()` perform order-tolerant checks.

Control flow and dependencies: tests use `test.New()` fake clientset, `go-ini`, `t.TempDir()`, and direct construction of `ClusterInfo`. The override path exercises Kubernetes API reads inside `mergeDefaultConfigWithRookConfigOverride()`.

Risks and coverage gaps: the tests cover happy paths for config generation but not failure paths for invalid ConfigMap INI, missing clientset, filesystem permission failures, `ROOK_CEPH_VERSION` parsing, out-of-quorum monitor exclusion, v2-only monitor formatting, or `WriteCephConfig()` copying to the default config path. `verifyConfig()` accepts a `loggingLevel` argument that is unused, suggesting leftover behavior from older logging config tests. The tests correctly avoid assuming map iteration order for monitors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crash.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/crash.go

Purpose: wraps Ceph crash module commands used by Rook to list and archive crash records.

Important APIs/types: `CrashList` models the broad JSON shape of `ceph crash ls`, including crash ID, entity, timestamp, process/version/OS/assertion/IO error fields, and backtrace. `GetCrashList()` runs `ceph crash ls` and unmarshals a slice of `CrashList`. `ArchiveCrash()` runs `ceph crash archive <id>`. `GetCrash()` currently delegates to `GetCrashList()`.

Control flow and state: all state lives in the Ceph crash module; this file persists nothing locally. `ArchiveCrash()` logs before and after archiving. Both operations use `NewCephCommand()`, so standard JSON output, config, keyring, timeout, and context cancellation behavior are inherited from `command.go`.

Dependencies and integration: consumed by health/reconciliation code that monitors cluster crash reports. It depends on `encoding/json`, `clusterd.Context`, `ClusterInfo`, and package logger. Risks include schema drift in Ceph crash output and a likely typo in the struct tag `iio_error_length`, which may prevent `IoErrorLength` from being populated from the expected Ceph field if the real JSON key is `io_error_length`. Test coverage only validates listing with a minimal crash JSON fixture; archive behavior and rich fields are not tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crash_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/crash_test.go

Purpose: provides a minimal unit test for crash listing.

Important test cases: `TestCephCrash` configures a mock executor that returns a single crash entry for `ceph crash ls`, calls `GetCrashList()`, and asserts no error plus one returned record. The `fakecrash` fixture includes `crash_id`, `timestamp`, `process_name`, and `entity_name`.

Control flow and dependencies: the mock checks `args[0] == "crash"` and `args[1] == "ls"`, relying on `NewCephCommand()` appending standard args after the command-specific arguments. It uses `AdminTestClusterInfo()` and `exectest.MockExecutor`.

Risks and coverage gaps: the test confirms the happy path but does not validate field-level unmarshalling, command errors, invalid JSON, `GetCrash()` delegation, or `ArchiveCrash()`. It also does not cover optional fields such as assertion details, IO error metadata, or backtrace.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/crush.go

Purpose: provides command wrappers and helpers for reading, modifying, compiling, and injecting Ceph CRUSH map information.

Important APIs/types: `CrushMap` models devices, types, buckets, rules, and tunables from `ceph osd crush dump`. `ruleSpec` and `stepSpec` model CRUSH rule JSON used by `crush_rule.go`. `CrushFindResult` models `ceph osd find`. Public helpers include `GetCrushMap()`, `GetCompiledCrushMap()`, `FindOSDInCrushMap()`, `GetCrushHostName()`, `NormalizeCrushName()`, `GetCrushRootFromSpec()`, `IsNormalizedCrushNameEqual()`, `UpdateCrushMapValue()`, and `GetOSDOnHost()`. Package helpers compile/decompile/inject/set CRUSH maps and construct derived file names.

Control flow and state: `GetCrushMap()` and `FindOSDInCrushMap()` run Ceph commands and unmarshal JSON. `GetCompiledCrushMap()` creates a temp file and asks Ceph to write the compiled map into it, returning the file path; cleanup is left to callers. `compileCRUSHMap()` and `decompileCRUSHMap()` run local `crushtool` and write sibling `.compiled`/`.decompiled` files. `injectCRUSHMap()` and `setCRUSHMap()` mutate cluster CRUSH state through Ceph commands with plain output.

Dependencies and integration: used by pool/stretch-cluster logic and OSD placement management. It integrates with `cephv1.ClusterSpec` storage config and command execution. Risks include uncleaned temp files, unsafe `UpdateCrushMapValue()` parsing on malformed `key=value` entries, map-order nondeterminism from Ceph output, and direct cluster mutation in inject/set helpers. Tests cover JSON dump parsing, host OSD listing, name normalization, and file-name helpers; command failure paths and temp file cleanup are not covered.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule.go

Purpose: builds CRUSH rules used by stretch-cluster and two-step replicated placement workflows, and retrieves named CRUSH rule JSON from Ceph.

Important APIs: `buildTwoStepPlainCrushRule()` and `buildTwoStepHybridCrushRule()` render textual CRUSH rule snippets with generated rule IDs, root, failure domain, sub-failure domain, and optional device class/hybrid storage classes. `buildTwoStepCrushRule()` returns a structured `ruleSpec` equivalent. `buildTwoStepCrushSteps()` creates `take`, `chooseleaf_firstn`, and `emit` steps. `generateRuleID()` and `checkIfRuleIDExists()` choose an unused rule ID. `getCrushRule()` runs `ceph osd crush rule dump <name>` and unmarshals a `ruleSpec`.

Control flow and state: rule construction is pure except for using the passed `CrushMap.Rules` as the existing ID set. `generateRuleID()` starts from the last rule's ID plus one and increments until unused, so it assumes the rules slice is non-empty and that the last rule is a reasonable starting point. `getCrushRule()` reads cluster state only.

Dependencies and integration: depends on `cephv1.PoolSpec` fields such as `CrushRoot`, `FailureDomain`, `DeviceClass`, `Replicated.ReplicasPerFailureDomain`, `SubFailureDomain`, and `HybridStorage`. `mon.go` uses rule generation for default stretch rules through related helpers. Risks include panic on empty rule lists, text-template drift from Ceph CRUSH syntax, and subtle differences between plain and structured rule construction. Tests cover step construction, ID generation with ordered/unordered rules, and compile/decompile/inject/set helpers in adjacent files.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule_test.go

Purpose: validates CRUSH rule construction and helper commands.

Important test cases: `TestBuildStretchClusterCrushRule` loads `testCrushMap` and verifies the next generated rule ID. `TestBuildCrushSteps` checks four generated steps and key root/failure-domain values. `TestCompileCRUSHMap`, `TestDecompileCRUSHMap`, `TestInjectCRUSHMapMap`, and `TestSetCRUSHMapMap` verify exact command-line construction for `crushtool` and Ceph CRUSH map mutation helpers. `Test_generateRuleID` covers ordered and unordered existing rule ID lists.

Control flow and dependencies: tests reuse the JSON fixture from `crush_test.go`, `exectest.MockExecutor`, and `AdminTestClusterInfo()`. They assert positional args before standard flags appended by `NewCephCommand()`.

Risks and coverage gaps: coverage is strong for command construction and common ID selection, but it does not cover empty rules, hybrid textual rule output, device class insertion, `getCrushRule()`, or command error wrapping. Tests for ID generation assume starting from the last slice element and incrementing to an unused ID, which documents current behavior even when rules are unsorted.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush_rule_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/crush_test.go

Purpose: tests CRUSH map JSON parsing and host/name helper behavior.

Important test cases: `testCrushMap` is a representative CRUSH dump with devices, types, buckets, replicated and hybrid rules, and tunables. `TestGetCrushMap` ensures `GetCrushMap()` parses expected counts. `TestGetOSDOnHost` verifies `ceph osd crush ls <normalized-host>` command shape. `TestCrushName` checks `NormalizeCrushName()` and `IsNormalizedCrushNameEqual()` across hostnames, AWS-style names, workers, masters, zones, and IP-like names. `TestBuildCompiledDecompileCRUSHFileName` validates suffix helpers.

Control flow and dependencies: tests use mock executors and assert command args by index. The name test intentionally compares many similar strings to catch accidental over-normalization.

Risks and coverage gaps: the fixture is large enough to catch broad CRUSH schema mapping issues but does not assert individual bucket/rule fields. Error paths for malformed JSON and command failure are not covered. `GetCompiledCrushMap()` is not directly tested, so temp-file creation and `--out-file` behavior are only indirectly represented by other CRUSH map command tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/crush_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass.go

Purpose: wraps Ceph commands for discovering CRUSH device classes and the OSD IDs assigned to a class.

Important APIs: `GetDeviceClasses()` runs `ceph osd crush class ls` and returns `[]string`. `GetDeviceClassOSDs()` runs `ceph osd crush class ls-osd <class>` and returns `[]int`.

Control flow and state: both functions are read-only cluster queries through `NewCephCommand()`. They request JSON output by default and unmarshal directly into simple slices. No local state or persistence is involved.

Dependencies and integration: used by OSD and pool placement reconciliation where device classes such as `ssd` or `hdd` determine CRUSH rules and pool placement. It depends on `encoding/json`, command execution, and `ClusterInfo`. Risks include Ceph command schema changes or command errors due to unsupported device-class operations in older clusters. `GetDeviceClassOSDs()` has explicit test coverage for non-empty and empty class membership; `GetDeviceClasses()` lacks a direct unit test.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass_test.go

Purpose: validates device-class OSD lookup.

Important test case: `TestGetDeviceClassOSDs` configures a mock executor for `ceph osd crush class ls-osd ssd` and `hdd`, expecting `[0,1,2]` for `ssd` and `[]` for `hdd`. It asserts both parsed result slices.

Control flow and dependencies: the test relies on `NewCephCommand()` placing command-specific args first and standard flags after them. It uses `AdminTestClusterInfo()` and `exectest.MockExecutor`.

Risks and coverage gaps: only the OSD lookup function is tested. There is no coverage for `GetDeviceClasses()`, command failures, invalid JSON, or device class names requiring special handling. The mock branches by fixed arg indexes, so it would catch changes in command construction order.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/deviceclass_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile.go

Purpose: manages Ceph erasure-code profile discovery, creation, detail lookup, and deletion for erasure-coded pools.

Important APIs/types: `CephErasureCodeProfile` maps Ceph profile JSON with string-encoded `k` and `m`, plugin, technique, failure domain, and CRUSH root. `ListErasureCodeProfiles()`, `GetErasureCodeProfileDetails()`, `CreateErasureCodeProfile()`, and `DeleteErasureCodeProfile()` are the public surface.

Control flow and state: listing and detail lookup are read-only JSON Ceph commands. `CreateErasureCodeProfile()` first reads the `default` profile to inherit plugin and technique, overrides plugin from `pool.ErasureCoded.Algorithm`, builds key/value args for data chunks, coding chunks, plugin, technique, optional failure domain/root/device class, and optional `stripe_unit` bytes, then runs `ceph osd erasure-code-profile set <profile> --force ...` with plain output. `DeleteErasureCodeProfile()` mutates cluster state via `rm`.

Dependencies and integration: depends on `cephv1.PoolSpec`, Kubernetes `resource.Quantity` conversion for `StripeUnit`, and shared command execution. It is integrated with pool creation logic. Risks include relying on the default profile for technique/plugin, stripe unit quantities that cannot be represented as int64 bytes, and destructive `--force` profile updates. Tests cover create argument construction for failure domain, CRUSH root, device class, and stripe unit conversion, but not list/get/delete error paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile_test.go

Purpose: verifies erasure-code profile creation command construction.

Important test cases: `TestCreateProfile`, `TestCreateProfileWithFailureDomain`, and `TestCreateProfileWithDeviceClass` call `testCreateProfile()` with different optional placement fields. The helper configures a pool spec with 2 data chunks, 3 coding chunks, and `4Ki` stripe unit, mocks `erasure-code-profile get default`, then asserts `set myapp --force` args include `k`, `m`, inherited plugin/technique, optional `crush-failure-domain`, optional `crush-root`, optional `crush-device-class`, and `stripe_unit=4096`.

Control flow and dependencies: uses `resource.MustParse`, `cephv1.PoolSpec`, and `exectest.MockExecutor`. The test asserts exact arg order, documenting the command contract.

Risks and coverage gaps: it covers only successful creation. Missing tests include invalid/default profile JSON, default profile lookup failure, stripe unit conversion failure, algorithm override, `ListErasureCodeProfiles()`, `GetErasureCodeProfileDetails()`, and `DeleteErasureCodeProfile()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/erasure-code-profile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/fake/osd.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/fake/osd.go

Purpose: provides deterministic fake Ceph OSD JSON strings for unit tests in the client package and related operator code.

Important APIs: `OsdLsOutput(numOSDs)` returns JSON for `ceph osd ls` with IDs from 0 to `numOSDs-1`. `OsdTreeOutput(numNodes, numOSDsPerNode)` returns a simple CRUSH tree with one root, host nodes, and OSD leaves. `OsdOkToStopOutput(queriedID, returnOsdIds)` returns success or failure-shaped JSON for `ceph osd ok-to-stop`. `OSDDeviceClassOutput(osdId)` returns device-class JSON for a single OSD or a fake error string when no ID is provided.

Control flow and state: all functions are pure string renderers. `OsdTreeOutput()` uses negative host IDs beginning at -3 and assigns OSD IDs as `n + 3*i`, which creates a predictable distribution for the documented 3-OSDs-per-node example but is less general if callers expect sequential IDs for other `numOSDsPerNode` values.

Dependencies and integration: used by `osd_test.go` and can be reused by tests needing plausible Ceph JSON without embedding long fixtures. Risks include hand-rendered JSON drifting from real Ceph schemas and limited modeling of complex CRUSH layouts, stray OSDs, non-HDD device classes, down/out states, and non-default roots. Tests consume these helpers for OSD list, tree, ok-to-stop, and device class scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/fake/osd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/filesystem.go

Purpose: manages CephFS lifecycle and status through Ceph CLI commands, including filesystem creation/removal, MDS rank control, standby handling, subvolume group/subvolume/snapshot discovery, and MDS dump parsing.

Important APIs/types: `MDSDump`, `MDSStandBy`, `CephFilesystem`, `CephFilesystemDetails`, `MDSMap`, and `MDSInfo` model CephFS JSON. Public variables `GetFilesystem`, `ListSubvolumeGroups`, `ListSubvolumesInGroup`, `ListSubVolumeSnapshots`, and `ListSubVolumeSnapshotPendingClones` expose replaceable function hooks for tests. Main functions include `ListFilesystems()`, `AllowStandbyReplay()`, `CreateFilesystem()`, `AddDataPoolToFilesystem()`, `SetNumMDSRanks()`, `FailAllStandbyReplayMDS()`, `GetMdsIdByRank()`, `WaitForActiveRanks()`, `FailFilesystem()`, `RemoveFilesystem()`, `WaitForNoStandbys()`, `GetMDSDump()`, and subvolume listing helpers.

Control flow and state: filesystem creation first enables multiple filesystems, creates the filesystem with the first data pool, then tries to add remaining data pools while logging non-fatal errors. Removal reads `fs get`, runs `fs rm`, and optionally deletes backing pools by mapping pool IDs through pool helpers from other files. MDS workflows poll `clusterInfo.Context` with Kubernetes wait utilities and match active rank counts or standby daemon absence. Standby detection uses a regex on MDS daemon names because the dump does not explicitly include filesystem ownership for standbys.

Dependencies and integration: relies on shared Ceph command wrappers, pool deletion helpers, `exec.CephCommandsTimeout`, Linux errno handling for idempotent data pool add, and Kubernetes wait. Risks include name-regex false positives/negatives for standby matching, partial success when adding extra data pools, destructive pool deletion when `preservePoolsOnDelete` is false, and polling that suppresses transient command errors until timeout. Tests provide broad signals around JSON mapping, removal/pool deletion, standby replay failure, rank lookup, MDS dump/polling, subvolume listing, and standby replay settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror.go

Purpose: wraps CephFS snapshot mirroring commands for enabling/disabling mirroring, managing peers, configuring snapshot schedules/retention, importing/exporting bootstrap tokens, and reading mirror daemon status.

Important APIs/types: `BootstrapPeerToken` extracts the `token` field from bootstrap creation JSON. Public functions are `RemoveFilesystemMirrorPeer()`, `EnableFilesystemSnapshotMirror()`, `DisableFilesystemSnapshotMirror()`, `AddSnapshotSchedule()`, `AddSnapshotScheduleRetention()`, `GetSnapshotScheduleStatus()`, `ImportFSMirrorBootstrapPeer()`, `CreateFSMirrorBootstrapPeer()`, and `GetFSMirrorDaemonStatus()`.

Control flow and state: enable/disable and peer removal directly mutate CephFS mirror state. Disable treats `ENOTSUP` as idempotent "already disabled." Schedule addition ignores `EEXIST`; retention addition logs an `ENOENT` case as already exists even though that errno usually means missing resource, so that branch deserves scrutiny. `GetSnapshotScheduleStatus()` removes newlines before JSON unmarshalling because the Ceph command may emit a leading newline. Bootstrap import trims token whitespace and enables combined output; bootstrap create unmarshals JSON and returns the raw token bytes.

Dependencies and integration: uses `cephv1.FilesystemSnapshotSchedulesSpec` and `cephv1.FilesystemMirroringInfo`, shared command execution, errno extraction, and logger. It integrates with CephFilesystemMirror reconciliation and status checks. Risks include command behavior changing across Ceph versions, token handling in logs/errors, status command not filtering by filesystem even though `fsName` is accepted for context, and idempotency depending on exact errno extraction. Tests cover core command construction, token base64 validity, peer removal, and daemon status parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror_test.go

Purpose: validates CephFS mirror command construction and basic response parsing.

Important test cases: `TestEnableFilesystemSnapshotMirror`, `TestDisableFilesystemSnapshotMirror`, `TestImportFilesystemMirrorPeer`, `TestCreateFSMirrorBootstrapPeer`, `TestRemoveFilesystemMirrorPeer`, and `TestFSMirrorDaemonStatus` each use mock executors to assert the command prefix and important positional args. `fsMirrorToken` provides a bootstrap token JSON fixture and the create test confirms the returned token is base64-decodable. Daemon status parsing checks daemon ID and filesystem name.

Control flow and dependencies: uses `exectest.MockExecutor`, `AdminTestClusterInfo()`, and `encoding/base64`. The daemon status test asserts the status command does not append the filesystem name, documenting global daemon-status behavior.

Risks and coverage gaps: no tests cover error idempotency for `ENOTSUP`, schedule add/retention/status APIs, newline-stripped JSON in schedule status, invalid bootstrap JSON, token trimming, or combined-output import errors. The test for daemon status indexes `args[5]` in a `NotEqual` assertion, which depends on standard flags being appended by `NewCephCommand()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_test.go

Purpose: provides broad unit coverage for CephFS JSON models, filesystem deletion, MDS control helpers, standby polling, subvolume discovery, and standby replay settings.

Important test cases: marshal tests verify `CephFilesystem` and `CephFilesystemDetails` struct tags. `TestFilesystemRemove` simulates `fs get`, `fs rm`, pool lookup, pool stats, and pool deletion to ensure metadata and data pools are removed when preservation is disabled. `TestFailAllStandbyReplayMDS` covers failing only `up:standby-replay` daemons and error propagation. `TestGetMdsIdByRank` covers success plus missing fs dump, missing rank mapping, and missing info mapping. `TestGetMDSDump`, `TestFSHasStandby`, and `TestWaitForNoStandbys` cover MDS dump parsing and polling behavior. `TestListSubvolumeGroups` and `TestListSubvolumesInGroup` cover empty/multiple/error cases. `TestAllowStandbyReplay` verifies both `allow_standby_replay` and `standby_count_wanted`.

Control flow and dependencies: tests use mock executors with JSON fixtures, `AdminTestClusterInfo()`, short timeouts, and package helpers from pool code during filesystem removal. They rely on standard flags being appended after command-specific args.

Risks and coverage gaps: the test file exercises many failure paths, but does not cover `CreateFilesystem()`, `AddDataPoolToFilesystem()` EINVAL idempotency, `SetNumMDSRanks()`, `WaitForActiveRanks()`, `FailFilesystem()`, subvolume snapshot listing, or pending clone listing. Polling tests use very short intervals/timeouts, which keeps tests fast but can be sensitive to scheduler timing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/image.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/image.go

Purpose: manages RBD image and snapshot listing/deletion/status operations for pools and RADOS namespaces.

Important APIs/types: `CephBlockImage` and `CephBlockImageSnapshot` model RBD JSON. `ListImagesInPool()` delegates to `ListImagesInRadosNamespace()`. Other APIs include `ListSnapshotsInRadosNamespace()`, `DeleteSnapshotInRadosNamespace()`, `MoveImageToTrashInRadosNamespace()`, `DeleteImageFromTrashInRadosNamespace()`, `DeleteImageInPool()`, `DeleteImageInRadosNamespace()`, spec helpers, `RBDStatus.GetWatchers()`, and `GetRBDImageStatus()`.

Control flow and state: image list uses `rbd ls -l <pool> [--namespace ns]` with JSON output. Because librados debug logging can prefix output, it extracts the first line beginning with `[` before unmarshalling. Snapshot listing/deletion and image deletion use RBD commands with optional namespace. Trash removal uses `ceph rbd task add trash remove <pool[/namespace]/imageID>`, not the RBD CLI directly. Status returns watcher addresses from `rbd status`.

Dependencies and integration: used by pool cleanup, CSI/image cleanup, and block mirroring operations. It depends on `regexp`, `encoding/json`, shared RBD/Ceph command wrappers, and namespace conventions. Risks include the regex capturing the first bracketed line rather than necessarily the JSON payload if debug logs contain bracketed text, namespace path formatting inconsistencies between commands, and destructive deletion operations. Tests cover list parsing with and without debug logs and watcher extraction; many mutation APIs are untested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/image_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/image_test.go

Purpose: validates RBD image list parsing under normal and debug-log-prefixed output, plus watcher list extraction.

Important test cases: `TestListImageLogLevelInfo` mocks `rbd ls -l` returning a normal JSON array or empty array and asserts parsed image counts. `TestListImageLogLevelDebug` prefixes the same payloads with multiline librados debug logs and verifies the regex still extracts JSON arrays. `TestGetWatchers` constructs `RBDStatus` with two watcher addresses and verifies `GetWatchers()` returns both.

Control flow and dependencies: tests use `exectest.MockExecutor` and `AdminTestClusterInfo()`. They assert the command is `rbd` and starts with `ls -l`, leaving standard args uninspected.

Risks and coverage gaps: tests do not cover namespace args, invalid JSON after regex extraction, no JSON array found, snapshot operations, image deletion/trash movement, trash removal via Ceph task, or `GetRBDImageStatus()` command parsing. The debug fixture protects a known real-world issue where librados logs contaminate stdout.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/info.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/info.go

Purpose: defines shared cluster identity, monitor, credential, owner, and lifecycle metadata used by all Ceph client command helpers.

Important APIs/types: `ClusterInfo` stores FSID, monitor secret, Ceph credentials, internal/external monitors, Ceph version, namespace, owner info, private cluster name, OSD upgrade timeout, network/CSI specs, reconcile context, and optional keyring override. `AllMonitors()` merges external and internal mons when external mons exist. `MonInfo` stores monitor name, endpoint, and out-of-quorum state. `CephCred` stores username and secret. Constructors/helpers include `NewClusterInfo()`, `SetName()`, `NamespacedName()`, `AdminClusterInfo()`, `AdminTestClusterInfo()`, `IsInitialized()`, `NewMonInfo()`, `NewMinimumOwnerInfo()`, and `NewMinimumOwnerInfoWithOwnerRef()`.

Control flow and state: `NamespacedName()` panics if the private name is unset, enforcing initialization. `AdminClusterInfo()` creates admin credentials and owner info for a namespace/name. `IsInitialized()` validates required fields and propagates context cancellation. `AllMonitors()` returns internal monitors directly when there are no external mons; otherwise it creates a merged map.

Dependencies and integration: this type is passed through nearly every client call. It integrates with ceph API types, version parsing/comparison, Kubernetes owner metadata, and controller-runtime namespaced names. Risks include the panic contract around unset names, map aliasing when only internal mons exist, mutable context state controlling command execution, and misspelled comments around monitors. There is no dedicated test file in this subset, but the constructors and context cancellation are exercised by command/config tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/keyring.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/keyring.go

Purpose: generates and writes Ceph keyring content for admin and non-admin users, creates keys through Ceph auth APIs, and validates base64-encoded key strings.

Important APIs: `AdminKeyringTemplate` includes broad `allow *` caps for mds, mon, osd, and mgr. `UserKeyringTemplate` emits a minimal user section. `CephKeyring()` chooses the template based on `AdminUsername`. `CreateKeyring()` calls `AuthGetOrCreateKey()` with desired caps and writes generated content. `WriteKeyring()` creates parent dirs with 0700 and writes keyring files with 0600. `IsKeyringBase64Encoded()` decodes with standard base64 and logs on failure.

Control flow and persistence: this file writes secret material to disk and relies on caller-provided paths. `GenerateConnectionConfigWithSettings()` in `config.go` uses `WriteKeyring()` for the connection keyring. `CreateKeyring()` mutates Ceph auth state if the key does not exist and persists the resulting keyring locally.

Dependencies and integration: depends on auth helpers from other client files, `os`, `filepath`, and shared logger. Risks include sensitive key material in memory and files, overly broad admin capabilities, incorrect username qualification if callers pass unqualified non-admin names, and logging base64 decode errors for invalid secret data. No direct tests are present in this subset; indirect coverage comes from config generation writing keyrings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/keyring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mgr.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mgr.go

Purpose: wraps Ceph manager module status, module enable/disable, balancer configuration, and minimum client compatibility commands.

Important APIs: `CephMgrMap()` and `CephMgrStat()` parse `mgr dump` and `mgr stat` into types defined elsewhere in the package. `MgrEnableModule()`, `MgrDisableModule()`, `ConfigureBalancerModule()`, and helper functions `enableModule()`, `enableDisableBalancerModule()`, `setBalancerMode()`, `setMinCompatClient()`, `mgrSetBalancerMode()`, and `desiredMinCompatClientVersion()` implement module changes. Constants define read/upmap-read balancer modes and a mutable retry wait duration.

Control flow and state: `MgrEnableModule()` retries up to five times, skips enabling `balancer` because Ceph treats it differently, and sleeps `moduleEnableWaitTime` between failures. `MgrDisableModule()` maps balancer to `ceph balancer off`; other modules use `mgr module disable`. `ConfigureBalancerModule()` chooses a min compat client version, sets it, then sets balancer mode with retries. `desiredMinCompatClientVersion()` requires Ceph v19+ for `read` and `upmap-read`, returning `reef`; other modes use `luminous`.

Dependencies and integration: depends on Ceph version comparison, shared command execution, and manager map/stat structs from other package files. Risks include mutable package retry duration in tests, version-gate correctness as Ceph evolves, enabling/disabling modules without first checking current state, and the error text in `enableModule()` always saying "enable" even for disable. Tests cover retry behavior, module command construction, balancer on/off, mode setting, and version gating.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mgr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mgr_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mgr_test.go

Purpose: validates manager module retry behavior, command construction, balancer control, and balancer compatibility version decisions.

Important test cases: `TestEnableModuleRetries` sets `moduleEnableWaitTime = 0`, forces invalid module failures, and asserts five retries while valid modules and balancer skip do not retry. `TestEnableModule` covers module enable/disable with force and invalid actions. `TestEnableDisableBalancerModule` verifies `balancer on/off`. `TestSetBalancerMode` verifies `balancer mode upmap`. `TestGetMinCompatClientVersion` verifies `read` and `upmap-read` require Ceph major 19 and return `reef`, while `upmap` returns `luminous`.

Control flow and dependencies: tests use `exectest.MockExecutor`, `AdminTestClusterInfo()`, and `cephver.CephVersion`. They mutate `moduleEnableWaitTime`, which speeds tests but is package global.

Risks and coverage gaps: no tests cover `CephMgrMap()`, `CephMgrStat()`, JSON parse failures, `ConfigureBalancerModule()` full flow, set-min-compat command construction, or `mgrSetBalancerMode()` retry failures. Because `moduleEnableWaitTime` is not restored, parallel or subsequent tests could inherit the zero duration.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mirror.go

Purpose: manages RBD mirroring for pools and RADOS namespaces, including bootstrap peer import/export, mirroring enable/disable, peer removal, status/info reads, snapshot schedule reset/listing, namespace mirroring, and cluster-wide peer token creation.

Important APIs/types: `PeerToken` is the cluster-wide base64 JSON token shape. `MirroredImages` and `Images` model verbose mirror status. Public APIs include `ImportRBDMirrorBootstrapPeer()`, `CreateRBDMirrorBootstrapPeer()`, `DisablePoolMirroring()`, `RemoveClusterPeer()`, `GetPoolMirroringStatus()`, `GetMirroredPoolImages()`, `GetPoolMirroringInfo()`, `EnableSnapshotSchedules()`, `ListSnapshotSchedulesRecursively()`, `EnableRBDRadosNamespaceMirroring()`, `DisableRBDRadosNamespaceMirroring()`, and `CreateRBDMirrorBootstrapPeerWithoutPool()`. Internal helpers enable pool mirroring and snapshot schedules.

Control flow and persistence: bootstrap import writes the token to a temp file with 0400, optionally copies it into the Multus command-proxy container, imports it with `rbd mirror pool peer bootstrap import`, and defers local and remote cleanup. Pool mirroring first reads current mirror info and skips if mode already matches; `init-only` is gated on Tentacle support. Snapshot schedules are reset by listing and removing all existing schedules before adding desired ones. Namespace mirroring is gated on Ceph v20+ and normalizes the implicit namespace sentinel. Cluster-wide bootstrap token creation creates or rotates a Ceph auth key, gathers monitor endpoints, marshals JSON, and base64-encodes it.

Dependencies and integration: integrates with CephBlockPool and RadosNamespace controllers, auth helpers, Ceph version gates, Multus remote executor, and `cephv1` mirroring CRD status types. Risks include temp-file cleanup errors ignored locally, token exposure in errors or filesystem, partial schedule reset failures being logged then followed by adds, mutating `remoteNamespace` pointer in place, and version gates needing updates as Ceph changes. Tests cover bootstrap create/import, pool enable/status/info, schedules, peer removal, disable, and status compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health.go

Purpose: periodically reads RBD mirroring health/status and writes it into CephBlockPool or CephBlockPoolRadosNamespace custom-resource status fields.

Important APIs/types: `mirrorChecker` stores command context, interval, controller-runtime client, cluster info, object namespaced name, monitored pool spec, and target object type. `NewMirrorChecker()` configures the checker and respects `monitoringSpec.StatusCheck.Mirror.Interval`. `CheckMirroring()` runs an immediate check and then repeats on a timer until context cancellation. `CheckMirroringHealth()` reads mirror status, mirror info, and optional snapshot schedule status. `UpdateStatusMirroring()`, `updatePoolStatusMirroring()`, `updateRadosNamespaceStatusMirroring()`, and `toCustomResourceStatus()` implement CR status updates.

Control flow and persistence: the checker persists status by calling `reporting.UpdateStatus()` on Kubernetes API objects. Pool status updates fetch the pool and initialize status if nil. Rados namespace status updates use `RetryOnConflict`, fetch the namespace and parent pool, and clear mirroring status if parent pool status checks are disabled. `toCustomResourceStatus()` carries forward existing `LastChanged`, sets `LastChecked` when fresh data exists, and always records detail strings, usually errors.

Dependencies and integration: depends on `mirror.go` query functions, controller-runtime client, Kubernetes API errors, retry utilities, Rook reporting helpers, and ceph CRD status types. Risks include `CheckMirroringHealth()` continuing after errors and returning nil, possible nil `mirrorInfo` use when `mirrorStatus` is non-nil but info failed, timer-based loop using `time.After` each iteration, and status freshness semantics around empty snapshot schedules. Tests cover `toCustomResourceStatus()` only; Kubernetes update paths and error cases are untested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health_test.go

Purpose: validates conversion from live mirroring data into CRD status structs.

Important test case: `TestToCustomResourceStatus` builds a healthy mirroring summary and info object with one peer. The first subcase verifies status and info are populated when snapshot schedules are empty. The second subcase passes one snapshot schedule and verifies the returned snapshot schedule status is populated.

Control flow and dependencies: tests call `toCustomResourceStatus()` directly without Kubernetes clients or command execution. They use `cephv1` status types and testify assertions.

Risks and coverage gaps: no coverage exists for `NewMirrorChecker()`, polling loop cancellation, status update functions, retry conflict handling, not-found behavior, disabled parent status checks, error detail propagation with nil live data, preserving `LastChanged`, or nil `mirrorInfo` combined with non-nil `mirrorStatus`. The tests assert presence and a few key values but not timestamps.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mirror_test.go

Purpose: validates RBD mirroring command construction, status/info parsing, snapshot schedule operations, and peer lifecycle helpers.

Important test cases: tests cover bootstrap peer creation, enabling pool mirroring, reading pool mirroring status and verbose mirrored images, importing bootstrap peers with and without direction, reading mirror info, adding snapshot schedules with optional start time, listing schedules flat and recursively, removing schedules, resetting schedules, disabling mirroring, and removing peers. JSON fixtures such as `mirrorStatus`, `mirrorInfo`, schedule lists, and bootstrap token data drive parsing checks.

Control flow and dependencies: tests use mock executors and assert command-specific args before appended standard flags. They use `cephv1.NamedPoolSpec`/`PoolSpec` for mirror mode and snapshot schedule inputs. Import tests account for the generated temp token path by checking arg length and relative positions rather than exact path.

Risks and coverage gaps: this file gives strong coverage for the central pool mirroring paths, but does not cover Multus remote token copy/cleanup, temp-file write failures, `init-only` version gate, namespace mirroring enable/disable, cluster-wide bootstrap token creation/rotation, schedule reset behavior after list errors, malformed JSON, or status backward compatibility details beyond basic parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mirror_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mon.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mon.go

Purpose: wraps monitor quorum/dump reads and stretch-cluster monitor configuration commands.

Important APIs/types: `MonStatusResponse`, `MonMapEntry`, `AddrvecEntry`, `MonDump`, and `MonDumpEntry` model quorum and mon dump JSON. Public functions include `GetMonQuorumStatus()`, `GetMonDump()`, `EnableStretchElectionStrategy()`, `CreateDefaultStretchCrushRule()`, `SetMonStretchTiebreaker()`, and `SetNewTiebreaker()`.

Control flow and state: quorum and dump functions are read-only JSON commands. `EnableStretchElectionStrategy()` runs `mon set election_strategy connectivity`. `CreateDefaultStretchCrushRule()` builds a replicated pool spec using stretch cluster sub-failure-domain and delegates to CRUSH rule creation helpers defined elsewhere. `SetMonStretchTiebreaker()` runs `mon enable_stretch_mode <mon> <default-rule> <bucket-type>` and treats EINVAL containing "stretch mode is already engaged" as idempotent success. `SetNewTiebreaker()` mutates the active tiebreaker with `mon set_new_tiebreaker`.

Dependencies and integration: used by stretch-cluster reconciliation and monitor status flows. It depends on `cephv1.ClusterSpec`, CRUSH rule helpers, errno extraction, and shared command execution. Risks include string matching for idempotent stretch-mode errors, partial stretch configuration if CRUSH rule creation succeeds but tiebreaker setting fails, and JSON schema drift in monitor address structures. Tests cover arg finalization, election strategy, tiebreaker commands, and mon dump parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mon_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/mon_test.go

Purpose: validates Ceph command argument construction from a monitor-related perspective and tests stretch monitor operations and mon dump parsing.

Important test cases: `TestCephArgs` checks standard args for `ceph` and `rbd`, timeout flags, config/keyring paths, toolbox `kubectl` wrapping, and config-dir variants. `TestStretchElectionStrategy` asserts `mon set election_strategy connectivity`. `TestStretchClusterMonTiebreaker` asserts `mon enable_stretch_mode` and `mon set_new_tiebreaker` commands. `TestMonDump` parses a realistic mon dump fixture and checks election strategy, CRUSH location, mon names/ranks, and quorum size.

Control flow and dependencies: tests use `exec.CephCommandsTimeout`, `RunAllCephCommandsInToolboxPod`, mock executors, and `AdminTestClusterInfo()`. They reset the toolbox global after use.

Risks and coverage gaps: there is no direct test for `GetMonQuorumStatus()`, `CreateDefaultStretchCrushRule()`, idempotent stretch-mode already-engaged error handling, invalid JSON, or command errors. Like command tests, this file mutates globals and must be run carefully if tests become parallelized.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/mon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/osd.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/osd.go

Purpose: wraps OSD status, usage, CRUSH weight/device-class changes, safe-to-destroy checks, OSD tree/list queries, ok-to-stop checks, primary affinity, metadata, and client blocklisting.

Important APIs/types: `OSDUsage`, `OSDNodeUsage`, `OSDDump`, `SafeToDestroyStatus`, `OsdTree`, `OsdList`, `OSDDeviceClass`, `OSDOkToStopStats`, and `OSDMetadata` map Ceph JSON. Functions include flag helpers on `OSDDump`, `SetFlagOnCrushUnit()`, `UnsetFlagOnCrushUnit()`, `StatusByID()`, `GetOSDUsage()`, `ResizeOsdCrushWeight()`, `SetDeviceClass()`, `GetOSDDump()`, `OsdSafeToDestroy()`, `HostTree()`, `OsdListNum()`, `OSDDeviceClasses()`, `OSDOkToStop()`, `SetPrimaryAffinity()`, `GetOSDMetadata()`, and `Blocklist()`.

Control flow and state: most functions are direct Ceph command wrappers. `UpdateFlagOnCrushUnit()` avoids redundant set/unset commands by inspecting `CrushNodeFlags`. `ResizeOsdCrushWeight()` parses current CRUSH weight and KiB size, converts KiB to TiB, and reweights only when calculated weight is positive, greater than current, and more than 1 percent higher. `SetDeviceClass()` removes the current class before setting the desired one. `OSDOkToStop()` returns command failure as not safe and returns the queried ID plus an error if JSON parsing fails after command success.

Dependencies and integration: used heavily by OSD orchestration, upgrades, maintenance, and device class reconciliation. It depends on `json.Number` to preserve numeric precision, shared command execution, and Ceph CLI semantics. Risks include destructive/mutating operations, division by zero in the percentage calculation if current CRUSH weight is zero, `SetDeviceClass()` leaving an OSD classless if the second command fails, and a typo in `Blocklist()` error text. Tests cover tree/list parsing, device classes, KiB-to-TiB conversion, and ok-to-stop behavior; many mutation paths are untested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/osd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/osd_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/osd_test.go

Purpose: validates selected OSD query and maintenance helpers.

Important test cases: `TestHostTree` parses a fake OSD tree and checks invalid JSON behavior. `TestOsdListNum` parses OSD ID lists and invalid JSON. `TestOSDDeviceClasses` uses fake device class output and verifies both success and error paths. `TestConvertKibibytesToTebibytes` verifies conversion for 1024 KiB and 1 TiB in KiB. `TestOSDOkToStop` covers successful ok-to-stop output, command failure for unsafe OSDs, and `maxReturned=0` pass-through.

Control flow and dependencies: tests use `exectest.MockExecutor`, `AdminTestClusterInfo()`, fake OSD helpers, and Ceph version constants. They capture `seenArgs` to validate `osd ok-to-stop <id> --max=<n>`.

Risks and coverage gaps: the tests do not cover `OSDDump.StatusByID()`, flag setting/unsetting, `GetOSDUsage()`, `ResizeOsdCrushWeight()`, `SetDeviceClass()`, `OsdSafeToDestroy()`, `SetPrimaryAffinity()`, metadata, or blocklist behavior. Existing tests give useful signals for JSON decoding and command shape, but OSD mutation paths remain higher risk due to limited coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/osd_test.go -->
