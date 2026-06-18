# sources/distributed-fs/ceph-client/include/dt-bindings/power/amlogic,t7-pwrc.h

Purpose: `amlogic,t7-pwrc.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 53 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (53). Representative constants
are `PWRC_T7_DSPA_ID`, `PWRC_T7_DSPB_ID`, `PWRC_T7_DOS_HCODEC_ID`, `PWRC_T7_DOS_HEVC_ID`,
`PWRC_T7_DOS_VDEC_ID`, `PWRC_T7_DOS_WAVE_ID`, `PWRC_T7_VPU_HDMI_ID`, `PWRC_T7_USB_COMB_ID`, `...`,
`PWRC_T7_SPICC2_ID`, `PWRC_T7_SPICC3_ID`, `PWRC_T7_SPICC4_ID`, `PWRC_T7_SPICC5_ID`,
`PWRC_T7_EDP0_ID`, `PWRC_T7_EDP1_ID`, `PWRC_T7_MIPI_DSI1_ID`, `PWRC_T7_AUDIO_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..51 across 53 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_T7_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PWRC group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 63 lines long. Notable source comments include none. Example value clusters are PWRC:
`PWRC_T7_DSPA_ID=0`, `PWRC_T7_DSPB_ID=1`, `PWRC_T7_DOS_HCODEC_ID=2`, `PWRC_T7_DOS_HEVC_ID=3`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_T7_DSPA_ID`, `PWRC_T7_DSPB_ID`, `PWRC_T7_DOS_HCODEC_ID`, `PWRC_T7_DOS_HEVC_ID`,
`PWRC_T7_DOS_VDEC_ID`, `PWRC_T7_DOS_WAVE_ID`, `PWRC_T7_VPU_HDMI_ID`, `PWRC_T7_USB_COMB_ID`. Test
signals include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
