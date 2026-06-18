# sources/distributed-fs/eos/mgm/proc/user/RmCmd.hh

Purpose: declares the protobuf-backed `RmCmd` command.

Important APIs and types: derives from `IProcCommand`, includes `ConsoleRequest.pb.h`, constructs with `RequestProto&&` and `VirtualIdentity&`, and overrides `ProcessRequest() noexcept`.

Control flow: the header only defines construction and dispatch shape. All removal behavior is implemented in `RmCmd.cc`.

State and persistence: no direct state beyond inherited command request, identity, and async execution metadata. The implementation performs namespace mutations.

Dependencies and integration: part of the modern command framework, replacing or paralleling legacy `ProcCommand::Rm()`.

Risks: compile-time compatibility depends on `IProcCommand` and protobuf request schema. Tests should instantiate the command with representative `RmProto` requests and verify the implementation contract through `ReplyProto`.
