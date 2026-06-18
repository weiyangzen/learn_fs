# sources/distributed-fs/ceph/src/rgw/rgw_gc_log.h

## Purpose
Declares helper functions that encode RGW garbage-collection queue operations into `librados::ObjectWriteOperation`s.

## Important APIs, Types, And Functions
The functions are `gc_log_init2()`, `gc_log_enqueue1()`, `gc_log_enqueue2()`, `gc_log_defer1()`, and `gc_log_defer2()`. They operate on `cls_rgw_gc_obj_info` entries with expiration values and queue sizing/deferred parameters.

## Control Flow
Callers prepare an object write operation, invoke one of these helpers to append cls_rgw GC operations, and submit the write through RADOS. The `1` helpers are comments-described as omap-oriented legacy operations, while `2` helpers target the cls_rgw GC queue.

## State And Persistence Behavior
This header does not hold state; persistence occurs when the resulting object write operation is submitted to RADOS/cls_rgw.

## Dependencies And Integration Points
Depends on `include/rados/librados.hpp` and `cls/rgw/cls_rgw_types.h`. It integrates RGW object deletion/lifecycle cleanup paths with the cls_rgw garbage collection log.

## Risks
Only declarations are present here, so callers depend on implementation semantics elsewhere. Version suffixes can be confusing without knowing which on-disk queue format is expected.

## Test Signals
Tests should verify encoded operations initialize queue sizing, enqueue expiration/object info, defer existing entries, and remain compatible with cls_rgw queue readers.
