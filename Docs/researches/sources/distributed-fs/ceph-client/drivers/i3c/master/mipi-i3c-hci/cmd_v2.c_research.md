# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v2.c

## Purpose

`cmd_v2.c` implements command descriptor preparation for MIPI I3C HCI v2.0. It uses v2 unified transfer descriptors, address-assignment descriptors, explicit dynamic addresses instead of v1 DAT indexes for normal transfers, and v2 transfer mode/rate selector definitions.

## Important APIs, Types, and Functions

- Unified descriptor macros `CMD_U*` encode device address, transfer rate, mode index, ID bytes, read/write, data length, and TID across four descriptor words.
- Address assignment macros `CMD_A*` encode v2 DAA read-ID and assign-address commands.
- `get_i3c_rate_idx()` and `get_i2c_rate_idx()` select rate IDs from the bus SCL rates.
- `hci_cmd_v2_prep_private_xfer()` prepares private I3C/I2C descriptors and packs up to five write bytes as immediate data bytes.
- `hci_cmd_v2_prep_ccc()` handles normal and raw CCC framing, including the NXP raw CCC quirk path for directed CCCs.
- `hci_cmd_v2_daa()` performs two-command DAA: read device ID then assign address.

## Control Flow

Private transfer preparation selects mode `XFERMODE_IDX_I3C_SDR` or `XFERMODE_IDX_I2C`, computes the rate index, assigns a TID, and emits either an immediate-data unified command or a data-buffer unified command. CCC preparation uses broadcast or directed CCC address fields directly. For raw directed CCCs, it delegates to private transfer preparation so the CCC byte is treated as part of the caller payload. For non-raw or broadcast CCCs, it inserts the CCC command byte into IDB0 and adjusts IDB count.

DAA allocates two `hci_xfer` entries. The first reads eight bytes of device ID with an address-assignment descriptor; the second assigns the selected dynamic address. It repeats until the first response is not success, then decodes PID/BCR/DCR from the returned ID words and calls `i3c_master_add_i3c_dev_locked()`.

## State and Persistence Behavior

Unlike v1 normal transfers, v2 descriptors use addresses directly and do not depend on per-device DAT indexes for command addressing. Transfer descriptors and response fields are per-xfer. DAA keeps a stack `device_id` buffer for each loop iteration and no persistent local allocation beyond the temporary xfer array.

## Dependencies and Integration Points

It includes `xfer_mode_rate.h` for mode/rate IDs, `cmd.h` for common response/TID fields, and core I3C helpers for address allocation and device registration. The implementation is selected by `core.c` when `HC_CAP_CMD_SIZE` advertises v2 descriptors.

## Risks and Edge Cases

The file explicitly notes that v2.0 spec details were in flux. Immediate CCC IDB count differs for raw and non-raw modes and should be validated against hardware. DAA treats any non-success first response as normal completion, which may hide unexpected bus errors. The two-command DAA sequence relies on both responses arriving and matching the issued TIDs.

## Test Signals

Validate descriptor fields for I3C/I2C rates, immediate writes up to five bytes, longer reads/writes, raw directed CCCs, and broadcast CCCs. DAA tests should cover successful read-ID/assign pairs, no-device completion, assignment failure, and PID/BCR/DCR decoding from returned words.
