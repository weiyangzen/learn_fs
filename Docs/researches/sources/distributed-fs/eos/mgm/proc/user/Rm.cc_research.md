# sources/distributed-fs/eos/mgm/proc/user/Rm.cc

Purpose: implements legacy removal command `ProcCommand::Rm()` for file deletion, wildcard deletion, recursive directory deletion, recycle-bin moves, and forced removal by root.

Important APIs and types: accepts `mgm.path`, `mgm.file.id`, `mgm.container.id`, `mgm.option`, and `mgm.deletion`; uses `GetPathFromFid`, `GetPathFromCid`, path mapping and token macros, POSIX regex for wildcard deletion, `XrdMgmOfsDirectory`, `gOFS->_exists`, `_find`, `_rem`, `_remdir`, `_attr_get`, `_stat`, `RecycleEntry`, and recycle constants.

Control flow: the command resolves file/container IDs or a path, maps and validates it, strips force for non-root, expands wildcard deletion by listing and regex matching, and checks existence. Non-recursive deletes call `_rem` for each target. Recursive deletes require a confirmation marker for shallow paths, collect the subtree with `_find`, then either simulate deletes and move the root into recycle garbage when recycle attributes are configured, or delete files and directories deepest-first.

State and persistence: mutates namespace metadata and possibly recycle-bin metadata. With recycle configured it preserves deleted trees through `RecycleEntry::ToGarbage`; with force or no recycle it deletes directly.

Dependencies and integration: legacy wrapper around the MGM OFS delete, recursive find, recycle, and quota-related deletion accounting paths.

Risks: the container-id branch calls `spath.c_str()` instead of assigning the resolved path, which appears to drop CID resolution. Wildcard handling only looks for `*` and uses regex after ad hoc conversion. Recursive shallow-path protection depends on `mgm.deletion=deep`. Tests should cover file ID and container ID deletion, force stripping, wildcard match/no-match behavior, recursive confirmation, recycle simulation failure, version directory exclusion, direct deepest-first deletion, ENOENT handling, and token-scoped removal.
