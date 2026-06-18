# sources/distributed-fs/ceph-client/include/dt-bindings/pmu/exynos_ppmu.h

Purpose: `exynos_ppmu.h` is a Devicetree binding header for a PMU/PPMU provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 12 `#define`s covering PMU/PPMU event and counter
selector constants. The main macro families are PPMU (12). Representative constants are
`PPMU_RO_BUSY_CYCLE_CNT`, `PPMU_WO_BUSY_CYCLE_CNT`, `PPMU_RW_BUSY_CYCLE_CNT`, `PPMU_RO_REQUEST_CNT`,
`PPMU_WO_REQUEST_CNT`, `PPMU_RO_DATA_CNT`, `PPMU_WO_DATA_CNT`, `PPMU_RO_LATENCY`,
`PPMU_WO_REQUEST_CNT`, `PPMU_RO_DATA_CNT`, `PPMU_WO_DATA_CNT`, `PPMU_RO_LATENCY`, `PPMU_WO_LATENCY`,
`PPMU_V2_RO_DATA_CNT`, `PPMU_V2_WO_DATA_CNT`, `PPMU_V2_EVT3_RW_DATA_CNT`. Function-like helpers are
none. Value shape: literal numeric range 0..34 across 12 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PMU_EXYNOS_PPMU_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`PPMU group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are PPMU/PMU drivers and DTS nodes
describing monitored bus or memory interfaces.

Local source signals: The file is 25 lines long. Notable source comments include `Samsung Exynos PPMU event types for
counting in regs`. Example value clusters are PPMU: `PPMU_RO_BUSY_CYCLE_CNT=0x0`,
`PPMU_WO_BUSY_CYCLE_CNT=0x1`, `PPMU_RW_BUSY_CYCLE_CNT=0x2`, `PPMU_RO_REQUEST_CNT=0x3`.

Risks and test signals: Primary risks are event selector drift can make performance counters sample the wrong bus endpoint.
Pay special attention to exported symbols such as `PPMU_RO_BUSY_CYCLE_CNT`,
`PPMU_WO_BUSY_CYCLE_CNT`, `PPMU_RW_BUSY_CYCLE_CNT`, `PPMU_RO_REQUEST_CNT`, `PPMU_WO_REQUEST_CNT`,
`PPMU_RO_DATA_CNT`, `PPMU_WO_DATA_CNT`, `PPMU_RO_LATENCY`. Test signals include PPMU probe, event
selection smoke tests, and DTS validation for all monitored channels.
