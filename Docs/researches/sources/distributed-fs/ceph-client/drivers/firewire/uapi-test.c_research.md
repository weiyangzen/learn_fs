# sources/distributed-fs/ceph-client/drivers/firewire/uapi-test.c

## Purpose
KUnit suite that locks down layout of FireWire character-device UAPI event structs exposed through `<linux/firewire-cdev.h>`. It guards ABI size and offset stability for userspace.

## APIs, Types, And Functions
The suite checks `struct fw_cdev_event_response`, `fw_cdev_event_request3`, `fw_cdev_event_response2`, and `fw_cdev_event_phy_packet2` using `sizeof()` and `offsetof()`. It accounts for the known x86-32 alignment difference in `fw_cdev_event_response`.

## Control Flow
Each test function asserts the total structure size and the offset of every fixed field before the trailing flexible `data` member. The cases are registered in the `firewire-uapi-structure-layout` KUnit suite.

## State, Persistence, And Dependencies
There is no mutable state or persistence. Dependencies are KUnit and the public FireWire cdev UAPI header; test behavior varies only by architecture alignment, explicitly handled for `CONFIG_X86_32`.

## Integration Points
The suite runs in kernel KUnit environments and serves as ABI regression coverage for the FireWire userspace event interface introduced or extended across kernel releases.

## Risks And Test Signals
The risk under test is silent UAPI ABI drift caused by field reordering, type changes, or alignment changes. A passing KUnit run confirms the checked layouts; it does not validate ioctl behavior or runtime event delivery.
