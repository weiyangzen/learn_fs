# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.c

## Purpose
`ufs-rockchip.c` is the Rockchip UFS platform variant, currently matching RK3576. It wires the generic UFS host core to Rockchip reset controls, clocks, memory-mapped HCI/MPHY GRF registers, device reset GPIO, RK3576 PHY initialization, and runtime/system PM behavior.

## Important APIs, Types, And Functions
The main variant table is `ufs_hba_rk3576_vops`, with `.init`, `.device_reset`, `.hce_enable_notify`, and `.phy_initialization`. `ufs_rockchip_common_init()` maps named resources (`hci_grf`, `mphy_grf`, `mphy`), obtains reset controls, enables `ref_out` and bulk clocks, acquires reset GPIO, and binds `struct ufs_rockchip_host` to the HBA. `ufs_rockchip_rk3576_phy_init()` programs UniPro/M-PHY DME attributes and direct MPHY registers. PM entry points wrap `ufshcd_runtime_suspend/resume` and `ufshcd_system_suspend/resume`.

## Control Flow And State
Probe looks up variant ops from OF match data and calls `ufshcd_pltfrm_init()`. RK3576 init sets UFSHCD quirks/capabilities for timeout handling, BKOPS, deep sleep, clock scaling, and WriteBooster, sets default runtime/system PM levels to level 5, and performs common resource setup. HCE PRE resets the controller; HCE POST resets/enables DME and runs PHY initialization. The PHY path toggles M-PHY config mode, writes lane-specific TX/RX timing and power-saving values, writes common and per-lane MPHY registers, then configures CPort link-up attributes.

Runtime state is held in `struct ufs_rockchip_host`: MMIO bases, reset GPIO/control, enabled clocks, and HBA backpointer. Suspend disables `ref_out` and may keep the genpd on depending on PM level; resume reenables `ref_out`, resets the controller for runtime resume, then returns control to the UFS core.

## Dependencies And Integration Points
The driver depends on platform resources named by DT, Linux reset/clock/GPIO/PM-domain APIs, `ufshcd-pltfrm`, UFS UniPro attributes, and the register definitions in `ufs-rockchip.h`. OF compatible `rockchip,rk3576-ufshc` supplies the RK3576 variant table.

## Risks And Edge Cases
Most DME writes in `ufs_rockchip_rk3576_phy_init()` ignore return codes, so partial PHY programming can be reported only later as link failure. Required reset GPIO and named MMIO resources make DT correctness critical. PM handling must coordinate `ref_out` with genpd state and UFS core suspend levels; a mismatch can strand the link or over-power the domain. There is no remove-time custom cleanup beyond managed resources and `ufshcd_pltfrm_remove()`.

## Test Signals
Use RK3576 hardware boot tests, DT resource-name validation, HCE PRE/POST link startup, runtime suspend/resume with PM levels below and at level 5, system suspend with `device_set_awake_path()`, reset GPIO pulse observation, and link stability under clock scaling and WriteBooster-enabled workloads.
