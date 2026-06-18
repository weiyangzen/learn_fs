# sources/distributed-fs/ceph-client/kernel/module/stats.c

## Purpose
Collects debug statistics about module load successes and failures, with emphasis on virtual memory wasted by failed or duplicate module loads.

## Important APIs, Types, And Functions
Exports counters and helpers declared in `internal.h`: `total_mod_size`, `total_text_size`, `invalid_kread_bytes`, `invalid_decompress_bytes`, `modcount`, `failed_kreads`, `failed_decompress`, `try_add_failed_module`, `mod_stat_bump_invalid`, and `mod_stat_bump_becoming`. It defines `read_file_mod_stats` and initializes debugfs files under `mod_debugfs_root`.

## Control Flow
The loader increments byte and count counters at specific failure stages. Duplicate failures are tracked in `dup_failed_modules` with a bitmask distinguishing becoming-stage and load-stage failures. The debugfs `stats` file builds a bounded text report with totals, averages, wasted virtual memory, and a capped duplicate-failure table.

## State And Persistence
State is in atomic counters and an RCU list of `struct mod_fail_load` entries for the lifetime of the boot. It is not durable across reboot.

## Dependencies And Integration Points
Depends on debugfs, atomic counters, `module_mutex` for duplicate list mutation, module decompression stats, and `main.c` failure labels. It is enabled by `CONFIG_MODULE_STATS`.

## Risks And Edge Cases
Counters must match the failure stage to avoid misleading memory pressure conclusions. The debugfs preamble has explicit size expectations and WARNs on overflow. Duplicate list allocation failure is non-fatal but loses diagnostic data.

## Test Signals
Fault-inject kernel reads, decompression, duplicate loads before and after allocation, and module init failures. Verify debugfs counters, average calculations, duplicate reason masks, and no sleeps/deadlocks from atomic accounting.
