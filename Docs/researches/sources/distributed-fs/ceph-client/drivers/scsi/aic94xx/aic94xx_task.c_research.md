# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_task.c

Purpose: this file is the normal I/O submission and completion path from libsas `sas_task` objects to aic94xx hardware SCBs for SSP, SMP, SATA/STP, and ATAPI.

Important APIs/types/functions: the exported entry point is `asd_execute_task()`. Core helpers are `asd_can_queue()`/`asd_can_dequeue()`, `asd_map_scatterlist()`, `asd_unmap_scatterlist()`, `asd_get_response_tasklet()`, `asd_task_tasklet_complete()`, and protocol builders/unbuilders for ATA, SMP, and SSP SCBs. `data_dir_flags[]` maps Linux DMA directions to hardware data-direction bits.

Control flow and state: `asd_execute_task()` reserves queue capacity, allocates an ASCB, attaches it to `task->lldd_task`, normalizes STP protocol bits, builds a protocol-specific SCB, posts it, and unwinds DMA/ASCB state on errors. Builders fill opcode, protocol/rate, frame fields, CDB/FIS/SMP SG descriptors, connection handle, retry count, data direction, and hardware SG list. Completion translates done-list opcodes into libsas task response/status, optionally reads response IU/FIS data from an EDB, unmaps DMA, marks task state done, frees the ASCB, and invokes `task_done()` unless the upper layer already marked the task aborted.

Persistence behavior: mutates `seq.can_queue`, `task->lldd_task`, task state flags, ASCB SG allocations, DMA mappings, and task status/residual data. Hardware SCBs and external SG lists are transient until completion or abort cleanup.

Dependencies and integration points: depends on libsas task/protocol structures, PCI DMA mapping APIs, ASCB allocation/posting, `aic94xx_sas.h` layouts/opcodes, and `asd_invalidate_edb()` from `aic94xx_scb.c`. TMF paths in `aic94xx_tmf.c` depend on `task->lldd_task` and transaction context indices created here.

Risks: cleanup asymmetry around ATA pre-mapped SG lists is subtle; the `err_unmap` branch appears to unmap ATA when allocation of an external SG list fails even though comments say libata already mapped it. Completion races with abort handling rely on task state locks and completion pointers. Multi-SG chaining depends on exact EOL/EOS flags and external list allocation.

Test signals: queue-full handling, allocation failure unwind, no-data/single-buffer/multi-SG DMA, ATA device-control updates, ATAPI packet copy, SMP request/response DMA, SSP response IU handling, every major done-list opcode mapping, and abort-vs-completion races.
