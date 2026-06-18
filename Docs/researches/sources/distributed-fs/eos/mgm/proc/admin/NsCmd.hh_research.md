# sources/distributed-fs/eos/mgm/proc/admin/NsCmd.hh

## Purpose
`NsCmd.hh` declares the protobuf-backed namespace administration command class. It is the interface contract for the implementation in `NsCmd.cc`, exposing only `ProcessRequest()` publicly while keeping each namespace subcommand handler private.

## Important APIs, Types, And Functions
`class NsCmd : public IProcCommand` takes an rvalue `eos::console::RequestProto` and a `VirtualIdentity`, passes them to `IProcCommand`, and overrides `ProcessRequest() noexcept`. Private methods map directly to `NsProto` subcommands: `MutexSubcmd`, `StatSubcmd`, `MasterSubcmd`, `CompactSubcmd`, `TreeSizeSubcmd`, `QuotaSizeSubcmd`, `CacheSubcmd`, `DrainSubcmd`, `ReserveIdsSubCmd`, `BenchmarkSubCmd`, `TrackerSubCmd`, and `BehaviourSubCmd`. Helper methods are `BreadthFirstSearchContainers()`, `UpdateTreeSize()`, and `TextHighlight()`.

## Control Flow
The header establishes a single dispatch entry point. The implementation reads the request's namespace oneof case and calls the matching private method with the protobuf submessage and a mutable reply object. Tree-size repair uses the BFS helper to produce per-depth container id lists, then calls `UpdateTreeSize()` bottom-up.

## State, Persistence, And Dependencies
The declaration depends on `mgm/Namespace.hh`, generated `proto/Ns.pb.h`, `mgm/proc/ProcCommand.hh`, and namespace container metadata interfaces. It stores no command-specific members beyond inherited request and identity state. Persistence and locking obligations are implicit in helper comments, especially the note that `BreadthFirstSearchContainers()` assumes a write lock on `eosViewRWMutex`.

## Integration Points
`NsCmd` is consumed by the MGM proc command factory or dispatcher for console `ns` requests. Its protobuf signatures keep the command layer tied to `Ns.pb.h`, while its inheritance ties execution to the common asynchronous `IProcCommand` lifecycle and reply protocol.

## Risks
Because subcommands are private and broad in scope, testing has to enter through `ProcessRequest()` and build protobuf requests for every branch. The BFS helper comment says a write lock is assumed, but callers must enforce that convention; mismatch can produce metadata races. The header also exposes a large command surface in one class, increasing regression risk when generated protobuf fields change.

## Test Signals
Compile-time signals are generated protobuf compatibility and successful override of `ProcessRequest()`. Runtime signals are branch coverage for every `NsProto` subcommand, correct propagation of `retc/std_out/std_err`, and lock-sensitive tests around tree-size update helpers.
