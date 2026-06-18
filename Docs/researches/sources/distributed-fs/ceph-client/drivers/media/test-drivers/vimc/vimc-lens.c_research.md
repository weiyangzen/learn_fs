# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-lens.c

## Purpose
`vimc-lens.c` implements a minimal virtual lens subdevice for VIMC ancillary links. It exposes a focus control but does not process frames.

## Important APIs, Types, and Functions
`struct vimc_lens_device` embeds `vimc_ent_device`, `v4l2_subdev`, `v4l2_ctrl_handler`, and the last `focus_absolute` value. `vimc_lens_add()` allocates the device, creates `V4L2_CID_FOCUS_ABSOLUTE`, registers a `MEDIA_ENT_F_LENS` subdev with no pads, and returns the entity wrapper. `vimc_lens_s_ctrl()` stores focus values. `vimc_lens_release()` frees controls, subdev state, entity state, and memory. The export is `vimc_lens_type`.

## Control Flow
The core topology creates two lens entities and attaches them as ancillary links to sensors. User-space control writes call `vimc_lens_s_ctrl()`, which updates in-memory focus state. There is no stream callback and no media data path.

## State and Persistence
The only simulated hardware state is `focus_absolute`, per lens instance and volatile. It resets on device release.

## Dependencies and Integration Points
The file uses V4L2 controls/events/subdev APIs and VIMC common registration. It integrates with media-controller ancillary links from `vimc-core.c`, allowing user space to see a sensor-lens relationship.

## Risks and Edge Cases
The focus value has no effect on generated sensor frames, so it is suitable for topology/control testing rather than optical simulation. There are no pads, so any code assuming every entity has a pad must handle lens entities carefully.

## Test Signals
Tests should verify lens subdevices appear in media topology, ancillary links point to sensors, focus control range is 0 to 1023, and control events/log status work.
