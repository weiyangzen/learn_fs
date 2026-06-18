# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/work.c

## Role

Implements the bcachefs background reconcile worker. Reconcile is the state-driven system that scans data, metadata, devices, stripes, and per-inode ranges for mismatches between current extent layout and configured IO path options, then schedules data moves or pointer changes to repair those mismatches.

## Main Responsibilities

- Encodes and decodes reconcile scan requests into `BTREE_ID_reconcile_scan` cookie keys.
- Maintains refcounted in-flight option-change registrations so a reconcile pass cannot clear a scan cookie while an option update is only half applied.
- Buffers reconcile work keys from logical and physical reconcile btrees to reduce contention with write-buffer flushing.
- Derives `data_update_opts` from `bch_extent_reconcile` records, including replica changes, target migration, checksum/compression rewrites, EC enable/disable, and bad/evacuating-device pointer removal.
- Moves direct data, btree nodes, and stripe work through `bch2_move_extent()` and `bch2_stripe_repair()`.
- Performs scan propagation for whole filesystem, metadata-only, device, stripe, and inode-scoped scans.
- Runs the reconcile kthread, phase scheduling, throttling, pending-work handling, copygc waits, and power-supply pause/resume.
- Exposes status and pending-scan text helpers for user-facing diagnostics.

## Scan Cookie Model

`reconcile_scan_encode()` maps structured scan requests to durable cookie positions. Reserved cookies cover filesystem-wide, metadata, pending, and stripes scans; device scans are encoded as `RECONCILE_SCAN_COOKIE_device + dev`; inode scans use the inode number directly when it is at or above `BCACHEFS_ROOT_INO`.

`bch2_set_reconcile_needs_scan_trans()` increments a cookie key in the reconcile scan btree. `bch2_clear_reconcile_needs_scan()` deletes the cookie only if the value still equals the value observed when the scan started, preventing concurrent scan requests from being lost.

## Option Change Guarding

The file defines `struct reconcile_scan_in_flight` and an rhashtable keyed by scan cookie. `bch2_set_reconcile_needs_scan_pre()` registers the cookie and increments it before an option change; `bch2_set_reconcile_needs_scan_post()` increments it again and wakes the worker after the option has settled. `opt_change_scope` cleanup unregisters cookies on both success and error paths.

This prevents a pass that scanned intermediate option state from deleting the only cookie that would cause a correct later pass.

## Reconcile Work Processing

Reconcile uses several btrees and phases:

- `BTREE_ID_reconcile_scan` for scan cookies and btree-node work buckets keyed by reconcile priority.
- `BTREE_ID_reconcile_hipri` and `BTREE_ID_reconcile_work` for logical data-order work.
- `BTREE_ID_reconcile_hipri_phys` and `BTREE_ID_reconcile_work_phys` for physical LBA-order work on rotational devices.
- `BTREE_ID_reconcile_pending` for work that cannot progress until devices/space/configuration change.

`next_reconcile_entry()` returns the next key for a phase. Non-scan work is buffered in a `darray_reconcile_work` of 1024 keys and then popped in order, reducing repeated btree walks and write-buffer contention.

## Data Option Derivation

`reconcile_set_data_opts()` is the central policy function. It inspects the extent's reconcile entry and produces a `struct data_update_opts`:

- Sets update type to `BCH_DATA_UPDATE_reconcile`.
- Chooses target and `BCH_WRITE_only_specified_devs` for non-hipri non-btree work.
- Drops bad, evacuating, offline, extra, wrongly targeted, wrongly checksummed, or wrongly compressed pointers.
- Handles erasure-code enablement by checking whether a stripe can form, avoiding endless retries when EC is impossible.
- Handles erasure-code disablement by setting `ptrs_kill_ec`.
- Marks work pending when no safe action can be taken, especially when replica reduction cannot happen without lowering required durability.

## Stripe Handling

`do_reconcile_stripe()` repairs stripe keys with `bch2_stripe_repair()`. If a stripe needs block evacuation, the stripe index and the current move IO sequence are stored in a retry list. `do_retry_stripes()` retries only after earlier data updates have drained, so stripe repair does not race data movement that it depends on.

`do_reconcile_scan_stripes()` recalculates whether stripes can widen after device/topology changes using a `widen_cache`.

## Scan Propagation

Filesystem and metadata scans walk root keys and btree levels with `do_reconcile_scan_btree()`. Leaf scanning is limited to extent and reflink btrees for full data scans; metadata scans skip leaves. Device scans walk backpointers for the selected device and update affected extents. Inode scans walk the logical extents for a single inode range.

When a scan sees a `KEY_TYPE_reflink_p` with `REFLINK_P_MAY_UPDATE_OPTIONS`, it follows the referenced reflink btree range and updates indirect extents with the referencing inode's IO options.

## Worker Lifecycle

`bch2_reconcile_thread()` waits until snapshot checking has completed, initializes a `moving_context` tied to the reconcile write point, then repeatedly runs `do_reconcile()`.

`do_reconcile()` advances through `reconcile_phases` in priority order: scan cookies, hipri btree work, hipri physical work, hipri logical work, normal btree work, normal physical work, normal logical work, and pending work. It flushes pending move IO between phases, waits on copygc when needed, and idles on the write IO clock when there is no visible work.

`bch2_reconcile_start()` creates the kthread unless mounted with `nochanges`; `bch2_reconcile_stop()` clears the RCU task pointer, synchronizes wakeups, stops the thread, and drops the task reference.

## Diagnostics and Initialization

`bch2_reconcile_status_to_text()` reports idle/running state, IO-clock wait timing, current phase/progress, and a reconcile thread backtrace. `bch2_reconcile_scan_pending_to_text()` reports whether scan work is pending once the filesystem may go read-write.

`bch2_fs_reconcile_init()` initializes the in-flight scan rhashtable and optional power-supply notifier. `bch2_fs_reconcile_exit()` destroys these resources and warns if in-flight scan entries remain.
