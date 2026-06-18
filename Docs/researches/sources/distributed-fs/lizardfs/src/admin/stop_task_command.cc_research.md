<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/stop_task_command.cc

## Purpose
Implements `lizardfs-admin stop-task`, cancelling a currently running master task by ID.

## Important APIs, Types, and Functions
Defines command methods. It parses the task ID with `std::stoi(..., base 0)`, sends `cltoma::stopTask::build(msgid, task_id)`, and deserializes `matocl::stopTask`.

## Control Flow, State, and Persistence
`run` requires host, port, and task ID. Invalid task ID text prints an error and returns without nonzero status. After authentication it sends cancellation request and prints success or not-found text. The server-side effect is cancellation of matching background task.

## Dependencies and Integration Points
Depends on `RegisteredAdminConnection`, task protocol, and IDs shown by `list-tasks`.

## Risks and Test Signals
Risks include invalid ID returning success status from the process, `std::out_of_range` not caught, no nonzero exit on not-found status, direct protocol message ID fixed to zero, and operational side effects of cancelling tasks like metadata saves. Test signals are decimal/hex IDs, invalid and out-of-range IDs, successful cancellation, not-found status, bad password, and consistency with `list-tasks` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.cc -->
