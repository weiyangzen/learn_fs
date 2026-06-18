## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.h

### Purpose
`pvrusb2-wm8775.h` declares the internal wm8775 audio subdevice update hook for pvrusb2.

### Important APIs, Types, And Functions
It includes `pvrusb2-hdw-internal.h` and declares `pvr2_wm8775_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *sd)`.

### Control Flow
The header has no runtime control flow. It exposes the update function to the hardware/subdevice synchronization code.

### State, Persistence, And Dependencies
No state is stored here. The dependency on internal pvrusb2 hardware structures keeps this interface private to the driver.

### Integration Points
The declaration links board audio routing updates to the wm8775-specific implementation.

### Risks
As with the implementation, the API is narrowly tailored to one audio subdevice and assumes callers already know when input state is dirty.

### Test Signals
Build coverage should include the subdevice update path, and runtime testing should verify radio/non-radio audio route changes.
