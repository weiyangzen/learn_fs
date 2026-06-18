# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruprocfs.c

Purpose: creates `/proc/sgi_uv/gru` diagnostics for the GRU driver. It exposes statistics, microcode-operation timing, debug options, active CCH status, and per-GRU resource status.

Important APIs/functions: `gru_proc_init()` creates the proc subtree and files; `gru_proc_exit()` removes it. `statistics_show()` prints `gru_stats`, `statistics_write()` clears counters, `mcs_statistics_show()` prints MCS operation timing, `mcs_statistics_write()` clears timing, `options_show()` and `options_write()` expose `gru_options`, and seq operations drive `cch_status` and `gru_status`.

Control flow: init creates `statistics`, `mcs_statistics`, `debug_options`, `cch_status`, and `gru_status`. Reads use `seq_file` or `single_open()` callbacks. Writes to the statistics files reset in-memory counters. Writes to debug options parse a user value with `kstrtoul_from_user()`.

State and persistence: proc files are views over volatile in-memory state: `gru_stats`, `mcs_op_statistics`, `gru_options`, and `gru_base` chiplet/context structures. No state persists across module unload or reboot.

Dependencies and integration: depends on `grutables.h` structures and global counters maintained throughout the GRU driver. The proc path is an operational integration point for administrators and tests to inspect active contexts, ASIDs, PIDs, resource availability, and debug/statistics flags.

Risks: status output walks `gru->gs_gts[]` without taking the main context lock, so values are diagnostic snapshots rather than stable transactional views. The `cch_seq_show()` DSR display appears to use `ts_cbr_au_count * GRU_DSR_AU_BYTES` rather than `ts_dsr_au_count`, which is a reporting-risk signal. Reset writes are coarse and can erase concurrent diagnostic evidence.

Test signals: validate proc creation/removal, counter reset behavior, debug option parsing failures, and output shape while contexts are loaded/unloaded. Cross-check `gru_status` free/busy counts against allocation paths.
