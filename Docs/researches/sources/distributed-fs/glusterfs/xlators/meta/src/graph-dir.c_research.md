# sources/distributed-fs/glusterfs/xlators/meta/src/graph-dir.c

## Purpose
Implements a per-graph meta directory that exposes fixed graph files/links and one subdirectory per xlator in the graph.

## Important APIs, Types, and Functions
- `graph_dir_dirents` defines fixed `top` symlink and `volfile` file entries.
- `graph_dir_fill()` gets `glusterfs_graph_t` from inode meta ctx, counts graph xlators, allocates dynamic dirents, and creates one directory entry per xlator.
- `glusterfs_graph_lookup()` scans `this->ctx->graphs` by graph UUID.
- `meta_graph_dir_hook()` sets graph dir ops and stores the graph pointer in inode meta ctx.

## Control Flow
When a graph UUID directory is looked up, the hook resolves the graph and stores it. Directory reads include fixed entries plus dynamic xlator directories.

## State and Persistence
Stores a graph pointer in inode metadata context. Reads live graph list and xlator names.

## Dependencies and Integration Points
Depends on meta ctx helpers, graph list, xlator linked list, and hooks for `top`, `volfile`, and xlator dirs. Used by `graphs-dir.c` dynamic entries.

## Risks
`graph_dir_fill()` allocates `count` entries without an explicit null terminator in the dynamic array; correctness depends on meta core using returned count. Graph pointer lifetime must outlive inode ctx usage.

## Test Signals
Meta graph directory listing should show `top`, `volfile`, and every xlator in the graph.
