# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore3_mme_ctrl_lo_regs.h

Purpose: generated lower-control register map for the DCORE3 MME engine. It exports 70 `mmDCORE3_MME_CTRL_LO_*` constants from `0x46CB000` to `0x46CB4EC`.

Important APIs/types/functions: macro-only API equivalent in layout to DCORE1 MME low control: architecture status/command, sync object registers, tensor section selectors, QM stall, log shadow, base address descriptors, tensor A/B/COUT descriptors, non-tensor regions, AGU input/output master/slave controls, WBC AXI E2E attributes, and ETF memory repair/wrap registers.

Control flow: none. External MME programming paths use these constants when targeting the DCORE3 MME instance.

State and persistence behavior: persistent MMIO state for DCORE3 MME execution, tensor addressing, AGU routing, sync completion, and repair controls. Values persist until reset/reprogramming.

Dependencies and integration points: included by `gaudi2_regs.h`; block metadata in `gaudi2_blocks_linux_driver.h`. It mirrors `dcore1_mme_ctrl_lo_regs.h`, enabling per-DCORE engine programming with the same logical layout but different absolute address base.

Risks: DCORE3/DCORE1 confusion is the main integration risk. Using the wrong base silently programs the wrong MME. Tensor/AGU/sync mistakes can cause data corruption, hangs, or incorrect completion signaling.

Test signals: DCORE3-specific MME command tests, cross-check that DCORE1 and DCORE3 layouts differ by expected address base only, sync-object completion validation, AGU stress tests, and generated source diff review.
