# sources/distributed-fs/glusterfs/xlators/features/index/src/index.h

## Purpose
Defines shared enums, private structs, local state, and cleanup macros for the index translator.

## Important APIs, Types, and Functions
- `index_state_t` tracks whether an inode is known in an index.
- `index_xattrop_type_t` names supported index classes: `XATTROP`, `DIRTY`, and `ENTRY_CHANGES`.
- `index_inode_ctx_t` stores queued stubs, virtual parent GFID for entry-change subdirs, state per type, and a processing flag.
- `index_fd_ctx_t` stores a `DIR *` and EOF offset for virtual readdir.
- `index_priv_t` stores base paths, internal virtual GFIDs, watchlists, worker state, pending count cache, and locks.
- `INDEX_STACK_UNWIND` centralizes unwind cleanup for `index_local_t`.

## Control Flow
The header’s structs enable `index.c` to serialize per-inode xattrop work separately from the global worker queue. The unwind macro clears `frame->local`, unwinds, unrefs the held inode/xdata, and returns local memory to the pool.

## State and Persistence
All defined structs are in-memory state. Persistent index entries are managed in `index.c` through filesystem paths stored in `index_priv_t`.

## Dependencies and Integration Points
Includes `call-stub.h` and the translator memory types. Uses GlusterFS list heads, GFID/uuid types, fd/inode types, pthread primitives, dicts, and atomics indirectly through included headers.

## Risks and Edge Cases
`state[XATTROP_TYPE_END]` depends on enum values staying dense and non-negative except `XATTROP_TYPE_UNSET`. `INDEX_STACK_UNWIND` assumes `frame->local` is an `index_local_t` and would be unsafe on unrelated frames.

## Test Signals
Compile coverage should catch enum/array drift. Runtime tests that queue multiple xattrop operations on one inode should verify `processing` and local cleanup are correct.
