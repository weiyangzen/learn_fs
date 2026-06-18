# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_drv.c

## Purpose
This is the PCI PF driver for C3xxx QAT devices. It provides module registration, PCI probe/remove/shutdown, manual memory/BAR cleanup, 48-bit DMA setup, device-manager registration, and common QAT device startup.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. The PCI driver exposes SR-IOV and AER callbacks via `adf_sriov_configure` and `adf_err_handler`.

## Control Flow
Module init requests `intel_qat`, then registers the PCI driver. Probe validates PCI ID and NUMA node, allocates `adf_accel_dev` and hw data with `kzalloc_node()`, registers the device manager entry, initializes C3xxx hw data, reads revision/fuse/softstrap registers, validates masks, creates config, enables PCI, sets a 48-bit DMA mask, requests regions, computes capabilities, maps all memory BARs, saves PCI state, initializes debugfs, and starts the device. Remove stops the device, unmaps BARs, removes config/debugfs/device-manager entries, releases PCI resources, and frees memory.

## State And Persistence Behavior
Runtime state is manually allocated and must be explicitly freed. Config/debugfs/framework state exists only while bound. PCI state is saved for reset recovery. There is no disk persistence.

## Dependencies And Integration Points
The driver depends on Linux PCI/DMA, C3xxx hardware data, Gen2 common QAT framework, debugfs, config, AER, SR-IOV, firmware, and `intel_qat` base module aliasing.

## Risks
Manual cleanup has several unwind labels and requires correct ordering. BAR indexing uses every selected memory BAR and can leave partially mapped resources on failure. `adf_shutdown()` assumes lookup success. DMA is limited to 48 bits, unlike Gen4/Gen6.

## Test Signals
Probe/remove cycles, firmware load, 48-bit DMA operation, device-manager status ioctl, debugfs `dev_cfg`, SR-IOV enable/disable, AER reset, and memory-leak/DMA-debug clean runs are useful signals.
