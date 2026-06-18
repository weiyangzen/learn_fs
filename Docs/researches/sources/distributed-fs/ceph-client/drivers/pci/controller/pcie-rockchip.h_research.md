# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.h

Purpose: Defines Rockchip AXI PCIe register offsets, bit fields, address translation constants, reset names, shared controller state, MMIO accessors, and common helper prototypes for host and endpoint drivers.

Important APIs/types/functions: Central type is `struct rockchip_pcie`, holding `reg_base`, `apb_base`, PHYs, resets, clocks, regulators, PERST GPIO, lane/link fields, IRQ domain, message region, RC/EP mode flag, and endpoint memory resource. Static inline `rockchip_pcie_read()` and `rockchip_pcie_write()` wrap APB MMIO. Register macros cover client config/status, core management, RC config, AXI outbound/inbound windows, endpoint BAR configuration, MSI/MSI-X controls, and message generation.

Control flow: No executable flow beyond inline MMIO accessors. The constants determine setup paths in `pcie-rockchip.c`, RC paths in `pcie-rockchip-host.c`, and EPC paths in `pcie-rockchip-ep.c`.

State and persistence: The header declares the in-memory state shape shared by both modes. Register definitions describe persistent controller state for link training, BAR windows, ATU regions, interrupts, and MSI/INTx generation.

Dependencies/integration: Includes kernel clock, reset, PCI, and ECAM headers. It is a private local interface and is not intended as a cross-subsystem ABI.

Risks: Duplicate definitions of `ROCKCHIP_PCIE_AT_MIN_NUM_BITS`, `ROCKCHIP_PCIE_AT_MAX_NUM_BITS`, and `ROCKCHIP_PCIE_AT_SIZE_ALIGN` exist in the header and should remain consistent if edited. Bit-field write-mask helpers encode the upper-half write-mask convention of `PCIE_CLIENT_CONFIG`; replacing them with plain values would break atomic updates. Reset-name order matters.

Test signals: Full compile coverage for host and endpoint objects, host enumeration, endpoint BAR/MSI behavior, static inspection against hardware manuals, and runtime logs for link, lanes, interrupts, and ATU programming.
