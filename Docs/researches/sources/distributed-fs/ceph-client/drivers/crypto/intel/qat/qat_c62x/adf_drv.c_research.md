# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_drv.c

## Purpose
This is the PCI PF driver for C62x QAT devices. It performs PCI binding, manual allocation and cleanup, fuse/softstrap reading, 48-bit DMA setup, BAR mapping, debugfs/config/device-manager integration, and common accelerator startup.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. The PCI table binds `PCI_DEVICE_ID_INTEL_QAT_C62X`.

## Control Flow
Module init requests the base `intel_qat` module and registers the PCI driver. Probe validates device ID and NUMA placement, allocates device and hw-data objects, registers with the device manager, initializes C62x hardware metadata, reads revision/fuse/softstrap registers, computes masks/SKU, creates config, enables PCI, sets a 48-bit DMA mask, requests regions, reads capabilities, maps memory BARs with an index offset when a fuse bit is set, saves PCI state, initializes debugfs, and calls `adf_dev_up(accel_dev, true)`. Remove stops and cleans all resources.

## State And Persistence Behavior
State is volatile and manually managed. PCI BAR mappings, config/debugfs entries, device-manager registration, saved PCI state, and status bits persist only while bound.

## Dependencies And Integration Points
The driver integrates Linux PCI/DMA, C62x hardware metadata, Gen2 QAT framework, config/debugfs, firmware loading, AER, SR-IOV, and common crypto/compression services.

## Risks
BAR indexing is conditional on `ADF_DEVICE_FUSECTL_MASK`, making resource mapping device-variant sensitive. Manual unwind paths must avoid leaks and double free. `adf_shutdown()` assumes the device-manager lookup succeeds.

## Test Signals
Probe/remove cycles, firmware load, C62x algorithm registration, 48-bit DMA, status ioctl, debugfs config, SR-IOV creation, AER reset, and DMA/memory sanitizer runs are useful validation.
