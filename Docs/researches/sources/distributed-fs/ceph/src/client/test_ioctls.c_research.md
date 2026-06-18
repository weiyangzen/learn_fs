# sources/distributed-fs/ceph/src/client/test_ioctls.c

## Purpose
`test_ioctls.c` is a small manual test utility for CephFS ioctl behavior.

## Important APIs, Types, and Functions
`main()` opens a target file, issues `CEPH_IOC_GET_LAYOUT`, changes stripe unit/count through `CEPH_IOC_SET_LAYOUT`, fetches layout again, issues `CEPH_IOC_GET_DATALOC` for a caller-provided offset, and optionally sets a directory layout policy with `CEPH_IOC_SET_LAYOUT_POLICY` before creating and inspecting a child file.

## Control Flow
The program requires `<filename> <offset>` and optionally a directory path. It exits on the first open/ioctl failure with `perror()`. For dataloc output it formats object metadata and resolves the OSD address with `getnameinfo()`.

## State and Persistence Behavior
It creates or opens the target file, modifies layout metadata, and optionally creates `<dir>/testfile`. These changes persist in the mounted filesystem.

## Dependencies and Integration Points
It includes POSIX file/ioctl/socket headers and `ioctl.h`. It must run on a CephFS mount that supports the ioctl commands.

## Risks
The utility does not close all file descriptors on error, overwrites `new_file_name` globally, and uses fixed test layout values. It is unsuitable as an automated assertion test without output parsing and cleanup.

## Test Signals
Expected output includes initial/final layout fields, dataloc object/offset/block/osd data, and inherited directory policy on the created test file.
