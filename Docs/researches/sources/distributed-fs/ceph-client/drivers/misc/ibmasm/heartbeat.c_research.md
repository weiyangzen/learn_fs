# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/heartbeat.c

## Purpose
`heartbeat.c` responds to service-processor heartbeats and registers a panic notifier so heartbeats stop after kernel panic, allowing the service processor to reboot the system if expected.

## Important APIs, Types, and Functions
Public functions are `ibmasm_register_panic_notifier()`, `ibmasm_unregister_panic_notifier()`, `ibmasm_heartbeat_init()`, `ibmasm_heartbeat_exit()`, and `ibmasm_receive_heartbeat()`. Internal state is `suspend_heartbeats` and `panic_notifier`.

## Control Flow
Init allocates a reusable heartbeat command buffer. On heartbeat message receipt, if suspension is not active, the driver copies the incoming dot command into the heartbeat command buffer, changes the type to `sp_write`, marks it pending, and executes it as a response. Exit waits for any heartbeat command, sets suspension, and drops the command reference. Panic notification sets suspension without further cleanup.

## State and Persistence
Heartbeat state is per service processor through `sp->heartbeat` plus global `suspend_heartbeats`. Once set, suspension remains until module reload.

## Dependencies and Integration Points
It depends on command execution, dot-command headers, the panic notifier chain, and low-level interrupt dispatch through `ibmasm_receive_message()`.

## Risks and Edge Cases
`suspend_heartbeats` is global, so one panic or exit affects all service processors. Reusing one command object for repeated heartbeats depends on serialized command execution and service-processor timing. Panic-path behavior intentionally stops responding rather than trying to clean up.

## Test Signals
Validate heartbeat response bytes, repeated heartbeats under load, module removal waiting for pending heartbeat, panic notifier registration/unregistration, and behavior with multiple service processors.
