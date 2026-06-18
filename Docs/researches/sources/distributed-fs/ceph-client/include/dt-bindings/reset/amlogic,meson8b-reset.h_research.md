# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson8b-reset.h

Purpose: `amlogic,meson8b-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 98 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_PERIPHS (16), RESET_DEMUX (8), RESET_AHB (5),
RESET_PARSER (5), RESET_AUDIO (4), RESET_SYS (4), RESET_A5 (4), RESET_VLD (2), RESET_DDR (2),
RESET_VDAC (2). Representative constants are `RESET_HIU`, `RESET_VLD`, `RESET_IQIDCT`, `RESET_MC`,
`RESET_VIU`, `RESET_AIU`, `RESET_MCPU`, `RESET_CCPU`, `...`, `RESET_PERIPHS_SDIO`,
`RESET_PERIPHS_UART_0`, `RESET_PERIPHS_UART_1`, `RESET_PERIPHS_ASYNC_0`, `RESET_PERIPHS_ASYNC_1`,
`RESET_PERIPHS_SPI_0`, `RESET_PERIPHS_SPI_1`, `RESET_PERIPHS_LED_PWM`. Function-like helpers are
none. Value shape: literal numeric range 0..207 across 98 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON8B_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET0`, `16-31`, `RESET1`, `48-63`, `RESET2`, `80-95`, `RESET3`, `112-127`, `RESET4`,
`142-159`, `RESET5`, `166-191`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 126 lines long. Notable source comments include `RESET0`, `8`, `16-31`, `RESET1`, `32`,
`48-63`. Example value clusters are RESET_PERIPHS: `RESET_PERIPHS_GENERAL=192`,
`RESET_PERIPHS_IR_REMOTE=193`, `RESET_PERIPHS_SMART_CARD=194`, `RESET_PERIPHS_SAR_ADC=195`;
RESET_DEMUX: `RESET_DEMUX=33`, `RESET_DEMUX_TOP=105`, `RESET_DEMUX_DES=106`,
`RESET_DEMUX_S2P_0=107`; RESET_AHB: `RESET_AHB_SRAM=38`, `RESET_AHB_BRIDGE=39`, `RESET_AHB_DATA=45`,
`RESET_AHB_CNTL=46`; RESET_PARSER: `RESET_PARSER=40`, `RESET_PARSER_REG=71`,
`RESET_PARSER_FETCH=72`, `RESET_PARSER_CTL=73`; RESET_AUDIO: `RESET_AUDIO_APB=76`,
`RESET_AUDIO_PLL_MODULATOR=101`, `RESET_AUDIO_DAC=104`, `RESET_AUDIO_PLL=164`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_HIU`,
`RESET_VLD`, `RESET_IQIDCT`, `RESET_MC`, `RESET_VIU`, `RESET_AIU`, `RESET_MCPU`, `RESET_CCPU`. Test
signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
