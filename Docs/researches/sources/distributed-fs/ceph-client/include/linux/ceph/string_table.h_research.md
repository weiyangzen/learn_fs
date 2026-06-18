# sources/distributed-fs/ceph-client/include/linux/ceph/string_table.h

## Purpose

`string_table.h` declares a shared interned string table for Ceph strings, primarily used for pool namespaces and other repeated names.

## Important APIs, Types, and Functions

`struct ceph_string` contains a `kref`, an RB-tree node or RCU head union, length, and flexible string bytes. APIs are `ceph_find_or_create_string()`, `ceph_release_string()`, `ceph_strings_empty()`, `ceph_get_string()`, `ceph_put_string()`, `ceph_compare_string()`, and `ceph_try_get_string()`.

## Control Flow

Callers find or create an interned string, take/drop krefs as ownership changes, compare by length and bytes, and use `ceph_try_get_string()` to safely acquire an RCU-protected pointer unless its refcount is already zero.

## State and Persistence Behavior

The backing implementation owns a global RB tree of interned strings. Individual strings are refcounted and released through RCU-safe teardown. No disk persistence is owned.

## Dependencies and Integration Points

It depends on kref, RB trees, RCU, and kernel string helpers. It integrates with `ceph_file_layout.pool_ns`, `ceph_object_locator.pool_ns`, OSD maps, and request targeting.

## Risks and Edge Cases

RCU users must not dereference after dropping protection without a kref. `ceph_compare_string(NULL, "", 0)` intentionally treats NULL as empty. Embedded NUL bytes are compared by explicit length but `strncmp` still works only over the provided length.

## Test Signals

Test interning deduplication, get/put release, `ceph_strings_empty()` after cleanup, RCU try-get races with release, NULL/empty comparisons, and namespace lifecycle through object locator copies.
