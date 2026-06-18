# sources/distributed-fs/eos/mgm/imaster/IMaster.hh

## Purpose

`IMaster.hh` defines the abstract interface for EOS MGM master/slave state management. It standardizes initialization, namespace booting, config application, master identity updates, transition status reporting, master logs, and shared filesystem status-file helpers.

## Important APIs, Types, and Functions

- `EOSMGMMASTER_SUBSYS_RW_LOCKFILE` points to `/var/eos/eos.mgm.rw`, whose existence means the node should be treated as MGM master/read-write.
- `EOSMQMASTER_SUBSYS_REMOTE_LOCKFILE` points to `/var/eos/eos.mq.remote.up`, whose existence tells local MQ to redirect to remote MQ.
- `struct Transition::Type` enumerates master transition categories: master-to-master, slave-to-master, master-to-master-read-only, master-read-only-to-slave, and secondary-slave failover.
- Pure virtual methods define the implementation contract: `Init()`, `BootNamespace()`, `ApplyMasterConfig()`, `IsMaster()`, `IsRemoteMasterOk()`, `GetMasterId()`, `SetMasterId()`, `GetServiceDelay()`, `GetLog()`, and `PrintOut()`.
- Shared implemented helpers are `ResetLog()`, `MasterLog()`, `FillNsCacheConfig()`, `CreateStatusFile()`, and `RemoveStatusFile()`.

## Control Flow

Concrete master implementations are expected to initialize current state with `Init()`, boot namespace services through `BootNamespace()`, apply stall/redirection and master settings through `ApplyMasterConfig()`, and report runtime identity/state through the query methods. Transition code uses `GetServiceDelay()` after failover-like changes to avoid immediately reissuing transfers before maps converge.

The header-provided `ResetLog()` takes `mMutex` and clears `mLog`. Other shared helper implementations are in `IMaster.cc`.

## State and Persistence Behavior

`IMaster` stores an in-memory log string and mutex. The interface also defines lock-file paths that represent persistent local host state for master/read-write and remote MQ redirection. Derived classes are responsible for the actual master identity, namespace boot state, redirection/stall rules, and service delay calculations.

## Dependencies and Integration Points

The interface lives in `EOSMGMNAMESPACE` and inherits `eos::common::LogId`. It uses `IConfigEngine` for namespace cache settings and POSIX file mode definitions for status-file helpers. Comments explicitly note that lock-file defines must agree with `XrdMqOfs.cc` without creating a direct code dependency, making this header part of a cross-module operational contract.

## Risks and Edge Cases

- The lock-file contract is duplicated with `XrdMqOfs.cc` by convention. Divergence would break master/MQ coordination without compiler help.
- `GetMasterId()` returns `const std::string` by value; the `const` qualifier on a returned value is unnecessary and can inhibit move semantics in older compilers.
- `ResetLog()` and `MasterLog()` protect `mLog`, but concrete `GetLog()` implementations must also lock consistently.
- The interface does not define thread-safety expectations for master identity transitions.

## Test Signals

Concrete implementations should be tested through this interface for transition behavior, master ID validation, service delay after transition, lock-file side effects, and log thread safety. ABI/compile tests should detect changes to the transition enum and pure virtual method set because consumers depend on the interface shape.
