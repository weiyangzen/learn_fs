# sources/distributed-fs/ceph-client/drivers/soc/pxa/Kconfig

## Purpose
Defines legacy PXA platform support symbols for multi-function pins and SSP helpers.

## Important APIs, Types, And Functions
Declares `PLAT_PXA` as a bool and `PXA_SSP` as a tristate helper for PXA2xx SSP ports.

## Control Flow
Other architecture configs select these symbols; the local Makefile builds `mfp.o` and `ssp.o` based on them and on PXA/MMP arch symbols.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Provides config symbols consumed by PXA/MMP platform and peripheral drivers.

## Risks
`PXA_SSP` has no prompt here, so it is intended as an internal selectable symbol. Missing selection breaks client drivers using the exported SSP request/free API.

## Test Signals
Expected symbols resolve when PXA or MMP platforms are configured.
