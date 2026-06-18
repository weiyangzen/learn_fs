# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hs.c

Purpose: Implements a Qualcomm ULPI high-speed USB PHY driver with regulator/clock sequencing, optional vendor init sequence, optional POR reset, and VBUS control through extcon or ULPI interrupts.

Important APIs/types/functions: `struct qcom_usb_hs_phy` holds the ULPI device, generic PHY, clocks, regulators, reset, init sequence, extcon device, and notifier. PHY ops are `qcom_usb_hs_phy_power_on()`, `_power_off()`, and `_set_mode()`. `qcom_usb_hs_phy_vbus_notifier()` mirrors extcon VBUS state into ULPI MISC_A.

Control flow: Probe parses `qcom,init-seq` as address/value pairs, gets `ref` and `sleep` clocks, `v1p8` and `v3p3` regulators, optional `por` reset, optional extcon, creates a PHY, and registers the provider. Power-on enables clocks, sets regulator loads/voltages, enables regulators, writes vendor ULPI init entries, pulses reset, initializes VBUS state, and registers the extcon notifier. `set_mode()` either enables ULPI ID/session-valid interrupts or uses VBUSVLDEXTSEL depending on extcon availability.

State and persistence: Runtime state is mostly resource handles and notifier registration. ULPI vendor init, OTG comparator disable, VBUS valid selection/value, and interrupt masks persist in the PHY until power-off or reset.

Dependencies and integration points: Depends on the ULPI bus, generic PHY, clocks, regulators, reset, extcon, notifier API, and OF properties. USB controller mode changes drive `set_mode()`.

Risks: The init sequence is DT-supplied raw ULPI writes with little validation. Extcon notifier registration happens at power-on and must be balanced at power-off. Regulator load/voltage settings influence signal stability and board power.

Test signals: Probe the ULPI compatible, verify init-seq writes, host/device/OTG mode transitions with and without extcon, VBUS notifier behavior, power-cycle under traffic, and regulator/clock cleanup on injected ULPI write failures.
