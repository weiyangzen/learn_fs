<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/core.h

Purpose: declares QCE core device state and the algorithm-family callback interface.

Important types: `struct qce_device` owns the crypto queue, mutex, completion work, active request/result, MMIO base, device pointer, clocks, interconnect path, DMA data, burst size, pipe-pair ID, and callbacks used by algorithms to enqueue and finish requests. `struct qce_algo_ops` defines a crypto type plus register/unregister and async request handler callbacks for skcipher, ahash, and AEAD families.

Control flow and integration: core builds a static array of `qce_algo_ops` from enabled Kconfig families, registers them at probe, and uses `async_req_handle` to process dequeued crypto requests. Algorithm files use the callbacks in `qce_device` to share queue and completion handling.

State and persistence: a `qce_device` instance persists for the platform device lifetime and serializes all algorithm requests through one active request pointer.

Dependencies: mutex/workqueue primitives, QCE DMA data, Linux crypto async request types via included files.

Risks and test signals: all algorithms share one hardware queue, so active request ownership must remain consistent after setup errors and DMA callbacks. Test mixed concurrent SHA/skcipher/AEAD submissions and errors before `async_req_done()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.h -->
