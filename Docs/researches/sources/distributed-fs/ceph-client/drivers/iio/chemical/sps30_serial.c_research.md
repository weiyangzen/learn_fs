# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_serial.c

Purpose: serdev transport implementation for the SPS30 core using Sensirion's framed UART protocol. It handles byte stuffing, checksum, asynchronous frame receive, command validation, device info logging, and ops registration.

Important APIs, types, and functions: `struct sps30_serial_priv` stores receive completion, frame buffer, byte count, escape state, and done flag. `sps30_serial_prep_frame()` constructs frames with SOF/EOF 0x7e, address, command, length, escaped payload/checksum, and checksum over bytes after SOF. `sps30_serial_receive_buf()` waits for SOF, unescapes bytes, appends until EOF, and completes a frame. `sps30_serial_frame_valid()` checks minimum size, expected address/command, zero state byte, length, and checksum. Transport ops implement start/stop, reset, read measurement, fan cleaning, cleaning-period read/write, and serial/version info. `sps30_serial_probe()` configures serdev at 115200 baud, no flow control, no parity, then calls `sps30_probe()`.

Control flow: each command prepares and writes a frame, waits up to 20 ms for a completed response frame, validates it, and copies bounded response payload. Measurement reads sleep one second before issuing read; empty measurement responses become `-ETIMEDOUT`.

State and persistence: transport state is volatile per transaction in `struct sps30_serial_priv`; core state holds the private pointer. Cleaning period persists in the sensor.

Dependencies and integration: depends on serdev, completion, min/max helpers, IIO for retrieving `iio_priv()` in the receive callback, and `sps30.h`. It imports namespace `IIO_SPS30` and matches `sensirion,sps30`.

Risks and test signals: escape decoding returns zero for unknown escaped bytes and warns after replacing, so malformed frames should be tested. Timeout is short relative to serial scheduling. Tests should cover escaped SOF/EOF/data bytes, checksum failure, nonzero state, wrong command response, buffer cap behavior, empty measurement frame, and probe serial configuration.
