# sources/distributed-fs/ceph-client/include/media/cadence/cdns-csi2rx.h

Purpose: Declares a tiny V4L2 subdevice helper for Cadence CSI-2 receiver pixel-per-clock negotiation.

Important APIs/types/functions: `cdns_csi2rx_negotiate_ppc(struct v4l2_subdev *subdev, unsigned int pad, u8 *ppc)` negotiates the requested pixels-per-clock value for a source pad and returns zero or a negative errno.

Control flow: The caller supplies a subdevice, output pad, and mutable requested PPC. The implementation is expected to validate hardware/pad support and update `*ppc` with an accepted value.

State and persistence: No state is defined in the header. State lives in the V4L2 subdevice driver.

Dependencies and integration: Depends on `<media/v4l2-subdev.h>` and integrates Cadence CSI-2 RX bridge drivers with downstream media pipeline format negotiation.

Risks and test signals: Risks are invalid pad numbers, unsupported PPC values, and callers not handling modified requests. Test with all source pads, boundary PPC values, and media graph format negotiation paths.
