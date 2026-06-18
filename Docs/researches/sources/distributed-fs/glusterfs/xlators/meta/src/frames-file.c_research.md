# sources/distributed-fs/glusterfs/xlators/meta/src/frames-file.c

## Purpose
Implements a meta virtual file that dumps active call stacks/frames in JSON-like text.

## Important APIs, Types, and Functions
- `frames_file_fill()` locks `this->ctx->pool`, iterates `pool->all_frames`, then each stack's `myframes`, printing frame xlator, timing, parent, wind/unwind edges, completion state, stack unique id, fop type, uid/gid, and lock owner.
- `frames_file_ops` exposes `.file_fill`.
- `meta_frames_file_hook()` attaches file ops.

## Control Flow
During file read, the function validates arguments, locks the global call pool, serializes all stacks/frames, and unlocks before returning `strfd->size`.

## State and Persistence
Reads volatile call-pool state. Does not persist anything.

## Dependencies and Integration Points
Depends on call stack/frame structures, `gf_fop_list`, `lkowner_utoa()`, strfd, and meta file-fill plumbing.

## Risks
Manual JSON formatting can produce malformed output if strings contain quotes. Holding the call-pool lock while formatting may be expensive on large active-frame sets.

## Test Signals
Reading the frames meta file during active I/O should show stack counts and frame data without deadlock.
