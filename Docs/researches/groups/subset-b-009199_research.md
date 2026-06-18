# subset-b-009199 research

Grouped research for the Syncthing model, NAT, netutil, osutil, pmp, and protocol files listed in work item `subset-b-009199`. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/requests_test.go -->
## sources/sync-backup/syncthing/lib/model/requests_test.go

Purpose: integration-heavy model request tests that exercise synchronization through fake connections, local scans, request serving, index sender behavior, ignored/invalid transitions, conflicts, symlink protection, and receive-encrypted edge cases. The file is a test signal for the request/puller/index subsystems rather than a reusable API module.

Important tests and helpers: `TestRequestSimple` validates remote index update to local file creation and outgoing local index acknowledgement. `TestSymlinkTraversalRead`, `TestSymlinkTraversalWrite`, and `TestRequestCreateTmpSymlink` protect against reading or writing through symlink and temporary-file paths. `pullInvalidIgnored` backs skipped send-only/send-receive tests for ignored, deleted, and invalid global state transitions. `TestIssue4841`, `TestRescanIfHaveInvalidContent`, `TestIgnoreDeleteUnignore`, and `TestRequestGlobalInvalidToValid` cover invalid local content, ignore toggling, empty-version deletes, and global invalid-to-valid repair. Rename/delete conflict cases include skipped/flaky `TestRequestRemoteRenameChanged`, active `TestRequestRemoteRenameConflict`, and `TestRequestDeleteChanged`. `TestNeedFolderFiles`, `TestRequestLastFileProgress`, `TestRequestIndexSenderPause`, `TestRequestIndexSenderClusterConfigBeforeStart`, and `TestRequestReceiveEncrypted` cover queue visibility, progress, remote/local pause handling, startup ordering, and encrypted folder requests.

Control flow and state: tests build a fake model via `setupModelWithConnection`, mutate fake remote files, call `sendIndexUpdate`, then wait on callback channels from `fakeConnection` or events from `evLogger`. They frequently trigger scans through `ScanFolder`, `ScanFolders`, or `ScanFolderSubdirs`, and query state through `NeedFolderFiles`, `NeedSize`, `CurrentGlobalFile`, and `LocalChangedFolderFiles`. Several tests rely on timeouts as synchronization boundaries because the puller and index sender are asynchronous.

Dependencies and integration points: uses `config`, `events`, fake filesystem `fs`, protocol file metadata, fake connections, and model internals such as folder runners and database updates. The tests cover integration with ignore matchers, receive-only/receive-encrypted folder types, cluster config state, and protected symlink traversal behavior.

Risks: many scenarios are timing-sensitive; three tests are explicitly skipped as flaky. Timeout-based "nothing should happen" assertions can miss delayed regressions. The tests mutate model internals and fake connection state, so helper behavior changes can mask real request regressions. Symlink tests skip on Windows, leaving Windows behavior covered separately by unsupported symlink invalidation.

Test signals: the file itself is the signal for request/puller behavior. Passing tests indicate safe block request routing, conflict preservation, ignore transition correctness, and index sender pause/resume semantics under the fake model harness.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/requests_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/sentdownloadstate.go -->
## sources/sync-backup/syncthing/lib/model/sentdownloadstate.go

Purpose: tracks which partial download blocks have already been advertised to a remote device so download-progress messages can be sent as append/forget deltas instead of full state snapshots.

Important types and functions: `sentFolderFileDownloadState` stores block indexes, version, creation time, update time, and block size for one file. `sentFolderDownloadState.update` compares active `sharedPullerState` instances to previously sent state and emits `protocol.FileDownloadProgressUpdate` values. `destroy` emits forget updates for all tracked files. `sentDownloadState` groups folder states and exposes `update`, `folders`, and `cleanup`.

Control flow and state: each update pass builds a `seen` set from active pullers. New files are announced only when they have at least one available block. Existing files are ignored when available-block timestamp and version match. Version or puller recreation changes trigger a forget for the old version followed by append for the new state. Otherwise the code assumes `sharedPullerState.Available()` is append-only and slices new block indexes from the previous length. Pullers missing from the pass are treated as completed or failed and generate forget updates.

Dependencies and integration points: reads `sharedPullerState.file`, `Available`, `AvailableUpdated`, and `created`, and emits protocol download progress updates consumed by BEP connections. It is used from a single progress emitter routine, so it deliberately has no locking.

Risks: correctness depends on append-only ordering and stable timestamps from `sharedPullerState`; if the available slice is reordered or truncated, slicing by previous length can panic or send wrong deltas. Map iteration makes forget ordering nondeterministic. Lack of internal synchronization is acceptable only while the single-routine invariant holds.

Test signals: no direct test in this subset. Indirect coverage appears in request/progress tests such as `TestRequestLastFileProgress` and protocol download progress serialization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/sentdownloadstate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/service_map.go -->
## sources/sync-backup/syncthing/lib/model/service_map.go

Purpose: generic utility that maps arbitrary keys to `suture.Service` instances and manages their lifecycle under an internal supervisor.

Important APIs: `newServiceMap` constructs the map and supervisor with event logging. `Add` replaces any existing service for a key, starts the new service through the supervisor, and stores its token. `Get`, `Stop`, `StopAndWaitChan`, `Remove`, `RemoveAndWait`, `RemoveAndWaitChan`, and `Each` provide keyed lifecycle and iteration operations. `Serve` runs the internal supervisor; `String` identifies the service.

Control flow and state: state is two maps, one from key to service and one from key to supervisor token. `Add` calls `Remove` first to avoid duplicate services. `Stop` removes the service from the supervisor but keeps it in `services`; `Remove` stops and deletes both maps. Wait variants return or consume a single error from supervisor removal. `Each` snapshots keys before iteration so callbacks can mutate the map, including removing current entries.

Dependencies and integration points: built on `github.com/thejerf/suture/v4`, `svcutil.AsService`, and `events.Logger`. It is intended for model-owned folder or device service collections where keyed add/remove must stay paired with supervisor membership.

Risks: explicitly not safe for concurrent use; callers must serialize access. Stopped services remain addressable after `Stop`, which is intentional but can surprise code expecting absence. Misusing wait timeouts can leak asynchronous stop errors if the channel is ignored.

Test signals: `service_map_test.go` covers add/remove startup, replacement stopping the old service, and removal while iterating.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/service_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/service_map_test.go -->
## sources/sync-backup/syncthing/lib/model/service_map_test.go

Purpose: verifies lifecycle semantics of `serviceMap` with dummy suture services and a real supervisor.

Important tests and helpers: `TestServiceMap` has subtests for simple add/remove, overwrite implying removal of the previous service, and `Each` with `RemoveAndWait` during iteration. `dummyService` closes `started` and `stopped` channels around a context wait, giving deterministic lifecycle observations.

Control flow and state: the test starts one outer supervisor, adds a `serviceMap`, then manipulates dummy services under it. It waits on service channels to prove supervisor start/stop propagation. The iteration test removes keys prefixed with `remove` while retaining `keep` services.

Dependencies and integration points: uses `events.NoopLogger` and `suture.NewSimple`. It validates that service-map mutation is compatible with suture tokens and callback-driven iteration.

Risks: subtests call `t.Parallel` while sharing the outer supervisor. The tested `serviceMap` is not concurrent-safe, but each instance is local to a subtest; the shared supervisor must tolerate concurrent additions. No timeout guards around channel waits, so a lifecycle regression can hang until the global test timeout.

Test signals: strong coverage for the documented semantics of replacement, deletion, and iteration mutation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/service_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/sharedpullerstate.go -->
## sources/sync-backup/syncthing/lib/model/sharedpullerstate.go

Purpose: per-file state object used by pullers while syncing a file. It coordinates temporary file creation, concurrent block writes/copies, progress counters, available-block discovery, encrypted trailer finalization, sparse-file sizing, and final close.

Important types and functions: `sharedPullerState` holds immutable file/fs/folder/temp metadata plus mutable counters and writer state protected by an RW mutex. `newSharedPullerState` builds current-file block lookup, initializes reused/available blocks, and timestamps. `lockedWriterAt` serializes close against concurrent `WriteAt`; `SyncClose` optionally fsyncs. `tempFile`, `addWriterLocked`, and `tempFileInWritableDir` create or reopen temp files with permissions, hiding, sparse truncation, and reuse handling. Progress APIs include `copyDone`, `copiedFromOrigin`, `copiedFromElsewhere`, `skippedSparseBlock`, `pullStarted`, `pullDone`, `Progress`, `Updated`, `AvailableUpdated`, and `Available`. `finalClose`, `finalizeEncrypted`, `writeEncryptionTrailer`, and `encryptionTrailerSize` finish the file and append metadata for encrypted files.

