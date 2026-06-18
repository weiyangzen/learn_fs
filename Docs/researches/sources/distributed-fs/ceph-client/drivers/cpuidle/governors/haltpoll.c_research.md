<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/haltpoll.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/haltpoll.c

## Purpose

`haltpoll.c` implements a guest-oriented cpuidle governor that alternates between polling and halt-style idle to reduce wakeup latency in virtualized environments where short sleeps are common.

## Important APIs, Types, And Functions

Module parameters control polling behavior: `guest_halt_poll_ns`, `guest_halt_poll_shrink`, `guest_halt_poll_grow`, `guest_halt_poll_grow_start`, and `guest_halt_poll_allow_shrink`. `haltpoll_select()` chooses state 0 polling or state 1 halt based on latency constraints, previous state, and poll timeout. `adjust_poll_limit()` grows or shrinks `dev->poll_limit_ns`. `haltpoll_reflect()` records the actual state and adjusts the poll limit after halt.

## Control Flow

At postcore init the governor registers only when `kvm_para_available()` is true. Selection returns polling for strict latency, alternates halt after a timed-out poll, and otherwise keeps the tick running while polling. Reflection grows the poll window if halt residency was below the global cap and shrinks it if sleeps exceed the cap.

## State And Persistence Behavior

Persistent per-CPU state is stored in generic `cpuidle_device` fields: `last_state_idx`, `poll_limit_ns`, `poll_time_limit`, and `last_residency_ns`. Module parameters can be changed at runtime through sysfs/module interfaces.

## Dependencies And Integration Points

It integrates with KVM paravirtual detection, cpuidle poll state behavior, scheduler tick control, power tracepoints, and governor registration.

## Risks And Test Signals

Risks include wasting CPU by over-polling, never growing from zero under unexpected wake patterns, and assuming state 1 is a useful halt state. Test in KVM guests with latency-sensitive workloads, module parameter changes, poll timeout tracing, and CPU utilization/power measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/haltpoll.c -->
