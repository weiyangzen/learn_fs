<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_goals_command.h

## Purpose
Declares the goal listing admin command.

## Important APIs, Types, and Functions
`ListGoalsCommand` overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
The header stores no state or helpers.

## Dependencies and Integration Points
Includes `admin/lizardfs_admin_command.h`; implementation integrates the goal protocol and output escaping.

## Risks and Test Signals
Risk is declaration drift. Build and CLI output tests for all display modes are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.h -->