Control flow and state: pull work starts with `copyTotal/copyNeeded` set to candidate local blocks and `reused` blocks available. A block that must be fetched calls `pullStarted`, moving work from copy to pull, then `pullDone` appends its block index to `available`. Local copies call `copyDone`. `finalClose` returns `(false,nil)` while work remains and no error exists; once all work is done or an error exists it ensures a writer exists, writes an encrypted trailer when needed, closes and un-hides the temp file, and returns the first error. Failures are sticky through `failLocked`.

Persistence and filesystem behavior: temp files are opened through the folder `fs.Filesystem`, created exclusive when not reusing, chmodded before reuse when permissions are enforced, hidden while active, and unhidden at close. Sparse mode truncates to final size plus encrypted trailer; if truncation fails on a reused larger temp file, the temp file is removed to avoid stale tail data. Final encrypted files append serialized native `FileInfo` in wire-name form plus a four-byte length.

Dependencies and integration points: uses `fs`, `osutil.NormalizedFilename`, protocol `FileInfo`/`BlockInfo`, protobuf sizing, `protoutil.MarshalTo`, and model metrics `metricFolderProcessedBytesTotal`. It feeds download progress through `Available` and integrates with request/puller finalization.

Risks: concurrency depends on correct mutex discipline and the append-only `available` invariant. `Available` returns the backing slice, so callers must treat it as read-only. Sparse truncation failures have nuanced cleanup behavior. Encryption trailer sizing uses `proto.Size` then marshals again; metadata changes must keep size calculations aligned. Permissions and hidden-file behavior are platform/filesystem dependent.

Test signals: `sharedpullerstate_test.go` covers read-only directory temp-file creation in the fake filesystem. Request tests indirectly cover progress and encrypted receive behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/sharedpullerstate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/sharedpullerstate_test.go -->
## sources/sync-backup/syncthing/lib/model/sharedpullerstate_test.go

Purpose: regression test for creating temporary puller files inside a read-only directory on Syncthing's fake filesystem.

Important test: `TestReadOnlyDir` creates a fake filesystem directory with mode `0555`, constructs a minimal `sharedPullerState` pointing to a temp file inside it, calls `tempFile`, asserts a non-nil descriptor, then final-closes the state.

Control flow and state: the test exercises `inWritableDir` through `sharedPullerState.tempFile`, confirming that directory permissions can be temporarily handled for temp-file creation. It also verifies `fail(nil)` is a no-op and `finalClose` can clean up the opened writer.

Dependencies and integration points: uses fake filesystem and random path roots. It is focused on permission handling in the puller temp-file path.

Risks: fake filesystem behavior may not model all host filesystem permission nuances, especially Windows ACLs or network filesystems.

Test signals: narrow but useful coverage of temp file creation under restrictive parent permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/sharedpullerstate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/testos_test.go -->
## sources/sync-backup/syncthing/lib/model/testos_test.go

Purpose: small test helper module defining common fatal/panic convenience functions for model tests.

Important APIs: `fatal` is the shared interface between `*testing.T` and `*testing.B` requiring `Fatal` and `Helper`. `must` marks itself as helper and fatals on non-nil error. `mustV` returns a value or panics on error for use where a testing object is not available.

Control flow and state: stateless helpers only.

Dependencies and integration points: used throughout model tests to reduce repetitive error handling. `mustV` is suitable for package-level or inline initialization where failing a test directly is not available.

Risks: `mustV` panics instead of failing a specific test, so use in concurrent or shared setup can produce less localized failures.

Test signals: no tests for the helpers; behavior is trivial and exercised indirectly by many model tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/testos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/testutils_test.go -->
## sources/sync-backup/syncthing/lib/model/testutils_test.go

Purpose: central test harness for model tests. It provides deterministic device IDs, default fake-folder configuration, config wrappers, model startup/cleanup, fake connection setup, ignore matcher substitution, cluster config helpers, local index event injection, config mutation helpers, and file-writing utilities.

Important APIs/types: package globals define `myID`, `device1`, `device2`, default wrappers/configs, and mocked connections. `newConfigWrapper`, `newDefaultCfgWrapper`, `newFolderConfig`, `setupModelWithConnection`, `setupModel`, `newModel`, and `testModel.ServeBackground` construct running model instances backed by sqlite temp DBs and fake filesystems. `cleanupModel` and `cleanupModelAndRemoveDir` stop services, events, DBs, and filesystem roots. `alwaysChanged` and `folderIgnoresAlwaysReload` force ignore reloads for tests. Helpers such as `basicClusterConfig`, `localIndexUpdate`, `pauseFolder`, `setFolder`, `setDevice`, `addDevice2`, `writeFile`, and `writeFilePerm` mutate model/config/filesystem state.

Control flow and state: `init` prepares a default config wrapper served in the background, sets fake device behavior, disables disk-free checks, and records a default folder config. Each test generally clones raw config into a new wrapper served under the test context, opens a temp sqlite DB, starts model and event logger goroutines, and scans folders before assertions. Cleanup cancels model and event contexts and removes config paths.

Dependencies and integration points: integrates `internal/db/sqlite`, `config`, `events`, fake `fs`, `ignore`, `protocol`, generated mocks, and random path generation. This harness is foundational for model request, folder, index, and config tests.

Risks: shared package-level defaults can leak assumptions into tests. Direct calls to model internals such as `removeFolder` and `addAndStartFolderLockedWithIgnores` make tests sensitive to internal refactors. Failure to call cleanup can leave goroutines or temp DB resources.

Test signals: not tested directly, but nearly every model test in this package depends on it; failures here cascade broadly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/testutils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/util.go -->
## sources/sync-backup/syncthing/lib/model/util.go

Purpose: miscellaneous model utilities for performing operations inside otherwise non-writable directories and for accumulating elapsed time into a Prometheus counter until context cancellation.

Important functions: `inWritableDir(fn, targetFs, path, ignorePerms)` temporarily ensures user write/execute permission on the parent directory of `path`, runs `fn`, and restores original permissions when needed. `addTimeUntilCancelled(ctx, counter)` periodically adds elapsed seconds to a counter until the context is done, then accounts for the final partial duration.

Control flow and state: `inWritableDir` stats the directory unless permissions are ignored or the build target is Windows. If user write/execute bits are already present it runs directly. Otherwise it chmods the parent to include `0700`, defers restoring the original mode, then invokes the callback. `addTimeUntilCancelled` uses a ten-second ticker and `time.Since(start)` to add increments.

Dependencies and integration points: uses `build.IsWindows`, `fs.Filesystem`, and Prometheus counters. It is used by puller/temp-file and file operation paths that need to create/remove files in read-only directories.

Risks: permission restoration errors are returned only after the callback path via deferred function behavior; callers must handle errors. Directory chmod semantics vary across fake, Windows, Unix, and network filesystems. `addTimeUntilCancelled` assumes a monotonic clock and that counter increments can tolerate approximate tick cadence.

Test signals: `utils_test.go` covers writable-dir behavior and Windows remove/rename scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/utils_test.go -->
## sources/sync-backup/syncthing/lib/model/utils_test.go

Purpose: tests `inWritableDir` permission-tweaking behavior and Windows-specific filesystem workarounds around read-only directories and files.

Important tests: `TestInWriteableDir` checks callback execution inside a read-only fake directory and restoration of directory permissions. `TestOSWindowsRemove`, `TestOSWindowsRemoveAll`, and `TestInWritableDirWindowsRename` are Windows-only tests for removing or renaming read-only files/directories using fake/basic filesystems and the model helper.

Control flow and state: tests create temporary fake or basic filesystems, apply restrictive chmod modes, call `inWritableDir` or filesystem remove/rename operations, and assert final existence or contents.

Dependencies and integration points: relies on `build.IsWindows`, fake filesystem behavior, and `rand` path generation. It validates helper assumptions used by puller and osutil file operations.

Risks: platform-gated tests leave non-Windows behavior partly dependent on fake filesystem semantics. Permission behavior can differ by host filesystem mount options.

Test signals: targeted coverage for permission restoration and Windows read-only file handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/debug.go -->
## sources/sync-backup/syncthing/lib/nat/debug.go

Purpose: defines the package-level logging adapter for NAT discovery and port mapping.

Important API: variable `l = slogutil.NewAdapter("NAT discovery and port mapping")` is used by NAT service code for debug logging.

Control flow and state: no runtime control flow beyond package initialization.

Dependencies and integration points: depends on `internal/slogutil`; used by `service.go` for debug traces around discovery, renewals, and mapping attempts.

Risks: none beyond logging category naming consistency.

Test signals: no direct tests; logging adapter behavior is covered elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/interface.go -->
## sources/sync-backup/syncthing/lib/nat/interface.go

Purpose: declares the common NAT/firewall traversal abstraction used by NAT providers such as NAT-PMP and UPnP.

Important APIs: `Protocol` constants `TCP` and `UDP`; `IPVersion` constants `IPvAny`, `IPv4Only`, and `IPv6Only`; `Device` interface with ID, local IPv4 gateway address, port mapping, IPv6 pinhole, external IPv4 address, and IP-version support methods.

Control flow and state: pure type definitions.

