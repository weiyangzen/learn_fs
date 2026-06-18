# sources/distributed-fs/ceph-client/drivers/regulator/qcom_usb_vbus-regulator.c

## Purpose
This small Qualcomm PMIC driver exposes the USB VBUS OTG output as a regulator. It supports software enable/disable and selectable current limits for PM8150B-style VBUS regulator blocks.

## Important APIs, Types, and Functions
The driver defines the OTG command, current-limit, and configuration registers relative to a DT-provided base address. `curr_table` exposes 500 mA through 3 A current limits. `qcom_usb_vbus_reg_ops` uses generic regmap regulator helpers for enable, disable, status, and current-limit operations. `qcom_usb_vbus_regulator_probe()` reads resources, patches `qcom_usb_vbus_rdesc`, registers the regulator, and disables hardware-controlled VBUS enable logic.

## Control Flow
Probe reads the `reg` property as the register base, obtains the parent regmap, retrieves regulator init data, fills `enable_reg`, `enable_mask`, `csel_reg`, and `csel_mask` in the static descriptor, registers the regulator, then clears `OTG_EN_SRC_CFG` so software controls VBUS enable. Runtime control is delegated to regulator core regmap helpers.

## State and Persistence
There is no private per-device state. The static descriptor is updated at probe time with register addresses, and PMIC registers store enable/current-limit state. The final `regmap_update_bits()` changes hardware behavior until reset or later reconfiguration.

## Dependencies and Integration Points
The file depends on a parent PMIC regmap, a DT node compatible with `qcom,pm8150b-vbus-reg`, a valid `reg` base, and regulator constraints from OF. It integrates with USB/OTG consumers through a standard `usb_vbus` regulator name and current-limit operations.

## Risks and Test Signals
Risk areas include the mutable static descriptor if multiple instances ever probe, ignoring the return value when disabling hardware VBUS enable logic, current selector/table mismatch, and missing parent regmap. Test signals include probe failure for missing `reg`/regmap, regulator enable bit transitions, current-limit selector programming, and verifying `OTG_EN_SRC_CFG` is cleared after probe.
