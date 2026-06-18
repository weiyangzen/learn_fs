<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/device.c

## Purpose
Implements R535 RM device/subdevice creation and RM event registration.

## Important APIs, Types, And Functions
Defines device constructor/destructor, subdevice constructor, event constructor/destructor, notification enable helper, and exports `r535_device`.

## Control Flow
Device construction allocates `NV01_DEVICE_0` under a client, then `NV20_SUBDEVICE_0` under the device. Event construction allocates `NV01_EVENT_KERNEL_CALLBACK_EX`, enables repeated notification via `NV2080_CTRL_CMD_EVENT_SET_NOTIFICATION`, then links the callback into the client's event list under the GSP client mutex. Destruction unlinks events and frees RM objects.

## State And Persistence
Persists RM device, subdevice, and event objects plus event callback list entries until explicit destructor calls.

## Dependencies And Integration Points
Used by display, FBSR, VMM, and internal GSP-RM setup. Depends on RM allocation/control APIs and client event lists.

## Risks And Edge Cases
Event callbacks must be unlinked before freeing objects. Partial construction must free parent objects on failure.

## Test Signals
Successful device/subdevice allocation, hotplug/IRQ event callbacks firing, and clean teardown without stale event callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/device.c -->
