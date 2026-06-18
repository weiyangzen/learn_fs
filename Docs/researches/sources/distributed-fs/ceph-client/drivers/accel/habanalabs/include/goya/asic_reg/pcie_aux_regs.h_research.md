# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/pcie_aux_regs.h

Purpose: defines 110 absolute Goya PCIe auxiliary register addresses. The block covers APB timeout, PHY/link initialization, BAR start/limit mirrors, bus-master/memory-space enables, PCIe capability settings, hot-plug/FLR/power-management signals, DBI access, diagnostic buses, RAS descriptors, and PERST state.

Important APIs/types/functions: no functions or types are present. The exported API is the `mmPCIE_AUX_*` macro set from `mmPCIE_AUX_APB_TIMEOUT` at `0xC07004` to `mmPCIE_AUX_PERST` at `0xC079B8`. Key integration macros include `mmPCIE_AUX_DBI`, `mmPCIE_AUX_FLR_INT`, `mmPCIE_AUX_LTSSM_EN`, `mmPCIE_AUX_SMLH_LINK_UP`, and `mmPCIE_AUX_RDLH_LINK_UP`.

Control flow: driver code uses these addresses to enable/configure PCIe, poll link state, service FLR, and expose DBI access. For example, the Goya/Gaudi property setup stores `CFG_BASE + mmPCIE_AUX_DBI` as the DBI register address; reset logic writes FLR control registers in the related aggregate set.

State and persistence: all state lives in the PCIe controller hardware. BAR, power-management, link, and FLR state persists across driver calls and changes on PCIe link/reset events.

Dependencies and integration: included through `goya_regs.h`; it is consumed by the Goya driver and is conceptually paired with PCIe wrapper registers in `pcie_wrap_regs.h`. It also feeds common habanalabs properties that abstract PCIe DBI access.

Risks: these are full MMIO addresses in the PSOC/PCIe range, unlike some router offsets. Mixing absolute and base-relative addresses can double-add `CFG_BASE`. PCIe state bits are timing-sensitive around FLR, PERST, and LTSSM changes; polling without hardware-specified waits risks false failures.

Test signals: PCIe enumeration, BAR sizing, DBI reads/writes, FLR recovery, link-up polling, power-state transitions, and RAS/error-injection paths provide practical coverage.
