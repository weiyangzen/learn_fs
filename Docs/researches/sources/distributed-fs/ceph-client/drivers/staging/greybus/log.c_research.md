# sources/distributed-fs/ceph-client/drivers/staging/greybus/log.c

## Purpose
Greybus Log protocol driver. It receives log strings from a module and emits them through dynamic debug on the bundle device.

## Important APIs, Types, And Functions
`struct gb_log` stores the connection. `gb_log_request_handler()` validates unsolicited `GB_LOG_TYPE_SEND_LOG` requests, checks length fields, bounds against `GB_LOG_MAX_LEN`, forces NUL termination, and logs with `dev_dbg()`. Probe/disconnect manage one connection.

## Control Flow
Probe requires one LOG CPort, allocates state, creates a connection with the request handler, enables it, and saves driver data. Incoming send-log requests are validated and printed. Disconnect disables and destroys the connection and frees state.

## State And Persistence
No persistent state beyond connection lifetime. Received log messages are not stored by the driver.

## Dependencies And Integration Points
Uses Greybus Log protocol, Greybus bundle matching by `GREYBUS_CLASS_LOG`, and Linux dynamic debug via `dev_dbg()`.

## Risks
The handler writes a terminator into the received payload buffer. Logs are intentionally debug-level to limit denial-of-service potential, but high-volume modules can still consume Greybus and CPU resources.

## Test Signals
Test probe CPort validation, wrong request type, too-small payload, mismatched length, zero length, oversized length, missing terminator, dynamic-debug enablement, and disconnect cleanup.
