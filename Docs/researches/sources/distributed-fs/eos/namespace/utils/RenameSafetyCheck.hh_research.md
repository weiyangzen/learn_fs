# sources/distributed-fs/eos/namespace/utils/RenameSafetyCheck.hh

## Purpose
Defines `isSafeToRename()`, a namespace consistency guard that prevents moving a directory under itself or under one of its descendants. It is a critical check for directory rename operations.

## Important APIs, types, and functions
`bool isSafeToRename(IView* view, IContainerMD* source, IContainerMD* target)` walks target ancestry through `IContainerMDSvc`. It uses `getContainerMDSvc()`, `getContainerMD(parentId)`, container id comparisons, and `throw_mdexception(EFAULT, msg)` on suspected namespace corruption.

## Control flow
The function rejects `source == target`, then starts at the target's parent and walks upward until root id `1`. If it sees the exact source object or a different object with the same id, it rejects the rename. A hard cap of 1024 iterations logs and throws for potential parent loops.

## State and persistence
No metadata is modified. The function assumes source/target or the global view mutex are at least read-locked by the caller, so correctness depends on external locking while parent links are inspected.

## Dependencies and integration points
Integrates with `IView`, `IContainerMD`, `IContainerMDSvc`, namespace exceptions, and EOS logging. It is used by namespace rename paths before committing parent-child changes.

## Risks and test signals
Null service returns, missing parents, and concurrent parent changes could crash or misclassify without caller locking. Tests should cover root, self-renames, moving into descendants, safe sibling moves, duplicate id object detection, and artificial parent loops exceeding 1024 iterations.
