<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/hsi_char.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hsi/hsi_char.h

## Purpose
`hsi_char.h` defines the userspace ioctl ABI for HSI character devices, allowing clients to configure transmission parameters, query modem/channel state, and issue break or wake operations.

## Important APIs, types, and functions
The header exports ioctl helpers under `HSI_CHAR_MAGIC` and commands `HSC_RESET`, `HSC_SET_PM`, `HSC_SEND_BREAK`, `HSC_SET_RX`, `HSC_GET_RX`, `HSC_SET_TX`, and `HSC_GET_TX`. Power-management values are `HSC_PM_DISABLE` and `HSC_PM_ENABLE`. Mode and arbitration constants include `HSC_MODE_STREAM`, `HSC_MODE_FRAME`, `HSC_FLOW_SYNC`, `HSC_ARB_RR`, and `HSC_ARB_PRIO`. `struct hsc_rx_config` carries RX mode, flow, and channel count; `struct hsc_tx_config` carries TX mode, channels, speed, and arbitration mode.

## Control flow
Users open an HSI char device, set RX/TX configuration with the config ioctls, optionally enable power management, send break or reset commands, then read/write HSI payloads through the character device.

## State and persistence behavior
Configuration is per HSI char instance and persists while the device is active. Runtime state includes PM enablement, reset/break effects, RX/TX mode, channel count, TX speed, arbitration mode, and transfer queues; payload data is transient.

## Dependencies and integration points
It depends on `<linux/types.h>` and ioctl macros available to users. It integrates with the kernel HSI framework, modem protocol headers such as `cs-protocol.h`, and userspace cellular stacks.

## Risks and test signals
Risks include unsupported speed/mode combinations, racing configuration changes with active transfers, PM state mismatches, reset/break side effects, and ABI layout drift for ioctl structs. Test signals include ioctl set/get symmetry, loopback transfers, break handling, suspend/resume, PM enable/disable tests, invalid parameter rejection, and 32/64-bit compat tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsi/hsi_char.h -->
