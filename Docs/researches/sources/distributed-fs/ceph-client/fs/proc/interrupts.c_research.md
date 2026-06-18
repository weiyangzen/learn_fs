<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/interrupts.c -->
## sources/distributed-fs/ceph-client/fs/proc/interrupts.c

Purpose: implements `/proc/interrupts`, exposing per-IRQ interrupt accounting through seq_file iteration.

Important APIs and functions: defines `int_seq_ops` with `int_seq_start`, `int_seq_next`, `int_seq_stop`, and architecture/core-provided `show_interrupts`; registers the file in `proc_interrupts_init` via `proc_create_seq`.

Control flow: the sequence position is treated as an IRQ number. Iteration starts while `*pos <= irq_get_nr_irqs()`, increments until it exceeds the current IRQ limit, and delegates each row to `show_interrupts`. `fs_initcall(proc_interrupts_init)` creates the root proc entry during boot.

State and persistence behavior: no private persistent state is stored in this file. It reads live IRQ topology and statistics from the generic IRQ subsystem on demand. The seq cursor is the only per-read state.

Dependencies and integration points: depends on `linux/interrupt.h`, `linux/irqnr.h`, procfs, and seq_file. The formatting and per-architecture data come from the IRQ subsystem's `show_interrupts` implementation.

Risks: IRQ counts and the number of IRQ descriptors can change while userspace reads, so output is a live snapshot rather than an atomic global view. Off-by-one errors in iterator bounds would either omit the synthetic header/last IRQ row expected by `show_interrupts` or walk past the IRQ limit.

Test signals: read `/proc/interrupts` on systems with sparse IRQs, many MSI/MSI-X vectors, CPU hotplug, and changing IRQ allocations; compare row count to `irq_get_nr_irqs`; verify seq_file seek/re-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/interrupts.c -->
