# sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.h

## Purpose
Declares the Allwinner A31 `sun6i-isp-proc` V4L2 subdevice, which is the ISP processing node between CSI input, metadata parameter input, and capture output. The header is the shared contract between the proc implementation and the rest of the sun6i ISP driver.

## Important APIs, Types, And Functions
`enum sun6i_isp_proc_pad` fixes the media pad layout: CSI sink, params sink, and source. `struct sun6i_isp_proc_format` maps media-bus codes to hardware input format and YUV sequence values consumed by the register programming path. `struct sun6i_isp_proc_source` tracks an upstream subdevice, parsed fwnode endpoint, and whether it is expected. `struct sun6i_isp_proc_async_subdev` embeds a V4L2 async connection with backpointer to the source. `struct sun6i_isp_proc` owns the V4L2 subdev, pads, async notifier, active mbus format, a format mutex, and two CSI source slots. Exported helpers are `sun6i_isp_proc_dimensions()`, `sun6i_isp_proc_format_find()`, `sun6i_isp_proc_setup()`, and `sun6i_isp_proc_cleanup()`.

## Control Flow
Setup allocates/registers the processing subdevice and async notifier; graph binding fills the `source_csi0/source_csi1` structures; format negotiation updates `mbus_format` under `lock`; dimensions are later consumed by parameter and capture configuration. Cleanup must unregister notifier/subdev resources in reverse.

## State And Persistence
State is in-memory kernel driver state only. The persistent contract is the media graph topology and active mbus format exposed through V4L2 while the device is registered.

## Dependencies And Integration Points
Depends on V4L2 device/subdevice, media pads, V4L2 fwnode endpoint parsing, and the parent `struct sun6i_isp_device`. Integrates with capture, params, and main ISP register programming through format/dimension helpers.

## Risks And Test Signals
Risk centers on async graph binding and format propagation: wrong pad indices or stale `mbus_format` would misprogram hardware dimensions or input format bits. Test signals include media graph enumeration, async notifier bind/unbind, `VIDIOC_SUBDEV_G/S_FMT`, streaming through CSI plus params queue, and cleanup without use-after-free.
