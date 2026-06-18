# sources/distributed-fs/glusterfs/xlators/meta/src/subvolume-link.c

Purpose: implements symlinks in an xlator's `subvolumes` directory. Each numeric entry points to a child translator by relative path.

Important APIs/types/functions: `subvolume_link_fill()` formats `../../<child-name>`. `meta_subvolume_link_hook()` parses the numeric dirent name with `strtol()`, walks the parent xlator's `children` list to that index, stores the selected child `xlator_t *`, and attaches `subvolume_link_ops`.

Control flow: `subvolumes-dir.c` creates numeric symlink entries. Lookup of one entry calls this hook; readlink invokes `subvolume_link_fill()`.

State and persistence behavior: stores a live child xlator pointer in inode context and persists nothing. Link target is generated on demand and cached per fd/readlink call by default logic.

Dependencies and integration points: depends on xlator child-list ordering and context propagated by `subvolumes-dir.c`.

Risks and edge cases: invalid numeric names or child-list changes can leave `subvol` null, and fill then dereferences it. The relative path assumes the meta tree layout remains `xlator/subvolumes/N -> ../../name`.

Test signals: readlink for every child index, behavior with no children, graph reload while entries are open, and invalid manual lookup names.
