<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/proc.c -->
# sources/distributed-fs/ceph-client/fs/afs/proc.c

## Purpose
Implements `/proc/net/afs` diagnostics and configuration for a network namespace.

## Important APIs, Types, And Functions
Exports `afs_proc_init()`, `afs_proc_cleanup()`, `afs_proc_cell_setup()`, `afs_proc_cell_remove()`, and `afs_put_sysnames()`. It implements seq_file views and writers for `cells`, `rootcell`, `servers`, `stats`, `sysname`, `addr_prefs`, and per-cell `vlservers` and `volumes`.

## Control Flow
Namespace initialization creates the proc tree. Readers iterate RCU-protected cell/server/volume/VL lists and print refcounts, active counts, DNS status, probe state, endpoint lists, address preferences, and counters. Writers allow adding pinned cells, setting the initial root cell once, changing `@sys` substitutions, and delegating address preference writes.

## State And Persistence
Proc writes mutate in-kernel namespace state: cell database, workstation cell, `afs_sysnames`, and address preferences. No file-backed persistence exists; values reset with namespace/module lifetime.

## Dependencies And Integration Points
Integrates procfs/seq_file, RCU lists from cell/server/volume management, DNS status enums, RxRPC peer address formatting, and address preference parsing.

## Risks And Edge Cases
Writers parse simple whitespace-delimited commands and must reject invalid names, recursive `@sys`, path separators, excessive substitutions, and repeated rootcell assignment. Readers rely on RCU and lock pairing; VL display assumes a valid server list when iterating.

## Test Signals
Read all proc files under active and empty namespaces, add cells through `cells`, set `rootcell`, update `sysname`, observe server/VL probe diagnostics, and run under lockdep with concurrent cell/server churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/proc.c -->
