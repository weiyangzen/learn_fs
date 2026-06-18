## sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/trove-ledger.h

Purpose: Declares the opaque handle-ledger interface layered above extent lists and below the collection-wide handle manager.

Important APIs and types: The header forward-declares `struct handle_ledger` and exposes functions for initialization, debug display, dump/free, adding legal extents, removing a specific handle, allocating/freeing handles, range-constrained allocation, peeking, setting cutoff/timeout, and retrieving free-count statistics. The enum reserves logical backing-store handles for free, recently-freed, and overflow extent lists.

Control flow: Callers initialize one ledger per collection, add valid handle extents, remove already-used handles, then allocate from or return to the ledger. The ledger controls whether returned handles become available immediately or after delayed reuse.

State and persistence: The state is intentionally opaque, but implementation currently uses in-memory extent lists. The enum and dump API indicate an intended persistent ledger format, while the active code does not implement it.

Dependencies and integration points: Includes `trove-types.h`, `trove-extentlist.h`, and `pvfs2-internal.h`. It is consumed by `trove-handle-mgmt.c`; DBPF code indirectly uses it through the higher-level manager.

Risks: The header gives callers no ownership details for the opaque object except that `trove_handle_ledger_free` must be called. `trove_handle_ledger_dump` is declared as if available but always fails in implementation. Return value conventions are mixed because allocation returns `TROVE_HANDLE_NULL` while many helpers return integer status.

Test signals: Compile tests should catch inline/export expectations. Integration tests should ensure ledger initialization, extent setup, allocation, free, timeout, and statistics behave consistently through `trove-handle-mgmt.c`.
