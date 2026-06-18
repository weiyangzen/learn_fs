<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.c -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.c

### Purpose
`mhi_controller.c` builds and manages the MHI controller used by qaic PCI devices. It defines family-specific channel/event tables, firmware image paths, controller callbacks, register access quirks, initial power-up, reset handling, and teardown.

### Important APIs, Types, And Functions
Public functions are `qaic_mhi_register_controller()`, `qaic_mhi_free_controller()`, `qaic_mhi_start_reset()`, and `qaic_mhi_reset_done()`. Important internal data are `fw_image_paths`, `aic100_channels`, `aic200_channels`, `aic100_events`, `aic200_events`, and `mhi_cntrl_configs`. Internal helpers implement register read/write callbacks, no-op runtime get/put, MHI status callbacks, and `mhi_reset_and_async_power_up()` fallback from SBL to PBL.

### Control Flow
Registration allocates `struct mhi_controller`, fills PCI device pointer, IOVA range, status/runtime/register callbacks, BAR registers, IRQ array, IRQ flags, firmware image path, family name/segment length, copies the family config with the module timeout, registers the controller, prepares power-up, and asynchronously powers up. If async power-up returns `-EIO` while in SBL, it performs a SoC reset, polls execution environment up to 25 seconds for PBL, then retries async power-up. Free powers down, unprepares, and unregisters. Reset start powers down with link-up true; reset done tries async power-up again.

### State, Persistence, And Dependencies
The controller state is owned by the MHI core after registration and referenced by `qaic_device->mhi_cntrl`. Channel tables define QAIC loopback, Sahara, diag, SSR, QDSS/logging, control, status, telemetry, debug, timesync, periodic timesync, and IPCR channels with execution-environment masks. Dependencies include Linux MHI, PCI, firmware files under `qcom/aic100/sbl.bin` and `qcom/aic200/sbl.bin`, and qaic reset cleanup callbacks.

### Integration Points
`qaic_drv.c` calls registration during PCI probe and reset helpers during PCI reset flows. MHI child drivers in qaic modules bind to configured channel names. `mhi_status_cb()` calls `qaic_dev_reset_clean_local_state()` on system error and logs fatal errors.

### Risks
The large static channel tables are hardware ABI; wrong channel number, direction, event ring, or EE mask breaks child drivers or firmware loading. The SOC_HW_VERSION read quirk returns a synthetic value at offset `0x224`; removing it can cause false link-down errors. The controller uses a full physical IOVA range, so remote-side size calculations depend on `PHYS_ADDR_MAX - 1`. Shared MSI handling changes IRQ flags. Power-up fallback timing is fixed and may fail slow devices.

### Test Signals
Probe AIC100 and AIC200, verify all expected MHI channels enumerate in SBL and AMSS, load Sahara firmware from configured paths, test SBL reset fallback, trigger MHI fatal/system error callbacks, exercise PCI reset start/done, vary `mhi_timeout_ms`, and confirm no channel/event table mismatches under MHI debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.c -->
