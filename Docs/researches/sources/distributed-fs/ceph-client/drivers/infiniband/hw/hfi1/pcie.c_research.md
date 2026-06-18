# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pcie.c

## Purpose
`pcie.c` contains the HFI1 driver's PCIe bring-up, BAR mapping, PCI configuration preservation, PCIe capability tuning, AER recovery hooks, and ASIC-specific PCIe link speed transition logic. It is the low-level bridge between Linux PCI core state and the device CSR/MMIO layout used by the rest of the HFI1 driver.

## Important APIs, Types, And Functions
`hfi1_pcie_init()` enables the PCI function, requests BAR regions, sets a coherent DMA mask, and marks the endpoint bus-master capable. `hfi1_pcie_ddinit()` maps BAR0 into uncached CSR windows, a write-combining PIO send-buffer aperture, and a write-combining receive-array aperture, then sets `HFI1_PRESENT`. `hfi1_pcie_ddcleanup()` tears those mappings down. `pcie_speeds()` and `update_lbus_info()` derive link speed/width and Gen3 capability. `save_pci_variables()` and `restore_pci_variables()` preserve command, BAR, ROM, DevCtl/LnkCtl/DevCtl2, MSI-X, and optional TPH config across secondary-bus resets. `tune_pcie_caps()` optionally raises MPS/MRRS and enables extended tags. `hfi1_pci_err_handler` wires Linux PCI error recovery to `hfi1_disable_after_error()` and `hfi1_init()`. `do_pcie_gen3_transition()` performs the long firmware-download, SerDes EQ, SBus, gasket, SBR, config-restore, retry, and link-validation sequence.

## Control Flow
Probe first calls the generic PCI setup, then maps device memory once `hfi1_devdata` exists. BAR0 is split because PIO buffers occupy the tail of the chip address space and need WC mapping while CSR regions stay uncached. Gen3 transition is conditional on ASIC silicon, requested module parameters, current speed, upstream bridge access, and Gen3 capability. It acquires the SBus resource, disables thermal polling, loads PCIe firmware, programs port-logic registers and EQ tables, arms gasket logic, forces a secondary bus reset through the parent bridge, restores PCI config, verifies gasket status and per-lane errors, updates cached link info, and retries if speed or width missed the target. AER callbacks request reset for frozen channels, disconnect on permanent failure, and reinitialize asynchronously on resume.

## State And Persistence
PCI state is cached in `dd` fields so device resets can be survived without relying on the PCI core retaining live hardware config. MMIO base pointers and physical address fields persist for the driver's lifetime until cleanup. Link metadata is cached in `lbus_width`, `lbus_speed`, `lbus_info`, and `link_gen3_capable`. Module parameters (`pcie_caps`, `pcie_target`, `pcie_force`, `pcie_retry`, `pcie_pset`, `pcie_ctle`) alter capability tuning and transition behavior only at runtime; no nonvolatile state is written.

## Dependencies And Integration Points
The file depends on Linux PCI/PCIe config helpers, DMA mask APIs, IO mapping APIs, AER recovery infrastructure, HFI1 CSR accessors, generated chip register definitions, ASPM control, SBus firmware loading, chip-resource locking, link bounce/reinit paths, and module parameters. Its mapped `piobase` and CSR windows are consumed by PIO, receive, interrupt, and firmware-management code throughout the driver.

## Risks
The Gen3 transition performs reset-sensitive operations while hoping the kernel and other devices do not access the endpoint during SBR. Error exits inside the SBus critical section must release resources and restore thermal polling; early returns after firmware/config failures are especially important to audit. `tune_pcie_caps()` trusts module-param bit fields and may alter upstream bridge settings. BAR size assumptions are strict. Mapping failures clean up partially initialized state, but later users depend on `HFI1_PRESENT` accurately tracking valid CSR access.

## Test Signals
Useful signals include probe failure at each PCI setup stage, 32-bit DMA fallback, BAR length mismatch, MMIO read-all-ones detection, save/restore PCI config across simulated reset, Gen1/Gen2/Gen3 module-param combinations, invalid `pcie_pset`, firmware download failure, SBR failure, gasket error/status variants, AER frozen/permanent paths, and link-width retry behavior.
