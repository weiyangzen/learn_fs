# subset-b-006068 Research

Grouped source research for Linux kernel runtime-verification monitors, RV core/reactor support, and tracing helpers. Each file section preserves the source path in the title and is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.h

## Purpose

This shared header provides helper logic for the deadline runtime-verification monitor family. It normalizes deadline task/server identity, syscall policy extraction, task and server storage initialization, and task lifecycle callbacks used by deadline child monitors such as `nomiss`.

## Important APIs, Types, and Functions

The header exports `rv_deadline` and `rv_ext_sched_class`, defines `should_skip_syscall_handle()`, `is_supported_type()`, `is_server_type()`, `fair_server_id()`, `ext_server_id()`, `get_entity_id()`, `task_is_scx_enabled()`, `EXPAND_ID`, `EXPAND_ID_TASK`, `get_server_type()`, and `extract_params()`. When included with `RV_MON_TYPE`, it also provides `get_server()`, `init_storage()`, `handle_newtask()`, and `handle_exit()` for DA/HA monitor storage.

## Control Flow

Deadline monitor C files include this header after setting monitor macros, then use the ID helpers from tracepoint handlers. `extract_params()` decodes `sched_setscheduler` and `sched_setattr` syscall arguments, rejects `SCHED_FLAG_KEEP_POLICY`, and returns the new policy stripped of `SCHED_RESET_ON_FORK`. `init_storage()` pre-allocates fair and sched-ext server slots per possible CPU, optionally walks the task list to create storage for existing `SCHED_DEADLINE` tasks, and destroys the monitor on allocation failure.

## State and Persistence Behavior

The header itself persists no state, but it defines the ID scheme that makes monitor state stable across events: positive task PIDs for tasks, negative CPU-derived IDs for fair and sched-ext deadline servers, and `NO_SERVER_ID` for unknown server types. Storage is in monitor-owned DA/HA objects and is rebuilt on monitor enable/reset.

## Dependencies and Integration Points

It depends on deadline scheduler internals, syscall argument helpers, `sched_attr`, tasklist traversal, sched-class extension support, and RV DA/HA helper APIs. It integrates child monitors with `sched_dl_*`, `sched_switch`, `task_newtask`, `sched_process_exit`, and syscall tracepoints.

## Risks and Edge Cases

Negative server IDs assume the number of possible CPUs bounds the server namespace. The syscall parser deliberately copies only up to `sched_flags`, so changes in syscall ABI semantics must be reflected here. `get_server()` may rely on pre-created storage because allocating from deadline server tracepoints can deadlock. Task exit destroys only deadline-task storage, so policy transitions are handled by child monitors.

## Test Signals

Useful checks include enabling deadline monitors on systems with and without syscall tracepoints, changing policies via `sched_setscheduler` and `sched_setattr`, deadline task fork/exit coverage, sched-ext enabled and disabled builds, and stress with fair-server tracepoints to verify negative IDs remain unique.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_NOMISS`, the deadline-family monitor that checks deadline entities finish before their deadline.

## Important APIs, Types, and Functions

The symbol depends on `RV`, `HAVE_SYSCALL_TRACEPOINTS`, and `RV_MON_DEADLINE`, defaults to enabled, and selects `HA_MON_EVENTS_ID` so hybrid automata events include entity IDs.

## Control Flow

Selecting the symbol builds the `nomiss` monitor and enables its trace event declarations through `CONFIG_RV_MON_NOMISS`. It is intended as a child of the deadline monitor container.

## State and Persistence Behavior

The Kconfig file holds no runtime state. It controls compile-time availability and trace-event template selection.

## Dependencies and Integration Points

It points users to `Documentation/trace/rv/monitor_deadline.rst` and integrates with the RV, syscall tracepoint, deadline container, and HA monitor-event infrastructure.

## Risks and Edge Cases

The dependency on syscall tracepoints means architectures without syscall tracing cannot build this monitor even if deadline scheduler tracepoints exist. The help text has a minor typo in "deadiline".

## Test Signals

Configuration tests should verify that enabling `RV_MON_DEADLINE` and syscall tracepoints makes `RV_MON_NOMISS` visible, and that disabling any dependency removes it cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.c

## Purpose

This module implements the `nomiss` hybrid-automata monitor for deadline tasks and deadline servers. It checks that supported deadline entities move through ready, running, sleeping, idle, and throttled states without missing their deadline plus a configurable tardiness threshold.

## Important APIs, Types, and Functions

The monitor is `RV_MON_PER_OBJ` with `HA_TIMER_WHEEL` and a `struct sched_dl_entity *` target. `deadline_thresh` is a module parameter defaulting to `TICK_NSEC`. Core HA callbacks are `ha_get_env()`, `ha_reset_env()`, `ha_verify_invariants()`, `ha_convert_inv_guard()`, `ha_verify_guards()`, `ha_setup_invariants()`, and `ha_verify_constraint()`. Trace handlers include `handle_dl_replenish()`, `handle_dl_throttle()`, `handle_dl_server_stop()`, `handle_sched_switch()`, `handle_sys_enter()`, and `handle_sched_wakeup()`.

## Control Flow

On enable, the module initializes DA/HA storage, pre-allocates deadline task and server storage through `init_storage(false)`, and attaches deadline, scheduler, syscall, task creation, and process-exit tracepoints. Deadline replenish resets the clock; throttle is allowed only under defer or constrained-deadline guard conditions depending on the current state; ready and running states arm timers until `dl_deadline + deadline_thresh`. `sched_switch` maps blocked deadline tasks to suspend, incoming deadline tasks to switch-in, and server execution/idle transitions to server-specific events. Syscall entry detects policy transitions into or out of `SCHED_DEADLINE` and creates or resets per-task storage.

## State and Persistence Behavior

State is per deadline entity in HA storage and keyed by task PID or per-CPU negative server IDs from `deadline.h`. Clock state is stored in HA environments, with timers armed for ready/running states and canceled when leaving them. The monitor has no disk persistence; state is rebuilt on enable and destroyed on disable.

## Dependencies and Integration Points

The file depends on generated `nomiss.h`, `rv/ha_monitor.h`, `monitors/deadline/deadline.h`, deadline scheduler tracepoints, syscall tracepoints, task lifecycle tracepoints, and `rv_trace.h` event declarations. It registers as a child of `rv_deadline`.

## Risks and Edge Cases

The monitor must avoid allocation from deadline-server tracepoints, hence the up-front storage creation. Syscall policy parsing races with task lookup and policy changes, mitigated with RCU lookup but still approximate. Server handling depends on whether `next->dl_server` is directly available or has to be resolved by CPU. Disabling detaches RCU-heavy task/syscall probes first to reduce teardown latency.

## Test Signals

Test signals include running deadline workloads with controlled replenish/throttle paths, toggling `deadline_thresh`, policy transitions through both scheduler syscalls, task fork/exit while enabled, sched-ext server builds, and trace output for `event_nomiss`, `error_nomiss`, and `error_env_nomiss`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss_trace.h

## Purpose

This trace header contributes `nomiss` event definitions to the global RV trace system when the monitor is built.

## Important APIs, Types, and Functions

Under `CONFIG_RV_MON_NOMISS`, it instantiates `event_nomiss`, `error_nomiss`, and `error_env_nomiss` from ID-aware DA/HA trace event classes.

## Control Flow

The file is included by `rv_trace.h` inside the `CONFIG_HA_MON_EVENTS_ID` block. Monitor transitions emit `event_nomiss`, invalid state/event combinations emit `error_nomiss`, and environment guard failures emit `error_env_nomiss`.

## State and Persistence Behavior

The file has no state. It defines tracepoint ABI fields for entity ID, state, event, next state, final-state flag, and failing environment.

## Dependencies and Integration Points

It depends on `event_da_monitor_id`, `error_da_monitor_id`, and `error_env_da_monitor_id` classes being declared before inclusion. It integrates with ftrace/perf tracing and the HA monitor framework.

## Risks and Edge Cases

Tracepoint names are part of user-visible tracing ABI. Missing `CONFIG_HA_MON_EVENTS_ID` or missing inclusion in `rv_trace.h` would leave the monitor without expected trace outputs.

## Test Signals

Enable the monitor and inspect `/sys/kernel/tracing/events/rv/event_nomiss`, `error_nomiss`, and `error_env_nomiss`; force a guard violation to verify ID and environment fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/nomiss_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_NRP`, a scheduler monitor checking that preemption follows `need_resched` expectations.

## Important APIs, Types, and Functions

The symbol depends on `RV` and `RV_MON_SCHED`, defaults to enabled except on ARM64, and selects `DA_MON_EVENTS_ID` for per-task event tracing.

## Control Flow

When enabled, the monitor is built as a child of the scheduler monitor collection. The default exclusion on ARM64 reflects known instability on that architecture.

## State and Persistence Behavior

State is compile-time configuration only. Runtime per-task DA state is in `nrp.c`.

## Dependencies and Integration Points

It integrates with the scheduler monitor container and RV DA event configuration. The help text references `Documentation/trace/rv/monitor_sched.rst`.

## Risks and Edge Cases

