# sources/distributed-fs/ceph/src/mds/MDSContext.h

## Purpose

`MDSContext.h` declares the MDS-specific context hierarchy. It adapts generic Ceph `Context` completions to the MDS rank locking model and provides wrappers for internal callbacks, I/O callbacks, journal callbacks, gather builders, and continuation stages.

## Important APIs And Types

`MDSContext` is the abstract base with `complete` and `get_mds`. `MDSHolder<T>` is a template that stores an `MDSRank*` and implements `get_mds`. `MDSInternalContext` is for callbacks already running inside MDS lock context. `MDSInternalContextWrapper` wraps an arbitrary `Context`.

`MDSIOContextBase` is for callbacks from I/O paths and declares `complete`, `print`, and static `check_ios_in_flight`. `MDSLogContextBase` extends it for journal operations with `write_pos`, `set_write_pos`, and `pre_finish`. `MDSIOContext` and `MDSIOContextWrapper` provide concrete MDS-held I/O contexts. `C_MDSInternalNoop` is a no-op gather leaf. `C_IO_Wrapper` turns an internal context into an I/O context and can queue itself through the MDS finisher.

Aliases `MDSGather`, `MDSGatherBuilder`, and `MDSContextFactory` bind generic gather/context helper templates to `MDSContext`.

## State And Persistence Behavior

The header does not persist state. The important durability contract is in `MDSLogContextBase`: journal completions carry write positions and are responsible for advancing MDLog safe position after completion. `MDSIOContextBase` instances may be tracked for diagnostics with creation timestamps and intrusive list items.

## Dependencies And Integration Points

It depends on `Context`, `elist`, `ceph_time`, and forward-declared `MDSRank`. It is widely used by `MDCache`, `MDLog`, `MDSContinuation`, journal events, storage completions, and gather patterns where callbacks need MDS lock semantics.

## Risks And Test Signals

Every subclass must respect whether `complete` expects the lock to be held or will acquire it itself. Mixing `MDSInternalContext` and `MDSIOContextBase` incorrectly can deadlock or run unlocked. Test signals include context tracking counts, callback behavior during daemon stop, wrapper ownership/destruction, gather cancellation, and journal callback safe-position updates.
