# sources/distributed-fs/lustre-release/lustre/mdt/mdt_fs.c

## Purpose

`mdt_fs.c` provides a small MDT filesystem-interface helper for per-export observability. Its exported function, `mdt_export_stats_init()`, initializes per-client/per-export lprocfs and debugfs statistics for an MDT export and creates an `open_files` debugfs view.

The file does not implement metadata operations. It connects MDT export lifecycle code to Lustre stats/debugfs infrastructure.

## Important APIs, Types, And Functions

`mdt_open_files_seq_fops` is a `struct file_operations` table for the per-export `open_files` debugfs file. It uses `ldebugfs_mdt_open_files_seq_open()` as the open callback and standard seq-file helpers for read, seek, and release.

`mdt_export_stats_init(struct obd_device *obd, struct obd_export *exp, void *localdata)` is called with the MDT OBD device, export, and a client `struct lnet_nid`. It initializes export lprocfs state, allocates the MDT stats counter block, initializes MDT counters, initializes per-NID LDLM stats, and creates the debugfs `open_files` entry under the export's NID debugfs directory.

## Control Flow

The function begins with `lprocfs_exp_setup(exp, client_nid)`. If that returns `-EALREADY`, the condition is treated as success because the per-export proc entries already exist. Other errors are returned.

On a fresh setup, it reads `exp->exp_nid_stats`, builds a stats path of the form `mdt.<obd_name>.exports.<nid>.stats`, and calls `ldebugfs_stats_alloc()` for `LPROC_MDT_LAST` counters using `LPROCFS_STATS_FLAG_NOPERCPU`. It initializes MDT stats counters as histograms with `mdt_stats_counter_init()`.

Next it initializes LDLM per-NID stats with `lprocfs_nid_ldlm_stats_init(stats)`. If that succeeds, it creates a read-only `open_files` debugfs file bound to the `nid_stat` object and `mdt_open_files_seq_fops`.

## State And Persistence Behavior

All state is runtime observability state. The function installs debugfs/lprocfs entries and allocates stats counters associated with `exp->exp_nid_stats`. There is no durable filesystem metadata mutation. The `-EALREADY` path makes repeated initialization idempotent for already-created proc entries.

The stats allocation is attached under the NID debugfs directory. Lifetime and cleanup are owned by the surrounding export/lprocfs infrastructure rather than by this file.

## Dependencies And Integration Points

The file depends on `lustre_compat/linux/fs.h` for file operation compatibility and `mdt_internal.h` for MDT stats declarations and `ldebugfs_mdt_open_files_seq_open()`.

It integrates with MDT export creation paths in `mdt_handler.c`, which call `mdt_export_stats_init()` for client exports. It also integrates with Lustre lprocfs/debugfs stats helpers, LDLM per-NID stats setup, seq-file read helpers, and LNet NID formatting through `libcfs_nidstr()`.

## Risks And Edge Cases

Stats allocation failure returns `-ENOMEM` after export proc setup has succeeded; cleanup is expected to be handled by the caller or lprocfs export teardown. If `lprocfs_nid_ldlm_stats_init()` fails, `nid_stats` remains allocated and the function returns the error without creating `open_files`.

The generated stats name uses a fixed stack buffer sized as `MAX_OBD_NAME * 4`. `scnprintf()` prevents overflow, but long OBD/NID strings can be truncated, so any consumer expecting globally unique debugfs stats names should account for truncation.

`debugfs_create_file()` return value is ignored. This matches the common pattern where debugfs visibility is noncritical, but tests should not assume `open_files` always exists after a successful return if debugfs creation fails.

## Test Signals

Tests should cover first-time export setup, repeated setup returning `-EALREADY`, stats allocation failure, LDLM stats initialization failure, and successful creation of MDT stats with `open_files` readability. Integration signals include the per-export stats path under debugfs/lprocfs, initialized `LPROC_MDT_LAST` counters, LDLM stats presence, and the ability to read the open-files seq file for a client export.
