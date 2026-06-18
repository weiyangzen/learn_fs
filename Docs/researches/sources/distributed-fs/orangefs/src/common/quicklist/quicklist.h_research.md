<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quicklist/quicklist.h -->
# sources/distributed-fs/orangefs/src/common/quicklist/quicklist.h

## Purpose
Provides OrangeFS's lightweight doubly linked list primitive, derived from Linux list-style intrusive links.

## Important APIs, Types, And Functions
Defines `struct qlist_head`, initialization macros, `qlist_add`, `qlist_add_tail`, `qlist_del`, `qlist_del_init`, `qlist_empty`, `qlist_pop`, `qlist_splice`, `qlist_entry`, iteration macros, `qlist_exists`, `qlist_count`, and `qlist_find`. Windows-specific iterator macros avoid GNU `typeof`.

## Control Flow
List heads point to themselves when empty. Add inserts between known neighbors; delete stitches neighbors around the removed link; pop removes the first item; splice moves all entries from one list into another position; iteration macros traverse raw links or containing entries.

## State And Persistence
All state is embedded in caller-owned structures via `qlist_head` fields. There is no allocation, locking, or persistence in this header.

## Dependencies And Integration Points
Used by `quickhash`, `tcache`, security key tables, and statecomp. Windows builds include `wincommon.h`; Unix builds use GNU `typeof` for typed entry iteration.

## Risks And Test Signals
Risks are typical intrusive-list hazards: deleting unlinked entries, mutating during non-safe iteration, no locking, and portability around `typeof`. Tests should cover empty, add, tail ordering, delete-init, pop, splice, safe removal during iteration, and Windows macro compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/quicklist/quicklist.h -->
