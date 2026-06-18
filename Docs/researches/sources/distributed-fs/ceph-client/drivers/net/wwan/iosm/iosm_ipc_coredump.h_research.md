# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.h

## Purpose
Declares IOSM coredump table wire formats, size limits, and coredump collection APIs.

## Important APIs, Types, And Functions
Defines `MAX_CD_LIST_SIZE`, `MAX_DATA_SIZE`, `MAX_SIZE_LEN`, packed `struct iosm_cd_list_entry`, packed `struct iosm_cd_list`, packed `struct iosm_cd_table`, and prototypes for `ipc_coredump_collect()` and `ipc_coredump_get_list()`.

## Control Flow
No independent flow. Devlink code uses these declarations to retrieve coredump metadata and snapshot data from the modem.

## State And Persistence
Packed structs represent modem-provided coredump list data. Each list entry carries a little-endian size and filename.

## Dependencies And Integration Points
Includes `iosm_ipc_devlink.h` for `struct iosm_devlink`, filename length constants, coredump region count, and RPSI integration.

## Risks
The flexible `entry[]` table is parsed from a fixed-size buffer; callers must validate `num_entries`. Packed layout and endian conversion must match modem firmware.

## Test Signals
Build and run coredump list parsing on modem firmware variants, including boundary filename lengths and max region counts.
