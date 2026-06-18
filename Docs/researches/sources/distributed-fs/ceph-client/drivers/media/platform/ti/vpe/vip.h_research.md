# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.h

Purpose: private header for the TI VIP capture driver. It defines the VIP data model, constants, resource ownership fields, stream queues, media-bus format mapping, and parser/scaler/CSC/VPDMA integration state used by `vip.c`.

Important APIs/types: `enum vip_csc_state` describes CSC availability/direction. `struct vip_buffer` wraps `vb2_v4l2_buffer` with driver queue/drop state. `struct vip_fmt` maps V4L2 pixel formats to media-bus codes and VPDMA per-plane formats. `struct vip_shared` owns common VPDMA and V4L2 state shared by slices. `struct vip_dev` represents one VIP slice with parser/scaler/CSC resources and IRQ. `struct vip_port` represents port A/B, endpoint, crop, active formats, shadow MMR/coeff buffers, and scaler/CSC allocation. `struct vip_stream` owns one video node, VPDMA list number, vb2 queue, buffer queues, descriptor list, and recovery state.

Control flow: `vip.c` includes this header before building all probe, format, streaming, and interrupt paths. Probe allocates `vip_shared`, two `vip_dev` instances, then ports and streams. Open/close use the port and stream counters to power resources up/down. Streaming updates the fields declared here and passes embedded VPDMA buffers to the helper library.

State and persistence: this header documents all long-lived driver state. The key persistent handles are MMIO bases, `struct vpdma_data`, `struct v4l2_device`, async notifiers, endpoint metadata, per-port allocated coefficient/MMR buffers, per-stream VPDMA channel bitmaps, and queues. No on-disk persistence exists.

Dependencies and integration: includes Linux video/V4L2/vb2/fwnode/async headers plus `vpdma.h`, `vpdma_priv.h`, `sc.h`, and `csc.h`. The constants tie VIP slices, ports, VPDMA channels, and CFD client IDs together.

Risks: it exposes internal layout tightly coupled to descriptor ordering and hardware channel numbering. `VIP_MAX_ACTIVE_FMT` must stay synchronized with `vip_formats[]`. The header includes `vpdma_priv.h`, so VIP code depends on private descriptor/register details, not only the public VPDMA API. Resource assignment fields (`sc_assigned`, `csc_assigned`) are integer port IDs with no separate locking beyond the device mutex expectations.

Test signals: compile coverage for `CONFIG_VIDEO_TI_VIP`; format enumeration count matching `VIP_MAX_ACTIVE_FMT`; two-slice/two-port probe; scaler and CSC allocation/free across repeated open/S_FMT/close; and async notifier cleanup on remove.
