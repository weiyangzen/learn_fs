# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-ufs.c

## Purpose
`zynqmp-ufs.c` exports ZynqMP/Versal firmware helpers for UFS bring-up. It reads secure firmware-managed registers to check M-PHY and SRAM readiness, sets SRAM bypass control, and reads UFS calibration values from eFuse cache.

## Important APIs and functions
`zynqmp_pm_is_mphy_tx_rx_config_ready(bool *is_ready)` reads the PMC IOU SLCR TX/RX config-ready register and reports whether any readiness bits in `GENMASK(3,0)` are set. `zynqmp_pm_is_sram_init_done(bool *is_done)` reads the SRAM CSR and checks bit 0. `zynqmp_pm_set_sram_bypass()` reads SRAM CSR, clears external-load-done, sets bypass, and writes bits 2:1 back through `zynqmp_pm_sec_mask_write_reg()`. `zynqmp_pm_get_ufs_calibration_values(u32 *val)` reads the UFS calibration eFuse cache offset.

## Control flow and integration
All helpers are thin exported wrappers around secure register read or masked-write firmware APIs. They use hard-coded PM register node ids for PMC IOU SLCR and eFuse cache plus local offsets/masks. The boolean query helpers validate output pointers before firmware access.

## State and persistence behavior
The file stores no private state. It reads or modifies firmware-controlled hardware register state. `zynqmp_pm_set_sram_bypass()` has a persistent hardware side effect until changed by firmware/hardware reset or another control path.

## Dependencies and integration points
The file depends on `linux/firmware/xlnx-zynqmp.h` for secure register helpers and on module exports for UFS host/PHY drivers. It is built under `CONFIG_ZYNQMP_FIRMWARE` with the core firmware object.

## Risks and test signals
Risks include register-node/offset drift across SoCs, treating any TX/RX ready bit as ready rather than requiring all lanes, missing null validation in `zynqmp_pm_get_ufs_calibration_values()`, and side effects from masked SRAM writes. Test signals include exported symbol resolution by UFS drivers, successful secure register reads on supported platforms, expected behavior when firmware denies access, and UFS initialization paths observing readiness/calibration values.