Users can still force-enable it on ARM64 for testing, so runtime behavior should be treated cautiously there.

## Test Signals

Kconfig matrix tests should cover x86/default enabled, ARM64 default disabled, and dependency gating through `RV_MON_SCHED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.c

## Purpose

This module implements the `nrp` per-task deterministic automaton monitor for "need resched preempts." It observes IRQ entry, need-resched setting, and scheduler entry to verify preemption is preceded by reschedule intent.

## Important APIs, Types, and Functions

The monitor uses `RV_MON_PER_TASK`, generated `nrp.h`, and `rv/da_monitor.h`. Handlers are `handle_irq_entry()`, `handle_vector_irq_entry()` on x86 APIC builds, `handle_sched_need_resched()`, and `handle_schedule_entry()`. Lifecycle functions are `enable_nrp()`, `disable_nrp()`, and module registration under `rv_sched`.

## Control Flow

On enable, it initializes DA storage and attaches generic IRQ handler, scheduler need-resched, scheduler entry, and optional x86 vector IRQ tracepoints. `TIF_NEED_RESCHED` starts the task monitor on `sched_need_resched`; IRQ entry drives the current task into IRQ/preempt context; scheduler entry emits either `schedule_entry_preempt` or normal `schedule_entry` based on the tracepoint's `preempt` flag.

## State and Persistence Behavior

State is per task and held by the DA framework. It is reset/destroyed when the monitor is disabled and has no persistence beyond the enabled session.

## Dependencies and Integration Points

The file depends on `trace/events/irq.h`, `trace/events/sched.h`, optional `asm/trace/irq_vectors.h`, `rv_trace.h`, and the scheduler container `rv_sched`. It uses `rv_attach_trace_probe()` and `rv_detach_trace_probe()` for instrumentation.

## Risks and Edge Cases

The handler intentionally starts at a simpler state for `need_resched`, which may not mirror all live system state but reduces false complexity. Architecture-specific IRQ tracepoint coverage can differ; x86 vector IRQs are added because generic IRQ entry is insufficient there. ARM64 instability is reflected in Kconfig.

## Test Signals

Signals include preemptive scheduling workloads, IRQ-heavy workloads, checking x86 vector event attachment, forcing need-resched paths, and observing `event_nrp`/`error_nrp` tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.h

## Purpose

This generated header defines the `nrp` deterministic automaton model.

## Important APIs, Types, and Functions

States are `preempt_irq`, `any_thread_running`, `nested_preempt`, and `rescheduling`. Events are `irq_entry`, `sched_need_resched`, `schedule_entry`, and `schedule_entry_preempt`. `struct automaton_nrp` stores names, transition table, initial state, and final states.

## Control Flow

The transition table starts at `preempt_irq`; valid paths lead through rescheduling and scheduler-entry states, while preemptive schedule entry from `any_thread_running` is invalid. Only `any_thread_running` is marked final.

## State and Persistence Behavior

The header is static model data. Per-task runtime state is allocated by the DA monitor layer.

## Dependencies and Integration Points

It is included by `nrp.c` after `RV_MON_TYPE` is set and before `rv/da_monitor.h` consumes model symbols.

## Risks and Edge Cases

Because the monitor is generated, enum names and table dimensions must remain synchronized with handler event names. The initial state choice interacts with the C file's start-event shortcut.

## Test Signals

Tests should cover IRQ entry, need-resched, normal schedule, preempt schedule, and final-state trace formatting for ID-aware DA events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp_trace.h

## Purpose

This file defines `nrp` tracepoint instances for ID-aware DA monitor events.

## Important APIs, Types, and Functions

It instantiates `event_nrp` and `error_nrp` when `CONFIG_RV_MON_NRP` is enabled.

## Control Flow

Included by `rv_trace.h`, it binds the generic `event_da_monitor_id` and `error_da_monitor_id` classes to monitor-specific tracepoint names.

## State and Persistence Behavior

There is no runtime state; the output schema carries task ID, state, event, next state, and final-state status.

## Dependencies and Integration Points

It depends on `CONFIG_DA_MON_EVENTS_ID` and the event classes declared in `rv_trace.h`.

## Risks and Edge Cases

If the trace header is not included under the matching config block, the monitor can still run but will lack expected user-visible transition/error tracepoints.

## Test Signals

Inspect RV trace events after building with `RV_MON_NRP`, and trigger a known invalid path to observe `error_nrp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_OPID`, a scheduler monitor checking that operations such as wakeup and need-resched occur with interrupts and preemption disabled.

## Important APIs, Types, and Functions

The symbol depends on `RV` and `RV_MON_SCHED`, defaults to enabled, and selects `HA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting the symbol builds the per-CPU hybrid automata monitor and its implicit-ID trace events.

## State and Persistence Behavior

The file contains compile-time configuration only.

## Dependencies and Integration Points

It integrates with the scheduler monitor container, HA monitor framework, and documentation for scheduler RV monitors.

## Risks and Edge Cases

It requires reliable IRQ/preempt state sampling at tracepoint time; that semantic dependency is not visible in Kconfig.

## Test Signals

Build matrix coverage should verify event class selection and dependency gating through `RV_MON_SCHED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.c

## Purpose

This module implements the `opid` per-CPU hybrid automata monitor, verifying that scheduler wakeup and need-resched operations happen with expected IRQ/preemption masking.

## Important APIs, Types, and Functions

The monitor uses `RV_MON_PER_CPU`, generated `opid.h`, and HA callbacks `ha_get_env()`, `ha_verify_guards()`, and `ha_verify_constraint()`. Runtime handlers are `handle_sched_need_resched()` and `handle_sched_waking()`.

## Control Flow

On enable, it initializes the DA/HA monitor and attaches `sched_set_need_resched_tp` and `sched_waking`. Each event uses `da_handle_start_run_event()` against the per-CPU implicit monitor. Guards require interrupts disabled for `sched_need_resched`, and both interrupts disabled and preemption disabled for `sched_waking`.

## State and Persistence Behavior

State is per CPU and trivial because the generated automaton has one state. Environment values are sampled live from `irqs_disabled()` and `preempt_count()`; no state persists after disable.

## Dependencies and Integration Points

It depends on scheduler tracepoints, `rv/ha_monitor.h`, `rv_trace.h`, and `rv_sched`. It compensates for tracepoint-induced preemption disable under `CONFIG_PREEMPTION` by treating preempt count `1` as still enabled at the original event point.

## Risks and Edge Cases

Guard correctness depends on accurately interpreting preempt count around tracepoint execution. Non-preempt kernels always report preemption off. Because the automaton itself never changes state, all useful detection is in environment guards.

## Test Signals

Tests should inspect `error_env_opid` on forced wake/need-resched contexts, compare preempt and non-preempt builds, and validate per-CPU trace output with `event_opid`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid_trace.h

## Purpose

This file defines tracepoint instances for the implicit per-CPU `opid` monitor.

## Important APIs, Types, and Functions

It instantiates `event_opid`, `error_opid`, and `error_env_opid` from implicit DA/HA event classes when `CONFIG_RV_MON_OPID` is enabled.

## Control Flow

The file is included by `rv_trace.h` under HA implicit events. Transition events use the no-ID schema; environment errors include state, event, and environment name.

## State and Persistence Behavior

No state is stored here; tracepoint schemas are generated at build time.

## Dependencies and Integration Points

It requires `event_da_monitor`, `error_da_monitor`, and `error_env_da_monitor` to be declared first.

## Risks and Edge Cases

Because it is no-ID tracing, consumers infer CPU from trace metadata rather than an explicit field.

## Test Signals

Verify `/sys/kernel/tracing/events/rv/event_opid` and `error_env_opid` exist and emit records with expected state/event strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_PAGEFAULT`, an RT-application monitor that reports page faults from real-time tasks.

## Important APIs, Types, and Functions

It depends on `RV`, `RV_MON_RTAPP`, `X86 || RISCV`, and `MMU`; selects `RV_LTL_MONITOR` and `LTL_MON_EVENTS_ID`; and defaults to enabled.

## Control Flow

Selecting the symbol builds an LTL monitor under the `rtapp` container and enables ID-aware LTL trace events.

## State and Persistence Behavior

Only compile-time configuration is held here.

## Dependencies and Integration Points

The architecture dependency reflects page-fault tracepoint availability. The help text frames this as safe for production when disabled at runtime.

## Risks and Edge Cases

Unsupported architectures cannot build it even if similar page-fault hooks exist under different names.

## Test Signals

Kconfig tests should cover x86/RISC-V MMU builds and ensure no symbol on unsupported/no-MMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.h

## Purpose

This generated header contains the Buchi automaton for the pagefault LTL property.

## Important APIs, Types, and Functions

Atoms are `LTL_PAGEFAULT` and `LTL_RT`. The automaton has a single state `S0`, with `ltl_atom_str()`, `ltl_start()`, and `ltl_possible_next_states()` implementing the property.

## Control Flow

The formula keeps `S0` only when the task is not RT or no page fault occurred. If `RT && PAGEFAULT`, no next state is set, causing a violation in the LTL framework.

## State and Persistence Behavior

