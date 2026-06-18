# File Research: sources/block-storage/util-linux/sys-utils/irq-common.h

Purpose: Shared declarations and data structures for IRQ reporting utilities.

Core contents:
- Defines column ids for `IRQ`, `TOTAL`, `DELTA`, and `NAME`.
- Defines `struct irq_info` for per-interrupt totals/deltas/name, `struct irq_cpu` for per-CPU totals/deltas, and `struct irq_stat` for a whole snapshot.
- Defines `struct irq_output` for selected columns, sorting callback, and output modes (`json`, key-value pairs, no headings).
- Declares column lookup/printing, sort selection, snapshot freeing, and smartcols table construction functions.

Dependencies and integration:
- Includes util-linux `cpuset.h` and libsmartcols types through function declarations.
- Consumed by `irq-common.c` and `irqtop.c`.

Risks and edge cases:
- `irq_output.columns` is fixed-size at twice the column count; callers must use provided parsing helpers or maintain bounds.
