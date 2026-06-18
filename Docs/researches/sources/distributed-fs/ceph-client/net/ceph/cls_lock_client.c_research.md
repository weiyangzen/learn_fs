# sources/distributed-fs/ceph-client/net/ceph/cls_lock_client.c

## Purpose
Implements kernel client helpers for Ceph RADOS object-class lock operations: acquire, unlock, break, set cookie, query lock info, free decoded lockers, and assert a lock as part of an OSD request.

## Important APIs, Types, and Functions
Exported APIs are `ceph_cls_lock()`, `ceph_cls_unlock()`, `ceph_cls_break_lock()`, `ceph_cls_set_cookie()`, `ceph_cls_lock_info()`, `ceph_free_lockers()`, and `ceph_cls_assert_locked()`. Internal decoders are `decode_locker()` and `decode_lockers()`. It uses `struct ceph_osd_client`, `struct ceph_object_id`, `struct ceph_object_locator`, `struct ceph_locker`, `struct ceph_entity_name`, and OSD class request helpers.

## Control Flow
Each mutating helper computes the encoded request size, rejects payloads over one page, allocates a page with `GFP_NOIO`, starts a versioned encoding block, encodes lock name, type, cookies, tag, description, locker identity, expiration, or flags as required, and calls `ceph_osdc_call()` with class `"lock"` and the relevant method. `ceph_cls_lock_info()` allocates request and reply pages, calls `"get_info"`, then decodes lockers, lock type, and tag from the reply. `ceph_cls_assert_locked()` initializes a class op in an existing OSD request and attaches a one-page encoded assertion payload.

## State and Persistence
The file owns no long-lived state. It allocates transient pages and decoded locker arrays/strings. Lock state itself persists in the RADOS object/class on the Ceph cluster, not in kernel memory.

## Dependencies and Integration Points
Depends on Ceph OSD client calls, class method names, Ceph encoding/decoding helpers, page-vector helpers, and exported lock client headers. It is used by higher-level Ceph clients needing distributed object locks.

## Risks
String lengths are taken with `strlen()`, so inputs must be NUL-terminated. All request payloads must fit in a single page; long descriptions or tags return `-E2BIG`. Decode paths must free partially decoded lockers on error. `decode_locker()` skips description after reading a length and depends on prior bounds checks in decode helpers. Cluster-side method compatibility depends on versioned encoding block layout.

## Test Signals
Exercise each class method against a test cluster, overlong string rejection, allocation failure paths, malformed `get_info` replies, multiple lockers decode/free, assert-locked class op composition inside multi-op requests, shared/exclusive lock types, break-lock target identity, and cookie update semantics.