Dependencies and integration points: `nat.Service` consumes `Device` implementations from registered discoverers. `pmp.wrapper` implements this interface for NAT-PMP. Other packages create `Mapping` values with protocol and IP version constraints.

Risks: the interface mixes IPv4 mapping and IPv6 pinhole capabilities; implementations must return accurate `SupportsIPVersion` values or the service can attempt unsupported operations.

Test signals: exercised indirectly by NAT service and PMP integration; no direct interface tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/registry.go -->
## sources/sync-backup/syncthing/lib/nat/registry.go

Purpose: global registry for NAT discovery providers and concurrent discovery fan-out.

Important APIs: `DiscoverFunc` is the provider signature. `Register` appends a provider to the global list. `discoverAll` runs all providers concurrently and returns a map from device ID to discovered `Device`.

Control flow and state: `discoverAll` starts one goroutine per provider, streams discovered devices through a channel, and uses a collector goroutine to fill the result map until all providers finish or context is canceled. Duplicate IDs are overwritten by the last received device.

Dependencies and integration points: providers register in package `init` functions such as `pmp.init`. `nat.Service.process` calls `discoverAll` before mapping renewal/acquisition.

Risks: `providers` is a package-level slice with no registration lock; registration is expected during init. Provider functions must respect context or discovery can block service processing. Duplicate provider IDs are silently overwritten.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/service.go -->
## sources/sync-backup/syncthing/lib/nat/service.go

Purpose: long-running service that discovers NAT/firewall devices and creates or renews external mappings for registered local listener addresses.

Important APIs: `NewService`, `CommitConfiguration`, `Serve`, `NewMapping`, and `RemoveMapping` are the public lifecycle surface. Internal functions `process`, `scheduleProcess`, `updateMapping`, `verifyExistingLocked`, `acquireNewLocked`, `tryNATDevice`, `hash`, and `addrSetsEqual` implement discovery and mapping state transitions.

Control flow and state: the service subscribes to config changes and tracks `enabled`, mappings, and a buffered process trigger under a mutex. `Serve` reacts to timer ticks, scheduled process events, and context cancellation. `process` classifies mappings as due for renewal or waiting, skips discovery when nothing needs renewal, discovers NAT devices, renews expired mappings, and opportunistically updates existing mappings. `updateMapping` sets a new expiry, verifies known NAT devices, acquires missing NAT devices, and notifies subscribers on changes. `tryNATDevice` uses IPv6 pinholes when supported; otherwise it uses deterministic pseudo-random external-port attempts seeded by device ID, local port, and NAT ID, trying requested or generated ports through `AddPortMapping`.

State and persistence: mapping state is in memory only. `Mapping.extAddresses` holds external addresses per NAT device ID; `expires` schedules renewal. On service shutdown, all mapping addresses are cleared and subscribers are notified through `Mapping.clearAddresses`; the code does not explicitly delete mappings from gateways, matching `RemoveMapping` semantics.

Dependencies and integration points: depends on `config.Wrapper` NAT options (`NATEnabled`, renewal, timeout, lease), protocol device ID for deterministic port selection, registered NAT providers, and `Mapping` notifications used by discovery/announcement code.

Risks: renewal timing depends on config values; zero renewal falls back to 30 minutes for scheduling but discovery still receives the configured renewal duration. The mapping mutex is held while calling NAT devices, which can block address readers/subscribers if devices hang despite contexts. External port selection is deterministic, useful for stability but can collide. `RemoveMapping` does not remove gateway mappings, so stale leases rely on expiry.

Test signals: no direct service test here. `structs_test.go` covers `Mapping` address/gateway helpers used by the service.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/structs.go -->
## sources/sync-backup/syncthing/lib/nat/structs.go

Purpose: data structures representing a requested local mapping and externally visible addresses assigned by NAT devices.

Important types/functions: `MappingChangeSubscriber`, `Mapping`, and `Address`. `Mapping` methods include `setAddressLocked`, `removeAddressLocked`, `clearAddresses`, `notify`, `Protocol`, `Address`, `ExternalAddresses`, `OnChanged`, `String`, `GoString`, and `validGateway`. `Address` provides `Equal`, `String`, and `GoString`.

Control flow and state: `Mapping` stores requested protocol/local address, IP version, a per-device map of external addresses, expiry time, and change subscribers under an RW mutex. Address setters/removers require the caller to hold the write lock and then call `notify` outside service-level decisions. `ExternalAddresses` flattens all per-device address slices. `clearAddresses` drops all external addresses and notifies. `validGateway` allows wildcard local IPs or exact local gateway IP matches.

Dependencies and integration points: used by `Service` to expose mapping results and by discovery/announcement code to subscribe to changes. Address formatting relies on `net.JoinHostPort`.

Risks: subscriber callbacks run synchronously in `notify`; a slow or reentrant subscriber can block NAT processing. `ExternalAddresses` order is map-dependent. Callers must respect lock expectations for `setAddressLocked`/`removeAddressLocked`.

Test signals: `structs_test.go` covers gateway matching and clearing addresses.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/structs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/structs_test.go -->
## sources/sync-backup/syncthing/lib/nat/structs_test.go

Purpose: tests core `Mapping` helper behavior.

Important tests: `TestMappingValidGateway` checks wildcard, matching IPv4, and mismatching IPv4 gateway behavior. `TestMappingClearAddresses` sets multiple external address entries, subscribes to change notifications, clears addresses, and verifies both notification count and empty external address state.

Control flow and state: tests manipulate `Mapping` internals under the mapping mutex for setup, then call exported methods to assert behavior.

Dependencies and integration points: uses `net.ParseIP` and NAT `Address` values. It validates assumptions used by `Service.acquireNewLocked` and `verifyExistingLocked`.

Risks: does not test ordering, synchronous subscriber blocking, or concurrent access.

Test signals: focused coverage for gateway filtering and address clear notifications.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/nat/structs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/interfaces_android.go -->
## sources/sync-backup/syncthing/lib/netutil/interfaces_android.go

Purpose: Android-specific network interface enumeration using `github.com/wlynxg/anet` instead of Go's standard `net` package.

Important APIs: `Interfaces` returns `anet.Interfaces`; `InterfaceAddrsByInterface` returns `anet.InterfaceAddrsByInterface`.

Control flow and state: simple wrappers with no state.

Dependencies and integration points: used by OS/network utility code that needs reliable interface addresses on Android. Complements `interfaces_other.go`.

Risks: depends on `anet` behavior and Android permissions/platform APIs. Build constraints rely on filename suffix for Android selection.

Test signals: no Android-specific tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/interfaces_android.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/interfaces_other.go -->
## sources/sync-backup/syncthing/lib/netutil/interfaces_other.go

Purpose: non-Android network interface enumeration using the standard library.

Important APIs: `Interfaces` calls `net.Interfaces`; `InterfaceAddrsByInterface` calls `intf.Addrs`.

Control flow and state: stateless wrappers under `!android` build constraint.

Dependencies and integration points: used by network utility code and NAT gateway matching on all non-Android platforms.

Risks: standard library interface enumeration can return platform-specific errors or omit down/permission-limited interfaces; callers filter as needed.

Test signals: indirectly exercised by osutil network tests, not directly here.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/interfaces_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/netutil.go -->
## sources/sync-backup/syncthing/lib/netutil/netutil.go

Purpose: network helpers for URL-like address construction and default gateway discovery.

Important APIs: `AddressURL(network, host)` builds a URL string with the network as scheme and host as host. `Gateway` returns the default gateway from `github.com/jackpal/gateway`, with Android-oriented environment fallback `FALLBACK_NET_GATEWAY_IPV4`.

Control flow and state: `AddressURL` constructs a `url.URL` and returns its string. `Gateway` calls `gateway.DiscoverGateway`; on error it checks the fallback environment variable, validates it with `net.ParseIP`, and returns either the parsed IP or an invalid-IP error.

Dependencies and integration points: `pmp.Discover` uses `Gateway` to instantiate a NAT-PMP client. Address URL helpers can be used by listener/dialer configuration formatting.

Risks: environment fallback trusts process environment and only validates parseability, not reachability. Gateway discovery can fail on Android 14+ due to `/proc/net/route` restrictions. `AddressURL` does not validate schemes or hosts.

Test signals: `netutil_test.go` covers basic URL construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/netutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/netutil_test.go -->
## sources/sync-backup/syncthing/lib/netutil/netutil_test.go

Purpose: validates `AddressURL` formatting.

Important test: `TestAddress` checks several network/host combinations such as `tcp` and arbitrary strings, expecting `scheme://host`.

Control flow and state: table-driven, stateless.

Dependencies and integration points: exercises only local string construction, not gateway discovery.

Risks: no tests for IPv6 host formatting, empty values, escaping, or fallback gateway behavior.

Test signals: narrow smoke coverage for URL construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/netutil/netutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/atomic.go -->
## sources/sync-backup/syncthing/lib/osutil/atomic.go

