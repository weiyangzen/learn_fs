# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-2p5ge.c

## Purpose
`mtk-2p5ge.c` implements the MediaTek MT7988 built-in 2.5GbE PHY driver. It loads required PHY MCU firmware into a fixed PMB memory window, configures internal PHY tuning, handles Clause 45 autonegotiation with Clause 22 1000BASE-T supplements, reports link speed through vendor auxiliary status, exposes pause-based rate matching, and provides LED control through shared MediaTek PHY helper functions.

## Important APIs, Types, And Functions
- `mt798x_2p5ge_phy_load_fw()` maps PMB and MCU CSR address ranges, validates and copies `mediatek/mt7988/i2p5ge-phy-pmb.bin`, stalls/restarts the PHY MCU, and resets the PHY.
- `mt798x_2p5ge_phy_probe()` patches missing C45 MMD presence bits, loads firmware, programs default LED behavior, switches LED pinctrl, allocates `struct mtk_socphy_priv`, and initializes LED state.
- `mt798x_2p5ge_phy_config_init()` requires `PHY_INTERFACE_MODE_INTERNAL`, tunes LPI threshold, enables a token-ring next-page setting, and enables hardware downshift.
- `mt798x_2p5ge_phy_config_aneg()` combines `genphy_c45_an_config_aneg()` with Clause 22 `MII_CTRL1000` advertisement programming.
- `mt798x_2p5ge_phy_get_features()` reads C45 PMA abilities and removes unsupported 100baseT half-duplex.
- `mt798x_2p5ge_phy_read_status()` uses C22 link update, C45 LPA plus C22 1G LPA, and vendor auxiliary speed bits.
- LED callbacks delegate blink, brightness, and hardware control to shared `mtk_phy_*` helpers.

## Control Flow And State Behavior
Probe is firmware-first: it ensures the hardware's incomplete MMD discovery is corrected, loads firmware via direct firmware request, initializes LED registers, selects LED pinmux, allocates private LED/helper state, and registers LED state with the shared library. Firmware loading powers the PHY down, writes host commands to stall the MCU, copies the exact-size firmware image to PMB memory, toggles `MD32_EN`, resets the PHY, waits for stabilization, and logs firmware date/version.

At config time the PHY must be connected through an internal interface. Autonegotiation is mostly Clause 45 but 1000BASE-T advertisement and partner advertisement are handled through Clause 22 because this hardware design exposes that mode there. Link status avoids generic C45 link status because the C45 bit can assert before AN is actually complete; it uses `genphy_update_link()` and reads speed from `PHY_AUX_CTRL_STATUS`. Runtime state is limited to devres mappings during firmware load, firmware-programmed hardware, and `phydev->priv`.

## Dependencies And Integration Points
The driver depends on firmware loading, fixed SoC MMIO mappings via `ioremap()`, phylib C22/C45 helpers, pinctrl state `i2p5gbe-led`, shared MediaTek helper functions from `mtk-phy-lib`, and `struct mtk_socphy_priv` from `mtk.h`. It integrates with Kbuild through `MODULE_FIRMWARE()` and the `MEDIATEK_2P5GE_PHY` symbol.

## Risks And Edge Cases
- Firmware size must match exactly; wrong firmware fails probe.
- Fixed physical MMIO addresses assume MT7988 SoC integration and are not discoverable resources.
- The firmware copy casts firmware bytes to `uint32_t *`, so alignment and endian expectations are hardware-specific.
- Missing LED pinctrl only logs an error; the PHY can still probe with nonfunctional LEDs.
- Ignored return values in some setup writes mean later failures may surface as link issues rather than probe errors.
- Link reporting depends on vendor auxiliary speed bits.

## Test Signals
Validate firmware present/missing/wrong-size cases, MCU restart and reset timing, internal-interface rejection for non-internal modes, C45 MMD presence patching, 10/100/1000/2500 link reporting, C22 1G advertisement and LPA handling, pause rate matching, LED0/LED1 defaults, LED triggers and brightness control, suspend/resume, and module firmware metadata.
