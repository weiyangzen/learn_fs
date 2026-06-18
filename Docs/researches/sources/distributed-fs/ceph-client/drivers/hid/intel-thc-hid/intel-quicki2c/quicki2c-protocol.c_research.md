# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-quicki2c/quicki2c-protocol.c

## Purpose
`quicki2c-protocol.c` implements HID-over-I2C transactions on top of Intel THC PIO, SWDMA, and DMA helpers. It encodes HIDI2C commands, reads device/report descriptors, handles HID GET/SET/output reports, powers the device, and performs reset with interrupt or fallback PIO acknowledgment.

## Important APIs, types, and functions
Public APIs are `quicki2c_set_power()`, `quicki2c_get_device_descriptor()`, `quicki2c_get_report_descriptor()`, `quicki2c_get_report()`, `quicki2c_set_report()`, `quicki2c_output_report()`, and `quicki2c_reset()`. Internal helpers are `quicki2c_init_write_buf()`, `quicki2c_encode_cmd()`, and `write_cmd_to_txdma()`.

## Control flow and integration points
Command construction writes the command register, encoded command, optional data register, and optional length-prefixed payload into `qcdev->report_buf`. `quicki2c_get_device_descriptor()` reads the descriptor from the ACPI-provided HID descriptor address by PIO and validates the HIDI2C BCD version. `quicki2c_get_report_descriptor()` reads from the report descriptor register with SWDMA. GET_REPORT sends a command and reads a `struct hidi2c_report_packet`, validating packet length and report ID before copying to the HID buffer. SET_REPORT and output reports write data through THC DMA.

Reset sends `HIDI2C_RESET`, waits up to five seconds for `reset_ack_wq`, and if no interrupt-driven ACK arrives, reads the input register manually and treats a zero length word as reset response. This integrates with `pci-quicki2c.c`, whose IRQ path sets `reset_ack` when it sees zero-length input during `QUICKI2C_RESETING`.

## State and persistence behavior
The file uses and updates `quicki2c_device` buffers, descriptor fields, reset flag/state, and report length. It does not persist anything outside live driver memory.

## Dependencies
It depends on Linux HID-over-I2C definitions, unaligned little-endian helpers, bitfield helpers, and exported THC APIs: `thc_tic_pio_write_and_read()`, `thc_tic_pio_read()`, `thc_swdma_read()`, and `thc_dma_write()`.

## Risks and edge cases
`quicki2c_init_write_buf()` must size command/data sequences correctly to avoid report-buffer overflow. GET_REPORT requires exact returned length and first data byte matching the report number, which may reject devices with unusual report framing. Reset fallback assumes a zero length word unambiguously means reset response. Unsupported output/input/feature type combinations return `-EINVAL`; unsupported raw request behavior is partly handled in HID glue. Concurrency around shared `report_buf`/`input_buf` is not locally serialized, so HID requests and IRQ/reset paths rely on higher-level sequencing.

## Test signals
Descriptor read and BCD mismatch, command encoding for report IDs below and above `HIDI2C_CMD_MAX_RI`, buffer overflow rejection, GET_REPORT length/ID validation, SET_REPORT and output report DMA writes, reset interrupt ACK and fallback PIO ACK paths, timeout behavior, runtime PM raw requests, and fuzzed device packet lengths should be covered.
