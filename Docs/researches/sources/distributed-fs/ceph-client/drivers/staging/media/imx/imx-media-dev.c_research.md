# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-dev.c

## Purpose

`imx-media-dev.c` is the platform driver for the i.MX5/6 media controller instance compatible with `fsl,imx-capture-subsystem`. It creates the top-level `imx_media_dev`, registers CSI async subdevices from device tree, adds IPU-internal subdevices when CSI devices bind, and creates the mem2mem CSC/scaler after media probe completion.

## Important APIs, Types, and Functions

The main callbacks are `imx_media_probe()`, `imx_media_remove()`, `imx_media_subdev_bound()`, and `imx6_media_probe_complete()`. The notifier ops install `.bound` and `.complete`. The platform driver matches `fsl,imx-capture-subsystem` and uses helpers from `imx-media-dev-common.c`, `imx-media-of.c`, `imx-media-internal-sd.c`, and `imx-media-csc-scaler.c`.

## Control Flow

Probe initializes the common media device, parses `ports` phandles to add CSI async matches, and registers the async notifier. Each bound CSI subdevice causes synchronous registration and linking of IPU-internal subdevices for that CSI's IPU. Completion first calls common probe completion, then creates and registers the IPU IC post-processor mem2mem device under the media mutex.

Remove unregisters the mem2mem scaler if present, unregisters and cleans up the async notifier, unregisters IPU-internal subdevices, unregisters the media and V4L2 devices, and cleans up the media device.

## State and Persistence Behavior

State lives in the devm-allocated `imx_media_dev` attached to the platform device. The file records `m2m_vdev` after successful scaler creation. No configuration is persisted across driver unload/reload.

## Dependencies and Integration Points

This is the integration root for the IMX media stack. It depends on platform device probing, OF matching, V4L2 async notifier callbacks, common media-device helpers, internal IPU subdevice registration, and the CSC/scaler video-device lifecycle.

## Risks and Edge Cases

Failure after common device initialization must clean notifier, V4L2, and media-device state. If mem2mem scaler registration fails during completion, the media graph may already have been registered by the common complete handler, making error handling important for probe behavior. Internal subdevice registration only triggers for subdevices with CSI group ids.

## Test Signals

Test probe with missing/disabled CSI ports, async bind of one and two CSIs, failure in internal-subdev registration, common completion failure, scaler init/register failure, and remove after partial or full probe.
