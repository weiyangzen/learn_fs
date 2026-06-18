# sources/distributed-fs/eos/mgm/proc/user/RouteCmd.hh

Purpose: declares `RouteCmd`, the protobuf-backed route management command.

Important APIs and types: derives from `IProcCommand`, includes `Route.pb.h`, `ProcCommand.hh`, `IContainerMD.hh`, and `<list>`, constructs with `RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, and declares private subcommand helpers for list, link, and unlink.

Control flow: public dispatch is through `ProcessRequest`; helper signatures show each subcommand mutates a shared `ReplyProto`.

State and persistence: no direct data fields are declared. Implementation mutates routing and config state.

Dependencies and integration: command is not marked in the constructor as needing the same async/path behavior as some other commands (`IProcCommand(..., false)`), which is relevant to routing commands that are not ordinary namespace operations.

Risks: unused includes may hide tighter coupling than needed. Tests should compile command registration and exercise each helper through protobuf requests rather than direct private calls.
