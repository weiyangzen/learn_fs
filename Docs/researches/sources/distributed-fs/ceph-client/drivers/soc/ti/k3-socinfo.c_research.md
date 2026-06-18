# sources/distributed-fs/ceph-client/drivers/soc/ti/k3-socinfo.c

## Purpose
This file registers TI K3 SoC identity information on the Linux SoC bus. It reads the CTRLMMR WKUP JTAG ID register, validates the TI manufacturer field, maps the part number to a family name, maps the variant to an SR revision string, and registers a `soc_device_attribute`.

## Important APIs, Types, And Functions
Important data includes the `k3_soc_ids` part-number table and revision maps for J721E and AM62LX. `k3_chipinfo_partno_to_names` resolves `family`, while `k3_chipinfo_variant_to_sr` allocates a revision string. `k3_chipinfo_probe` performs MMIO regmap setup, field extraction, root-node `model` lookup, and `soc_device_register`. The driver is registered at `subsys_initcall` for compatible `ti,am654-chipid`.

## Control Flow
Probe maps resource 0, wraps it with a regmap, reads offset 0, checks `MFG == 0x17`, extracts `variant` and `partno`, allocates attributes, populates family/revision/machine, and registers the SoC device. Errors free allocated strings/attributes before returning.

## State And Persistence
The driver has no mutable global runtime state. Its persistent kernel-visible result is the SoC bus device and strings allocated for `soc_device_attribute`. Hardware state is read-only chip identification.

## Dependencies And Integration Points
It depends on an MMIO chipid node, regmap MMIO, OF root `model`, and Linux `sys_soc`. Other drivers can match revisions using `soc_device_match`; for example, the K3 ring accelerator uses SoC family/revision to enable a DMA reset quirk.

## Risks And Test Signals
Risks include unknown part numbers, variant table gaps, invalid manufacturer fields, and memory leaks if registration fails. Test signals are boot logs like `Family:<name> rev:<SR> JTAGID[...] Detected`, populated `/sys/devices/soc*` fields, and correct `soc_device_match` behavior for AM65X/J721E/AM62-class boards.
