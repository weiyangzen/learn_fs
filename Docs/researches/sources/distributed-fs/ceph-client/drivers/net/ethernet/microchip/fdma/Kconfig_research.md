# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Kconfig

## Purpose
This Kconfig fragment defines `CONFIG_FDMA`, the build switch for the shared Microchip Frame DMA API.

## Important APIs and Integration
`config FDMA` is a boolean option presented as `"FDMA API"` only under `COMPILE_TEST`. Other Microchip switchcore drivers select it directly, so normal product builds are expected to enable it via dependent drivers rather than through a user-visible prompt.

## Control Flow and State
Kconfig has no runtime control flow. Its state is the build-time symbol `CONFIG_FDMA`, which controls whether `fdma/Makefile` builds `fdma.o`.

## Dependencies and Risks
The option has no explicit dependencies beyond optional visibility under `COMPILE_TEST`. The main risk is dependency hygiene: any driver that calls FDMA helpers must `select FDMA` or depend on it, otherwise link failures occur. Because the prompt is hidden outside compile testing, direct user configuration is intentionally limited.

## Test Signals
`allyesconfig`, `allmodconfig`, and `COMPILE_TEST` builds should include `fdma_api.o`. Drivers such as `lan966x` and `sparx5` selecting `FDMA` are the practical integration checks.
