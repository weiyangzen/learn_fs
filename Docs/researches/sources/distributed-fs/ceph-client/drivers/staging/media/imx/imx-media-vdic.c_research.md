# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-vdic.c

## Purpose

`imx-media-vdic.c` implements the IPUv3 VDIC deinterlacer as a V4L2 subdevice. It supports a direct CSI-to-VDIC path for high-motion mode and an indirect memory-to-VDIC path using three IDMAC input channels for previous/current/next fields.

## Important APIs, Types, and Functions

`struct vdic_priv` stores the subdevice, pads, IPU/VDI resources, three IDMAC channels, active input pad, pipeline ops, field buffer bookkeeping, source/sink entities, pad formats, frame intervals, optional IDMAC input capture video device, motion control, and stream count. Public functions are `imx_media_vdic_register()` and `imx_media_vdic_unregister()`.

Important internals include `vdic_get_ipu_resources()`, `setup_vdi_channel()`, `vdic_setup_direct()`, `vdic_setup_indirect()`, `vdic_start()`, `vdic_stop()`, `vdic_s_stream()`, `vdic_set_fmt()`, `vdic_link_setup()`, `vdic_link_validate()`, and frame interval get/set callbacks.

## Control Flow

Registration creates a three-pad subdevice: direct sink, IDMAC sink, and direct source. Registered initialization assigns default formats and frame intervals and creates the deinterlacing-mode menu control. Link setup enforces a single source and sink. The direct sink must connect from a CSI direct source pad; the IDMAC sink must connect from a video device; the source must connect to a downstream subdevice.

On stream-on, the driver chooses direct or indirect ops from link state, obtains VDI and any required IDMAC channels, configures VDI for UYVY 4:2:2 processing at the active input dimensions, sets field order and motion mode, runs path-specific setup, enables VDI, starts channels, and optionally starts upstream CSI for direct mode.

## State and Persistence Behavior

State is runtime-only and protected by `lock`. Active pad formats and intervals persist while the subdevice is registered. Hardware resources are acquired during streaming and released on streamoff. Motion mode cannot change while streaming.

## Dependencies and Integration Points

VDIC is synchronously registered by `imx-media-internal-sd.c`. It integrates with CSI direct links, IC downstream links, V4L2 controls, media pad validation, IPUv3 VDI, FSU links, CPMEM, and IDMAC. It reuses format/colorimetry helpers from `imx-media-utils.c`.

## Risks and Edge Cases

Direct CSI mode is validated to require `HIGH_MOTION`; low and medium motion need three fields and are unsupported without memory input. Indirect path buffer fields are partly scaffolded in this file, but no vb2 queue handling is visible here, so consumers must ensure the IDMAC input path supplies buffers through the broader graph. Width is limited to 968 and aligned to 16 pixels. Output is always progressive.

## Test Signals

Test direct CSI link validation for high versus low/medium motion, indirect IDMAC-link validation, interlaced input field enforcement, progressive source output, frame interval doubling in direct mode, motion-control busy rejection, resource acquisition failure cleanup, and stream count behavior across repeated stream-on/off calls.
