# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.c

## Purpose
`ufs-sprd.c` is the Unisoc/Sprd UFS platform variant for `sprd,ums9620-ufs`. It supplies reset, syscon, regulator, secure-monitor crypto enablement, PHY SRAM/calibration programming, Hibern8 reference-clock control, and variant operations for the generic UFS core.

## Important APIs, Types, And Functions
The driver uses `struct ufs_sprd_host` and `struct ufs_sprd_priv` from `ufs-sprd.h`. Common helpers parse reset controls, syscon phandles, and regulators; `ufs_sprd_common_init()` allocates host state, binds match-data private ops, sets UFS capabilities/quirks, and parses DT. N6-specific callbacks include `ufs_sprd_n6_init()`, `sprd_ufs_n6_hce_enable_notify()`, `ufs_sprd_n6_phy_init()`, `sprd_ufs_n6_h8_notify()`, `ufs_sprd_n6_device_reset()`, and `ufs_sprd_suspend()`.

## Control Flow And State
Probe retrieves the OF match entry and passes its embedded variant ops to `ufshcd_pltfrm_init()`. N6 init enables the MPHY regulator and, if crypto remains advertised, calls `ufs_sprd_n6_key_acc_enable()` to enable key-register access via an ARM SMCCC SiP call after ensuring HCE is set. HCE PRE sets PHY SRAM flags in syscon, resets the host, and retries crypto access; HCE POST initializes PHY DME attributes, waits for SRAM init completion via syscon polling, applies lane AFE calibration writes, enables MPHY, and records UniPro version.

The power-change notify configures initial adaptation when UniPro is at least 1.8. Hibern8 notify disables UIC completion interrupt before enter and controls AON APB reference-clock/PLL bits around enter/exit. Suspend disables auto-Hibern8 timer under the host lock during PRE_CHANGE. Runtime state includes reset controls, syscon regmaps, regulator handles, HBA backpointer, and cached UniPro version.

## Dependencies And Integration Points
The driver depends on DT match data, syscon/regmap, reset controls named `"controller"` and `"device"`, regulator `"vdd-mphy"`, ARM SMCCC, UFS core PM/link callbacks, and vendor DME attributes in `ufs-sprd.h`. It advertises clock gating, crypto, and WriteBooster to the core, with crypto dynamically disabled if secure firmware refuses key access.

## Risks And Edge Cases
`ufs_sprd_n6_key_acc_enable()` loops around HCE enable and may clear crypto capability on failure; this affects blk-crypto availability for the lifetime of the HBA. PHY init depends on a 10-iteration millisecond-scale SRAM done poll and ignores many DME set return values. Hibern8 notification masks UIC completion interrupts and toggles reference clocks, so incorrect callback ordering can produce missed completions or inaccessible HCI state.

## Test Signals
Validate probe with all DT phandles present, regulator enable failure paths, SMCCC crypto success/failure, HCE PRE/POST sequencing, PHY SRAM timeout handling, Hibern8 enter/exit with reference-clock scope checks, suspend auto-Hibern8 timer clearing, and power-mode changes on UniPro 1.8+ devices.
