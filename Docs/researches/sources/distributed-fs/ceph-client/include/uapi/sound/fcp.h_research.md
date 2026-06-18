# sources/distributed-fs/ceph-client/include/uapi/sound/fcp.h

## Purpose
`fcp.h` defines the ALSA hwdep userspace ABI for the Focusrite Control Protocol driver. It exposes privileged control of proprietary Focusrite USB audio interface features for Scarlett, Clarett, Clarett+, and Vocaster devices.

## Important APIs, Types, and Constants
Version macros define FCP hwdep version 2.0.0 and extraction helpers. Ioctls are `FCP_IOCTL_PVERSION`, `FCP_IOCTL_INIT`, `FCP_IOCTL_CMD`, `FCP_IOCTL_SET_METER_MAP`, and `FCP_IOCTL_SET_METER_LABELS`.

`struct fcp_init` contains step 0/2 response sizes, two initialization opcodes, and a flexible response tail. `struct fcp_cmd` contains an opcode, request size, response size, and in-place flexible data buffer. `struct fcp_meter_map` configures control-channel-to-meter mappings with signed slots, and `struct fcp_meter_labels` provides null-terminated label data.

## Control Flow and State
Userspace opens the hwdep device with `CAP_SYS_RAWIO`, queries protocol version, calls `FCP_IOCTL_INIT` to synchronize sequence numbers and protocol state, then uses `FCP_IOCTL_CMD` for device commands. Meter support is configured by setting a meter map, then labels. The map size and slot count become fixed after first configuration, though mappings may be updated.

## State and Persistence Behavior
Initialization synchronizes driver/device sequence state. Meter map and labels configure ALSA level-meter controls and remain functional after the hwdep device closes. Command buffers are variable-length and response data overwrites request data.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/ioctl.h>`. Integration points are ALSA hwdep, the Focusrite USB mixer/scarlett2 driver, privileged user daemons such as fcp-server, and level-meter ALSA controls.

## Risks and Test Signals
Risks include privileged near-direct device access, flexible-array size validation, sequence synchronization mistakes, response-overwrites-request buffer sizing, and immutable meter map dimensions after configuration. Tests should cover version/init flow, invalid command before init, command req/resp size bounds, meter map reconfiguration rules, label parsing, and permission enforcement.