Runtime state is a per-task bitset of atoms and Buchi states. This header stores only generated static logic.

## Dependencies and Integration Points

It includes `<linux/rv.h>` and is consumed by `pagefault.c` and `rv/ltl_monitor.h`.

## Risks and Edge Cases

The model is intentionally minimal; any mistake in atom pulsing or RT atom refresh directly determines false positives or false negatives.

## Test Signals

Exercise all atom combinations: non-RT/no fault, non-RT/fault, RT/no fault, and RT/fault, expecting violation only for the last.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault_trace.h

## Purpose

This trace header defines `pagefault` LTL monitor tracepoint instances.

## Important APIs, Types, and Functions

It instantiates `event_pagefault` and `error_pagefault` under `CONFIG_RV_MON_PAGEFAULT`.

## Control Flow

Included by `rv_trace.h` under `CONFIG_LTL_MON_EVENTS_ID`, it binds generic LTL event/error classes to monitor-specific names.

## State and Persistence Behavior

No state is stored; event records carry task identity, state strings, atom strings, and next-state strings.

## Dependencies and Integration Points

It depends on `event_ltl_monitor_id` and `error_ltl_monitor_id`.

## Risks and Edge Cases

Trace records identify tasks by PID and comm, which can be reused over time; consumers should correlate with timestamps.

## Test Signals

Verify event creation and trigger a real-time task page fault to observe `error_pagefault`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_RTAPP`, the container for monitors that detect real-time application latency hazards.

## Important APIs, Types, and Functions

It depends on `RV` and at least two per-task monitor slots through `RV_PER_TASK_MONITORS >= 2`.

## Control Flow

When selected, the container monitor is built and child monitors such as `pagefault` and `sleep` can register beneath it.

## State and Persistence Behavior

It is a compile-time container selector only.

## Dependencies and Integration Points

It integrates with per-task LTL monitor slot accounting and the RV monitor hierarchy.

## Risks and Edge Cases

Insufficient per-task monitor slots prevent this collection from being available, even if individual monitor logic compiles.

## Test Signals

Kconfig tests should vary `RV_PER_TASK_MONITORS` and verify child monitors register under `rtapp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.c

## Purpose

This module registers the `rtapp` RV monitor container for real-time application monitors.

## Important APIs, Types, and Functions

It defines exported `struct rv_monitor rv_rtapp` with a name and description, plus module init/exit functions `register_rtapp()` and `unregister_rtapp()`.

## Control Flow

Module init calls `rv_register_monitor(&rv_rtapp, NULL)`, creating a top-level monitor directory. Module exit unregisters it. There are no enable/disable callbacks because it is a container.

## State and Persistence Behavior

The container holds no runtime monitoring state. Its presence in the global RV monitor list and tracefs tree persists only while the module/configured built-in code is active.

## Dependencies and Integration Points

It depends on `<linux/rv.h>` and is referenced by child monitors such as `pagefault` and `sleep`.

## Risks and Edge Cases

Child monitor registration depends on the parent being registered. Container detection in RV core also treats missing enable callbacks as a container signal.

## Test Signals

Check `available_monitors` and `monitors/rtapp/` in tracefs, and verify child names appear as `rtapp:pagefault` or `rtapp:sleep`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.h

## Purpose

This header declares the `rtapp` monitor container symbol for child monitors.

## Important APIs, Types, and Functions

It exposes `extern struct rv_monitor rv_rtapp;`.

## Control Flow

There is no control flow; child modules include it and pass `&rv_rtapp` to `rv_register_monitor()`.

## State and Persistence Behavior

It declares shared container state owned by `rtapp.c`.

## Dependencies and Integration Points

It requires `struct rv_monitor` to be visible from including code and is used by RT-app child monitors.

## Risks and Edge Cases

Linkage requires the container object to be built when children are built.

## Test Signals

Compile/link tests with `pagefault` and `sleep` enabled verify the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/rtapp/rtapp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SCHED`, the scheduler monitor collection.

## Important APIs, Types, and Functions

It depends on `RV` and at least three per-task monitor slots through `RV_PER_TASK_MONITORS >= 3`.

## Control Flow

Selecting it builds the scheduler container, allowing child monitors such as `nrp`, `opid`, `sco`, `scpd`, `snep`, `snroc`, `sssw`, and `sts` to register beneath it.

## State and Persistence Behavior

It holds compile-time configuration only.

## Dependencies and Integration Points

It integrates with the RV hierarchy and scheduler monitor documentation.

## Risks and Edge Cases

Per-task slot pressure can hide the whole monitor collection even though several children are per-CPU or implicit monitors.

## Test Signals

Kconfig matrix tests should verify child availability only when the container and enough per-task slots are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.c

## Purpose

This module registers the top-level `sched` RV monitor container for scheduler behavior specifications.

## Important APIs, Types, and Functions

It defines exported `struct rv_monitor rv_sched` with no enable, disable, or reset callbacks, and module init/exit registration functions.

## Control Flow

`register_sched()` registers the container with no parent. `unregister_sched()` removes it. Child monitors pass `&rv_sched` as their parent.

## State and Persistence Behavior

The container tracks registration and enabled state in the RV core but has no own automaton state. Enabling a container in RV core enables children.

## Dependencies and Integration Points

It depends on `<linux/rv.h>` and is included through `sched.h` by scheduler child monitors.

## Risks and Edge Cases

RV core treats a monitor with children or missing enable callback as a container; this file relies on that behavior. Registration order matters for nested child display and parent linkage.

## Test Signals

Tracefs should show `sched` in available monitors and child monitors nested under `monitors/sched/`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.h

## Purpose

This header declares the scheduler RV monitor container.

## Important APIs, Types, and Functions

It exposes `extern struct rv_monitor rv_sched;`.

## Control Flow

There is no runtime flow; child monitor modules include it for parent registration.

## State and Persistence Behavior

It declares state owned by `sched.c`.

## Dependencies and Integration Points

Including code must already know `struct rv_monitor`. It integrates all scheduler child monitors with the container.

## Risks and Edge Cases

The child modules must link with the container symbol.

## Test Signals

Compile/link tests with scheduler child monitors enabled verify the declaration and symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SCO`, a scheduler monitor ensuring `sched_set_state` occurs only in thread context.

## Important APIs, Types, and Functions

It depends on `RV` and `RV_MON_SCHED`, defaults to enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds the per-CPU `sco` automaton and implicit trace events.

## State and Persistence Behavior

The file stores compile-time configuration only.

## Dependencies and Integration Points

It integrates with the scheduler monitor collection and DA implicit event classes.

## Risks and Edge Cases

The monitor assumes scheduler entry/exit tracepoints bracket scheduling context accurately.

## Test Signals

Kconfig and runtime smoke tests should verify the `sco` child appears under `sched`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.c

## Purpose

This module implements the `sco` per-CPU DA monitor for scheduling-context operations, checking that `sched_set_state` happens only in thread context.

## Important APIs, Types, and Functions

It uses `RV_MON_PER_CPU`, generated `sco.h`, and `rv/da_monitor.h`. Handlers are `handle_sched_set_state()`, `handle_schedule_entry()`, and `handle_schedule_exit()`.

## Control Flow

On enable, the monitor initializes DA storage and attaches `sched_set_state_tp`, `sched_entry_tp`, and `sched_exit_tp`. A set-state event starts from thread context, scheduler entry transitions into scheduling context, and scheduler exit restarts the monitor in thread context.

## State and Persistence Behavior

State is per CPU in the DA framework. It is reset by `da_monitor_reset_all` and destroyed on disable.

## Dependencies and Integration Points

It depends on scheduler tracepoints, `rv_trace.h`, and the `rv_sched` parent.

## Risks and Edge Cases

Correctness depends on tracepoint ordering around schedule entry/exit. `da_handle_start_event()` on set-state/exit is used to resynchronize if the current model state is unknown.

## Test Signals

Enable under scheduler stress and check for unexpected `error_sco`; targeted tests can invoke state changes inside and outside scheduler context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.h

## Purpose

This generated header defines the two-state `sco` deterministic automaton.

## Important APIs, Types, and Functions

States are `thread_context` and `scheduling_context`; events are `sched_set_state`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The initial/final state is `thread_context`. `schedule_entry` moves to scheduling context, `schedule_exit` moves back, and `sched_set_state` is valid only in thread context.

## State and Persistence Behavior

The header provides static transition data; per-CPU state is stored by the DA monitor.

## Dependencies and Integration Points

It is included by `sco.c` and interpreted by `rv/da_monitor.h`.

## Risks and Edge Cases

Any mismatch between schedule tracepoint bracketing and actual context can produce false errors.

## Test Signals

Exercise state-set calls around scheduler transitions and check final-state annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco_trace.h

## Purpose

This trace header defines implicit DA event instances for `sco`.

## Important APIs, Types, and Functions

It instantiates `event_sco` and `error_sco` under `CONFIG_RV_MON_SCO`.

## Control Flow

Included by `rv_trace.h`, it maps generic no-ID DA trace classes to monitor-specific tracepoints.

## State and Persistence Behavior

No runtime state is stored.

## Dependencies and Integration Points

