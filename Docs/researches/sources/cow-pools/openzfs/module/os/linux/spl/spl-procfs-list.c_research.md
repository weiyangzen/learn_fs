# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-procfs-list.c

Read completely: 285 lines.

This implements `procfs_list_t`, a scalable wrapper for exposing SPL linked lists through procfs `seq_file` entries under the kstat namespace.

Key responsibilities:
- Provides per-open cursors to avoid quadratic `seq_list_start()` rescans on large lists.
- Supports optional header, row show, and clear callbacks.
- Installs/uninstalls proc entries through the kstat proc namespace.
- Initializes, destroys, and appends nodes to wrapped lists.

Important implementation details:
- Each list node embeds a `procfs_list_node_t` at a caller-provided offset; the helper stores a monotonically increasing node ID there.
- The per-open cursor caches the last node and position. Reads can resume from the cached node or advance to the next node without walking from the head.
- If entries have been dropped from the head and the cached node is stale, `start()` returns `-EIO` to prevent reading removed entries.
- Position `0` is reserved for `SEQ_START_TOKEN`, so `pl_next_id` starts at 1.
- Writes call the optional clear callback and otherwise just return the write length.

Dependencies and interactions:
- Uses SPL lists/mutexes and Linux procfs/seq_file.
- Uses `kstat_proc_entry_install()` and `kstat_proc_entry_delete()` from `spl-kstat.c`.

Reliability notes:
- The design assumes callers add only through `procfs_list_add()` and remove only from the head if they manipulate the underlying list directly.
- Callers must hold `pl_lock` when adding nodes.
