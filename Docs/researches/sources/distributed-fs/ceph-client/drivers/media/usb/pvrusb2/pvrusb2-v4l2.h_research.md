## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-v4l2.h

### Purpose
`pvrusb2-v4l2.h` declares the internal V4L2 bridge constructor for the pvrusb2 driver.

### Important APIs, Types, And Functions
The header forward declares `struct pvr2_v4l2` and exposes `pvr2_v4l2_create(struct pvr2_context *)`. It includes `pvrusb2-context.h` because the constructor is tied to an existing pvrusb2 context.

### Control Flow
There is no runtime control flow in the header. Callers create a V4L2 bridge after a pvrusb2 context and hardware object are ready; ownership is then managed through pvrusb2 channel callbacks and V4L2 device release paths.

### State, Persistence, And Dependencies
No state is stored here. The header is the compile-time contract between context setup code and `pvrusb2-v4l2.c`.

### Integration Points
The constructor hooks higher-level pvrusb2 context code to V4L2 node registration without exposing bridge internals.

### Risks
Because only a constructor is exported, callers cannot explicitly destroy the object; lifetime must remain consistent with channel cleanup and disconnect callbacks in the implementation.

### Test Signals
Build coverage should ensure all users include this header rather than duplicating the opaque type. Runtime tests are covered through V4L2 node registration and disconnect handling.
