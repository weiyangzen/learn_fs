## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-video-v4l.h

### Purpose
`pvrusb2-video-v4l.h` declares the internal saa7115 subdevice update hook used by the pvrusb2 hardware layer.

### Important APIs, Types, And Functions
It includes `pvrusb2-hdw-internal.h` and declares `pvr2_saa7115_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

### Control Flow
The header has no runtime flow. It makes the implementation available to code that iterates or updates pvrusb2 I2C subdevices.

### State, Persistence, And Dependencies
There is no stored state. The dependency on the internal hardware header indicates this is not a public V4L2 API; it expects full access to pvrusb2 hardware internals.

### Integration Points
The declaration integrates the pvrusb2 video decoder adapter with lower-level subdevice synchronization code.

### Risks
Including an internal hardware header widens compile-time coupling. Changes to `struct pvr2_hdw` or V4L2 subdevice declarations may require coordinated edits.

### Test Signals
Build tests should cover configurations that compile saa7115 routing support. Runtime signals are input switching and routing verification in `pvrusb2-video-v4l.c`.
