# sources/distributed-fs/ceph-client/include/dt-bindings/reset/cortina,gemini-reset.h

Purpose: `cortina,gemini-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 31 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are GEMINI (31). Representative constants are
`GEMINI_RESET_DRAM`, `GEMINI_RESET_FLASH`, `GEMINI_RESET_IDE`, `GEMINI_RESET_RAID`,
`GEMINI_RESET_SECURITY`, `GEMINI_RESET_GMAC0`, `GEMINI_RESET_GMAC1`, `GEMINI_RESET_PCI`, `...`,
`GEMINI_RESET_WDOG`, `GEMINI_RESET_EXTERN`, `GEMINI_RESET_CIR`, `GEMINI_RESET_SATA0`,
`GEMINI_RESET_SATA1`, `GEMINI_RESET_TVC`, `GEMINI_RESET_CPU1`, `GEMINI_RESET_GLOBAL`. Function-like
helpers are none. Value shape: literal numeric range 0..31 across 31 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CORTINA_GEMINI_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `GEMINI group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 37 lines long. Notable source comments include none. Example value clusters are GEMINI:
`GEMINI_RESET_DRAM=0`, `GEMINI_RESET_FLASH=1`, `GEMINI_RESET_IDE=2`, `GEMINI_RESET_RAID=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `GEMINI_RESET_DRAM`,
`GEMINI_RESET_FLASH`, `GEMINI_RESET_IDE`, `GEMINI_RESET_RAID`, `GEMINI_RESET_SECURITY`,
`GEMINI_RESET_GMAC0`, `GEMINI_RESET_GMAC1`, `GEMINI_RESET_PCI`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
