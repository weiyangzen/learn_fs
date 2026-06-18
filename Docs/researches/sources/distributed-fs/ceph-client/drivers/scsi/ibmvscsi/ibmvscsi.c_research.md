<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.c

## Purpose

`ibmvscsi.c` is the IBM POWER virtual SCSI initiator driver. It presents a Linux `Scsi_Host` for a VIO `"vscsi"` device and speaks SRP over the platform Command/Response Queue (CRQ) hypervisor transport. The driver converts SCSI midlayer commands into SRP information units, advertises client capabilities through VIOSRP management datagrams, handles partition migration and adapter reset events, and exposes host metadata through SRP transport/sysfs attributes.

## Important APIs, Types, and Functions

- Module parameters tune topology and behavior: `max_id`, `max_channel`, `init_timeout`, `max_requests`, `fast_fail`, and `client_reserve`.
- `ibmvscsi_init_crq_queue()`, `ibmvscsi_reset_crq_queue()`, `ibmvscsi_reenable_crq_queue()`, and `ibmvscsi_release_crq_queue()` own CRQ page allocation, DMA mapping, hypervisor `H_REG_CRQ`/`H_FREE_CRQ`/`H_ENABLE_CRQ`, IRQ setup, tasklet setup, and teardown.
- `initialize_event_pool()`, `get_event_struct()`, and `free_event_struct()` manage the fixed pool of SRP event slots and coherent IU storage used as CRQ correlation tokens.
- `ibmvscsi_queuecommand_lck()` builds SRP_CMD IUs, maps scatterlists with `scsi_dma_map()`, formats direct or indirect SRP descriptors, and sends the event through `ibmvscsi_send_srp_event()`.
- `ibmvscsi_send_srp_event()` enforces server request-limit credit, reserves final slots for task management, copies the IU into DMA-visible storage, links the event into `hostdata->sent`, installs optional timers, and calls `H_SEND_CRQ`.
- `ibmvscsi_handle_crq()` dispatches initialization messages, transport events, and command responses. It validates correlation tokens against the event pool, updates request credits, calls the event completion callback, removes the event from `sent`, and frees it.
- Management sequence functions include `send_mad_adapter_info()`, `adapter_info_rsp()`, `enable_fast_fail()`, `send_mad_capabilities()`, `capabilities_rsp()`, `send_srp_login()`, and `login_rsp()`.
- Error recovery hooks are `ibmvscsi_eh_abort_handler()`, `ibmvscsi_eh_device_reset_handler()`, `ibmvscsi_eh_host_reset_handler()`, and `ibmvscsi_host_reset()`.
- Probe/remove and runtime integration are handled by `ibmvscsi_probe()`, `ibmvscsi_remove()`, `ibmvscsi_resume()`, `ibmvscsi_module_init()`, and `ibmvscsi_module_exit()`.

## Control Flow

Probe allocates a SCSI host, maps persistent capabilities and adapter-info buffers, starts a reset work thread, registers and enables the CRQ, initializes the event pool, registers with the SCSI midlayer and SRP transport, sends the initial CRQ init message, waits up to `init_timeout` for a positive request limit, and scans the host if login completed.

CRQ interrupts are edge-oriented. `ibmvscsi_handle_event()` disables VIO interrupts and schedules `srp_task`; `ibmvscsi_task()` drains all valid CRQ entries, clears their valid bits with barriers, reenables interrupts, and rechecks the queue to avoid losing arrivals between drain and enable.

The normal I/O path is SCSI midlayer `queuecommand` -> event allocation -> SRP_CMD construction -> data descriptor mapping -> request-limit accounting -> `H_SEND_CRQ` -> CRQ response interrupt -> `handle_cmd_rsp()` -> SCSI completion. For multiple SG entries, the driver embeds up to `MAX_INDIRECT_BUFS` descriptors in the IU and allocates an external coherent descriptor table for larger lists, using the table descriptor VA to point either into the IU or the external table.

Initialization is a management handshake: adapter info is exchanged first; AIX servers may get an enable-fast-fail MAD; then capabilities are exchanged; finally SRP login negotiates the request-limit delta and unblocks queued SCSI requests. CRQ transport events block SCSI requests and either reenable after migration (`format == 0x06`) or reset the CRQ. The kthread serializes reset, reenable, and unblock actions outside interrupt context.

## State and Persistence

Persistent per-adapter state lives in `struct ibmvscsi_host_data`: CRQ queue, event pool, `sent` list, request-limit atomic, action state for the work thread, cached MAD adapter information, capabilities, and DMA addresses for persistent MAD buffers. Module-global state stores local partition name/number and the adapter list. There is no on-disk persistence; state is recreated at probe and module load. Runtime-visible state is exposed through SCSI host attributes such as `vhost_loc`, `vhost_name`, `srp_version`, `partition_name`, `partition_number`, `mad_version`, and `os_type`.

`request_limit` is the main flow-control state. It starts at `-1`, moves to `0` while login is pending, and is set to the server-provided delta after `SRP_LOGIN_RSP`; responses add their `req_lim_delta`. Reset paths set it back to `0` or `-1` and purge outstanding requests.

## Dependencies and Integration Points

The file depends on PowerPC VIO and PHYP hypercalls (`H_SEND_CRQ`, `H_REG_CRQ`, `H_FREE_CRQ`, `H_ENABLE_CRQ`), Open Firmware properties for partition metadata and location codes, Linux DMA mapping APIs, tasklets, kthreads, timers, SCSI midlayer APIs, and `scsi_transport_srp`. Protocol definitions come from `<scsi/viosrp.h>` and the local `ibmvscsi.h`.

The driver registers a `vio_driver` for `"IBM,v-scsi"`, a `scsi_host_template`, and an SRP transport template. It reports desired DMA memory to VIO through `get_desired_dma()`.

## Risks and Edge Cases

- Request credit accounting is concurrency-sensitive. `ibmvscsi_send_srp_event()` assumes `host_lock` protection, and the final two request slots are reserved for reset/abort except for very small server limits.
- Correlation tokens are raw event pointers echoed by the hypervisor/server. The file validates pointer range/alignment and free state, but stale or duplicate tokens are serious protocol errors.
- The CRQ interrupt path relies on memory barriers around valid bits and on drain/reenable/recheck sequencing to avoid lost edge-triggered interrupts.
- External indirect descriptor allocation can fail under constrained memory; CMO firmware suppresses some error logs but returns busy.
- Timeout handling for internal commands resets the whole adapter connection.
- Probe error paths must unwind in the right order: CRQ, tasklet, kthread, persistent DMA mappings, event pool, SCSI host, and SRP transport.
- Migration and partner failure handling purposely purges or requeues requests; regressions here can cause hangs during LPAR mobility or stale I/O completions.

## Test Signals

Useful validation signals include successful module load only when `FW_FEATURE_VIO` is present, CRQ init/login logs, `SRP_LOGIN succeeded`, nonzero request-limit before scan, SCSI scan/device discovery, host sysfs attributes populated with server adapter data, clean unload with no event-pool in-use warning, abort/LUN reset paths returning `SUCCESS`, simulated `H_CLOSED` causing host-busy/retry, migration CRQ causing reenable and re-login, and DMA mapping failure tests returning busy without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.c -->
