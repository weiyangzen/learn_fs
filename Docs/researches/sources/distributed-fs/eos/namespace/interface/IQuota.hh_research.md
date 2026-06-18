## sources/distributed-fs/eos/namespace/interface/IQuota.hh

Purpose: Defines quota accounting interfaces for per-container quota nodes and the quota stats manager.

Important APIs and types: `IQuotaNode` wraps `QuotaNodeCore` and exposes per-user/per-group logical space, physical space, and file counts, plus `addFile`, `removeFile`, `meld`, uid/gid enumeration, and core replace/update. `IQuotaStats` manages nodes, provides all ids, and registers a physical-size mapper.

Control flow: file/container accounting calls quota nodes to add/remove files and merge usage; quota stats registers/removes nodes keyed by container id. `getPhysicalSize` calls the registered mapper and throws if none is configured.

State and persistence: `IQuotaNode` stores a quota stats pointer, container id, and `QuotaNodeCore`. Concrete implementations decide whether accounting state is persisted, cached, or recomputed.

Dependencies and integration: depends on file/container metadata and QuarkDB `QuotaNodeCore`. Integrated with services via `setQuotaStats` and view quota-node registration.

Risks: `IQuotaNode` keeps raw quota stats pointer. `getPhysicalSize` throws a default `MDException` with no errno specialization when mapper is missing. Implementations must keep logical and physical accounting consistent with file layout/replica changes.

Test signals: add/remove file accounting, physical-size mapper registration/failure, meld semantics, uid/gid set enumeration, core replace/update, node registration/removal, and quota node id listing.