It depends on `event_da_monitor` and `error_da_monitor`.

## Risks and Edge Cases

No explicit CPU field is included; consumers rely on trace metadata for CPU context.

## Test Signals

Inspect RV trace events and trigger an invalid state-set-in-scheduler path if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SCPD`, checking that `schedule()` is called with preemption disabled.

## Important APIs, Types, and Functions

It depends on `RV`, `TRACE_PREEMPT_TOGGLE`, and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds a per-CPU DA monitor that consumes preempt toggle and scheduler entry/exit tracepoints.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It requires preemption tracepoints and scheduler monitor infrastructure.

## Risks and Edge Cases

Without `TRACE_PREEMPT_TOGGLE`, the model cannot observe preempt-disable state changes.

## Test Signals

Kconfig tests should verify dependency gating on `TRACE_PREEMPT_TOGGLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.c

## Purpose

This module implements the `scpd` per-CPU DA monitor for "schedule called with preemption disabled."

## Important APIs, Types, and Functions

It uses `RV_MON_PER_CPU`, generated `scpd.h`, preemptirq tracepoints, scheduler tracepoints, and handlers for preempt disable/enable and schedule entry/exit.

## Control Flow

On enable, DA storage is initialized and four tracepoints are attached. `preempt_disable` moves to `can_sched`; `preempt_enable` restarts the model in `cant_sched`; schedule entry is valid only when scheduling is allowed; schedule exit keeps the monitor in the can-schedule region until preemption is re-enabled.

## State and Persistence Behavior

State is per CPU and transient. `da_monitor_reset_all` resynchronizes the model on global monitoring re-enable.

## Dependencies and Integration Points

The file depends on `trace/events/preemptirq.h`, `trace/events/sched.h`, `rv_trace.h`, and `rv_sched`.

## Risks and Edge Cases

Tracepoint overhead and preemption accounting can affect observed order. Missing preempt toggles would make the automaton stale, which is why Kconfig depends on them.

## Test Signals

Run lockdep/scheduler stress with RV enabled, inspect `event_scpd` transitions, and verify no errors on normal schedule paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.h

## Purpose

This generated header defines the `scpd` DA model.

## Important APIs, Types, and Functions

States are `cant_sched` and `can_sched`; events are `preempt_disable`, `preempt_enable`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The model starts/finalizes in `cant_sched`. Preempt disable allows scheduling, preempt enable returns to the final state, and schedule entry/exit are valid only while in `can_sched`.

## State and Persistence Behavior

It supplies static state names and transition table; per-CPU runtime state is external.

## Dependencies and Integration Points

It is included by `scpd.c` and DA monitor helpers.

## Risks and Edge Cases

The final state being `cant_sched` means long preemption-disabled sections are non-final but not necessarily erroneous unless invalid events occur.

## Test Signals

Test transition coverage for all four events and invalid schedule-entry without prior preempt-disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd_trace.h

## Purpose

This header defines tracepoint instances for the `scpd` implicit DA monitor.

## Important APIs, Types, and Functions

It instantiates `event_scpd` and `error_scpd` under `CONFIG_RV_MON_SCPD`.

## Control Flow

Included by `rv_trace.h`, it maps generic implicit DA trace classes to monitor-specific names.

## State and Persistence Behavior

No state is stored in this header.

## Dependencies and Integration Points

It depends on no-ID DA event classes and ftrace event generation.

## Risks and Edge Cases

No explicit CPU ID is emitted beyond standard trace metadata.

## Test Signals

Build with `RV_MON_SCPD` and inspect trace event availability and emitted transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SLEEP`, an RT-app LTL monitor for undesirable sleeps by real-time tasks.

## Important APIs, Types, and Functions

It depends on `RV`, `HAVE_SYSCALL_TRACEPOINTS`, and `RV_MON_RTAPP`; selects `RV_LTL_MONITOR`, `TRACE_IRQFLAGS`, and `LTL_MON_EVENTS_ID`; and defaults enabled.

## Control Flow

Selecting it builds the LTL monitor and required trace event support under the `rtapp` container.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It requires syscall tracepoints, scheduler/lock tracepoints, and IRQ flags tracing. The help text warns of performance impact from `TRACE_IRQFLAGS`.

## Risks and Edge Cases

Production use may be costly due to selected tracing. Architectures without syscall tracepoints cannot build it.

## Test Signals

Kconfig tests should cover syscall tracing and `TRACE_IRQFLAGS` selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.c

## Purpose

This module implements the `sleep` LTL monitor, detecting real-time tasks that sleep in latency-dangerous ways while allowing known acceptable sleep/wake patterns.

## Important APIs, Types, and Functions

It uses generated `sleep.h`, `rv/ltl_monitor.h`, atom callbacks `ltl_atoms_fetch()` and `ltl_atoms_init()`, scheduler handlers, lock contention handlers, syscall enter/exit handlers, and `handle_kthread_stop()`.

## Control Flow

On enable, it initializes per-task LTL monitoring and attaches scheduler wake/set-state, lock contention, kthread stop, and syscall tracepoints. `ltl_atoms_fetch()` updates `LTL_RT` using `rt_or_dl_task()`. Initialization clears pulse atoms and classifies kernel threads, migration threads, and RCU tasks. Syscall entry marks clock nanosleep, futex wait/PI-lock, and epoll wait contexts; syscall exit clears those syscall atoms. Scheduler state changes pulse sleep or abort-sleep, wake paths capture wake source and priority, and RT mutex contention marks blocking context.

## State and Persistence Behavior

State is per task in the LTL framework. Pulse atoms represent transient events, while syscall/blocking atoms persist until exit/end handlers clear them. Kernel-thread classification persists in the monitor state and is recomputed at initialization. There is no disk persistence.

## Dependencies and Integration Points

It depends on scheduler, syscall, lock, IRQ context, futex constants, RT/deadline helpers, `rv_trace.h`, and the `rtapp` container.

## Risks and Edge Cases

The source includes a FIXME noting `handle_kthread_stop()` can race with other tracepoint handlers. Correctness depends on matching syscall enter/exit for all relevant sleep syscalls and on priority comparisons in wake context. Kernel-thread name classification for migration/RCU tasks is string based.

## Test Signals

Run RT tasks through futex wait, futex PI lock, epoll wait, absolute clock nanosleep, RT mutex blocking, interrupt/NMI wakes, kthread stop paths, and negative tests for unexpected `error_sleep`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.h

## Purpose

This generated header contains the Buchi automaton for the `sleep` LTL property.

## Important APIs, Types, and Functions

It defines nineteen atoms covering sleep/wake, RT status, syscall sleep forms, futex/RT mutex blocking, kernel-thread exceptions, and wake source/priority. It defines eight Buchi states `S0` through `S7`, `ltl_atom_str()`, `ltl_start()`, and `ltl_possible_next_states()`.

## Control Flow

The generated boolean logic allows safe cases such as non-RT/no-sleep, accepted blocking mechanisms, wake by equal-or-higher priority, hardirq/NMI wake, abort sleep, kthread stop, migration/RCU tasks, and selected absolute nanosleep/epoll/futex waits. Missing a next state indicates property violation.

## State and Persistence Behavior

Per-task atom and state bitsets are managed by the LTL framework. This file is static generated logic and stores no mutable data.

## Dependencies and Integration Points

It includes `<linux/rv.h>` and expects the implementation file to update atoms consistently with tracepoints.

## Risks and Edge Cases

The generated boolean variables are opaque, so maintaining correctness requires tracing back to the original LTL spec. Atom update omissions can invalidate the property more easily than the generated code itself.

## Test Signals

Property tests should target every named atom category and verify both accepted and violating next-state sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep_trace.h

## Purpose

This header defines tracepoint instances for the `sleep` LTL monitor.

## Important APIs, Types, and Functions

It instantiates `event_sleep` and `error_sleep` under `CONFIG_RV_MON_SLEEP`.

## Control Flow

Included by `rv_trace.h` under `CONFIG_LTL_MON_EVENTS_ID`, it binds generic LTL event/error classes to monitor-specific names.

## State and Persistence Behavior

No mutable state is stored here.

## Dependencies and Integration Points

It depends on the LTL ID event classes and the `sleep` monitor's atom/state string generation.

## Risks and Edge Cases

Task PID reuse can make long trace captures ambiguous without timestamps and task lifetime context.

## Test Signals

Enable the monitor, inspect tracefs event availability, and trigger a known violation to observe `error_sleep`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SNEP`, checking that scheduling does not enable preemption unexpectedly.

## Important APIs, Types, and Functions

It depends on `RV`, `TRACE_PREEMPT_TOGGLE`, and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds the per-CPU scheduler DA monitor.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It depends on preemption toggle tracepoints and scheduler monitor infrastructure.

## Risks and Edge Cases

The monitor cannot operate without precise preempt toggle visibility.

## Test Signals

Kconfig tests should verify the `TRACE_PREEMPT_TOGGLE` dependency and child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.c

## Purpose

This module implements the `snep` per-CPU DA monitor for "schedule does not enable preempt."

## Important APIs, Types, and Functions

