# sources/distributed-fs/glusterfs/xlators/meta/src/xlator-dir.c

Purpose: defines the virtual directory layout for one translator and provides hooks to bind either a named graph xlator or the process root xlator.

Important APIs/types/functions: `xlator_dir_dirents` exposes `view`, `type`, `name`, `subvolumes`, `options`, `private`, `history`, `meminfo`, and `profile`. `meta_xlator_dir_hook()` retrieves a graph pointer from the parent inode, searches `graph->first` by `loc->name`, stores the matching `xlator_t *`, and attaches `xlator_dir_ops`. `meta_root_hook()` binds `this->ctx->root` as the special root xlator directory.

Control flow: graph directories use `meta_xlator_dir_hook()` for each translator child. Once an xlator directory is looked up, its fixed dirents route to specialized files and directories that all inherit the xlator context. The top-level `root` entry bypasses graph-name lookup and directly uses the process root xlator.

State and persistence behavior: stores live `xlator_t *` pointers in inode context. No persistent data is written.

Dependencies and integration points: depends on graph hooks that supply `glusterfs_graph_t *`, `xlator_search_by_name()`, and all child hook declarations in `meta-hooks.h`.

Risks and edge cases: failed name lookup can store null xlator context, causing later child fills to crash. Graph replacement can invalidate stored xlator pointers. The fixed directory layout is a user-visible diagnostic ABI.

Test signals: lookup every xlator by graph name, traverse every fixed child, test special `.meta/root`, and validate behavior after graph reload or missing names.
