<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.h -->
# sources/distributed-fs/lizardfs/src/admin/stop_task_command.h

## Purpose
Declares the stop-task admin command.

## Important APIs, Types, and Functions
`StopTaskCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared here.

## Dependencies and Integration Points
Includes base command and `common/server_connection.h`; implementation uses authenticated task protocol.

## Risks and Test Signals
Risk is declaration drift and cancellation side effects. Build plus task lifecycle integration tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.h -->
