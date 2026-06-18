# sources/distributed-fs/ceph-client/fs/xfs/scrub/dirtree.h

Purpose: Defines shared directory-tree path tracking structures and APIs used by the directory tree scrubber and repairer.

Important APIs, types, and functions: Defines `struct xchk_dirpath_step` for one parent-link step, `enum xchk_dirpath_outcome` for scan and repair states, `struct xchk_dirpath` for an in-core path with seen-inode bitmap and xfarray indices, `struct xchk_dirtree_outcomes` for evaluation counts, and `struct xchk_dirtree` for global scan/repair state. Declares iteration macros and functions `xchk_dirtree_parentless()`, `xchk_dirtree_find_paths_to_root()`, `xchk_dirpath_append()`, and `xchk_dirtree_evaluate()`.

Control flow: `dirtree.c` fills path steps and outcomes while scanning; `dirtree_repair.c` consumes and mutates outcomes to delete excess paths or adopt orphaned directories. Repair-specific outcome values (`DELETING`, `DELETED`, `ADOPTING`, `ADOPTED`) let live update hooks distinguish self-induced changes from stale external mutations.

State and persistence: The header defines transient in-memory state only: names in `xfblob`, steps in `xfarray`, path list entries, scratch parent records, hook state, lock, and stale/aborted booleans. Persistent directory entries and parent pointers are changed only by repair code using this state.

Dependencies and integration points: Integrates parent records, parent args, adoption context, dirent hooks, inode bitmaps, xfile arrays/blobs, and scrub context. It is the contract boundary between scan/evaluate and repair/fix logic.

Risks and test signals: Risks include outcome state-machine drift between scrub and repair, stale hook processing after `sc->ip` release, and xfarray index assumptions that path steps for a path are sequential after the second step. Test path creation/deletion/adoption transitions, cleanup after aborted scans, and concurrent hook callbacks during teardown.
