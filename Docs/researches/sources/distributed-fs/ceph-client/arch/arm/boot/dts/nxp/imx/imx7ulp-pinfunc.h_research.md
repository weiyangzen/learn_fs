# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7ulp-pinfunc.h

## Purpose
This header is the Devicetree pin-function catalog for the NXP/Freescale i.MX7ULP A7-domain IOMUXC1 controller. It defines `IMX7ULP_PAD_*__*` macros for pads PTC, PTD, PTE, and PTF. The macros are consumed by `fsl,imx7ulp-iomuxc1` pinctrl groups in `imx7ulp.dtsi` and board DTS files.

Unlike i.MX6UL and i.MX7D, i.MX7ULP uses a shared mux/config register layout. Each macro expands to `<mux_conf_reg input_reg mux_mode input_val>`, and the board DTS appends the fifth `CONFIG` cell. The file contains 462 macros over 68 pads, covering FlexBus, FXIO1, VIU, trace, TPM, LPSPI, SDHC, USB, LPUART, LPI2C, and GPIO-style port functions.

## Important APIs, Types, and Functions
The public API is `IMX7ULP_PAD_PTC<n>__*`, `IMX7ULP_PAD_PTD<n>__*`, `IMX7ULP_PAD_PTE<n>__*`, and `IMX7ULP_PAD_PTF<n>__*`. Each macro contributes four cells to `fsl,pins`; the i.MX7ULP binding documents five cells after config is appended. This matches `pinctrl-imx.c` support for `SHARE_MUX_CONF_REG` and `FSL_PIN_SHARE_SIZE` (20 bytes per pin).

`mux_conf_reg` is the combined mux/config register offset, `input_reg` is the select-input offset or zero, `mux_mode` is an unshifted mode inserted into the driver-defined mux bitfield, and `input_val` is the daisy value. The i.MX7ULP driver uses mask `0xf00` and shift `8`. The file has 218 macros with nonzero input-select registers and modes through `0xc`.

## Control Flow
`imx7ulp.dtsi` includes this header and declares the IOMUXC1 controller. Board DTS files compile macros plus config into five-cell entries. `drivers/pinctrl/freescale/pinctrl-imx7ulp.c` matches `fsl,imx7ulp-iomuxc1` and sets `ZERO_OFFSET_VALID | SHARE_MUX_CONF_REG`. Generic parsing reads `mux_conf_reg`, uses it as both mux and config register, then reads `input_reg`, `mux_mode`, `input_val`, and config. State selection read-modify-writes only the mux bits, writes input-select registers when present, and uses the pinconf path for pad config. GPIO direction uses an i.MX7ULP hook to toggle OBE/IBE bits in the shared register.

## State and Persistence Behavior
The header stores no state. Compiled DTBs persist the tuple values. Runtime state lives in IOMUXC1 shared mux/config registers, input-select registers, and GPIO direction-related OBE/IBE bits. Because mux and configuration fields share a register, offset and mask correctness are especially important.

## Dependencies and Integration Points
It is included by `imx7ulp.dtsi`, consumed by board pinctrl groups under `fsl,imx7ulp-iomuxc1`, parsed by `pinctrl-imx.c` with `SHARE_MUX_CONF_REG`, specialized by `pinctrl-imx7ulp.c`, and described by `Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml`. Peripheral integration covers LPUART4-7, LPI2C4-7, LPSPI2-3, TPM, SDHC0/1, FXIO, FlexBus, VIU, trace, USB0/USB1, and GPIO ports PTC/PTD/PTE/PTF.

## Risks
The largest risk is using the wrong tuple width: these macros are four cells before config, not five. Combined mux/config registers make offset mistakes more damaging, and mux mode values are unshifted modes rather than full register images. GPIO direction depends on OBE/IBE bits in the same register, so pad config changes can interfere with direction behavior. Nonzero input select values are common; daisy errors can leave inputs dead while output muxing appears correct. The header covers only IOMUXC1 A7-domain pads.

## Test Signals
Build i.MX7ULP DTBs and run `dtbs_check` for `Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml`. Confirm five cells per full `fsl,pins` entry. Runtime tests should cover LPUART, LPI2C, LPSPI, SDHC, USB ID/OC/ULPI where wired, GPIO direction changes, and pinctrl debugfs group mappings. For edits, compare generated DTB cells and verify shared-register read-modify-write behavior.
