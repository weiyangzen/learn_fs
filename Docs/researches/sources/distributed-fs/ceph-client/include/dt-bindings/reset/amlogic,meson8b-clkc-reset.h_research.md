# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-clkc-reset.h

Purpose: `amlogic,meson8b-clkc-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 16 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CLKC (16). Representative constants are
`CLKC_RESET_L2_CACHE_SOFT_RESET`, `CLKC_RESET_AXI_64_TO_128_BRIDGE_A5_SOFT_RESET`,
`CLKC_RESET_SCU_SOFT_RESET`, `CLKC_RESET_CPU0_SOFT_RESET`, `CLKC_RESET_CPU1_SOFT_RESET`,
`CLKC_RESET_CPU2_SOFT_RESET`, `CLKC_RESET_CPU3_SOFT_RESET`, `CLKC_RESET_A5_GLOBAL_RESET`,
`CLKC_RESET_A5_AXI_SOFT_RESET`, `CLKC_RESET_A5_ABP_SOFT_RESET`,
`CLKC_RESET_AXI_64_TO_128_BRIDGE_MMC_SOFT_RESET`, `CLKC_RESET_VID_CLK_CNTL_SOFT_RESET`,
`CLKC_RESET_VID_DIVIDER_CNTL_SOFT_RESET_POST`, `CLKC_RESET_VID_DIVIDER_CNTL_SOFT_RESET_PRE`,
`CLKC_RESET_VID_DIVIDER_CNTL_RESET_N_POST`, `CLKC_RESET_VID_DIVIDER_CNTL_RESET_N_PRE`. Function-like
helpers are none. Value shape: literal numeric range 0..15 across 16 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON8B_CLKC_RESET_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `CLKC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 27 lines long. Notable source comments include
`_DT_BINDINGS_AMLOGIC_MESON8B_CLKC_RESET_H`. Example value clusters are CLKC:
`CLKC_RESET_L2_CACHE_SOFT_RESET=0`, `CLKC_RESET_AXI_64_TO_128_BRIDGE_A5_SOFT_RESET=1`,
`CLKC_RESET_SCU_SOFT_RESET=2`, `CLKC_RESET_CPU0_SOFT_RESET=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`CLKC_RESET_L2_CACHE_SOFT_RESET`, `CLKC_RESET_AXI_64_TO_128_BRIDGE_A5_SOFT_RESET`,
`CLKC_RESET_SCU_SOFT_RESET`, `CLKC_RESET_CPU0_SOFT_RESET`, `CLKC_RESET_CPU1_SOFT_RESET`,
`CLKC_RESET_CPU2_SOFT_RESET`, `CLKC_RESET_CPU3_SOFT_RESET`, `CLKC_RESET_A5_GLOBAL_RESET`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
