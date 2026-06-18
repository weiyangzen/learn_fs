# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/store.h

Purpose: `store.h` declares a simple persistent key/value file store used by glusterd-style management code.

Important APIs and types: `gf_store_handle_t` tracks path, active fd, temp fd, read `FILE *`, and local lock state. `gf_store_iter_t` tracks an open file, filepath, and read buffer. `gf_store_op_errno_t` distinguishes success, null key/value, EOF, ENOMEM, and stat failure. APIs create directories/handles/temp files, sync directory entries, rename/unlink temp paths, tokenize lines, retrieve/save values/items, iterate entries, stringify store errors, and lock/unlock handles.

Control flow and state: callers create or retrieve a handle, optionally lock it, write to temp files, sync, rename into place, iterate entries, and destroy the handle. Persistence relies on temp-file then rename patterns plus directory sync.

Dependencies and integration: includes compatibility and Gluster core headers. Graph mux pidfile logic is separate but follows similar lock-and-file persistence concerns.

Risks: key/value tokenization must handle malformed lines and buffer limits. Atomicity depends on correct temp path, fsync, rename, and directory sync ordering. `locked` is local state and must match actual `lockf` state.

Test signals: crash-safety tests around temp rename, lock contention, iteration EOF/errors, malformed key/value lines, long values near 8192 bytes, missing directories, and cleanup of temp files are important.
