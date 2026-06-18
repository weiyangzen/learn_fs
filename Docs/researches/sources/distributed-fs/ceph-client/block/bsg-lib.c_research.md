# sources/distributed-fs/ceph-client/block/bsg-lib.c

Purpose: provides a helper library for block SCSI generic (BSG) transport queues. It turns SG_IO v4 userspace commands into blk-mq driver requests, maps payload buffers, manages `struct bsg_job` lifetime, and creates/removes BSG request queues for lower-level drivers.

Important APIs and functions: private `struct bsg_set` wraps a `blk_mq_tag_set`, registered `bsg_device`, job callback, and timeout callback. Public functions are `bsg_job_put()`, `bsg_job_get()`, `bsg_job_done()`, `bsg_remove_queue()`, and `bsg_setup_queue()`. Core internals include `bsg_transport_sg_io_fn()`, `bsg_teardown_job()`, `bsg_prepare_job()`, `bsg_queue_rq()`, `bsg_init_rq()`, `bsg_exit_rq()`, and `bsg_timeout()`.

Control flow: `bsg_setup_queue()` creates a blocking blk-mq queue with per-request `struct bsg_job` storage and registers a `/dev/bsg` node through `bsg_register_queue()`. SG_IO v4 validates protocol/subprotocol and `CAP_SYS_RAWIO`, allocates request and optional bidirectional request, copies the command block from userspace, maps dout/din buffers, executes the request synchronously, copies reply data back, unmaps bios, and frees requests. Driver-submitted jobs flow through `bsg_queue_rq()`, which prepares scatterlists, takes device references, invokes the driver job callback, and completes through `bsg_job_done()`.

State and persistence: queue state lives in `bsg_set`, blk-mq tag set storage, per-request `bsg_job`, scatterlist allocations, reply buffers, and device references. No persistent storage exists.

Dependencies and integration points: depends on blk-mq, BSG core registration from `bsg.c`, SG_IO v4 structures, SCSI sense/status helpers, user copy APIs, request timeout and fake-timeout support, and driver-provided job/timeout callbacks.

Risks and test signals: this is a privileged passthrough path, so user pointer validation, buffer mapping/unmapping symmetry, bidirectional request cleanup, kref/device-reference balance, and timeout behavior are critical. Test invalid protocol/subprotocol, missing `CAP_SYS_RAWIO`, unidirectional and bidirectional transfers, user copy failures, driver job errors, fake timeouts, queue removal with in-flight jobs, and per-request reply allocation failures.
