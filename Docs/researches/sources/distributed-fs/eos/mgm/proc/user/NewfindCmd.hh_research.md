# sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.hh

Purpose: declares `NewfindCmd`, the asynchronous protobuf-backed find command.

Important APIs and types: derives from `IProcCommand`, takes `eos::console::RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, optionally exposes a gRPC `ProcessRequest(ServerWriter<ReplyProto>*)`, and declares helpers `PrintFileInfoMinusM`, `ModifyLayoutStripes`, `ProcessAtomicFilePurge`, and `PurgeVersions`. It forward-declares `FindResult` and `eos::IFileMD`.

Control flow: the header establishes that normal command execution returns a `ReplyProto`, while streaming execution is compiled only under `EOS_GRPC`. Helper overloads route default output to `mOfsOutStream` or accept an explicit stream.

State and persistence: no state is declared beyond the inherited request, identity, and output streams. Mutating behavior is implemented in the `.cc` helpers for purge and layout changes.

Dependencies and integration: ties console protobuf requests to MGM command dispatch through `IProcCommand`, and conditionally to the WNC gRPC protobuf service.

Risks: templated private helpers are implemented in the `.cc`, which works because they are only instantiated there but limits reuse. Tests compile both `EOS_GRPC` and non-gRPC builds to catch signature drift, and should exercise helper call paths through public command requests.
