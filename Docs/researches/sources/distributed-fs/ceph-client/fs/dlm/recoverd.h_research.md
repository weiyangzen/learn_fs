# sources/distributed-fs/ceph-client/fs/dlm/recoverd.h

## Purpose
`recoverd.h` declares the lifecycle and synchronization interface for the DLM recovery daemon thread.

## Important APIs, Types, And Functions
It exposes start/stop plus suspend/resume functions for a lockspace's recoverd task.

## Control Flow
Lockspace setup starts recoverd. Membership stop/start paths suspend or resume it around recovery state reset. Teardown stops the thread.

## State And Persistence
No header-owned state. The implementation stores the task pointer and recovery synchronization state in `struct dlm_ls`.

## Dependencies And Integration Points
Used by membership and lockspace code to coordinate recovery thread execution with lockspace stop/start.

## Risks
Suspend/resume must be balanced because it locks/unlocks `ls_recoverd_active`. Stopping recoverd while recovery lock is held must release `ls_in_recovery` correctly.

## Test Signals
Lockspace create/destroy and membership recovery tests should verify no stuck recoverd tasks or unreleased recovery locks.
