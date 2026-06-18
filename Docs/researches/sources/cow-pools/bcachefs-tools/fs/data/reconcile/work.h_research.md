# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.h

## Role

Public interface for the reconcile worker implemented in `work.c`. It defines scan request types, option-change bracketing state, wakeup helpers, pending-work helpers, status output, and lifecycle entry points.

## Key Definitions

- `RECONCILE_SCAN_TYPES()` enumerates scan classes: `fs`, `metadata`, `pending`, `stripes`, `device`, and `inum`.
- `struct reconcile_scan` stores the scan type plus either a device index or inode number.
- `BCH_OPT_CHANGE_SCANS_MAX` is currently 4, with a comment noting no option change touches more than one bracketed scan today.
- `struct opt_change_scope` holds the filesystem pointer and scan cookies registered during an option change.

## API Surface

- `bch2_set_reconcile_needs_scan_trans()`, `bch2_set_reconcile_needs_scan()`: set/increment durable scan cookies.
- `bch2_set_reconcile_needs_scan_pre()` and `_post()`: bracket option changes so reconcile does not clear an in-progress scan.
- `bch2_set_fs_needs_reconcile()`: queue a full filesystem reconcile scan.
- `bch2_reconcile_scan_cookie_is_set()`: test whether a scan cookie key exists.
- `bch2_extent_reconcile_pending_mod()`: add or remove an extent from the pending reconcile class.
- `bch2_reconcile_status_to_text()` and `bch2_reconcile_scan_pending_to_text()`: diagnostic printers.
- `bch2_reconcile_start()`, `bch2_reconcile_stop()`, `bch2_fs_reconcile_init()`, `bch2_fs_reconcile_exit()`: runtime and filesystem lifecycle.

## Wakeup Behavior

`bch2_reconcile_wakeup()` increments `c->reconcile.kick`, RCU-loads the reconcile task pointer, and wakes it if present. The kick counter is used by the worker to restart passes when new work arrives.

`bch2_reconcile_pending_wakeup()` queues the pending scan cookie and wakes the worker.
