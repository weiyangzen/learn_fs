# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.c

### Purpose
`intel_gsc_uc.c` coordinates the GSC microcontroller lifecycle: early support detection, local memory allocation, pinned GSC context creation, delayed firmware loading, proxy servicing, HuC authentication sequencing, resume handling, teardown, and status printing.

### Important APIs, Types, And Functions
Exports include `intel_gsc_uc_init_early()`, `intel_gsc_uc_init()`, `intel_gsc_uc_fini()`, `intel_gsc_uc_flush_work()`, `intel_gsc_uc_resume()`, `intel_gsc_uc_load_start()`, and `intel_gsc_uc_load_status()`. Important internals are `gsc_work()`, `gsc_engine_supported()`, `gsc_allocate_and_map_vma()`, and `gsc_unmap_and_free_vma()`.

### Control Flow
Early init initializes `intel_uc_fw`, work item, support state, and an ordered workqueue when a GSC engine exists. Full init loads firmware metadata, allocates 4 MiB stolen memory and maps it, creates a pinned GSC engine context, initializes proxy opportunistically, and marks firmware loadable. `intel_gsc_uc_load_start()` sets `GSC_ACTION_FW_LOAD` under `gt->irq_lock` and queues work. The worker takes runtime PM, consumes action bits, uploads firmware, optionally authenticates HuC by GSC after GuC auth, runs software proxy, and marks firmware running only if proxy status reports normal.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is `struct intel_gsc_uc`: firmware metadata, release/security versions, local stolen VMA and iomap, pinned context, ordered workqueue, action bits, and proxy substate. Dependencies include GSC firmware/proxy helpers, GSC engine, stolen memory, runtime PM, HuC auth, uncore FWSTS registers, and debug printing. Integration points are i915 GT/uc init, resume, FLR cleanup through firmware upload, HuC authentication, MEI proxy, and debugfs. Risks include missing GSC engine, stolen allocation failure, worker/proxy ordering deadlocks, marking firmware running before proxy is established, and teardown races with queued work. Test signals include firmware status transitions, `gsc_info`, workqueue flush behavior, HuC auth completion, and FWSTS dumps.
