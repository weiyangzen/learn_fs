# File Research: sources/block-storage/util-linux/sys-utils/irq-common.c

Purpose: Shared parser, sorter, and libsmartcols table builder for interrupt and softirq display tools.

Core behavior:
- Defines output columns (`IRQ`, `TOTAL`, `DELTA`, `NAME`) with smartcols width hints, alignment/truncation flags, help text, and JSON types.
- Parses `/proc/interrupts` or `/proc/softirqs`, counts active CPU columns from the header, sums per-IRQ and per-CPU totals over an optional CPU filter, and stores descriptive names.
- For softirqs, maps well-known softirq names such as `NET_RX`, `BLOCK`, and `RCU` to friendly descriptions.
- Builds smartcols tables for IRQ rows and for per-CPU percentage summaries.
- Computes deltas from a previous snapshot, sorts by total by default, and supports sorting by IRQ, total, delta, or name.

Important implementation details:
- CPU filtering is applied while accumulating totals; absent a cpuset all CPUs are included.
- `/proc/interrupts` parsing advances the input cursor by fixed-width counter fields after `sscanf("%10lu")`, matching the kernel file's column layout.
- `get_scols_table()` copies `irq_info` into a sortable result array so the original snapshot can be retained as the next `prev_stat`.
- Threshold filtering uses total counts, not deltas.

Dependencies and integration:
- Implements APIs declared in `irq-common.h`.
- Used by `irqtop.c` and likely other util-linux IRQ reporting tools.
- Uses libsmartcols, util-linux cpuset, string, pathnames, xalloc, and NLS helpers.

Risks and edge cases:
- Delta calculation assumes current and previous IRQ arrays have the same ordering and count. If `/proc/interrupts` changes between samples, deltas can be associated with the wrong row.
- Per-CPU total percentage divides by `curr->total_irq`; unusual empty input could risk invalid percentages.
