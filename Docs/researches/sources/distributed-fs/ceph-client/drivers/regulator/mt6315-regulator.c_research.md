<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6315-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6315-regulator.c

## Purpose
Implements MediaTek MT6315 SPMI buck regulator support for four buck rails, including voltage control, enable, status, mode switching, and shutdown power-off sequencing.

## Important APIs, Types, And Functions
`struct mt6315_regulator_info` wraps descriptors with status and low-power mode metadata. `struct mt_regulator_init_data` stores per-buck mode-set masks that vary by SPMI USID. Key functions are `mt6315_map_mode()`, `mt6315_regulator_get_mode()`, `mt6315_regulator_set_mode()`, `mt6315_get_status()`, `mt6315_regulator_probe()`, and `mt6315_regulator_shutdown()`.

## Control Flow
SPMI probe creates a 16-bit-address regmap, allocates chip and mode data, chooses VBUCK1 mode-set masks based on `pdev->usid`, sets common one-bit masks for remaining bucks, then registers VBUCK1 through VBUCK4. Mode get checks force-PWM bits first, then low-power bits. Mode set writes force-PWM, clears force-PWM or low-power when returning normal, and sleeps briefly after leaving low-power. Shutdown unlocks protected TMA registers, enables a power-off sequence bit, then relocks.

## State And Persistence
Driver state includes the regmap in `struct mt6315_chip` and per-device mode masks in `mt_regulator_init_data`. Hardware registers persist voltage, enable, mode, and shutdown sequence configuration.

## Dependencies And Integration Points
Depends on SPMI, regmap, regulator core, OF match `mediatek,mt6315-regulator`, and public MT6315 regulator register/ID header. It integrates as an SPMI child device rather than an MFD platform subdevice.

## Risks And Test Signals
Risks include USID-specific mode masks, mode transition timing, shutdown protected-key sequence, lack of chip ID validation in this file, and global four-buck assumptions. Test by probing each USID role, changing all buck voltages, toggling FAST/NORMAL/IDLE modes, reading debug status registers, and validating shutdown sequence writes on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6315-regulator.c -->