Purpose: atomic-ish file writer that writes to a secure temporary file in the destination directory and renames it into place on close.

Important APIs: `ErrClosed`, `TempPrefix`, `AtomicWriter`, `CreateAtomic`, `CreateAtomicFilesystem`, `Write`, and `Close`.

Control flow and state: `CreateAtomic` wraps a basic filesystem rooted at the destination directory; `CreateAtomicFilesystem` creates a secure temp file with `TempFile`. `Write` accumulates the first write error and closes the temp file on failure. `Close` removes the temp file on exit, syncs the temp file best-effort, closes it, records existing destination mode, renames temp to final path, handles Windows read-only rename by chmod/retry, restores previous mode if possible, fsyncs the containing directory best-effort, and marks the writer closed by setting `ErrClosed`.

Persistence behavior: successful close replaces or creates the target path. Existing file mode is preserved after replacement when supported. The temp file is in the same directory for same-filesystem rename semantics, and directory fsync improves crash durability where supported.

Dependencies and integration points: uses Syncthing `fs.Filesystem`, `TempFile`, `build.IsWindows`, and path handling. Used anywhere Syncthing needs durable config/state writes.

Risks: not safe for multiple close/write calls after close beyond returning stored error. Rename atomicity depends on filesystem semantics. Chmod restoration can fail on filesystems without chmod support and is tolerated only if resulting mode matches. The deferred temp removal ignores errors.

Test signals: `atomic_test.go` and `atomic_unix_test.go` cover create, replace, read-only replacement, and temp permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/atomic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/atomic_test.go -->
## sources/sync-backup/syncthing/lib/osutil/atomic_test.go

Purpose: tests creation and replacement behavior of `AtomicWriter`.

Important tests: `TestCreateAtomicCreate` verifies target file does not appear before close and contains written data after close. `TestCreateAtomicReplace` and `TestCreateAtomicReplaceReadOnly` share `testCreateAtomicReplace` to replace existing writable and read-only files while preserving old permissions.

Control flow and state: tests create temp directories/files, write through `CreateAtomic`, close, read final data, and stat permissions.

Dependencies and integration points: uses real OS filesystem paths, not fake filesystem, so it exercises platform rename/chmod behavior.

Risks: permission checks can vary by OS; read-only mode handling is especially platform-sensitive.

Test signals: strong regression coverage for atomic create/replace and mode preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/atomic_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/atomic_unix_test.go -->
## sources/sync-backup/syncthing/lib/osutil/atomic_unix_test.go

Purpose: Unix-specific test ensuring atomic temp files start with secure permissions.

Important test: `TestTempFilePermissions` creates an atomic writer, stats the temp file before close, and verifies mode `0600`.

Control flow and state: the test observes the temporary file directly through `w.next.Name()` before the final rename.

Dependencies and integration points: relies on Unix permission semantics and `CreateAtomic`/`TempFile`.

Risks: unavailable on non-Unix platforms; umask or filesystem semantics could affect expectations if temp creation changes.

Test signals: security-relevant coverage for temp file permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/atomic_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/filenames_darwin.go -->
## sources/sync-backup/syncthing/lib/osutil/filenames_darwin.go

Purpose: Darwin filename normalization helpers.

Important APIs: `NormalizedFilename` returns NFC form for Syncthing wire/internal normalized names; `NativeFilename` returns NFD form expected by macOS filesystems.

Control flow and state: stateless calls to `golang.org/x/text/unicode/norm`.

Dependencies and integration points: used where Syncthing converts between native filesystem names and normalized protocol names, including encrypted trailer metadata in model puller state.

Risks: Unicode normalization mistakes can cause duplicate or inaccessible names across platforms.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/filenames_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/filenames_unix.go -->
## sources/sync-backup/syncthing/lib/osutil/filenames_unix.go

Purpose: filename normalization helpers for non-Windows, non-Darwin Unix-like platforms.

Important APIs: `NormalizedFilename` converts to NFC; `NativeFilename` returns the input unchanged.

Control flow and state: stateless.

Dependencies and integration points: used by filesystem/protocol conversion paths on Linux/BSD and other Unix targets.

Risks: assumes native filesystems do not require decomposition or separator conversion.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/filenames_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/filenames_windows.go -->
## sources/sync-backup/syncthing/lib/osutil/filenames_windows.go

Purpose: Windows filename normalization helpers.

Important APIs: `NormalizedFilename` converts path separators to slashes and normalizes Unicode to NFC; `NativeFilename` converts slashes to Windows separators.

Control flow and state: stateless path and Unicode conversions.

Dependencies and integration points: used when translating between protocol paths and native Windows paths. Important for request/symlink and encrypted metadata paths.

Risks: path separator conversion must not be applied to already-native strings in the wrong direction. Unicode normalization can interact with case-insensitive filesystem behavior.

Test signals: indirectly covered by Windows-specific model tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/filenames_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/hidden_unix.go -->
## sources/sync-backup/syncthing/lib/osutil/hidden_unix.go

Purpose: no-op console hiding implementation for non-Windows platforms.

Important API: `HideConsole` does nothing.

Control flow and state: none.

Dependencies and integration points: platform counterpart to Windows console hiding.

Risks: none.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/hidden_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/hidden_windows.go -->
## sources/sync-backup/syncthing/lib/osutil/hidden_windows.go

Purpose: Windows implementation for hiding the console window.

Important API: `HideConsole` dynamically looks up `GetConsoleWindow` and `ShowWindow`; if a console window exists it calls `ShowWindow(hwnd, 0)`.

Control flow and state: uses lazy DLL loading and only calls functions if lookup succeeds.

Dependencies and integration points: used by Windows GUI/background startup paths.

Risks: direct syscall use and window-handle handling are Windows-specific. Failures are silently ignored.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/hidden_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_linux.go -->
## sources/sync-backup/syncthing/lib/osutil/lowprio_linux.go

Purpose: Linux-specific lowering of process CPU priority, with process-group handling to affect all threads.

Important API: `SetLowPriority` checks current kernel nice value, moves the process into its own process group when needed, then calls `syscall.Setpriority` for the process group.

Control flow and state: if current priority is already low enough it returns nil. Otherwise it ensures process group leadership through `Getpgid` and `Setpgid`, then sets priority to the kernel-translated value for user nice 9.

Dependencies and integration points: called during startup when Syncthing is configured to run with lower CPU/IO priority.

Risks: process group changes can fail under supervisors or permission constraints. Linux nice values use inverted kernel representation, making constants subtle. Errors are returned for callers to log/handle.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_noop.go -->
## sources/sync-backup/syncthing/lib/osutil/lowprio_noop.go

Purpose: iOS no-op implementation of priority lowering.

Important API: `SetLowPriority` returns nil.

Control flow and state: none.

Dependencies and integration points: selected by iOS build tags to satisfy the cross-platform API.

Risks: callers may believe priority was lowered when the platform cannot do it; this is intentional.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_noop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_unix.go -->
## sources/sync-backup/syncthing/lib/osutil/lowprio_unix.go

Purpose: generic Unix priority lowering for non-Windows, non-Linux, non-iOS targets and Android.

Important API: `SetLowPriority` checks current process priority and calls `syscall.Setpriority` to set nice level 9 when needed.

Control flow and state: if current nice is already at or below desired priority, returns nil; otherwise attempts to set priority for process zero.

Dependencies and integration points: platform API counterpart to Linux and Windows implementations.

Risks: build expression includes Android via the `|| android` part; priority syscalls can fail due to platform permissions.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_windows.go -->
## sources/sync-backup/syncthing/lib/osutil/lowprio_windows.go

Purpose: Windows implementation for lowering process priority.

Important API: `SetLowPriority` opens the current process and sets priority class to idle/background-equivalent through Windows syscalls.

Control flow and state: the function calls Windows process priority APIs and returns wrapped errors on failure.

Dependencies and integration points: selected on Windows builds for startup priority configuration.

Risks: Windows permissions/API availability can cause failures; behavior differs from Unix nice values.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/lowprio_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/net.go -->
## sources/sync-backup/syncthing/lib/osutil/net.go

Purpose: helpers for interface address enumeration and IP extraction from strings or `net.Addr`.

Important APIs: `GetInterfaceAddrs(includePtP)` returns IP networks for up interfaces while excluding loopback and, by default, point-to-point interfaces. `IPFromString` parses host:port or raw host strings. `IPFromAddr` extracts IPs from `*net.TCPAddr`, `*net.UDPAddr`, `*net.IPAddr`, and `*net.IPNet`.

Control flow and state: `GetInterfaceAddrs` obtains interfaces through `netutil.Interfaces`, filters flags, obtains addresses via `netutil.InterfaceAddrsByInterface`, extracts IPs, and appends only valid `*net.IPNet` addresses. `IPFromString` first tries `net.SplitHostPort`, then raw parse. `IPFromAddr` switches on address type and returns an error for unsupported types.

