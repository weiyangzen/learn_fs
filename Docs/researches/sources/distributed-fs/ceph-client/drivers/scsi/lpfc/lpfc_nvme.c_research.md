# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.c

## Purpose

`lpfc_nvme.c` implements the initiator-side NVMe over Fibre Channel binding for the Broadcom/Emulex lpfc SLI-4 driver. It registers an `nvme_fc_port_template` with the Linux NVMe-FC transport, translates transport callbacks into lpfc work queue entries, manages local and remote NVMe port lifetime, sends and receives NVMe link service traffic, submits NVMe FCP I/O, and handles abort, completion, drain, and reset cleanup paths.

The file is tightly coupled to the lpfc node discovery model. NVMe remote ports are bound to `struct lpfc_nodelist` instances through `ndlp->nrport`, and I/O is allowed only when the node type and state match the expected NVMe target or initiator role. It shares SLI-4 queue, XRI, SGL, WQE, completion, and ABTS infrastructure with the SCSI/FCP side while keeping NVMe-specific statistics and completion semantics.

## Important APIs, Types, and Functions

The primary public entry points are `lpfc_nvme_create_localport`, `lpfc_nvme_destroy_localport`, `lpfc_nvme_update_localport`, `lpfc_nvme_register_port`, `lpfc_nvme_rescan_port`, `lpfc_nvme_unregister_port`, `lpfc_sli4_nvme_pci_offline_aborted`, `lpfc_sli4_nvme_xri_aborted`, `lpfc_nvme_wait_for_io_drain`, `lpfc_nvme_cancel_iocb`, `lpfc_nvme_flush_abts_list`, and `lpfc_nvmels_flush_cmd`. They are invoked from lpfc initialization, discovery, error recovery, and queue cleanup code.

The transport callback table `lpfc_nvme_template` wires the NVMe-FC host transport to local driver methods: local and remote port delete, queue create/delete, link-service request and abort, FCP I/O submit and abort, and link-service response transmit. The template also advertises hardware queue count, SGL segment limits, DMA boundary, and private data sizes for lpfc local port, remote port, and per-FCP request state.

`lpfc_nvme_create_queue` and `lpfc_nvme_delete_queue` allocate and free a small `lpfc_nvme_qhandle`, mapping NVMe queue index `qidx` to an lpfc hardware queue index. Queue zero is the admin queue and maps to hardware queue zero; I/O queues map modulo the configured maximum hardware queues. The handle also captures the CPU at creation time for diagnostics.

`__lpfc_nvme_ls_req`, `lpfc_nvme_ls_req`, `lpfc_nvme_gen_req`, `lpfc_nvme_ls_req_cmp`, `__lpfc_nvme_ls_req_cmp`, `__lpfc_nvme_ls_abort`, and `lpfc_nvme_ls_abort` implement outgoing NVMe link services. They allocate BPL DMA wrappers, build `CMD_GEN_REQUEST64_WQE` requests with NVMe FC type and ELS4 request R_CTL, hold an ndlp reference through completion, invoke the transport `done` callback, and cancel outstanding LS requests by scanning the nvmels work queue completion list.

`lpfc_nvme_handle_lsreq` handles unsolicited NVMe LS requests for the initiator personality by forwarding the payload to `nvme_fc_rcv_ls_req`; responses are sent by `lpfc_nvme_xmt_ls_rsp`, which reuses the generic response implementation from `lpfc_nvmet.c`.

The I/O submission path is `lpfc_nvme_fcp_io_submit` -> `lpfc_get_nvme_buf` -> `lpfc_nvme_prep_io_cmd` -> `lpfc_nvme_prep_io_dma` -> `lpfc_sli4_issue_wqe`. `lpfc_nvme_adj_fcp_sgls` rewrites the command and response SGEs for NVMe command IU and response IU semantics, with optional embedded command support. Completion flows through `lpfc_nvme_io_cmd_cmpl`, which decodes CQE status, reconstructs NVMe ERSP IUs when needed, reports transport status, handles exchange-busy deferral, updates congestion-management feedback, and releases the lpfc I/O buffer.

