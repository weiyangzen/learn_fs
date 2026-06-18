# sources/distributed-fs/orangefs/src/io/buffer/ncac-list.h

## Purpose
Provides a local Linux-kernel-style intrusive doubly linked list implementation for NCAC.

## Important APIs, Types, And Functions
Defines `struct list_head`, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, add/delete/move/splice helpers, `list_empty`, `offsetof`, `container_of`, and `list_entry`.

## Control Flow
NCAC uses list heads embedded in requests, extents, inode clean/dirty lists, cache active/inactive/free lists, and progress lists. Add/delete functions manipulate links in O(1).

## State And Persistence
State is stored in caller-embedded `list_head` links. `list_del` poisons pointers while `list_del_init` resets them to a single-item list. No locking is built in.

## Dependencies And Integration Points
Included by `internal.h` and most buffer modules. It duplicates common kernel list semantics without requiring Linux headers.

## Risks And Test Signals
Risks include no iteration macros beyond `list_entry`, GCC-specific `typeof` in `container_of`, overriding `offsetof`, and misuse after `list_del` poisoned entries. Tests should cover add/tail/delete/init/splice behavior and portability builds.
