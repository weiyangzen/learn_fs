# sources/distributed-fs/ceph/src/client/MetaRequest.h

## Purpose
`MetaRequest.h` declares the client’s MDS request record, including operation header, paths, pinned cache objects, cap release hints, routing/retry state, reply state, waiters, and helper predicates.

## Important APIs, Types, and Functions
Fields include private inode/dentry refs for path/path2/other targets, `ceph_mds_request_head head`, `filepath path/path2`, `alternate_name`, fscrypt metadata, payload `data`, cap drop/unless masks, release vector, regetattr mask, MDS routing fields, refcount, reply, readdir `dirp`, unsafe flags/list items, wait contexts, target inode, and caller perms. Methods include `abort()`, `aborted()`, `get_abort_code()`, setters/takers for inode refs, dentry setters, `get()`/`_put()`, caller/owner setters, path/data helpers, `is_write()`, `can_forward()`, `auth_is_best()`, and `dump()`.

## Control Flow
Client operation code constructs a request with an MDS op, attaches paths/cache refs/perms/data, assigns a tid, routes it through a session, and waits for reply/safe completion. Forward/retry fields track MDS redirection. `auth_is_best()` helps choose auth versus replica MDS based on operation and caps.

## State and Persistence Behavior
The request object is volatile but models durable metadata operation progress until MDS reply and safe journal acknowledgement. `got_unsafe`, unsafe xlist items, and waitfor_safe contexts preserve ordering and completion semantics for writes.

## Dependencies and Integration Points
It depends on MDS op/message types, `filepath`, `DentryRef`, `InodeRef`, `UserPerm`, and xlist. `Client` and `MetaSession` manage ownership, sending, aborting, replay, and completion.

## Risks and Edge Cases
Reference counting is manual and `_put()` is intentionally pseudo-private for `Client::put_request()`. Cap release masks must match cache state or stale caps can linger. Forwarding is disallowed for writes and opens. `auth_is_best()` contains subtle MDS lock/cap heuristics, especially for getattr/xattr/rstat behavior.

## Test Signals
Write/open forwarding refusal, auth-MDS selection for getattr/xattr/rstat, abort propagation, request replay after reconnect, safe waiters, cap release encoding, fscrypt alternate-name create/open requests, and refcount cleanup.
