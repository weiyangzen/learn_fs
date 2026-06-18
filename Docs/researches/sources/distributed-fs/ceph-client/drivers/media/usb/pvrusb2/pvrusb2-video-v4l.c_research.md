## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.c

### Purpose
`pvrusb2-video-v4l.c` connects pvrusb2 input state to the V4L2 saa7115 video decoder subdevice. It maps pvrusb2 logical inputs to saa7115 routing IDs for supported board routing schemes.

### Important APIs, Types, And Functions
The file defines `struct routing_scheme`, two static route arrays for Hauppauge and OnAir-style signal routing, and `pvr2_saa7115_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

### Control Flow
When `input_dirty` or `force_dirty` is set on the hardware object, the update function selects the route table from `hdw->hdw_desc->signal_routing_scheme`, validates the current input value against the table size, maps it to an saa7115 input constant, and calls `sd->ops->video->s_routing(sd, input, 0, 0)`.

### State, Persistence, And Dependencies
The file has only static routing tables. Runtime state is read from `struct pvr2_hdw`, especially `input_val`, dirty flags, and hardware descriptor fields. It depends on pvrusb2 internal hardware declarations, pvrusb2 tracing, V4L2 subdevice APIs, and `<media/i2c/saa7115.h>`.

### Integration Points
This function is called from the pvrusb2 hardware/subdevice update path when analog input selection changes. It is one link between V4L2 user-facing input ioctls and board-level I2C video decoder routing.

### Risks
Invalid routing scheme IDs or input values are logged and ignored, so a misdescribed board can leave the saa7115 on an old route. The implementation assumes `sd->ops->video->s_routing` exists for this subdevice.

### Test Signals
Tests should switch TV, radio, composite, and S-Video inputs on boards for both routing schemes and verify the saa7115 subdevice receives the expected route. Negative tests should cover unsupported route scheme IDs and out-of-range input values.
