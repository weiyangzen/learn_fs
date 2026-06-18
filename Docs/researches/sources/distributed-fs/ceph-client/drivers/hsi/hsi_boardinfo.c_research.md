# sources/distributed-fs/ceph-client/drivers/hsi/hsi_boardinfo.c

## Purpose
Provides the board-file registration path for statically described HSI clients.

## Important APIs, Types, and Functions
- Global `hsi_board_list` stores `struct hsi_cl_info` entries and is exported GPL for internal framework use.
- `hsi_register_board_info()` copies an array of `struct hsi_board_info` into allocated list entries during init.

## Control Flow
Callers pass board info and length. The function allocates an array of `struct hsi_cl_info`, copies each board entry, and appends it to `hsi_board_list`. Later, `hsi_core.c` scans the list when a matching controller registers and instantiates clients on the requested port.

## State and Persistence
The global list persists for the life of the kernel. Entries are allocated during init and are not freed here, matching traditional board-info registration patterns.

## Dependencies and Integration Points
Depends on `hsi_core.h`, list APIs, slab allocation, and the HSI framework's `struct hsi_board_info`. It integrates with `hsi_scan_board_info()` in `hsi_core.c`.

## Risks and Test Signals
Risks include allocation failure, stale board data, or mismatched HSI controller/port IDs causing clients not to appear. Test signals include static board clients being created after controller registration and graceful `-ENOMEM` on allocation failure.
