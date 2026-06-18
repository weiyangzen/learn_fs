## sources/distributed-fs/eos/namespace/interface/IContainerMDSvc.hh

Purpose: Defines the service interface for creating, fetching, caching, updating, deleting, and observing container metadata objects.

Important APIs and types: `IContainerMDChangeListener` reports `Updated`, `Deleted`, `Created`, and `MTimeChange`. `IContainerMDSvc` exposes initialize/configure/finalize, async/sync fetch by id/clock, cache drop, create, update store, remove, count, listeners, quota stats, lost+found, create-in-parent, file service wiring, container accounting, first-free-id, cache stats, and id blacklist.

Control flow: concrete services allocate ids, hydrate metadata from backing stores, keep caches coherent, call listeners on changes, and coordinate with file services/accounting.

State and persistence: service implementations own cache and backing-store persistence for container metadata. Interface also controls listener and quota/accounting links.

Dependencies and integration: depends on container/file metadata interfaces, `MDException`, `MDLocking`, cache statistics, quota stats, and change listeners. QuarkDB and in-memory implementations fulfill this contract.

Risks: comments mention adding file listeners in a container service, indicating inherited terminology. Callers must write-lock objects as required by implementation before store updates/removal. Listener ordering affects quota/accounting correctness.

Test signals: service lifecycle, async and sync fetch equivalence, cache drop, create/update/remove persistence, listener notifications, lost+found creation, id blacklisting, and cache statistics.
