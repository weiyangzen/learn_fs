# sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.h

## Purpose
Defines public Samsung S/PDIF machine-driver clock source IDs for internal and external MCLK.

## Important APIs, Types, And Functions
Defines `SND_SOC_SPDIF_INT_MCLK` and `SND_SOC_SPDIF_EXT_MCLK`.

## Control Flow
No executable flow. Machine drivers pass these IDs to `snd_soc_dai_set_sysclk()`, and `spdif.c` maps them to the `CLKCTL_MCLK_EXT` bit.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by Samsung SMDK S/PDIF machine driver and Samsung S/PDIF controller driver.

## Risks And Edge Cases
The include guard is defined as `__FILE__`, an unusual but functioning pattern. Constants must stay synchronized with `spdif_set_sysclk()`.

## Test Signals
Compile coverage and SMDK S/PDIF sysclk calls for internal MCLK.
