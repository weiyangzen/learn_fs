# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_sock.h

## Purpose

`hci_sock.h` defines the userspace-facing HCI socket ABI: socket options, control-message flags, sockaddr layout, HCI channels, packet filters, ioctls, device/connection statistics, and inquiry request structures.

## Important APIs, Types, and Functions

Socket options include `HCI_DATA_DIR`, `HCI_FILTER`, and `HCI_TIME_STAMP`, with CMSG flags for direction and timestamps. `struct sockaddr_hci` selects HCI device and channel (`RAW`, `USER`, `MONITOR`, `CONTROL`, `LOGGING`), with `HCI_DEV_NONE` as wildcard/no-device. `struct hci_filter` and `struct hci_ufilter` contain packet type masks, event masks, and opcode filters. Ioctl constants cover device up/down/reset/stat, device/connection/auth queries, raw/scan/auth/encrypt/packet/link/MTU settings, block/unblock address, and inquiry. Request/response structs model device stats/info, connection info/list, authentication info, and inquiry parameters.

## Control Flow

HCI sockets bind to a device/channel through `sockaddr_hci`, optionally install filters, and send/receive raw or channel-specific HCI traffic. Ioctl handlers in HCI core use these structures to control controller state, query devices/connections, adjust legacy settings, and trigger inquiry.

## State and Persistence Behavior

The header itself stores no state. Socket filters and channel bindings are per-socket runtime state; device stats and flags are snapshots of `hci_dev` state. Ioctls can change controller runtime configuration but do not directly persist to disk.

## Dependencies and Integration Points

It depends on Bluetooth address types and Linux ioctl encoding. It integrates with AF_BLUETOOTH/HCI sockets, HCI core device management, monitor/control/logging channels, and legacy userspace tools.

## Risks and Edge Cases

Filter masks differ between kernel `unsigned long` and fixed-width userspace filter structures, so compat handling matters. Flexible arrays in list/query structs require strict user length validation. Many ioctls are privileged or legacy and can race with device unregister/open/close. Channel semantics differ significantly; raw/user/control/monitor/logging must enforce permissions and isolation.

## Test Signals

Test bind to each channel, wildcard device behavior, filter mask conversion including compat, timestamp/direction CMSG delivery, every ioctl with invalid and valid userspace buffers, device unregister during socket operations, inquiry cache flush flag, block/unblock address, and permission checks.
