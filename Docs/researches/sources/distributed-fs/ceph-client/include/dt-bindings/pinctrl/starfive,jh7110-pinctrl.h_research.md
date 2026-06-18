# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/starfive,jh7110-pinctrl.h

Purpose: `starfive,jh7110-pinctrl.h` is a Devicetree binding header for a pin controller. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 120 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PAD_GMAC1 (14),
PAD_GMAC0 (14), PAD_SD0 (11), PAD_QSPI (6), GPOUT (2), GPOEN (2), PAD_GPIO0 (1), PAD_GPIO1 (1),
PAD_GPIO2 (1), PAD_GPIO3 (1). Representative constants are `PAD_GPIO0`, `PAD_GPIO1`, `PAD_GPIO2`,
`PAD_GPIO3`, `PAD_GPIO4`, `PAD_GPIO5`, `PAD_GPIO6`, `PAD_GPIO7`, `...`, `PAD_GMAC0_TXD3`,
`PAD_GMAC0_TXEN`, `PAD_GMAC0_TXC`, `GPOUT_LOW`, `GPOUT_HIGH`, `GPOEN_ENABLE`, `GPOEN_DISABLE`,
`GPI_NONE`. Function-like helpers are none. Value shape: literal numeric range 0..255 across 120
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_STARFIVE_JH7110_H__`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `sys_iomux pins`, `aon_iomux pins`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 137 lines long. Notable source comments include `sys_iomux pins`, `aon_iomux pins`.
Example value clusters are PAD_GMAC1: `PAD_GMAC1_MDC=75`, `PAD_GMAC1_MDIO=76`, `PAD_GMAC1_RXD0=77`,
`PAD_GMAC1_RXD1=78`; PAD_GMAC0: `PAD_GMAC0_MDC=6`, `PAD_GMAC0_MDIO=7`, `PAD_GMAC0_RXD0=8`,
`PAD_GMAC0_RXD1=9`; PAD_SD0: `PAD_SD0_CLK=64`, `PAD_SD0_CMD=65`, `PAD_SD0_DATA0=66`,
`PAD_SD0_DATA1=67`; PAD_QSPI: `PAD_QSPI_SCLK=89`, `PAD_QSPI_CS0=90`, `PAD_QSPI_DATA0=91`,
`PAD_QSPI_DATA1=92`; GPOUT: `GPOUT_LOW=0`, `GPOUT_HIGH=1`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PAD_GPIO0`, `PAD_GPIO1`, `PAD_GPIO2`, `PAD_GPIO3`, `PAD_GPIO4`, `PAD_GPIO5`,
`PAD_GPIO6`, `PAD_GPIO7`. Test signals include dt_binding_check coverage, DTS compile coverage for
each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using representative mux
groups.
