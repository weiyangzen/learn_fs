<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-sata.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-sata.c

Purpose: Provides a simple built-in SATA PHY driver for Marvell MVEBU SoCs. It toggles PLL/IVREF/TX/RX power bits and SATA interface shutdown around a controller clock.

Important APIs and types: `struct priv` stores an unnamed clock and MMIO base. PHY callbacks are `phy_mvebu_sata_power_on()` and `phy_mvebu_sata_power_off()`. Probe creates a single generic PHY and registers `of_phy_simple_xlate`.

Control flow: Power-on enables the clock, sets `MODE_2_FORCE_PU_TX`, `MODE_2_FORCE_PU_RX`, `MODE_2_PU_PLL`, and `MODE_2_PU_IVREF`, clears `CTRL_PHY_SHUTDOWN`, and disables the clock. Power-off enables the clock, clears the same mode bits, sets `CTRL_PHY_SHUTDOWN`, and disables the clock. Probe maps resources, gets the clock, creates/registers the PHY, and turns off possible bootloader state.

State and persistence: Software state is only the clock/base pointer. Hardware power state persists in `SATA_PHY_MODE_2` and `SATA_IF_CTRL`.

Dependencies and integration points: Uses generic PHY, platform MMIO, clock framework, and `marvell,mvebu-sata-phy`. It is built in via `builtin_platform_driver()` for early SATA availability.

Risks: `clk_prepare_enable()` return values are ignored. No PLL-ready polling exists, so link failures surface at the SATA controller. The probe comment contains a typo but behavior intentionally disables bootloader-enabled PHY state.

Test signals: Built-in probe ordering, SATA link after power-on, bootloader-on handoff, controller remove or suspend power-off, and register readback of shutdown and mode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-sata.c -->
