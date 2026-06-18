# sources/distributed-fs/ceph-client/include/linux/rv.h

## Purpose
`rv.h` declares the Runtime Verification monitor and reactor interface used by kernel RV monitors.

## Important APIs, types, and functions
Core constants identify monitor scopes (`RV_MON_GLOBAL`, `RV_MON_PER_CPU`, `RV_MON_PER_TASK`, `RV_MON_PER_OBJ`) and name limits. Types include `struct da_monitor`, optional `struct ltl_monitor`, optional `struct ha_monitor`, `struct rv_reactor`, and `struct rv_monitor`. APIs include `rv_monitoring_on()`, `rv_register_monitor()`, `rv_unregister_monitor()`, `rv_get_task_monitor_slot()`, `rv_put_task_monitor_slot()`, `rv_register_reactor()`, `rv_unregister_reactor()`, and `rv_react()`.

## Control flow, state, and persistence
Monitors register with RV core and may be global, per-CPU, per-task, or per-object. Deterministic automata/LTL/HA monitor state is owned by monitor implementations and updated from tracepoints/events. Reactors register callbacks for violation responses; `rv_react()` formats a message and dispatches to the active reactor when RV is enabled. Registered monitors/reactors persist until unregistered.

## Dependencies and integration points
It depends on RV Kconfig options, monitor generated code, task monitor slot allocation, trace/events instrumentation, and optional automata models. Integration points include scheduler/preemption monitors, tracepoint-driven verification, sysfs/debugfs RV controls, and custom reaction policies.

## Risks and test signals
Risks include racing monitor state updates, exhausting per-task slots, reacting recursively from tracing contexts, accepting unknown LTL atoms/states, and build differences when RV subfeatures are disabled. Test signals include monitor register/unregister, per-task slot allocation/free, tracepoint event transitions, deliberate violation reactions, disabled-config no-op behavior, and generated automata state validation.
