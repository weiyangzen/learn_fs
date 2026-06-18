<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.cc -->
# sources/distributed-fs/eos/mgm/filesystem/FileSystem.cc

## Purpose

`FileSystem.cc` implements the MGM-side `FileSystem` wrapper around `eos::common::FileSystem`. It adds filesystem-change listener registration, shared-hash update notification, drain-transition handling, and local accounting for active balancer transfers.

## Important APIs, Types, and Functions

Key methods are the constructor/destructor, `RegisterWithExistingListeners()`, `UnregisterFromListeners()`, `AttachFsListener()`, `DetachFsListener()`, `NotifyFsListener()`, `ProcessUpdateCb()`, `SetConfigStatus()`, overridden `SetString()`, `IsDrainTransition()`, `ShouldBroadCast()`, `IncrementBalanceTx()`, and `DecrementBalanceTx()`. Static tags include `local.balancer.running`, `stat.geotag`, and `stat.errc`.

## Control Flow

Construction logs the queue path, registers with already interested listeners from the messaging realm, subscribes to the backing shared hash, and attaches `ProcessUpdateCb()`. Shared-hash updates are filtered by key against `mMapListeners` and delivered as `FsChangeListener::Event`. `SetString("configstatus", ...)` redirects to `SetConfigStatus()`. On a broadcast-capable master realm, config-status changes are classified by `IsDrainTransition()`, start or stop `gOFS->mDrainEngine`, repair finished drain state when stopping, and then write the new config status through the base class.

## State and Persistence Behavior

The base `common::FileSystem` owns persistent shared-hash fields. This wrapper owns runtime listener maps, a subscription handle, and atomic `mNumBalanceTx`. `IncrementBalanceTx()`/`DecrementBalanceTx()` write the local running-transfer counter with `SetLongLongLocal()`, so the value is visible in local filesystem state but is not a durable cross-process counter.

## Dependencies and Integration Points

The file depends on `MessagingRealm`, `FsChangeListener`, `FsView`, global `gOFS`, drain engine APIs, and `qclient::SharedHashSubscription`. It is part of the MGM filesystem view and receives storage-node shared-hash updates.

## Risks and Edge Cases

`SetConfigStatus()` assumes callers hold `FsView::ViewMutex`, as documented in the header; missing that lock can race global view state. `DecrementBalanceTx()` can underflow the unsigned atomic if called too often. Listener notification holds `mRWMutex` while invoking listener callbacks, so slow or reentrant listeners could create latency or lock-order issues. A non-broadcasting realm returns true from `SetConfigStatus()` without writing local state.

## Test Signals

Tests should cover drain transition classification, config-status set paths with mocked drain start/stop success and failure, listener attach/detach/update delivery, subscription callback detachment on destruction, and balance counter increment/decrement writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.cc -->
