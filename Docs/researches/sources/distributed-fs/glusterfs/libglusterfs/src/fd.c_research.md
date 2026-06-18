# sources/distributed-fs/glusterfs/libglusterfs/src/fd.c

## Purpose
`fd.c` implements GlusterFS' in-memory file-descriptor object lifecycle and the process/client fd table used to map integer fd slots to `fd_t *` instances. It is not a POSIX fd wrapper around kernel descriptors; it tracks Gluster translator state for open files/directories, binds fds to inodes, keeps refcounts, stores per-translator fd context, and provides statedump/dict dump helpers for diagnostics.

## Important APIs, Types, and Functions
- `gf_fd_fdtable_alloc()`, `gf_fd_fdtable_destroy()`: allocate and tear down `fdtable_t`, including its `pthread_rwlock_t`, free-slot list, and references held by table entries.
- `gf_fd_unused_get()`, `gf_fd_put()`, `gf_fdptr_put()`, `gf_fd_fdptr_get()`: allocate, release, find, and ref table entries. `GF_ANON_FD_NO` is ignored on put.
- `fd_create_uint64()`, `fd_create()`, `fd_anonymous_with_flags()`, `fd_anonymous()`: allocate `fd_t` objects from the inode table's fd mempool, initialize `_ctx`, lock context, inode reference semantics, flags, and list membership.
- `fd_ref()`, `__fd_ref()`, `fd_unref()`: atomic refcount operations around `fd_t`. `fd_unref()` removes the fd from the inode list and destroys it when the count reaches zero.
- `fd_bind()`, `__fd_bind()`, `fd_lookup()`, `fd_lookup_uint64()`, `fd_lookup_anonymous()`: manage inode `fd_list` membership and PID/anonymous lookup.
- `fd_close()`, `fd_destroy()`: invoke translator callback hooks (`fdclose`, `fdclosedir`, `release`, `releasedir`) and release inode/lock/context state.
- `fd_ctx_set()`, `fd_ctx_get()`, `fd_ctx_del()` and unlocked variants: attach one `uint64_t` value per xlator to an fd.
- `fd_dump()`, `fdtable_dump()`, `fd_ctx_dump()`, `fdtable_dump_to_dict()`: statedump and dictionary export.

## Control Flow
`gf_fd_fdtable_alloc()` creates a table, then under a write lock calls `gf_fd_fdtable_expand()` with `nr=0`. Expansion rounds to a power-of-two multiple sized by `fdentry_t`, allocates a new entry array, copies old entries if present, chains new entries through `next_free`, sets `first_free`, and frees the old array. `gf_fd_unused_get()` takes a write lock, pops `first_free`, marks the entry `GF_FDENTRY_ALLOCATED`, and stores the caller's `fd_t *`; if no free slot exists it expands and retries, with a defensive two-attempt cap.

`fd_create*()` allocates an `fd_t` using `fd_allocate()`, which initializes `_ctx` sized to the current graph's `xl_count + 1`, creates an fd-lock context, initializes the inode list and lock, and sets the atomic refcount to 1. The actual inode reference is taken by `fd_create_uint64()` after allocation because `fd_allocate()` may be called while holding `inode->lock`; taking `inode_ref()` there would invert lock ordering. Anonymous fds are allocated and bound while holding `inode->lock`, with `GF_ANON_FD_FLAGS` plus possible `O_DIRECT`.

`fd_unref()` decrements the atomic refcount while holding `inode->lock`; if it reaches zero and is still on the inode list, it unlinks the fd and decrements `active_fd_count`. Destruction is done after unlocking and calls translator release callbacks based on file type, restores `THIS`, destroys the fd lock, frees context, decrements `fd_count` if the fd had been bound, unrefs the inode and fd lock context, and returns the fd object to its mempool.

## State and Persistence
All state is process memory only. Persistent side effects are indirect through translator callbacks. `fdtable_t` state includes `fdentries`, `max_fds`, `first_free`, and a rwlock. `fd_t` state includes inode binding, PID, flags, anonymous flag, per-xl context array, fd-lock context, and atomic refcount. Table dump functions serialize current runtime state to statedump or dictionaries but do not persist it.

## Dependencies and Integration Points
The file depends on `glusterfs/fd.h`, inode/table definitions, mempool allocation (`mem_get0`, `mem_put`, `GF_CALLOC`, `GF_REALLOC`), atomics, list helpers, fd-lock context, statedump, logging, and translator graph callbacks. It is a core integration point between higher-level FOP open/create/opendir paths, inode lifecycle, client fd tables, and translators that store fd-private state.

## Risks and Edge Cases
- `gf_fd_fdtable_expand()` updates `first_free` to the start of the new range, so callers must hold the table write lock.
- `gf_fd_put()` checks `fd < fdtable->max_fds` before taking the lock, so concurrent table resize assumptions depend on ownership discipline.
- `gf_fd_put()` deliberately masks double-put/unallocated-put bugs by no-oping if the entry is not allocated.
- `fd_ctx_set()` can reallocate `_ctx`; callers using unlocked variants must already hold `fd->lock`.
- `fd_destroy()` changes thread-local `THIS` while invoking xlator callbacks and must restore it even across directory/file branches.
- Lock-order comments in `fd_allocate()` are important: moving `inode_ref()` inside allocation can deadlock.

## Test Signals
Useful tests cover fdtable growth and free-list reuse, invalid puts and anonymous fd behavior, refcount-to-destroy callback ordering, per-xl fd context set/get/delete including growth beyond initial graph count, statedump/dict output for open fds, and concurrent `gf_fd_fdptr_get()` plus `gf_fd_put()` behavior under the table locks.
