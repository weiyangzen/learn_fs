# sources/distributed-fs/ceph/src/mds/JournalPointer.cc

## Purpose

`JournalPointer.cc` implements durable RADOS load/save operations for the MDS journal pointer object. The pointer tells an MDS rank which journal inode is currently active (`front`) and which backup/reformat journal inode may exist (`back`).

## Important APIs, Types, And Functions

`get_object_id()` computes the fixed RADOS object name for the rank by adding `node_id` to `MDS_INO_LOG_POINTER_OFFSET` and formatting it as `<hex ino>.00000000`.

`load(Objecter*)` performs a blocking `read_full()` on the pointer object in `pool_id`, waits with `C_SaferCond`, decodes the object into `front` and `back`, and returns the objecter result or `-EINVAL` for decode errors.

`save(Objecter*) const` is the blocking write path. It asserts the objecter is non-null and the pointer is not null, encodes the pointer, writes the full object with `write_full()`, waits for completion, logs write errors, and returns the status.

`save(Objecter*, Context*) const` is the asynchronous variant. It encodes the pointer and submits `write_full()` with the supplied completion context. The comment says it assumes the caller already holds the objecter lock.

## Control Flow And Data Flow

MDLog creates a `JournalPointer` for the rank and metadata pool. On startup/recovery it calls `load()` to find existing journal locations. On journal creation or reformat, it updates `front`/`back` and calls a save variant to persist the new pointer. Data flows through Ceph buffer encoding into one RADOS object per MDS rank.

Error flow is deliberately simple. Missing/read-failed objects return the objecter error and leave the pointer as-is/null. Decode corruption maps to `-EINVAL`. Blocking writes return the objecter write status and log negative results; asynchronous writes leave error handling to the completion path.

## State And Persistence Behavior

The durable state is the encoded `front` and `back` inode numbers stored in the metadata pool object named by rank. `node_id` and `pool_id` are not encoded; they are local addressing parameters. `is_null()` means both inode numbers are zero, and the blocking save path refuses to persist such a null pointer.

Writes use `write_full()`, replacing the whole pointer object. Reads use `read_full()`, so partial state is not interpreted. The timestamp passed to writes is `ceph::real_clock::now()`.

## Dependencies And Integration Points

Dependencies include `JournalPointer.h`, `mdstypes.h`, `Objecter`, `Messenger` for debug prefix identity, `C_SaferCond`, `cpp_strerror`, object locators, and snap context. Integration is primarily with `MDLog.cc`, including asynchronous pointer writes and journal reformat logic.

## Risks And Edge Cases

The asynchronous `save()` does not assert `!is_null()`, unlike the blocking variant, so callers can accidentally persist a null pointer through that path. `get_object_id()` depends on valid `node_id`; the default constructor leaves `node_id = -1` and `pool_id = -1`, so load/save on a default object would address invalid storage. Decode errors return `-EINVAL` without logging details beyond the caller's handling.

Because this object is the root of journal discovery, stale or corrupted pointer contents can prevent MDS recovery or send it to the wrong journal inode. Objecter write/read error handling must distinguish missing pointer during first initialization from real I/O failures.

## Test Signals

Tests should cover object ID formatting for rank values, encode/decode round trips, blocking save refusing null pointers, load returning `-EINVAL` on malformed data, load behavior for missing objects, asynchronous save behavior and completion error propagation, and MDLog recovery/reformat paths that update `front` and `back` correctly.
