<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.h

## Purpose

`ibmvscsi.h` defines the private data structures and constants for the IBM POWER virtual SCSI initiator driver. It bridges Linux SCSI host state, SRP events, VIO CRQ transport state, and persistent VIOSRP management buffers used by `ibmvscsi.c`.

## Important APIs, Types, and Constants

- `MAX_INDIRECT_BUFS` is the number of SRP direct descriptors that can be embedded alongside an indirect descriptor in `struct srp_cmd::add_data`.
- Queue and capacity defaults include `IBMVSCSI_MAX_REQUESTS_DEFAULT`, `IBMVSCSI_CMDS_PER_LUN_DEFAULT`, `IBMVSCSI_MAX_SECTORS_DEFAULT`, `IBMVSCSI_MAX_CMDS_PER_LUN`, and `IBMVSCSI_MAX_LUN`.
- `struct crq_queue` stores the DMA-mapped CRQ ring, current consumer index, DMA token, size, and spinlock.
- `struct srp_event_struct` is the per-request event slot. It contains the coherent transfer IU pointer, local IU image, associated `scsi_cmnd`, CRQ header, completion callback, SCSI completion callback, list node, timer, optional sync response pointer, and optional external indirect descriptor list.
- `struct event_pool` owns the event-slot array and coherent IU storage.
- `enum ibmvscsi_host_action` defines deferred work actions: none, reset, reenable, and unblock.
- `struct ibmvscsi_host_data` is the per-adapter aggregate: adapter list node, request-limit atomic, migration flag, current action, device pointer, event pool, CRQ queue, tasklet, sent list, SCSI host, work thread/waitqueue, MAD adapter info, capabilities buffer, and DMA addresses for persistent MAD data.

## Control Flow and State

The header does not implement logic, but its fields encode the driver control model. `crq_queue` is consumed by the interrupt tasklet. `event_pool` slots are allocated under SCSI host locking, sent through the CRQ, and returned from `ibmvscsi_handle_crq()` by pointer correlation. `ibmvscsi_host_data::action` is the handoff from interrupt/error contexts to the kthread that performs reset, reenable, or unblock work. `caps_addr` and `adapter_info_addr` keep pre-mapped management buffers available for login-time MAD exchange.

## Dependencies and Integration Points

The header imports Linux list/completion/interrupt primitives and `<scsi/viosrp.h>`, and forward-declares `struct scsi_cmnd` and `struct Scsi_Host`. All structures are internal to the `ibmvscsi` initiator and are consumed by the implementation file rather than exported as a public API.

## Risks and Edge Cases

- `srp_event_struct` embeds both local and DMA-visible IU pointers; confusing `iu`, `xfer_iu`, and `sync_srp` can cause stale DMA payloads or use-after-completion.
- `MAX_INDIRECT_BUFS` must remain consistent with the space available in the SRP IU additional data area.
- `request_limit` and `sent` list semantics depend on external locking in the C file, not on encapsulation in the structures.
- The host action enum is intentionally small; new actions must be handled in the work-thread predicates and dispatcher.

## Test Signals

Compile-time structure layout checks in `ibmvscsi.c` (`BUILD_BUG_ON(sizeof(evt_struct->iu.srp) != SRP_MAX_IU_LEN)`) indirectly validate these definitions. Runtime tests should exercise embedded and external indirect descriptor paths, kthread action transitions, and event pool exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/ibmvscsi.h -->
