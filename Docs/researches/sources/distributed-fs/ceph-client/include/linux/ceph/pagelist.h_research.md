# sources/distributed-fs/ceph-client/include/linux/ceph/pagelist.h

## Purpose

`pagelist.h` defines a refcounted page-backed append buffer used by Ceph message and OSD class-operation encoding paths.

## Important APIs, Types, and Functions

`struct ceph_pagelist` holds a page list, mapped tail pointer, total length, remaining room, reserve/free-list state, and refcount. APIs are `ceph_pagelist_alloc()`, `ceph_pagelist_release()`, `ceph_pagelist_append()`, `ceph_pagelist_reserve()`, `ceph_pagelist_free_reserve()`, and inline little-endian encoders for 64/32/16/8-bit values and strings.

## Control Flow

Callers allocate a pagelist, optionally reserve page capacity, append raw bytes or encoded primitives, attach the pagelist to a Ceph message, and release it when no longer referenced.

## State and Persistence Behavior

Runtime state is the list of allocated pages, mapped tail, current length, reserve pages, and refcount. No disk persistence is owned, but bytes become wire payloads for Ceph messages.

## Dependencies and Integration Points

It depends on list, refcount, byteorder, and kernel page allocation. It integrates with messenger `CEPH_MSG_DATA_PAGELIST`, OSD request data, monitor commands, and class method payload construction.

## Risks and Edge Cases

Append/reserve error handling is critical under memory pressure. String encoding takes a `char *` plus explicit length and does not imply NUL termination. Lifetime must outlive any message data cursor using the pagelist.

## Test Signals

Test append across page boundaries, reserve/free-reserve accounting, primitive endian encoders, zero-length and multi-page strings, refcount release, and message send paths that consume pagelists.
