# sources/distributed-fs/eos/mgm/proc/user/DfCmd.hh

## Purpose

`DfCmd.hh` declares the protobuf command class for `df` requests. It provides the type boundary between console `DfProto` requests and the `IProcCommand` asynchronous command framework.

## Important APIs, Types, and Functions

`class DfCmd : public IProcCommand` exposes a constructor taking `eos::console::RequestProto&&` and `VirtualIdentity&`, a default destructor, and `ProcessRequest() noexcept`. The constructor passes `false` as the final `IProcCommand` argument, indicating the command does not require write behavior.

## Control Flow

There is no local control flow beyond construction and virtual dispatch. The command framework calls `ProcessRequest()` implemented in `DfCmd.cc`.

## State and Persistence

The class stores no additional fields beyond inherited request and identity state. It declares no persistent behavior.

## Dependencies and Integration Points

The header depends on `mgm/Namespace.hh`, `proto/Df.pb.h`, `mgm/proc/ProcCommand.hh`, and `IContainerMD.hh`. It integrates with the same protobuf command framework used by `AclCmd`.

## Risks and Test Signals

The main risks are API compatibility and command classification. If `Df` ever needs authorization, path prefetching, or write-side effects, the constructor flag and implementation must change. Test signals are compile-time protobuf compatibility and runtime dispatch of `RequestProto.df()` into a successful reply.
