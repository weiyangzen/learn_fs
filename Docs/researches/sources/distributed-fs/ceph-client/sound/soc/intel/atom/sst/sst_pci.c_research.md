# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pci.c

## Purpose
This file provides legacy PCI enumeration for the Intel SST LPE driver on Merrifield/Tangier-style devices. It maps PCI BAR resources, validates relocated DDR/IMR firmware base expectations, initializes the common SST context, and registers runtime PM for PCI-bound hardware.

## Important APIs, types, and functions
Resource mapping is implemented by `sst_platform_get_resources()`. PCI lifecycle is `intel_sst_probe()` and `intel_sst_remove()`, registered through `sst_driver` and the `intel_sst_ids` PCI table. It uses `relocate_imr_addr_mrfld()` to compare the PCI DDR base against platform library metadata.

## Control flow
Probe allocates `intel_sst_drv`, stores platform data from `pci->dev.platform_data`, records the IRQ and firmware filename, calls `sst_context_init()`, enables the PCI function, stores a PCI reference, maps DDR/SHIM/mailbox/IRAM/DRAM resources, stores driver data, and configures runtime PM. Remove calls common cleanup, releases the PCI reference, and clears driver data.

## State and persistence behavior
The file creates no persistent state beyond fields in `intel_sst_drv` and the PCI driver-data pointer. PCI-managed region and ioremap resources are tied to the PCI device lifetime.

## Dependencies and integration points
It depends on PCI core APIs, platform data supplied to the PCI device, common SST context helpers, and firmware/library metadata from `asm/platform_sst_audio.h`. Runtime PM callbacks are provided by `intel_sst_pm`.

## Risks and edge cases
The probe calls `sst_context_init()` before enabling the PCI device and before mapping resources, but common context init requests IRQ and can rely on mapped `shim` fields, making ordering especially sensitive for this legacy path. DDR mapping and base validation only apply to `PCI_DEVICE_ID_INTEL_SST_TNG`. Missing `lib_info` or relocated base mismatch fails probe.

## Test signals
Test PCI probe/remove on supported Tangier hardware, BAR request/mapping failures, DDR base relocation validation, firmware filename selection, IRQ handling after resource mapping, runtime PM enablement, and cleanup after partial probe failures.
