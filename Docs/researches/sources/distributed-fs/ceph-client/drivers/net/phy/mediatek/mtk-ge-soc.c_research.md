# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge-soc.c

## Purpose
`mtk-ge-soc.c` implements MediaTek/Airoha SoC gigabit PHY support for MT7981, MT7988, AN7581, and AN7583. The driver focuses on analog/DSP tuning, efuse and software calibration, LED control, shared MT7988 package state, and minimal interrupt handling through generic no-ack phylib helpers.

## Important APIs, Types, And Functions
- `struct mtk_socphy_shared` stores package-wide MT7988 boottrap polarity data and per-address `struct mtk_socphy_priv` records.
- Calibration helpers include `cal_cycle()`, `rext_*`, `tx_offset_*`, `tx_amp_*`, `tx_r50_*`, `tx_vcm_cal_sw()`, `cal_efuse()`, `cal_sw()`, `start_cal()`, and `mt798x_phy_calibration()`.
- Fine-tuning paths include `mt798x_phy_common_finetune()`, `mt7981_phy_finetune()`, `mt7988_phy_finetune()`, and `mt798x_phy_eee()`.
- Probe paths are `mt7981_phy_probe()`, `mt7988_phy_probe()`, `mt7988_phy_probe_shared()`, and `an7581_phy_probe()`.
- LED operations include `mt798x_phy_led_blink_set()`, `mt798x_phy_led_brightness_set()`, hardware-trigger get/set/is-supported helpers, MT7988 LED polarity boottrap handling, and `an7581_phy_led_polarity_set()`.
- `mtk_socphy_driver[]` maps exact PHY IDs to phylib callbacks.

## Control Flow And State Behavior
For MT7981/MT7988, probe allocates or joins private state, initializes shared LED state, and runs calibration. MT7988 joins a PHY package for addresses 0-3, reads a package-level GPIO boottrap register through a `mediatek,pio` phandle once, uses the captured bits to set LED0 polarity per PHY, applies LED pinctrl, disables TX power saving to satisfy compliance and support TX-VCM calibration, then calibrates. MT7981 uses per-device private state and calibration. Airoha AN7581/AN7583 probe mainly sets LED pinctrl and private state; AN7583 additionally clears `BMCR_PDOWN` in `config_init`.

`mt798x_phy_config_init()` applies chip-specific finetune tables, common token-ring/DSP tuning, EEE tuning, and calibration. Calibration reads an NVMEM cell named `phy-cal-data`, validates four nonzero words, applies efuse-backed REXT/TX offset/TX amplitude/TX R50 values, and runs software TX-VCM calibration on pair A. `tx_vcm_cal_sw()` performs a binary-search-like calibration over TX reserve settings using analog comparator cycles and restores calibration control bits before returning. State is stored in MDIO MMD registers, token-ring debug nodes, NVMEM-derived values, and package private memory.

## Dependencies And Integration Points
The driver depends on phylib, `PHY_PACKAGE`, NVMEM cell APIs, regmap/syscon, OF phandles, pinctrl, shared MediaTek helper functions, token-ring debug accessors, and generic PHY interrupt helpers. It integrates with board firmware through `phy-cal-data`, `mediatek,pio`, and `gbe-led` pinctrl, with LEDs through phylib LED hooks, and with Kconfig dependencies on Airoha/MediaTek platforms.

## Risks And Edge Cases
- Calibration quality depends on valid efuse data. Missing NVMEM is tolerated, but malformed or zero data returns errors.
- Many finetune constants are silicon-specific magic values; changing them requires hardware validation.
- MT7988 package sharing assumes MDIO addresses 0-3 and a valid `mediatek,pio` phandle.
- Calibration functions often perform several MDIO writes and may leave analog state altered if a lower-level helper silently fails.
- LED polarity depends on boottrap pins shared with LEDs; configuring pinctrl too early can cause bogus blinking or wrong polarity.
- `tx_vcm_cal_sw()` has narrow timing limits and reports low/high margin warnings that should be treated as signal-quality risks.

## Test Signals
Test exact PHY ID matching for all four devices, MT7988 package join/probe-once behavior, invalid address rejection, `mediatek,pio` missing/error paths, NVMEM defer/missing/invalid/valid cases, calibration success and timeout handling, MT7981 versus MT7988 finetune register writes, AN7583 power-down clearing, LED polarity modes, LED hardware triggers, no-ack interrupt path, suspend/resume, and link stability/EEE behavior after calibration.
