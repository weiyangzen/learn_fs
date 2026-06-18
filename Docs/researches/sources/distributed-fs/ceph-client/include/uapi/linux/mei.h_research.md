# sources/distributed-fs/ceph-client/include/uapi/linux/mei.h

## Purpose
Defines Intel Management Engine Interface userspace ioctls for connecting an open MEI device file to a firmware client by UUID, optionally with a virtual tag, and for enabling/retrieving event notifications.

## Important APIs, Types, And Functions
Exports `IOCTL_MEI_CONNECT_CLIENT`, `IOCTL_MEI_NOTIFY_SET`, `IOCTL_MEI_NOTIFY_GET`, `IOCTL_MEI_CONNECT_CLIENT_VTAG`, `mei_client`, `mei_connect_client_data`, `mei_connect_client_vtag`, and `mei_connect_client_data_vtag`.

## Control Flow
Userspace opens the MEI device, issues a connect ioctl with input UUID or UUID plus vtag, receives firmware client properties in the same union, then uses read/write on that fd for the selected firmware channel. Notification ioctls set and acknowledge pending events.

## State, Persistence, And Dependencies
Connection state is bound to the file descriptor and is released on close. The header depends on `linux/mei_uuid.h` for `uuid_le`.

## Integration Points
Used by MEI userspace services and libraries to communicate with Intel firmware clients. It integrates with file operations, MEI driver connection management, and optional notification support.

## Risks
The connect structs use unions for input/output, so callers must not expect input fields to remain intact after ioctl success. Tagged connections may fail with `-EOPNOTSUPP`. Max message size and protocol version must be honored by userspace.

## Test Signals
Test connect by UUID, vtag rejection/support, notification set/get behavior, max message length enforcement, close-triggered disconnect, and ABI ioctl numbers.
