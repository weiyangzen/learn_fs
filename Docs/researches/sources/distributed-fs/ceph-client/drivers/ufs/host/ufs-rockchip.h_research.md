# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.h

## Purpose
`ufs-rockchip.h` is the private register and state definition header for the Rockchip UFS host variant. It defines lane selector IDs, vendor DME attributes, direct MPHY register offsets, MPHY config mode values, endian/debug attributes, the Rockchip host state structure, and small MMIO helper macros.

## Important APIs, Types, And Macros
Important constants include `SEL_TX_LANE*`, `SEL_RX_LANE*`, `VND_TX_*`, `VND_RX_*`, `CMN_REG*`, `TRSV*_REG*`, `MPHY_CFG`, and `MIB_T_DBG_CPORT_*`. `struct ufs_rockchip_host` stores the HBA pointer, `ufs_phy_ctrl`, `ufs_sys_ctrl`, `mphy_base`, reset GPIO, reset control array, `ref_out_clk`, bulk clocks, and a `caps` field. `ufs_sys_writel()`, `ufs_sys_readl()`, `ufs_sys_set_bits()`, and `ufs_sys_ctrl_clr_bits()` wrap raw MMIO access.

## Control Flow And State
The header has no independent flow. Its definitions are consumed by `ufs-rockchip.c` during RK3576 PHY initialization and reset/clock setup. The state structure is allocated during variant init and then consulted by HCE, device reset, and PM callbacks.

## Dependencies And Integration Points
The header assumes Linux I/O accessors and UFS core types are available through the including C file. The lane selector and register constants must match RK3576 M-PHY hardware documentation. It is private to the Rockchip driver and not an exported UFS subsystem interface.

## Risks And Edge Cases
Register offsets and values are hardware-specific and not self-describing. The MMIO macros perform relaxed raw access without validation; callers must pass mapped bases and valid offsets. The `caps` field is currently not used in the C file, so future changes should either use it deliberately or avoid accumulating dead state.

## Test Signals
The header is tested through successful RK3576 compile and runtime PHY bring-up. Register programming can be validated by readback/debug instrumentation around the MPHY offsets and by link startup stability across both lanes.