Dependencies and integration points: used by NAT mapping gateway validation and address/listener selection. Android behavior depends on `netutil` wrappers.

Risks: interface filtering can omit useful point-to-point addresses unless requested. Unsupported address types return errors. Host parsing can treat malformed host:port strings as raw IP parse failures.

Test signals: `osutil_test.go` covers `IPFromString`; other functions are indirectly covered.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/net.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/osutil.go -->
## sources/sync-backup/syncthing/lib/osutil/osutil.go

Purpose: native OS file operation utilities for robust rename/copy, target preparation, deletion detection, and directory size calculation.

Important APIs: `RenameOrCopy`, `Copy`, `withPreparedTarget`, `copyFileContents`, `IsDeleted`, and `DirSize`. Package-level `renameLock` serializes rename/copy target preparation.

Control flow and state: `RenameOrCopy` locks, attempts rename when source and destination filesystems match, falls back to copy on failure, and removes source after successful copy. `Copy` also locks and delegates to `withPreparedTarget`. `withPreparedTarget` removes existing target files or directory trees and temporarily grants parent directory write permission through `fs.InWritableDir`. `copyFileContents` opens source and destination, uses the filesystem `CopyRangeMethod`, syncs and closes with deferred error propagation. `IsDeleted` stats a path and returns true only for not-exist. `DirSize` walks a real OS directory and sums non-directory sizes.

Persistence behavior: copy writes destination with source mode, syncs destination file, and removes source only after copy success. Directory operations are best-effort around permissions through `InWritableDir`.

Dependencies and integration points: relies on Syncthing `fs.Filesystem` abstractions and is used by model/puller code for final placement and conflict handling.

Risks: rename/copy is serialized globally, which avoids races but can become a bottleneck. Cross-filesystem rename behavior depends on the filesystem implementation returning errors. Removing existing targets before copy means a later copy failure can leave no destination. Directory size ignores walk errors beyond returning zero for inaccessible trees.

Test signals: `osutil_test.go` covers deletion detection, rename/copy, and IP parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/osutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/osutil_test.go -->
## sources/sync-backup/syncthing/lib/osutil/osutil_test.go

Purpose: tests deletion detection, rename/copy semantics, and IP string parsing.

Important tests: `TestIsDeleted` checks missing, present, and error cases. `TestRenameOrCopy` creates source/destination fake filesystems, exercises `RenameOrCopy`, and verifies destination data and source removal. `TestIPFromString` checks host:port and raw IP parsing.

Control flow and state: tests create temporary fake or OS-backed paths, mutate files, call osutil helpers, and assert final filesystem state.

Dependencies and integration points: validates helpers used by model pullers and network/NAT code.

Risks: fake filesystem tests may not capture all OS rename/copy edge cases. IP parsing tests are narrow.

Test signals: solid smoke coverage for core file helper semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/osutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/ping.go -->
## sources/sync-backup/syncthing/lib/osutil/ping.go

Purpose: TCP latency measurement helpers.

Important APIs: `TCPPing(ctx, address)` measures time to establish a TCP connection and closes it. `GetLatencyForURL(ctx, addr)` parses a URL string and delegates to `TCPPing` on the URL host.

Control flow and state: `TCPPing` records start time, uses `net.Dialer.DialContext`, closes on success, and returns elapsed time. `GetLatencyForURL` uses `url.Parse` and passes `u.Host`.

Dependencies and integration points: used by connection/address selection or diagnostics that rank endpoints by TCP connect latency.

Risks: measures connect time only, not TLS/BEP latency. URL strings without a host produce dial errors. Context controls timeout/cancel behavior.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/replacingwriter.go -->
## sources/sync-backup/syncthing/lib/osutil/replacingwriter.go

Purpose: streaming writer that replaces byte sequences while writing, plus a helper for platform-native line endings.

Important APIs: `ReplacingWriter` has `Writer`, `From`, and `To` fields and implements `Write`. `LineEndingsWriter` returns a writer that maps LF to CRLF on Windows and leaves data unchanged on other platforms.

Control flow and state: `Write` scans input for occurrences of `From`, writes preceding chunks and `To` replacements to the underlying writer, and reports the original input length when all underlying writes succeed. It handles empty/no-match cases by direct write.

Dependencies and integration points: used for text output where newline normalization or simple replacement is needed.

Risks: replacement does not carry partial match state across separate `Write` calls; callers streaming arbitrary chunks can miss patterns split across boundaries. Returned byte count is input length, not bytes written after expansion/contraction, as expected by `io.Writer`.

Test signals: `replacingwriter_test.go` covers several replacement cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/replacingwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/replacingwriter_test.go -->
## sources/sync-backup/syncthing/lib/osutil/replacingwriter_test.go

Purpose: tests `ReplacingWriter` behavior for simple string substitutions.

Important test/data: `testcases` define input, `from`, `to`, and expected output. `TestReplacingWriter` writes each input to a buffer through `ReplacingWriter` and compares output.

Control flow and state: table-driven, single-write cases.

Dependencies and integration points: validates text replacement helper but not `LineEndingsWriter` platform behavior.

Risks: does not test split replacement sequences across multiple writes or underlying writer errors.

Test signals: basic substitution coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/replacingwriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/rlimit_unix.go -->
## sources/sync-backup/syncthing/lib/osutil/rlimit_unix.go

Purpose: Unix implementation for maximizing the open-file resource limit.

Important API: `MaximizeOpenFileLimit` reads `RLIMIT_NOFILE`, raises current soft limit toward hard limit or a package cap, writes it back with `Setrlimit`, and returns the resulting current limit.

Control flow and state: if get/set rlimit fails, it returns the current known limit and wrapped error. Constants bound the target to avoid overflow or unreasonable values.

Dependencies and integration points: used during startup to allow many folder/file descriptors.

Risks: permissions, systemd limits, containers, or macOS limits can prevent raising the soft limit. Callers must treat errors as non-fatal where appropriate.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/rlimit_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/rlimit_windows.go -->
## sources/sync-backup/syncthing/lib/osutil/rlimit_windows.go

Purpose: Windows no-op implementation for open-file limit maximization.

Important API: `MaximizeOpenFileLimit` returns `0, nil`.

Control flow and state: none.

Dependencies and integration points: satisfies cross-platform startup API where Unix rlimits do not apply.

Risks: callers should not interpret zero as a useful limit on Windows.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/rlimit_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/tempfile.go -->
## sources/sync-backup/syncthing/lib/osutil/tempfile.go

Purpose: filesystem-abstracted temporary file creation adapted from Go's temp-file approach.

Important APIs: internal `reseed` and `nextSuffix`, and exported `TempFile(filesystem, dir, prefix)`.

Control flow and state: a package atomic counter is seeded from random data and incremented for suffixes. `TempFile` defaults empty dir to `.`, tries up to 10,000 generated names, creates files with `OptReadWrite|OptCreate|OptExclusive` and mode `0600`, and handles existing-file collisions by retrying. If a name-generation collision pattern persists it reseeds.

Dependencies and integration points: used by `AtomicWriter` and other fs-abstracted temp-file code. Depends on Syncthing `fs.Filesystem` and crypto-random package `rand`.

Risks: failure to create after many attempts returns the last error or a too-many-attempts error. Security depends on exclusive create and mode `0600` support by filesystem implementation.

Test signals: `atomic_unix_test.go` indirectly validates temp permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/tempfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/traversessymlink.go -->
## sources/sync-backup/syncthing/lib/osutil/traversessymlink.go

Purpose: detects whether a path traverses a symlink or hits a non-directory component where a directory is expected.

Important APIs: `TraversesSymlinkError`, `NotADirectoryError`, and `TraversesSymlink(filesystem, name)`.

Control flow and state: the function cleans/splits the path, walks components from root toward the target with `Lstat`, allows missing final or intermediate components, returns `TraversesSymlinkError` for symlink components, `NotADirectoryError` for non-directory intermediate components, and nil for safe paths.

Dependencies and integration points: used by model request/puller code to prevent reading or writing through symlinks outside the folder root.

Risks: correctness depends on `Lstat` not following symlinks and on path cleaning preserving security boundaries. Race conditions remain possible between check and later open unless callers also use safe filesystem primitives.

Test signals: `traversessymlink_test.go` covers symlink, non-directory, missing, and benchmark cases; request tests cover end-to-end symlink traversal rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/traversessymlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/traversessymlink_test.go -->
## sources/sync-backup/syncthing/lib/osutil/traversessymlink_test.go

Purpose: tests and benchmarks symlink traversal detection.

Important tests: `TestTraversesSymlink` builds a fake filesystem tree with directories, files, and symlinks and checks expected nil or typed errors for various paths. `TestIssue4875` covers a regression around missing paths below file/non-directory components. `BenchmarkTraversesSymlink` measures repeated safe-path checks.

Control flow and state: table-driven tests call `TraversesSymlink` and compare error types, not exact messages. Benchmark stores result in a package variable to avoid compiler elimination.

