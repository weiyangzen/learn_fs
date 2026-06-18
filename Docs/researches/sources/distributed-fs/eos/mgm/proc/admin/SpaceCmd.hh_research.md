# sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.hh

## Purpose
`SpaceCmd.hh` declares the protobuf-backed EOS space administration command class and its private subcommand handler interface.

## Important APIs, Types, And Functions
`class SpaceCmd : public IProcCommand` accepts a request and virtual identity and overrides `ProcessRequest() noexcept`. Private methods cover space listing, tracker/status/set/node-set/node-get/reset/define/config/quota/rm/inspector/groupbalancer/groupdrainer operations. `FsSpace` is forward-declared for `GroupBalancerStatusCmd()`.

## Control Flow
The header establishes a one-handler-per-protobuf-subcommand layout. Most handlers mutate a shared `ReplyProto&`; a few stateless helpers are `static` (`TrackerSubcmd`, `ResetSubcmd`, `InspectorSubcmd`) because they do not need command instance fields. Group balancer and group drainer handling is split into a top-level command method plus a status helper.

## State, Persistence, And Dependencies
The class has no extra data members beyond `IProcCommand`. It depends on generated `Space.pb.h`, MGM namespace macros, and the proc command base. Persistence and subsystem reconfiguration are delegated to the implementation.

## Integration Points
`SpaceCmd` is the modern protobuf command layer for space operations. Its signatures couple console protobuf schema directly to MGM filesystem-space internals while hiding implementation detail from the dispatcher.

## Risks
The broad private handler list reflects a large operational surface in one class. Static handlers can still mutate globals, so their static-ness should not be read as safety. Generated protobuf changes affect this header directly.

## Test Signals
Compile every generated protobuf type referenced here. Runtime dispatch tests should verify every `SpaceProto` oneof reaches the expected handler and that static and non-static handlers produce consistent reply status fields.
