# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-apq8064-sata.c

This Qualcomm APQ8064 SATA PHY driver programs a UNIPHY/SATA SerDes register block through direct MMIO. `struct qcom_apq8064_sata_phy` keeps the MMIO base, always-enabled `cfg` clock, and device pointer.

Probe maps the register resource, creates a generic PHY, gets and enables the `cfg` clock, registers `of_phy_simple_xlate`, and disables the clock on remove. Init writes a fixed sequence: power down/up transitions, RX/TX impedance calibration setup, UNIPHY PLL reference, calibration, SDM, SSC, lock-detect registers, global PLL power-up, and polls PLL lock plus TX/RX calibration status with `readl_relaxed_poll_timeout()`. After calibration it writes functional-mode CDR, data, alignment, OOB, equalization, and drive controls. Exit powers down SATA PHY and PLL blocks.

State is MMIO register programming and the enabled config clock. Dependencies are clk, generic PHY, MMIO polling, and OF. Risks include fixed magic tuning values, 10 second timeout constant despite comment saying 1 second, no runtime PM, and limited recovery after calibration failure. Test signals are poll timeouts and SATA link bring-up.
