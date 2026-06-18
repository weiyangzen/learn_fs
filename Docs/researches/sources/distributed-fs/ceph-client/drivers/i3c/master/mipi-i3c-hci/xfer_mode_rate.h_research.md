# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/xfer_mode_rate.h

## Purpose

`xfer_mode_rate.h` defines HCI v2 transfer mode table indexes, transfer mode entry bit fields, transfer rate selector IDs, and transfer rate table entry fields. It is the shared vocabulary for parsing extended mode/rate capabilities and creating v2 command descriptors.

## Important APIs, Types, and Functions

- `XFERMODE_IDX_I3C_SDR`, `XFERMODE_IDX_I3C_HDR_DDR`, `XFERMODE_IDX_I3C_HDR_T`, `XFERMODE_IDX_I3C_HDR_BT`, and `XFERMODE_IDX_I2C` identify fixed transfer modes.
- `XFERMODE_*` masks describe supported flag, mode, multilane, and additional-function fields in mode table entries.
- `XFERRATE_I3C_*` and `XFERRATE_I2C_*` constants are descriptor `XFER_RATE` selector values used by `cmd_v2.c`.
- `XFERRATE_*` fields decode data transfer rate table entries, including actual kHz, rate ID, mode ID, and mode-specific data.

## Control Flow

`cmd_v2.c` selects fixed mode indexes and rate selector values from bus SCL rates. `ext_caps.c` parses rate/mode capability tables and logs advertised entries using these definitions.

## State and Persistence Behavior

The header contains constants only. It stores no state and performs no runtime discovery itself.

## Dependencies and Integration Points

It depends on Linux bit macros via includers. It is specific to HCI v2.0 and later.

## Risks and Edge Cases

Mandatory versus optional rates are represented as constants, but current code does not validate that optional advertised tables actually support selected values. Future HDR or multilane support must use the mode/rate tables rather than hard-coded SDR/I2C selections.

## Test Signals

Descriptor tests should verify rate IDs selected by `cmd_v2.c` match requested bus speeds. Ext-cap tests should decode synthetic mode/rate table entries and confirm logged mode IDs and kHz values are correct.
