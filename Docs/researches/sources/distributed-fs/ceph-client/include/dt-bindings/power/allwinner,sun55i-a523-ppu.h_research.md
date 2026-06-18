# sources/distributed-fs/ceph-client/include/dt-bindings/power/allwinner,sun55i-a523-ppu.h

Purpose: `allwinner,sun55i-a523-ppu.h` is a Devicetree binding header for a power-domain provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 5 `#define`s covering power-domain IDs, power-gate
IDs, or performance-state constants. The main macro families are PD_DSP (1), PD_NPU (1), PD_AUDIO
(1), PD_SRAM (1), PD_RISCV (1). Representative constants are `PD_DSP`, `PD_NPU`, `PD_AUDIO`,
`PD_SRAM`, `PD_RISCV`, `PD_DSP`, `PD_NPU`, `PD_AUDIO`, `PD_SRAM`, `PD_RISCV`. Function-like helpers
are none. Value shape: literal numeric range 0..4 across 5 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_POWER_SUN55I_A523_PPU_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PD_DSP group`, `PD_NPU group`, `PD_AUDIO group`, `PD_SRAM group`, `PD_RISCV group`, which is
the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are generic power-domain providers, device
`power-domains` phandles, OPP/performance-state users, and SoC power-controller drivers.

Local source signals: The file is 12 lines long. Notable source comments include `_DT_BINDINGS_POWER_SUN55I_A523_PPU_H_`.
Example value clusters are PD_DSP: `PD_DSP=0`; PD_NPU: `PD_NPU=1`; PD_AUDIO: `PD_AUDIO=2`; PD_SRAM:
`PD_SRAM=3`; PD_RISCV: `PD_RISCV=4`.

Risks and test signals: Primary risks are renumbering domain IDs or performance levels can attach devices to the wrong power
island or request the wrong voltage corner. Pay special attention to exported symbols such as
`PD_DSP`, `PD_NPU`, `PD_AUDIO`, `PD_SRAM`, `PD_RISCV`. Test signals include dt_binding_check, boot-
time genpd attachment, power-domain on/off sequencing, suspend/resume, and device runtime-PM smoke
tests.
