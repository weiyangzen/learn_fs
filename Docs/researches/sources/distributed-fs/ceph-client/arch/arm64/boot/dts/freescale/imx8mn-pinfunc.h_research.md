<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mn-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mn-pinfunc.h

### Purpose
This header defines i.MX8M Nano IOMUX function tuples for DTS pinctrl states.

### Important APIs, Types, And Functions
It exports 632 macros under `__DTS_IMX8MN_PINFUNC_H`, using the same five-field tuple contract `<mux_reg conf_reg input_reg mux_mode input_val>`. Macro groups cover boot mode pins, GPIO1, ENET, NAND, SD1/SD2, SAI, ECSPI, UART, I2C, PWM, GPT, USB, and clock/root functions.

### Control Flow
The header participates only in DTS preprocessing. The i.MX pinctrl driver consumes expanded tuples and applies mux, pad configuration, and select-input settings at runtime.

### State, Persistence, And Dependencies
There is no mutable state. Numeric offsets and input values must match the i.MX8MN IOMUXC hardware manual, binding, and driver.

### Integration Points
i.MX8MN board DTS files include this header for pin groups used by storage, Ethernet, audio, serial, SPI, I2C, GPIO, USB, and low-power states. The Freescale Makefile selects many i.MX8MN boards and overlays that depend on these constants.

### Risks
The Nano and Mini headers look similar but are not identical; copying `MX8MM_*` tuples into `MX8MN_*` contexts can misroute signals. Select-input registers are especially error-prone because some alternate functions share mux modes but differ by input value.

### Test Signals
Build i.MX8MN DTBs, run dt-schema validation, and test storage boot, Ethernet, UART/I2C/SPI, audio, USB, and suspend/resume. Peripheral probe failures and pinctrl debugfs state are strong diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mn-pinfunc.h -->
