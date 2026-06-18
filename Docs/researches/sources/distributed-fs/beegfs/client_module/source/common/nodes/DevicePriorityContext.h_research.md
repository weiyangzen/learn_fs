# sources/distributed-fs/beegfs/client_module/source/common/nodes/DevicePriorityContext.h

Purpose: Defines the small context object used when ranking devices/NICs for connection priority.

Important APIs/types/functions: `DevicePriorityContext` contains `maxConns` and, under `BEEGFS_NVFS`, a GPU index associated with the first page.

Control flow: The header has no functions; selection code elsewhere passes this context into priority comparisons.

State and persistence behavior: Plain transient value object, not persisted.

Dependencies and integration points: Integrates connection/device selection with optional NVFS GPU locality hints.

Risks: Callers must initialize all fields for the active build configuration; otherwise priority logic can use stale stack values.

Test signals: Compile with and without `BEEGFS_NVFS`, and test device ranking with max connection limits and GPU locality where enabled.
