# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.c

Purpose: this file provides common request allocation, WQ descriptor queueing, WQ completion acknowledgement, untagged request tracking, DMA unmapping, descriptor debugging, and simple timing stats for SNIC.

Important APIs, types, and functions: `snic_queue_wq_desc()` maps a request buffer for DMA, checks WQ descriptor availability, posts an Ethernet WQ descriptor, and increments active firmware request stats. `snic_req_init()` allocates `snic_req_info` plus `snic_host_req` and optional SG descriptors from the correct mempool. `snic_abort_req_init()` and `snic_dr_req_init()` allocate task-management request buffers. `snic_req_free()` unmaps request/abort/reset DMA mappings and returns memory to pools. `snic_handle_untagged_req()`, `snic_release_untagged_req()`, and `snic_free_all_untagged_reqs()` maintain `spl_cmd_list`. `snic_wq_cmpl_handler()` services WQ ACK completions.

Control flow: SCSI, discovery, and control paths allocate request info, initialize firmware payloads, and call `snic_queue_wq_desc()`. WQ completions arrive on CQ0 and clear `buf->os_buf` through `snic_wq_cmpl_frame_send()`. Error/remove paths clean WQ buffers and untagged requests, unmapping response buffers when present.

State and persistence: state is mempool-backed request objects, DMA mappings in request fields, WQ ring state, `fw.actv_reqs`, `spl_cmd_list`, and per-request response buffer addresses. No persistent state exists.

Dependencies and integration: depends on vNIC WQ/CQ helpers, firmware wire structs, SNIC stats, PCI DMA APIs, SCSI DMA APIs indirectly through request users, and locks in `struct snic`.

Risks: `snic_req_init()` selects default vs max SG pool using `sg_cnt <= SNIC_REQ_CACHE_DFLT_SGL`, comparing SG count to enum value 0 rather than descriptor capacity; any nonzero SG count goes to max pool. WQ availability is global and assumes one queue. Request lifetime is split between WQ ACK, firmware completion, and cleanup paths, so double-free and stale DMA mapping risks are concentrated here.

Test signals: run I/O with SG counts 0, 1, 32, 60, queue-full conditions, DMA mapping failures, control request cleanup during remove, and WQ CQ wraparound. KASAN/DMA-API debug should catch mapping lifetime mistakes.
