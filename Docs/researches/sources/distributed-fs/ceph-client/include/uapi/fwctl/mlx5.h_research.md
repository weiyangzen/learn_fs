<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/mlx5.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/mlx5.h

## Purpose
Defines MLX5-specific fwctl discovery data. MLX5 uses firmware user contexts, and this header exposes the UID and capability set bound to a fwctl fd.

## Important APIs, Types, And Functions
`struct fwctl_info_mlx5` contains `uid` and `uctx_caps`. RPC command buffers are expected to follow MLX5 firmware command layouts from the hardware programming reference, with the kernel forcing the fd-bound UID into command headers.

## Control Flow
Userspace calls `FWCTL_INFO`, verifies `FWCTL_DEVICE_TYPE_MLX5`, reads the UID/capability set, and sends MLX5 firmware command buffers via `FWCTL_RPC`. The kernel binds each fd to a user context and mediates commands according to fwctl security scope.

## State And Persistence
The important state is the firmware user context bound to the fd. Firmware-side changes can persist according to MLX5 command semantics; the header only exposes discovery fields.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and generic fwctl. Integrates with MLX5 firmware command handling, user-context capability assignment, NIC/device management tools, and fwctl lockdown/CAP policy.

## Risks And Edge Cases
Incorrectly trusting userspace-supplied UID would violate isolation; the kernel must overwrite/enforce it. Capability drift between firmware and userspace tooling can lead to unsupported command attempts.

## Test Signals
Verify `FWCTL_INFO` UID/caps, command header UID enforcement, unsupported capability rejection, scope enforcement, and firmware error encoding in output buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/mlx5.h -->
