# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson-a1-power.h

Purpose: `meson-a1-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 21 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (21). Representative constants
are `PWRC_DSPA_ID`, `PWRC_DSPB_ID`, `PWRC_UART_ID`, `PWRC_DMC_ID`, `PWRC_I2C_ID`, `PWRC_PSRAM_ID`,
`PWRC_ACODEC_ID`, `PWRC_AUDIO_ID`, `...`, `PWRC_IR_ID`, `PWRC_SPICC_ID`, `PWRC_SPIFC_ID`,
`PWRC_USB_ID`, `PWRC_NIC_ID`, `PWRC_PDMIN_ID`, `PWRC_RSA_ID`, `PWRC_MAX_ID`. Function-like helpers
are none. Value shape: literal numeric range 8..28 across 21 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON_A1_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 32 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_DSPA_ID=8`, `PWRC_DSPB_ID=9`, `PWRC_UART_ID=10`, `PWRC_DMC_ID=11`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_DSPA_ID`, `PWRC_DSPB_ID`, `PWRC_UART_ID`, `PWRC_DMC_ID`, `PWRC_I2C_ID`, `PWRC_PSRAM_ID`,
`PWRC_ACODEC_ID`, `PWRC_AUDIO_ID`. Test signals include dt_binding_check, boot-time genpd
attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
