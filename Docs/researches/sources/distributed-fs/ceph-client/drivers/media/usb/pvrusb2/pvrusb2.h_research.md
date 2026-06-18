## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2.h

### Purpose
`pvrusb2.h` provides a small shared pvrusb2 driver constant for instance tracking.

### Important APIs, Types, And Functions
The only exported definition is `PVR_NUM`, set to `20`, the maximum number of pvrusb2 instances that receive small numeric unit IDs for array-valued module parameters.

### Control Flow
There is no control flow. Other pvrusb2 files use `PVR_NUM` to size arrays such as requested video, radio, and VBI minor numbers.

### State, Persistence, And Dependencies
No state is stored in the header. The value influences module-parameter arrays and whether extra connected devices can be addressed by per-unit options.

### Integration Points
`pvrusb2-v4l2.c` uses `PVR_NUM` for `video_nr`, `radio_nr`, and `vbi_nr`. Hardware instance numbering uses the bound as a limit when mapping unit number to preferred minor.

### Risks
If more than 20 devices are connected, driver operation continues but extra devices do not get unit-specific module parameter control. Raising the value changes static module parameter array sizes.

### Test Signals
Build-time coverage is enough for the header. Runtime testing would connect more than one device and verify per-unit module parameters map only within the allowed range.
