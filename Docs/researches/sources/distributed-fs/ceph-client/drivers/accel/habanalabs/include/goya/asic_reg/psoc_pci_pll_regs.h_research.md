# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_pci_pll_regs.h

Purpose: defines the PSOC PCI PLL register map for PCIe/PCI-related clocking. It mirrors the common 41-register PLL prototype at addresses `0xC72100` through `0xC72440`.

Important APIs/types/functions: no functions or types. The exported macros are `mmPSOC_PCI_PLL_NR`, `NF`, `OD`, `NB`, `CFG`, lock/loss and bypass registers, data-change/reset controls, divider factors/commands/selects/enables/busy flags, clock gater/relaxation registers, reference thresholds, not-stable status, and frequency calculation enable.

Control flow: clock initialization code writes PLL factors, pulses change/reset controls, waits for lock/stability, enables dividers, and only then allows dependent PCIe logic to proceed.

State and persistence: register contents are persistent hardware clock state for PCI-related domains. They can survive normal driver function calls and are reset only by hardware reset or explicit reconfiguration.

Dependencies and integration: included by `goya_regs.h` alongside PCIe aux/wrapper registers. It is a prerequisite map for stable PCIe behavior even if direct use is often inside firmware or board initialization code.

Risks: PCIe link training and DBI/MMIO access can fail if this PLL is unstable. Incorrect divider busy handling can cause intermittent PCIe failures that look like transport or link issues.

Test signals: PCIe link training, FLR and warm reset, DBI access, DMA stress, PLL lock telemetry, and suspend/resume validate the map.
