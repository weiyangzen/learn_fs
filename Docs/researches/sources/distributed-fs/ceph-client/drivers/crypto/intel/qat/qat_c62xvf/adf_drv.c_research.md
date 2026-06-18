# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_drv.c

## Purpose
This is the PCI VF driver for C62x QAT virtual functions. It binds C62x VF PCI IDs, creates a VF `adf_accel_dev`, initializes VF metadata, maps PCI resources, starts the common QAT framework without PF-only init, and coordinates with the PF over PF/VF messages.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. Important common calls include `adf_devmgr_add_dev()`, `adf_init_hw_data_c62xiov()`, `adf_cfg_dev_add()`, `adf_dev_up()`, `adf_flush_vf_wq()`, and `adf_clean_vf_map(true)`.

## Control Flow
Probe validates the VF device ID, allocates the VF, marks `is_vf`, locates the PF via `pdev->physfn`, adds it to the device manager, initializes hardware data, adds config, enables PCI, sets 48-bit DMA, requests regions, maps all memory BARs, enables bus mastering, initializes the PF/VF completion, initializes debugfs, and calls `adf_dev_up(accel_dev, false)`. Remove flushes VF work, stops the device, unmaps BARs, removes config/debugfs/device-manager state, releases PCI resources, and frees memory.

## State And Persistence Behavior
Runtime state is manually allocated and volatile. PF/VF messaging state is stored in `accel_dev->vf`; stable VF numbering is tracked by the common device manager's VF map.

## Dependencies And Integration Points
It integrates Linux PCI/DMA, C62x VF hardware data, Gen2 VF PFVF callbacks, debugfs, config, common QAT lifecycle, and the base `intel_qat` module.

## Risks
The VF depends on PF presence and response timing. Manual cleanup and workqueue flushing are race-sensitive. Like the C3xxx VF driver, it uses 48-bit DMA and maps all memory BARs in order.

## Test Signals
SR-IOV VF creation/removal, host and guest VF binding, PF/VF init/shutdown messages, crypto/compression traffic, hot-remove, and module unload with clean VF map are useful signals.
