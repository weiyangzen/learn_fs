# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/command.c

## Purpose
`command.c` serializes dot-command execution to the IBM ASM service processor. It allocates command buffers, queues commands, sends one active command through the low-level I2O path, waits for responses, and advances queued work.

## Important APIs, Types, and Functions
Public functions are `ibmasm_new_command()`, `ibmasm_free_command()`, `ibmasm_exec_command()`, `ibmasm_wait_for_response()`, and `ibmasm_receive_command_response()`. Internal helpers are `enqueue_command()`, `dequeue_command()`, `do_exec_command()`, and `exec_next_command()`.

## Control Flow
Callers allocate a command with bounded buffer size, fill it, and call `ibmasm_exec_command()`. If no command is active, it becomes `sp->current_command`, gains a reference, and is sent with `ibmasm_send_i2o_message()`; otherwise it is appended to `sp->command_queue`. Responses from interrupt context copy data into the current command buffer, mark status complete, wake waiters, drop the active reference, and dispatch the next queued command. Send failure marks the current command failed and also advances the queue.

## State and Persistence
State is in `struct command` buffers, krefs, wait queues, statuses, and the service processor's current/queued command pointers. `command_count` is debug-only global state. Nothing persists beyond memory.

## Dependencies and Integration Points
The file depends on `ibmasm.h`, low-level I2O send support, service-processor spinlock, wait queues, krefs, and dot-command callers from filesystem, heartbeat, and setup code.

## Risks and Edge Cases
`ibmasm_wait_for_response()` ignores the return value from interrupted waits, so callers rely on status inspection. `ibmasm_free_command()` unconditionally `list_del()`s the queue node, making initialization and list state important. Response handling assumes only one current command and that response size fits by truncation to the command buffer.

## Test Signals
Exercise sequential command ordering, queued command advancement after success and send failure, timeout behavior, interrupted waits, oversized buffer rejection, kref balance under filesystem close, and response truncation.