It uses generated `snep.h`, `rv/da_monitor.h`, preempt toggle handlers, and scheduler entry/exit handlers.

## Control Flow

On enable, it attaches preempt disable/enable and scheduler entry/exit tracepoints. Preempt toggles use start events to resynchronize to non-scheduling context, schedule entry transitions into scheduling context, and schedule exit restarts in non-scheduling context.

## State and Persistence Behavior

State is per CPU and transient, resettable through `da_monitor_reset_all`.

## Dependencies and Integration Points

It depends on `trace/events/preemptirq.h`, `trace/events/sched.h`, `rv_trace.h`, and `rv_sched`.

## Risks and Edge Cases

The generated model's state name `scheduling_contex` contains a typo that is user-visible in traces. Resynchronizing on preempt toggles can mask some earlier missed events but avoids persistent desynchronization.

## Test Signals

Run scheduler/preempt stress and inspect `event_snep` and `error_snep` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.h

## Purpose

This generated header defines the `snep` DA model.

## Important APIs, Types, and Functions

States are `non_scheduling_context` and `scheduling_contex`; events are `preempt_disable`, `preempt_enable`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The model starts/finalizes outside scheduling context. Schedule entry enters scheduling context; schedule exit leaves it. Preempt enable inside scheduling context is invalid.

## State and Persistence Behavior

It defines static model data; runtime state is per CPU in DA storage.

## Dependencies and Integration Points

It is consumed by `snep.c` and DA helpers.

## Risks and Edge Cases

The typo in `scheduling_contex` appears in enum and trace names and should be treated as ABI-like once exposed.

## Test Signals

Transition tests should verify preempt enable during scheduling produces an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep_trace.h

## Purpose

This header defines implicit DA tracepoint instances for `snep`.

## Important APIs, Types, and Functions

It instantiates `event_snep` and `error_snep` under `CONFIG_RV_MON_SNEP`.

## Control Flow

Included by `rv_trace.h`, it exposes transition and error tracepoints.

## State and Persistence Behavior

No mutable state is stored.

## Dependencies and Integration Points

It depends on generic implicit DA event classes.

## Risks and Edge Cases

Trace names include generated state strings, including the model typo.

## Test Signals

Verify trace event availability and error output under forced invalid preempt/schedule ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SNROC`, checking that `sched_set_state` occurs only in the target task's own context.

## Important APIs, Types, and Functions

It depends on `RV` and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a per-task DA monitor with ID-aware trace events.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates with scheduler monitor infrastructure and per-task DA event tracing.

## Risks and Edge Cases

Task-context correctness depends on accurate switch-in/out tracepoints.

## Test Signals

Kconfig and runtime smoke tests should verify child registration and ID-aware events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.c

## Purpose

This module implements the `snroc` per-task DA monitor, checking that a task's state is set non-runnable only from its own running context.

## Important APIs, Types, and Functions

It uses generated `snroc.h`, `rv/da_monitor.h`, `handle_sched_set_state()`, and `handle_sched_switch()`.

## Control Flow

On enable, it attaches `sched_set_state_tp` and `sched_switch`. Switch-out starts/resynchronizes the previous task into other context; switch-in transitions the next task into own context. `sched_set_state` is handled for the task passed by the tracepoint.

## State and Persistence Behavior

State is per task and transient. The model starts in `other_context`, then becomes valid own-context after switch-in.

## Dependencies and Integration Points

It depends on scheduler tracepoints, the scheduler container, ID-aware DA trace events, and task identity from tracepoint arguments.

## Risks and Edge Cases

The first state-set event before a task has been observed running may be invalid by design. Switch tracepoint ordering is essential to avoid false positives.

## Test Signals

Exercise task state changes from self and external contexts, context switches, and observe `event_snroc`/`error_snroc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.h

## Purpose

This generated header defines the `snroc` per-task automaton.

## Important APIs, Types, and Functions

States are `other_context` and `own_context`; events are `sched_set_state`, `sched_switch_in`, and `sched_switch_out`.

## Control Flow

The model starts/finalizes in `other_context`. Switch-in moves to own context, switch-out returns to other context, and `sched_set_state` is valid only in own context.

## State and Persistence Behavior

Static transition data only; per-task state is stored by DA helpers.

## Dependencies and Integration Points

It is included by `snroc.c`.

## Risks and Edge Cases

Final state marks only `other_context`, so a currently running task is non-final but expected.

## Test Signals

Test all event transitions and invalid set-state from other context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc_trace.h

## Purpose

This header defines ID-aware DA tracepoints for `snroc`.

## Important APIs, Types, and Functions

It instantiates `event_snroc` and `error_snroc` under `CONFIG_RV_MON_SNROC`.

## Control Flow

Included by `rv_trace.h`, it exposes task-ID transition and error records.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

It depends on `event_da_monitor_id` and `error_da_monitor_id`.

## Risks and Edge Cases

PID reuse can affect long trace interpretation.

## Test Signals

Inspect tracefs events and ensure records include the task ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SSSW`, checking state-sleep and wakeup relationships.

## Important APIs, Types, and Functions

It depends on `RV` and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a per-task scheduler DA monitor.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates with scheduler and signal tracepoints through the implementation.

## Risks and Edge Cases

The property is sensitive to scheduler state distinctions such as yield, preempt, suspend, and RT lock wait.

## Test Signals

Kconfig tests should verify ID-aware event support and scheduler parent dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.c

## Purpose

This module implements the `sssw` per-task DA monitor, verifying that setting a task sleepable leads to sleeping and that sleeping tasks require wakeup or signal-related transitions.

## Important APIs, Types, and Functions

It uses generated `sssw.h`, `rv/da_monitor.h`, scheduler set-state/switch/wakeup handlers, and a signal-delivery handler.

## Control Flow

On enable, it attaches `sched_set_state_tp`, `sched_switch`, `sched_wakeup`, and `signal_deliver`. Set-state maps `TASK_RUNNING` to runnable and all other states to sleepable. Switch-out classifies preemption, yield, RT-lock blocking, or suspend; switch-in marks runnable execution. Wakeup uses a start event to allow resynchronization into runnable/signal-wakeup paths, and signal delivery resolves signal wakeup state.

## State and Persistence Behavior

State is per task and held in DA storage. It is reset/destroyed by the DA monitor lifecycle.

## Dependencies and Integration Points

It depends on scheduler and signal tracepoints, `rv_trace.h`, and the scheduler container.

## Risks and Edge Cases

Mapping all non-running states to sleepable can be conservative. The code has a special `TASK_RTLOCK_WAIT` blocking case because that state has racy conditions. Signal wakeups are modeled separately to avoid false errors when signals make tasks runnable.

## Test Signals

Exercise blocking sleeps, yields, preemptions, wakeups, signal delivery, and RT lock wait paths while monitoring `event_sssw` and `error_sssw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.h

## Purpose

This generated header defines the `sssw` per-task automaton.

## Important APIs, Types, and Functions

States are `runnable`, `signal_wakeup`, `sleepable`, and `sleeping`. Events cover runnable/sleepable set-state, blocking/suspend/preempt/yield switch variants, switch-in, wakeup, and signal delivery.

## Control Flow

The model starts/finalizes in `runnable`. Sleepable state can transition to sleeping on suspend/blocking and back to runnable on wakeup or runnable set-state. Sleeping accepts wakeup only. Signal wakeup is an intermediate state resolved by signal delivery or execution/wakeup paths.

## State and Persistence Behavior

Static model data only; per-task state is external.

## Dependencies and Integration Points

It is consumed by `sssw.c` and the DA monitor framework.

## Risks and Edge Cases

The transition table encodes nuanced scheduler semantics; implementation event classification must stay synchronized with the model.

## Test Signals

Transition tests should cover every switch subtype and invalid wake/sleep combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw_trace.h

## Purpose

This header defines ID-aware DA tracepoint instances for `sssw`.

## Important APIs, Types, and Functions

It instantiates `event_sssw` and `error_sssw` under `CONFIG_RV_MON_SSSW`.

## Control Flow

Included by `rv_trace.h`, it exposes per-task transition and error tracing.

## State and Persistence Behavior

No mutable state is stored.

## Dependencies and Integration Points

It depends on generic ID-aware DA event classes.

## Risks and Edge Cases

Consumers must account for PID reuse and task lifetime when interpreting IDs.

## Test Signals

Enable `sssw` and verify task IDs appear in transition/error records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_STALL`, a sample HA monitor that identifies tasks stalled longer than a threshold.

## Important APIs, Types, and Functions

It depends on `RV` and selects `HA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a standalone per-task HA sample monitor with ID-aware events.

## State and Persistence Behavior

Only compile-time configuration is held.

## Dependencies and Integration Points

It integrates directly with RV rather than a container and points to `Documentation/trace/rv/monitor_stall.rst`.

## Risks and Edge Cases

As a sample monitor, default thresholds and semantics may be illustrative rather than production policy.

## Test Signals

Kconfig tests should verify standalone availability with `RV` and HA ID event selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.c

## Purpose

This module implements the standalone `stall` per-task HA monitor that detects tasks remaining enqueued but not running longer than a configurable jiffy threshold.

## Important APIs, Types, and Functions

