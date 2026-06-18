# sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.hh

Purpose: Declares `FsckCmd`, the `IProcCommand` implementation for protobuf fsck administration.

Important APIs/types/functions: The class constructor accepts `RequestProto` and `VirtualIdentity` and passes `false` to the base command. `ProcessRequest()` returns a full `ReplyProto`. When `EOS_GRPC_GATEWAY` is enabled, a second `ProcessRequest()` writes streamed replies to a gRPC `ServerWriter`.

Control flow: The header defines the unary and optional streaming entry points only; subcommand branching is contained in the implementation. The streaming overload exists to support REST/gRPC gateway paths without changing the command object's request and identity inputs.

State and persistence behavior: The class has no own persistent members beyond inherited request/identity. All fsck state is maintained in `gOFS->mFsckEngine` and FST endpoints.

Dependencies and integration points: Includes `Fsck.pb.h`, `IProcCommand.hh`, EOS namespace definitions, and optionally gateway gRPC generated headers. Used by console/gateway command routing for `FsckProto` requests.

Risks: Conditional compilation means gateway builds can diverge from normal builds. Duplicated overload semantics require tests in both build configurations.

Test signals: Compile both with and without `EOS_GRPC_GATEWAY`, verify command factory construction, unary return values, and streamed reply emission for each subcommand.
