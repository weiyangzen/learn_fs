# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_ioctl.c

## Purpose
This file implements common ioctl dispatch for HabanaLabs information, debug, eventfd, security-attestation, firmware-query, and control-device requests.

## Important APIs, Types, And Functions
`hl_info_ioctl()` is the DRM compute info entry point. `hl_ioctl_control()` is the control-node ioctl path and only accepts `DRM_IOCTL_HL_INFO`. `_hl_info_ioctl()` dispatches `HL_INFO_*` opcodes. `hl_debug_ioctl()` handles `HL_DEBUG_OP_*`. `_hl_ioctl()` marshals control ioctl payloads using a small stack buffer or heap allocation. Helper families expose hardware IP info, events, DRAM usage, idle/utilization, clocks, PCI counters, throttling, CS counters, sync-manager data, security attestation, signed device info, and captured error events.

## Control Flow
The info dispatcher validates padding, serves a whitelist of safe opcodes even while the device is disabled/resetting, then requires `hl_device_operational()` for live firmware/hardware queries. Most handlers validate user buffer pointer and size, fill a local or allocated struct, and copy bounded data back to userspace. Debug operations require operational state and, for coresight ops, `hdev->in_debug`.

## State And Persistence
The file reads persistent counters and snapshots from `hdev`, `hpriv`, context CS counters, throttling state, reset/open stats, and captured error structures. It mutates notifier event masks and owns `eventfd_ctx` registration/unregistration for a file private.

## Dependencies And Integration Points
It depends on HabanaLabs UAPI structs, firmware CPUCP helpers, ASIC callbacks, eventfd, copy-to/from-user, reset/status state, and the control file opened in `habanalabs_drv.c`.

## Risks
This is UAPI-facing; pointer, size, and padding validation are critical. Eventfd lifetime must match file release. Firmware passthrough allocation/free sizes and 1 MiB limit need coverage. Debug access relies on debug-mode state.

## Test Signals
Test every opcode class in reset and operational states, malformed padding, undersized/null buffers, control-node eventfd rejection, double eventfd register/unregister, debug when not in debug mode, attestation copy paths, and firmware generic request errors.
