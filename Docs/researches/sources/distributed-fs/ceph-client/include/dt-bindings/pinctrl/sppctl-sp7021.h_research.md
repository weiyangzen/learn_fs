# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sppctl-sp7021.h

Purpose: `sppctl-sp7021.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 154 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are MUXF (122), GROP (32).
Representative constants are `MUXF_GPIO`, `MUXF_IOP`, `MUXF_L2SW_CLK_OUT`, `MUXF_L2SW_MAC_SMI_MDC`,
`MUXF_L2SW_LED_FLASH0`, `MUXF_L2SW_LED_FLASH1`, `MUXF_L2SW_LED_ON0`, `MUXF_L2SW_LED_ON1`, `...`,
`GROP_USB0_I2C`, `GROP_USB1_I2C`, `GROP_USB0_OTG`, `GROP_USB1_OTG`, `GROP_UPHY0_DEBUG`,
`GROP_UPHY1_DEBUG`, `GROP_UPHY0_EXT`, `GROP_PROBE_PORT`. Function-like helpers are none. Value
shape: literal numeric range 0..153 across 154 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_SPPCTL_SP7021_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `MUXF group`, `GROP group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are `dt-bindings/pinctrl/sppctl.h`. Integration points are pinctrl provider drivers,
board DTS files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 179 lines long. Notable source comments include `Sunplus SP7021 dt-bindings Pinctrl
header file`, `Please don't change the order of the following defines. They are based on order of
'hardware' control register defined in MOON2 ~ MOON3 registers.`, `Please don't change the order of
the following defines. They are based on order of items in array 'sppctl_list_funcs' in Sunplus
pinctrl driver.`. Example value clusters are MUXF: `MUXF_GPIO=0`, `MUXF_IOP=1`,
`MUXF_L2SW_CLK_OUT=2`, `MUXF_L2SW_MAC_SMI_MDC=3`; GROP: `GROP_SPI_FLASH=122`,
`GROP_SPI_FLASH_4BIT=123`, `GROP_SPI_NAND=124`, `GROP_CARD0_EMMC=125`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `MUXF_GPIO`, `MUXF_IOP`, `MUXF_L2SW_CLK_OUT`, `MUXF_L2SW_MAC_SMI_MDC`,
`MUXF_L2SW_LED_FLASH0`, `MUXF_L2SW_LED_FLASH1`, `MUXF_L2SW_LED_ON0`, `MUXF_L2SW_LED_ON1`. Test
signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs,
GPIO loopback, and peripheral bring-up using representative mux groups.
