# sources/distributed-fs/ceph-client/kernel/kcsan/debugfs.c

## Purpose
Provides `/sys/kernel/debug/kcsan` for enabling/disabling KCSAN, displaying counters, maintaining report filter lists, and running a microbenchmark of runtime overhead.

## Important APIs, Types, and Functions
Defines `kcsan_counters` and counter names. Filter state is `report_filterlist`, protected by `report_filterlist_lock`. Main functions are `kcsan_skip_report_debugfs`, `insert_report_filterlist`, `set_report_filterlist_whitelist`, `show_info`, `debugfs_write`, `microbenchmark`, and `kcsan_debugfs_init`.

## Control Flow
Reads print enabled state, counters, filter type, and function list. Writes accept `on`, `off`, `microbench=<iters>`, `whitelist`, `blacklist`, or `!function_name`. Filter insertion resolves a function through kallsyms, grows the address array outside the raw spinlock, then appends under lock. Report filtering sorts lazily and uses bsearch on function starts.

## State and Persistence
Counters are atomic longs kept for the current boot. Filterlist memory persists until reboot and is not exposed as durable configuration. `kcsan_enabled` is toggled live with `WRITE_ONCE`.

## Dependencies and Integration Points
Depends on debugfs, seq_file, kallsyms, sort/bsearch, KCSAN core/reporting APIs, and raw spinlocks usable from report paths.

## Risks
Report filtering runs from diagnostic paths and must not allocate under raw locks. Duplicate entries are not deduplicated in kernel. Microbenchmark temporarily disables KCSAN globally and rewrites the current context, so it is a diagnostic tool rather than production state.

## Test Signals
Manual debugfs reads/writes validate command parsing. KCSAN reports should disappear or appear according to whitelist/blacklist mode. Counter changes provide runtime evidence of watchpoints, races, capacity pressure, and encoding false positives.