It uses `RV_MON_PER_TASK`, `HA_TIMER_WHEEL`, generated `stall.h`, `threshold_jiffies` module parameter, HA callbacks for jiffy clock handling, and scheduler switch/wakeup handlers.

## Control Flow

On wakeup from dequeued state or preemption from running state, it resets the jiffy clock. Entering `enqueued` starts a timer for `threshold_jiffies`; leaving enqueued cancels it. `sched_switch` maps blocking switch-out to wait/dequeued and other switch-outs to preempt/enqueued, then marks the next task switch-in. `sched_wakeup` marks a task enqueued.

## State and Persistence Behavior

State is per task in HA storage, with one clock environment `clk`. Timers are armed while a task is enqueued. State is destroyed on disable and has no persistence.

## Dependencies and Integration Points

It depends on scheduler tracepoints, HA monitor helpers, and ID-aware HA trace events. It registers with no parent.

## Risks and Edge Cases

Jiffy resolution means detection precision depends on HZ and timer behavior. The monitor treats all preempted running tasks as enqueued and all non-running non-preempt switch-outs as wait/dequeued, matching scheduler tracepoint semantics but not every scheduling nuance.

## Test Signals

Use runnable task starvation scenarios, vary `threshold_jiffies`, and observe `event_stall`, `error_stall`, and `error_env_stall`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.h

## Purpose

This generated header defines the `stall` HA automaton.

## Important APIs, Types, and Functions

States are `dequeued`, `enqueued`, and `running`; events are `sched_switch_in`, `sched_switch_preempt`, `sched_switch_wait`, and `sched_wakeup`; environment is `clk`.

## Control Flow

The model starts/finalizes in `dequeued`. Wakeup moves to enqueued, switch-in to running, preempt returns to enqueued, and wait returns to dequeued.

## State and Persistence Behavior

It declares static model data and an environment slot for the jiffy clock; runtime state lives in HA storage.

## Dependencies and Integration Points

It is included by `stall.c` and consumed by `rv/ha_monitor.h`.

## Risks and Edge Cases

Only `dequeued` is final; enqueued/running are expected transient states but final-state consumers should not treat them as immediate errors.

## Test Signals

Transition coverage should verify timer start/cancel behavior around enqueued entry/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall_trace.h

## Purpose

This header defines ID-aware HA tracepoints for the `stall` monitor.

## Important APIs, Types, and Functions

It instantiates `event_stall`, `error_stall`, and `error_env_stall` under `CONFIG_RV_MON_STALL`.

## Control Flow

Included by `rv_trace.h`, it exposes transition, invalid event, and environment/timer violation records.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

It depends on ID-aware DA/HA event classes.

## Risks and Edge Cases

Trace interpretation requires correlating task IDs with scheduler events and threshold settings.

## Test Signals

Force an enqueued task past the threshold and verify the environment error tracepoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_STS`, a scheduler monitor for relationships between scheduler calls and task switches.

## Important APIs, Types, and Functions

It depends on `RV`, `TRACE_IRQFLAGS`, and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds a per-CPU DA monitor consuming IRQ flag, IRQ entry, scheduler entry/exit, and switch tracepoints.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It requires IRQ flag tracing and scheduler monitor infrastructure.

## Risks and Edge Cases

The monitor is sensitive to architecture-specific interrupt tracepoint coverage.

## Test Signals

Kconfig tests should verify `TRACE_IRQFLAGS` gating and child monitor registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.c

## Purpose

This module implements the `sts` per-CPU DA monitor for "schedule implies task switch" and related IRQ-disabled scheduling invariants.

## Important APIs, Types, and Functions

It uses generated `sts.h`, `rv/da_monitor.h`, IRQ flag handlers, IRQ entry handlers, scheduler switch/entry/exit handlers, and optional x86 local APIC vector IRQ handlers.

## Control Flow

On enable, it attaches IRQ disable/enable, generic IRQ entry, scheduler switch, scheduler entry, scheduler exit, and optional x86 vector tracepoints. Events drive the automaton through can-schedule, scheduling, disable-to-switch, switching, enable-to-exit, and IRQ states. Schedule exit uses a start event to resynchronize to the final can-schedule state after a scheduling sequence.

## State and Persistence Behavior

State is per CPU in DA storage. It is resettable through `da_monitor_reset_all` and destroyed on disable.

## Dependencies and Integration Points

It depends on `trace/events/irq.h`, `trace/events/preemptirq.h`, `trace/events/sched.h`, optional `asm/trace/irq_vectors.h`, and the scheduler container.

## Risks and Edge Cases

IRQ tracepoint coverage varies by architecture; x86 vector tracepoints are attached to cover local timer, irq work, reschedule, and call-function interrupts. The property can be affected by nested IRQs and precise ordering of IRQ enable/disable relative to scheduler tracepoints.

## Test Signals

Run scheduler and interrupt stress, inspect `event_sts` and `error_sts`, and compare x86/local-APIC builds with non-x86 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.h

## Purpose

This generated header defines the `sts` scheduler/task-switch automaton.

## Important APIs, Types, and Functions

States are `can_sched`, `cant_sched`, `disable_to_switch`, `enable_to_exit`, `in_irq`, `scheduling`, and `switching`. Events are `irq_disable`, `irq_enable`, `irq_entry`, `sched_switch`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The model starts/finalizes in `can_sched`. Schedule entry enters scheduling, IRQ disable moves toward a required switch, switch then requires IRQ enable before exit, and IRQ entry has dedicated transitions.

## State and Persistence Behavior

The header stores static transition data only; runtime state is per CPU in DA storage.

## Dependencies and Integration Points

It is consumed by `sts.c` and DA monitor helpers.

## Risks and Edge Cases

The model encodes strict event ordering; small tracepoint reorderings can surface as monitor errors.

## Test Signals

Transition tests should cover scheduler entry/exit with and without switches, interrupt entry during disabled sections, and invalid switch outside scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts_trace.h

## Purpose

This header defines implicit DA tracepoints for `sts`.

## Important APIs, Types, and Functions

It instantiates `event_sts` and `error_sts` under `CONFIG_RV_MON_STS`.

## Control Flow

Included by `rv_trace.h`, it exposes scheduler/task-switch monitor transitions and errors.

## State and Persistence Behavior

No runtime state is held in this header.

## Dependencies and Integration Points

It depends on generic implicit DA trace classes.

## Risks and Edge Cases

Per-CPU identity comes from tracing metadata rather than an explicit trace field.

## Test Signals

Verify event availability and emitted transitions under scheduler activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_WIP`, a sample wakeup-in-preemptive per-CPU monitor.

## Important APIs, Types, and Functions

It depends on `RV` and `TRACE_PREEMPT_TOGGLE`, selects `DA_MON_EVENTS_IMPLICIT`, and has no scheduler-container dependency.

## Control Flow

Selecting it builds a standalone per-CPU DA monitor using preempt toggle and wakeup tracepoints.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates with RV, preempt toggle tracepoints, and scheduler waking tracepoints.

## Risks and Edge Cases

The help text notes the monitor illustrates a limitation of preempt disable/enable events, so it is primarily a sample.

## Test Signals

Kconfig tests should verify standalone availability and dependency on `TRACE_PREEMPT_TOGGLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.c

## Purpose

This module implements the standalone `wip` per-CPU DA sample monitor for wakeups while in a preemptive context.

## Important APIs, Types, and Functions

It uses generated `wip.h`, `rv/da_monitor.h`, handlers for `preempt_disable`, `preempt_enable`, and `sched_waking`, plus normal RV module registration.

## Control Flow

On enable, it initializes DA storage and attaches preempt enable, scheduler waking, and preempt disable tracepoints. Preempt disable moves to non-preemptive; preempt enable restarts to preemptive; waking is valid only from non-preemptive according to the model.

## State and Persistence Behavior

State is per CPU and transient. The monitor registers without a parent and exposes `da_monitor_reset_all`.

## Dependencies and Integration Points

It depends on preemptirq and scheduler tracepoints, `rv_trace.h`, and RV core registration.

## Risks and Edge Cases

As documented, preempt toggle events can miss nested or initial preemption state details, so the sample can be sensitive to enable-time state. The tracepoint attach order differs from detach order but all are removed before destroy.

## Test Signals

Run wakeup-heavy workloads with preemption toggles, inspect `event_wip`/`error_wip`, and test monitor enable during both preemptive and non-preemptive contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.h

## Purpose

This generated header defines the `wip` sample automaton.

## Important APIs, Types, and Functions

States are `preemptive` and `non_preemptive`; events are `preempt_disable`, `preempt_enable`, and `sched_waking`.

## Control Flow

The model starts/finalizes in `preemptive`. Preempt disable enters non-preemptive, preempt enable exits it, and `sched_waking` is valid only in non-preemptive state.

## State and Persistence Behavior

Static transition data only; runtime state is per CPU.

## Dependencies and Integration Points

It is included by `wip.c` and DA helpers.

## Risks and Edge Cases

The model is intentionally illustrative and may flag behavior based on simplified preemption observation.

## Test Signals

Transition tests should cover wakeup before/after preempt disable and invalid repeated preempt toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip_trace.h

## Purpose

This header defines implicit DA tracepoints for `wip`.

## Important APIs, Types, and Functions

It instantiates `event_wip` and `error_wip` under `CONFIG_RV_MON_WIP`.

## Control Flow

Included by `rv_trace.h`, it binds generic implicit DA trace classes to the sample monitor.

## State and Persistence Behavior

No mutable state is stored.

## Dependencies and Integration Points

It depends on generic no-ID DA event classes.

## Risks and Edge Cases

CPU identity is implicit in standard trace metadata.

## Test Signals

Verify trace event availability and record formatting during wakeup/preempt events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_WWNR`, a sample wakeup-while-not-running per-task monitor.

