<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_regs.h

## Purpose
`pdma0_core_regs.h` maps the PDMA0 core global register block. It provides addresses for enabling, halting, flushing, protection, clock gating, read/write channel tuning, memory initialization, error messaging, and status.

## Important APIs, types, and functions
Exports include `mmPDMA0_CORE_CFG_0`, `CFG_1`, `PROT`, `CKG`, read global/HBW/LBW max outstanding and max size/cache/inflight registers, write global/HBW/LBW equivalent registers, memory init start/busy/done/status, error message address low/high and data, status registers `STS0`/`STS1`, and read-context status selection/size/base/id registers. No functions or types are present.

## Control flow
The header has no C flow. PDMA init writes global configuration, protection/cache settings, and outstanding limits, then enables the core. Reset/quiesce paths halt or flush and poll status. Error paths program or read error-message registers. Diagnostics select read-context status and inspect active context details.

## State and persistence
Hardware state includes enable/halt/flush status, transaction tuning, memory-init state, error-message target/data, and active read context status. Values persist until reset or explicit reprogramming.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pdma0_core_masks.h`, `pdma0_core_ctx_regs.h`, PDMA queue-manager headers, and Gaudi2 reset/security/MMU setup.

## Risks and test signals
Bad core control addresses can wedge DMA or allow transfers with wrong protection/cache policy. Test signals include PDMA enable/disable, halt/flush completion, memory init completion, transfer throughput within expected outstanding limits, correct error reporting on invalid transfers, and status registers showing idle after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_regs.h -->
