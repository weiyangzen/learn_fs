## sources/distributed-fs/ceph-client/include/linux/bsg-lib.h

**Purpose:** This header defines the block SCSI generic (BSG) helper-library interface used by transport drivers that expose request/reply command queues through the block layer.

**Important APIs/types/functions:** `struct bsg_buffer` describes DMA payload scatterlists. `struct bsg_job` carries device pointer, `kref`, timeout, transport-specific request/reply buffers and lengths, request/reply payloads, result, received payload length, bidi request/bio, and driver-private `dd_data`. Callback types are `bsg_job_fn` and `bsg_timeout_fn`. Functions include `bsg_job_done()`, `bsg_setup_queue()`, `bsg_remove_queue()`, `bsg_job_get()`, and `bsg_job_put()`.

**Control flow, state, persistence:** Drivers create a queue with `bsg_setup_queue()`, receive jobs through the supplied job callback, fill reply/result fields, and complete with `bsg_job_done()`. Job lifetime is reference-counted; queue lifetime is explicit. No persistent storage is defined here.

**Dependencies/integration:** Includes `linux/blkdev.h`, integrates with request queues, queue limits, scatterlists, block error handling timeouts, and transport-specific command protocols.

**Risks and test signals:** Risks are reference leaks, double completion, incorrect reply lengths, scatterlist direction mistakes, timeout races, and bidi request ownership errors. Test signals include SG_IO passthrough tests, timeout/error injection, queue teardown under in-flight jobs, refcount debugging, and DMA mapping checks.
