# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sev-dev-tio.c

## Purpose

`sev-dev-tio.c` implements the low-level SEV-TIO firmware interface used to connect PCIe devices to SNP/TDISP flows. It manages Scatter List Address buffers, SPDM request/response objects, firmware-owned page transitions, and TIO device lifecycle commands.

## Important APIs, Types, And Functions

Public functions include `sev_tio_init_locked()`, `sev_tio_continue()`, `sev_tio_dev_create()`, `sev_tio_dev_connect()`, `sev_tio_dev_disconnect()`, `sev_tio_dev_reclaim()`, and `sev_tio_cmd_buffer_len()`. Internal command buffer structures cover TIO status, init, device create/connect/disconnect/measure/cert/reclaim. SLA helpers include `make_sla()`, `sla_buffer_map()`, `sla_buffer_unmap()`, `sla_alloc()`, `sla_free()`, `sla_expand()`, and SPDM helpers `spdm_ctrl_alloc()`, `spdm_ctrl_init()`, and `spdm_ctrl_free()`.

## Control Flow

TIO initialization queries firmware status, validates the returned status structure, and issues `SEV_CMD_TIO_INIT` when firmware says TIO is enabled but not initialized. Device create allocates a firmware-owned device context SLA and a firmware page, then sends `TIO_DEV_CREATE`. Connect allocates request, response, scratch, and output buffers, fills an SPDM control structure, and calls `sev_tio_do_cmd()`. If firmware returns SPDM-request status, the function prepares DOE payload lengths and returns a PCI DOE feature code so the higher TSM layer can exchange SPDM messages and call `sev_tio_continue()`. Reclaim frees firmware pages, sends reclaim, frees SLA buffers, and clears context state.

## State And Persistence Behavior

Per-device state is stored in `struct tsm_dsm_tio`: SLA addresses, vmapped request/response headers, current command replay buffer, PSP return code, firmware data page, and PCI IDE stream pointers. SLA buffers may be hypervisor-owned or firmware-owned; freeing firmware-owned buffers requires SNP reclaim before releasing pages. Output and scratch buffers can be expanded when firmware requests larger buffers.

## Dependencies And Integration Points

It depends on SEV command submission from `sev-dev.c`, SNP RMP helpers, PCI DOE constants, Linux TSM and PCI IDE types from `sev-dev-tio.h`, and AMD SEV firmware command definitions. `sev-dev-tsm.c` drives its SPDM continuation loop.

## Risks And Test Signals

Risks include page-state leaks when reclaim fails, vmap/unmap mismatches for scatter SLAs, firmware-owned buffer expansion errors, SPDM header length validation gaps, and deadlocks if locked SEV command paths call reclaim paths that also lock. Test with SEV-TIO-capable firmware, DOE CMA and secure-session exchanges, buffer expansion responses, connect/disconnect/reclaim failure injection, and RMP/page-leak diagnostics.
