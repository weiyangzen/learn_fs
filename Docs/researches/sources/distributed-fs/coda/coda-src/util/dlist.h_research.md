# sources/distributed-fs/coda/coda-src/util/dlist.h

## Purpose
Declares the intrusive circular doubly-linked list primitive.

## Important APIs, Types, And Functions
`CFN` is the ordering callback. `DlGetType` selects head/tail removal. `dlist`, `dlist_iterator`, and `dlink` define container, traversal, and embedded link state.

## Control Flow
Callers derive from `dlink`, add objects to one list at a time, remove explicitly or through `get()`, and traverse with an iterator.

## State And Persistence
Membership state lives in private `next` and `prev` pointers inside each `dlink`. There is no persistence or ownership of derived objects.

## Dependencies And Integration Points
Includes `stdio.h` for print overloads and is used by `dhash`, `dict`, and many Coda intrusive structures.

## Risks
The `is_linked()` check only tests `next != NULL`; damaged half-linked nodes are possible if users mutate internals indirectly. No locking or safe-delete iteration is provided.

## Test Signals
Compile derived classes, verify one-list-at-a-time enforcement, ordering callback behavior, and print diagnostics.
