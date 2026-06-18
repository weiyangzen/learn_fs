<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.h -->
# sources/distributed-fs/lizardfs/src/admin/manage_locks_command.h

## Purpose
Declares the lock-management admin command.

## Important APIs, Types, and Functions
`ManageLocksCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No state lives in the header; destructive behavior is in the implementation.

## Dependencies and Integration Points
Includes the base command header. Implementation integrates master lock protocol and authentication.

## Risks and Test Signals
Risk is declaration drift and the command's privileged nature hidden behind a simple interface. Authenticated integration tests are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.h -->
