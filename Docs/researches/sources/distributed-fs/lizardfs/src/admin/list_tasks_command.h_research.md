<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_tasks_command.h

## Purpose
Declares the task listing command.

## Important APIs, Types, and Functions
`ListTasksCommand` overrides `name`, `usage`, and `run`; it does not declare custom supported options.

## Control Flow, State, and Persistence
No state is defined in the header.

## Dependencies and Integration Points
Includes base command and `common/server_connection.h`, though implementation handles connection details.

## Risks and Test Signals
Risks include unnecessary include coupling and lack of supported-options override. Build and command dispatch tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.h -->
