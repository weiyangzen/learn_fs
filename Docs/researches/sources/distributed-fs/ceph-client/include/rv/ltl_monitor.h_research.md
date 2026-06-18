# sources/distributed-fs/ceph-client/include/rv/ltl_monitor.h

Purpose: Implements a generated LTL monitor runtime over per-task RV storage, including atom tracking, Büchi-state validation, trace output, and violation reaction.

Important APIs/types/functions: Defines a module-specific `rv_monitor`, allocates `ltl_monitor_slot`, initializes per-task `struct ltl_monitor`, and provides `ltl_atom_set()`, `ltl_atom_update()`, `ltl_atom_pulse()`, `ltl_validate()`, `ltl_trace_event()`, and task-newtask handling. Generated code must provide atom fetch/init, atom names, start logic, next-state calculation, and trace events.

Control flow and state: Init allocates a task monitor slot, attaches `task_newtask`, initializes all existing process threads and idle tasks, and marks atoms initially unknown. Atom updates clear unknown bits, refresh atoms, start the monitor once all atoms are known, compute possible next states from all active BA states, copy next states into the monitor, and react if no valid state remains.

Dependencies and integration: Depends on Linux RV task slots, tasklist traversal, scheduler/task tracepoints, seq buffers, generated LTL monitor helpers, and RV reactors.

Risks and test signals: Risks include task slot leaks, missing new-task initialization, atom unknown-state bugs, bitmap size mismatches, and trace buffer truncation. Tests should cover monitor load/unload, task creation, atom pulse semantics, violation traces, concurrent task updates, and generated model boundary sizes.
