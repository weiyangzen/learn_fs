# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm_common.h

## Purpose
`qm_common.h` defines the shared hardware queue context and event entry layouts consumed by `qm.c` and HiSilicon accelerator drivers. It is a compact ABI-like header for CQE/EQE/AEQE and SQC/CQC/EQC/AEQC memory images plus declarations for common QM helpers.

## Important APIs, types, and functions
The primary types are `struct qm_cqe`, `struct qm_eqe`, `struct qm_aeqe`, `struct qm_sqc`, `struct qm_cqc`, `struct qm_eqc`, and `struct qm_aeqc`. They use little-endian fields because the structures are copied directly to or from DMA buffers and mailbox-programmed hardware contexts. Declared helpers are `qm_set_and_get_xqc()`, `hisi_qm_show_last_dfx_regs()`, and `hisi_qm_set_algqos_init()`.

## Control flow
The header has no executable control flow. Its structures are populated in `qm.c` during queue startup (`qm_sq_ctx_cfg()`, `qm_cq_ctx_cfg()`, `qm_eq_ctx_cfg()`, `qm_aeq_ctx_cfg()`), read during queue-drain checks, and interpreted by interrupt/completion paths.

## State and persistence behavior
Instances of these structures live in coherent DMA regions owned by `struct hisi_qm` and per-QP buffers. Hardware updates CQE/EQE/AEQE content, while the driver writes SQC/CQC/EQC/AEQC content. There is no file or cross-boot persistence.

## Dependencies and integration points
The header depends on Linux endian types and `struct hisi_qm` from the public HiSilicon accelerator QM API. It is included by `qm.c`; sibling accelerator drivers can include it when they need direct xQC or DFX helper access.

## Risks and edge cases
Because these structures mirror hardware layouts, field order, size, alignment, and endian conversions are critical. Expanding or reordering fields would silently corrupt mailbox/DMA context programming. Callers must also use the matching `QM_MB_CMD_*` command so `qm_set_and_get_xqc()` copies the correct structure size.

## Test signals
Build coverage catches missing declarations, but meaningful validation comes from queue bring-up, xQC dump/set mailbox tests, completion interrupt tests, and reset/drain tests that compare SQC and CQC tails.
