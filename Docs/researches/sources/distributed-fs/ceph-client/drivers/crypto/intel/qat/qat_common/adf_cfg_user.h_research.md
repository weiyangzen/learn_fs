# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_user.h

## Purpose
This header defines packed user-to-kernel configuration structures accepted by the QAT control ioctl for setting device resource parameters.

## Important APIs, Types, And Functions
Important types are `struct adf_user_cfg_key_val`, `struct adf_user_cfg_section`, and `struct adf_user_cfg_ctl_data`. The key/value and section structs contain user pointers expressed through unions with `__u64` padding to support compat layouts. There are no functions.

## Control Flow
No executable flow exists. `adf_ctl_drv.c` walks linked user-space section and key/value lists using these layouts and copies each node with `copy_from_user()`.

## State And Persistence Behavior
These structures describe transient ioctl input. Once copied, values are converted into kernel `adf_cfg` sections and keys. No persistent storage is created by the header.

## Dependencies And Integration Points
It includes config common and string headers and is used by `/dev/qat_adf_ctl` ioctl handling. It is part of the user-facing ABI.

## Risks
Packed layout and pointer padding are ABI-sensitive. The kernel limits traversal to 512 sections and 256 keys per section; malformed user pointers cause ioctl failure and config rollback.

## Test Signals
32-bit compat ioctl tests, config of nested sections/key values, invalid user pointer handling, maximum section/key bounds, and status after rollback validate this header.
