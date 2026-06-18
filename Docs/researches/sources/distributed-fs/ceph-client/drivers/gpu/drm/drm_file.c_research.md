# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_file.c

## Purpose
`drm_file.c` implements DRM character-device file lifecycle and common file operations. It allocates per-open `drm_file` contexts, wires driver open/postclose callbacks, manages event delivery to userspace, releases per-file DRM resources, prints fdinfo memory stats, and provides a test-only internal file constructor.

## Important APIs, Types, And Functions
Key exported APIs are `drm_open()`, `drm_release()`, `drm_release_noglobal()`, `drm_read()`, `drm_poll()`, `drm_file_alloc()`, `drm_file_free()`, `drm_file_update_pid()`, `drm_event_reserve_init()`, `drm_event_reserve_init_locked()`, `drm_event_cancel_free()`, `drm_send_event()`, `drm_send_event_locked()`, `drm_send_event_timestamp_locked()`, `drm_show_fdinfo()`, `drm_show_memory_stats()`, `drm_print_memory_stats()`, and `drm_file_err()`. Important state includes `struct drm_file`, event lists, GEM handle tables, PRIME file private data, syncobj state, DRM master state, and client identity fields.

## Control Flow
Open acquires a DRM minor, optionally takes `drm_global_mutex` for legacy load/unload drivers, increments open count, shares the device address space, allocates a `drm_file`, initializes GEM/syncobj/PRIME/debugfs/client state, runs driver open, initializes master state for primary clients, and links the file into `dev->filelist`. Release unlinks the file, frees events and mode objects, releases GEM/syncobj/PRIME/master resources, calls driver postclose, drops open count, and restores in-kernel clients on last close. `drm_read()` serializes event reads, waits like a pipe, copies only whole events, and puts events back if the userspace buffer is too small or copy fails.

## State, Persistence, And Dependencies
Per-file state persists from open to release: framebuffer ownership list, event space quota, pending and delivered events, waitqueue, locks, client id/name, pid, PRIME data, GEM handles, syncobjs, and master data. The file depends on DRM minor/device lifetime, debugfs clients, GEM and syncobj subsystems, DMA fences, poll/read waitqueues, PCI fdinfo, RCU pid handling, and optional legacy global locking.

## Integration Points
Drivers normally use these functions in their `file_operations` table. KMS page flips, vblank waits, and driver-private asynchronous completions reserve and send events through this file. `/proc/<pid>/fdinfo` uses `drm_show_fdinfo()` and optional driver `show_fdinfo` hooks. Tests and in-kernel clients can use `mock_drm_getfile()` to construct an anonymous DRM file around a minor.

## Risks
Event accounting is subtle: reservation subtracts from `event_space`, close must unlink pending events without racing senders, reads must restore accounting if an event cannot be copied, and fences/completions must be signaled exactly once. Open and release ordering must unwind driver callbacks, debugfs, GEM, syncobj, PRIME, master, and minor references correctly. `drm_file_update_pid()` must preserve master ownership semantics and use RCU safely.

## Test Signals
High-value tests include open failure unwinding after driver open failure, primary versus render-node clients, lastclose restore, event reserve/cancel/send/read with small buffers and nonblocking reads, close with pending events, fence timestamp signaling, fdinfo memory accounting for shared/private/resident/active/purgeable GEM objects, and pid update after file handoff.
