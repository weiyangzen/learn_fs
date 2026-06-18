# sources/distributed-fs/ceph-client/kernel/irq/proc.c

## Purpose
`proc.c` exposes generic IRQ state through procfs. It creates `/proc/irq`, per-IRQ control/status files, handler directories, default SMP affinity controls, and `/proc/interrupts` output for generic IRQ accounting.

## Important APIs, types, and functions
Important entry points are `init_irq_proc()`, `register_irq_proc()`, `unregister_irq_proc()`, `register_handler_proc()`, `unregister_handler_proc()`, and `show_interrupts()`. SMP helpers expose `smp_affinity`, `smp_affinity_list`, `affinity_hint`, `effective_affinity`, `effective_affinity_list`, `node`, and `default_smp_affinity`. `irq_spurious_proc_show()` reports spurious counters.

## Control flow
Initialization creates `/proc/irq`, registers `default_smp_affinity`, then creates directories for existing IRQ descriptors. When a handler is requested, `register_irq_proc()` creates `/proc/irq/<n>` plus affinity and spurious files, and `register_handler_proc()` creates a unique handler-name directory. Affinity writes parse cpumasks or CPU lists, reject masks without online CPUs except for architecture autoselection, and call `irq_set_affinity()`. `/proc/interrupts` iterates IRQ numbers, skips hidden/chained/unallocated descriptors, prints per-CPU counts, chip/domain/hwirq/level metadata, and action names.

## State and persistence
State consists of proc dentries stored in descriptors/actions plus user-visible snapshots of descriptor counters and affinity masks. Writes update live genirq affinity state; proc entries disappear when IRQs or handlers are unregistered.

## Dependencies and integration points
It depends on procfs, seq_file, irq descriptors, affinity helpers from `manage.c`, cpumask parsers, sparse IRQ lookup rules, kernel interrupt statistics, and architecture `arch_show_interrupts()` extension.

## Risks and test signals
Risks include proc entry lifetime races with descriptor removal, affinity writes making systems unusable, duplicate handler names, stale action directories, hidden IRQ leakage, and inconsistent `/proc/interrupts` snapshots without descriptor-specific proc protection. Test signals include request/free cycles, concurrent proc reads during free, affinity bitmask and list writes, default affinity rejection of offline-only masks, effective-affinity display, duplicate shared handler names, spurious file contents, and architecture-specific interrupt rows.
