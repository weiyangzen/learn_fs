<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-usb.c

Purpose: Provides a legacy Marvell PXA/MMP2 USB UTMI PHY driver with SoC-version-specific tuning for MMP2, PXA910, and PXA168.

Important APIs and types: `enum pxa_usb_phy_version` selects version behavior. `struct pxa_usb_phy` stores PHY, base, and version. Register helpers `u2o_get/set/clear/write()` provide relaxed MMIO with readback. PHY callbacks are `pxa_usb_phy_init()` and `pxa_usb_phy_exit()`.

Control flow: Probe selects version from OF match data, maps registers, creates a generic PHY, registers a provider, and creates legacy lookup aliases when no DT node exists. Init powers PLL and PHY, applies PXA910 extra reference bits if needed, programs PLL/TX/RX fields, writes a PXA168-specific IVREF workaround, pulses VCO calibration and TX RCAL with delays, polls `PLL_READY` up to 100 ms, and enables PXA168 reserve/OTG addon bits. Exit disables PXA168 OTG addon, clears buffer powerdown/clock/power bits, and powers down PLL/PHY.

State and persistence: Version is the only cached software state. Register programming persists until exit or reset. PLL-ready timeout only warns and init still returns success.

Dependencies and integration points: Uses generic PHY, platform MMIO, DT match data, optional legacy PHY lookup names for `mv-udc`, `pxa-u2oehci`, and `mv-otg`.

Risks: Timeout does not fail init. Hardcoded analog settings differ by board quirks only for PXA168 IVREF. Legacy lookup creation expands integration surface and can affect non-DT users. `dev_info()` in init/exit can be noisy.

Test signals: Probe each compatible, legacy non-DT lookup, USB host/device/OTG enumeration, PXA168 hub workaround validation, calibration timeout observation, and suspend/resume after exit/init cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-usb.c -->
