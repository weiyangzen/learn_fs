# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov9.h

## Purpose
`samsung,exynosautov9.h` defines clock IDs for the Exynos Auto V9 CMU hierarchy used in automotive Samsung SoCs.

## Important APIs, types, and functions
The header uses families `FOUT_*`, `MOUT_*`, `DOUT_*`, `GOUT_*`, and `CLK_*`. Sections cover `CMU_TOP`, `CMU_BUSMC`, `CMU_CORE`, `CMU_DPUM`, `CMU_FSYS0`, `CMU_FSYS1`, `CMU_FSYS2`, `CMU_PERIC0`, `CMU_PERIC1`, and `CMU_PERIS`. IDs describe shared PLLs, top-level mux/divider/gates, display processing, storage, USB/UFS/MMC-like high-speed domains, peripheral IP clocks, and watchdog clocks.

## Control flow
The header has compile-time constant flow only. Runtime clock operations are handled by domain CMU providers referenced by DTS nodes.

## State and persistence
The file is stateless. Numeric IDs are binding ABI and section-local where a CMU provider owns a subsection. Runtime state is in CMU registers and automotive power/retention domains.

## Dependencies and integration points
It integrates with Exynos Auto V9 device trees, Samsung CMU driver tables, automotive display, core/bus interconnect, storage/high-speed IO, PERIC serial controllers, PERIS watchdog/system blocks, and power management.

## Risks and test signals
Risks include using `GOUT_*` top-domain outputs directly under a child CMU, provider-domain numbering mistakes, and breaking watchdog or safety-related clocks. Test signals include `dtbs_check`, CMU provider registration, serial/storage/display smoke tests, watchdog clocks visible and enabled, and suspend/resume validation for automotive always-on domains.
