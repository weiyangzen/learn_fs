# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-ap806.c

Purpose: this is the Armada AP806 pinctrl table driver. It exposes the application processor's 20 MPP pins to the MVEBU pinctrl core, covering GPIO plus SDIO, SPI0, I2C0, UART0, and UART1 functions.

Important APIs, types, and functions: `armada_ap806_mpp_modes[]` is the complete pin/function table. `armada_ap806_mpp_controls[]` defines pins 0-19 as an unnamed `mvebu_regmap_mpp_ctrl` range. `armada_ap806_mpp_gpio_ranges[]` maps all 20 pins as GPIO-capable. `armada_ap806_pinctrl_probe()` validates that the pinctrl node has a parent syscon device, populates `armada_ap806_pinctrl_info`, and invokes `mvebu_pinctrl_simple_regmap_probe(pdev, parent, 0)`.

Control flow: after OF match on `marvell,ap806-pinctrl`, probe expects the parent node to provide the syscon regmap holding the MPP registers. The shared regmap helper creates one control-data entry per control with offset zero, then the common MVEBU core builds groups, functions, DT maps, pinmux operations, pinconf operations, and GPIO ranges. All runtime get/set operations are regmap reads or masked writes of 4-bit MPP fields.

State and persistence behavior: software state is the static SoC info plus device-managed regmap control data. Hardware mux values persist in the parent syscon registers. There are no variants, no explicit locking in this file, and no suspend/resume handling.

Dependencies and integration points: dependencies are the parent syscon/MFD device, MVEBU core, OF platform matching, and standard pinctrl clients. Integration is through DTS `marvell,function` and `marvell,pins`; the exposed names include a likely typo-like subname `i2c0` `"sdk"` for MPP5, which is part of the ABI once consumed by debug output or documentation.

Risks and test signals: probe fails with `-ENODEV` if the DT hierarchy omits the parent syscon. Because all pins share offset zero, any future AP806 register-layout change would need a different offset or control split. Test signals include successful regmap lookup, SDIO 8-bit and reset/power pins, SPI0 chip selects, UART0/1 muxing, GPIO request on all 20 pins, and DT rejection for unsupported functions on GPIO-only pins 13-18.
