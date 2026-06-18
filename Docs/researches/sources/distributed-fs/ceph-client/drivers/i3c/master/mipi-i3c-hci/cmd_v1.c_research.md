# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd_v1.c

## Purpose

`cmd_v1.c` implements HCI v1.0/v1.1 command descriptor generation. It translates Linux I3C core CCC/private-transfer/DAA requests into v1 address-assignment, immediate-data, regular-data, and internal-control descriptor words.

## Important APIs, Types, and Functions

- Descriptor macros define v1 address assignment (`CMD_0_ATTR_A`), immediate transfer (`CMD_0_ATTR_I`), regular transfer (`CMD_0_ATTR_R`), combo transfer, and internal-control fields.
- `enum hci_cmd_mode` maps bus rates to HCI v1 I3C/I2C mode selectors.
- `get_i3c_mode()` and `get_i2c_mode()` derive descriptor mode from `bus->scl_rate`.
- `fill_data_bytes()` packs up to four write bytes into descriptor word 1 and clears `xfer->data` so I/O backends do not transfer a separate data buffer.
- `hci_cmd_v1_prep_ccc()`, `hci_cmd_v1_prep_i3c_xfer()`, and `hci_cmd_v1_prep_i2c_xfer()` prepare transfer descriptors.
- `hci_cmd_v1_daa()` performs one-address-at-a-time ENTDAA using a temporary DAT entry and DCT readback.

## Control Flow

CCC preparation rejects raw CCC framing, resolves directed CCC addresses through the v1 DAT, assigns a TID, and chooses immediate descriptors for writes of four bytes or less, otherwise regular descriptors. Private I3C/I2C preparation follows the same immediate-versus-regular split using the device's allocated DAT index.

DAA allocates one temporary DAT entry per candidate device, asks the core for the next free dynamic address, writes that address into DAT, resets the DCT read index, submits an address-assignment command with `ROC|TOC`, then interprets response status. Address-header/NACK with response length 1 means no more devices; successful assignment reads PID/BCR/DCR from DCT, frees the temporary DAT entry, and registers the new device with the I3C core, which will allocate its persistent DAT entry.

## State and Persistence Behavior

Prepared descriptors are stored in caller-owned `struct hci_xfer`. Persistent device state is the DAT index stored in per-device master data by core attach callbacks. DAA temporarily mutates DAT and DCT state and always frees the temporary DAT slot on exit when allocated.

## Dependencies and Integration Points

This file depends on `dat_v1` for DAT allocation/address lookup, `dct_v1` for DCT identity reads, `i3c_hci_process_xfer()` for synchronous command execution, and I3C core helpers such as `i3c_master_get_free_addr()` and `i3c_master_add_i3c_dev_locked()`.

## Risks and Edge Cases

Raw CCC is unsupported for v1 and returns `-EINVAL` if requested by a quirk. Small write payload packing reads a `u8 *` supplied by the caller; zero-length writes are handled but malformed non-NULL assumptions would be caller bugs. DAA registers devices without passing captured PID/BCR/DCR to the core, leaving the core to rediscover data later. One-at-a-time DAA is simple but slower and has several hardware response interpretations that should be checked on real controllers.

## Test Signals

Test immediate and regular descriptors for broadcast CCC, directed CCC, private I3C, and legacy I2C. Exercise DAA with no devices, one device, multiple devices, DAT exhaustion, DCT readback, and non-success response status. Hardware tests should verify DAT slots are freed after DAA failures.
