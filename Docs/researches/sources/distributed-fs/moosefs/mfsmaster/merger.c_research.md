## sources/distributed-fs/moosefs/mfsmaster/merger.c

Purpose: merges multiple textual changelog files by ascending change id and applies them through `restore_file`. It is used during automatic metadata restoration to replay changelog fragments after loading the best available metadata snapshot.

Important APIs and types: `hentry` stores a changelog file handle, shared filename pointer, line buffer, parsed line pointer, and next change id. The global heap orders entries by `nextid`. `merger_start` opens all input files, initializes heap entries, records maximum allowed id hole and progress bounds. `merger_loop` repeatedly applies the lowest-id change and advances or removes that file. Helper functions implement heap up/down, entry reading, entry deletion, and entry creation.

Control flow: each file's first valid line is read by `merger_nextentry`; invalid or empty files are dropped. The heap root is applied with `restore_file(filename, id, ptr, verblevel)`. After each successful restore, the same file advances one line; if it reaches EOF or invalid data, it is removed and the heap is rebalanced. Progress is printed periodically for ids divisible by 2497 when first/last bounds are known.

State and persistence behavior: no durable state is written directly here; persistence mutation occurs through `restore_file`, which replays metadata changelog operations into in-memory structures. The module owns file handles and buffers during a restore run and frees them on completion or error.

Dependencies and integration points: depends on `restore.h` for changelog application, `sharedpointer` for filename ownership, `mfslog` for warnings, and `clocks` for progress ETA. `metadata.c` calls it from `meta_loadall` after selecting metadata and changelog files.

Risks: `maxidhole` rejects non-monotonic or unexpectedly distant ids per file as garbage, which protects restore but may discard a damaged tail. `merger_delete_entry` operates on `heap[heapsize]` after callers decrement/swap; that convention must be preserved. Progress ETA divides by `(heap[0].nextid - firstlv)` only after current id is above the first version; the code handles below-first separately.

Test signals: test merging two or more interleaved changelogs, duplicate/out-of-order ids, large id holes, unreadable files, restore errors, and progress-bounds behavior. Use fake `restore_file` in unit tests to assert exact application order.
