<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uconn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uconn.c

## Purpose

`uconn.c` exposes display connectors as NVIF user objects and translates kernel HPD/AUX/GSP events into NVIF connector events.

## Important APIs, Types, And Functions

`nvkm_uconn_uevent_gsp()`, `_aux()`, and `_gpio()` convert source-specific event bits to `NVIF_CONN_EVENT_V0_*` bits. `nvkm_uconn_uevent()` validates event arguments, finds an output on the connector, chooses GSP display events, DP AUX/I2C events, or GPIO HPD events, and registers the uevent. `nvkm_connector_is_dp_dms()` handles a DP DMS IRQ exception. `nvkm_uconn_new()` validates the connector id, maps DCB connector types to NVIF connector types, installs the object under `disp->client.lock`, and rejects duplicate opens.

## Control Flow

Userspace opens a connector object through `udisp.c`. `nvkm_uconn_new()` locates the connector by id and returns its type. Event registration later calls `nvkm_uconn_uevent()`, which selects the proper event backend depending on GSP, DP AUX presence, output location, and HPD GPIO. Destruction clears `conn->object.func` under the display client lock.

## State And Persistence Behavior

The connector object is embedded in `struct nvkm_conn`. Its `object.func` is non-NULL only while opened by a client. Event subscriptions are managed through `nvkm_uevent` and the underlying display/I2C/GPIO event sources.

## Dependencies And Integration Points

It depends on connector/output lists, GSP display resource manager events, I2C/AUX event sources, GPIO HPD events, DCB connector type constants, and NVIF connector ABI structures.

## Risks And Edge Cases

Only one user object can wrap a connector at a time. Some connector types are unimplemented and are reported as VGA while returning `-EINVAL`. DP IRQ over GPIO is rejected except for external/DMS cases. If no output path is found for a connector, event setup fails with `-EINVAL`.

## Test Signals

Test connector open/close, reported connector type, plug/unplug/IRQ delivery over GSP, AUX, and GPIO paths, duplicate open returning `-EBUSY`, and unsupported connector warnings for unusual DCB entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uconn.c -->
