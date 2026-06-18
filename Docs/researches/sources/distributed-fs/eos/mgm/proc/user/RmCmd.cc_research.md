# sources/distributed-fs/eos/mgm/proc/user/RmCmd.cc

Purpose: implements protobuf-backed removal as `RmCmd::ProcessRequest()`, covering path, file ID, container ID, detached metadata cleanup, globbing, recursive deletion, recycle-bin moves, and workflow bypass.

Important APIs and types: uses `RmProto`, `ReplyProto`, `NamespaceMap`, `PROC_MVID_TOKEN_SCOPE`, `IsOperationForbidden`, `Glob`, `XrdMgmOfsDirectory`, `gOFS->_exists`, `_find`, `_rem`, `_remdir`, `_attr_get`, `_stat`, `RemoveDetached`, `RecycleEntry`, and recursive stall macros.

Control flow: it first resolves path or ID. If an ID has no path and caller is root, it attempts `RemoveDetached`; non-root is denied. It maps namespace aliases, applies operation-forbidden checks, strips bypass-recycle force from non-root, optionally expands globbing, validates existence, clears recursive for files and globbed directory contents, and then either recursively collects a subtree or deletes direct targets. Recursive recycle mode performs simulated file and directory removals before moving the root to garbage; direct mode deletes files then directories deepest-first and passes `noworkflow` to file removal.

State and persistence: mutates namespace and possibly recycle metadata. `noworkflow` and `bypassrecycle` alter side effects in lower layers. Detached removal can delete namespace objects not reachable by path.

Dependencies and integration: this is the modern console command path for deletion, integrating with access policy, token scope, recycle, and namespace service edge cases.

Risks: recursive `_find` is requested with `E2BIG` failure behavior and can reject large trees. `ret_c |= errno` can produce combined error values for multiple direct failures. Globbing disables recursive deletion for matched entries. Tests should cover detached root-only cleanup, path mapping, operation forbidden errors, no-globbing, empty glob returning ENOENT, recycle simulation, direct recursive delete with `noworkflow`, force stripping, file versus directory recursive flags, and E2BIG tree limits.
