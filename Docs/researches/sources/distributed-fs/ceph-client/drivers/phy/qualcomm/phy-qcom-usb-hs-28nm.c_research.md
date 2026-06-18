# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs-28nm.c

Purpose: Provides the Qualcomm 28 nm Synopsys/femto high-speed USB PHY driver for `qcom,usb-hs-28nm-femtophy`, handling power, retention, POR reset, high-voltage DP/DM wake interrupts, and optional init sequences.

Important APIs/types/functions: Main types are `struct hsphy_init_seq`, `struct hsphy_data`, and `struct hsphy_priv`. PHY ops are `qcom_snps_hsphy_init()`, `_exit()`, `_power_on()`, `_power_off()`, and `_set_mode()`. Helpers manage reset, POR reset, retention, HV interrupt masks, and init-sequence writes.

Control flow: Probe maps MMIO, gets `ref`, `ahb`, and `sleep` clocks, gets `phy` and `por` resets, gets `vdd`, `vdda1p8`, and `vdda3p3` supplies, creates/registers a PHY, and sets 1.8 V/3.3 V regulator loads. Init enables clocks, pulses the PHY reset, writes match-data init sequence entries, and performs POR reset with SIDDQ cleared. Power-on enables regulators, disables wake interrupts, and exits retention. Power-off enters retention, enables DP/DM wake interrupts based on current mode, and disables regulators.

State and persistence: State includes current `phy_mode`, resource handles, and optional init data. Retention and interrupt-mask state persists in PHY registers across low-power periods; regulator load votes persist until driver removal or error cleanup.

Dependencies and integration points: Uses generic PHY, platform MMIO, bulk clocks, resets, regulators, OF match data, and USB controller `set_mode()` calls.

Risks: Wake interrupt polarity depends on the last mode reported by the consumer. Probe sets regulator loads but remove-time load cleanup is devm-only for regulators, not explicit for successful probe. Register programming is byte-wide and timing-sensitive around reset/POR.

Test signals: Probe with the femtophy compatible, verify regulator load votes and clock/reset sequencing, enumerate HS/FS/LS devices, suspend with connected and disconnected states, confirm DP/DM wake masks, and test init-sequence register delays.
