# sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.c

## Purpose
Implements EDAC support for Freescale/NXP MPC85xx and QorIQ memory-controller families. The file registers three related platform drivers: the shared FSL DDR memory-controller EDAC driver, an MPC85xx L2-cache ECC device, and, when PCI is enabled, a PCI/PCIe error-reporting EDAC device.

## Important APIs, Types, And Functions
- `mpc85xx_pci_err_probe` and `mpc85xx_pci_err_remove` allocate `edac_pci_ctl_info`, map PCI error registers, configure capture/enable registers, and optionally request the PCI error IRQ.
- `mpc85xx_pci_check`, `mpc85xx_pcie_check`, and `mpc85xx_pci_isr` decode and clear PCI or PCIe error status before reporting parity or non-parity errors to EDAC.
- `mpc85xx_l2_err_probe` and `mpc85xx_l2_err_remove` allocate `edac_device_ctl_info`, map L2 error registers, install injection sysfs files, and enable polling or interrupt handling.
- `mpc85xx_l2_check` and `mpc85xx_l2_isr` report single-bit L2 ECC errors as CE and configuration/multibit/tag parity errors as UE.
- `mpc85xx_mc_init` registers the memory-controller, L2, and PCI platform drivers as one module.

## Control Flow
Module initialization normalizes `edac_op_state` to polling or interrupt mode and calls `platform_register_drivers`. The memory-controller driver delegates probe/remove to `fsl_mc_err_probe` and `fsl_mc_err_remove`. The L2 probe opens a devres group, allocates one EDAC device with CPU/L blocks, maps the controller's error window at resource offset `0xe00`, clears pending status, saves `ERRDIS`, enables detection, attaches injection attributes, adds the EDAC device, and requests the IRQ in interrupt mode. L2 checking reads `ERRDET`, dumps captured registers, writes back the detect bits to clear them, and calls CE/UE helpers. The PCI probe follows the same pattern for `edac_pci_ctl_info`, detects PCIe capability, programs PCI or PCIe capture masks, clears status, adds the EDAC PCI device, then either polls or handles shared interrupts.

## State And Persistence
Persistent module state includes allocation indexes and saved hardware registers: `orig_l2_err_disable`, `orig_pci_err_cap_dr`, and `orig_pci_err_en`. Per-device state is held in `struct mpc85xx_l2_pdata` and `struct mpc85xx_pci_pdata`, including mapped register bases, IRQs, EDAC index, and PCIe mode. Remove paths restore saved disable/capture/enable values, dispose IRQ mappings, and free EDAC control structures.

## Dependencies And Integration Points
Depends on Open Firmware resources and IRQs, big-endian MMIO accessors, EDAC core device/PCI APIs, PCI host bridge capability helpers, and shared Freescale DDR EDAC support from `fsl_ddr_edac.h`. Device matching is by OF compatible strings for memory/L2 controllers and by platform device ID for PCI error reporting.

## Risks And Edge Cases
The PCI saved-register variables are module-global, so multiple PCI error devices could overwrite restore state. The probe path uses both devres groups and manual EDAC freeing; error ordering must remain correct to avoid leaked control info. Master aborts are intentionally ignored for PCI config cycles, and PCIe invalid config accesses are masked to avoid noisy boot logs. Injection sysfs stores use `simple_strtoul` guarded only by `isdigit(*data)`, so malformed values can silently no-op.

## Test Signals
Tests should cover poll and interrupt modes, L2 CE/UE bit combinations, PCI parity versus non-parity classification, PCIe capture reset behavior, resource/IRQ acquisition failures, restore of original hardware masks after unload, and visibility/behavior of `inject_data_hi`, `inject_data_lo`, and `inject_ctrl`.