Abort handling is split between transport-requested aborts and firmware/reset-driven abort completions. `lpfc_nvme_fcp_abort` validates that the request still matches the lpfc buffer and is still on the completion queue before issuing `lpfc_sli4_issue_abort_iotag`. `lpfc_nvme_abort_fcreq_cmpl` releases the abort WQE. `lpfc_sli4_nvme_xri_aborted` and `lpfc_sli4_nvme_pci_offline_aborted` complete deferred aborted I/O and return buffers once the XRI is released.

## Control Flow

Initialization registers a local NVMe initiator port with `nvme_fc_register_localport` after filling `nvme_fc_port_info` from the vport WWNN/WWPN. The registration allocates transport-side localport storage and the lpfc private `lpfc_nvme_lport`. The driver then stores `vport->localport`, sets `vport->nvmei_support`, and clears all per-lport counters. Later FCID changes call `lpfc_nvme_update_localport` to update the localport port id and role, using discovery role when DID is zero and initiator role otherwise.

Discovery registers remote NVMe ports with `nvme_fc_register_remoteport`. `lpfc_nvme_register_port` builds `nvme_fc_port_info` from the ndlp DID, WWPN, WWNN, devloss timeout, and PRLI-derived target, initiator, or discovery capabilities. It handles reregister races by checking `ndlp->nrport`, preserving or acquiring ndlp references, clearing `NVME_XPT_UNREG_WAIT`, setting `NVME_XPT_REGD`, and rebinding the returned transport private rport to the current ndlp. Unregistration sets `NVME_XPT_UNREG_WAIT`, optionally forces devloss to zero during unload or HBA error, calls `nvme_fc_unregister_remoteport`, breaks `ndlp->nrport`, and drops the registration reference.

FCP I/O submission starts in the NVMe transport callback with localport, remoteport, queue handle, and `nvmefc_fcp_req`. The function rejects missing private data, driver unload, HBA I/O flush, missing request private area, missing ndlp, and unmapped target nodes. Keep-alive commands on admin queue can be expedited when resources are scarce. CMF read accounting can reject or time I/O. Shared ndlp queue depth is enforced unless expedited. Hardware queue selection follows either the transport queue mapping or CPU-based scheduling. A driver I/O buffer is allocated, request-private state is linked, optional VMID tags are attached, WQE and SGLs are prepared, and the WQE is issued to the selected hardware queue.

Completion reconstructs the NVMe transport view from lpfc CQEs. `CQE_CODE_NVME_ERSP` produces a synthetic `nvme_fc_ersp_iu` with command id, SQ head, SQ id, completion result, and transferred length. Plain success reports bytes placed and no response IU. `IOSTAT_FCP_RSP_ERROR` may actually be a valid NVMe ERSP of length `LPFC_NVME_ERSP_LEN`; otherwise it is logged as a protocol error. Local rejects and other errors become `NVME_SC_INTERNAL`, with PCI-offline and SLI-down tracked as offline conditions so exchange-busy handling does not defer forever. If XB is set and not offline, the buffer is put on the NVMe ABTS list rather than immediately returned.

Shutdown and error recovery are deliberately asynchronous. Localport unregister stores a stack completion in `lport->lport_unreg_cmp`, calls `nvme_fc_unregister_localport`, and waits in `lpfc_nvme_lport_unreg_wait`, periodically logging pending I/O, SCSI/NVMe ABTS buffers, and NVMe LS commands. Reset drains call `lpfc_nvme_wait_for_io_drain`, `lpfc_nvme_cancel_iocb`, `lpfc_nvme_flush_abts_list`, and `lpfc_nvmels_flush_cmd` to flush or synthesize completions.

## State and Persistence Behavior

The file maintains runtime kernel state only; there is no durable on-disk persistence. Persistent-like behavior is embodied in transport registrations, node references, queue mappings, and outstanding WQE/XRI ownership.

