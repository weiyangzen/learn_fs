# sources/distributed-fs/ceph-client/drivers/scsi/atp870u.h

Purpose: defines constants and the host-private data structure used by the ATP870U-family SCSI driver.

Important APIs/types/functions: constants define command/sense limits, queue depth `qcnt`, scatter-gather limit, adapter/target counts, max sectors, and ATP880/ATP885 PCI device IDs. `struct atp_unit` stores base/I/O/PCI ports, per-channel queue state, target maps, speed/async data, queued commands, nested per-target DMA/PRD/current-command state, and pointers to `Scsi_Host` and `pci_dev`.

Control flow: the header has no executable flow. `atp870u.c` allocates `struct atp_unit` as SCSI host private data, initializes its arrays in `atp870u_init_tables()`, mutates it in queue/interrupt paths, and frees coherent PRD tables during teardown.

State and persistence: this structure is the volatile state container for the whole adapter. Per-target `prd_table` memory is coherent DMA memory, `curr_req` tracks the active command, and maps such as `active_id`, `wide_id`, `ultra_map`, and `async` summarize discovery/negotiation.

Dependencies and integration: depends on kernel integer and DMA address types plus SCSI/PCI structures supplied by the C file. It forms the internal ABI between initialization, interrupt, queueing, and scan code in `atp870u.c`.

Risks and test signals: fixed dimensions assume at most two channels and sixteen SCSI IDs. PRD table size is hardcoded in the C file at 1024 bytes and must remain sufficient for `ATP870U_SCATTER` entries plus splitting. Test signals are compile-time structure use across all chip variants, coherent allocation/free for every populated `id[channel][target]`, and queue arrays cleared before scan or command submission.
