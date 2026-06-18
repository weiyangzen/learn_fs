# sources/distributed-fs/ceph-client/fs/ceph/ioctl.h

## Purpose
`ioctl.h` defines the CephFS user ABI for Ceph-specific ioctl commands. It documents and declares the layout and data-location structures used by `ioctl.c`, and assigns ioctl numbers under `CEPH_IOCTL_MAGIC`.

## Important APIs, types, and functions
The header defines `CEPH_IOCTL_MAGIC`, `struct ceph_ioctl_layout`, `struct ceph_ioctl_dataloc`, and command macros `CEPH_IOC_GET_LAYOUT`, `CEPH_IOC_SET_LAYOUT`, `CEPH_IOC_SET_LAYOUT_POLICY`, `CEPH_IOC_GET_DATALOC`, `CEPH_IOC_LAZYIO`, and `CEPH_IOC_SYNCIO`.

`struct ceph_ioctl_layout` uses 64-bit fields for stripe unit, stripe count, object size, data pool, and obsolete preferred OSD. `struct ceph_ioctl_dataloc` carries an in/out file offset plus object offset/number/size/name, stripe-block offset/size, primary OSD id, and OSD socket address.

## Control flow
There is no executable control flow. The macros encode direction and type information for VFS ioctl dispatch. Userspace fills the input fields and `ioctl.c` copies, validates, and completes the output fields.

## State and persistence behavior
The header has no state. It defines the ABI through which userspace can read or request persistent CephFS layout metadata, query volatile cluster placement, or change per-open I/O mode flags.

## Dependencies and integration points
It depends on Linux ioctl/type headers and is included by the CephFS ioctl implementation and userspace-facing builds that need these command definitions. It is tightly coupled to `ioctl.c` and the Ceph file layout model.

## Risks
This is ABI surface. Field size, layout, command number, direction, and magic changes can break existing tools. The obsolete `preferred_osd` field must remain compatible, and the reused numeric command value for layout policy and syncio is safe only because the encoded ioctl direction/type differs.

## Test signals
Compile-time ABI size checks in userspace tools, ioctl round trips on 32-bit and 64-bit architectures, old tool compatibility for `preferred_osd`, and command-dispatch tests for each macro are the most relevant signals.
