<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.h -->
# sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.h

## Purpose
Declares the shadow promotion admin command.

## Important APIs, Types, and Functions
`PromoteShadowCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No header state.

## Dependencies and Integration Points
Includes `common/server_connection.h` and base command header; implementation uses authenticated admin protocol.

## Risks and Test Signals
Risks are operational rather than structural. Build and HA integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.h -->
