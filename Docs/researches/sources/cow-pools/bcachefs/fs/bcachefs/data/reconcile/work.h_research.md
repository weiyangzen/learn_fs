# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/work.h

Public interface for the reconcile worker and scan-cookie API.

Key contents:
- Defines `RECONCILE_SCAN_TYPES()` and `struct reconcile_scan` for fs, metadata, pending, stripes, device, and inode scans.
- Declares `bch2_reconcile_opts[]` string table.
- Defines `struct opt_change_scope`, its cleanup class, and `BCH_OPT_CHANGE_SCANS_MAX`.
- Declares scan enqueue helpers, pre/post option-change helpers, pending mutation, status rendering, thread lifecycle, and fs init/exit functions.
- Provides inline `bch2_reconcile_wakeup()` which increments `c->reconcile.kick` and wakes the RCU-protected thread.
- Provides inline `bch2_reconcile_pending_wakeup()` to enqueue a pending scan cookie and wake the worker.

Important invariants:
- `opt_change_scope` is intentionally cleanup-managed so failed option changes do not leak in-flight scan-cookie registrations.
- Waking uses RCU around `c->reconcile.thread` because stop/start synchronize with wakeups.
