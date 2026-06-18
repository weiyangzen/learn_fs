# sources/distributed-fs/coda/coda-src/lka/lka_private.h

Purpose: private data contract for LKA database handles. It defines `struct lkdb`, which links an rwcdb handle into Venus's lookaside list and tracks metadata/statistics.

State: `lkdb` stores list linkage, open rwcdb handle, allocated database name, allocated database directory, entry count, attempts, hits, and SHA verification failures. `LKA_VERSION_STRING` is the descriptor prefix used by both `mklka` and runtime binding.

Dependencies and risks: depends on `rwcdb`, `dllist`, and public `lka.h`. The descriptor string is the format gate; changing it without migration rejects older databases. Ownership is manual and centralized in `delete_lkdb`. Tests should cover descriptor compatibility and stats behavior.
