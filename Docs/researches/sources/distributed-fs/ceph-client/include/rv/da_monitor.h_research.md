# sources/distributed-fs/ceph-client/include/rv/da_monitor.h

Purpose: Implements deterministic automata runtime-monitor templates for global, per-CPU, per-task, and per-object Linux runtime verification monitors.

Important APIs/types/functions: Defines `rv_this`, hook macros for HA extensions, `da_monitor_reset/start/enabled/handling_event`, monitor storage for each `RV_MON_TYPE`, trace/error helpers, and event entry points such as `da_handle_event()`, `da_handle_start_event()`, and `da_handle_start_run_event()`. Per-object mode uses `struct da_monitor_storage`, an RCU hash table, and helpers for create/get/destroy/fill storage.

Control flow and state: A monitor starts in the model initial state and ignores events until monitoring is enabled. Event handling reads `curr_state`, computes the next state, atomically updates with `try_cmpxchg`, invokes extension hooks, traces transitions, and resets on invalid transitions or too many racing retries. Per-task monitors allocate task RV slots; per-object monitors allocate hash entries and free them with RCU.

Dependencies and integration: Depends on generated automata, Linux RV core, tracepoints generated per monitor, task RV storage, RCU, hashtables, delayed work context assumptions, and optional HA hooks.

Risks and test signals: Risks include racing event updates, unsafe allocation in event context, per-object lifetime leaks, task slot exhaustion, reset-hook ordering, and tracepoint signature mismatch. Tests should compile each monitor type, run concurrent event streams, force invalid transitions, exercise per-object create/destroy under RCU, and verify trace/error emission.
