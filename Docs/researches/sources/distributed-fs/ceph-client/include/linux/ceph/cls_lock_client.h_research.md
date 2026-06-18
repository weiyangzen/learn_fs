# sources/distributed-fs/ceph-client/include/linux/ceph/cls_lock_client.h

## Purpose

`cls_lock_client.h` declares the client-side interface to Ceph's RADOS object-class lock operations. It lets kernel clients acquire, release, break, inspect, and assert object locks through OSD class calls.

## Important APIs, Types, and Functions

Types include `enum ceph_cls_lock_type`, `ceph_locker_id`, `ceph_locker_info`, and `ceph_locker`. APIs are `ceph_cls_lock()`, `ceph_cls_unlock()`, `ceph_cls_break_lock()`, `ceph_cls_set_cookie()`, `ceph_cls_lock_info()`, `ceph_free_lockers()`, and `ceph_cls_assert_locked()`.

## Control Flow

The call path is OSD-client driven: callers pass an `osdc`, object id, object locator, lock name, cookie, tag, and type; the implementation constructs class method requests against the target object. `ceph_cls_assert_locked()` adds a class assertion operation to an existing OSD request.

## State and Persistence Behavior

The header itself stores no state. Lock state persists in RADOS object-class metadata on the OSD side. Returned locker arrays and strings are caller-owned until released with `ceph_free_lockers()`.

## Dependencies and Integration Points

It includes `osd_client.h` and therefore integrates with OSD request allocation, object ids, locators, entity names, and messenger delivery.

## Risks and Edge Cases

Cookie/tag/name strings are trust boundaries and must be encoded with correct lengths. Breaking locks requires identifying the existing locker accurately. Memory ownership of `tag` and `lockers` returned from info queries is a likely leak/double-free risk.

## Test Signals

Exercise exclusive/shared lock acquisition, unlock, break-lock, cookie replacement, lock-info decoding, assert-locked operation composition, and cleanup of returned locker arrays on success and error paths.
