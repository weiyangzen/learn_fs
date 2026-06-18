<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_private.h -->
# sources/distributed-fs/ceph-client/include/linux/list_private.h

## Purpose
This header supplies list traversal/container helpers for structures with private `struct list_head` members. It avoids direct field access in macro expansions by computing the member offset and doing pointer arithmetic.

## Important APIs, Types, and Functions
The API mirrors common `list.h` typed helpers with `list_private_` prefixes: `list_private_entry`, first/last entry helpers, next/previous helpers, circular helpers, `list_private_entry_is_head`, forward/reverse iterators, continue/from variants, safe variants, and `list_private_safe_reset_next`. `__list_private_offset()` derives the member offset.

## Control Flow
Macros convert between list nodes and containing objects, then use the underlying `list_head` links for traversal. Safe variants cache the next object before caller code can delete the current object.

## State and Persistence Behavior
No state is owned here. The caller owns list heads and embedded nodes, and the same mutation and locking rules as `list.h` apply.

## Dependencies and Integration Points
It depends on `linux/compiler.h` and `linux/list.h`. It is useful for code that wants typed iteration over private list members while keeping the member name unavailable to ordinary direct users.

## Risks and Test Signals
Risks include giving the wrong type/member pair, using unsafe iterators while deleting, and assuming the privacy wrapper changes locking semantics. Build errors around private members, debug-list reports, and iterator tests over add/delete paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_private.h -->
