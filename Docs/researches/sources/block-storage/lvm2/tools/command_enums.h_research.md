# File Research: sources/block-storage/lvm2/tools/command_enums.h

## Purpose
`command_enums.h` centralizes generated enums and command policy flags used by LVM2 command parsing and dispatch.

## Contents
It includes generated command-definition IDs, then expands macro lists into option enums, value enums, LV property enums, LV type enums, and top-level command enums.

It also defines command policy flags such as `PERMITTED_READ_ONLY`, `ALL_VGS_IS_DEFAULT`, `ENABLE_ALL_DEVS`, `LOCKD_VG_SH`, `NO_METADATA_PROCESSING`, `ALLOW_HINTS`, `ALLOW_EXPORTED`, `CHECK_DEVS_USED`, and `ALTERNATIVE_EXTENTS`.

## Integration Notes
Enum ordering and flag values are consumed by `command.c`, `command.h`, command dispatch, command validation, and `commands.h`.
