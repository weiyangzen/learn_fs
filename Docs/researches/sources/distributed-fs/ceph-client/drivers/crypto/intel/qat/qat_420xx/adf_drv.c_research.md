# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_drv.c

## Purpose
This is the PCI physical-function driver for Intel QAT 420xx devices. It binds the `PCI_DEVICE_ID_INTEL_QAT_420XX` device, allocates an `adf_accel_dev`, initializes 420xx-specific Gen4 hardware metadata, maps device BARs, seeds the in-kernel QAT configuration table, and brings the accelerator up through the common `adf_dev_up()` lifecycle.

## Important APIs, Types, And Functions
The local entry points are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, and `adf_cleanup_accel()`. Probe calls `adf_devmgr_add_dev()`, `adf_init_hw_data_420xx()`, `adf_cfg_dev_add()`, `adf_gen4_cfg_dev_init()`, `adf_dbgfs_init()`, `adf_dev_up()`, and `adf_sysfs_init()`. The PCI driver also exposes `adf_sriov_configure` and `adf_err_handler` through the common QAT framework.

## Control Flow
Probe rejects invalid NUMA placement, allocates device and hardware-data objects with `devm_kzalloc()`, reads PCI revision and Gen4 fuse state, computes accelerator/AE masks, creates config, enables PCI, installs a 64-bit DMA mask, initializes Gen4 default services, obtains capability masks, maps memory BARs selected by `ADF_GEN4_BAR_MASK`, saves PCI state, initializes debugfs, starts the device, and adds sysfs. Error paths stop the device if needed, remove debugfs/config/device-manager state, and clean 420xx hw data.

## State And Persistence Behavior
All state is volatile kernel state anchored in `struct adf_accel_dev`, its `hw_device`, PCI BAR mappings, config table, debugfs directory, sysfs entries, and common framework status bits. Firmware names are advertised with `MODULE_FIRMWARE()` but no data is persisted by this file.

## Dependencies And Integration Points
The file depends on PCI core, DMA mapping, Gen4 config/hardware helpers, the common QAT device manager, debugfs, sysfs, AER, SR-IOV, and the 420xx hardware-data module. It imports the `CRYPTO_QAT` namespace and soft-depends on `crypto-intel_qat`.

## Risks
The AE-mask validation assumes AE0/admin availability semantics inherited from Gen4 code. Any mismatch between BAR order, 420xx hardware metadata, or firmware files can fail probe. `adf_shutdown()` assumes `adf_devmgr_pci_to_accel_dev()` returns a device and does not null-check before `adf_dev_down()`.

## Test Signals
Useful signals are successful PCI probe, firmware load of `qat_420xx.bin` and `qat_420xx_mmp.bin`, `qat_dev*` sysfs/debugfs creation, crypto/compression registration depending on configured services, SR-IOV enable/disable, FLR/AER recovery, and clean module unload.
