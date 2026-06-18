# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quickspi/quickspi-protocol.c

## Purpose
`quickspi-protocol.c` implements HIDSPI protocol transactions over Intel THC. It writes HIDSPI output reports through DMA or PIO, reads the device descriptor, retrieves the report descriptor, parses inbound HIDSPI responses/data, resets the touch device through ACPI `_RST`, and implements HID GET/SET report operations with waitqueue completions.

## Important APIs, types, and functions
Public APIs are `quickspi_handle_input_data()`, `quickspi_get_report_descriptor()`, `quickspi_set_power()`, `reset_tic()`, `quickspi_get_report()`, and `quickspi_set_report()`. Internal helpers are `write_cmd_to_txdma()`, `quickspi_get_device_descriptor()`, and `acpi_tic_reset()`.

## Control flow and integration points
`write_cmd_to_txdma()` formats an `output_report` in `qsdev->report_buf` and submits it with `thc_dma_write()`. `quickspi_get_device_descriptor()` sends a `DEVICE_DESCRIPTOR` command by PIO, waits for a non-DMA interrupt, reads interrupt-cause length, reads the input report body, and copies the descriptor from a `DEVICE_DESCRIPTOR_RESPONSE`.

`quickspi_handle_input_data()` parses RXDMA input body headers. It copies report descriptors and wakes `report_desc_got_wq`, records set-power command responses, handles reset responses depending on state, copies GET report responses into `report_buf` and wakes `get_report_cmpl_wq`, wakes SET report completions, and forwards DATA input reports to HID only when the driver is enabled.

`reset_tic()` switches interrupt trigger type, executes ACPI `_RST`, unquiesces interrupts, waits for reset ACK, validates a zero-length reset response body through PIO, sets state reset, and then reads the device descriptor. GET/SET report operations send the appropriate report type and wait up to `QUICKSPI_ACK_WAIT_TIMEOUT` seconds for protocol parsing to set completion flags.

## State and persistence behavior
The file updates `quickspi_device` state, reset/non-DMA/report/get/set completion flags, cached report descriptor, report buffer, report length, and device descriptor. No state is persisted beyond the live device.

## Dependencies
It depends on ACPI, bitfield helpers, HID-over-SPI structures/constants, THC PIO/DMA/interrupt APIs, QuickSPI HID forwarding, and the ACPI companion stored by the PCI driver.

## Risks and edge cases
GET/SET report completion flags are single-flight and not protected by a mutex here. `quickspi_set_report()` skips the first byte of the HID buffer (`buf + 1`) and subtracts one from length, so zero-length or malformed caller buffers would underflow. Device descriptor fetch depends on non-DMA interrupt ordering and exact length from THC interrupt cause. Reset changes interrupt trigger type and must remain synchronized with HIDSPI requirements. DATA reports larger than descriptor max are dropped.

## Test signals
Device descriptor command/response, unexpected input report type, report descriptor length mismatch, set-power response, reset ACK timeout and validation, ACPI `_RST` failure, RXDMA DATA forwarding, GET input/feature report completion, SET output/feature completion, zero/short SET report buffers, and concurrent raw requests are the key tests.
