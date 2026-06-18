# sources/distributed-fs/lizardfs/src/master/filesystem_dump.cc

## Purpose
`filesystem_dump.cc` implements human-readable metadata dumping for the `METARESTORE` build. It prints nodes, edges, free inode records, and xattrs in a line-oriented diagnostic format.

## Important APIs and control flow
All functions are under `#ifdef METARESTORE`. `fs_dumpnode` prints one node with type, inode, goal, extra mode bits, permissions, uid/gid, timestamps, trash time, and type-specific payload: device major/minor, symlink path, or file length/chunk/session lists. `fs_dumpedge` prints directory, trash, reserved, or null edges. `fs_dumpnodes` walks all node hash buckets. `fs_dumpedgelist` overloads dump normal directory entries, trash entries, and reserved entries. `fs_dumpedges` recursively walks directory edges from root. `fs_dumpfree` iterates `gMetadata->inode_pool`. `xattr_dump` walks xattr hash buckets. `fs_dump` calls these in node, edge, trash/reserved, free-inode, and xattr order.

## State and persistence behavior
The dump is read-only with respect to metadata state. It exposes transient in-memory structures after metadata load or changelog replay, including detached trash/reserved paths and active open session ids stored on file nodes.

## Dependencies and integration points
The file depends on freenode/inode pool iteration, metadata globals, node lookup helpers, name escaping, and xattr hash tables. It is a recovery/debugging surface rather than a master runtime dependency.

## Risks and test signals
The output format is likely consumed by humans or recovery tests, so changing delimiters, escaping, or type letters can break tooling. Tests should run metarestore dumps for each node type, long or escaped names, sparse file chunk lists, reserved/trash entries, free inode records, and xattr entries. Because traversal is recursive for directory edges, corrupt cycles would be dangerous and should be caught earlier by metadata validation.