Dependencies and integration points: validates osutil safety checks used by model request handling.

Risks: fake filesystem symlink semantics may differ from all OS/filesystem combinations.

Test signals: good focused coverage for symlink traversal safety.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/osutil/traversessymlink_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/pmp/debug.go -->
## sources/sync-backup/syncthing/lib/pmp/debug.go

Purpose: registers the NAT-PMP package for debug logging.

Important API: package `init` calls `slogutil.RegisterPackage("NAT-PMP discovery and port mapping")`.

Control flow and state: registration at package initialization.

Dependencies and integration points: enables package-specific logging controls for NAT-PMP discovery and mapping.

Risks: none beyond logging category consistency.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/pmp/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/pmp/empty_test.go -->
## sources/sync-backup/syncthing/lib/pmp/empty_test.go

Purpose: placeholder test file to make coverage reporting show 0% instead of no coverage for the package.

Important content: package declaration and comment only.

Control flow and state: none.

Dependencies and integration points: affects Go test coverage reporting.

Risks: can hide absence of meaningful PMP tests unless coverage is inspected carefully.

Test signals: explicitly indicates no real NAT-PMP tests exist in this package.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/pmp/empty_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/pmp/pmp.go -->
## sources/sync-backup/syncthing/lib/pmp/pmp.go

Purpose: NAT-PMP discovery provider and adapter implementing the `nat.Device` interface.

Important APIs: package `init` registers `Discover` with `nat.Register`. `Discover(ctx, renewal, timeout)` finds the default gateway, creates a NAT-PMP client, queries external address under timeout, and returns a `wrapper` device. `wrapper` implements `ID`, `GetLocalIPv4Address`, `AddPortMapping`, `AddPinhole`, `SupportsIPVersion`, and `GetExternalIPv4Address`.

Control flow and state: discovery calls `netutil.Gateway` through `svcutil.CallWithContext`, logs and returns nil on failure, then calls NAT-PMP external address to validate the gateway. The wrapper ID includes `NAT-PMP@<gateway>`. `AddPortMapping` maps Syncthing `nat.Protocol` to lowercase NAT-PMP protocol strings, converts lease duration to seconds, and returns the mapped external port. IPv6 pinholes are unsupported and return an error; `SupportsIPVersion` accepts `IPvAny` and `IPv4Only`.

Dependencies and integration points: depends on `jackpal/go-nat-pmp`, `nat`, `netutil.Gateway`, `osutil.TCPPing` or local address helpers as visible in wrapper behavior, and the NAT service registry.

Risks: gateway discovery and external address calls can fail under router/firewall/Android restrictions. NAT-PMP supports IPv4 only. Lease duration conversion truncates to seconds. The package has only placeholder tests.

Test signals: no substantive tests; behavior is covered only through integration/manual NAT environments.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/pmp/pmp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/benchmark_test.go -->
## sources/sync-backup/syncthing/lib/protocol/benchmark_test.go

Purpose: benchmarks BEP request throughput over loopback TCP, with and without TLS.

Important functions/types: `BenchmarkRequestsRawTCP`, `BenchmarkRequestsTLSoTCP`, `benchmarkRequestsTLS`, `benchmarkRequestsConnPair`, `getTCPConnectionPair`, `negotiateTLS`, and `fakeModel`. The fake model responds to requests with a buffer of requested size containing the offset encoded at the end.

Control flow and state: benchmarks create a connected TCP pair, optionally wrap it in TLS, start two protocol connections, send cluster configs, then alternate 128 KiB requests between both directions while verifying buffer length and offset marker.

Dependencies and integration points: uses protocol `NewConnection`, dialer TCP options, test certificates, compression metadata, and connection/model interfaces. It measures connection request/response performance rather than correctness of model storage.

Risks: TLS benchmark skips if test certificates are unavailable. Loopback performance depends on host and TCP settings. It uses `InsecureSkipVerify` appropriately for local benchmark setup.

Test signals: benchmark-only performance signal for raw and TLS request paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_clusterconfig.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_clusterconfig.go

Purpose: typed Go representation and wire conversion for BEP cluster configuration messages.

Important types/functions: `Compression`, `FolderType`, `FolderStopReason` constants; `ClusterConfig` with `toWire` and `clusterConfigFromWire`; `Folder` with `toWire`, `folderFromWire`, `Description`, `LogAttr`, and `IsRunning`; `Device` with `toWire` and `deviceFromWire`.

Control flow and state: conversion functions allocate slices and recursively convert folders/devices to generated protobuf `bep` types. `Folder.IsRunning` treats paused as not running and all other reasons as running. Logging helpers return structured folder identity.

Dependencies and integration points: used during connection cluster-config exchange, index sender pause decisions, encrypted password token propagation, introducer behavior, and remote device metadata.

Risks: nil wire folders/devices are not guarded except top-level cluster config nil. Adding BEP fields requires updating conversions or data will be dropped. `DeviceID(w.Id)` assumes valid byte length from wire.

Test signals: request index sender pause/startup tests indirectly exercise cluster config behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_clusterconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_download_progress.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_download_progress.go

Purpose: typed Go representation and wire conversion for BEP download progress messages.

Important types/functions: alias `FileDownloadProgressUpdateType` with append/forget constants; `DownloadProgress` with `toWire` and `downloadProgressFromWire`; `FileDownloadProgressUpdate` with `toWire` and `fileDownloadProgressUpdateFromWire`.

Control flow and state: conversions map update slices and convert version vectors and block indexes between Go ints and generated protobuf fields.

Dependencies and integration points: produced by model `sentdownloadstate` and sent over protocol connections to advertise partially available blocks.

Risks: block indexes convert between `int` and protobuf integer widths; extremely large indexes could overflow on narrow platforms, though block counts are bounded by file/block sizes. No nil guard in `downloadProgressFromWire`.

Test signals: indirectly covered by model progress tests and connection tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_download_progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_fileinfo.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_fileinfo.go

Purpose: central file metadata model for BEP and the local database, including local invalid flags, conflict/equivalence logic, block metadata, block-size selection, hashes, and platform-specific ownership/xattr data.

Important types/functions: `FlagLocal` constants and `HumanString`; `BlockSizes` initialization; `FileInfo` with `ToWire`, `FileInfoFromWire`, `FileInfoFromDB`, `FileInfoFromDBTruncated`, string/log helpers, status methods, `BlockSize`, `FileSize`, accessors, `IsEquivalent`, `IsEquivalentOptional`, `InConflictWith`, and `WinsConflict`; utility functions `ModTimeEqual`, `PermsEqual`, `BlocksHash`, `VectorHash`; mutation helpers `SetMustRescan`, `SetIgnored`, `SetUnsupported`, `SetDeleted`; `BlockInfo`; `PlatformData`, `UnixData`, `WindowsData`, `XattrData`, and equality/conversion helpers.

Control flow and state: `init` builds valid block sizes from min to max and initializes the global protocol buffer pool after block sizes exist. `ToWire` serializes all public BEP fields and optionally DB-only internal fields; it panics if a truncated non-deleted/non-invalid/non-ignored file would be serialized. Incoming invalid wire state becomes `FlagLocalRemoteInvalid`. Equivalence first rejects must-rescan, masks ignored flags, compares identity/type/deletion/invalid state, ownership/xattrs/permissions according to options, then applies type-specific checks. Conflict detection uses version-vector dominance and previous/current block hashes. Setters for invalid/deleted states clear content.

Persistence behavior: local-only fields `LocalFlags` and `EncryptionTrailerSize` are serialized only when `withInternalFields` is true for DB storage. Truncated DB reads mark `truncated` to prevent accidental wire serialization without block data.

Dependencies and integration points: generated `bep` protobuf types, protocol vector/counter types, build platform flags, block constants, and global `BufferPool`. This file underpins scanning, syncing, database state, conflict resolution, encrypted metadata wrapping, and request block selection.

Risks: changes here have high blast radius. Equality semantics are subtle around invalid flags, permissions on Windows, ownership by ID/name, xattr ordering, and blocks-hash shortcuts. Platform data pointer comparisons are used as a fast inequality check before detailed comparison. Serialization panics guard against truncated misuse but can surface as runtime crashes if callers violate invariants.

Test signals: `bep_fileinfo_test.go`, `conflict_test.go`, encryption tests, and many model tests cover flags, equivalence, conflicts, consistency, and encrypted wrapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_fileinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_fileinfo_test.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_fileinfo_test.go

Purpose: validates `FileInfo` local flags, equivalence logic, block sizing, block hash behavior, wire/database consistency, and platform metadata comparisons.

Important tests: `TestLocalFlagBits` verifies invalid flag transitions. `TestIsEquivalent` is a broad table of name/type/size/deletion/invalid/mtime/permissions/blocks/ownership/xattr cases with optional ignore settings. Additional tests in the file cover block size selection, empty-block hashes, file-info consistency, wire conversion, and platform data behavior.

