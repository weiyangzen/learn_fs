# sources/distributed-fs/ceph-client/kernel/gcov/fs.c

## Purpose
`fs.c` exposes kernel gcov coverage data under debugfs as a directory tree rooted at `/sys/kernel/debug/gcov`. It creates one data file per instrumented object, provides symlinks needed by gcov tooling, supports per-file and global counter resets, and optionally preserves accumulated coverage for unloaded modules.

## Important APIs, types, and functions
The central type is `struct gcov_node`, which models debugfs directories and data files, tracks loaded `gcov_info` pointers, an `unloaded_info` copy, child lists, symlink dentries, and names. `struct gcov_iterator` holds a synthesized gcda buffer for seq-file reading. Key functions are `gcov_event()`, `add_node()`, `add_info()`, `remove_info()`, `save_info()`, `get_accumulated_info()`, `gcov_seq_open()`, `gcov_seq_write()`, `reset_write()`, `add_links()`, and `gcov_fs_init()`.

## Control flow
Initialization creates the `gcov` debugfs directory and `reset` control file, then enables event replay so already registered coverage objects appear. `gcov_event(GCOV_ADD)` locates an existing node by filename or creates path directories and a data file; duplicate object names are checked for compatibility and accumulated at read time. Opening a data file copies and sums the relevant `gcov_info` objects under `node_lock`, serializes them to a fixed gcda buffer, and hands that buffer to seq-file callbacks in page-sized strides. Writing to a data file resets that object or removes an unloaded-only node; writing to `reset` resets all live nodes and prunes unload-only leaves.

## State and persistence
All state is in memory: `root_node`, `all_head`, child lists, debugfs dentries, live `loaded_info` arrays, and optional `unloaded_info` snapshots. `gcov_persist`, controlled by the `gcov_persist=` boot parameter, determines whether unload data is deep-copied and accumulated or removed when the last live object disappears. Open readers use independent deep-copy buffers, so concurrent counter updates do not mutate the active seq read.

## Dependencies and integration points
The file depends on debugfs, seq_file, module gcov events, compiler-specific helpers declared in `gcov.h`, `OBJTREE`/`SRCTREE` path definitions, and Linux allocation/list/mutex primitives. It integrates with both GCC and Clang backends through the common `gcov_info_*()` API and creates `.gcno` symlinks through `gcov_link[]` so external gcov tools can pair runtime data with build artifacts.

## Risks and test signals
Risks include path traversal behavior from `.` and `..` components, stale node lookup by filename when two objects share a name, incomplete symlink cleanup on partial failure, large coverage buffers stressing `kvmalloc`, compatibility decisions losing saved unload data, and reset/remove races around open files. Test signals include recursive copy of debugfs gcov, per-file reset and global reset, module unload/reload with compatible and incompatible code, object paths under objtree and external builds, `.tmp_` deskewed module filenames, and concurrent reads during add/remove events.
