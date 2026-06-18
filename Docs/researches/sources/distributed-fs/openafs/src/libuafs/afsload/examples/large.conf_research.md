## sources/distributed-fs/openafs/src/libuafs/afsload/examples/large.conf

Purpose: Larger afsload scenario that exercises create, read, copy, concatenate, truncate, append, rename, hard-link, symlink, failure expectation, cleanup, and directory removal across multiple nodes.

Important structure: Starts with `nodeconfig` applying `afsconfig` and `logfile` to all nodes, then a sequence of `step` blocks. It uses wildcard node ranges, specific node ids, named step `"read newly created file"`, and actions from `AFS::Load::Action`.

Control flow: All nodes enter `/afs/.localcell/afsload`, node 0 creates a scratch directory, all nodes enter it, several nodes create files, all nodes validate reads, node 0 copies 1M from `/dev/urandom` into AFS, all nodes read multiple files, node 1 mutates `foo`, subsequent steps validate rename/link/symlink semantics, expected ENOENT is asserted after unlinking the hard-link target, and cleanup removes generated files and directory.

State and persistence: Creates and removes a `scratch` directory under the configured AFS path, uses `/tmp/afsload/cache.$RANK` and logs `/tmp/afsload/log.$RANK`, and reads local `/dev/urandom`.

Dependencies and integration: Depends on all relevant action classes, working AFS write permissions, cache directories already existing, and at least nodes 0, 1, and 2 being present for node-specific steps.

Risks: Not isolated if a previous failed run leaves `scratch` or files behind. Uses `.localcell` and assumes writable `/afs/.localcell/afsload`. The `1M` random copy may be slow or nondeterministic in timing.

Test signals: Good integration test for afsload parser and runtime, especially multi-node synchronization, link semantics, negative assertions, and cleanup reliability.
