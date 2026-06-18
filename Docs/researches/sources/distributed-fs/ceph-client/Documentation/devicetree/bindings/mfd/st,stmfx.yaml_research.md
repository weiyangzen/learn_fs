# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmfx.yaml

Purpose: Schema for the ST STMFX I2C multi-function expander, covering GPIO expansion, optional IDD/touchscreen pin availability, open-drain behavior, supply, interrupt line, and pinctrl child configuration.

Important schema surface and control flow: top-level `compatible = "st,stmfx-0300"`, I2C `reg` of 0x42 or 0x43, and `interrupts` are required. Optional properties include `drive-open-drain` and `vdd-supply`. The `pinctrl` child requires `compatible = "st,stmfx-0300-pinctrl"`, GPIO and interrupt controller cells, `gpio-ranges`, and allows `*-pins` groups using pinmux-node semantics plus bias, drive, and output configuration properties.

State, dependencies, and integration: DT state configures the STMFX MFD and its pinctrl/GPIO/IRQ providers, including which pins are available when touchscreen or IDD functions consume analog GPIOs. Dependencies include I2C, interrupt, regulator supply, GPIO, and pinctrl bindings. Risks include incorrect `gpio-ranges` when some analog pins are unavailable, using an unsupported I2C address, and missing interrupt-controller cells in the pinctrl child. Test signals are schema validation, pin group validation, GPIO range sanity, and runtime GPIO/IRQ/pinctrl provider registration.
