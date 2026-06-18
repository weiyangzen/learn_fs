<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-usb.c

Purpose: Supports the MMP3 USB2 PHY, including revision-specific PLL programming and explicit VCO/TX impedance calibration.

Important APIs and types: `struct mmp3_usb_phy` holds the PHY and register base. Register helpers `u2o_get()`, `u2o_set()`, and `u2o_clear()` wrap read-modify-write with readback. Main callbacks are `mmp3_usb_phy_init()` and `mmp3_usb_phy_calibrate()`.

Control flow: Probe maps registers, creates a PHY, and registers an OF provider. Init chooses A0 or B0 bit layouts using `cpu_is_mmp3_a0()` and `cpu_is_mmp3_b0()`, programs PLL feedback/reference dividers, PLL power/lock bypass/KVCO/ICP, TX impedance threshold, TX amplitude and VDD, slew rate, RX squelch threshold, analog power, and OTG power. Calibrate waits 200 us, starts VCO calibration, waits 400 us, pulses TX RCAL, waits again, then polls `USB2_PLL_READY_MASK_MMP3` for up to 100 ms.

State and persistence: The active programming persists in PHY registers until reset or power loss. No driver state records calibration result beyond returned errors.

Dependencies and integration points: Depends on MMP CPU revision helpers, generic PHY, platform MMIO, and `marvell,mmp3-usb-phy` DT binding. The USB controller invokes init/calibrate through generic PHY.

Risks: Unsupported silicon revisions fail init. The driver hardcodes analog values and depends on exact A0/B0 bit placements. Calibrate returns timeout but leaves earlier power and calibration bits as programmed.

Test signals: A0 and B0 probe coverage, `phy_init()` plus `phy_calibrate()`, timeout injection for PLL ready, USB enumeration after calibration, and register readback across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mmp3-usb.c -->
