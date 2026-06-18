# sources/distributed-fs/glusterfs/xlators/meta/src/top-link.c

Purpose: implements a symlink exposing the top translator of a graph.

Important APIs/types/functions: `top_link_fill()` retrieves a `glusterfs_graph_t *` from inode context and formats the top xlator's name. `meta_top_link_hook()` installs `top_link_ops` and copies the parent graph context.

Control flow: graph directory modules expose a `top` link. Lookup binds graph context to the link inode; readlink asks `top_link_fill()` for the target.

State and persistence behavior: no persistent state. The symlink points to the top member of the graph snapshot stored in inode context.

Dependencies and integration points: depends on the graph context installed by graph-related hooks and on `graph->top` being a valid xlator pointer.

Risks and edge cases: null graph or top pointers crash fill. If graph topology changes while a fd/inode is cached, the target may become stale.

Test signals: readlink on graph top links for active and historical graphs, and behavior when graph top is absent in synthetic/test graphs.
