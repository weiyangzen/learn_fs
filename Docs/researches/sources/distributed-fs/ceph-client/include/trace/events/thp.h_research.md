# sources/distributed-fs/ceph-client/include/trace/events/thp.h

Purpose: Defines transparent huge page tracepoints for PMD state changes, updates, and migration-entry transitions.

Important APIs/types/functions: Declares event classes `hugepage_set`, `hugepage_update`, and `migration_pmd`, with concrete THP events built from those templates. They capture mm address, PMD/PTE values, and old/new state where relevant.

Control flow: Memory-management code invokes generated helpers while installing, modifying, or replacing huge PMD entries. The event classes centralize field layout so related operations share the same trace ABI.

State/persistence: No memory state is owned here. Events persist snapshots of page-table state into trace buffers for later debugging.

Dependencies/integration: Uses tracepoint infrastructure and MM/page-table types. It integrates with THP fault, collapse, split, and migration paths.

Risks: Page-table values are architecture-sensitive and timing-sensitive. Incorrect field types or formatting can hide THP races or produce misleading traces.

Test signals: Compile with THP enabled; run hugepage fault/collapse/migration tests while enabling `thp:*` events and confirm PMD transitions are emitted.
