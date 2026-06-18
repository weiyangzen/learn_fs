# sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.c

Purpose: implements the blk-mq block driver for s390 storage class memory increments, batching block requests into EADM asynchronous operation blocks with MSB/AIDAW descriptors.

Important APIs/types/functions: global pools are `inactive_requests` and `aidaw_pool`; `struct scm_request` wraps an AOB and request array. Key functions include `scm_alloc_rqs()`, `scm_request_fetch()`/`done()`, `scm_request_prepare()`, `scm_blk_request()`, `scm_blk_irq()`, `scm_blk_handle_error()`, `scm_blk_dev_setup()`, `scm_blk_dev_cleanup()`, `scm_blk_set_available()`, and module init/exit.

Control flow: module init registers a dynamic major, preallocates request/AIDAW resources, sets up s390 debug, and registers the SCM bus driver. Per-device setup allocates a blk-mq tag set and disk. Queueing aggregates up to `nr_requests_per_io` block requests into one AOB, maps pages through AIDAWs, starts EADM, and completes/requeues original requests from the interrupt callback.

State and persistence behavior: persistent state is block-layer device state only. Runtime state includes preallocated request objects, queued request counts, per-device `SCM_OPER` vs `SCM_WR_PROHIBIT`, pending hctx aggregate request, and debug logs. Write-prohibited state is set after an EADM response and cleared by SCM availability notification.

Dependencies and integration points: integrates blk-mq with s390 EADM (`eadm_start_aob`, `struct aob/msb/aidaw`), the SCM bus driver in `scm_drv.c`, s390 debug, DMA64 address conversion, mempools, and Linux request completion/requeue APIs.

Risks and test signals: request pooling bounds throughput and can return `BLK_STS_RESOURCE`; AIDAW capacity must match queue limits; `nr_requests_per_io` is limited to 1..64 but `nr_requests` can stress memory. Test read/write batches, resource exhaustion, fake timeouts, write-prohibited responses, availability recovery, hot remove with queued I/O, and init failure cleanup.
