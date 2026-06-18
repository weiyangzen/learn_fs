# sources/distributed-fs/ceph-client/include/linux/mtd/pfow.h

## Purpose

Defines the PFOW command register interface for LPDDR/Numonyx-style object-mode flash programming and erase operations over an MTD map.

## Important APIs, Types, and Functions

It provides PFOW register offsets, LPDDR command codes, DSR status/error masks, and `send_pfow_command()` which writes command, address, length, optional data, and execute registers through `map_write()`.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PFOW_H`, `PFOW_QUERY_STRING_P`, `PFOW_QUERY_STRING_F`, `PFOW_QUERY_STRING_O`, `PFOW_QUERY_STRING_W`, `PFOW_MANUFACTURER_ID`, `PFOW_DEVICE_ID`, `PFOW_PROGRAM_BUFFER_OFFSET`, `PFOW_PROGRAM_BUFFER_SIZE`, `PFOW_COMMAND_CODE`, `PFOW_COMMAND_DATA`, `PFOW_COMMAND_ADDRESS_L`, `PFOW_COMMAND_ADDRESS_H`, `PFOW_DATA_COUNT_L`, `PFOW_DATA_COUNT_H`, `PFOW_COMMAND_EXECUTE`.

## Control Flow

Callers build `map_word` commands with the LPDDR helper macros, write command/address/count/data registers at `map->pfow_base`, and start execution by writing `LPDDR_START_EXECUTION`; later code checks the DSR ready/error bits.

## State and Persistence Behavior

Hardware PFOW command and status registers carry transient operation state. Persistent state is flash blocks, locks, and OTP contents changed by commands.

## Dependencies and Integration Points

It depends on `map.h` and `qinfo.h` command helpers. It integrates with LPDDR flash chip drivers.

Direct includes observed in the source are: `#include <linux/mtd/qinfo.h>`.

## Risks and Edge Cases

Address/count splitting uses `map_bankwidth()` bits-per-chip; wrong bank width or PFOW base sends commands to wrong registers. DSR error bits must be fully checked and cleared.

## Test Signals

Mock map writes for word program, buffer program, erase, lock/unlock, OTP commands, plus DSR error handling and wide-bank address splitting.

Source read signal: 124 lines, 4489 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
