# sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.c

## Purpose

`thread-stack.c` reconstructs per-thread call stacks and branch stacks from branch samples. It supports two related modes: lightweight callchain synthesis for samples, and full call/return pairing for call-path export through a `call_return_processor`.

## Important APIs, Types, and Functions

Internal `struct thread_stack_entry` stores a return address, timing/count snapshots, export IDs, a `call_path`, and flags for no-call, trace-end, and non-call synthetic edges. Internal `struct thread_stack` stores the dynamic entry array, trace number, running branch/instruction/cycle counts, kernel boundary, current comm, optional branch-stack ring, and retpoline detection state. Public functions include `thread_stack__event()`, `thread_stack__sample()`, `thread_stack__sample_late()`, `thread_stack__br_sample()`, `thread_stack__br_sample_late()`, `thread_stack__flush()`, `thread_stack__free()`, `thread_stack__depth()`, `thread_stack__set_trace_nr()`, `thread_stack__process()`, `call_return_processor__new()`, and `call_return_processor__free()`.

## Control Flow and State

Stacks grow in blocks of 2048 entries. Idle thread `pid == tid == 0` uses one stack per CPU; other threads use one stack. `thread_stack__event()` lazily allocates state, flushes when `trace_nr` changes, updates the optional branch ring, and then pushes calls or pops returns for callchain synthesis. `thread_stack__sample()` converts the current synthesized stack into an `ip_callchain`, inserting user/kernel context markers. Late sample helpers drop entries that happened after delayed hardware sample capture. `thread_stack__process()` is the richer export path: it tracks current comm, initializes the bottom frame, updates branch/insn/cycle counters, handles calls, returns, trace begin/end, missing calls/returns, optimized jumps to symbol starts, kernel-to-user returns, and x86 retpoline cleanup before invoking the processor callback.

## Dependencies and Integration Points

It integrates with `thread`, `machine`, `env`, `symbol`, `comm`, `event`, and `call-path` code. It consumes `PERF_IP_FLAG_*` branch metadata and `perf_sample` counts. Export users receive `struct call_return` records with parent db-id wiring for database output. Branch-stack output feeds sample synthesis, scripting, and report views.

## State and Persistence Behavior

State lives in `thread->ts` until flushed or freed. Trace discontinuities intentionally discard or export unfinished state to avoid misleading callchains. Call/return export stores per-entry db IDs and parent references but does not persist itself; persistence happens in the callback consumer. Branch ring buffers persist only up to the configured depth.

## Risks and Test Signals

Risks include stack corruption across trace gaps, missing return handling for longjmp-like flows, kernel/user boundary mistakes, retpoline over-filtering, branch-ring wrap errors, and memory pressure on deep stacks. Tests should exercise call/return pairs, unmatched calls, unmatched returns, trace begin/end, idle per-CPU stacks, late samples, retpoline thunks, branch stack wrapping, comm changes on exec, and callback error propagation.
