# File Research: sources/block-storage/linux-dm/drivers/md/dm-uevent.c

## Purpose
Provides device-mapper uevent support for path-related target events, currently path failure and path reinstatement. It packages DM-specific environment variables and queues events through the mapped device for later emission through the kobject uevent mechanism.

## Main Interfaces
- `dm_path_uevent()` builds and queues a path event for a target.
- `dm_send_uevents()` sends and frees all events on a supplied event list.
- `dm_uevent_init()` and `dm_uevent_exit()` create and destroy the event slab cache.
- Internal helpers include `dm_uevent_alloc()`, `dm_uevent_free()`, and `dm_build_path_uevent()`.

## Control Flow
`dm_path_uevent()` validates the event type, translates it to a kobject action and string name, builds the event with target name, DM action, sequence number, path, and valid-path count, then attaches the event to the mapped device via `dm_uevent_add()`. Later, `dm_send_uevents()` removes each event from the list, copies the current mapped-device name and UUID, appends them to the environment, calls `kobject_uevent_env()`, and frees the event.

## State And Synchronization
Events are allocated from the `_dm_event_cache` kmem cache using `GFP_ATOMIC`, making event creation usable from constrained contexts. Each `struct dm_uevent` stores a mapped-device pointer, kobject action, environment buffer, list node, and local name/UUID buffers.

## Integration Points
Used by DM targets that need to notify user space about path state changes, especially multipath-style target behavior. It relies on core DM helpers including `dm_next_uevent_seq()`, `dm_uevent_add()`, and `dm_copy_name_and_uuid()`, and exports `dm_send_uevents()` and `dm_path_uevent()` to GPL modules.

## Notable Behaviors
- Device name and UUID are copied at send time, not event-build time, so removal races can cause an unsent event to be skipped.
- Event payload includes `DM_TARGET`, `DM_ACTION`, `DM_SEQNUM`, `DM_PATH`, `DM_NR_VALID_PATHS`, `DM_NAME`, and `DM_UUID`.
- Invalid event type is logged and dropped.

## Risks And Review Focus
- Environment construction failure drops the event; new fields must account for limited `kobj_uevent_env` capacity.
- Mapped-device lifetime assumptions are shared with the DM core event queue; callers should only queue events through the supported DM path.
