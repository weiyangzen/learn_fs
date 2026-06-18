# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.c

## Purpose
Implements IOSM modem coredump list retrieval and per-file coredump data collection for devlink regions.

## Important APIs, Types, And Functions
Exports `ipc_coredump_collect()` and `ipc_coredump_get_list()`. `ipc_coredump_collect()` allocates a vmalloc buffer, sends `rpsi_cmd_coredump_get`, and reads data in chunks up to `MAX_DATA_SIZE`. `ipc_coredump_get_list()` allocates a `MAX_CD_LIST_SIZE` table, sends start/end/list commands, reads the table, validates entry count and file sizes, updates `devlink->cd_file_info[]`, and emits devlink flash status notifications for filenames and sizes.

## Control Flow
Devlink snapshot invokes `ipc_coredump_collect()` with a region entry. Collection uses the actual file size from `cd_file_info`, but allocates the default region size passed by the caller. Start-list flow sends an RPSI command, reads exactly 4 KiB, validates the number of entries against `IOSM_NOF_CD_REGION`, and stores each modem-reported actual size if it does not exceed the default.

## State And Persistence
Coredump metadata persists in `iosm_devlink.cd_file_info`, specifically `actual_size` populated from modem list entries. Collected snapshot data is vmalloc-owned and later freed by the devlink region destructor.

## Dependencies And Integration Points
Depends on `iosm_ipc_devlink.h`, devlink status notifications, RPSI command constants, and IMEM devlink read/write helpers. Called from `iosm_ipc_devlink.c` snapshot and init flows.

## Risks
If `ipc_imem_sys_devlink_read()` returns zero bytes without error during collection, the loop would not make progress. `size` is declared `u8[MAX_SIZE_LEN]` but passed to `snprintf()` as a char buffer. The code requires an exact 4 KiB list read and rejects any short read. File-size validation prevents modem-reported sizes from exceeding default region sizes.

## Test Signals
Test coredump start/list/end, zero entries, too many entries, oversized file entries, short list reads, chunked data reads over 64 KiB, read errors mid-file, and devlink region snapshot cleanup.
