# sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.hh

Purpose: Declares `MonitCmd`, the protobuf `IProcCommand` for MGM monitoring configuration.

Important APIs/types/functions: The class constructor stores `RequestProto` and `VirtualIdentity` through the base. `ProcessRequest()` is the public command entry point. Private helpers return `ReplyProto` by value for config dispatch, config list/set, enable, and disable.

Control flow: The declaration models monitoring as a small command tree with nested config subcommands. Returning `ReplyProto` by value lets helper methods short-circuit validation failures cleanly.

State and persistence behavior: The class has no own persistent state. Implementation reads and writes global monitoring config through `FsView` and applies it through `gOFS`.

Dependencies and integration points: Includes `IProcCommand.hh` and generated `Monit.pb.h`. It is used by MGM protobuf command routing for monitoring requests.

Risks: Header and proto oneof schema must evolve together. The small helper surface makes unsupported future subcommands return `EINVAL` until implemented.

Test signals: Construction, dispatch to config/enable/disable, unsupported oneof handling, and compile compatibility with `Monit.pb.h`.
