# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h

Purpose: generated AXUSER map for the normal MSI-X path of `DCORE0_VDEC0_BRDG_CTRL`. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_NRM_*` constants from `0x41E3A00` to `0x41E3A4C`.

Important APIs/types/functions: macro-only set for HB/LB AXUSER attributes and override registers, scoped to normal MSI-X interrupt writes.

Control flow: none. Driver interrupt setup programs these attributes before normal interrupt flows are enabled.

State and persistence behavior: persistent MMIO state affects transaction identity, protection, ordering, snooping, and QoS for normal MSI-X writes.

Dependencies and integration points: included by `gaudi2_regs.h`; connected to NRM interrupt masks, wait counters, APB write controls, completion queue address fields, and MSI-X LBW write data in the main VDEC bridge control map.

Risks: attribute mistakes can break normal interrupt delivery or violate memory protection. Similar ABNRM/L2C/VCD files require careful channel-specific use.

Test signals: normal MSI-X delivery tests, bridge wait/counter observations, security/isolation tests for interrupt writes, and generation diff checks.
