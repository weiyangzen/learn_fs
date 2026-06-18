<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/core.c

Purpose: implements the Qualcomm Crypto Engine platform driver, one-slot async request queue, hardware resource acquisition, version validation, and algorithm-family registration.

Important APIs and functions: `qce_handle_queue()` enqueues requests, handles backlog notification, serializes one active request in `qce->req`, and dispatches by crypto type through `qce_handle_request()`. `qce_req_done_work()` completes the active request and starts the next. `qce_async_request_enqueue()` and `qce_async_request_done()` are installed in `struct qce_device` for algorithm files. `qce_check_version()` rejects unsupported v5.0, sets BAM burst size, and derives pipe-pair ID from the RX DMA channel.

Control flow: probe maps MMIO, configures a 32-bit DMA mask, enables optional clocks, votes memory interconnect bandwidth, requests DMA channels and shared buffers, validates version, initializes mutex/work/queue, installs async callbacks, and registers all compiled algorithm families with devm cleanup.

State and persistence: `struct qce_device` stores queue, active request, result, MMIO base, clocks, interconnect path, DMA resources, burst size, pipe pair, and callbacks. Requests persist in `crypto_queue` until dispatched/completed.

Dependencies and integration: platform/OF matches `qcom,crypto-v5.1`, `qcom,crypto-v5.4`, and `qcom,qce`; optional clocks `core`, `iface`, `bus`; interconnect path `memory`; DMA helper; algorithm ops arrays gated by Kconfig.

Risks and test signals: queue depth is one, so backlog behavior and completion work ordering are important. Algorithm registration unwind in `devm_qce_register_algs()` uses the current `ops` variable when unregistering prior families, which is suspicious and should be reviewed. Test probe deferral, absent optional clocks, interconnect errors, unsupported v5.0, request backlog, each Kconfig algorithm combination, and remove/devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.c -->
