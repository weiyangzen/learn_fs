# sources/distributed-fs/ceph-client/include/dt-bindings/reset/aspeed,ast2700-scu.h

Purpose: `aspeed,ast2700-scu.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 109 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are SCU1 (64), SCU0 (45). Representative constants are
`SCU0_RESET_SDRAM`, `SCU0_RESET_DDRPHY`, `SCU0_RESET_RSA`, `SCU0_RESET_SHA3`, `SCU0_RESET_HACE`,
`SCU0_RESET_SOC`, `SCU0_RESET_VIDEO`, `SCU0_RESET_2D`, `...`, `SCU1_RESET_UHCI`,
`SCU1_RESET_PORTC_USB2UART`, `SCU1_RESET_PORTC_VHUB_EHCI`, `SCU1_RESET_PORTD_USB2UART`,
`SCU1_RESET_PORTD_VHUB_EHCI`, `SCU1_RESET_H2X`, `SCU1_RESET_I3CDMA`, `SCU1_RESET_PCIE2RST`.
Function-like helpers are none. Value shape: literal numeric range 0..63 across 109 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_MACH_ASPEED_AST2700_RESET_H_`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`SOC0`, `SOC1`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 124 lines long. Notable source comments include `Device Tree binding constants for
AST2700 reset controller.`, `SOC0`, `SOC1`, `_MACH_ASPEED_AST2700_RESET_H_`. Example value clusters
are SCU1: `SCU1_RESET_LPC0=0`, `SCU1_RESET_LPC1=1`, `SCU1_RESET_MII=2`, `SCU1_RESET_PECI=3`; SCU0:
`SCU0_RESET_SDRAM=0`, `SCU0_RESET_DDRPHY=1`, `SCU0_RESET_RSA=2`, `SCU0_RESET_SHA3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `SCU0_RESET_SDRAM`,
`SCU0_RESET_DDRPHY`, `SCU0_RESET_RSA`, `SCU0_RESET_SHA3`, `SCU0_RESET_HACE`, `SCU0_RESET_SOC`,
`SCU0_RESET_VIDEO`, `SCU0_RESET_2D`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
