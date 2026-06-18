# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.h

## Purpose

This generated header is the C representation of the `nomiss` automaton consumed by the hybrid automata monitor implementation.

## Important APIs, Types, and Functions

It defines states `ready`, `idle`, `running`, `sleeping`, and `throttled`; events for deadline replenish, server idle/stop, throttle, switch-in/suspend, and wakeup; and HA environments `clk`, `is_constr_dl`, and `is_defer`. `struct automaton_nomiss` contains state names, event names, environment names, transition table, initial state, and final-state bitmap.

## Control Flow

The transition table starts in `ready`. Invalid transitions flag monitor errors, while valid transitions move entities among deadline lifecycle states. The generated table is interpreted by DA/HA helper code; the C file supplies guards, timers, and environment values.

## State and Persistence Behavior

The automaton defines the state encoding used by per-entity HA storage. It declares `env_max_stored_nomiss` and asserts it fits `MAX_HA_ENV_LEN`. Runtime state lives in the monitor framework, not in this static header.

## Dependencies and Integration Points

The header expects HA/DA monitor macros such as `MAX_HA_ENV_LEN` and `INVALID_STATE` handling from the including C file. It integrates with `nomiss.c` and trace events named after the same monitor.

## Risks and Edge Cases

Generated enum names are part of the contract with `nomiss.c`; changing the model without regenerating C handlers can break guard logic. Final states mark only `ready`, so resets and startup behavior must be consistent with the model's intended quiescent state.

## Test Signals

Build coverage should verify static assertions and enum references. Runtime tests should exercise every event from each state, especially invalid throttle/suspend paths and final-state trace annotations.
