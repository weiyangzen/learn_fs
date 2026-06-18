# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/dct_v1.c

## Purpose

`dct_v1.c` implements the single exported helper for reading HCI Device Characteristic Table entries. It decodes the identity data captured by hardware during DAA.

## Important APIs, Types, and Functions

- `i3c_hci_dct_get_val()` reads four 32-bit words at `hci->DCT_regs + dct_idx * 16`.
- It decodes PID from DCT word 0 plus bits 47:32 in word 1, DCR from word 2 bits 71:64, and BCR from word 2 bits 79:72.

## Control Flow

The function performs four consecutive `readl()` operations, then applies `FIELD_GET()` with the HCI word-aware masks from `hci.h`. It writes decoded values through caller-provided output pointers and returns no status.

## State and Persistence Behavior

No software state is stored. Hardware DCT state is consumed as a snapshot at the time of the call.

## Dependencies and Integration Points

It uses Linux MMIO reads and bitfield helpers. It is used by the v1 command DAA implementation for debug logging and potential future identity handoff to the I3C core.

## Risks and Edge Cases

There is no bounds or NULL check for `DCT_regs` or the output pointers. The caller must ensure the table is present, the index is valid, and hardware has populated the entry.

## Test Signals

Unit-style tests can feed known MMIO values through an emulated register area and verify PID/BCR/DCR extraction. Integration tests should compare DCT values with the device information later obtained by the I3C core after DAA.
