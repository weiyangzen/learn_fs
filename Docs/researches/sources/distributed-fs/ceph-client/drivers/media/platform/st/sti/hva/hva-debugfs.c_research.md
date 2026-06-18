# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-debugfs.c

Purpose: implements optional debugfs views and performance accounting for HVA device and per-context encoder state.

Important APIs and functions: exported hooks are `hva_debugfs_create`, `hva_debugfs_remove`, `hva_dbg_ctx_create`, `hva_dbg_ctx_remove`, `hva_dbg_perf_begin`, and `hva_dbg_perf_end`. Debugfs show functions expose device identity, registered encoders, last completed context, hardware registers, and currently running contexts.

Control flow: device probe creates a debugfs directory with `device`, `encoders`, `last`, and `regs` files. Context creation adds a numbered per-context file and initializes min performance metrics. Encoding paths call perf begin/end around hardware work. Context removal snapshots the last stream-info-bearing context for later inspection, then removes the file. Show handlers compute averages and format frame/stream/control/error/performance details.

State and persistence: runtime-only debug state lives in `hva->dbg` and `ctx->dbg`, including timestamps, min/max/total durations, periods, bitrate windows, and debugfs dentries. The last context snapshot persists only until device removal or overwrite by a later context.

Dependencies and integration points: depends on debugfs, seq_file show helpers, V4L2 control menu strings, HVA core types, and `hva_hw_dump_regs` from `hva-hw.c`.

Risks: debugfs reads wake hardware to dump registers, so they interact with runtime PM. Snapshotting an entire `hva_ctx` into `last_ctx` copies pointers and transient fields for diagnostics only; it must not be treated as a live context. Min metrics start at `UINT_MAX`, so displays before samples can look odd.

Test signals: mount debugfs and inspect files during idle, active encoding, after release, and with runtime PM suspended. Compare reported frames, bitrate, and durations against V4L2 buffer timestamps and payload sizes.
