# File Research: sources/block-storage/mdadm/monitor.c

## Role

`monitor.c` is the mdmon monitor-thread implementation. It watches sysfs state files for external metadata arrays, updates metadata through the active `superswitch`, handles dirty/clean transitions, records device failures and bad blocks, checkpoints reshape/sync progress, and signals the manager thread when higher-level actions are needed.

## Core Helpers

- `add_fd()` validates sysfs fds and adds them to a select fd set.
- `read_attr()`, `read_resync_start()`, `read_sync_completed()`, `read_state()`, and `read_action()` read sysfs fields.
- `read_dev_state()` maps member state words into mdadm `DS_*` flags.
- `signal_manager()` sends `SIGUSR1` to the manager thread.

## Bad-Block Handling

- `process_ubb()` records an unacknowledged bad block in external metadata, then acknowledges it to the kernel by writing back to the sysfs bad-block descriptor.
- `compare_bb()` compares kernel bad-block entries to metadata entries, recording missing entries or clearing stale metadata entries.
- `read_bb_file()` parses kernel bad-block lines of `sector length\n`.
- `process_dev_ubb()` handles unacknowledged bad blocks.
- `check_for_cleared_bb()` clears metadata bad blocks no longer present in the kernel acknowledged list.

## read_and_act()

`read_and_act()` is the monitor state machine for one active array:

- Reads current array state/action, resync start, sync completion, and per-device state/recovery.
- Marks metadata dirty on `write-pending`, `active`, or `suspended`.
- Handles `active-idle` by moving array to clean before marking metadata clean.
- Moves `readonly` arrays to `read-auto` or `active` unless metadata version begins with `external:-`.
- Detects array stop/deactivation and marks metadata clean.
- Detects resync/recovery completion and updates metadata/device state.
- Detects reshape start and requests manager reshape checks.
- Records failed devices, unblocks blocked faulty devices, requests removal when writable, and propagates degraded checks.
- Updates reshape/sync checkpoints based on `sync_completed` and `reshape_position`.
- Calls `sync_metadata()` and writes pending sysfs state/action/member changes.
- Signals the manager when degraded checks, reshape checks, or member removals are pending.

## Main Monitor Loop

`wait_and_act()`:

- Builds select sets from array state/action/sync fds and each member’s state/bad-block fds.
- Removes deactivated arrays by handing them to `discard_this` for the manager.
- Exits when no arrays remain or `SIGTERM` arrives and arrays are clean, after checking exclusive access to the container.
- Waits with `pselect()` while unblocking `SIGUSR1`.
- Processes queued metadata updates from the manager with `process_update()`.
- Calls `read_and_act()` for each active array.
- Propagates a failed physical device across other container members with `reconcile_failed()`.

`do_monitor()` repeatedly calls `wait_and_act()`, forcing an initial immediate pass.

## Invariants and Risks

- Metadata is synchronized at most once per wakeup after relevant state changes.
- Monitor must not close member descriptors while the manager is removing a disk; it marks `mon_descriptors_not_used`.
- Failure propagation is across arrays sharing the same external container and physical major/minor.
- SIGTERM exits only after dirty arrays are clean, preserving external metadata consistency.
