# File Research: sources/block-storage/lvm2/libdm/ioctl/libdm-targets.h

Purpose: defines libdevmapper's internal ioctl/task data structures shared by the ioctl implementation and related low-level code.

Read coverage: complete file read, 99 lines.

Key contents:
- Declares `struct target`, the internal linked-list node for a table segment with start sector, length, target type, target parameters, and next pointer.
- Defines the full internal `struct dm_task`, including public task type, device name/UUID and mangled variants, target list, major/minor identity, permissions, read-ahead, ioctl result buffer, rename/message/geometry state, flags, udev cookie state, expected/ioctl errno, timestamp recording, and feature toggles.
- Defines `struct cmd_data`, mapping a public task type to a command name, ioctl number, and version triplet.
- Defines remove retry constants: `DM_IOCTL_RETRIES` and `DM_RETRY_USLEEP_DELAY`.
- Declares internal helpers `dm_ioctl_exec()`, `dm_check_version()`, and `dm_task_get_existing_table_size()`.

Dependencies:
- Includes the public `libdevmapper.h` API and standard integer/types headers.
- Forward-declares `struct dm_ioctl`, keeping the kernel ioctl ABI definition out of this internal header's public declarations.

Risk and edge cases:
- `struct dm_task` is an internal ownership hub; memory-management mistakes around moved target lists, `dmi.v4`, mangled strings, and secure data can produce leaks, double frees, or missed zeroing.
- The header exposes internals across libdm compilation units, so field changes require careful ABI/API separation from the public opaque `struct dm_task`.
- Retry constants directly shape remove latency: 25 retries at 200 ms can add about five seconds to busy-device removal attempts.
