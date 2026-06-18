# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_spi.c

## Purpose
`cros_ec_spi.c` is the SPI transport driver for Chrome EC. It implements both legacy command and v3 packet transfer callbacks, handles SPI framing/preamble reads, checksum validation, chip-select timing, retryable EC-not-ready markers, high-priority transfer execution, device-tree timing properties, registration with the Chrome EC core, and PM delegation.

## Important APIs, Types, and Functions
- `struct cros_ec_spi` stores the SPI device, last transfer time, start/end CS delays, and high-priority worker.
- `terminate_request()` deasserts chip select with optional delay and updates `last_transfer_ns`.
- `receive_n_bytes()`, `cros_ec_spi_receive_packet()`, and `cros_ec_spi_receive_response()` implement SPI receive phases.
- `do_cros_ec_pkt_xfer_spi()` handles protocol v3 `ec_host_response` transfers.
- `do_cros_ec_cmd_xfer_spi()` handles legacy protocol v2 response layout.
- `cros_ec_xfer_high_pri()` runs transfer work on a FIFO-scheduled kthread worker.
- Probe/remove and PM callbacks bind the transport to the generic EC core.

## Control Flow
Transfer starts with `cros_ec_prepare_tx()`, waits for the required inter-transaction recovery time, allocates an RX echo buffer, locks the SPI bus, optionally inserts a start delay, transmits the request with `cs_change`, scans returned bytes for retryable markers (`PAST_END`, `RX_BAD_DATA`, `NOT_READY`), reads the response after finding `EC_SPI_FRAME_START`, terminates the request to release CS, unlocks, then parses EC result, payload length, and checksum. Public `cmd_xfer` and `pkt_xfer` callbacks only enqueue this work on the high-priority worker and wait synchronously for completion.

## State and Persistence
Per-device state persists in `struct cros_ec_spi`: timing delays from firmware properties, `last_transfer_ns` for recovery delay enforcement, and the high-priority worker lifetime. The EC core owns command buffers and protocol state. Wakeup is enabled on the SPI device after successful registration.

## Dependencies and Integration Points
The driver depends on Linux SPI APIs, device tree compatible `"google,cros-ec-spi"`, optional DT properties `google,cros-ec-spi-pre-delay` and `google,cros-ec-spi-msg-delay`, Chrome EC protocol helpers, scheduler FIFO support, and core EC registration/suspend/resume APIs.

## Risks and Edge Cases
SPI timing is delicate: insufficient recovery, start, or end delays can make the EC abort transactions. Response polling uses a 200 ms deadline and reads 32 preamble bytes at a time. v3 packet receive checks `response->data_len > ec_dev->din_size`, but the later payload length is checked against `ec_msg->insize`; both limits matter. Legacy receive returns `-ENOSPC` for oversized payloads while v3 uses `-EMSGSIZE`. High-priority worker creation and FIFO scheduling are required to avoid long preemption during chip-select assertions.

## Test Signals
No local SPI KUnit is included in this subset. Shared protocol tests cover transmit framing and EC result handling. Runtime test signals include successful `cros_ec_register()`, absence of preamble timeouts/checksum errors, and stable command behavior under load or slow tunneled I2C commands.
