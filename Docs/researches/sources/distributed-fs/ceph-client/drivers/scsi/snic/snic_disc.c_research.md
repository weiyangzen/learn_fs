# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_disc.c

Purpose: this file implements SNIC target discovery and target device lifecycle. It sends report-targets firmware requests, converts returned target IDs into Linux device objects, starts SCSI scans, and removes targets safely during unbind or target deletion.

Important APIs, types, and functions: `snic_disc_init()`, `snic_disc_start()`, and `snic_disc_term()` manage discovery state. `snic_queue_report_tgt_req()` allocates a request plus DMA response buffer and queues `SNIC_REQ_REPORT_TGTS`. `snic_report_tgt_cmpl_handler()` handles firmware completion, stores target response data, and queues `tgt_work`. `snic_tgt_create()` creates `struct snic_tgt`, initializes an embedded `struct device`, assigns `scsi_tgt_id`, adds it to `disc.tgt_list`, and queues scan work. `snic_tgt_del_all()` queues deletion work for all targets.

Control flow: discovery starts by checking `in_remove`, transitioning `disc.state` to pending, and posting a report-targets request. Completion unmaps the DMA response, transfers ownership of the response buffer to discovery work when targets exist, and releases the untagged request. Target discovery work restarts discovery if a request arrived while one was in progress; otherwise it creates targets and queues `scsi_scan_target()`. Deletion blocks target I/O, aborts outstanding target commands, unblocks offline, removes SCSI target children, deletes the device, and drops the reference.

State and persistence: discovery state lives in `struct snic_disc`: target list, mutex, state, pending request count, next SCSI target id, response target count, and response buffer pointer. Each `struct snic_tgt` stores hardware target id, synthetic SCSI target id, state, flags, device, and work items. No persistent storage exists.

Dependencies and integration: depends on firmware request formats, SNIC request allocation/WQ queueing, SCSI scan/remove/block APIs, host lock, and the global ordered event workqueue.

Risks: discovery uses both mutex and host lock, and target deletion has to coordinate with scan work and outstanding SCSI commands. Several `SNIC_BUG_ON` checks trust firmware target counts and types. Response buffer lifetime crosses interrupt and workqueue contexts. `disc_timeout` exists in the header but is not used here.

Test signals: validate initial discovery, repeated discovery while pending, no-target response, max-target boundary, target add/remove, PCI unbind during discovery, and deletion with outstanding I/O. Device model reference counting should be checked with KASAN and driver-core debug.
