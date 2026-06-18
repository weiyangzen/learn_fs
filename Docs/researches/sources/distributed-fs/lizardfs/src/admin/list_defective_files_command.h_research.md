<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.h

## Purpose
Declares the defective-files listing command.

## Important APIs, Types, and Functions
`ListDefectiveFilesCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No state or helper logic lives in the header.

## Dependencies and Integration Points
Includes the base admin command and `common/server_connection.h`, although the connection type is only needed in the implementation.

## Risks and Test Signals
Risks include unnecessary include coupling and declaration drift. Build tests and CLI option parsing tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.h -->
