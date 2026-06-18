# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic-common.c

## Purpose
This file is the common registration wrapper for i.MX Image Converter subdevices. It maps media group IDs to task-specific IC operation tables, initializes the common `imx_ic_priv`, registers the V4L2 subdevice, and unregisters/cleans up task-specific resources.

## Important APIs and Functions
`imx_media_ic_register()` allocates `struct imx_ic_priv`, stores the IPU device and IPU pointer, maps group IDs to `IC_TASK_PRP`, `IC_TASK_ENCODER`, or `IC_TASK_VIEWFINDER`, initializes `priv->sd` with the selected `imx_ic_ops`, configures entity ops/function/owner/flags/group/name, invokes the task-specific `init()`, and registers the subdevice with the supplied `v4l2_device`.

`imx_media_ic_unregister()` looks up `imx_ic_priv`, calls the task-specific `remove()`, unregisters the subdevice, and cleans up the media entity.

## Control Flow and State
The wrapper has a simple dispatch table: PRP uses `imx_ic_prp_ops`, while encoder and viewfinder use `imx_ic_prpencvf_ops`. Task-specific private state is stored through `priv->task_priv` during the init callback. Registration names are derived from group ID and IPU number.

## Dependencies and Integration Points
It depends on V4L2 device/subdev APIs, media entity APIs, IPU numbering, `imx-media.h` group IDs/name helpers, and task ops from `imx-ic-prp.c` and `imx-ic-prpencvf.c`. It is called by i.MX media device setup code when instantiating internal IPU IC subdevices.

## Risks and Test Signals
Risks include invalid group IDs returning `-EINVAL`, init failures leaking partially initialized subdev fields, and unregister assuming valid task ID and initialized task private state. Test signals include media graph creation for PRP, PRPENC, and PRPVF, failure injection in task init/register, and clean unregister with media entity cleanup.
