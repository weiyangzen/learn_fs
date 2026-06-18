# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-internal-sd.c

## Purpose

`imx-media-internal-sd.c` describes and registers the IPU-internal media topology behind each i.MX CSI. It creates synchronous VDIC and IC subdevices, records them per IPU, and creates static media links among CSI, VDIC, PRP, PRPENC, and PRPVF blocks.

## Important APIs, Types, and Functions

The file defines `struct internal_subdev`, `struct internal_pad`, and `struct internal_link` plus the `int_subdev[]` topology table. Exported functions are `imx_media_register_ipu_internal_subdevs()` and `imx_media_unregister_ipu_internal_subdevs()`. Internal helpers are `create_internal_link()` and `create_ipu_internal_links()`.

## Control Flow

When an async CSI binds, the parent calls `imx_media_register_ipu_internal_subdevs()`. The function derives the IPU from the CSI parent device, validates the IPU id, stores the `ipu_soc`, registers missing synchronous subdevices through their `sync_register` callbacks, then walks all internal source pads and creates media pad links to already-registered sinks. CSI entries themselves are not synchronously registered because they are the async-bound subdevices.

On registration failure it unwinds already-created synchronous subdevices for that IPU. Unregistration iterates both possible IPUs and all internal subdevice slots, calling each available `sync_unregister()`.

## State and Persistence Behavior

State is held in `imxmd->ipu[]` and `imxmd->sync_sd[2][NUM_IPU_SUBDEVS]`. The topology table is static. No persistent storage is used. Registration drops the media mutex around subdevice register/unregister callbacks to avoid lock inversion with V4L2 registration internals.

## Dependencies and Integration Points

This file integrates the common media device with `imx_media_vdic_register()`, `imx_media_ic_register()`, and their unregister counterparts. It depends on IPUv3 device data, media pad link creation, group ids from `media/imx.h`, and pad constants from `imx-media.h`.

## Risks and Edge Cases

The link table assumes pad indexes and group ids stay synchronized with the subdevice implementations. `imx_media_unregister_ipu_internal_subdevs()` does not clear `sync_sd` entries after unregistering, which is safe only if the surrounding device is being torn down and no re-registration occurs. Link creation skips existing links, making repeated CSI binds idempotent for links.

## Test Signals

Test single and dual IPU registration, repeated CSI binding on the same IPU, invalid IPU device/id errors, failures from VDIC or IC registration, link creation idempotence, unwind behavior, and remove-time unregister ordering.
