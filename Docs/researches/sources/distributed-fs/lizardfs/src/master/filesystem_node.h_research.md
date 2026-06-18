# sources/distributed-fs/lizardfs/src/master/filesystem_node.h

## Purpose
`filesystem_node.h` declares the low-level node utility API used by filesystem operations, load/store code, periodic scanners, and metarestore diagnostics.

## Important APIs
Inline helpers include `fsnodes_hash`, `fsnodes_lookup`, `fsnodes_id_to_node`, `fsnodes_id_to_node_verify`, and `fsnodes_update_ctime`. The non-inline API covers escaping names, purging/undeletion, detached trash/reserved serialization, path construction, attribute filling, session verification, operation-context node lookup, name/access checks, length and ownership changes, node creation, stats propagation, link/unlink/remove-edge operations, append/chunk/goal/trashtime/eattr recursion, ACL operations, directory serialization, file check summaries, tape enqueueing, and size/parent helpers.

## Control flow and state behavior
The API separates fast inline lookup/check helpers from mutation helpers that maintain global metadata invariants. `fsnodes_update_ctime` has special trash handling: changing ctime affects `TrashPathKey`, so it removes and reinserts the trash path entry around the timestamp update.

## Dependencies and integration points
The header depends on node types, metadata globals, protocol directory entry types, named inode entries, and FsContext. It is included by operations, dump, checksum, periodic, freenode, and metadata code.

## Risks and test signals
Typed lookup verification uses `assert`, so production builds can still receive null or wrong-type pointers if callers misuse unchecked functions. Tests should use debug builds to catch type invariants, and operation-level tests should validate public status-code behavior for missing/wrong-type inodes. Any new node mutation helper should be checked for checksum, stats, quota, xattr, ACL, chunk, and detached-container side effects.
