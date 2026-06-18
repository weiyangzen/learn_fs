# File Research: sources/block-storage/util-linux/sys-utils/lsirq.c

`lsirq.c` implements `lsirq(1)`, a command-line frontend for displaying interrupt or softirq counters.

Key behavior:
- Delegates data parsing and table construction to shared IRQ helpers through `get_scols_table()`.
- Supports JSON, key-value pairs, no headings, custom columns, sorting, input-file override, softirq mode, counter threshold, and CPU-list filtering.
- Defaults to `/proc/interrupts` or `/proc/softirqs` depending on `--softirq`.
- Defaults output columns to IRQ, total, and name.
- Parses CPU lists into a dynamically allocated cpuset sized from the system maximum CPU count.
- Prints column help via `irq_print_columns()`.

Important dependencies:
- `irq-common.h`/`irq-common.c` for column definitions, parsing, sorting, and smartcols table creation.
- util-linux cpuset and option-exclusion helpers.
- `libsmartcols` through the IRQ common layer.

Risk notes:
- JSON and pairs output are mutually exclusive.
- Invalid CPU count discovery aborts `--cpu-list`.
- The file itself is intentionally thin; most correctness lives in `irq-common`.