Important mutable state includes `vport->localport`, `vport->nvmei_support`, `ndlp->nrport`, `ndlp->fc4_xpt_flags`, `ndlp->cmd_pending`, `lpfc_nvme_lport` atomic counters, `lpfc_nvme_rport` bindings, per-request `lpfc_nvme_fcpreq_priv->nvme_buf`, I/O buffer `flags`, `nvmeCmd`, `ndlp`, hardware queue index, and ABTS lists. The code uses spinlocks on ndlp, hbalock, ring locks, and per-buffer locks to protect races between transport callbacks, completions, aborts, and driver teardown.

Reference ownership is central. Outgoing LS WQEs hold an ndlp reference until completion. Remote-port registration either reuses an existing nrport reference or takes a new ndlp reference and drops it at unregister/delete time. FCP request private data points back to the active lpfc I/O buffer only while the buffer owns the request; completion clears both directions before invoking `done` unless exchange-busy deferral requires later release.

## Dependencies and Integration Points

The file depends on Linux NVMe-FC host APIs from `<linux/nvme-fc-driver.h>` and `<linux/nvme-fc.h>`, SCSI and FC transport definitions, and lpfc internal SLI-4, discovery, logging, vport, and debugfs infrastructure. It integrates with `lpfc_init.c` for localport creation/destruction, reset cleanup, queue and buffer allocation, and firmware capability gating. It integrates with `lpfc_attr.c` for reporting counters and local/remote port state through sysfs `nvme_info`.

Shared helpers from other lpfc modules include `lpfc_sli4_issue_wqe`, `lpfc_sli_get_iocbq`, `lpfc_sli_release_iocbq`, `lpfc_get_io_buf`, `lpfc_release_io_buf`, `lpfc_get_sgl_per_hdwq`, `lpfc_ndlp_check_qdepth`, `lpfc_vmid_get_appid`, `lpfc_update_cmf_cmd`, `lpfc_update_cmf_cmpl`, `lpfc_disc_state_machine`, and SLI abort helpers. The file also calls generic LS response and abort helpers declared in `lpfc_nvme.h` and implemented in `lpfc_nvmet.c`.

## Risks and Edge Cases

The highest-risk areas are asynchronous lifetime races among nvme-fc transport unregister, ndlp deletion, abort completion, and I/O completion. The code contains explicit guards for missing private pointers, stale `ndlp->nrport`, `NVME_XPT_UNREG_WAIT`, mismatched `nvmefc_fcp_req`, requests no longer on `LPFC_IO_ON_TXCMPLQ`, HBA flush, PCI offline, and localport unload.

Queue-depth and buffer scarcity paths must preserve CMF accounting and not leak request-private backpointers. The expedited keep-alive path intentionally bypasses normal scarcity controls for admin keep-alive commands, so changes around `lpfc_get_nvme_buf` or qdepth handling should preserve that behavior.

SGL construction is sensitive to segment counts, expanded SGL links, embedded command layout, response IU length, endian conversions, and last-SGE marking. Incorrect changes can cause DMA corruption or protocol-level data mismatches. The completion path also depends on subtle interpretation of `IOSTAT_FCP_RSP_ERROR` as a valid NVMe ERSP in one case.

Exchange-busy handling defers buffer release onto ABTS lists. Any change that clears `LPFC_SBUF_XBUSY`, calls `done`, or releases buffers in a different order can create double completion, use-after-free, or XRI reuse before firmware releases the exchange.

## Test Signals

Strong runtime signals include `nvme_info` counters for LS requests/completions/errors, FCP no-XRI, bad ndlp, queue-depth, WQ errors, aborts, completion XB, and completion errors. Kernel logs with message ids in the 6000-6213 and 6310 ranges expose queue binding, LS issue/completion, I/O failures, aborts, unregister waits, and ABTS flushes. Debugfs timing and CPU-affinity checks under `CONFIG_SCSI_LPFC_DEBUG_FS` can identify queue steering and latency regressions.

Functional testing should cover localport registration/unregistration, remoteport register/unregister/reregister under devloss, discovery role rescan, admin keep-alive under low resources, read/write/control I/O, embedded and non-embedded commands, high segment counts with expanded SGLs, CMF-managed reads, VMID-tagged I/O, transport-requested aborts, firmware XRI abort completions, PCI offline cleanup, and simultaneous unload with active NVMe LS and FCP I/O.
