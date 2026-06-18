# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/clock.h

## Purpose

This header declares the nVHE tracing clock interface and compiles it to no-ops when EL2 tracing is disabled.

## Important APIs, Types, And Functions

APIs are `trace_clock_update()` and `trace_clock()`.

## Control Flow

With `CONFIG_NVHE_EL2_TRACING`, callers can update clock conversion parameters and read a nanosecond timestamp. Without tracing, update is empty and reads return 0.

## State And Persistence Behavior

The enabled implementation persists conversion parameters in `clock.c`; the disabled inline version has no state.

## Dependencies And Integration Points

It is consumed by nVHE trace infrastructure and host hypcalls that update EL2 trace clock data.

## Risks And Test Signals

Risks are accidentally relying on nonzero timestamps when tracing is disabled. Test signals are trace timestamps changing after `__tracing_update_clock()` and zero timestamps in non-tracing builds.
