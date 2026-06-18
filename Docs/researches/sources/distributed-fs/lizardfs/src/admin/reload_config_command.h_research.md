<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.h -->
# sources/distributed-fs/lizardfs/src/admin/reload_config_command.h

## Purpose
Declares the reload-config admin command.

## Important APIs, Types, and Functions
`ReloadConfigCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared here.

## Dependencies and Integration Points
Includes base command header. Implementation uses authenticated admin protocol.

## Risks and Test Signals
Risk is declaration drift and live configuration side effects. Build plus authenticated integration tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.h -->
