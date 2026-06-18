# File Research: sources/block-storage/mdadm/mdmon.h

## Role

`mdmon.h` is the shared internal header for the mdmon manager and monitor implementation.

## Key Types

- `enum array_state` maps md sysfs `array_state` words used by mdmon.
- `enum sync_action` maps md sysfs `sync_action` words.
- `struct active_array` tracks one active subarray/member array in a container: generic `mdinfo`, owning container, replacement/discard links, sysfs fds, checkpoint state, previous/current/next array and sync states, and manager notification flags.
- Declares global metadata update queues: `update_queue` and `update_queue_handled`.

## Declared Interfaces

The header declares `do_monitor()`, `do_manager()`, `remove_pidfile()`, `read_dev_state()`, mdstat helpers, process/thread globals, termination flags, and monitor loop counters.

## Important Inline

`is_resync_complete()` computes completion for RAID1/4/5/6 and RAID10 by comparing `resync_start` with the relevant component/sync size. It handles RAID10 copy geometry from layout bits.

## Invariants

- Monitor and manager share address space and coordinate through globals and `SIGUSR1`.
- `struct active_array` stores open sysfs descriptors because mdmon reacts to sysfs poll/select events rather than repeatedly reopening attributes.
- Completion math only handles levels known to mdmon; unsupported levels leave `sync_size` zero.
