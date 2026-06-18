# sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.hh

Purpose: Declares `NodeCmd`, the protobuf command object for MGM node administration.

Important APIs/types/functions: `NodeCmd` derives from `IProcCommand`, overrides `ProcessRequest()`, and declares helpers for `LsSubcmd`, `RmSubcmd`, static `StatusSubcmd`, `ConfigSubcmd`, `ConfigFsSpecific`, `SetSubcmd`, and `ProxygroupSubcmd`.

Control flow: The header captures the command tree represented by `NodeProto`: list, remove, status, config, set, and proxygroup. `ConfigFsSpecific()` separates node-level config from filesystem config changes that must be applied to every filesystem under selected nodes.

State and persistence behavior: No persistent members are declared. The implementation mutates global `FsView`, shared hashes, config engine, and filesystem config.

Dependencies and integration points: Includes `Namespace.hh`, generated `Node.pb.h`, and `ProcCommand.hh`. It is consumed by protobuf admin command routing and interacts with FST node state through the implementation.

Risks: Static `StatusSubcmd()` cannot use instance identity or JSON helpers unless passed explicitly, so status behavior is intentionally limited. Header signatures must track proto submessage names and generated namespace changes.

Test signals: Dispatch coverage for all declared helpers, static status behavior, config filesystem-specific path, unsupported oneof handling, and compile compatibility with generated `Node.pb.h`.
