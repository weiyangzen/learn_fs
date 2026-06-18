# sources/distributed-fs/ceph-client/drivers/hsi/hsi_core.h

## Purpose
Defines private HSI core structures shared by board-info registration and core bus scanning.

## Important APIs, Types, and Functions
- `struct hsi_cl_info` wraps `struct hsi_board_info` with a list node.
- Declares the global `hsi_board_list`.

## Control Flow
No executable control flow. `hsi_boardinfo.c` appends entries to `hsi_board_list`; `hsi_core.c` scans it when controllers are registered.

## State and Persistence
The header describes the in-memory static-client registry. Persistence is kernel-lifetime only.

## Dependencies and Integration Points
Depends on public `<linux/hsi/hsi.h>` for `struct hsi_board_info` and list infrastructure through included kernel headers.

## Risks and Test Signals
Risks are limited to structure coupling between the two C files. Test signals are successful static client registration and no duplicate external definition of `hsi_board_list`.
