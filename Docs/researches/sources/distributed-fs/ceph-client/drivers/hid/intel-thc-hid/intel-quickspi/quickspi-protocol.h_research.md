# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.h

## Purpose
`quickspi-protocol.h` declares the QuickSPI HIDSPI protocol operations shared by the PCI driver and HID glue.

## Important APIs, types, and functions
It defines `QUICKSPI_ACK_WAIT_TIMEOUT` and declares `quickspi_handle_input_data()`, `quickspi_get_report()`, `quickspi_set_report()`, `quickspi_get_report_descriptor()`, `quickspi_set_power()`, and `reset_tic()`.

## Control flow and integration points
There is no executable control flow. The PCI probe/PM/recovery paths call reset, descriptor, and power functions; the IRQ thread calls `quickspi_handle_input_data()`; HID raw requests call GET/SET report functions.

## State and persistence behavior
The header owns no state. Declared functions operate on live `struct quickspi_device` fields and waitqueue flags.

## Dependencies
It includes Linux HID-over-SPI for `enum hidspi_power_state` and HIDSPI constants. It forward-declares `struct quickspi_device`.

## Risks and edge cases
Timeout constant changes alter all report/reset waits. GET report does not take an output length parameter in this API, so callers rely on the protocol layer's cached `report_len` and buffer sizing.

## Test signals
Build coverage, reset/probe flow, IRQ RX parsing, HID raw GET/SET calls, and timeout handling validate this contract.
