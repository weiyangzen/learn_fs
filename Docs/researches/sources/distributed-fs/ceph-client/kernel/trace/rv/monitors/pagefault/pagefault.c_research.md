# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.c

## Purpose

This module implements the `pagefault` LTL monitor that flags page faults by real-time or deadline tasks, including PI-boosted tasks.

## Important APIs, Types, and Functions

It uses generated `pagefault.h`, `rv/ltl_monitor.h`, `ltl_atoms_fetch()`, `ltl_atoms_init()`, and `handle_page_fault()`. Lifecycle functions are `enable_pagefault()`, `disable_pagefault()`, and registration under `rv_rtapp`.

## Control Flow

On enable, `ltl_monitor_init()` prepares per-task LTL state and the module attaches `page_fault_kernel` and `page_fault_user`. Each page fault pulses `LTL_PAGEFAULT` on `current`. `ltl_atoms_fetch()` continually updates `LTL_RT` from `rt_or_dl_task(task)`, so the Buchi automaton checks the current scheduling class/boost state.

## State and Persistence Behavior

Per-task LTL state is held in the LTL monitor framework. `LTL_PAGEFAULT` is initialized false on task creation and pulsed for one evaluation event. There is no persistence after disable.

## Dependencies and Integration Points

It depends on exception tracepoints, RT/deadline scheduler helpers, `rv_trace.h`, and the `rtapp` container.

## Risks and Edge Cases

The monitor reports only faults that pass through the architecture tracepoints selected by Kconfig. PI-boost detection via `rt_or_dl_task()` intentionally broadens scope beyond nominal RT policy. If tracing is disabled through the global RV switch, state can be reset on re-enable.

## Test Signals

Use RT/deadline tasks with deliberately unmapped memory, non-RT page-fault controls, kernel and user fault paths, and trace events `event_pagefault`/`error_pagefault`.
