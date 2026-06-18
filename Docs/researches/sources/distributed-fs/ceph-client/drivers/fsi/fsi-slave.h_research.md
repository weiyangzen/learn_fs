# sources/distributed-fs/ceph-client/drivers/fsi/fsi-slave.h

## Purpose
`fsi-slave.h` is a private FSI core header that defines the in-kernel representation of an FSI slave device. It is used by FSI client and master-adjacent code that needs to reach from `struct device` or an FSI device to slave addressing and parent-master details.

## Important APIs, Types, and Functions
The file defines `struct fsi_slave` with embedded `struct device dev`, parent `struct fsi_master *master`, character-device state, FSI address and link identifiers, `cfam_id`, `chip_id`, address-space `size`, and timing fields `t_send_delay` and `t_echo_delay`. The only helper is `to_fsi_slave(d)`, a `container_of()` conversion from the embedded device.

## Control Flow
There is no runtime control flow in this header. It defines shared layout consumed by FSI core and client drivers. In this work item, `i2cr-scom.c` uses `fsi_dev->slave->master` to confirm that the SCOM client is attached under an I2CR FSI master.

## State and Persistence
The structure is runtime kernel state. It is not persisted and does not define locking; users rely on the FSI core's object lifetime rules.

## Dependencies and Integration Points
The header depends on Linux `device` and `cdev` types and forward-declares `struct fsi_master`. It is intentionally local to `drivers/fsi`, not a UAPI contract.

## Risks and Test Signals
Because users dereference `slave->master`, lifetime and initialization ordering are important. Any future layout changes must be coordinated with all FSI client drivers. Test signals are compile coverage of FSI clients, hotplug/remove paths that free slaves, and lockdep or KASAN findings around master/slave lifetime.
