# sources/distributed-fs/ceph-client/drivers/md/dm-uevent.c

## Purpose
`dm-uevent.c` implements optional device-mapper uevent support for path-related target events. It builds environment payloads for failed/reinstated paths, queues them on a mapped device, and later sends them through the kernel kobject uevent mechanism.

## Important APIs, Types, And Functions
- `_dm_uevent_type_names[]` maps `DM_UEVENT_PATH_FAILED` and `DM_UEVENT_PATH_REINSTATED` to `KOBJ_CHANGE` and string actions.
- `struct dm_uevent` stores target mapped-device pointer, kobject action, uevent environment, list node, and copied DM name/UUID buffers.
- `dm_uevent_init()` creates a slab cache for events; `dm_uevent_exit()` destroys it.
- `dm_path_uevent()` validates event type, builds a path uevent, and queues it with `dm_uevent_add()`.
- `dm_send_uevents()` drains a list, appends current `DM_NAME` and `DM_UUID`, sends via `kobject_uevent_env()`, and frees each event.

## Control Flow
Targets call `dm_path_uevent()` with target pointer, path string, and valid path count. The code obtains the mapped device from the target table, allocates an event with `GFP_ATOMIC`, populates `DM_TARGET`, `DM_ACTION`, `DM_SEQNUM`, `DM_PATH`, and `DM_NR_VALID_PATHS`, then queues the list node on the mapped device. Later, mapped-device uevent dispatch calls `dm_send_uevents()`, which removes each event from the list, copies device name/UUID while the device still exists, appends those fields, invokes `kobject_uevent_env()`, logs send failures, and frees the slab object.

## State And Persistence Behavior
There is no persistent state. Runtime state is the slab cache and queued `struct dm_uevent` objects. Sequence numbers come from `dm_next_uevent_seq(md)`. Events are best-effort: if the mapped device name/UUID can no longer be copied during removal, the event is skipped and freed.

## Dependencies And Integration Points
The file depends on DM core helpers from `dm.h`, `dm-uevent.h`, `dm_table_get_md()`, `dm_uevent_add()`, `dm_copy_name_and_uuid()`, and `dm_next_uevent_seq()`. It uses kernel kobject uevents, slab cache allocation, and exported GPL symbols so targets such as multipath can report path state changes.

## Risks
- Allocation uses `GFP_ATOMIC`; pressure can drop events.
- Environment addition failure collapses to `-ENOMEM` and drops the event.
- Only path failed/reinstated events are supported by the local enum mapping.
- Events are skipped if the device is disappearing before dispatch.

## Test Signals
Test init/exit cache lifecycle, invalid event type rejection, allocation failure path, each `add_uevent_var()` failure path, queued event list draining, name/UUID copy failure during device removal, `DM_SEQNUM` monotonicity, and generated environment variables for both path event types.