## Important APIs, Types, and Functions

It depends on `RV` and selects `DA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a standalone per-task sample monitor with ID-aware events.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates directly with RV and scheduler tracepoints in the implementation.

## Risks and Edge Cases

The help text explicitly says the model is broken on purpose to test reactors.

## Test Signals

Kconfig tests should verify ID-aware event support and standalone monitor availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.c

## Purpose

This module implements the standalone `wwnr` per-task sample monitor for wakeup while not running. The model is intentionally flawed to exercise RV reactors.

## Important APIs, Types, and Functions

It uses generated `wwnr.h`, `rv/da_monitor.h`, `handle_switch()`, `handle_wakeup()`, and standard RV lifecycle registration.

## Control Flow

On enable, it initializes DA storage and attaches `sched_switch` and `sched_wakeup`. Switch-out starts monitoring only after the first interruptible suspension; other switch-outs are normal events. Switch-in moves a task to running, and wakeup emits a wakeup event for the target task.

## State and Persistence Behavior

State is per task in DA storage. It is reset by `da_monitor_reset_all` and destroyed on disable.

## Dependencies and Integration Points

It depends on scheduler tracepoints, ID-aware DA events, and RV core registration. It has no parent container.

## Risks and Edge Cases

Because the model is deliberately broken, errors are expected and useful for reactor testing. Starting only after interruptible suspension means early task history is ignored.

## Test Signals

Enable with `printk` or `panic` reactors in controlled environments, run sleep/wakeup workloads, and observe `event_wwnr`/`error_wwnr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.h

## Purpose

This generated header defines the intentionally broken `wwnr` sample automaton.

## Important APIs, Types, and Functions

States are `not_running` and `running`; events are `switch_in`, `switch_out`, and `wakeup`.

## Control Flow

The model starts/finalizes in `not_running`. Switch-in enters running, switch-out leaves running, wakeup is accepted in not-running, and wakeup while running is invalid.

## State and Persistence Behavior

Static model data only; runtime state is per task in DA storage.

## Dependencies and Integration Points

It is included by `wwnr.c` and DA monitor helpers.

## Risks and Edge Cases

The model's intentional mismatch with real scheduler wakeup behavior is used to test reactor paths, not to enforce production correctness.

## Test Signals

Trigger wakeup while running and verify `error_wwnr` plus selected reactor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr_trace.h

## Purpose

This header defines ID-aware DA tracepoints for `wwnr`.

## Important APIs, Types, and Functions

It instantiates `event_wwnr` and `error_wwnr`; comments note the ID is the task PID.

## Control Flow

Included by `rv_trace.h`, it exposes per-task transition and error records for the sample monitor.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It depends on generic ID-aware DA event classes.

## Risks and Edge Cases

PID reuse applies to trace interpretation, and the monitor is expected to generate errors by design.

## Test Signals

Verify trace records include PID and expected transition strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_panic.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_panic.c

## Purpose

This module registers the `panic` RV reactor, which panics the kernel when a monitor exception triggers the selected reactor.

## Important APIs, Types, and Functions

`rv_panic_reaction()` calls `vpanic(msg, args)`. `rv_panic` is a `struct rv_reactor` with name `panic`, description, and reaction callback. Module init/exit register and unregister the reactor.

## Control Flow

When loaded, `register_react_panic()` calls `rv_register_reactor(&rv_panic)`. If a monitor selects this reactor and `reacting_on` is true, RV core calls the reaction through `rv_react()`, leading directly to `vpanic()`.

## State and Persistence Behavior

The only state is the reactor's registration in the RV reactor list and any monitor selection pointing at it. It persists while the module is loaded.

## Dependencies and Integration Points

It depends on `<linux/rv.h>` reactor APIs and integrates with `rv_reactors.c` selection files under `monitors/*/reactors`.

## Risks and Edge Cases

This reactor is destructive by design. It should be used only when a monitor violation should halt the system. Registration ignores the return value, so duplicate registration failures do not abort module init.

## Test Signals

In a controlled test kernel, select `panic` for a deliberately failing monitor such as `wwnr` and verify a panic occurs with the monitor message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_printk.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_printk.c

## Purpose

This module registers the `printk` RV reactor, which logs monitor exception messages to the kernel log without halting the system.

## Important APIs, Types, and Functions

`rv_printk_reaction()` calls `vprintk_deferred(msg, args)`. `rv_printk` is a `struct rv_reactor` named `printk`, with module init/exit registration.

## Control Flow

On load, the reactor is registered. When selected for a monitor and reactors are globally enabled, `rv_react()` invokes the deferred printk callback for violations.

## State and Persistence Behavior

State is limited to reactor registration and monitor selection. No messages are persisted beyond normal kernel log behavior.

## Dependencies and Integration Points

It depends on RV reactor APIs and integrates with the reactor selection tracefs files created by `rv_reactors.c`.

## Risks and Edge Cases

High-frequency monitor violations can flood kernel logs. Registration return value is ignored, so duplicate-name failures are silent to module init.

## Test Signals

Select `printk` on a monitor that can violate and verify deferred kernel log output without panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/reactor_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/rv.c

## Purpose

This file implements the runtime-verification user interface, monitor registration hierarchy, monitor enable/disable control, global monitoring switch, per-task monitor slot allocation, and tracefs/debugfs-style files under `rv/`.

## Important APIs, Types, and Functions

It defines `rv_interface_lock`, `rv_root`, `rv_monitors_list`, task monitor slot state, `get_monitors_root()`, `rv_get_task_monitor_slot()`, `rv_put_task_monitor_slot()`, `rv_is_nested_monitor()`, `rv_is_container_monitor()`, `rv_enable_monitor()`, `rv_disable_monitor()`, `rv_register_monitor()`, `rv_unregister_monitor()`, `rv_monitoring_on()`, and `rv_init_interface()`. File operations implement `available_monitors`, `enabled_monitors`, `monitoring_on`, and per-monitor `enable`/`desc`.

## Control Flow

Initialization creates `rv/`, `rv/monitors`, monitor list files, global `monitoring_on`, initializes reactors, and turns monitoring on. Monitor registration validates name length and uniqueness, rejects nested parents beyond one level, creates the monitor directory, and inserts children next to their parent. Enabling a container enables each direct child; disabling a container disables all direct children and synchronizes tracepoint callbacks once. Writing `enabled_monitors` enables or disables by name, with `!` disabling and truncate disabling all. Turning monitoring back on resets enabled monitors first to resynchronize state after ignored events.

## State and Persistence Behavior

State is in memory: registered monitor list, tracefs dentries, enabled flags, parent/root pointers, global `monitoring_on`, and per-task monitor slot allocation. There is no persistence across reboot or module unload.

## Dependencies and Integration Points

It depends on tracefs helpers, seq files, mutex/guard cleanup helpers, RV public APIs, optional RV tracepoints, and reactor initialization. Monitor modules call `rv_register_monitor()`/`rv_unregister_monitor()` and use `rv_monitoring_on()` indirectly through monitor frameworks.

## Risks and Edge Cases

Global locking serializes registration and user writes. Disable paths call `tracepoint_synchronize_unregister()` to avoid callbacks using destroyed state. Container detection relies on child list adjacency and missing enable callbacks. Writing nested names trims the parent prefix and matches by child name only, so duplicate child names across containers would conflict with the global uniqueness check.

## Test Signals

Tracefs tests should cover available/enabled reads, enable/disable writes, `!monitor` disable, truncate disable-all, container enable/disable, monitoring_on reset behavior, registration duplicate/name-length failures, and task monitor slot exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/rv.h

## Purpose

This private RV header defines shared RV interface structures, tracefs wrappers, size limits, exported RV core symbols, and reactor stubs/prototypes.

## Important APIs, Types, and Functions

It defines `struct rv_interface`, aliases RV file modes and create/remove helpers to tracefs APIs, `DEFINE_FREE(rv_remove, ...)`, `MAX_RV_MONITOR_NAME_SIZE`, `MAX_RV_REACTOR_NAME_SIZE`, and extern declarations for locks, monitor list, monitor control helpers, and reactor setup.

## Control Flow

The header has no runtime flow. Compile-time conditionals provide real reactor functions under `CONFIG_RV_REACTORS` or no-op stubs otherwise.

## State and Persistence Behavior

It declares shared in-memory state but owns none. Tracefs dentries are managed by implementation files using the cleanup helper.

## Dependencies and Integration Points

