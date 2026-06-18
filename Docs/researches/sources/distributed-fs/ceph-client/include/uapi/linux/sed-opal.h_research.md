<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sed-opal.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sed-opal.h

Purpose: defines ioctl payloads and command numbers for managing TCG Opal self-encrypting drives through block device ioctls.

Important APIs, types, and functions: constants define `OPAL_KEY_MAX` and `OPAL_MAX_LRS`. Enums cover MBR enable/done, users, lock states/flags, key types, revert options, and table operations. Structs include `opal_key`, LR activation/reactivation/setup/status, session info, user/LR assignment, sum ranges, lock/unlock, password changes, MBR data/done/shadow MBR, generic table read/write, status, geometry, discovery, and revert LSP. Ioctls `IOC_OPAL_*` cover save, lock/unlock, ownership, LSP activation/revert, password changes, LR setup/erase/status, MBR operations, table RW, status/geometry/discovery, PSID revert, stack reset, and SUM status.

Control flow: userspace opens a block device and issues Opal ioctls with credentials and target ranges. The kernel Opal layer translates requests into TCG commands, authenticates sessions, manipulates locking ranges, MBR shadowing, or tables, and returns status/geometry/discovery data.

State and persistence behavior: Opal state persists inside drive firmware: ownership, users, keys, locking ranges, MBR flags, geometry, and SUM/range status. Kernel state is a transient command session. User keys are copied through ioctl buffers and must be cleared by callers when appropriate.

Dependencies and integration points: depends on Linux types and ioctl encoding via included block/ioctl context. It integrates with block devices, libata/NVMe/SCSI passthrough as implemented by the Opal core, drive firmware, and storage encryption management tools.

Risks and edge cases: credential buffers are fixed 256 bytes with explicit lengths. Many ioctls are destructive, especially revert, erase, secure erase, PSID revert, and stack reset. Range IDs are bounded by `OPAL_MAX_LRS`; table offsets/lengths and shadow MBR buffers need strict bounds checks.

Test signals: ioctl layout tests, discovery/status/geometry on supported and unsupported drives, lock/unlock and LR setup on test devices, invalid key lengths, invalid LR numbers, MBR enable/done flows, generic table bounds, and negative tests for destructive commands gated by credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sed-opal.h -->
