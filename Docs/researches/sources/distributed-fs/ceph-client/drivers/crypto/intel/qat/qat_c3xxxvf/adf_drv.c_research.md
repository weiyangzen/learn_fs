# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_drv.c

## Purpose
This is the PCI virtual-function driver for C3xxx QAT VFs. It binds VF PCI IDs, associates a VF with its PF when present, initializes VF-specific hardware metadata, maps VF BARs, starts the common QAT device lifecycle without PF-only initialization, and notifies the PF through PF/VF messaging.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. It uses `adf_init_hw_data_c3xxxiov()`, `adf_vf2pf_notify_init()`, `adf_vf2pf_notify_shutdown()`, `adf_flush_vf_wq()`, and `adf_clean_vf_map(true)`.

## Control Flow
Probe validates VF ID, allocates the device, marks it `is_vf`, looks up the physical PF by `pdev->physfn`, adds the VF to the device manager, initializes hw data and config, enables PCI, sets a 48-bit DMA mask, requests regions, maps memory BARs, sets bus master, initializes `vf.msg_received` completion, creates debugfs, and calls `adf_dev_up(accel_dev, false)`. Remove flushes VF work, stops the device, cleans common and PCI resources, and frees memory. Module exit unregisters the PCI driver and cleans VF ID mappings.

## State And Persistence Behavior
VF state is volatile and manually allocated. PF/VF response state lives in the `accel_dev->vf` union, including completion and temporary response. Device IDs are tracked in the common VF map for stable user-visible numbering.

## Dependencies And Integration Points
It integrates Linux PCI/DMA, Gen2 VF hardware data, QAT config/debugfs/device manager, PF/VF messaging, VF workqueues, and the common start/stop path.

## Risks
PF lookup may be null in guest-like scenarios and device-manager logic handles that differently from host VFs. Manual cleanup ordering is sensitive. VF operation depends on PF responses; failure to flush work on removal can race with teardown.

## Test Signals
Create/remove C3xxx VFs, bind them on host or guest, observe successful PF/VF init notification, run crypto/compression requests, remove while idle and under load, and verify VF map cleanup after module unload.
