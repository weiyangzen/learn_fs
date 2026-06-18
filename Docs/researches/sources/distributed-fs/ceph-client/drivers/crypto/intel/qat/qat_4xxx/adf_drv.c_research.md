# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_drv.c

## Purpose
This is the PCI PF driver for QAT 4xxx, 401xx, and 402xx devices. It handles PCI discovery, validates NUMA and fused accelerator presence, attaches device-specific hardware metadata, configures PCI/DMA/BAR resources, and starts the accelerator through the shared QAT framework.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, and `adf_cleanup_accel()`. The PCI table binds `PCI_DEVICE_ID_INTEL_QAT_4XXX`, `PCI_DEVICE_ID_INTEL_QAT_401XX`, and `PCI_DEVICE_ID_INTEL_QAT_402XX`. The `pci_driver` supplies SR-IOV and AER callbacks through `adf_sriov_configure` and `adf_err_handler`.

## Control Flow
Probe allocates `adf_accel_dev` and `adf_hw_device_data`, registers with `adf_devmgr_add_dev()`, initializes 4xxx hw data with the PCI device ID, reads revision and fuse data, computes masks/SKU, creates config, enables PCI, sets a 64-bit DMA mask, seeds Gen4 config, derives capability masks, requests and maps Gen4 memory BARs, saves PCI state, enables RAS accounting, initializes debugfs, calls `adf_dev_up(accel_dev, true)`, and initializes sysfs. Remove and shutdown call `adf_dev_down()` before cleanup.

## State And Persistence Behavior
Device state persists only while the PCI device is bound: `accel_dev`, its config table, debugfs/sysfs nodes, hardware callback table, PCI BAR mappings, and framework status bits. `pcim_*`/`devm_*` resources are tied to device lifetime, while common framework resources are explicitly cleaned.

## Dependencies And Integration Points
The driver relies on Linux PCI/DMA, Gen4 config, 4xxx hardware data, QAT device manager, debugfs/sysfs, AER, SR-IOV, common init/shutdown, and firmware files declared by `MODULE_FIRMWARE()`.

## Risks
Failure unwind must remove the device from the manager after it has been added. Capability validation happens before BAR mapping but after config, so config cleanup matters on early errors. `adf_shutdown()` lacks a null check on the device-manager lookup. Firmware declarations must match `adf_4xxx_hw_data.c` selection.

## Test Signals
Probe logs, BAR mappings, `qat_dev*` status via ioctl/sysfs, `dev_cfg` debugfs, algorithm registration, firmware load by SKU, SR-IOV VF creation/removal, AER/FLR restart, and clean unload are the main test signals.
