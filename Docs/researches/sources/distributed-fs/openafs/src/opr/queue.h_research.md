# sources/distributed-fs/openafs/src/opr/queue.h

Purpose: generic intrusive doubly-linked circular queue implementation.

Important APIs/types/functions: `struct opr_queue` embeds next/prev links. Provides scan macros, init/zero/add/remove operations, append/prepend/insert, emptiness/on-queue checks, count, swap, split, splice, and container macros (`opr_queue_Entry`, `First`, `Last`, `Next`, `Prev`).

Control flow: all operations are inline pointer rewrites. Split/splice transfer ranges between circular queues and reinitialize sources as appropriate.

State and persistence: queue state is embedded in caller-owned objects. No allocation or persistence.

Dependencies/integration: used by `opr_dict`, `opr_cache`, and any code needing multi-queue membership. In kernel builds it avoids stdlib.

Risks and test signals: intrusive queues require each object to have separate link fields for separate queues. Removing an unlinked element or double insertion corrupts pointers. Tests should cover empty/single/multiple elements, safe scans with removal, split/splice, and swap.
