# sources/distributed-fs/orangefs/src/client/usrint/fts.c

## Purpose
`fts.c` provides a local copy of the BSD file tree traversal implementation for the OrangeFS user-interface library. It backs the `fts_open`, `fts_read`, `fts_children`, `fts_set`, and `fts_close` API declared in `fts.h`, with small usrint adaptations that map libc-internal names such as `__open` and `__readdir` onto the active POSIX wrapper layer. OrangeFS utilities such as `ofs_cp`, `ofs_rm`, and `ofs_setdirhint` use this walker to traverse local/PVFS-visible path trees with `FTS_COMFOLLOW | FTS_PHYSICAL`.

## Important APIs, Types, And Functions
The exported API is the traditional `FTS *fts_open(char * const *argv, int options, compar)`, `FTSENT *fts_read(FTS *)`, `FTSENT *fts_children(FTS *, int)`, `int fts_set(FTS *, FTSENT *, int)`, and `int fts_close(FTS *)`. Internally, `fts_alloc` creates variable-size `FTSENT` nodes and optionally co-locates a `struct stat`; `fts_build` reads a directory into a linked list of children; `fts_stat` classifies nodes as regular files, directories, symlinks, cycles, stat failures, or default entries; `fts_sort` materializes a reusable pointer array for `qsort`; `fts_palloc` expands the traversal path buffer; and `fts_safe_changedir` verifies device/inode before changing cwd.

## Control Flow
`fts_open` validates option bits, allocates the traversal stream, forces `FTS_NOCHDIR` for logical walks, allocates a path buffer, creates a root-parent sentinel, stats each root argument, optionally sorts roots, then installs a dummy `FTS_INIT` current node. `fts_read` drives the preorder/postorder state machine: it handles caller instructions (`FTS_AGAIN`, `FTS_FOLLOW`, `FTS_SKIP`), descends into `FTS_D` nodes by calling `fts_build`, returns linked siblings, then climbs to parents and emits `FTS_DP`. `fts_children` builds child lists for the current preorder directory without advancing the stream. `fts_build` opens the current directory, optionally changes into it, skips dot entries unless requested, creates child nodes, grows the shared path buffer when needed, runs `fts_stat` unless `FTS_NOSTAT` can avoid it, sorts children if requested, and restores cwd for child-only reads or empty directories.

## State And Persistence Behavior
Traversal state is entirely in memory. `FTS` owns the shared path buffer, current node pointer, pending child list, sort array, root directory fd, options, and device id. `FTSENT` nodes link to parents/siblings, store path/name lengths, stat data, cycle back-pointers, symlink fds, caller instructions, and user scratch fields. The implementation may change the process cwd unless `FTS_NOCHDIR` is set, restoring through `fts_rfd`, parent walks, or symlink fds. No durable state is written.

## Dependencies And Integration Points
The file includes `usrint.h`, libc/POSIX headers, and `<fts.h>`. Because `fts.h` maps `__open`, `__opendir`, `__fchdir`, and related symbols, traversal can be compiled inside the usrint interposition layer. It depends on `stat/lstat`, `opendir/readdir/closedir`, `dirfd`, `qsort`, and 64-bit `__fxstat64` in `fts_safe_changedir`.

## Risks
This implementation mutates process cwd, which is fragile in multi-threaded programs or when mixed with code expecting cwd stability. Path lengths are capped below `USHRT_MAX` because `FTSENT.fts_pathlen` is a `u_short`; very deep paths fail with `ENAMETOOLONG`. `fts_padjust` must update every outstanding pointer after reallocating the shared path buffer, making pointer ownership subtle. `fts_safe_changedir` protects against directory replacement races but still relies on fd/cwd semantics. Memory allocation failures set `FTS_STOP` and can leave traversal terminated.

## Test Signals
Useful tests should cover empty roots, zero-length root rejection, preorder/postorder ordering, sorted and unsorted traversal, `FTS_NOSTAT`, `FTS_NOCHDIR`, `FTS_XDEV`, `FTS_SKIP`, `FTS_AGAIN`, symlink follow/no-follow, dangling symlinks, cycle detection, long-path growth, dot entry handling, unreadable directories, and cwd restoration after `fts_close`. Integration tests should exercise OrangeFS tools that call `fts_open` over both local and PVFS-mounted trees.
