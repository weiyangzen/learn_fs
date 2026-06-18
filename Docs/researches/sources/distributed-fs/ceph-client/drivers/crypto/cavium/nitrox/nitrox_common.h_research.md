# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_common.h

Purpose: declares shared NITROX driver interfaces across PCI main, algorithm, request manager, software resource, and device-reference code.

Important APIs: algorithm registration functions, context pool functions `crypto_alloc_context()`/`crypto_free_context()`, device reference helpers `nitrox_get_first_device()`/`nitrox_put_device()`, software init/cleanup, response tasklet `pkt_slc_resp_tasklet()`, request submission `nitrox_process_se_request()`, and backlog work `backlog_qflush_work()`.

Control flow and state: this header has no state but defines the cross-module contract: transforms acquire a device and context, algorithms submit SE requests, interrupts schedule response processing, and backlog work drains queued commands.

Dependencies and integration points: includes `nitrox_dev.h` and `nitrox_req.h`, so it couples public helpers to both device and request layouts. It is the common include for HAL/lib/ISR/algorithm modules.

Risks and test signals: risks include broad include coupling, exported request-manager helpers requiring matching object membership, and callers needing clear lifetime/refcount ordering. Test signals include successful module link, algorithm init acquiring devices only when ready, and interrupt tasklets resolving to request-manager response processing.
