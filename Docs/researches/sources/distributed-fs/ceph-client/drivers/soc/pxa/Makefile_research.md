# sources/distributed-fs/ceph-client/drivers/soc/pxa/Makefile

## Purpose
Build glue for PXA/MMP SoC support helpers.

## Important APIs, Types, And Functions
No C APIs. Builds `mfp.o` for `CONFIG_PXA3xx` or `CONFIG_ARCH_MMP`, and `ssp.o` for `CONFIG_PXA_SSP`.

## Control Flow
Kernel build includes objects according to architecture and helper selections.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects architecture configs to shared PXA pinmux and SSP support code.

## Risks
Both `CONFIG_PXA3xx` and `CONFIG_ARCH_MMP` can request `mfp.o`; build system coalesces the object, but source changes need to remain compatible with both users.

## Test Signals
Configured PXA/MMP builds include the expected object files without duplicate symbol issues.
