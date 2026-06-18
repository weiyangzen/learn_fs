<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-hsic.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-hsic.c

Purpose: Implements the minimal Marvell MMP3 HSIC PHY provider. It enables the HSIC block and bypasses its PLL through one control register.

Important APIs and types: `struct mmp3_hsic_data` stores the MMIO base. `mmp3_hsic_phy_init()` is the sole PHY operation and sets `HSIC_ENABLE` and `PLL_BYPASS` in `HSIC_CTRL`.

Control flow: Probe allocates driver data, maps the MMIO resource, creates one generic PHY, associates drvdata, and registers `of_phy_simple_xlate`. Consumer `phy_init()` reads `HSIC_CTRL`, ORs in enable and PLL bypass bits, and writes it back.

State and persistence: There is no software state beyond the mapped base. Hardware state remains enabled after init; no exit or power-off callback clears the bits.

Dependencies and integration points: Uses the generic PHY framework and the `marvell,mmp3-hsic-phy` compatible. It is expected to be driven by the MMP3 USB/HSIC controller through a PHY phandle.

Risks: No clock, reset, calibration, or polling path exists, so it assumes the surrounding SoC code has prepared clocks and power domains. Lack of a disable callback may matter for suspend or module unload if the controller expects full shutdown.

Test signals: DT probe, successful `phy_init()` from the HSIC controller, HSIC device attach, suspend/resume behavior, and readback that `HSIC_ENABLE` and `PLL_BYPASS` are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-hsic.c -->
