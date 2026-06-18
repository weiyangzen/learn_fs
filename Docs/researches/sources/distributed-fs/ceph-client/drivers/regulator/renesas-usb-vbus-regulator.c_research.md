# sources/distributed-fs/ceph-client/drivers/regulator/renesas-usb-vbus-regulator.c

Purpose: provides a single fixed 5 V USB VBUS regulator for Renesas RZ/G2L-style USB blocks. It is a tiny platform child driver that exposes the parent MFD/syscon regmap bit as a regulator named `vbus`.

Important APIs/types/functions: `rzg2l_usb_vbus_reg_ops` delegates enable, disable, and status to the regulator regmap helpers. `rzg2l_usb_vbus_rdesc` describes one fixed voltage with `enable_reg = 0`, `enable_mask = BIT(0)`, and inverted enable polarity. `rzg2l_usb_vbus_regulator_probe()` fetches the parent regmap, locates the `regulator-vbus` child node, and registers the regulator with `devm_regulator_register()`.

Control flow: platform probe obtains the parent regmap, takes an OF node reference for the child regulator node, registers the regulator, drops the OF reference, and returns probe status. No runtime callbacks are implemented beyond the generic regulator ops.

State and persistence: all mutable state is in the parent hardware register and regulator core state; this driver keeps no private data. Settings are not persisted by the driver beyond whatever the parent register retains.

Dependencies and integration: depends on a parent device that supplies a regmap and an OF child node named `regulator-vbus`. It integrates with the regulator framework and platform bus, using asynchronous preferred probing.

Risks and test signals: the inverted enable bit is the primary hardware-contract risk. Probe should be tested with missing regmap, missing child node, successful registration, and consumer enable/disable reads against the parent register bit.
