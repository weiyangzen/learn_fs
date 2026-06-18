# sources/distributed-fs/ceph-client/fs/dlm/member.h

## Purpose
`member.h` declares lockspace membership and slot-management APIs for recovery, rcom, lockspace, and midcomms users.

## Important APIs, Types, And Functions
The header exposes lockspace start/stop, list clearing, membership tests, recovery member update, slot version/copy/assign helpers, and final recovery-done lockspace-op notification.

## Control Flow
Consumers call `dlm_ls_stop()` before membership recovery, then `dlm_ls_start()` to queue a new `dlm_recover` run. Recovery/rcom paths use the slot helpers while gathering and distributing per-node slot maps.

## State And Persistence
The header owns no state; it exposes functions that mutate `struct dlm_ls` membership lists, slots, generation, and recovery state.

## Dependencies And Integration Points
It depends on core DLM types from `dlm_internal.h`. `recover.c`, `recoverd.c`, `rcom.c`, `requestqueue.c`, and lockspace code all use these declarations.

## Risks
API misuse can break recovery ordering. `dlm_recover_members()` has an adjacent formatting issue in its prototype (`rv,int`) but this is syntactic only.

## Test Signals
Compile coverage across recovery and rcom users plus runtime membership-change tests validate this interface.
