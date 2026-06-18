# File Research: sources/block-storage/util-linux/sys-utils/irqtop.c

Purpose: Implements `irqtop(1)`, an interactive or batch top-like display for kernel interrupt or softirq activity.

Core behavior:
- Supports curses screen mode by default and batch stdout mode with `--batch`; JSON implies batch mode.
- Periodically refreshes using `timerfd` and `epoll`, handles signals through `signalfd`, and accepts interactive sort keys from stdin.
- Displays a header with total interrupts, delta interrupts, hostname, and current timestamp.
- Shows optional per-CPU percentage tables (`auto`, `never`, `always`) and the main IRQ/softirq table from `irq-common.c`.
- Supports CPU filtering, refresh delay, iteration limit, selected columns, sort column, softirq mode, and total-count threshold.
- Interactive keys sort by IRQ (`i`), total (`t`), delta (`d`), name (`n`), or quit (`q`).

Important implementation details:
- `update_screen()` selects `/proc/softirqs` or `/proc/interrupts`, builds smartcols output, renders through curses or stdout, and retains the current snapshot as `prev_stat` for the next delta.
- `event_loop()` multiplexes timer, signals, and stdin. Window resize triggers terminal dimension refresh and `resizeterm()` when available.
- Terminal state is saved/restored around curses mode when stdin is a TTY.
- Default columns are `IRQ,TOTAL,DELTA,NAME`; `--output` is parsed through `irq_column_name_to_id()`.

Dependencies and integration:
- Uses `irq-common.c`, libsmartcols, curses/slang/ncurses variants, util-linux cpuset, time, monotonic, tty, hostname, and parsing helpers.

Risks and edge cases:
- The event loop returns an accumulated status but `main()` currently returns `EXIT_SUCCESS`, so update failures do not affect process exit status.
- Batch mode still uses the same event loop and timer semantics; an explicit iteration count is needed for bounded repeated batch output.
- Snapshot delta caveats from `irq-common.c` apply if IRQ rows appear/disappear between refreshes.
