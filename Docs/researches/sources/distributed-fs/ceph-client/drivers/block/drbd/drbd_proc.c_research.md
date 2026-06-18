# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_proc.c

## Purpose

`drbd_proc.c` renders the legacy `/proc/drbd` status view using `seq_file`. It reports module/protocol version information, per-minor connection/role/disk state, IO counters, pending counters, write-ordering mode, out-of-sync amount, optional synchronization or verification progress, and optional lower-level cache statistics. This is an observability file; it does not configure DRBD.

## Important APIs, Types, And Functions

- `struct proc_dir_entry *drbd_proc` is the procfs entry handle exported for DRBD proc registration elsewhere.
- `drbd_seq_show(struct seq_file *seq, void *v)` is the main seq_file show callback.
- `drbd_get_syncer_progress` computes total sync/verify work, remaining bitmap bits, and per-mille completion.
- `drbd_syncer_progress` formats the progress bar, percentage, remaining/total amount, estimated finish time, recent and average speed, desired sync rate, stalled marker, and optional sector-position detail.
- `seq_printf_with_thousands_grouping` formats kB/sec speeds with comma grouping.

## Control Flow

`drbd_seq_show` prints a header with `REL_VERSION`, generic-netlink API version, supported protocol range, and build tag. It then takes `rcu_read_lock` and iterates `drbd_devices` by minor through `idr_for_each_entry`. It inserts blank lines for gaps in minor numbering.

For an unconfigured device in `C_STANDALONE`, `D_DISKLESS`, secondary state, it prints `cs:Unconfigured`. Otherwise it snapshots `device->state`, derives the connection-state string, reads the first peer connection's network configuration via RCU to determine protocol letter, and emits the classic `/proc/drbd` line with role, disk states, protocol, suspension flags, congestion reason, AL suspension marker, network/disk counters, pending counters, epoch count, write ordering, and out-of-sync kB.

If the connection state is sync source, sync target, verify source, or verify target, `drbd_syncer_progress` appends detailed progress. Optional details are gated by `drbd_proc_details`: level 1 prints resync/activity-log cache stats and detailed sector position; level 2 adds blocked-on-activity-log count.

## State And Persistence Behavior

This file does not persist or mutate DRBD state. It reads live counters, bitmap weights, local-device metadata availability, activity-log suspension flags, sync marks, verify positions, and connection configuration. Some values are inherently approximate because they race with live replication, resync, verification, and state changes; the code explicitly clamps impossible progress values when state changes race with `rs_total` resets.

The progress calculations use bitmap units (`BM_BLOCK_SIZE`) and convert to kB or MB for display. Rolling speed estimates are based on `rs_mark_left`, `rs_mark_time`, `rs_last_mark`, `rs_start`, and `rs_paused`. Stalled detection is based on an older sync mark exceeding 180 seconds.

## Dependencies And Integration Points

The file integrates with procfs and `seq_file`, DRBD global device idr state, RCU-protected network configuration, DRBD bitmap helpers, local-device reference helpers (`get_ldev_if_state`, `put_ldev`), activity-log/resync cache stats, DRBD state-string helpers, and global tunable `drbd_proc_details`. It is a compatibility/status interface for users and scripts that still consume `/proc/drbd`, complementing the generic-netlink status APIs in `drbd_nl.c`.

## Risks

- Output is a live, unlocked status snapshot. Multi-field consistency is best-effort; scripts must tolerate races and transient combinations.
- `first_peer_device(device)` is assumed valid in configured paths. Object lifetime and device initialization order must preserve that assumption.
- Progress arithmetic intentionally avoids overflow on 32-bit systems. Changes to bitmap sizing, sync mark units, or per-mille math need careful type review.
- The legacy text format is likely consumed by external tools. Cosmetic changes can be compatibility regressions.
- `drbd_proc_details` increases detail and can expose lower-level internal counters; changes should consider output volume and locking.

## Test Signals

Tests should read `/proc/drbd` across unconfigured, standalone, connected, primary/secondary, diskless, syncing, verifying, and paused-sync states. Golden-output checks should cover the version header, minor gaps, protocol letters, suspension flags, write-ordering characters, counter scaling, and out-of-sync units. Resync/verify tests should validate progress bounds, stalled marker behavior, desired sync rate display, and optional detail output at `drbd_proc_details` levels 1 and 2.
