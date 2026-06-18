# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli4.h

## Purpose
`lpfc_sli4.h` defines the SLI-4-specific in-memory model and function surface for LPFC adapters. It covers event/completion/work/receive/mailbox queues, FCoE FCF/FIP records, bootstrap mailbox memory, SLI-4 capability and resource limits, CPU/IRQ/hardware-queue mapping, XRI/RPI/VPI/VFI allocation state, per-hardware-queue buffer pools, and prototypes for SLI-4 setup, queue creation, doorbells, asynchronous events, XRI abort handling, and FCF discovery.

## Important APIs, Types, And Functions
Key enums are `enum lpfc_sli4_queue_type`, `enum lpfc_sli4_queue_subtype`, and `enum lpfc_poll_mode`. `struct lpfc_queue` is the queue primitive for EQ, CQ, MQ, WQ, HRQ, and DRQ instances. It stores list linkage, queue IDs, entry geometry, page arrays, host/HBA indexes, notification and processing limits, doorbell registers, polling state, work items, associated queues, RQ buffers, and per-queue counters.

`struct lpfc_sli4_hba` is the main SLI-4 HBA extension. It stores mapped PCI/SLI registers, interface-type-specific status/error registers, doorbell registers, bootstrap mailbox, queue arrays, fast-path hardware queues, slow-path mailbox/ELS/NVMe-LS queues, receive queues, FCF state, link state, resource bitmaps and ID arrays for XRI/RPI/VFI, RPI headers, SGL lists, aborted lists, async work queues, CPU vector maps, IRQ handles, idle stats, trunk/optic state, and feature capability data. `struct lpfc_sli4_hdw_queue` groups a fast-path EQ/CQ/WQ tuple with I/O buffer lists, aborted I/O lists, multi-XRI pools, FC-4 stats, and per-HWQ SGL/command-response pools.

Other important structures include `struct lpfc_fcf`, `struct lpfc_fcf_rec`, `struct lpfc_fcf_conn_rec`, `struct lpfc_bmbx`, `struct lpfc_max_cfg_param`, `struct lpfc_pc_sli4_params`, `struct lpfc_sglq`, `struct lpfc_rpi_hdr`, `struct lpfc_rsrc_blks`, `struct lpfc_rdp_context`, and `struct lpfc_lcb_context`. Important inline helpers are `lpfc_sli4_qe()` for locating a queue entry by index and `lpfc_sli4_unrecoverable_port()` for ERR/RN status interpretation.

## Control Flow
The header describes, but does not execute, the SLI-4 control plane. Probe/setup code calls `lpfc_sli4_hba_setup()`, maps SLI registers, discovers capabilities into `lpfc_pc_sli4_params`, creates queues with `lpfc_eq_create()`, `lpfc_cq_create()`, `lpfc_wq_create()`, `lpfc_rq_create()`, and `lpfc_mq_create()`, then posts SGLs/RPI headers and arms queues. Runtime interrupts consume EQ/CQ entries through `struct lpfc_queue`, write EQ/CQ doorbells through function pointers, and dispatch completions or async events into the HBA work queues. Teardown reverses this with destroy/unset functions and resource-list cleanup.

Resource flow is mostly bitmap/list driven. XRI, RPI, VPI, VFI, FCFI, queue, and SGL resources are described by max/base/used counts, bitmaps, block lists, active lists, and per-HWQ pools. Multi-XRI pools split public and private XRI lists and use heartbeat counters to tune pool balance.

## State And Persistence
The state is volatile driver/HBA state initialized during PCI probe and firmware setup. It mirrors firmware-assigned queue IDs, resource extents, FCF records, link state, and adapter capabilities but does not itself persist data. FCF state persists across runtime rediscovery attempts in memory with flags such as `FCF_AVAILABLE`, `FCF_REGISTERED`, `FCF_IN_USE`, and rediscovery bits. Timers (`redisc_wait`) and delayed work fields persist pending rediscovery or poll work until canceled.

## Dependencies And Integration Points
The header depends on Linux IRQ polling, CPU frequency/affinity, workqueues, timers, per-CPU storage, DMA, PCI MMIO, and LPFC hardware bitfield macros. It is consumed by LPFC SLI-4 setup, interrupt, mailbox, FCoE, discovery, NVMe/FC, NVMET, SCSI fast path, debugfs, and vport code. Doorbell helpers and queue prototypes form the bridge between high-level LPFC operations and firmware queue commands.

## Risks And Edge Cases
Queue geometry must match firmware capabilities; bad entry size/count/page assumptions can corrupt queue memory or doorbell accounting. Hardware queue and CPU vector mapping is sensitive to CPU hotplug, IRQ affinity, and polling mode transitions. Resource counters (`xri_used`, `rpi_used`, `vpi_used`, pool counts) must match bitmap/list state or the driver can leak firmware resources or double-free IDs. FCF rediscovery flags have overlapping pending/event/failover meanings, so failover races can select stale FCF data. The inline `lpfc_sli4_qe()` trusts `q_pgs` and index bounds supplied by callers.

## Test Signals
Validation signals include SLI-4 probe on all supported interface types, queue creation/destruction under varied page sizes and queue counts, MSI-X/IRQ affinity mapping, interrupt and poll-mode completion paths, FCF scan/failover/rediscovery, XRI/RPI/VPI/VFI allocation exhaustion and recovery, SGL repost after reset, async link/FIP/DCBX/FC events, NVMET and NVMe-LS queue setup, and unload with all queue/list/bitmap resources reclaimed.
