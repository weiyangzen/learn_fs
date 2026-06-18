# sources/distributed-fs/glusterfs/xlators/meta/src/meta-helpers.c

Purpose: provides the shared context, fd-cache, xdata, stat synthesis, and content-fill helpers used by every `meta` hook and default FOP. It is the glue between Gluster inode/fd context APIs and the translator's per-file `meta_ops` model.

Important APIs/types/functions: `meta_fd_get()` allocates or returns per-fd `meta_fd_t`; `meta_fd_release()` frees cached data and dirents. `meta_ops_get()`, `meta_ops_set()`, `meta_fops_get()`, `meta_ctx_get()`, and `meta_ctx_set()` manage two inode-context slots: one for ops and one for arbitrary hook payload. `meta_direct_io_mode()` prepares xdata for direct I/O. `meta_iatt_fill()` and `default_meta_iatt_fill()` synthesize file attributes. `meta_file_fill()`, `meta_dir_fill()`, and `fixed_dirents_len()` materialize and count virtual content.

Control flow: `meta_ops_set()` initializes a hook's fop table with defaults and stores the ops pointer in inode context. Later FOP wrappers call `meta_fops_get()` to dispatch to that ops table or `default_fops` if no meta ops exist. File reads call `meta_file_fill()`, which opens a `strfd`, invokes `ops->file_fill()`, transfers ownership of the generated buffer to the fd cache, and closes the `strfd`. Directory reads call `meta_dir_fill()` once per fd and keep returned dirents until release.

State and persistence behavior: all state is in memory. Inode context stores raw pointers to static `struct meta_ops` tables and hook-selected live objects such as `xlator_t`, `glusterfs_graph_t`, or `data_t`. Fd context owns generated buffers and dynamically allocated names. `meta_local_t` owns an optional xdata dict and is cleaned during stack unwind.

Dependencies and integration points: uses Gluster memory accounting types, inode/fd context APIs, `dict_new()`/`dict_unref()`, UUID helpers, `gfid_to_ino()`, realtime timestamp helpers, and `strfd`. The public prototypes are declared in `meta.h` and consumed by `meta.c`, `meta-defaults.c`, and all hook modules.

Risks and edge cases: context values are untyped `void *`/integer casts, so mismatched hook payloads can crash fill callbacks. `meta_iatt_fill()` returns without populating iatt if no ops are attached, so callers must ensure hooks ran before stat/read replies. Cached dynamic content can become stale while a fd remains open. `default_meta_iatt_fill()` generates a UUID when the inode gfid is null, which can create non-stable synthetic identities.

Test signals: verify fd allocation/release under repeated open/read/close, directory fill ownership, direct-io xdata allocation and cleanup through `META_STACK_UNWIND`, stat modes for dirs/symlinks/read-only/tunable files, and hook context propagation from parent to child.
