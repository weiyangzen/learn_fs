# sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.hh

Purpose: declares `RecycleCmd`, the protobuf-backed recycle command handler.

Important APIs and types: derives from `IProcCommand`, includes `proto/Recycle.pb.h` and `ProcCommand.hh`, constructs with `RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, and overloads `ProcessRequest(std::vector<std::map<std::string, std::string>>*)` for callers that need structured listing rows.

Control flow: the header defines the public command entry points only; subcommand dispatch is implemented in the `.cc`.

State and persistence: no direct state beyond inherited command data. Mutations are performed by recycle subsystem calls in the implementation.

Dependencies and integration: connects console recycle protobufs to the MGM asynchronous command framework and exposes a structured-listing integration point.

Risks: the vector overload is only meaningful for `ls` and falls back to the normal method otherwise, so tests should validate both call forms. Header includes `ProcCommand.hh` rather than only `IProcCommand` because `IProcCommand` is made available there; compile tests should catch include fragility.
