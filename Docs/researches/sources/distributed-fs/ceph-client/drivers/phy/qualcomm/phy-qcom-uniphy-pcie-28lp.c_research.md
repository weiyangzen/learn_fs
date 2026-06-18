# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-uniphy-pcie-28lp.c

Purpose: Implements Qualcomm UNIPHY PCIe 28LP PHY support for IPQ5018 and IPQ5332 families, including per-lane initialization and fixed pipe clock provider registration.

Important APIs/types/functions: `struct qcom_uniphy_pcie_data` describes lane offset, PHY generation, init sequence, and pipe clock rate. `struct qcom_uniphy_pcie` holds resources and lane count. Generic PHY ops are `qcom_uniphy_pcie_power_on()` and `_power_off()`, with `qcom_uniphy_pcie_init()` applying per-lane register tables.

Control flow: Probe reads match data, requires `num-lanes`, maps MMIO, gets all clocks and reset arrays, creates one PHY, registers a fixed-rate pipe clock named from the PHY id, and registers an OF provider. Power-on asserts/deasserts resets with required delays, enables all clocks, waits again, and writes the configured init sequence to each lane base separated by `lane_offset`. Power-off disables clocks and asserts resets.

State and persistence: Runtime state is resource handles, lane count, SoC data, and MMIO base. Hardware CDR/SSCG/PCS or Gen3 PHY configuration persists while powered.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clock bulk APIs, reset arrays, clock-provider APIs, OF match data, and `num-lanes` DT. PCIe host controller drivers consume the PHY and pipe clock.

Risks: `num-lanes` is trusted and not bounded against the mapped resource size. The code registers one pipe clock provider, so multi-PHY DT clock topology must match expectations. A stale macro `phy_to_dw_phy` references unrelated types and is unused but confusing. Init tables are minimal and SoC-specific.

Test signals: Probe IPQ5018 and IPQ5332 compatibles, verify pipe clock rate is 125 MHz or 250 MHz as configured, power-cycle PCIe links, test one-lane and multi-lane DTs, confirm reset/clock ordering, and inspect lane-offset register writes.
