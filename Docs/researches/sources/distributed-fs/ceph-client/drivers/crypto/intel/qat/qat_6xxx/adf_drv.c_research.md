# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_drv.c

## Purpose
This is the PCI PF driver for Intel QAT Gen6 devices. It differs from older QAT probe code by using devm cleanup actions heavily, mapping fixed 64-bit BAR numbers, reading multiple fuse registers before hardware-data setup, and selecting default services based on SKU and device ID parity.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_shutdown()`, `adf_gen6_cfg_dev_init()`, and devm cleanup callbacks (`adf_device_down()`, `adf_dbgfs_cleanup()`, `adf_cfg_device_remove()`, `adf_cleanup_hw_data()`, `adf_devmgr_remove()`). The PCI table binds `PCI_DEVICE_ID_INTEL_QAT_6XXX`.

## Control Flow
Probe rejects invalid NUMA placement, allocates device and hw-data objects, reads revision and Gen6 fuse registers, enables PCI, registers the device manager entry, installs devm cleanup actions, initializes Gen6 hw data, computes accelerator/AE masks and SKU, creates config, sets a 64-bit DMA mask, writes default `ServicesEnabled` (`sym` for WCY, otherwise `dc` on odd accel IDs and `sym;asym` on even IDs), reads capability masks, maps SRAM/PMISC/ETR BARs with `pcim_iomap_region()`, saves PCI state, enables RAS, creates debugfs, starts the device, and creates sysfs.

## State And Persistence Behavior
Runtime state is in `adf_accel_dev`, `hw_data`, devm-managed cleanup stack, BAR mappings, config table, debugfs/sysfs, and framework status bits. The service default is stored in the volatile config table and affects firmware/capability setup.

## Dependencies And Integration Points
It integrates Linux PCI/DMA, Gen6 shared and hardware-data modules, heartbeat config, QAT config/device/debug frameworks, AER, SR-IOV, firmware loading, and sysfs.

## Risks
The default service split by `accel_id % 2` is policy-sensitive. The no-`remove` driver relies on devm actions for cleanup. `adf_dev_up()` failure manually calls `adf_dev_down()` before the devm down action is installed. `adf_shutdown()` also lacks a null check on device-manager lookup.

## Test Signals
Signals include successful probe with fixed BAR map 0/2/4, correct default service based on WCY and accel ID, firmware load, PM/VC initialization, AER/FLR recovery, SR-IOV behavior, sysfs/debugfs creation, and clean unbind/shutdown via devm cleanup.
