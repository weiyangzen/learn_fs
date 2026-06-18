# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.h

## Purpose
`dot_command.h` defines the IBM ASM dot-command protocol header, message type constants, size calculation, and timeout classification.

## Important APIs, Types, and Functions
It defines type values `sp_write`, `sp_write_next`, `sp_read`, `sp_read_next`, `sp_command_response`, `sp_event`, and `sp_heartbeat`. Packed `struct dot_command_header` contains type, command size, data size, status, and reserved fields. Inline helpers are `get_dot_command_size()` and `get_dot_command_timeout()`.

## Control Flow
Callers use `get_dot_command_size()` to validate or size outgoing/incoming buffers. `get_dot_command_timeout()` returns extended timeout for selected long-running commands `6.3.1`, `7.1`, and `8.x`, otherwise normal timeout.

## State and Persistence
No state is stored. The packed header describes transient command buffers exchanged with the service processor.

## Dependencies and Integration Points
The header depends on `IBMASM_CMD_TIMEOUT_*` constants from `ibmasm.h` and is consumed by command, filesystem, heartbeat, and low-level message code.

## Risks and Edge Cases
The inline size helper performs no overflow checking on command and data sizes. Timeout classification assumes command bytes are present according to `command_size`; callers must validate buffer length first.

## Test Signals
Unit-style tests can feed representative headers to verify size and timeout selection, including short buffers, maximum data sizes, and long-running command patterns.
