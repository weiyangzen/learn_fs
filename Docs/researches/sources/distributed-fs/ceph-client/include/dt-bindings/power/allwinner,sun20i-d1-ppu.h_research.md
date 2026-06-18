# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun20i-d1-ppu.h

Purpose: `allwinner,sun20i-d1-ppu.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_CPU (1), PD_VE (1), PD_DSP (1).
Representative constants are `PD_CPU`, `PD_VE`, `PD_DSP`, `PD_CPU`, `PD_VE`, `PD_DSP`. Function-like
helpers are none. Value shape: literal numeric range 0..2 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN20I_D1_PPU_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PD_CPU group`, `PD_VE group`, `PD_DSP group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 10 lines long. Notable source comments include `_DT_BINDINGS_POWER_SUN20I_D1_PPU_H_`.
Example value clusters are PD_CPU: `PD_CPU=0`; PD_VE: `PD_VE=1`; PD_DSP: `PD_DSP=2`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_CPU`, `PD_VE`, `PD_DSP`. Test signals include dt_binding_check, boot-time genpd attachment,
power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke tests.
