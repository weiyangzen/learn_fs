<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rename.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rename.cc

Purpose: validates and replays remote rename operations during directory resolution, including conflict detection and target cleanup.

Important APIs/control flow: exported `CheckAndPerformRename` calls `CheckResolveRenameSemantics` to validate source/target parent directories, source name binding, source object existence, parent pointers, target existence expectations, target parent pointer, and target remove/update conflicts. On success it calls `CleanRenameTarget` for non-empty directory targets, replays `PerformRename`, adjusts disk usage for deleted targets, and spools a `ResolveViceRename_OP` log. On `EINCONS`, it either returns a hinted directory fid or marks/merges affected inconsistency entries.

State/persistence: mutates vnodes/directories through `PerformRename`, `TreeRmBlk` subtree removal, `MarkObjInc`, disk usage updates, and resolution log spooling. Uses in-memory `inclist`/`newinclist` for conflict propagation.

Dependencies/integration: relies on operation semantics (`CheckRenameSemantics`, `PerformRename`), directory handles, `vlist`, RU conflict helpers, `treeremove`, `resstats`, and `ops.cc` logging.

Risks/test signals: conflict outcomes depend on complete `vlist` population and correct parent pointer lookup. Hinted resolution avoids marking objects, which can change retry behavior. Test same-parent and cross-parent renames, pre-existing/deleted targets, non-empty directory overwrite, file and directory RU conflicts, and hinted resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rename.cc -->
