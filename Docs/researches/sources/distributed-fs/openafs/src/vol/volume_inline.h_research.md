# sources/distributed-fs/openafs/src/vol/volume_inline.h

## Purpose
Provides small inline policy and state-machine helpers for the volume package. These helpers decide when volumes require checkout or disk/partition locking, classify program types and states, and implement demand-attach wait/state-change primitives.

## Important APIs And Functions
`VOL_CV_TIMEDWAIT` wraps condition-variable waiting with optional absolute timeout while preserving VOL lock debug bookkeeping. `VIsSalvager`, `VRequiresPartLock`, `VMustCheckoutVolume`, `VShouldCheckInUse`, `VCanUnlockAttached`, and `VVolLockType` encode attach policy across fileserver, volserver, utilities, and salvagers. DAFS helpers include `VLockVolumeByIdNB`, `VUnlockVolumeById`, `VIsSalvaging`, `VIsExclusiveState`, `VIsErrorState`, `VIsOfflineState`, `VIsValidState`, `VCreateReservation_r`, `VWaitStateChange_r`, `VTimedWaitStateChange_r`, `VWaitExclusiveState_r`, and `VChangeState_r`. `VPTypeToString` provides diagnostics.

## Control Flow And State
The file centralizes decision branches around `programType`, attach mode, and volume type. Non-DAFS utility processes take partition locks; DAFS uses per-volume header locks. Volume state waits assume `VOL_LOCK` is held and at least one user/waiter reference exists. `VChangeState_r` updates global state counters and broadcasts `attach_cv`.

## Persistence And Integration
The helpers do not persist directly, but they protect persistent volume headers and special inode state by selecting read/write/no-lock modes and deciding whether the `inUse` bit should be trusted during attach. They depend on `volume.h`, `partition.h`, pthread/opr primitives, DAFS locks, and configured package options such as FSSYNC and unsafe attach.

## Risks And Test Signals
Policy bugs here can cause false salvage, unsafe concurrent attach, or deadlock. `VShouldCheckInUse` is particularly sensitive because readonly checkouts intentionally tolerate `inUse`. Test signals include attach-mode matrix tests, DAFS lock mode tests for writable vs readonly volumes, timed wait timeout behavior, state counter accounting, and asserts for invalid states or unknown checkout modes.
