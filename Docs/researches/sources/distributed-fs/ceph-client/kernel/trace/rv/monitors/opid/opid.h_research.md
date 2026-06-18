# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.h

## Purpose

This generated header defines the single-state `opid` HA model.

## Important APIs, Types, and Functions

It defines state `any`, events `sched_need_resched` and `sched_waking`, environments `irq_off` and `preempt_off`, and `struct automaton_opid`.

## Control Flow

Both events transition from `any` back to `any`; correctness is determined by HA guard checks in `opid.c`.

## State and Persistence Behavior

The model's state is always final and initial. Runtime state exists per CPU in the HA/DA layer, while environment storage is bounded by `MAX_HA_ENV_LEN`.

## Dependencies and Integration Points

It is included by `opid.c` and consumed by `rv/ha_monitor.h`.

## Risks and Edge Cases

Since the transition table cannot reject events, all violations depend on guard code and tracepoint coverage.

## Test Signals

Build tests should verify the environment static assertion; runtime tests should force guard failures and observe `error_env_opid`.
