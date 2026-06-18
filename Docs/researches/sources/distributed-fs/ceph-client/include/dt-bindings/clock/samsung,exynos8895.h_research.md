# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos8895.h

## Purpose
`samsung,exynos8895.h` defines device-tree clock IDs for Exynos8895 CMU domains including TOP, PERIS, FSYS0, FSYS1, PERIC0, and PERIC1.

## Important APIs, types, and functions
All IDs are `CLK_*` macros. `CMU_TOP` provides shared PLLs, top-level muxes/dividers, and gated outputs to subsystem CMUs. `CMU_PERIS` covers system/peripheral infrastructure. `CMU_FSYS0` and `CMU_FSYS1` cover high-speed storage and connectivity paths. `CMU_PERIC0` and `CMU_PERIC1` cover USI, UART, I2C/SPI-style peripheral clocks and bus gates.

## Control flow
The header only defines constants. DT clock specifiers select IDs under a particular CMU provider; the Exynos8895 CMU driver registers and controls those clocks through the common clock framework.

## State and persistence
The header has no mutable state. IDs are persistent ABI and are domain-local, so the same numeric value can mean different clocks under different CMU nodes.

## Dependencies and integration points
It integrates with Exynos8895 DTS, Samsung CMU driver data, subsystem CMUs, high-speed storage/USB, PERIC serial buses, system register blocks, and power management.

## Risks and test signals
Risks include cross-domain ID misuse, renumbering shipped bindings, and omission of top-level CMU gate clocks required by child domains. Test signals include schema validation, CMU probe for all domains, functional UART/USI/I2C/SPI, storage/USB bring-up through FSYS, and clk-summary parent chains from TOP to child CMUs.
