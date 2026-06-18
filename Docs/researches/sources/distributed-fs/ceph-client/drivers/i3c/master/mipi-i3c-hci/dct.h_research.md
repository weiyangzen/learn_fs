# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct.h

## Purpose

`dct.h` declares the HCI Device Characteristic Table read helper used by v1 DAA to retrieve newly assigned device identity fields.

## Important APIs, Types, and Functions

- `i3c_hci_dct_get_val(struct i3c_hci *hci, unsigned int dct_idx, u64 *pid, unsigned int *dcr, unsigned int *bcr)` reads one DCT entry and returns PID, DCR, and BCR.

## Control Flow

The v1 DAA path resets the DCT index, performs address assignment, then calls this helper on DCT index 0 to decode the device that just participated.

## State and Persistence Behavior

The header owns no state. It exposes read-only access to hardware DCT contents through `hci->DCT_regs`.

## Dependencies and Integration Points

It depends on `struct i3c_hci` from `hci.h` and is implemented by `dct_v1.c`. Its main consumer is `cmd_v1.c`.

## Risks and Edge Cases

Callers must ensure the DCT section exists and contains the requested index. The function contract has no explicit error return, so invalid hardware state would surface as decoded garbage or MMIO faults.

## Test Signals

DAA tests should validate PID/BCR/DCR decoding for known DCT words and ensure callers reset the DCT index before reading.