Control flow and state: table-driven tests construct `FileInfo` values, mutate flags or platform fields, and compare results from methods such as `IsEquivalentOptional`, `BlocksEqual`, and conversion functions.

Dependencies and integration points: uses build flags for platform permission semantics and validates invariants relied on by scanner, database, and puller code.

Risks: test coverage is broad but must be kept in sync with BEP schema changes and new platform metadata fields.

Test signals: high-value regression coverage for one of the protocol package's most central data types.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_fileinfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_hello.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_hello.go

Purpose: implements BEP hello message serialization, exchange, and version-mismatch detection.

Important APIs: constants `HelloMessageMagic` and `Version13HelloMagic`; errors `ErrTooOldVersion` and `ErrUnknownMagic`; `Hello` with `toWire`, `helloFromWire`, `Magic`; `ExchangeHello`, `IsVersionMismatch`, `readHello`, and `writeHello`.

Control flow and state: `ExchangeHello` requires a non-zero outgoing timestamp, writes a hello, then reads the peer hello. `readHello` reads four magic bytes, handles v0.14 protobuf hello with a two-byte size capped at 32767, maps known old v12/v13 headers to `ErrTooOldVersion`, and otherwise returns `ErrUnknownMagic`. `writeHello` marshals protobuf and panics if too large for the signed 16-bit-compatible size limit.

Dependencies and integration points: used at connection startup before BEP message exchange. Relies on generated `bep.Hello` and protobuf encoding.

Risks: write-before-read ordering assumes both peers follow the same exchange pattern over full-duplex connections. Unknown magic may represent newer protocols or non-Syncthing traffic. Panics on missing timestamp or oversized outgoing hello catch programmer bugs.

Test signals: `bep_hello_test.go` covers current hello parsing and old/unknown magic errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_hello.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_hello_test.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_hello_test.go

Purpose: tests BEP hello exchange compatibility and error classification.

Important tests/helpers: `TestVersion14Hello` builds a v0.14 hello frame, exchanges it through an in-memory `readWriter`, and verifies received fields. `TestOldHelloMsgs` feeds known v12, v13, and unknown magic headers and checks exact errors. `readWriter` couples separate reader/writer buffers for `ExchangeHello`.

Control flow and state: tests simulate the peer's read side with prepared bytes while capturing outgoing write bytes.

Dependencies and integration points: validates protobuf hello framing used before connection startup.

Risks: does not test oversized messages, missing timestamp panic, short reads, or malformed protobuf bodies.

Test signals: focused compatibility coverage for hello framing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_hello_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_index_updates.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_index_updates.go

Purpose: typed Go representation and wire conversion for BEP index and index update messages.

Important types/functions: `Index` and `IndexUpdate` structs, each with folder/files fields and `toWire`/from-wire conversions.

Control flow and state: conversion allocates file slices and maps each `FileInfo` through `ToWire(false)` or `FileInfoFromWire`. `IndexUpdate` additionally carries a `LastSequence` value.

Dependencies and integration points: used by connections to send full indexes and incremental updates between devices. Model request tests use `IndexUpdate` to simulate remote changes.

Risks: internal DB-only fields are intentionally not sent over the wire. Schema changes require conversion updates. No nil guards for nested wire file pointers.

Test signals: broad indirect coverage through model request tests and protocol connection benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_index_updates.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_request_response.go -->
## sources/sync-backup/syncthing/lib/protocol/bep_request_response.go

Purpose: typed request/response structures and wire conversion for BEP block requests.

Important types/functions: `ErrorCode` alias and no-error/generic/no-such-file/invalid constants; `Request` with ID, folder, name, offset, size, hash, weak hash, from temporary flag, and block number; `Response` with ID, code, and data. `toWire` and from-wire functions convert to generated `bep` messages.

Control flow and state: direct field mapping, with integer width conversions for sizes/block numbers.

Dependencies and integration points: used by protocol connections and model request handling; encryption wrappers transform request name/offset/size/hash around these structs.

Risks: size and block number conversions can overflow if callers exceed BEP bounds. Error code mapping is separate in `errors.go`.

Test signals: request integration tests and protocol benchmarks exercise this path indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bep_request_response.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bufferpool.go -->
## sources/sync-backup/syncthing/lib/protocol/bufferpool.go

Purpose: global bucketed byte-slice pool for protocol buffers sized around valid block sizes.

Important APIs: global `BufferPool`, `bufferPool`, `newBufferPool`, `Get`, `Put`, `getBucketForLen`, and `putBucketForCap`.

Control flow and state: `newBufferPool` creates one `sync.Pool` per block size plus a small-message bucket. `Get` chooses the smallest bucket satisfying the requested length, returns a slice with requested length and bucket capacity, or allocates exact size for oversized requests. `Put` requires slices with capacities matching known buckets and panics for invalid capacities or non-empty lengths depending on implementation checks. Bucket selection is tied to `BlockSizes` initialized in `bep_fileinfo.go`.

Dependencies and integration points: used by protocol message read/write paths to reduce allocations. Must be initialized after block sizes.

Risks: callers must only put slices obtained from the pool and with expected length/capacity state. Invalid put usage can panic. Holding pooled buffers after put can corrupt data.

Test signals: `bufferpool_test.go` covers bucket selection, invalid put panics, and concurrent stress.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bufferpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bufferpool_test.go -->
## sources/sync-backup/syncthing/lib/protocol/bufferpool_test.go

Purpose: verifies buffer-pool bucket math, panic behavior, and concurrent use.

Important tests/helpers: `TestGetBucketNumbers` and `TestPutBucketNumbers` validate bucket selection for lengths/capacities. `TestStressBufferPool` runs concurrent get/put loops. `shouldPanic` asserts misuse panics.

Control flow and state: tests interact with a fresh pool or global bucket functions and intentionally trigger invalid cases.

Dependencies and integration points: protects allocation-sensitive protocol buffering behavior.

Risks: stress test can miss rare races without the race detector. Bucket expectations must track block-size constants.

Test signals: good coverage for pool invariants and misuse detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/bufferpool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/common_test.go -->
## sources/sync-backup/syncthing/lib/protocol/common_test.go

Purpose: shared protocol test fixtures and helpers.

Important content: defines reusable fake request responses, mocked connection info, test keys/cert-like identifiers, or helper assertions used by protocol tests in the package.

Control flow and state: helper-only; state is generally package-level fixtures for tests.

Dependencies and integration points: consumed by connection, benchmark, encryption, and serialization tests.

Risks: shared helpers can hide assumptions or introduce coupling between tests if mutated globally.

Test signals: no direct tests; indirectly exercised by protocol test suite.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/conflict_test.go -->
## sources/sync-backup/syncthing/lib/protocol/conflict_test.go

Purpose: tests conflict winner selection for `FileInfo`.

Important test: `TestWinsConflict` constructs file infos with versions, modification times, and invalid flags to assert `WinsConflict` behavior.

Control flow and state: table/simple assertions compare pairs and expected winners.

Dependencies and integration points: validates conflict resolution used by model global/local reconciliation and request conflict tests.

Risks: narrow coverage; broader conflict behavior also depends on `InConflictWith` and model-level conflict file creation.

Test signals: focused unit coverage for tie-break rules.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/conflict_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/counting.go -->
## sources/sync-backup/syncthing/lib/protocol/counting.go

Purpose: wraps readers and writers to maintain protocol-wide byte counters and last-activity timestamps.

Important types/functions: `countingReader`, `countingWriter`, global `totalIncoming`/`totalOutgoing` counters, methods `Read`, `Write`, `Tot`, `Last`, and `TotalInOut`.

Control flow and state: read/write methods delegate to the wrapped object, add successful byte counts to both instance and global atomics, and update last activity time. `Tot` reads per-wrapper total; `Last` reads the timestamp.

Dependencies and integration points: used by raw protocol connections for statistics and activity reporting.

Risks: only successful byte counts are tracked; partial reads/writes with errors count bytes returned by the underlying call. Time fields must be concurrency-safe through their type implementation.

Test signals: no direct tests in this subset; connection benchmarks exercise counters indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/counting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/debug.go -->
## sources/sync-backup/syncthing/lib/protocol/debug.go

Purpose: defines the protocol package logging adapter.

Important API: variable `l = slogutil.NewAdapter("The BEP protocol")`.

Control flow and state: package initialization only.

Dependencies and integration points: used by protocol connection internals for debug logging.

Risks: none beyond logging category naming.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/deviceid.go -->
## sources/sync-backup/syncthing/lib/protocol/deviceid.go

Purpose: represents, formats, parses, and validates Syncthing device IDs derived from certificate/public-key bytes.

Important APIs: `DeviceID` type, likely `NewDeviceID`, `DeviceIDFromString`, `String`, `Short`, `GoString`, `MarshalText`, `UnmarshalText`, `Compare`, and constants for local/empty IDs. It uses base32 encoding with Luhn-like check characters from `luhn.go`.

