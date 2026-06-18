# sources/distributed-fs/coda/coda-src/venus/local_fso.cc

Purpose: provides local-repair related `fsobj` helpers for display names, local-object flags, CML lookup by transaction id, repair-mode mutation wrappers, and local version-vector assignment.

Important APIs and flow: `SetComp` replaces the recoverable component string, and `GetComp` returns it or a fid string fallback. `SetLocalObj`/`UnsetLocalObj` toggle the local flag. `FinalCmlent` scans `mle_bindings` to return the last CML entry for an IOT transaction id. `RepairStore`, `RepairSetAttr`, `RepairCreate`, `RepairRemove`, `RepairLink`, `RepairRename`, `RepairMkdir`, `RepairRmdir`, and `RepairSymlink` capture current user/time and call the corresponding disconnected operation with `prepend=1`, meaning the repair path logs the action without applying second-class local state again. `SetLocalVV` directly writes `stat.VV`.

State and persistence: component strings, local flags, version vectors, and repair log side effects are recoverable. The repair wrappers rely on transactions opened by the disconnected methods they call.

Dependencies and integration: depends on CML bindings, `Disconnected*` mutation methods from CFS call files, `VprocSelf` user context, RVM macros, and repair replay in `local_cml.cc`.

Risks and test signals: risks include component string ownership, asserting when no final CML entry exists, misuse of repair wrappers outside already-updated local state, and direct local VV updates that bypass server validation. Tests should cover name changes, local flag transitions, final CML lookup with multiple tids, each repair wrapper’s prepend behavior, and local VV repair updates.
