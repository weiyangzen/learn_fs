# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_serial.c

Purpose: serdev transport wrapper for the SCD30 core using the sensor's Modbus-like serial protocol. It provides framing, CRC16 validation, receive-buffer completion, serial-port setup, and delegates IIO behavior to `scd30_probe()`.

Important APIs, types, and functions: `struct scd30_serdev_priv` tracks a completion, current receive buffer, expected byte count, and accumulated count. `scd30_serdev_cmd_lookup_tbl[]` maps abstract core commands to serial register ids. `scd30_serdev_command()` builds read or write frames with device address 0x61, op code 0x03 or 0x06, register, count/value, and little-endian CRC16; it validates echoed write frames or read headers/CRC before copying payload. `scd30_serdev_receive_buf()` appends incoming bytes into the pending response and completes when the expected count arrives. `scd30_serdev_probe()` allocates private state, opens the serdev, sets 19200 baud, disables flow control, sets no parity, resolves optional firmware IRQ, and calls the shared core.

Control flow: all runtime transactions set `priv->buf`, `num_expected`, and `num`, write a frame, and wait up to 200 ms for receive completion. The serdev callback is asynchronous and only consumes bytes for an active transaction. Read measurement uses a larger word count while other reads request one word; stop/reset are encoded as writes of 1.

State and persistence: transport state is transient per transaction in `struct scd30_serdev_priv`; core state holds the private pointer and command callback. No persistent settings are stored by the transport.

Dependencies and integration: depends on serdev, firmware node IRQ lookup, CRC16, unaligned helpers, and `scd30.h`. It shares the same `sensirion,scd30` compatible and imports `IIO_SCD30`.

Risks and test signals: races around `priv->buf` and late bytes can corrupt the next transaction if locking in the core is bypassed; currently the core mutex serializes command use. Tests should cover partial receive completion, timeout, echoed write mismatch, read byte-count mismatch, CRC failure, unexpected op code, ignored unsolicited bytes, and probe behavior without an IRQ.
