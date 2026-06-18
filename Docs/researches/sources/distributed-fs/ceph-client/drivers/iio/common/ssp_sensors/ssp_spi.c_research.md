
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_spi.c

## Purpose
`ssp_spi.c` implements the SSP AP-to-MCU transport protocol over SPI. It creates command/read/write messages, performs GPIO handshakes, manages pending asynchronous completions, handles threaded IRQ responses, parses MCU data frames, and exposes helper commands used by `ssp_dev.c`.

## Important APIs, types, and functions
- `struct ssp_msg_header` is the packed command header: command, length, options, and data.
- `struct ssp_msg` tracks transfer length/options, pending-list linkage, completion pointer, and DMA-capable buffer.
- `ssp_create_msg()`, `ssp_fill_buffer()`, `ssp_get_buffer()`, and `ssp_clean_msg()` manage message buffers.
- `ssp_do_transfer()` performs the AP/MCU GPIO handshake, writes the header, queues pending transfers, and waits for completion when needed.
- `ssp_irq_msg()` reads MCU response headers, matches pending messages, performs read/write payload phases, or parses MCU-to-AP data frames.
- Exported-to-driver helpers include `ssp_command()`, `ssp_send_instruction()`, `ssp_get_chipid()`, `ssp_set_magnetic_matrix()`, `ssp_get_sensor_scanning_info()`, `ssp_get_firmware_rev()`, and `ssp_clean_pending_list()`.

## Control flow
For AP-originated commands, callers create an `ssp_msg`, `ssp_do_transfer()` lowers the AP-MCU GPIO, writes the header, optionally appends the message to `pending_list`, raises the handshake line, and waits for the IRQ handler to complete the message. `ssp_irq_msg()` reads a small header from the MCU, decodes message type, matches AP read/write replies by options, transfers the payload, handles return-byte write completions, and completes waiters. For MCU-originated writes, it reads the full frame and calls `ssp_parse_dataframe()`, which dispatches bypass sensor data to registered IIO children, debug strings to logging, time-sync updates to parent timestamp state, and reset requests to refresh work.

## State and persistence behavior
Transport state lives in `struct ssp_data`: `comm_lock`, `pending_lock`, `pending_list`, header buffer, handshake GPIOs, `timeout_cnt`, `com_fail_cnt`, `time_syncing`, `timestamp`, and registered child IIO devices. No persistent storage is used. Pending messages are heap allocated per transfer and freed by the caller after completion; `ssp_clean_pending_list()` completes and unlinks outstanding entries during reset/removal.

## Dependencies and integration points
This file depends on SPI core APIs, GPIO descriptor handshakes, kernel completions, lists, mutexes, IIO child data callbacks, and SSP protocol definitions from `ssp.h`. It is tightly coupled to `ssp_dev.c` for lifecycle and refresh scheduling, and to child IIO drivers through `data->sensor_devs[]` and `struct ssp_sensor_data::process_data`.

## Risks and edge cases
- `ssp_offset_map` contains `SSP_UNIMPLEMENTED` entries set to `-1`; if an unimplemented sensor ID appears in bypass data, `idx += -1` can move the parser backward and corrupt parsing.
- `ssp_parse_dataframe()` does not reject unimplemented offsets before advancing, and it treats library data as `idx += len`, which jumps beyond the frame from the current index.
- `ssp_clean_pending_list()` completes pending messages but does not free them; this is correct for callers that own the message, but any unmatched ownership path would leak.
- `ssp_do_transfer()` increments `timeout_cnt` on handshake and completion failures but does not increment `com_fail_cnt`; watchdog behavior depends on other code updating communication failures.
- Matching pending messages only by `options` can be ambiguous if multiple in-flight messages share the same option bits.
- GPIO handshake timeout loops can sleep for roughly 1.5 seconds per state before failing.

## Test signals
Transport tests need real or emulated MCU behavior: WHOAMI read returns `SSP_DEVICE_ID`, firmware/scanning reads decode little-endian values, sensor add/remove instructions complete, MCU bypass frames deliver samples to the correct IIO device, dead/unmatched packets are drained and reported, and reset while transfers are pending wakes waiters without list corruption. Fuzzing `ssp_parse_dataframe()` with unknown sensor IDs and malformed lengths is especially valuable.
