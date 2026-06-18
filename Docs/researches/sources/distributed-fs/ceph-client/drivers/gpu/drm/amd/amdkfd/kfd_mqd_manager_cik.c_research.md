# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_cik.c

Purpose: implements MQD manager operations for CIK-era ASICs. It programs `struct cik_mqd` compute descriptors and `struct cik_sdma_rlc_registers` SDMA descriptors, including HIQ/DIQ variants and checkpoint/restore support.

Important APIs/types/functions: `mqd_manager_init_cik` constructs per-type managers. `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, and `destroy`/`free` helpers cover CP queues. SDMA uses `init_mqd_sdma` and `update_mqd_sdma`. HIQ uses `init_mqd_hiq` and `update_mqd_hiq`. `update_cu_mask`, `set_priority`, `checkpoint_mqd`, `restore_mqd`, `checkpoint_mqd_sdma`, and `restore_mqd_sdma` manage optional state transitions.

Control flow: CP MQDs are GTT suballocated, zeroed/aligned, initialized with header, persistent state, quantum, static thread masks, base address, and AQL enable when needed. Update fills PQ base, rptr report address, doorbell offset, VMID, queue size, optional ATC bits, NO_UPDATE_RPTR for AQL, CU mask, and pipe priority. SDMA update fills ring control, RB base, rptr writeback, doorbell, virtual address, engine/queue ID. HIQ update marks the queue as privileged KMD. Manager init wires different allocation/free/load callbacks for CP, HIQ, DIQ, and SDMA.

State and persistence: queue state persists in MQD memory and SDMA register snapshots. Restore copies checkpointed MQDs back and rewrites doorbell offsets from current queue properties before marking queues inactive.

Dependencies/integration: depends on CIK register/struct headers, shared MQD helpers, KFD GTT suballocation, KFD2KGD HQD callbacks, and debugfs `seq_hex_dump`.

Risks: CIK-specific field encodings differ from SOC15 generations. `se_mask[4]` assumes max four shader engines. Restore must rewrite doorbell offsets to avoid stale process mappings. Test signals include CIK CP/HIQ/DIQ/SDMA queue creation, AQL vs PM4 loading, CU-mask update, checkpoint/restore, debugfs MQD dumps, and HIQ preemption-failure detection.
