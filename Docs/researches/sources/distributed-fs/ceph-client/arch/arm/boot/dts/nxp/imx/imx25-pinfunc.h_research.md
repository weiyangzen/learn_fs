# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx25-pinfunc.h

Purpose: i.MX25 pin-function binding header. It names pad/function tuples used by i.MX25 DTS pinctrl groups and includes compatibility aliases for older SDHC naming.

Important APIs/types/functions: each `MX25_PAD_<pad>__<function>` macro expands to a five-cell tuple documented as `<mux_reg conf_reg input_reg mux_mode input_val>`. The file covers external memory and NAND, LCDC, FEC Ethernet, SIM, audio, CSPI, UART, SDHC/ESDHC, CSI, I2C, PWM, USB, keypad, GPIO, and boot/control pins. Compatibility macros map older `SDHC*` names to newer `ESDHC*` names near the end of the file. The include guard is `__DTS_IMX25_PINFUNC_H`.

Control flow: no runtime flow. The DTS preprocessor injects the five numeric cells into pinctrl properties, and the i.MX pinctrl driver writes mux, pad configuration, and input-select registers.

State and persistence: no mutable state. DTBs persist selected pin setup and Linux pinctrl owns runtime register state.

Dependencies and integration: integrated with i.MX25 board DTS files and the i.MX pinctrl binding. It depends on driver semantics for mux register offsets, config register offsets, input select offsets, mux modes, and daisy-chain input values.

Risks: wrong `input_reg` or `input_val` can break receive paths while mux and pad settings look correct. Compatibility aliases can hide older DTS naming, so maintainers should avoid adding new users of aliases. Test with `make ARCH=arm dtbs`, binding checks, targeted board boot, and peripheral validation for FEC, SDHC, UART, SPI, LCD, and CSI paths changed by a patch.
