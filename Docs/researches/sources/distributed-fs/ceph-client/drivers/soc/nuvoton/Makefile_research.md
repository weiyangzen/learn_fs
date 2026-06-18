# sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Makefile

## Purpose
Build glue for the Nuvoton WPCM450 SoC driver.

## Important APIs, Types, And Functions
No C APIs. `obj-$(CONFIG_WPCM450_SOC) += wpcm450-soc.o`.

## Control Flow
The object is compiled into the kernel/module when `WPCM450_SOC` is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Consumes the local Kconfig symbol and links the WPCM450 SoC identification source.

## Risks
None beyond normal config/object mismatches.

## Test Signals
`wpcm450-soc.o` appears in build output when the config is enabled.
