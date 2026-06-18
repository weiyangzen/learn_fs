# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/cmd.h

## Purpose

`cmd.h` is the shared command/response contract for the MIPI I3C HCI master driver. It defines descriptor bits that are common to both HCI v1 and v2 command formats, response decoding helpers, HCI response error codes, transfer ID generation, and the `hci_cmd_ops` vtable consumed by the core.

## Important APIs, Types, and Functions

- `CMD_0_TOC`, `CMD_0_ROC`, `CMD_0_ATTR`, and `CMD_0_TID` are descriptor word-0 fields that the core may add after version-specific preparation.
- `RESP_STATUS()`, `RESP_TID()`, and `RESP_DATA_LENGTH()` decode hardware response descriptors used by PIO and DMA backends and by core transfer result handling.
- `enum hci_resp_err` maps HCI status nibbles to success, CRC/parity/frame/NACK/overflow/short-read/terminated/not-supported, and transfer-specific errors.
- `hci_get_tid()` allocates four-bit command transaction IDs from `hci->next_cmd_tid`.
- `struct hci_cmd_ops` abstracts descriptor preparation for CCC, private I3C, private I2C, and DAA operations.
- `mipi_i3c_hci_cmd_v1` and `mipi_i3c_hci_cmd_v2` are the two concrete implementations selected by core capability probing.

## Control Flow

The core calls the chosen `hci->cmd` callbacks when preparing transfers. Version-specific code fills `struct hci_xfer.cmd_desc[]`, assigns `cmd_tid`, and may consume small write payloads into immediate descriptor bytes by clearing `xfer->data`. The core later sets common `ROC` and `TOC` bits and submits descriptors to the selected I/O backend.

## State and Persistence Behavior

This header owns no storage, but its TID macro mutates `hci->next_cmd_tid`. TIDs wrap modulo 16, so correctness depends on the response queues preserving order or matching responses before a wrapped TID can collide with a live descriptor.

## Dependencies and Integration Points

It depends on bit helpers from `hci.h` and Linux bitfield macros included by C files. It is included by command implementations, core transfer paths, PIO/DMA backends, and error handlers.

## Risks and Edge Cases

TID width is only four bits, so stalled or out-of-order hardware responses can make diagnostics ambiguous. Several response enum values are shared by different transfer contexts, requiring callers to interpret status with command type in mind. The common `CMD_0_*` masks must remain synchronized with both descriptor formats.

## Test Signals

Useful signals include descriptor TID/attribute bit validation for v1 and v2 commands, response decoding for every status nibble, timeout/dequeue behavior with wrapped TIDs, and CCC/I3C/I2C transfers that verify `ROC` and `TOC` are applied by the core after version-specific preparation.
