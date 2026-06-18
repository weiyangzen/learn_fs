## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_core.c

Purpose: serdev/UART transport for BNO055, implementing the chip's serial register protocol as a custom regmap bus and delegating IIO behavior to the common BNO055 core.

Important APIs, types, and functions: `struct bno055_ser_priv` stores the expected command response, expected data length, response buffer, command status, mutex-protected command state, RX finite-state machine, stale-command marker, completion, and serdev pointer. `bno055_ser_send_cmd()` serializes read/write commands, handles stale interrupted commands, retries non-critical hardware failures up to five times, and waits for completion. `bno055_ser_receive_buf()` parses `0xEE` status packets and `0xBB` data packets, copies payload into the waiting regmap buffer, and reports status to `bno055_ser_handle_rx()`. Regmap callbacks are `bno055_ser_write_reg()` and `bno055_ser_read_reg()`.

Control flow: probe allocates transport state, binds serdev callbacks, opens the serial device, enforces 115200 baud, no parity, no flow control, initializes custom regmap, then calls `bno055_probe()` with serial burst threshold 22 and `sw_reset=false`. Command send splits bytes into two-byte chunks with 2-3 ms gaps to avoid BNO055 RX buffer overrun. Reads set the response buffer under lock before sending; RX completion wakes the waiting regmap call.

State and persistence behavior: the RX FSM tracks packet type, expected length, and bytes received across callbacks. `expect_response`, `response_buf`, and `cmd_status` are shared between the regmap thread and RX callback under `lock`. `cmd_stale` handles interrupted waits by waiting for prior command completion before issuing the next one. There is no persistent sensor state beyond transport synchronization; the common driver owns sensor mode/calibration.

Dependencies and integration points: depends on serdev, completions, mutexes, regmap custom buses, optional tracepoints from `bno055_ser_trace.h`, and the common `bno055_probe()`. Device matching uses OF compatible `bosch,bno055`.

Risks and edge cases: the serial protocol is fragile and timing-dependent; exceeding the chip's inter-byte tolerance or buffer capacity causes failures. Software reset is disabled because a successful reset may produce no response. RX malformed packets set critical status and can force `-EIO`. Interrupted reads leave stale state that must drain. `val_size` over 128 is rejected. The RX copy intentionally avoids writing when `response_buf` is NULL or would exceed expected length.

Test signals: serial probe with exact baud/parity, read/write register transactions, retry tracepoints under induced `STATUS_FAIL`, timeout behavior, interrupted command handling, malformed packet handling, stale response safety, common BNO055 probe over serial with reset GPIO present, and buffered scan bursts using threshold 22.
