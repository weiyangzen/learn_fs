## sources/distributed-fs/ceph-client/arch/arm/xen/p2m.c

### Purpose
Maintains ARM Xen physical-to-machine mappings for foreign grant pages using an RB tree.

### Important APIs, Types, And Functions
Defines `struct xen_p2m_entry`, global `phys_to_mach`, lock `p2m_lock`, and functions `__pfn_to_mfn`, `set_foreign_p2m_mapping`, `clear_foreign_p2m_mapping`, `__set_phys_to_machine_multi`, `__set_phys_to_machine`, and `p2m_init`.

### Control Flow
Mapping updates allocate an entry, take the write lock, insert into the RB tree by PFN, or remove an existing range when setting `INVALID_P2M_ENTRY`. Lookups take the read lock and find an entry whose PFN range covers the query. Grant map completion records MFNs; if recording fails it immediately unmaps that grant reference.

### State, Persistence, And Dependencies
Persistent state is the in-memory RB tree of PFN-to-MFN ranges protected by `p2m_lock`. Dependencies include Xen grant operations, RB tree APIs, spin/rw locks, and invalid mapping constants.

### Integration Points
Used by Xen DMA, grant-table, and page translation helpers to distinguish local and foreign machine frames.

### Risks
Overlapping or duplicate PFN entries are rejected but range-overlap beyond identical starts is not broadly merged. GFP_NOWAIT allocation can fail in mapping paths. Bad cleanup leaves stale foreign mappings and DMA/cache decisions wrong.

### Test Signals
Map/unmap grant pages repeatedly, run concurrent p2m lookups, inject allocation failures, and verify `__pfn_to_mfn` returns invalid after unmap.
