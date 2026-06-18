# sources/distributed-fs/glusterfs/xlators/meta/src/graphs-dir.c

## Purpose
Implements the meta `graphs` directory, exposing the active graph link and one directory per known graph UUID.

## Important APIs, Types, and Functions
- `graphs_dir_dirents` includes `active` symlink.
- `graphs_dir_fill()` counts `this->ctx->graphs`, allocates dirents, and creates graph directory entries named by `graph_uuid` using `meta_graph_dir_hook`.
- `graphs_dir_ops` combines fixed and dynamic dirents.
- `meta_graphs_dir_hook()` attaches ops to the inode.

## Control Flow
Lookup/hook sets directory ops; readdir uses fixed plus dynamic graph entries.

## State and Persistence
Reads runtime graph list; no owned persistent state.

## Dependencies and Integration Points
Depends on active link and graph directory hooks, GlusterFS context graph list, and meta directory machinery.

## Risks
Graph list mutation during directory fill would require safety from surrounding graph/context lifecycle. Allocated dynamic names must be freed by meta core.

## Test Signals
Reading meta graphs directory should show `active` and each graph UUID directory.
