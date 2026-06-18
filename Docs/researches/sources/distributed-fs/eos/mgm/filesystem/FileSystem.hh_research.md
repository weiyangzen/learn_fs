<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.hh -->
# sources/distributed-fs/eos/mgm/filesystem/FileSystem.hh

## Purpose

`FileSystem.hh` declares the MGM filesystem class. It extends the common filesystem model with MGM-specific listener notification, drain-control entry points, and local balancer transfer accounting.

## Important APIs, Types, and Functions

The class inherits from `eos::common::FileSystem` and `eos::common::LogId`. Public APIs include static `sNumBalanceTxTag`, static `IsDrainTransition()`, constructor/destructor, `AttachFsListener()`, `DetachFsListener()`, `ShouldBroadCast()`, `SetConfigStatus()`, `SetString()`, `IncrementBalanceTx()`, and `DecrementBalanceTx()`. Private members include shared-hash subscription `mSubscription`, listener map `mMapListeners`, listener mutex `mRWMutex`, `mNumBalanceTx`, and helper callbacks.

## Control Flow

The declaration shows that status writes funnel through `SetString()` and `SetConfigStatus()`, while shared-hash updates flow into `ProcessUpdateCb()` and then `NotifyFsListener()`. Listener registration is updated both for new listener attachment and existing listeners when a filesystem object is created.

## State and Persistence Behavior

State spans base filesystem shared-hash state, local listener registrations, local subscription lifecycle, and atomic balancer counter. Listener state is runtime only; base class key/value updates may broadcast or persist according to the common filesystem and messaging realm implementation.

## Dependencies and Integration Points

The header depends on common filesystem/logging, MGM namespace macros, `mq/FsChangeListener.hh`, qclient shared-hash types, and `mq::MessagingRealm`. It integrates with `FsView` locking rules and the drain engine through implementation.

## Risks and Edge Cases

The API documents that `SetConfigStatus()` and `SetString()` must be called with `FsView::ViewMutex`; this is a contract rather than enforced by the type. Listener maps store shared pointers and can prolong listener lifetime. The class relies on callback detachment before destruction to avoid use-after-free.

## Test Signals

Header/API tests should verify construction with a mock realm, attach/detach behavior, listener interest filtering, drain transition return values, and that overriding `SetString()` preserves non-`configstatus` base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.hh -->
