# sources/distributed-fs/ceph-client/lib/percpu_counter.c

## Purpose
Implements batched per-CPU counters for scalable approximate counting with precise sum and comparison paths.

## APIs, Control Flow, and State
Exports setters, batched add, sync, precise sum, multi-counter init/destroy, compare, limited add, and the global `percpu_counter_batch`. Each counter has a global `s64 count`, raw spinlock, and per-CPU `s32` deltas. `percpu_counter_add_batch()` keeps small changes on the local CPU and folds into the global count when a batch threshold is exceeded, using local cmpxchg when available or IRQ-disabled fallback otherwise. `__percpu_counter_sum()` locks and includes online plus dying CPUs. Init can allocate multiple adjacent percpu counters and registers debug objects and CPU hotplug list entries. CPU-dead callbacks fold the outgoing CPU's delta into global counts and recompute batch size.

## Dependencies, Integration, Risks, and Tests
Depends on percpu allocation, CPU hotplug, debugobjects, raw spinlocks, and module init. Risks include approximation errors when callers use rough reads, hotplug races if dying CPU deltas are missed, limited-add overflow assumptions, debug object false positives, and misuse after destroy. Test signals include hotplug folding tests, precise-vs-approx compare tests, limited-add boundary coverage, debugobjects free fixups, and stress tests with interrupt-context updates.
