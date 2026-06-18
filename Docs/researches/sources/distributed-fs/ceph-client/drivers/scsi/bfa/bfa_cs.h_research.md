# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_cs.h

## Purpose
`bfa_cs.h` provides common services shared by the BFA driver: trace buffering, queue macros, state machine macros, wait counters, WWN/FCID formatting, and 24-bit Fibre Channel id endian conversion. It is infrastructure used by both HAL code and Fibre Channel control state machines.

## Important APIs and Types
`struct bfa_trc_mod_s` owns a circular trace buffer of `struct bfa_trc_s` entries, with head/tail counters, stop flag, and timestamps. `BFA_TRC_FILE`, `bfa_trc`, and `bfa_trc32` stamp a module/file id and source line into `__bfa_trc`. Queue helpers wrap Linux `list_head`: `bfa_q_deq`, `bfa_q_deq_tail`, `bfa_q_is_on_q`, and accessors for first/next/prev. `bfa_sm_*` macros provide simple state machines; `bfa_fsm_*` macros add entry actions. `struct bfa_wc_s` implements a small wait counter with a resume callback.

## Control Flow and State
State machine macros store a function pointer directly in the object being controlled. `bfa_fsm_set_state` updates the function pointer and immediately calls the new state entry function, which is why state transitions in `bfa_core.c` can perform side effects such as IOC enable, mailbox configuration, or callback queueing as soon as the transition occurs. The wait counter starts with a held reference; callers call `bfa_wc_wait` to drop it and run the resume callback when the count reaches zero.

## State and Persistence Behavior
Trace state is an in-memory ring. On wrap, the oldest entry advances by moving `head`. `bfa_trc_stop` prevents further trace writes, commonly after serious assertions. There is no durable persistence, but trace content is diagnostic state consumed by driver debug paths.

## Dependencies and Integration Points
The header depends on `bfad_drv.h` for kernel types, `ktime_get_ts64`, `list_head`, logging, and endian context. The 24-bit conversion helpers `bfa_hton3b` and `bfa_ntoh3b` are used by frame builders and FC id handling.

## Risks and Test Signals
Risks include raw macro manipulation of `list_head`, null or double-dequeued queue entries, callback reentrancy in wait counters, and endian-sensitive bit/byte interpretation of WWNs and FCIDs. Test signals are trace wrap/stop behavior, state transition entry actions, queue dequeue on empty and non-empty lists, wait counter zero transition, and FC id formatting on little- and big-endian builds.
