# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.h

## Purpose

`lpfc_nvme.h` is the shared declaration layer for lpfc NVMe initiator and NVMe target support. It pulls in the Linux NVMe, NVMe-FC driver, and NVMe-FC protocol headers, defines lpfc-specific NVMe constants, declares transport-private data structures, describes target exchange state and flags, and exposes cross-file helper prototypes shared between `lpfc_nvme.c` and `lpfc_nvmet.c`.

The header is not standalone logic, but it is the contract that keeps the initiator and target implementations synchronized around queue handles, local/remote port private data, target-port counters, per-XRI context ownership, and LS helper reuse.

## Important APIs, Types, and Constants

Initiator constants include `LPFC_NVME_DEFAULT_SEGS`, `LPFC_NVME_ERSP_LEN`, `LPFC_NVME_WAIT_TMO`, `LPFC_NVME_EXPEDITE_XRICNT`, `LPFC_NVME_FB_SHIFT`, `LPFC_NVME_MAX_FB`, and `LPFC_NVME_LS_TIMEOUT`. They define default segment advertisement, expected NVMe ERSP IU length, unregister wait logging interval, expedited XRI reserve size, first-burst encoding bounds, and link-service timeout.

Target constants include `LPFC_NVMET_DEFAULT_SEGS`, RQ posting defaults, `LPFC_NVMET_SUCCESS_LEN`, MRQ bounds, `LPFC_NVMET_WAIT_TMO`, and `LPFC_NVMET_INV_HOST_ACTIVE`. These configure target SGL advertisement, receive queue depth assumptions, successful response length, maximum multi-receive queues, targetport unregister wait time, and hosthandle invalidation state.

`lpfc_ndlp_get_nrport(ndlp)` is a small but important safety macro. It returns NULL if there is no NVMe rport binding or if `NVME_XPT_UNREG_WAIT` is set, preventing users from dereferencing transport-private remoteport state during asynchronous unregister.

`struct lpfc_nvme_qhandle` is the per-NVMe-queue opaque handle returned to the host transport. It stores the lpfc hardware queue index, the original NVMe queue index, and CPU at creation.

`struct lpfc_nvme_lport` is private data behind `nvme_fc_local_port`. It points back to `lpfc_vport`, stores the localport unregister completion, and contains atomic counters for LS requests, FCP submission failures, aborts, and completion errors.

`struct lpfc_nvme_rport` is private data behind `nvme_fc_remote_port`. It binds the remote transport object to the lpfc localport and ndlp, plus a completion for remoteport unregister flows.

`struct lpfc_nvme_fcpreq_priv` is per-FCP-request private storage used by the NVMe-FC host transport. Its single `nvme_buf` pointer links a transport request to the active lpfc I/O buffer so abort callbacks can find the WQE/XRI to abort.

`struct lpfc_nvmet_tgtport` is private data behind `nvmet_fc_target_port`. It stores the owning HBA, targetport unregister completion, invalidation state, and many atomic counters grouped by receive LS, transmit LS, receive FCP, transmit FCP, abort, and defer paths. These counters feed observability through sysfs/debug paths and are essential for diagnosing target behavior.

`struct lpfc_nvmet_ctx_info` is the per-CPU, per-MRQ context-list bucket used by the target side. It contains a context list, lock, next/start CPU pointers for replenishment, a count, and padding to reduce cache-line contention.

`struct lpfc_async_xchg_ctx` is the central target exchange context. It stores the target transport FCP request, active-list linkage, HBA, ndlp, optional LS request/response state, active and abort WQEs, a context lock, SID, OXID, payload size, MRQ index, state, flags, payload/RQ buffer pointers, owning context buffer, hardware queue, and optional debug timestamp fields. It is used for both unsolicited LS and FCP target exchanges.

The exported prototypes connect the two C files: initiator LS request, completion, and abort helpers from `lpfc_nvme.c`; target/generic unsolicited LS abort and LS response helpers from `lpfc_nvmet.c`.

## Control Flow Role

The header defines the finite-state vocabulary used by target exchange code: LS receive, LS abort, LS response, FCP receive, data, abort, done, and free. It also defines flags that can be combined independently of state: I/O in progress, abort operation issued, exchange busy, context release requested, ABTS received, RQ buffer reuse through workqueue, WQ-full deferral, and transport-notification state.

The target implementation relies on these states to validate transitions in LS response completion, FCP operation preparation and completion, release, abort, and context repost. The initiator implementation relies on the shared LS helper declarations and on initiator private structures for queue and transport object callbacks.

## State and Persistence Behavior

All data declared here represents in-kernel volatile state. No fields are persisted across driver reload or reboot. However, these structures model long-lived runtime ownership: localport and targetport private areas live as long as their transport registrations; rport private data lives as long as remoteport registration; `lpfc_async_xchg_ctx` instances are pooled and reused across target FCP exchanges; per-request private data lives across submit, abort, and completion callbacks.

Because the structures are shared across interrupt, workqueue, transport callback, discovery, and unload contexts, the lock annotations and field grouping matter. `ctxlock` protects target exchange flags, ndlp lock protects `nrport` and FC4 transport flags, and per-context-list locks protect target context pools. Atomic counters avoid broad locking for stats.

## Dependencies and Integration Points

This header directly depends on the kernel NVMe-FC APIs and lpfc internal structures declared elsewhere. It is included by `lpfc_nvme.c`, `lpfc_nvmet.c`, `lpfc_init.c`, `lpfc_attr.c`, and other lpfc modules that need NVMe state or helper prototypes. The macros and structs integrate with SLI-4 queue allocation, receive queue handling, XRI/SGL pools, debugfs timing, sysfs `nvme_info`, discovery state, and transport registration APIs.

The prototypes intentionally share LS request/response logic between initiator and target modes. That reuse means changes to LS helper signatures or `lpfc_async_xchg_ctx` fields must be coordinated across both C files and with unsolicited receive code outside this subset.

## Risks and Edge Cases

The main risk is field ownership ambiguity. `lpfc_async_xchg_ctx` is touched by interrupt handlers, worker threads, abort callbacks, transport release callbacks, and cleanup paths. Flags such as `LPFC_NVME_CTX_RLS`, `LPFC_NVME_XBUSY`, and `LPFC_NVME_ABORT_OP` determine whether a context can be recycled; incorrect interpretation can lead to use-after-free, leaks, or double release.

The `lpfc_ndlp_get_nrport` macro intentionally hides rports while unregister is pending. Bypassing it or changing `NVME_XPT_UNREG_WAIT` semantics can reintroduce stale transport object dereferences.

Stats counters are grouped by comments that name implementation functions. Adding paths without updating counters or sysfs output can make operational diagnosis misleading.

The MRQ context indexing macro assumes `phba->sli4_hba.nvmet_ctx_info` is allocated as `num_possible_cpu * cfg_nvmet_mrq` and that `cfg_nvmet_mrq` is clamped before use. Invalid MRQ sizing would corrupt context-list indexing.

## Test Signals

Compile coverage with `CONFIG_NVME_FC`, `CONFIG_NVME_TARGET_FC`, and `CONFIG_SCSI_LPFC_DEBUG_FS` is important because the header exposes fields under conditional debug usage and prototypes consumed under conditional NVMe support. Runtime signals include coherent `nvme_info` counters, correct localport/targetport registration, no stale rport lookup while unregister wait is set, balanced ndlp references on hosthandle release, and no context-list corruption under multi-CPU/MRQ target I/O.
