# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-ss.c

Purpose: Implements an older Qualcomm SuperSpeed USB PHY driver for `qcom,usb-ss-28nm-phy`, managing regulators, clocks, reset, and basic lane/reference power bits.

Important APIs/types/functions: `struct ssphy_priv` stores MMIO, device, optional reset controls, two regulators, three clocks, and current mode. PHY ops are `qcom_ssphy_power_on()` and `_power_off()`. Resource helpers initialize clock, regulator, and reset arrays.

Control flow: Probe maps MMIO, gets `ref`, `ahb`, and `pipe` clocks, optional `com` reset and required `phy` reset when `com` exists, gets `vdd` and `vdda1p8` supplies, creates the PHY, and registers a provider. Power-on enables supplies and clocks, performs either register-based reset or reset-controller toggles, selects PCS clock, powers lane0, enables reference PHY, and clears test power-down. Power-off reverses lane/reference bits, asserts test power-down, and disables clocks and supplies.

State and persistence: State is resource handles plus the hardware control bits in `PHY_CTRL0/1/2/4`. No runtime PM or init-count state is kept.

Dependencies and integration points: Depends on generic PHY, platform MMIO, clock bulk APIs, reset controllers, regulators, and OF simple PHY translation. USB3 controllers consume this PHY.

Risks: Reset behavior changes depending on whether a reset controller exists, so DT binding differences affect the hardware sequence. There is no PHY-ready poll after power-on. The `mode` field is initialized but unused, limiting suspend/wake specialization.

Test signals: Probe with and without external reset controls, verify regulator and clock balance, USB3 enumeration, repeated power cycles, register dumps for lane/ref/test bits, and behavior when pipe clock or regulators defer.
