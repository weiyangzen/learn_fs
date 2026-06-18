<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_proto.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_proto.h

Purpose: Defines DisplayLink bulk message command codes and register numbers used by UDL modeset and transfer code.

Important APIs/types/functions: Constants include `UDL_MSG_BULK`, register-write command, raw/RLE/copy framebuffer commands for 8/16 bpp, color-depth values, timing registers, blank modes, framebuffer base-address registers and masks, and video-register lock/unlock values.

Control flow: `udl_modeset.c` and `udl_transfer.c` compose command buffers using these constants before submitting URBs.

State and persistence: No state; hardware protocol definition only.

Dependencies and integration points: Uses Linux `GENMASK` via `linux/bits.h`.

Risks and test signals: Protocol mistakes cause display corruption or blanking. Test by tracing command streams for mode set, blank, base address, and encoded damage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_proto.h -->
