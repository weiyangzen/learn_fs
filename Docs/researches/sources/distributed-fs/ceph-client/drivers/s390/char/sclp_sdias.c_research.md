<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.c

**Purpose:** `sclp_sdias.c` implements "store data in absolute storage" for dump IPL paths, mainly to copy FCP dump data from HSA into absolute storage.

**Important APIs and functions:** Public functions are `sclp_sdias_blk_count()`, `sclp_sdias_copy()`, and init `sclp_sdias_init()`. `sdias_sclp_send()` retries SCLP request submission and waits for accepted and, in async mode, done completions. `sclp_sdias_receiver_fn()` copies asynchronous event data into `sdias_evbuf`. `sclp_sdias_init_sync()` and `_async()` probe supported completion mode.

**Control flow, state, and persistence:** Init only runs for dump IPL. It allocates one shared DMA SCCB page, registers a debug area, then tries synchronous mode without a receiver and asynchronous mode with `EVTYP_SDIAS_MASK` receive. Operations are serialized by `sdias_mutex` and reuse the shared SCCB. Block count sends EQ_SIZE, while copy sends EQ_STORE_DATA with destination physical address, first block, block count, and 64-bit ASA size.

**Dependencies and integration:** It depends on SCLP Write Event Data, dump IPL detection, debug feature, completions, scheduler timeouts, and SDIAS structures in `sclp_sdias.h`.

**Risks and test signals:** Risks include fixed event ID reuse, completion objects not reinitialized between requests, long retry loops, async event races, shared SCCB lifetime, and partial-store semantics. Tests should cover non-dump no-op init, sync and async probing, block count response statuses, full/partial/no-data copy statuses, and retry exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.c -->
