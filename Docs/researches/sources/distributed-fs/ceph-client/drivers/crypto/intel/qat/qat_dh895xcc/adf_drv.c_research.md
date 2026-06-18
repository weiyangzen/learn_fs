# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_drv.c

Purpose: implements the PCI driver for Intel QAT DH895xCC physical-function devices.

Important APIs and functions: `adf_probe()` validates PCI ID and NUMA placement, allocates `adf_accel_dev` and hardware data, initializes DH895xCC hw data, reads revision/fuses, creates config, enables PCI/DMA, maps BARs, saves PCI state, starts debugfs, and calls `adf_dev_up()`. `adf_remove()` and `adf_shutdown()` stop the device; cleanup helpers unmap BARs, remove config/debugfs/devmgr entries, clean hw data, release regions, disable PCI, and free memory. Module init registers the PCI driver after requesting `intel_qat`.

Control flow: probe proceeds in staged allocation with labels for cleanup. After BAR mapping and `pci_set_master()`, `adf_dev_up(accel_dev, true)` starts full PF services including firmware and SR-IOV-capable common layers. Remove reverses startup with `adf_dev_down()`, ADF cleanup, PCI cleanup, and free. Shutdown only calls `adf_dev_down()`.

State and persistence: persistent per-device state is `adf_accel_dev`, `adf_accel_pci` BAR mappings, hw data, config table, debugfs entries, and devmgr registration. PCI saved state persists across reset/error flows.

Dependencies and integration points: depends on Linux PCI/module/DMA APIs, ADF common driver, config, debugfs, SR-IOV, error handler, and DH895xCC hw-data callbacks. Module firmware declarations integrate with request_firmware.

Risks and test signals: cleanup ordering must match successful stages; `adf_cleanup_accel()` assumes devmgr registration occurred. BAR enumeration indexes selected memory BARs into `ADF_PCI_MAX_BARS`, so platform resource ordering matters. Tests should cover invalid PCI IDs, NUMA rejection, no AE/accelerator fuse cases, DMA mask failure, BAR map failure, `adf_dev_up()` failure rollback, remove after partial probe failure, SR-IOV configure, PCI error handling, and firmware availability.
