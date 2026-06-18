# sources/distributed-fs/ceph-client/scripts/include/list_types.h

## Purpose
Defines the minimal intrusive list node types used by scripts-side list and hashtable helpers.

## APIs, Control Flow, and State
The header declares `struct list_head` with `next`/`prev`, `struct hlist_head` with `first`, and `struct hlist_node` with `next` and `pprev`. It has no functions or behavior; callers manage node lifetime.

## Dependencies and Integration
It is included by `list.h` and by code that embeds list nodes in host-tool structures, notably genksyms symbols.

## Risks and Test Signals
The types are intentionally ABI-local to host tools. Test signals are successful compilation and no accidental mixing with incompatible full-kernel list definitions in the same translation unit.
