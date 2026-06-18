# sources/distributed-fs/ceph-client/include/dt-bindings/power/meson8-power.h

Purpose: `meson8-power.h` is a Devicetree binding header for a power-domain provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PWRC (3). Representative constants
are `PWRC_MESON8_VPU_ID`, `PWRC_MESON8_ETHERNET_MEM_ID`, `PWRC_MESON8_AUDIO_DSP_MEM_ID`,
`PWRC_MESON8_VPU_ID`, `PWRC_MESON8_ETHERNET_MEM_ID`, `PWRC_MESON8_AUDIO_DSP_MEM_ID`. Function-like
helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_MESON8_POWER_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are `PWRC
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 13 lines long. Notable source comments include `_DT_BINDINGS_MESON8_POWER_H`. Example
value clusters are PWRC: `PWRC_MESON8_VPU_ID=0`, `PWRC_MESON8_ETHERNET_MEM_ID=1`,
`PWRC_MESON8_AUDIO_DSP_MEM_ID=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PWRC_MESON8_VPU_ID`, `PWRC_MESON8_ETHERNET_MEM_ID`, `PWRC_MESON8_AUDIO_DSP_MEM_ID`. Test signals
include dt_binding_check, boot-time genpd attachment, power-domain on/off sequencing,
suspend/resume, and device runtime-PM smoke tests.
