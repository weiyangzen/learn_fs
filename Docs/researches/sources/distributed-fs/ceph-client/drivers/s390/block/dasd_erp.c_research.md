# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_erp.c

## Purpose
This file provides the default DASD error-recovery primitives shared by DASD disciplines. It allocates ERP requests from per-device ERP memory, retries requests when no specialized recovery exists, collapses ERP chains back to the original request, and delegates sense-data logging to the active discipline.

## Important APIs, Types, and Functions
`dasd_alloc_erp_request()` and `dasd_free_erp_request()` manage `struct dasd_ccw_req` objects from `device->erp_chunks`. `dasd_default_erp_action()` is the generic retry action. `dasd_default_erp_postaction()` frees all ERP requests in a chain and transfers final success/failure state back to the original CQR. `dasd_log_sense()` handles user-visible sense logging, while `dasd_log_sense_dbf()` logs to s390 debug feature. The allocation, free, default action, default postaction, and sense logging helpers are exported.

## Control Flow
ERP allocation validates that data and CCW arrays fit within a page, computes an aligned object layout containing `dasd_ccw_req`, optional CCWs, and optional data, then allocates from the device ERP chunk pool under `device->mem_lock`. It initializes list heads, zeroes memory, stores the discipline magic after converting it to EBCDIC, sets `DASD_CQR_FLAGS_USE_ERP`, and takes a DASD device reference.

The default ERP action either resets a request to `DASD_CQR_FILLED` for retry, refreshing the path mask unless this is a path-verification request, or marks it failed when retries are exhausted. Postaction starts from the current ERP head, remembers final timing and start device, frees every ERP request until it reaches the original request (`refers == NULL`), and marks the original done or failed. Sense logging checks timeout and transport errors specially, then calls the discipline's `dump_sense` or `dump_sense_dbf` callback when available.

## State and Persistence
The file stores no global state. ERP request state lives in per-device chunk pools, CQR chains, CQR status fields, retry counters, path masks, and device references. There is no persistence beyond the lifetime of recovery processing.

## Dependencies and Integration Points
This file depends on DASD core request structures, per-device memory chunks, device refcounting, ccw layout, s390 debug support, EBCDIC conversion, and discipline callbacks. ECKD and FBA both select the default ERP postaction; FBA uses the default action directly, while ECKD chooses between 3990-specific and default ERP based on controller type.

## Risks and Test Signals
Risk areas include BUG_ON page-size assumptions for ERP payloads, matching every successful allocation with the device refcount decrement in `dasd_free_erp_request()`, preserving original request timing/status correctly while freeing a chain, and avoiding retries on stale path masks. Test signals include allocation failure paths, ERP chain cleanup with multiple linked requests, retry exhaustion logs, timeout and transport-error sense handling, discipline-specific dump callback invocation, and refcount/chunk leak checks under repeated recovery.
