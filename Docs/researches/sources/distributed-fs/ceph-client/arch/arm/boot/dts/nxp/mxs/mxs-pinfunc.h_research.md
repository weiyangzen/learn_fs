# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/mxs-pinfunc.h

Purpose: this small shared binding header defines electrical configuration constants for MXS pinctrl nodes.

Important API surface: it exports eight macros: `MXS_DRIVE_4mA`, `MXS_DRIVE_8mA`, `MXS_DRIVE_12mA`, `MXS_DRIVE_16mA`, `MXS_VOLTAGE_LOW`, `MXS_VOLTAGE_HIGH`, `MXS_PULL_DISABLE`, and `MXS_PULL_ENABLE`. These map directly to `fsl,drive-strength`, `fsl,voltage`, and `fsl,pull-up` property values.

Control flow: none. DTS files include this header for symbolic constants, and dtc emits the numeric property values.

State and persistence: no state is held. Numeric values persist in DTBs as pin electrical settings that the MXS pinctrl driver applies at boot.

Dependencies and integration: included by `imx23-pinfunc.h`, `imx28-pinfunc.h`, and board DTS/DTSI files using MXS pinctrl properties.

Risks and test signals: changing numeric values would alter drive strength, voltage selection, or pull-up behavior across many boards. Test with `make dtbs`, schema checks for MXS pinctrl properties, and hardware validation for buses sensitive to drive/pull settings.
