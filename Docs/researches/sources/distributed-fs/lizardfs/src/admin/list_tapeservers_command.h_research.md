<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.h

## Purpose
Declares the tapeserver listing command.

## Important APIs, Types, and Functions
`ListTapeserversCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No runtime state is declared here.

## Dependencies and Integration Points
Includes `admin/lizardfs_admin_command.h`; implementation integrates tapeserver protocol.

## Risks and Test Signals
Risk is minimal declaration drift. Build and live-protocol tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.h -->
