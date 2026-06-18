# sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_rpmsg.c

## Purpose
This file implements the RPMsg transport for CDX controller firmware communication. It attaches to the remote R5 processor, creates an RPMsg endpoint named `mcdi_ipc`, forwards MCDI requests to firmware, and feeds firmware responses back into the MCDI engine.

## Important APIs, Types, and Functions
Exported internal APIs are `cdx_rpmsg_send()`, `cdx_setup_rpmsg()`, and `cdx_destroy_rpmsg()`. Important callbacks are `cdx_rpmsg_probe()`, `cdx_rpmsg_remove()`, `cdx_rpmsg_cb()`, and `cdx_rpmsg_post_probe_work()`. Remoteproc helpers are `cdx_attach_to_rproc()` and `cdx_detach_to_r5()`.

## Control Flow
Controller probe calls `cdx_setup_rpmsg()`, which parses the `xlnx,rproc` phandle, boots/attaches to the remote processor, stores the controller pointer in the RPMsg ID table's `driver_data`, initializes work, and registers the RPMsg driver. When the `mcdi_ipc` channel probes, an endpoint is created, `struct cdx_mcdi` receives `ept` and `rpdev`, and deferred work registers the CDX controller with the bus. Incoming RPMsg payloads are length-checked and passed to `cdx_mcdi_process_cmd()`.

## State and Persistence Behavior
Transport state lives in `struct cdx_mcdi`: remoteproc pointer `r5_rproc`, RPMsg endpoint `ept`, RPMsg device `rpdev`, and work item. The static RPMsg ID table temporarily stores one controller pointer in `driver_data`, making this transport effectively single-controller during setup.

## Dependencies and Integration Points
It depends on `remoteproc`, `rpmsg`, OF phandles, the MCDI core, and controller/bus lifecycle callbacks. It is the concrete `mcdi_request` transport used by `mcdi.c`.

## Risks
The static `driver_data` handoff is fragile for multiple controllers probing concurrently. `cdx_rpmsg_send()` allocates a combined buffer for every command and does not retry RPMsg send failures. `cdx_attach_to_rproc()` calls `rproc_boot()` but teardown uses `rproc_detach()`, so semantics depend on the remoteproc provider. Remove flushes post-probe work before unregistering the controller, which is necessary to avoid registering after teardown. Payload length validation only checks upper bound and trusts MCDI parsing for structure.

## Test Signals
Exercise deferred probe when the remote processor is unavailable, RPMsg endpoint creation/removal, command send failure injection, oversized response rejection, controller registration only after RPMsg probe, and teardown with in-flight work or MCDI commands.
