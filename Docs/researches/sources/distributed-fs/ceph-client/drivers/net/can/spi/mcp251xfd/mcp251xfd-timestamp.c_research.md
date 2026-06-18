# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-timestamp.c

Purpose: Converts the MCP251xFD 32-bit hardware time base counter into stable nanosecond timestamps for RX, TX echo, and error SKBs.

Important APIs, types, and functions: `mcp251xfd_timestamp_init()` configures the `cyclecounter`; `mcp251xfd_timestamp_start()` initializes the `timecounter` and schedules maintenance; `mcp251xfd_timestamp_stop()` cancels work. Internal helpers read TBC and periodically call `timecounter_read()`.

Control flow: Core initializes and starts the timecounter on open/start. Delayed work runs every configured interval, reads before half-wrap can occur, and reschedules itself. RX/TEF/error paths convert raw hardware timestamps through the timecounter.

State and persistence behavior: Maintains volatile cyclecounter, timecounter, and delayed work in `mcp251xfd_priv`. No persistent clock state survives close.

Dependencies and integration points: Uses Linux clocksource/timecounter helpers, delayed work, and `mcp251xfd_get_timestamp_raw()`. Core sets TBC prescaler and starts/stops the worker.

Risks: The interval must remain below half the 32-bit counter wrap; a static assertion covers this. Read errors log but return zero, making timestamps inaccurate if SPI repeatedly fails.

Test signals: Timestamp monotonicity across long runtime, RX/TX/error hwtstamps, stop/open work cancellation, forced TBC read error logging, and near-wrap validation.
