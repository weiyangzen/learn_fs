# sources/distributed-fs/ceph-client/include/linux/hid-over-spi.h

## Purpose
`hid-over-spi.h` defines HID over SPI protocol packet formats. It gives SPI HID drivers the enums, headers, size macros, and descriptor layout needed to request descriptors, send commands, move reports, handle fragmentation, and interpret response bodies.

## Important APIs, Types, And Functions
The central definitions are `enum input_report_type`, `enum output_report_type`, `enum hidspi_power_state`, `struct input_report_body_header`, `struct input_report_body`, `struct output_report_header`, `struct output_report`, and `struct hidspi_dev_descriptor`. Bit masks such as `HIDSPI_INPUT_HEADER_VER`, `HIDSPI_INPUT_HEADER_REPORT_LEN`, `HIDSPI_INPUT_HEADER_LAST_FLAG`, and `HIDSPI_INPUT_HEADER_SYNC` describe the 32-bit input header. `HIDSPI_INPUT_BODY_SIZE()` and `HIDSPI_OUTPUT_REPORT_SIZE()` size variable payload packets.

## Control Flow And State
Transport code sends output reports for descriptor reads, feature reports, input report requests, output reports, and command content. Incoming SPI frames are validated via protocol version, sync byte, length, last-fragment flag, body type, content length, and content ID. Fragmented input bodies are accumulated until the last flag. Persistent state is hardware descriptor values, power state, pending command/report transactions, and any driver buffers used for fragment assembly.

## Dependencies And Integration Points
The header depends on `linux/bits.h` and `linux/types.h`. It integrates with HID core as a low-level transport beneath report descriptor parsing and raw report request/output callbacks.

## Risks
Risks include frame length calculation mistakes because header length is measured in 32-bit words, missing `__packed` on `struct hidspi_dev_descriptor`, accepting invalid report type enum values, failing to validate fixed protocol version `0x0300`, and fragment reassembly buffer overflow. Power transitions and command response matching must be serialized by the implementation.

## Test Signals
Tests should cover device/report descriptor responses, fragmented data reports, reset and command responses, get/set feature, output reports, power on/sleep/off, invalid sync/version, content length mismatch, and maximum fragment/report sizes.
