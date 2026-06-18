<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.h

### Purpose
`ivpu_sysfs.h` declares the device sysfs registration entry point for ivpu.

### Important APIs, Types, And Functions
The only exported API is `ivpu_sysfs_init(struct ivpu_device *vdev)`.

### Control Flow
There is no executable flow in the header.

### State, Persistence, And Dependencies
It includes `ivpu_drv.h` for `struct ivpu_device`. Registered sysfs attributes persist for the managed lifetime of the device because the implementation uses devm registration.

### Integration Points
The PCI/DRM device setup path calls this after `ivpu_device` exists and before userspace monitoring reads attributes.

### Risks
The header is small, but including `ivpu_drv.h` makes it a broad dependency. Prototype changes affect device initialization.

### Test Signals
Successful build and sysfs attribute presence under the ivpu device are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.h -->
