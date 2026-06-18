# sources/distributed-fs/ceph-client/include/dt-bindings/reset/k210-rst.h

Purpose: `k210-rst.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 28 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are K210 (28). Representative constants are
`K210_RST_ROM`, `K210_RST_DMA`, `K210_RST_AI`, `K210_RST_DVP`, `K210_RST_FFT`, `K210_RST_GPIO`,
`K210_RST_SPI0`, `K210_RST_SPI1`, `...`, `K210_RST_FPIOA`, `K210_RST_TIMER0`, `K210_RST_TIMER1`,
`K210_RST_TIMER2`, `K210_RST_WDT0`, `K210_RST_WDT1`, `K210_RST_SHA`, `K210_RST_RTC`. Function-like
helpers are none. Value shape: literal numeric range 0..29 across 28 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by `RESET_K210_SYSCTL_H`;
after preprocessing, DTS C-preprocessor users and C drivers see only the constants and any packing
helpers. Comment-delimited groups or observed macro clusters are `K210 group`, which is the intended
lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 42 lines long. Notable source comments include `Kendryte K210 SoC system controller
K210_SYSCTL_SOFT_RESET register bits. Taken from Kendryte SDK (kendryte-standalone-sdk).`,
`RESET_K210_SYSCTL_H`. Example value clusters are K210: `K210_RST_ROM=0`, `K210_RST_DMA=1`,
`K210_RST_AI=2`, `K210_RST_DVP=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `K210_RST_ROM`,
`K210_RST_DMA`, `K210_RST_AI`, `K210_RST_DVP`, `K210_RST_FFT`, `K210_RST_GPIO`, `K210_RST_SPI0`,
`K210_RST_SPI1`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
