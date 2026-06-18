# sources/distributed-fs/ceph-client/kernel/trace/rv/Kconfig

## Purpose
`kernel/trace/rv/Kconfig` defines the Runtime Verification configuration menu, event helper symbols, monitor-category symbols, monitor Kconfig inclusions, and reactor options.

## Important APIs, types, and functions
Key config symbols are `RV`, `RV_PER_TASK_MONITORS`, event selectors such as `RV_MON_EVENTS`, `RV_MON_MAINTENANCE_EVENTS`, `DA_MON_EVENTS_*`, `LTL_MON_EVENTS_ID`, `HA_MON_EVENTS_*`, monitor type helpers `RV_LTL_MONITOR` and `RV_HA_MONITOR`, and reactors `RV_REACTORS`, `RV_REACT_PRINTK`, and `RV_REACT_PANIC`.

## Control flow
Selecting `RV` enables tracing and exposes runtime verification infrastructure. The file then sources individual monitor Kconfig files grouped by scheduler, rtapp, deadline, and generic categories. Event helper symbols select shared trace event support needed by generated monitor code. Reactor config entries depend on `RV_REACTORS` and are enabled by default when reactors are available.

## State and persistence
Kconfig choices persist in the kernel build configuration, not at runtime. `RV_PER_TASK_MONITORS` sets a compile-time integer bound from 1 to 8 with default 2.

## Dependencies and integration points
This file integrates RV with the kernel tracing subsystem via `select TRACING`, with many monitor subdirectories through `source` statements, and with reactor implementations built from the matching Makefile. The comments mark insertion points for generated or future monitors.

## Risks and test signals
Risks include accidentally selecting event infrastructure without its dependent monitor semantics, missing a new monitor's Kconfig source line, default-on reactors surprising minimal builds, and compile failures if a sourced monitor path is absent. Test signals include `olddefconfig` visibility, builds with `CONFIG_RV=n` and `CONFIG_RV=y`, individual monitor selection, and reactor symbols producing expected object inclusion.
