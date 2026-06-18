# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_mme_ctrl_lo_regs.h

Purpose: generated lower-control register map for the DCORE1 MME engine. It exports 70 `mmDCORE1_MME_CTRL_LO_*` constants from `0x42CB000` to `0x42CB4EC`.

Important APIs/types/functions: macro-only API for architecture status/command, sync object data/address/value registers, tensor section selectors for A/B/COUT, QM stall, log shadow registers, base address registers, tensor A/B/COUT base descriptors, non-tensor start/end regions, AGU master/slave controls for inputs and outputs, sync-object address/value fields, slave WBC AXI E2E attributes, and ETF memory repair/wrap registers.

Control flow: none. External MME setup code programs tensor/non-tensor descriptors, AGU controls, sync objects, and commands, then reads status.

State and persistence behavior: MMIO-backed state controls DCORE1 MME command execution, tensor addressing, AGU behavior, queue-manager stall, sync-object signaling, and repair-related registers. Values persist until reset or next programming sequence.

Dependencies and integration points: included by `gaudi2_regs.h`; block base/sections are defined in `gaudi2_blocks_linux_driver.h`. It is structurally mirrored by `dcore3_mme_ctrl_lo_regs.h` at a different DCORE address base.

Risks: MME tensor/AGU address programming errors can corrupt data or hang compute. Sync object mistakes affect completion semantics. DCORE-specific base addresses must not be mixed between DCORE1 and DCORE3.

Test signals: MME command smoke tests on DCORE1, tensor descriptor readback, sync-object completion tests, AGU addressing stress tests, and generated comparison with DCORE3 where layouts should match except base.
