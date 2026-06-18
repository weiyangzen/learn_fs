# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.c

## Purpose
Exposes IPC4 firmware exception telemetry through debugfs. It locates the telemetry debug slot, maps the exception payload in the mailbox BAR, and provides a read-only `exception` file for crash/debug collection.

## APIs, Types, and Functions
The public entry point is `sof_ipc4_create_exception_debugfs_node()`. Internal helpers are `sof_ipc4_query_exception_address()` and `sof_telemetry_entry_read()`, with `sof_telemetry_fops` backing the debugfs file.

## Control Flow, State, and Persistence
Node creation allocates a `snd_sof_dfsentry`, marks it as always-accessible IOMEM, records a size of one debug slot minus the leading separator word, links it into `sdev->dfsentry_list`, and creates `debugfs/exception`. Reads validate position and count, locate the telemetry slot via `sof_ipc4_find_debug_slot_offset_by_type()`, skip the first separator magic word, copy the slot contents from I/O memory into a temporary kernel buffer, copy the requested range to user space, and advance `ppos`.

## Dependencies and Integration
Depends on debugfs, SOF debug entry bookkeeping, BAR/mailbox mapping in `sdev->bar[sdev->mailbox_bar]`, IPC4 debug-slot constants, and the debug-slot search helper declared in `ipc4-priv.h`. The binary layout of the payload is defined by `ipc4-telemetry.h`.

## Risks and Test Signals
Risks include missing telemetry slot descriptors, invalid BAR mapping, stale exception data after reboot/crash recovery, and allocating a full slot-sized buffer for every read. Test signals are debugfs node creation, correct zero-length behavior past EOF, successful reads after firmware exception, `-EFAULT` when no telemetry slot exists, and binary dump parsing against the coredump header structures.
