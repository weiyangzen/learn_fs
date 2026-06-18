# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_io.h

Purpose: this header defines SNIC request allocation sizes, SG descriptor formats, per-SCSI-command private state, request-info state, and request helper prototypes.

Important APIs, types, and functions: `struct snic_sg_desc`, `struct snic_dflt_sgl`, and `struct snic_max_sgl` define DMA SG entries. `enum snic_req_cache_type` selects mempools for default SG, max SG, and task-management request buffers. `struct snic_internal_io_state` is stored in `scsi_cmnd` private memory and carries request pointer, flags, state, abort status, and LUN reset status. `struct snic_req_info` ties a firmware request to a SCSI command, target id, DMA response buffer, abort/reset request buffers, and completions. Macros convert between request info, request, and SGL memory.

Control flow: queueing allocates `snic_req_info`, stores it in `CMD_SP(sc)`, initializes `rqi->req`, posts the request, and later completion/error paths use `req_to_rqi()` or `CMD_SP()` to find state and free it.

State and persistence: all structures are runtime-only. They are the core state machines for command lifetime, task management, and cleanup.

Dependencies and integration: used by `snic_io.c`, `snic_scsi.c`, discovery, control, and resource helpers. It depends on firmware request type declarations from `snic_fwint.h` through including users.

Risks: the `CMD_SP` macro stores `struct snic_req_info *` as `char *`, so type discipline is manual. `req_to_rqi()` trusts `hdr.init_ctx`, which is firmware-visible and must not be corrupted. Cache sizing and 16-byte alignment must match DMA and firmware assumptions.

Test signals: allocation/free tests under memory pressure, task-management reuse, command timeout races, and DMA API debug are most valuable. Compile-time checks for cache object sizes and alignment would reduce risk.
