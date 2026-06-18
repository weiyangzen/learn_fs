# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/fault.c

Purpose: handles SPU class 0 and class 1 exceptions for `spu_run()`. It either reports SPE events to the caller through `event_return` or converts them into Linux signals.

Important functions: `spufs_handle_class0()` handles DMA alignment, invalid DMA command, and SPU error interrupts. `spufs_handle_class1()` handles address-translation faults from MFC accesses. `spufs_handle_event()` centralizes event-vs-signal behavior and restarts DMA for recoverable storage faults.

Control flow: class 1 handling records the faulting EA/DSISR, switches utilization to iowait, releases the context mutex before calling `hash_page()` or `copro_handle_mm_fault()`, reacquires `state_mutex`, clears saved fault registers, updates minor/major fault counters, restarts DMA when possible, or raises a storage event. Class 0 clears pending bits after signaling and returns `-EIO`.

State and dependencies: updates `ctx->stats` and physical SPU stats, uses `ctx->csa.class_*` fields captured by callbacks, and depends on PowerPC hash MMU and copro fault helpers. Risks include races while the context is saved or rescheduled during fault handling, incorrect signal address for alignment faults, and incomplete event delivery if `SPU_CREATE_EVENTS_ENABLED` callers do not drain events. Test signals include induced invalid DMA, page faults, access-denied faults, and event-enabled `spu_run` returns.
