# sources/distributed-fs/orangefs/src/common/llist/llist.h

Purpose: Declares the simple OrangeFS linked-list container API.

Important APIs/types: `PINT_llist` node contains `void *item` and `PINT_llist_p next`. Macro `PINT_llist_add()` aliases head insertion. Prototypes cover creation, emptiness, insertion, traversal callbacks, free, search, remove, head/tail access, count, and raw next traversal.

Control flow contract: Callers create a sentinel list with `PINT_llist_new()` and should treat the first node as non-data. Comparator callbacks return zero for equality.

State/persistence: Header defines only in-memory list shape.

Dependencies/integration: Includes `<stdio.h>` and `<stdlib.h>` for C consumers.

Risks: Exposes struct internals, so callers can corrupt links. No const-correct variants. No API to free only nodes without item callback.

Test signals: Compile consumers using macro alias and direct traversal; static analysis for callers that assume first node contains data.
