# sources/distributed-fs/eos/mgm/proc/admin/FsCmd.hh

Purpose: Declares the protobuf `FsCmd` command object used by MGM admin processing for filesystem operations.

Important APIs/types/functions: `FsCmd` derives from `IProcCommand`, constructs with `RequestProto` and `VirtualIdentity`, and overrides `ProcessRequest()`. Private helpers mirror all supported `FsProto` subcommands: `List`, `Config`, `Mv`, `Rm`, `DropDeletion`, `DropGhosts`, `Add`, `Boot`, `DumpMd`, `Status`, `DropFiles`, `Compare`, and `Clone`. `DisplayModeToString()` maps list display enums to `FsView` format selectors. `SemaphoreProtectedProcDumpmd()` wraps legacy dumpmd access. `SizeOfArray()` is a small constexpr helper. `mSemaphore`, `mOut`, `mErr`, and `mRetc` carry shared dump throttling and per-command response state.

Control flow: The header establishes a single command instance per request with private subcommand methods called by `ProcessRequest()`. The base constructor flag is `true`, indicating this command uses the asynchronous/proc command behavior configured by `IProcCommand`.

State and persistence behavior: The class itself owns only response buffers and return code. Persistent effects are implemented in the `.cc` via `FsView`, shared hashes, config engine, and namespace services. The static semaphore is process-wide and affects all `fs dumpmd` invocations.

Dependencies and integration points: Includes `IProcCommand`, `Namespace.hh`, and `ConsoleRequest.pb.h`, with XRootD types used in method signatures through included project headers. It is consumed by the MGM admin command factory for filesystem proto requests.

Risks: Because `mOut`, `mErr`, and `mRetc` are mutable command state, helper methods must consistently set them on all paths. Static semaphore lifecycle and early returns in the implementation are cross-request risks. Header declarations expose a broad private surface, so proto schema changes require synchronized updates here and in dispatch.

Test signals: Compile coverage for all proto subcommand signatures, construction through command factory, one response per command instance, and semaphore behavior across concurrent `DumpMd` calls.
