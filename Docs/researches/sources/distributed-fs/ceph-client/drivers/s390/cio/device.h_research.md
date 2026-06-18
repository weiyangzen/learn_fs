# sources/distributed-fs/ceph-client/drivers/s390/cio/device.h

## Purpose
This header declares the CCW device finite-state-machine states/events and the internal helper APIs used by the CCW bus, I/O subchannel driver, recognition/path-verification code, request handling, timeout handling, machine-check recovery, and CMF integration.

## Important APIs, Types, and Functions
It defines `enum dev_state` with normal, recognition, online/offline, verification, boxed, quiesce, disconnected, CMF, and lock-stealing states; `enum dev_event` for not-operational, interrupt, timeout, and verify events; `fsm_func_t`; and external `dev_jumptable`. Inline `dev_fsm_event()` increments IRQ stats for interrupt events and dispatches the state-machine action. It declares helper APIs for subchannel init/recognition, online/offline, sense, internal request handling, path grouping/verification/disband, STLOCK, recovery, timers, not-operational/disconnected transitions, CMF retry/reactivation, and `dev_attr_cmb_enable`.

## Control Flow
The core inline flow is `dev_fsm_event()`: read the current private state, update interrupt accounting when needed, and call the state/event function from `dev_jumptable`. `dev_fsm_final_state()` identifies stable states that online/offline and recognition wait loops use.

## State and Persistence
The header defines symbolic state values but no storage. Runtime state lives in `ccw_device_private` owned by `asm/ccwdev.h`/implementation files. There is no persistence.

## Dependencies and Integration Points
It depends on CCW device definitions, timers, atomics, wait queues, notifiers, IRQ stats, and `io_sch.h`. It is the coordination contract between `device.c`, device FSM implementation files, path-grouping code, request code, and `cmf.c`.

## Risks and Test Signals
Risk areas include jumptable coverage for every state/event pair, interrupt accounting in special CMF states, wait loops relying on final-state classification, and state additions that require updates across multiple implementation files. Test signals include state-machine table compile coverage, interrupt/timeout/not-operational event injection, online/offline wait completion, CMF change/update retries, disconnected recovery, and path-verification/disband transitions.