It includes tracing internals, tracefs, mutex, and public `<linux/rv.h>`. It is used by RV core and reactor implementation files.

## Risks and Edge Cases

Name size constants constrain user-visible monitor/reactor names. Stubbing reactors when disabled means monitor directories omit reactor files without changing monitor code.

## Test Signals

Compile coverage with and without `CONFIG_RV_REACTORS`, and tests for monitor/reactor name length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv_reactors.c -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/rv_reactors.c

## Purpose

This file implements the RV reactor registry and user interface. Reactors are selectable reactions invoked when a runtime monitor reports a model exception.

## Important APIs, Types, and Functions

It defines `rv_reactors_list`, `rv_register_reactor()`, `rv_unregister_reactor()`, `reactor_populate_monitor()`, `init_rv_reactors()`, `rv_react()`, and the built-in `nop` reactor. File operations expose `available_reactors`, global `reacting_on`, and per-monitor `reactors` selection files.

## Control Flow

Initialization creates `available_reactors` and `reacting_on`, registers `nop`, and enables reacting. Monitor directory creation calls `reactor_populate_monitor()`, which creates a `reactors` file and sets the monitor reactor to `nop`. Reading a monitor reactor file lists all reactors with the selected one in brackets. Writing a reactor name swaps the monitor to that reactor, disabling and re-enabling the monitor if necessary; container swaps propagate to direct children. `rv_react()` checks `reacting_on` and monitor callback presence before invoking the selected reaction under a lockdep wait-free map.

## State and Persistence Behavior

State is in-memory: registered reactor list, per-monitor selected reactor pointer/callback, and global `reacting_on`. There is no persistence beyond module/runtime lifetime.

## Dependencies and Integration Points

It depends on RV core lock/list state, seq files, tracefs file creation through `rv.h`, memory barriers for `reacting_on`, and external reactors such as `printk` and `panic`.

## Risks and Edge Cases

Swapping a reactor on a container can enable all children afterward, even children that were previously off, as noted by the source comment. `reactor_populate_monitor()` assumes `nop` is registered before monitor population; initialization order must preserve that. Unregistering a reactor does not scan monitors that may still point to it.

## Test Signals

Test reactor listing, per-monitor selection, global `reacting_on` toggling, container reactor swaps, monitor re-enable around swaps, duplicate reactor registration, and violations with `nop`, `printk`, and `panic` reactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv_reactors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv_trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/rv/rv_trace.h

## Purpose

This header defines the RV trace event classes and includes monitor-specific trace snippets for DA, HA, LTL, and maintenance events.

## Important APIs, Types, and Functions

It declares classes `event_da_monitor`, `error_da_monitor`, `error_env_da_monitor`, `event_da_monitor_id`, `error_da_monitor_id`, `error_env_da_monitor_id`, `event_ltl_monitor_id`, `error_ltl_monitor_id`, and `rv_retries_error`. It includes monitor trace headers conditionally by config.

## Control Flow

Build-time config blocks decide which event classes and monitor instances are emitted. DA/HA implicit events omit explicit IDs; ID events include an integer entity/task ID. LTL events include task comm/PID plus states, atoms, and next-state strings. The bottom sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for `define_trace.h`.

## State and Persistence Behavior

The header stores no runtime state, but it defines tracing ABI and event schemas visible through ftrace/perf.

## Dependencies and Integration Points

It depends on Linux tracepoint macros, `<linux/rv.h>`, task structs for LTL events, and the generated monitor trace headers under `monitors/*/*_trace.h`.

## Risks and Edge Cases

Adding a new monitor requires inserting its trace header in the matching config block. Tracepoint names and fields are user-visible. LTL task identity uses comm and PID, which can change or be reused.

## Test Signals

Build configs should cover implicit DA, ID DA, implicit/ID HA, LTL, and maintenance events; runtime tests should list `/sys/kernel/tracing/events/rv/` and validate sample event formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/rv/rv_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/simple_ring_buffer.c -->
# sources/distributed-fs/ceph-client/kernel/trace/simple_ring_buffer.c

## Purpose

This file implements a lightweight per-CPU simple ring buffer over caller-provided pages. It supports reserving and committing trace-style events, swapping a reader page for consumption, resetting, enabling/disabling tracing, and initialization/unload with direct or custom page loaders.

## Important APIs, Types, and Functions

Exported APIs are `simple_ring_buffer_swap_reader_page()`, `simple_ring_buffer_reserve()`, `simple_ring_buffer_commit()`, `simple_ring_buffer_reset()`, `simple_ring_buffer_init_mm()`, `simple_ring_buffer_init()`, `simple_ring_buffer_unload_mm()`, `simple_ring_buffer_unload()`, and `simple_ring_buffer_enable_tracing()`. Internal helpers manage tagged list links, head discovery, page reset/init, tail movement, event size/time-extend formatting, and status transitions.

## Control Flow

Initialization loads a metadata page, one reader page, and at least two ring pages from a `ring_buffer_desc`, links ring pages circularly, tags the last page as pointing to the head, and stores page metadata. Writers reserve by atomically moving status from `READY` to `WRITING`, compute timestamp delta and optional time-extend event, move the tail if the current page lacks space, fill a `ring_buffer_event`, and return the payload pointer. Commit updates page commit offset, increments entry count, and releases status back to ready. Reader swap finds the tagged head, splices the reader page into the ring before the head, updates lost-event metadata from overruns, and hands the old head out as the new reader page.

## State and Persistence Behavior

State lives in `struct simple_rb_per_cpu`, `simple_buffer_page` descriptors, buffer data pages, and metadata counters. Link pointers use low-bit tags for head/head-moving markers. Counters track entries, overruns, pages lost/touched, reader ID, reader lost events, and timestamps. No data is persisted outside the provided memory pages.

## Dependencies and Integration Points

It depends on `linux/simple_ring_buffer.h`, ring buffer event layout, atomic/local operations, memory barriers, page-sized buffer assumptions, and exported GPL symbols for in-kernel users.

## Risks and Edge Cases

The link tagging assumes alignment leaves low bits free. Head movement uses release/acquire ordering and retry loops; bugs can cause reader/writer races or lost-event misreporting. `simple_ring_buffer_init_mm()` sets `meta->nr_subbufs` before `nr_pages` is populated, which is notable for readers of the metadata. Reserve does not validate event length against page capacity before formatting, relying on caller discipline and page movement logic.

## Test Signals

Tests should cover init with too few pages, reserve/commit/read swap, timestamp extension paths, page rollover and overrun accounting, reset while enabled/disabled, unload during writer quiescence, custom load/unload failure cleanup, and concurrent writer/reader stress with KCSAN/lockdep-style tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/simple_ring_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/synth_event_gen_test.c -->
# sources/distributed-fs/ceph-client/kernel/trace/synth_event_gen_test.c

## Purpose

This test module exercises in-kernel synthetic event creation and generation APIs. It creates synthetic events through command-building and descriptor-array paths, enables them, emits test records through multiple tracing APIs, and removes them on module exit.

## Important APIs, Types, and Functions

It uses `synth_event_gen_cmd_start()`, `synth_event_add_field()`, `synth_event_gen_cmd_end()`, `synth_event_create()`, `trace_get_event_file()`, `trace_array_set_clr_event()`, `synth_event_trace_array()`, `synth_event_trace_start()`, `synth_event_add_next_val()`, `synth_event_add_val()`, `synth_event_trace_end()`, `synth_event_trace()`, `trace_put_event_file()`, and `synth_event_delete()`. Test functions are `test_gen_synth_cmd()`, `test_empty_synth_event()`, `test_create_synth_event()`, `test_add_next_synth_val()`, `test_add_synth_val()`, and `test_trace_synth_event()`.

## Control Flow

Module init creates `gen_synth_test` by starting a command with four fields and adding three more; creates `empty_synth_test` by starting empty and adding all fields; creates `create_synth_test` from a static descriptor array; enables each event; emits records using array, sequential-value, named-value, and variadic trace helpers; then disables events before returning. Error paths delete events already created and release event files. Module exit disables all events, puts event files, and deletes the synthetic events.

## State and Persistence Behavior

Static pointers hold the three `trace_event_file` references while the module is loaded. Synthetic event definitions exist in the tracing subsystem until deleted. The test values are transient trace records in the trace buffer.

## Dependencies and Integration Points

It depends on `linux/trace_events.h`, dynamic synthetic event APIs, module ownership (`THIS_MODULE`), top-level tracing instance access, and the synthetic event subsystem.

## Risks and Edge Cases

Init error cleanup is staged and must match the events already created. Exit assumes all three event pointers were successfully initialized, which is fine after successful module load but would be unsafe if partial init somehow reached exit. Events must be disabled before deletion. The values are intentionally bogus and include string pointers cast to `u64`, which is acceptable for this kernel API test but not general user input.

## Test Signals

Build with `CONFIG_SYNTH_EVENT_GEN_TEST`, insert the module, inspect the trace buffer for `create_synth_test`, `empty_synth_test`, and `gen_synth_test`, verify named/sequential/array emission, remove the module, and confirm synthetic events are deleted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/synth_event_gen_test.c -->
