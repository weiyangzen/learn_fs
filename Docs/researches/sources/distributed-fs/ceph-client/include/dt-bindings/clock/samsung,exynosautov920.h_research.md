# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov920.h

## Purpose
`samsung,exynosautov920.h` defines clock binding IDs for ExynosAuto v920 CMU domains, including top-level, CPU cluster, peripheral, miscellaneous, high-speed, media, and GPU domains.

## Important APIs, types, and functions
The macro families are `FOUT_*`, `MOUT_*`, `DOUT_*`, and `CLK_*`. Sections cover `CMU_TOP`, `CMU_CPUCL0`, `CMU_CPUCL1`, `CMU_CPUCL2`, `CMU_PERIC0`, `CMU_PERIC1`, `CMU_MISC`, `CMU_HSI0`, `CMU_HSI1`, `CMU_HSI2`, `CMU_M2M`, `CMU_MFC`, `CMU_MFD`, and `CMU_G3D`. IDs represent shared/MMC/G3D PLLs, top-level mux/divider clocks, CPU cluster switches, PERIC buses, high-speed interfaces, memory-to-memory and media codec clocks, and GPU clocks.

## Control flow
DTS files include these constants under the appropriate CMU provider. Runtime control is delegated to ExynosAuto v920 CMU driver data and common clock framework operations.

## State and persistence
The header contains no state. Domain-local numeric IDs are stable ABI; CMU registers and power domains hold runtime state.

## Dependencies and integration points
It integrates with automotive Exynos device trees, Samsung CMU support, CPU frequency/cluster management, PERIC serial buses, HSI storage/connectivity blocks, M2M/MFC/MFD media engines, G3D GPU, and power management.

## Risks and test signals
Risks include confusing CPU cluster provider IDs, changing section-local numbering, and missing top-level parent clocks for child CMUs. Test signals include successful CMU registration for every domain, CPU cluster clock rate changes, PERIC console/serial tests, storage/high-speed IO smoke tests, media codec probing, GPU clock registration, and `dtbs_check`.
