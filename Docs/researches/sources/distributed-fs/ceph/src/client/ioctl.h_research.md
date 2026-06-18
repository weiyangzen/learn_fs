# sources/distributed-fs/ceph/src/client/ioctl.h

## Purpose
`ioctl.h` defines CephFS-specific ioctl ABI structures and command numbers shared by FUSE/client code and test utilities.

## Important APIs, Types, and Functions
It defines `CEPH_IOCTL_MAGIC`, `ceph_ioctl_layout`, layout commands `CEPH_IOC_GET_LAYOUT`, `CEPH_IOC_SET_LAYOUT`, `CEPH_IOC_SET_LAYOUT_POLICY`, `ceph_ioctl_dataloc`, `CEPH_IOC_GET_DATALOC`, and `CEPH_IOC_LAZYIO`.

## Control Flow
There is no executable control flow. FUSE ioctl handling decodes these command numbers and fills or consumes these structures.

## State and Persistence Behavior
`SET_LAYOUT` and `SET_LAYOUT_POLICY` can persist file or directory layout policy in CephFS metadata. `GET_DATALOC` reports mapping information for a file offset.

## Dependencies and Integration Points
It depends on platform ioctl headers and Ceph integer types. `fuse_ll.cc` supports `CEPH_IOC_GET_LAYOUT`; `test_ioctls.c` exercises layout and dataloc commands.

## Risks
This is a stable ABI surface: struct size, alignment, and command numbering must not drift. `sockaddr_storage` in `ceph_ioctl_dataloc` requires compatible includes and caller buffer sizing.

## Test Signals
Tests should compile on Linux and BSD/macOS guarded paths, and runtime ioctl tests should verify layout round-trips and dataloc fields.
