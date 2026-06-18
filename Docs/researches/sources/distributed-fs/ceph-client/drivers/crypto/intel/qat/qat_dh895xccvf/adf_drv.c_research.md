# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_drv.c

Purpose: implements the PCI driver for DH895xCC QAT virtual functions.

Important APIs and functions: `adf_probe()` validates the VF PCI ID, allocates an `adf_accel_dev`, marks it `is_vf`, links it to its PF in the device manager, initializes VF hw data, creates config, enables PCI/DMA, maps BARs, initializes VF2PF completion, starts debugfs, and calls `adf_dev_up(accel_dev, false)`. `adf_remove()` flushes VF work, stops the device, cleans ADF state, releases PCI resources, and frees memory. Module exit unregisters the PCI driver and clears the VF map.

Control flow: unlike PF probe, VF probe does not read fuse masks from hardware or save PCI state. It uses fixed one-engine masks from VF hw data and depends on PF messaging for lifecycle coordination. Remove explicitly calls `adf_flush_vf_wq()` before shutdown to drain PF/VF work.

State and persistence: persistent state includes VF `adf_accel_dev`, PF association, mapped BARs, config/debugfs, completion `accel_dev->vf.msg_received`, and devmgr registration under the PF.

Dependencies and integration points: depends on Linux PCI/DMA, ADF VF/PFVF common code, config/debugfs, and DH895xCCVF hw data. Imports `CRYPTO_QAT`.

Risks and test signals: probe assumes `pdev->physfn` maps to a PF accel device; missing PF association can affect devmgr behavior. Cleanup looks up PF during removal, so PF teardown ordering matters. Tests should cover PF absent/present probe, DMA/BAR failure rollback, VF2PF completion behavior, workqueue flushing, remove ordering, and module unload `adf_clean_vf_map(true)`.
