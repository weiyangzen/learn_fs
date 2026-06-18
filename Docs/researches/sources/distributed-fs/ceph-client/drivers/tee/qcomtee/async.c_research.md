# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/async.c

## Purpose
`async.c` parses asynchronous QCOMTEE messages appended to outbound invocation buffers and currently handles secure-world object release requests. It prevents async requests from being replayed by clearing the async buffer after processing.

## Important APIs, Types, And Functions
The file defines async protocol versions 1.0, 1.1, 1.2 and treats 1.2 as current. `struct qcomtee_async_msg_hdr` carries version and operation. `struct qcomtee_async_release_msg` carries a counted array of object ids to release.

`qcomtee_get_async_buffer()` computes the available async-message region in a `qcomtee_object_invoke_ctx`: if the invocation context is not busy, the full outbound buffer is available; if a callback request already occupies the buffer, it skips callback header, input buffers, and output buffers using `qcomtee_msg_*` helpers and alignment. `async_release()` erases each object id from the object invocation context with `qcomtee_idx_erase()` and drops the object with `qcomtee_object_put()`. `qcomtee_fetch_async_reqs()` loops through aligned async messages until unused zeroed space, major-version mismatch, unsupported op, parse failure, or insufficient remaining space, then zeroes the entire async buffer with `memzero_explicit()`.

## Control Flow And State
Async state is encoded in the outbound message buffer associated with one invocation context. The driver consumes messages sequentially, advances by aligned consumed size, and resets the buffer so QTEE does not see the same async requests again. Release messages mutate object-index state in the invocation context and object refcounts.

## Dependencies And Integration Points
This file depends on `qcomtee.h` for object invocation context, buffer, callback-message layout, argument iteration macros, object index erase, object put, and QCOMTEE message operation ids. It integrates with the QCOMTEE call path that owns outbound buffers and invokes `qcomtee_fetch_async_reqs()` after QTEE has had a chance to write async messages.

## Risks
`async_release()` trusts `msg->counts` enough to iterate and compute `struct_size()`; the `size` argument is currently unused, so a malformed count could overread the async buffer unless upstream message bounds are guaranteed elsewhere. `qcomtee_fetch_async_reqs()` checks only major version, so newer minor versions are accepted even if they add incompatible operation formats under the same major. Offset computation for busy callback buffers must stay aligned with the callback message format or async parsing can overlap normal callback payloads.

## Test Signals
Feed empty zeroed async buffers, valid release messages with one and many ids, unsupported op codes, major-version mismatch, truncated release messages, and busy callback buffers with input/output payloads. Verify released objects are removed and refcounts drop once, and that the async buffer is zeroed after every exit path.
