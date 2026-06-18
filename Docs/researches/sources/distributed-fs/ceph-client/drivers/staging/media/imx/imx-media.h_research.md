# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media.h

## Purpose

`imx-media.h` is the shared private header for the i.MX5/6 media stack. It defines pad indexes, internal subdevice indexes, common pixel-format and video-device structures, the top-level `imx_media_dev`, DMA buffer records, helper inlines, and cross-file function prototypes.

## Important APIs, Types, and Functions

Important enums define IPU internal subdevice slots (`IPU_CSI0`, `IPU_CSI1`, `IPU_VDIC`, `IPU_IC_PRP`, `IPU_IC_PRPENC`, `IPU_IC_PRPVF`) and pad indexes for CSI, VDIC, PRP, and PRPENC/VF. `struct imx_media_pixfmt` describes FourCC/media-bus-code mappings, bpp, bus cycles, colorspace, planar/bayer/IPU flags. `enum imx_pixfmt_sel` provides format selection masks.

`struct imx_media_video_dev` wraps a V4L2 video device, active pixel format, compose rectangle, pixel-format descriptor, and list node. `struct imx_media_dev` embeds `media_device`, `v4l2_device`, the shared media pipeline, mutex, video-device list, IPU handles, async notifier, mem2mem video device, and registered synchronous subdevices. The header prototypes utilities, device-common functions, FIM, internal subdevice registration, OF parsing, VDIC, IC, capture, and CSC/scaler entry points.

## Control Flow

The header does not execute control flow directly, but it encodes the contracts that make graph construction and streaming work across files. Pad indexes are consumed by media link creation and subdevice ops. `to_imx_media_vb()` converts vb2 buffers to the driver buffer wrapper. `to_pad_vdev_list()` accesses per-pad reachable video-device lists stored in a subdevice's `host_priv`.

## State and Persistence Behavior

The defined structures hold runtime state only. The header sets the default frame size and EOF timeout constants used by multiple drivers. No persistent storage or static mutable data is introduced here.

## Dependencies and Integration Points

It includes Linux platform-device, V4L2 controls/devices/fwnode/subdev headers, vb2 DMA-contig, and IPUv3 definitions. All IMX media implementation files depend on this header for shared structures, pad constants, and function declarations.

## Risks and Edge Cases

Changing enum order or pad constants can silently break internal link tables and subdevice ops. `to_pad_vdev_list()` depends on `sd->host_priv` being owned by imx-media common code. The header exposes many cross-file APIs without namespace isolation beyond `imx_media_*`, so lifecycle expectations must be kept consistent manually.

## Test Signals

Compile coverage is the main signal: all IMX media objects must agree on pad constants, struct fields, and prototypes. Runtime graph tests that exercise CSI, VDIC, IC, capture, FIM, and scaler together validate this header's shared contracts.
