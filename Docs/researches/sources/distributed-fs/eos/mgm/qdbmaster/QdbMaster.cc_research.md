<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.cc -->
# sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.cc

## Purpose
`QdbMaster.cc` implements the `QdbMaster` concrete `IMaster` backend for QuarkDB-backed EOS MGM deployments. It boots the namespace plugin, supervises QuarkDB lease ownership, transitions an MGM between slave and master behavior, applies master configuration, toggles namespace cache settings, and starts/stops master-only services.

## Important APIs and functions
- `QdbMaster::QdbMaster` stores the local `host:port` identity and creates a `qclient::QClient` from `QdbContactDetails`.
- `Init()` marks namespace state as booting and starts the `Supervisor` assisted thread.
- `BootNamespace()` loads the `NamespaceGroup` plugin, builds QuarkDB namespace configuration, initializes container/file/filesystem/accounting views, registers `Quota::MapSizeCB`, runs namespace `initialize1/initialize2`, starts cache refresh listening, and sets `gOFS->mNamespaceState`.
- `Supervisor()` is the main election loop. It waits for namespace boot, calls `AcquireLeaseWithDelay()`, refreshes `mMasterIdentity` from `GetLeaseHolder()`, and dispatches `SlaveToMaster()` or `MasterToSlave()` on role changes.
- `ConfigureTimeouts()` reads `EOS_QDB_MASTER_INIT_LEASE_MS` and `EOS_QDB_MASTER_LEASE_MS`, caps regular lease validity at five minutes, and ensures transition leases are at least as long as steady-state leases.
- `AcquireLease()`, `ReleaseLease()`, and `GetLeaseHolder()` use QuarkDB commands `lease-acquire`, `lease-release`, and `lease-get` against static key `master_lease`.
- `SlaveToMaster()` drains in-flight requests, refreshes inode providers, enables config broadcasts, applies config, loads quota nodes, enables namespace caching, starts WFE recovery, broadcasts master id, and starts LRU, recycler, device tracker, geotree refresh, and tape GC if enabled.
- `MasterToSlave()` clears master status, stops master-only engines, stalls/drains requests, disables config broadcast and namespace caching, applies config once during initial slave boot, and stops tape GC if configured.
- `PostSlaveToMaster()` runs an optional `mgmofs.postslavetomaster` shell hook with old/new master ids and a 60 second timeout.
- `ApplyMasterConfig()` serializes config application with a static mutex, restarts drain handling, disables direct FsView config engine interaction through `ConfigResetMonitor`, and autoloads `gOFS->MgmConfigAutoLoad`.
- `SetMasterId()` currently only arranges an acquire delay when called on the current master for a different target; it does not write a new lease holder directly.
- `IsRemoteMasterOk()` builds a root URL from the current master id and checks reachability via `XrdCl::FileSystem::Ping`.

## Control flow
Startup flows through `Init()` and `BootNamespace()` in parallel with the supervisor: `BootNamespace()` completes namespace initialization and then waits until `mOneOff` is cleared by the supervisor. The supervisor installs a boot stall rule, waits for namespace state `kBooted`, attempts to acquire or observe the QDB lease, and performs a one-off master or slave transition. Later loop iterations renew/observe the lease at half the lease interval when a master exists, react to lease loss by moving master to slave, and react to lease acquisition by moving slave to master and invoking the optional post-transition hook.

The transition paths deliberately gate client traffic. `SlaveToMaster()` sets a short stall rule, disables request acceptance, waits for in-flight requests to drain, refreshes metadata providers, applies config, starts master-only services, removes the stall, writes the master lockfile, and then delays accepting requests for `sMasterDelaySec` in the supervisor loop. `MasterToSlave()` removes the lockfile, stops master-only services, stalls/drains, disables broadcasts and namespace caching, and leaves the process as a listener.

## State and persistence
- Persistent election state lives in QuarkDB under `QdbMaster::sLeaseKey` (`master_lease`) with values managed by QuarkDB lease commands.
- Local role state is held in atomics `mIsMaster`, `mOneOff`, `mConfigLoaded`, `mAcquireDelay`, and `mDoMasterDelay`; master identity string access is protected by `mMutexId`.
- Namespace boot state and all services are global through `gOFS`; this file mutates `mNamespaceState`, namespace service pointers, request tracker state, messaging broadcast mode, config engine state, cache settings, and status lockfiles.
- Config persistence is delegated to the MGM config engine. This file loads config but does not itself persist master election decisions.
- The optional post-transition hook is external process state and is only logged on failure; the transition is already complete when it runs.

## Dependencies and integration points
`QdbMaster` is tightly coupled to MGM globals and services: `XrdMgmOfs`, `Access`, `Quota`, `WFE`, `Fsck`, `LRU`, `Recycle`, `Devices`, `GeoTreeEngine`, `ConverterEngine`, `IConfigEngine`, `MessagingRealm`, tape GC, namespace plugin interfaces, QuarkDB namespace constants, `qclient`, XRootD client ping, and shell command execution. `BootNamespace()` is the bridge between the plugin manager and the global namespace service pointers consumed by most MGM subsystems. `SlaveToMaster()` integrates quota loading and recycler startup, making these research files part of the master failover path.

## Risks and edge cases
- `GetLeaseHolder()` parses a textual `lease-get` reply and includes `pos_end - pos + 1`, which can retain a newline in `mMasterIdentity`; downstream URL construction and string comparison must tolerate or normalize this.
- `SetMasterId()` constructs `hostname + std::to_string(port)` without a colon, unlike the constructor identity documentation. If this is user reachable, comparisons to `mIdentity` can be misleading.
- Master transitions call `std::abort()` on config or tape-GC start failures. That is defensible for consistency but high impact during failover.
- The supervisor depends on `mConfigLoaded`; if autoload is empty, `ApplyMasterConfig()` returns false and transition paths can abort. This may be intentional for QDB deployments but is a deployment-sensitive behavior.
- Many operations use global mutable state with lock ordering spread across subsystems. Deadlock risk is mitigated in `ApplyMasterConfig()` by `ConfigResetMonitor`, but transitions still touch request tracker, namespace services, messaging, access rules, and engines in sequence.
- `PostSlaveToMaster()` builds a shell command by concatenating quoted master ids. Values are expected MGM identities, but any future untrusted source would need stronger argument passing.

## Test signals
No direct unit tests for `QdbMaster` were found in the scanned tree. Useful validation signals are integration/failover tests with QuarkDB lease acquisition/loss, namespace boot failure injection, config autoload failure behavior, master-to-slave service shutdown, post-transition hook timeout/failure, and XRootD remote master ping handling. Because `SlaveToMaster()` starts `Recycle` and calls `Quota::LoadNodes()`, recycle/quota integration tests also indirectly exercise successful master transition prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.cc -->
