# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos2200-cmu.h

## Purpose
`samsung,exynos2200-cmu.h` defines clock IDs for Exynos2200 CMU domains. It supports top-level and domain-specific clock controllers used by DTS and Samsung CMU drivers.

## Important APIs, types, and functions
All exported IDs use the `CLK_*` namespace. Sections cover `CMU_TOP`, `CMU_ALIVE`, `CMU_PERIS`, `CMU_CMGP`, `CMU_HSI0`, `CMU_PERIC0`, `CMU_PERIC1`, `CMU_PERIC2`, `CMU_UFS`, and `CMU_VTS`. The IDs include PLL outputs, muxes, dividers, and gate outputs such as shared PLLs, MMC PLL, CMU bus feeds, UART/I2C/SPI/USI clocks, UFS, and voice-trigger-system clocks.

## Control flow
There is no runtime code in the header. DTS nodes for each CMU domain use these IDs; the Exynos CMU driver registers the matching clocks and applies common clock framework operations.

## State and persistence
The header is stateless. Each section's numbers are ABI for its corresponding provider domain and may restart numbering within a domain. Actual state is in CMU registers and low-power always-on domains.

## Dependencies and integration points
It integrates with Exynos2200 DTS, Samsung CMU driver data, always-on/peripheral/high-speed/UFS/VTS devices, serial interfaces, storage, and power-domain sequencing.

## Risks and test signals
Risks include using an ID with the wrong CMU provider because domain-local numbering repeats, altering IDs used by shipped DTBs, and misdescribing always-on or VTS clocks. Test signals include schema checks, domain CMU probe logs, no unresolved clock phandles, UART/USI/I2C/SPI operation, UFS bring-up, and VTS/audio clock checks.
