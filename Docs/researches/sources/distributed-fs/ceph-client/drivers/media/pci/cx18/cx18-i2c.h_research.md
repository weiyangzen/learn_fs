# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-i2c.h

## Purpose
This header exposes cx18 I2C adapter lifecycle, subdevice registration, and subdevice lookup helpers.

## Important APIs, Types, and Functions
It declares `cx18_i2c_register()`, `cx18_find_hw()`, `init_cx18_i2c()`, and `exit_cx18_i2c()`.

## Control Flow
No runtime flow is in the header. Probe calls adapter initialization, card subdevice setup calls `cx18_i2c_register()`, and cleanup calls `exit_cx18_i2c()`.

## State and Persistence
I2C state resides in `struct cx18` adapters and V4L2 subdevice lists, not in the header.

## Dependencies and Integration Points
It is used by driver, card/subdevice, fileops, and ioctl code. `cx18_find_hw()` is the shared bridge from hardware flag masks to V4L2 subdev pointers.

## Risks and Edge Cases
Callers must ensure adapters are initialized before registering I2C subdevices. `cx18_find_hw()` returns the first exact `grp_id` match, so subdevices sharing a group would require care.

## Test Signals
Compile/link coverage plus successful I2C adapter registration and hardware subdev discovery in probe are the key signals.