Control flow and state: parsing removes separators, validates length and check digits, decodes base32 data into the fixed-size ID, and rejects malformed strings. Formatting groups encoded bytes with check characters into human-readable chunks. Short IDs provide compact numeric/device map keys.

Dependencies and integration points: used throughout config, protocol cluster configs, NAT deterministic port selection, database device identities, and logs.

Risks: check digit and grouping compatibility are critical; accepting malformed IDs can cause identity confusion, while changing formatting breaks user-visible IDs.

Test signals: `deviceid_test.go` covers parse/format and validation behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/deviceid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/deviceid_test.go -->
## sources/sync-backup/syncthing/lib/protocol/deviceid_test.go

Purpose: validates device ID formatting, parsing, equality, short IDs, text marshaling, and rejection of invalid IDs.

Important tests: test cases use known device ID strings such as the model test IDs and malformed variants to check round-trips and error paths.

Control flow and state: table-driven parse/format assertions and mutation of strings/check digits to prove validation works.

Dependencies and integration points: protects user-facing device identity and config/protocol compatibility.

Risks: tests must preserve historical formatting examples; new accepted forms require explicit cases.

Test signals: high-value coverage for identity parsing and check digits.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/deviceid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/doc.go -->
## sources/sync-backup/syncthing/lib/protocol/doc.go

Purpose: package documentation stub for the protocol package.

Important content: package comment states that `protocol` implements the Block Exchange Protocol.

Control flow and state: none.

Dependencies and integration points: contributes Go documentation.

Risks: minimal; documentation can become too terse relative to package complexity.

Test signals: none.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/encryption.go -->
## sources/sync-backup/syncthing/lib/protocol/encryption.go

Purpose: implements receive-encrypted protocol transformations: encrypted metadata wrappers, encrypted request/response data, deterministic encrypted names and block tokens, password/file key derivation, and encrypted-path parent detection.

Important types/functions: constants for nonce/tag/key sizes, padding, overhead, path component size, and cache sizes. `encryptedModel` decrypts incoming indexes/requests from untrusted devices and encrypts served data. `encryptedConnection` encrypts outgoing indexes/requests and decrypts responses. Metadata functions include `encryptFileInfos`, `encryptFileInfo`, `decryptFileInfos`, and `DecryptFileInfo`. Crypto helpers include `encryptName`, `decryptName`, `encryptBytes`, `encryptDeterministic`, `decryptDeterministic`, `encrypt`, `DecryptBytes`, `randomNonce`, `encryptBlockHash`, `PasswordToken`, `knownBytes`, `slashify`, `deslashify`, and `IsEncryptedParent`. `KeyGenerator` caches scrypt-derived folder keys and HKDF-derived file keys. `folderKeyRegistry` stores active folder keys.

Control flow and state: encrypted outgoing metadata wraps the real serialized `FileInfo` in `Encrypted`, replaces the name with deterministic base32 AES-SIV output split into filesystem-safe components, creates fake block sizes/hashes with ChaCha overhead and minimum padding, and uses a deterministic aggregate version vector for untrusted-device ordering. Requests to encrypted peers adjust name, offset, size, hash, and block number before transport; responses are decrypted and trimmed. Requests from encrypted peers are inverse-translated, served by the raw model, padded if needed, encrypted, and returned. Folder keys are replaced wholesale when cluster config passwords are set.

Persistence/security behavior: scrypt uses folder-specific known bytes as salt/input context; HKDF derives file keys from folder key plus filename. Random content encryption uses XChaCha20-Poly1305 with nonce prepended. Deterministic names and block hashes use AES-SIV; block-hash additional data includes offset to avoid revealing identical blocks at different offsets. Encrypted paths use `.syncthing-enc` top-level sentinels.

Dependencies and integration points: wraps raw protocol model/connection interfaces, uses generated BEP protobufs, LRU caches, `miscreant` AES-SIV, x/crypto chacha20poly1305/hkdf/scrypt, and Syncthing random source. Model receive-encrypted tests exercise this layer.

Risks: high security sensitivity. Request offset/size arithmetic must remain exact; `realOffset` underflow panics on impossible encrypted requests. Padding and overhead constants define on-disk/wire compatibility. Deterministic encryption leaks equality for names and same-offset blocks by design. Key caches store pointers to keys and must remain protected by mutex. Some Go versions/race detector combinations are skipped in tests due crypto issues.

Test signals: `encryption_test.go` covers name encryption format/determinism, key derivation vectors, invalid names, random byte encryption, file-info wrapping/decryption, consistency, and encrypted parent detection. Model receive-encrypted request tests provide integration coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/encryption_test.go -->
## sources/sync-backup/syncthing/lib/protocol/encryption_test.go

Purpose: validates deterministic encrypted names, password/file key derivation, byte encryption, encrypted file-info wrapping, and encrypted parent path detection.

Important tests/helpers: `TestEnDecryptName` checks path format, determinism, plaintext absence, and round-trip for varied name lengths. `TestKeyDerivation` verifies a known encrypted-name vector and decrypts a known byte ciphertext. `TestDecryptNameInvalid` rejects malformed encrypted paths. `TestEnDecryptBytes` checks random nonce behavior and round-trip. `encFileInfo`, `TestEnDecryptFileInfo`, `TestEncryptedFileInfoConsistency`, and `TestIsEncryptedParent` validate metadata wrapping and sentinel path recognition.

Control flow and state: tests use a package `testKeyGen`, zero keys for deterministic cases, random data for parent component lengths, and skip affected crypto tests under specific Go race-detector conditions.

Dependencies and integration points: protects protocol encryption compatibility and receive-encrypted model behavior.

Risks: known-vector tests are sensitive to crypto/library or parameter changes, which is desirable for compatibility. Race-detector skip leaves a coverage gap in affected environments.

Test signals: strong security/compatibility regression coverage for encryption helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/encryption_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/errors.go -->
## sources/sync-backup/syncthing/lib/protocol/errors.go

Purpose: maps protocol response error codes to Go errors and back.

Important APIs: package errors such as `ErrGeneric`, `ErrNoSuchFile`, and `ErrInvalid`; `codeToError`; `errorToCode`.

Control flow and state: `codeToError` switches BEP error codes to errors, returning nil for no error and generic for unknown/non-success. `errorToCode` uses `errors.Is` style matching or direct comparisons to map known errors to codes and defaults to generic.

Dependencies and integration points: used by request/response handling to translate model request failures into BEP responses.

Risks: preserving `errors.Is` compatibility matters if callers wrap errors. Unknown codes collapsing to generic can hide detail but preserves compatibility.

Test signals: indirect coverage through request tests and protocol connection behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/indexid.go -->
## sources/sync-backup/syncthing/lib/protocol/indexid.go

Purpose: compact random identifier for device/folder index instances with binary marshal/unmarshal support.

Important APIs: `IndexID` type, `String`, `Marshal`, `Unmarshal`, and `NewIndexID`.

Control flow and state: marshal encodes the uint64 in big-endian bytes; unmarshal decodes exact-length data; `NewIndexID` reads random bytes and constructs an ID.

Dependencies and integration points: used in cluster config device metadata to identify remote index generations.

Risks: random generation must not silently return zero or reused IDs; unmarshal length validation is important for DB/wire compatibility.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/indexid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/luhn.go -->
## sources/sync-backup/syncthing/lib/protocol/luhn.go

Purpose: base32 check-character helper used by device ID formatting and validation.

Important APIs: `luhnBase32`, `codepoint32`, and `luhn32`.

Control flow and state: `codepoint32` maps base32 bytes to numeric values. `luhn32` computes a modified Luhn-like checksum over a string and returns a base32 check rune or an error for invalid input.

Dependencies and integration points: used by `deviceid.go` to create and verify human-readable device ID chunks.

Risks: algorithm is intentionally not standard Luhn; compatibility with historical Syncthing IDs is critical. Invalid character handling must remain strict.

Test signals: `luhn_test.go` covers checksum examples and invalid inputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/luhn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/luhn_test.go -->
## sources/sync-backup/syncthing/lib/protocol/luhn_test.go

Purpose: tests modified base32 Luhn checksum behavior.

Important tests: known input/check-character pairs verify checksum output, and invalid characters verify error paths.

Control flow and state: simple table-driven unit tests.

Dependencies and integration points: protects device ID validation compatibility.

Risks: narrow by design; broader device ID parsing is covered in `deviceid_test.go`.

Test signals: focused checksum regression coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/luhn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/metrics.go -->
## sources/sync-backup/syncthing/lib/protocol/metrics.go

Purpose: declares protocol metrics for Prometheus or Syncthing's metrics subsystem.

Important content: metric definitions/counters/gauges for protocol traffic or connection behavior, registered at package init or exposed as package variables.

Control flow and state: metric variables are initialized once and updated by protocol connection/counting paths.

Dependencies and integration points: integrates protocol byte counters and connection stats with observability.

Risks: metric label cardinality and registration names must stay stable. Duplicate registration can panic if initialization patterns change.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/protocol/metrics.go -->
