# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra194-clock.h

## Purpose
Defines Tegra194 clock IDs for DT bindings and BPMP clock access. It covers SoC clocks for display, audio, storage, I/O, fabric, CPU, PLL, PCIe, UFS, XUSB, MIPI, and always-on domains.

## Important APIs, Types, and Constants
The exported API is the `TEGRA194_CLK_*` macro set. IDs start at `TEGRA194_CLK_ACTMON` 1 and run through entries such as `TEGRA194_CLK_NAFLL_*`, `TEGRA194_CLK_PEX*`, `TEGRA194_CLK_UFS*`, and `TEGRA194_CLK_PLLE_HPS` 326. There are 313 numeric clock definitions and no functions or structs.

## Control Flow and State
This header has no runtime path. The only flow is the include guard `__ABI_MACH_T194_CLOCK_H`. State is external: the selected numeric ID is interpreted by the Tegra BPMP clock provider and common clock framework.

## Dependencies and Integration Points
No local includes are required. DTS clock specifiers include this header and pass IDs to Tegra194 clock provider nodes. Kernel drivers indirectly depend on these constants through DT resources such as `clocks` and `assigned-clocks`.

## Risks and Test Signals
Numeric values are DT ABI and must remain stable. Holes in the sequence are intentional compatibility space, not cleanup opportunities. Good signals are `dtbs_check`, Tegra194 DTS compilation, and boot tests that exercise display, storage, network, PCIe, and audio clock requests.
