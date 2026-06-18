# sources/distributed-fs/moosefs/mfsmaster/flocklocks.h

## Purpose
`flocklocks.h` declares the master-side advisory whole-file lock subsystem used by client protocol handling, open-file cleanup, metadata persistence, and changelog restore. It hides the internal inode hash, lock queues, and wakeup logic behind a compact API.

## Important APIs
`flock_locks_cmd` is the primary command entry point. It takes the client connection pointer, session id, message id, request id, inode, lock owner, and protocol operation, then returns a MooseFS status code such as OK, WAITING, EAGAIN, EINTR, ECANCELED, NOTOPENED, or EINVAL depending on lock state.

`flock_file_closed` releases/removes all locks and waiters for a session/inode pair when the open-file layer closes a file. `flock_disconnected` removes waiting locks tied to a disconnected client connection. `flock_list` serializes active locks for all inodes or one inode into the protocol buffer format, returning the required byte count when called with `buff == NULL`.

`flock_mr_change` applies changelog/metadata-restore lock changes without going through the client wait path. `flock_store` and `flock_load` serialize active locks to/from metadata using `bio`. `flock_cleanup` frees all module state, and `flock_init` allocates and registers runtime hooks.

## Control Flow And State
The header exposes no structs, so callers cannot inspect or mutate lock queues directly. Client operations flow through `flock_locks_cmd`; lifecycle notifications flow through close/disconnect hooks; persistence flows through store/load and replay.

Only active locks are part of persisted state. Waiting lock attempts are represented internally by message/request instances and are expected to be resolved by wakeups, interruption, release, disconnect, or process restart loss.

## Dependencies And Integration Points
The header includes `bio.h`, making metadata persistence part of the public contract. It is consumed by `matoclserv.c`, `openfiles.c`, `metadata.c`, and `restore.c` in the master process.

The `void *connptr` API keeps the header independent of the client service connection type but makes pointer identity part of the subsystem contract. The `message_id` and `req_id` parameters are important for asynchronous FUSE wakeup behavior.

## Risks
Because the command API uses raw protocol operation bytes and a raw `void *` connection pointer, misuse is easy to compile. Callers must pass the exact connection object later used for disconnect cleanup and wakeups.

Persistence callers must obey load ordering: open-file/session state needs to exist before `flock_load`, otherwise validation fails or locks are ignored depending on `ignoreflag`.

## Test Signals
Header-level integration tests should verify that client command handling, open-file close handling, metadata store/load, and restore replay all link against this API and agree on status-code semantics. ABI-sensitive tests should cover the `flock_list` size-then-fill protocol because consumers rely on exact serialized byte counts.
