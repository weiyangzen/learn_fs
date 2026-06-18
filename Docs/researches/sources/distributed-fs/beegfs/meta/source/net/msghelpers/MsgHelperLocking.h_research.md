<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.h

## Purpose
Declares static helpers for metadata file locking messages.

## Important APIs, Types, and Functions
`MsgHelperLocking` exposes `trySesssionRecovery()` and `flockAppend()` and hides construction. The header depends on `EntryInfo`, `StorageErrors`, and `SessionFileStore`.

## Control Flow, State, and Persistence
The signatures show that recovery returns a referenced `SessionFile*` to the caller on success and that flock append mutates lock state through `EntryLockDetails`.

## Dependencies and Integration Points
Used by flock message handlers and session recovery paths. Integrates with file session stores and lock detail types.

## Risks and Test Signals
Tests should verify caller ownership/reference expectations for `outSessionFile` and that `flockAppend()` maps lock-grant state to `SUCCESS` or `WOULDBLOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.h -->
