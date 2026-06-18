# File Research: sources/block-storage/mdadm/managemon.c

## Role

`managemon.c` implements the mdmon management thread for containers using external metadata. It handles blocking and allocation-heavy work that the monitor thread should avoid: discovering new member arrays, reacting to container disk changes, assigning spares to degraded arrays, replacing active-array snapshots, and receiving metadata update messages from external mdadm processes.

## Major Responsibilities

- Maintains `struct active_array` instances for arrays within an external-metadata container.
- Watches `/proc/mdstat` state through `manage()` and compares it with mdmon’s in-memory container/array model.
- Adds newly appeared container disks into metadata with `add_disk_to_container()`.
- Removes missing container disks from metadata with `remove_disk_from_container()`.
- Opens sysfs attributes needed by monitor-side polling through `sysfs_open2()` and `disk_init_and_add()`.
- Handles member-array lifecycle: new array discovery, degraded-array spare activation, reshape device discovery, level changes, linear/raid0 removal from monitoring, and member disk removal.
- Queues metadata updates through `update_queue_pending`, `update_queue`, and `update_queue_handled`.
- Accepts mdmon socket messages in `read_sock()` and converts them into metadata updates or ping/control actions.
- Coordinates replacement of active-array structures with the monitor thread using `replace_array()`, `pending_discard`, `discard_this`, and SIGUSR1 wakeups.

## Control Flow

`do_manager()` is the long-running loop. When no metadata update is actively being consumed, it reads mdstat, calls `manage()`, accepts at most one socket client via `read_sock()`, frees mdstat, removes old replaced arrays, promotes pending metadata updates, marks the manager ready, wakes the monitor during shutdown, and waits on mdstat/socket or signal state.

`manage()` iterates mdstat entries. The container entry is sent to `manage_container()`, while container member arrays are matched by metadata version and either passed to `manage_member()` or discovered through `manage_new()`.

`manage_new()` builds an `active_array` from sysfs, opens per-device and per-array sysfs files, parses the external subarray instance, initializes safemode handling, captures reshape checkpoints for already-reshaping arrays, asks the metadata handler to open/manage the new instance, and replaces any victim placeholder in the container array list.

`manage_member()` refreshes runtime sysfs details, honors frozen/sync-active states, updates level changes, lowers safe-mode delay during SIGTERM shutdown, removes requested member disks after monitor descriptors are no longer in use, activates metadata-provided spares for degraded arrays, queues resulting metadata updates, waits for updates to drain, replaces the array snapshot, and starts recovery. It also handles reshape-triggered new device discovery and array-size restoration.

## Metadata Update Handling

Metadata updates are explicitly staged. `queue_metadata_update()` appends to `update_queue_pending`; `check_update_queue()` promotes pending updates only when the active queue is empty and wakes the monitor. `free_updates()` releases buffers and auxiliary space lists. `handle_message()` handles special message lengths for monitor ping, manager ping, or normal external metadata update preparation through the supertype handler’s `prepare_update()`.

## Dependencies

This file depends on mdadm/mdmon internals: `struct supertype`, metadata handler callbacks (`add_to_super`, `remove_from_super`, `write_init_super`, `open_new`, `activate_spare`, `prepare_update`), mdstat parsing, sysfs helpers, socket message helpers, signal state, and monitor-thread globals.

## Important Invariants

- The manager never mutates the monitor’s live active-array object in place for structural changes; it duplicates and replaces it.
- `duplicate_aa()` skips devices with invalid `state_fd`, so disk removal invalidates future clones.
- Monitor wakeups are sent with `tgkill(..., SIGUSR1)` to the monitor thread id.
- Degraded spare assignment is skipped while metadata updates are pending to avoid decisions based on stale metadata.
- Disk removal waits for monitor descriptors to be unused before writing `remove` through a newly opened sysfs descriptor, avoiding a kernel suspend deadlock noted in comments.
- Shutdown uses safe-mode delay reduction and monitor wakeups so external metadata can become clean quickly.

## Risks

The file has delicate cross-thread ownership. File descriptors may be shared with clones unless `container` is cleared, and replacement/discard sequencing relies on monitor cooperation. Several paths continue after partial sysfs open failures, so future changes need to preserve the “monitor only ready arrays” behavior enforced by `aa_ready()`.
