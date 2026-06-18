# sources/distributed-fs/ceph-client/fs/dlm/recover.h

## Purpose
`recover.h` declares the recovery wait, master, lock, RSB, and inactive-cleanup APIs used by the recovery daemon and recovery message handlers.

## Important APIs, Types, And Functions
The header exposes general wait/status functions, phase barriers for members/directory/locks/done, master recovery send/reply functions, lock recovery send/reply accounting, RSB finalization, and inactive cleanup.

## Control Flow
`recoverd.c` calls the phase functions in order. `rcom.c` calls reply entry points when lookup or lock recovery replies arrive. Lock and directory code consult recovery flags established by these APIs.

## State And Persistence
No header-owned state. Implementations mutate lockspace, resource, and lock state for the active recovery generation.

## Dependencies And Integration Points
The header connects recoverd, rcom, dir, lock, lowcomms, member, and ast code around a common recovery sequence.

## Risks
Callers must honor recovery phase order; calling lock recovery before directory/master recovery will operate on incomplete master data.

## Test Signals
Compile coverage and integration tests that drive full recovery sequences validate the interface.
