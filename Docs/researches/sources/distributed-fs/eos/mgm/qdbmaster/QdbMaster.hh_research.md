<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.hh -->
# sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.hh

## Purpose
`QdbMaster.hh` declares the QuarkDB implementation of the MGM master interface. It exposes the `IMaster` operations needed by the rest of MGM while hiding lease acquisition, role transition, namespace cache management, and supervisor-thread details.

## Important APIs and types
- `class QdbMaster : public IMaster` is non-copyable and owns a `qclient::QClient` plus an `AssistedThread`.
- Public interface overrides include `Init`, `BootNamespace`, `ApplyMasterConfig`, `IsMaster`, `IsRemoteMasterOk`, `GetMasterId`, `SetMasterId`, `GetServiceDelay`, `GetLog`, and `PrintOut`.
- `sLeaseKey` is the static QuarkDB lease key shared by all MGM nodes in the election group.
- `POST_SLAVE_TO_MASTER_TIMEOUT` defines a 60 second cap for the optional post-transition script.
- Private transition helpers are `Supervisor`, `AcquireLease`, `AcquireLeaseWithDelay`, `ReleaseLease`, `GetLeaseHolder`, `SlaveToMaster`, `PostSlaveToMaster`, and `MasterToSlave`.
- Namespace caching helpers `DisableNsCaching`, `EnableNsCaching`, and timeout helper `ConfigureTimeouts` are private implementation details.

## Control flow and state model
The header shows an object with two identities: immutable local `mIdentity` and mutex-protected `mMasterIdentity`. `mIsMaster`, `mOneOff`, and `mConfigLoaded` control role and boot progress. `mAcquireDelay` deliberately pauses reacquisition after a manual master change request. `mLeaseValidity`, `mDoMasterDelay`, `mMasterDelayDeadline`, and static `sMasterDelaySec` shape lease renewal and post-promotion request admission.

`GetMasterId()` takes `mMutexId` and returns a copy, while `UpdateMasterId()` is private and uses the same mutex. `IsMaster()` is a simple atomic read. The class owns its supervisor thread and joins it in the destructor.

## Persistence behavior
The header itself does not define persistence, but its fields identify the persisted/remote source of truth as the QuarkDB lease key. Local role fields are process-local and rebuilt on restart by `Init()` and the supervisor. The config-loaded flag tracks whether MGM config was loaded during transitions, not whether it is durably stored.

## Dependencies and integration points
The declaration depends on `IMaster`, `AssistedThread`, and `QdbContactDetails`, with a forward declaration of `qclient::QClient`. Because public methods match `IMaster`, other MGM code can interact through the abstract master interface; the implementation still requires QDB contact details and a local host-port identity.

## Risks and test signals
The interface exposes very little direct configurability, so most testing must instantiate with a fake or test QuarkDB client only if the implementation is made injectable. Current ownership of `std::unique_ptr<qclient::QClient>` and private lease methods make isolated unit tests difficult. Race-focused tests should cover concurrent `GetMasterId()`, destructor thread join behavior, `IsMaster()` visibility, and acquire-delay semantics after `SetMasterId()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.hh -->
