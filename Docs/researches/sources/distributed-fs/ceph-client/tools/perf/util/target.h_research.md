# sources/distributed-fs/ceph-client/tools/perf/util/target.h

## Purpose

`target.h` defines the common target-selection contract used by perf commands. It represents whether a command is operating on explicit PIDs, TIDs, CPUs, system-wide mode, BPF-selected tasks, inherited children, mmap usage, per-thread collection, and delayed start behavior.

## Important APIs, Types, and Functions

The central type is `struct target`, with string selectors (`pid`, `tid`, `cpu_list`, `bpf_str`, `attr_map`) and booleans that describe target mode. `enum target_errno` reserves perf-specific negative validation errors for mutually exclusive target combinations. The public declarations are `target__validate()`, `parse_uid()`, and `target__strerror()`. Inline helpers include `target__has_task()`, `target__has_cpu()`, `target__none()`, `target__enable_on_exec()`, `target__has_per_thread()`, and `target__uses_dummy_map()`.

## Control Flow and State

The header itself has no runtime control flow, but its inline predicates encode decisions used by record/stat/top setup. `target__enable_on_exec()` returns true for a command-spawned workload with no initial delay. `target__uses_dummy_map()` chooses dummy mmap events for task-oriented or per-thread modes so perf can bootstrap event delivery even without explicit CPU mmap rings.

## Dependencies and Integration Points

It depends only on standard types and integrates with record options, evlist creation, validation diagnostics, and target-to-thread/CPU map construction. It is consumed wherever perf translates CLI selectors into kernel perf_event attributes.

## Risks and Test Signals

Risks are mostly semantic: invalid combinations such as PID plus CPU or BPF plus TID must be rejected consistently by the implementation. Tests should cover each target mode, dummy-map decisions, delayed start behavior, and formatted validation errors for all `target_errno` values.
