# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_dp.c

Purpose: provides the DRM connector and encoder integration for the HIBMC DP block, including EDID/DPCD discovery, connector status, mode bandwidth validation, AUX registration, HPD ISR handling, and atomic encoder enable/disable.

Important APIs/functions: `hibmc_dp_init()` initializes hardware, encoder, connector, helpers, and HPD polling. `hibmc_dp_detect()` reads DPCD, descriptor, downstream info, branch sink count, and HPD status. `hibmc_dp_mode_valid()` compares mode clock times bpp to current link bandwidth. `hibmc_dp_hpd_isr()` handles threaded HPD plug/unplug events and calls connector hotplug notification.

Control flow: HIBMC KMS init calls `hibmc_dp_init()` when the SERDES control register suggests DP hardware exists. Late connector registration enables DP interrupts and registers AUX; early unregister disables them. Atomic encoder enable disables the stream, mode-sets/trains the DP link, then enables the stream.

State and persistence: uses `struct hibmc_dp` embedded in driver private data. `irq_status` is latched by the primary IRQ handler and interpreted by the threaded handler. DPCD, branch flag, downstream ports, descriptor, and HPD status live under `dp_dev`.

Dependencies and integration points: depends on DRM EDID, DP AUX helpers, atomic helpers, `dp_hw.h`, `dp_comm.h`, and `dp_config.h`. It is connected to MSI vector 1 by `hibmc_drm_drv.c`.

Risks: `irq_status` is used as a latch without explicit locking, so IRQ/thread ordering matters. A nonzero IRQ status with HPD status not in can short-circuit detection. Mode validation uses current software link caps, which may not yet reflect post-training downgrade. Branch-device sink count handling depends on downstream HPD bit.

Test signals: AUX registration, EDID mode enumeration, branch and non-branch sink detect, HPD plug/unplug interrupt flow, link reset on unplug, mode rejection above bandwidth, and atomic enable/disable.
