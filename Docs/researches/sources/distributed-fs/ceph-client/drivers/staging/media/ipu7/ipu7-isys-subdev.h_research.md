# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-subdev.h

## Purpose
Declares the generic ISYS V4L2 subdevice wrapper and helper API shared by CSI2 and other IPU7 ISYS bridge subdevices.

## Important APIs, Types, and Constants
`struct ipu7_isys_subdev` embeds `struct v4l2_subdev`, links to the parent `ipu7_isys`, points to a zero-terminated supported-code array, owns media pads and an optional control handler, carries an optional control initializer, and records `source` as the SSI/CSI stream source. `to_ipu7_isys_subdev()` converts from a V4L2 subdev. Prototypes expose MIPI data-type conversion, bayer helpers, format/routing operations, active stream format retrieval, init, and cleanup.

## Control Flow and State
The header is a contract for concrete subdevices. Concrete users initialize `isys`, supported codes, optional control callbacks, and source IDs, then call `ipu7_isys_subdev_init()`. V4L2 active-state routing and formats drive later video setup and link validation.

## Dependencies and Integration Points
Includes media entity, V4L2 controls, and V4L2 subdev headers. CSI2 uses it directly, video code treats remote subdevices as `ipu7_isys_subdev`, and queue/video validation depends on its active-format helper.

## Risks and Test Signals
Because `supported_codes` is expected to be zero-terminated, missing a sentinel would overrun enumeration. `source` defaults to -1 and must be set before streaming. Test signals include correct devnode creation, mandatory sink pad flags, successful route initialization, clean control-handler cleanup, and correct source ID propagation into firmware stream setup.
