<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/poll_state.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/poll_state.c

## Purpose

`poll_state.c` supplies the generic cpuidle polling state used by drivers that want a state 0 busy-wait option.

## Important APIs, Types, And Functions

`cpuidle_poll_state_init()` fills `drv->states[0]` with name `POLL`, zero latency/residency, power usage `-1`, `CPUIDLE_FLAG_POLLING`, and the `poll_idle()` enter callback. `poll_idle()` enables interrupts, marks the current task polling, loops on `need_resched()`, calls `cpu_relax()`, and stops after `cpuidle_poll_time()` expires.

## Control Flow

On entry the function records local time, clears `poll_time_limit`, enables IRQs, and uses `current_set_polling_and_test()` to avoid polling when reschedule is already pending. It checks elapsed time every `POLL_IDLE_RELAX_COUNT` relax operations, sets `poll_time_limit` when the limit is reached, disables IRQs, clears polling, and returns the state index.

## State And Persistence Behavior

The function updates `dev->poll_time_limit`; governors use that as feedback. The cached poll duration lives in `dev->poll_limit_ns` and is computed by the cpuidle core.

## Dependencies And Integration Points

It depends on scheduler polling flags, local clock, IRQ flag helpers, `cpu_relax()`, cpuidle driver state layout, and governor feedback fields.

## Risks And Test Signals

Risks include excessive CPU burn, incorrect IRQ state on exit, and stale poll limits after state disables. Test with haltpoll/menu/teo polling use, reschedule latency measurements, sysfs state disable changes, and tracepoints showing poll timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/poll_state.c -->
