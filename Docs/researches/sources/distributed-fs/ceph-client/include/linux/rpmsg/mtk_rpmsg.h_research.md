# sources/distributed-fs/ceph-client/include/linux/rpmsg/mtk_rpmsg.h

## Purpose
`mtk_rpmsg.h` exposes MediaTek rpmsg helper APIs for creating a remoteproc subdevice backed by MediaTek IPI operations.

## Important APIs, types, and functions
The header defines `ipi_handler_t` and `struct mtk_rpmsg_info`, whose callbacks are `register_ipi()`, `unregister_ipi()`, and `send_ipi()`, plus `ns_ipi_id` for name-service support. Public APIs are `mtk_rpmsg_create_rproc_subdev()` and `mtk_rpmsg_destroy_rproc_subdev()`.

## Control flow, state, and persistence
MediaTek platform code supplies IPI callbacks, creates an `rproc_subdev`, and remoteproc start/stop paths use that subdevice to register IPI handlers, send rpmsg payloads by IPI ID, and optionally process name-service announcements. State lives in the remoteproc subdevice, platform device, and transport implementation, not in the header.

## Dependencies and integration points
It depends on `platform_device.h` and `remoteproc.h`. It integrates the rpmsg core with MediaTek SCP/remoteproc IPI transports and service discovery through a configured name-service IPI.

## Risks and test signals
Risks include IPI ID collisions, registering handlers before firmware is ready, failing to unregister handlers on remoteproc stop, send timeout misuse, and missing name-service support when `ns_ipi_id` is `-1`. Test signals include MediaTek remoteproc boot/stop, IPI registration/unregistration, send timeout paths, rpmsg channel discovery, remote crash recovery, and subdevice destroy cleanup.
