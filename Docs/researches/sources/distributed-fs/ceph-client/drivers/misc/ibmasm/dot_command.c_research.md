# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/dot_command.c

## Purpose
`dot_command.c` dispatches incoming service-processor dot commands and sends built-in driver VPD and OS state dot commands during driver initialization/removal.

## Important APIs, Types, and Functions
Public functions are `ibmasm_receive_message()`, `ibmasm_send_driver_vpd()`, and `ibmasm_send_os_state()`. `struct os_state_command` packages the OS-state command. It uses `struct dot_command_header` and helpers from `dot_command.h`.

## Control Flow
Incoming interrupt data is ignored if empty or malformed, clamped to the inbound message size, and dispatched by header type to event, command-response, or heartbeat handlers. Driver VPD creates a write dot command `4.3.5.10` with the IBMASM driver VPD string, executes it, waits for the normal timeout, and returns `-ENODEV` if incomplete. OS state sends command `4.3.6` with up/down data and waits similarly.

## State and Persistence
The file itself stores no long-lived state. The VPD and OS-state commands temporarily allocate `struct command` objects and affect service-processor state, especially heartbeat behavior.

## Dependencies and Integration Points
It integrates command execution, event handling, heartbeat handling, and module probe/remove. It depends on dot-command wire layout and service-processor command queues.

## Risks and Edge Cases
Incoming command size is trusted after only header-based calculation and clamping; malformed command/data sizes can change dispatch size. `strcat()` into the VPD data buffer relies on the zeroed command allocation and fixed buffer sizing. Unknown message types are logged but otherwise dropped.

## Test Signals
Validate dispatch for event/response/heartbeat, malformed zero or oversized sizes, VPD command buffer bytes, OS up/down during probe/remove, and timeout handling when the service processor does not respond.
