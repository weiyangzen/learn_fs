# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-snps-femto-v2.c

Purpose: Provides a Qualcomm Synopsys femto USB high-speed PHY v2 driver with clock/reset/regulator control, UTMI register programming, runtime suspend hooks, and optional DT-driven electrical tuning.

Important APIs/types/functions: Key structs are `override_param`, `override_param_map`, `phy_override_seq`, and `struct qcom_snps_hsphy`. PHY ops are `qcom_snps_hsphy_init()`, `qcom_snps_hsphy_exit()`, and `qcom_snps_hsphy_set_mode()`. Tuning helpers include `qcom_snps_hsphy_read_override_param_seq()` and `qcom_snps_hsphy_override_param_update_val()`.

Control flow: Probe maps MMIO, initializes optional `cfg_ahb` and required `ref` clocks, gets reset and supplies, enables but forbids runtime PM, creates the PHY, stores driver data, reads optional per-compatible tuning properties, and registers the provider. Init enables supplies and clocks, asserts/deasserts reset, enables UTMI common-control override, pulses POR, programs FSEL/refclk/VBUS override and any collected tuning sequence, bypasses the regulator, takes the PHY out of suspend/SIDDQ/POR, and clears overrides. Runtime suspend toggles auto-resume for host mode.

State and persistence: Driver state tracks `phy_initialized`, current mode, and a nine-entry tuning sequence. Hardware state includes override registers, suspend controls, VBUS-valid forcing, SIDDQ, POR, and regulator bypass until exit/reset.

Dependencies and integration points: Uses generic PHY, clocks, reset, regulators, runtime PM, OF match data, and DT properties such as `qcom,hs-disconnect-bp` or amplitude/impedance tuning keys. It integrates with USB host/device controllers through the generic PHY framework.

Risks: Tuning lookup falls back to the last table entry when a DT value is not matched, so bad DT values can still program hardware. Runtime PM is forbidden by default, so tests must explicitly allow it. Init sequencing is timing-sensitive and has no final PLL-ready poll.

Test signals: Probe all compatibles, check regulator/clock/reset balance, inspect override register writes for SC7280 tuning properties, run host/device HS enumeration, exercise runtime suspend in host mode, and validate behavior when optional `cfg_ahb` or tuning properties are absent.
