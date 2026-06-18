## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-visconti.c

Purpose: Toshiba Visconti DesignWare PCIe root-complex glue driver. It controls ULREG, SMU, and MPU register blocks, clocks, reset sequencing, link training, and a CPU-address translation quirk for Visconti SoCs.

Important APIs, types, and functions: `struct visconti_pcie` embeds DWC state and holds ULREG/SMU/MPU bases plus ref/core/aux clocks. Register helpers wrap relaxed MMIO. `visconti_pcie_host_init()` enables SMU clocks, releases ULREG reset, selects RC mode, drives PERST, releases power-up reset, waits for PHY SRAM init, marks external load done, and waits for core reset monitor. `visconti_pcie_start_link()` enables LTSSM, polls L0, unmasks event interrupts, and enables MPU memory protection if DWC sees link-up. `visconti_pcie_stop_link()` disables LTSSM and MPU. `visconti_pcie_cpu_addr_fixup()` strips `pp->io_base` from CPU addresses for this SoC bus mapping.

Control flow: probe allocates state, maps three named resources, acquires clocks, sets DWC ops, gets the `"intr"` IRQ, attaches host ops, and calls `dw_pcie_host_init()`. DWC host setup calls the platform init and link callbacks.

State and persistence: volatile register state includes SMU clock/reset bits, ULREG mode/PERST/PHY status/LTSSM/event masks, MPU enable bit, DWC host state, and clock handles. There is no persistent state and no remove path.

Dependencies and integration points: DesignWare host core, platform MMIO resources `"ulreg"`, `"smu"`, `"mpu"`, named clocks `ref`, `core`, `aux`, platform IRQ `"intr"`, and DT compatible `toshiba,visconti-pcie`.

Risks: Link-up checks `val & PCIE_UL_S_L0`, which treats any set bit overlap with `0x11` as true rather than equality; this may over-report link in other LTSSM states. Clock handles are acquired but not explicitly enabled in this file, implying reset/clock control is partially through SMU or external setup. CPU address fixup depends on DT `io_base`.

Test signals: boot enumeration, host init poll completion, LTSSM L0 polling, event-mask setup, MPU enable/disable, outbound address correctness for IO windows, and behavior when PHY/core poll timeouts occur.
