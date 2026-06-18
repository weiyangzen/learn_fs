# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Find.inc

## Purpose

`Find.inc` implements recursive namespace search and clone-marker management for the MGM. It can traverse directories with permission checks, match attributes and file names, enforce non-admin result limits, produce maps of found directories/files, and handle special `sys.clone` operations for listing, marking, creating, and cleaning clone state.

## Important APIs, Types, and Functions

- `_cloneFoundItem` records found container/file ids and traversal depth for delayed clone output.
- `_clone_escape()` curl-escapes names containing spaces or percent signs.
- `_cloneResp()` converts collected clone ids back into path output or compact JSON records, including attributes and stat tuples.
- `_cloneMD()` finds or creates `/proc/.../clone/<id>` clone anchor directories.
- `_clone()` recursively marks, lists, or cleans clone metadata according to flags `>`, `=`, `-`, `+`, `?`, and `!`.
- `XrdMgmOfs::_find()` is the main recursive find implementation.

## Control Flow

For `key == "sys.clone"`, `_find` parses the clone flag and id, rejects limited users, loads the root container, calls `_clone`, and emits clone output through `_cloneResp`. Clone recursion can set or clear container/file clone ids, create clone anchor directories, remove cloned files/containers on cleanup, and collect output outside the large lock.

Normal find initializes a breadth/depth list of directories, obtains per-user directory/file limits from `Access::GetFindLimits()`, and marks non-root/non-admin/non-sudo users as limited. It then loops by depth until no more directories, max depth, limit, or termination. For each directory it optionally sleeps, prefetches children, checks POSIX/ACL read+browse permission, checks public access, skips version directories or ctime-too-new entries, and then scans child directories and files.

Directory matches can be by any attr matching wildcard key, exact key with `*` value, exact key/value, or no key. File matches can include symlink display, file-name wildcard matching, ctime filtering, and result limits. If no file results are found, it falls back to checking whether the original path was itself a file. It always includes the queried directory when accessible. If `out_error.getErrInfo() == E2BIG`, limited results become an error rather than a warning.

## State and Persistence Behavior

Normal find is read-only except for stats and optional access helper side effects. Clone mode mutates namespace metadata: clone ids and clone FST markers on containers/files, creation/removal of clone directories, removal of cloned files via `_rem`, metadata store updates through directory/file services, and FUSE refresh/deletion notifications. Clone cleanup can remove stored clone artifacts under the MGM proc path.

## Dependencies and Integration Points

Dependencies include namespace iterators, `Prefetcher`, `Acl`/`_access`, `_attr_ls`, `_attr_get`, `Access::GetFindLimits`, public access rules, recycle-bin helpers, JSONCPP, `FileId`, file/directory services, FUSE xcast, `_rem`, and `ThreadAssistant`. It integrates with shell/proc commands that need recursive listings and backup/clone workflows.

## Risks and Edge Cases

- Clone mode is highly stateful and bypasses normal user limits; only privileged identities should be able to use it.
- `_clone` deliberately releases and reacquires `eosViewRWMutex` around prefetch in some paths; lock ordering regressions can deadlock or race.
- Hard-link handling in `_cloneResp` suppresses zombie targets and rewrites metadata to target files; restore tooling depends on emitted `H`/`L` fields.
- Result limiting can truncate silently with warnings unless fail-if-limited mode is requested through `E2BIG`.
- Permission checks combine direct container access and `_access`; differences between those paths affect find visibility.
- Large trees can consume substantial memory in `found_dirs` and `found`.

## Test Signals

Tests should cover recursive traversal, max depth, no-files mode, attr wildcard and exact matching, file wildcard matching, symlink display, version-dir skip, ctime filters, public access denial, ACL fallback, per-user limits with warning and `E2BIG` failure, assistant termination, original-path-is-file fallback, JSON clone output, clone mark/list/cleanup flags, hard-link clone output, and FUSE/deletion side effects from clone cleanup.
