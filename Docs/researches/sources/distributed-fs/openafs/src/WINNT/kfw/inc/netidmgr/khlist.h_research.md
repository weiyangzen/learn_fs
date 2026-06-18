# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khlist.h

## Purpose

`khlist.h` provides small intrusive list, queue, and tree macros used internally by NetIDMgr headers and implementations. It is explicitly "not exported" and warns that most macros are unsafe.

## Important APIs, Types, and Functions

- LIFO macros: `LDCL`, `LINIT`, `LPUSH`, `LPOP`, `LDELETE`, `LEMPTY`, `LNEXT`, and `LPREV`.
- Tree-with-LIFO-children macros: `TDCL`, `TINIT`, `TADDCHILD`, `TFIRSTCHILD`, `TPOPCHILD`, `TDELCHILD`, and `TPARENT`.
- FIFO queue macros: `QDCL`, `QINIT`, `QPUT`, `QGET`, `QDEL`, `QGETT`, `QTOP`, `QBOTTOM`, `QNEXT`, and `QPREV`.
- Tree-with-FIFO-children macros: `TQDCL`, `TQINIT`, `TQADDCHILD`, `TQFIRSTCHILD`, and `TQPARENT`.

## Control Flow

These macros splice intrusive `next`/`prev` fields directly into caller-provided structures. Queue insertion uses `LPUSH` on the tail and queue removal walks through the reverse links from head to tail. Tree macros combine list or queue children with a parent pointer, allowing context trees (`kherr_context`) and message/event lists (`kmq_message`, `khui_alert`, `khui_property_page`) to share minimal linkage logic.

## State and Persistence Behavior

The macros mutate embedded pointers in-place and do not allocate, free, validate, lock, or track ownership. Persistent state is entirely owned by the enclosing subsystem. A node can only be in one list/tree that uses the same embedded linkage fields at a time.

## Dependencies and Integration Points

`kherr.h` uses `LDCL`, `TDCL`, and `QDCL` for events and contexts. `kmq.h` uses list and queue declarations for responses, messages, queues, subscriptions, and message types. `khalerts.h` uses list links for alert objects. `khprops.h` uses `QDCL` and `LDCL` for property pages.

## Risks and Edge Cases

- Macro arguments are evaluated multiple times in some cases and have no type safety.
- `TINIT` initializes children and parent but does not call `LINIT`; callers must initialize list links separately when needed.
- Deleting or popping a node not currently in the target list can corrupt unrelated lists.
- No synchronization is provided; callers must hold subsystem locks.
- Queue direction is non-obvious: `QNEXT(pe)` maps to `prev` and `QPREV(pe)` maps to `next`.

## Test Signals

- Exercise push/pop/delete on empty, single-node, and multi-node lists.
- Verify FIFO order for `QPUT` plus `QGET` and LIFO order for `QGETT`.
- Add and remove child nodes in both LIFO and FIFO tree variants.
- Run debug builds with assertions in wrapper code to detect double insertion or deletion.
